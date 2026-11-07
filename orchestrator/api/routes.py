from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
import io
import zipfile
from typing import List, Optional, Dict, Any
import uuid
import random
import logging
from datetime import datetime, timezone
from pydantic import BaseModel
from models.schemas import (
    JobSubmitRequest, 
    JobSubmitResponse, 
    WorkerRegisterRequest, 
    WorkerRegisterResponse, 
    WorkerHeartbeatResponse,
    TaskCompleteRequest,
    VerifyPasswordRequest
)
from services.rabbitmq import rabbitmq_client
from services.storage import storage
from services.redis_client import redis_manager
from core.splitter import TaskSplitter
from core.aggregator import StateAggregator
from services.database import db

router = APIRouter(prefix="/api/v1")
logger = logging.getLogger(__name__)

def _normalize_job_type(raw_type: str) -> str:
    """Normalize polymorphic job type strings across dashboard, schemas, and workers."""
    cleaned = str(raw_type).lower().strip()
    if cleaned in ("image", "image_processing"):
        return "image"
    if cleaned in ("math", "matrix", "matrix_multiplication"):
        return "math"
    if cleaned in ("crypto", "cryptography", "pow"):
        return "crypto"
    return cleaned

# ── Helper to push events into MongoDB ──
async def _emit_event(job_id: str, source: str, level: str, message: str, worker_id: str = None):
    """Store a real-time event in the job_events collection."""
    event = {
        "job_id": job_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "level": level,
        "message": message,
    }
    if worker_id:
        event["worker_id"] = worker_id
    await db.db.job_events.insert_one(event)

@router.get("/jobs")
async def list_jobs():
    jobs = []
    cursor = db.db.jobs.find().sort("_id", -1)
    async for document in cursor:
        document["_id"] = str(document["_id"])
        if "progress" not in document:
            document["progress"] = 0
            
        # Secure the password
        has_pass = bool(document.get("password"))
        if "password" in document:
            del document["password"]
        document["requires_password"] = has_pass
            
        jobs.append(document)
    return {"jobs": jobs}

@router.post("/jobs/{job_id}/verify_password")
async def verify_password(job_id: str, req: VerifyPasswordRequest):
    job = await db.db.jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if not job.get("password"):
        return {"success": True}
        
    if job.get("password") != req.password:
        raise HTTPException(status_code=401, detail="Incorrect password")
        
    return {"success": True}

@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = await db.db.jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job["_id"] = str(job["_id"])
    if "progress" not in job:
        job["progress"] = 0
    if "password" in job:
        job["requires_password"] = True
        del job["password"]
    else:
        job["requires_password"] = False
    return job

@router.post("/jobs/submit", response_model=JobSubmitResponse, status_code=202)
async def submit_job(job_request: JobSubmitRequest):
    job_id = f"job-{random.randint(1000, 9999)}"
    normalized_type = _normalize_job_type(job_request.job_type)
    split_count = job_request.split_count or 10

    job_doc = {
        "job_id": job_id,
        "job_name": job_request.job_name,
        "job_type": normalized_type,
        "status": "partitioning",
        "pool_id": job_request.pool_id,
        "raw_data_url": job_request.raw_data_url,
        "compute_mode": job_request.compute_mode,
        "progress": 0,
        "total_chunks": split_count,
        "completed_chunks": 0,
        "failed_chunks": 0
    }
    await db.db.jobs.insert_one(job_doc)
    
    tasks = TaskSplitter.partition_job(
        job_id=job_id, 
        raw_data_url=job_request.raw_data_url, 
        job_type=normalized_type,
        parameters=job_request.parameters,
        split_count=split_count,
        compute_mode=job_request.compute_mode
    )
    
    for task in tasks:
        rabbitmq_client.publish_task(
            pool_id=job_request.pool_id, 
            task_payload=task
        )
    
    await db.db.jobs.update_one({"job_id": job_id}, {"$set": {"status": "processing", "total_chunks": len(tasks), "completed_chunks": 0}})
    return {"job_id": job_id, "status": "processing"}

@router.post("/jobs/upload_and_submit", status_code=202)
async def upload_and_submit(
    job_name: str = Form(...),
    job_type: str = Form(...),
    pool_id: str = Form(...),
    max_workers: Optional[int] = Form(None),
    split_count: Optional[int] = Form(None),
    compute_mode: str = Form("any"),
    password: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    # 1. Resolve partition count (accepts either split_count from UI or max_workers)
    partitions = split_count if split_count is not None else (max_workers if max_workers is not None else 10)
    normalized_type = _normalize_job_type(job_type)

    # 2. Generate unique Job ID
    job_id = f"job-{random.randint(1000, 9999)}"
    
    # 3. Upload the raw data to MinIO
    object_name = f"{job_id}/{file.filename}"
    raw_data_url = await storage.upload_file(file, object_name)
    
    # 4. Save Initial Job State to MongoDB
    job_doc = {
        "job_id": job_id,
        "job_name": job_name,
        "job_type": normalized_type,
        "status": "partitioning",
        "pool_id": pool_id,
        "raw_data_url": raw_data_url,
        "compute_mode": compute_mode,
        "progress": 0,
        "total_chunks": partitions,
        "completed_chunks": 0,
        "failed_chunks": 0,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    if password:
        job_doc["password"] = password
        
    await db.db.jobs.insert_one(job_doc)
    
    compute_label = {"gpu_only": "GPU Only", "cpu_only": "CPU Only", "any": "Hybrid"}.get(compute_mode, compute_mode)
    await _emit_event(job_id, "ORCHESTRATOR", "SYSTEM", f"Job '{job_name}' created [{compute_label}]. Slicing into {partitions} partitions...")
    
    # 5. Partition the Job into Micro-Tasks
    tasks = TaskSplitter.partition_job(
        job_id=job_id, 
        raw_data_url=raw_data_url, 
        job_type=normalized_type,
        parameters={"max_workers": partitions},
        split_count=partitions,
        compute_mode=compute_mode
    )
    
    await _emit_event(job_id, "ORCHESTRATOR", "INFO", f"Partitioned into {len(tasks)} chunks. Publishing to queue '{pool_id}'...")
    
    # 6. Push Tasks to RabbitMQ
    for task in tasks:
        rabbitmq_client.publish_task(
            pool_id=pool_id, 
            task_payload=task
        )
    
    # 7. Update Status in DB
    await db.db.jobs.update_one({"job_id": job_id}, {"$set": {"status": "processing", "total_chunks": len(tasks), "completed_chunks": 0}})
    
    await _emit_event(job_id, "ORCHESTRATOR", "SUCCESS", f"All {len(tasks)} chunks queued. Job is now PROCESSING.")
    
    return {"job_id": job_id, "status": "processing", "raw_data_url": raw_data_url, "partitions": len(tasks)}

@router.put("/jobs/{job_id}/halt")
async def halt_job(job_id: str):
    job = await db.db.jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    await db.db.jobs.update_one({"job_id": job_id}, {"$set": {"status": "halted"}})
    await _emit_event(job_id, "ORCHESTRATOR", "WARNING", "Job HALTED by orchestrator. Workers will discard remaining chunks.")
    return {"status": "halted"}

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    job = await db.db.jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    await db.db.jobs.delete_one({"job_id": job_id})
    await db.db.job_events.delete_many({"job_id": job_id})
    return {"status": "deleted"}

@router.post("/jobs/{job_id}/task_complete")
async def task_complete(job_id: str, req: TaskCompleteRequest):
    """
    Called by workers upon finishing (or failing) a task.
    Correctly distinguishes success vs failure without falsely inflating progress.
    """
    job = await db.db.jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    total = job.get("total_chunks") or req.total_chunks or 1

    # Case A: Task Failed
    if req.status == "failed":
        result = await db.db.jobs.find_one_and_update(
            {"job_id": job_id},
            {"$inc": {"failed_chunks": 1}},
            return_document=True
        )
        failed_count = result.get("failed_chunks", 1)
        completed_count = result.get("completed_chunks", 0)
        
        await _emit_event(
            job_id, 
            "WORKER", 
            "ERROR", 
            f"Chunk {req.chunk_index} FAILED: {req.error_message or 'Unknown error'}",
            req.worker_id
        )

        if completed_count + failed_count >= total:
            status = "completed" if completed_count > 0 else "failed"
            await db.db.jobs.update_one({"job_id": job_id}, {"$set": {"status": status}})
            if completed_count > 0:
                await StateAggregator.stitch_results(job_id)

        return {"status": "recorded_failure", "failed_chunks": failed_count}

    # Case B: Task Succeeded
    result = await db.db.jobs.find_one_and_update(
        {"job_id": job_id},
        {"$inc": {"completed_chunks": 1}},
        return_document=True
    )
    
    completed = result.get("completed_chunks", 1)
    failed = result.get("failed_chunks", 0)
    new_progress = min(100, int(round((completed / total) * 100)))
    
    update_data = {"progress": new_progress}
    if completed + failed >= total or new_progress >= 100:
        new_progress = 100
        update_data["progress"] = 100
        update_data["status"] = "completed"
        await db.db.jobs.update_one({"job_id": job_id}, {"$set": update_data})
        # Trigger background state stitcher
        await StateAggregator.stitch_results(job_id)
    else:
        await db.db.jobs.update_one({"job_id": job_id}, {"$set": update_data})

    return {"status": "success", "progress": new_progress}

# ── Event Log Endpoints ──

class EventLogRequest(BaseModel):
    source: str
    level: str
    message: str
    worker_id: Optional[str] = None

@router.post("/jobs/{job_id}/events")
async def post_event(job_id: str, req: EventLogRequest):
    """Workers push real-time events here."""
    await _emit_event(job_id, req.source, req.level, req.message, req.worker_id)
    return {"status": "logged"}

@router.get("/jobs/{job_id}/events")
async def get_events(job_id: str, after: Optional[str] = Query(None)):
    """Dashboard polls this to get new events."""
    query = {"job_id": job_id}
    if after:
        query["timestamp"] = {"$gt": after}
    
    events = []
    cursor = db.db.job_events.find(query).sort("timestamp", 1).limit(200)
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        events.append(doc)
    return {"events": events}

# ── Results / Download Endpoints ──

@router.get("/jobs/{job_id}/results")
async def list_results(job_id: str):
    """List all processed result files for a completed job."""
    files = storage.list_results(job_id)
    return {"files": files}

@router.get("/jobs/{job_id}/download")
async def download_results(job_id: str):
    """
    Delivers the master stitched deliverable ZIP if generated,
    or dynamically packages all result chunks.
    """
    job = await db.db.jobs.find_one({"job_id": job_id})
    files = storage.list_results(job_id)
    if not files:
        raise HTTPException(status_code=404, detail="No results found for this job")

    # If master stitched archive exists, stream it directly
    master_key = f"{job_id}/results/{job_id}_master_results.zip"
    try:
        master_bytes = storage.download_file(master_key)
        return StreamingResponse(
            io.BytesIO(master_bytes),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={job_id}_final_deliverable.zip"}
        )
    except Exception:
        pass

    # Fallback: Create zip in memory from all individual chunk files
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            file_bytes = storage.download_file(f["key"])
            zf.writestr(f["filename"], file_bytes)
    
    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={job_id}_results.zip"}
    )

# ── Worker Heartbeat & Registry Endpoints ──

@router.post("/workers/register", response_model=WorkerRegisterResponse)
async def register_worker(worker: WorkerRegisterRequest):
    worker_doc = worker.model_dump()
    worker_doc["status"] = "online"
    worker_doc["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
    
    # Register lease in Redis
    redis_manager.renew_lease(worker.worker_id, worker.pool_id)
    
    await db.db.workers.update_one(
        {"worker_id": worker.worker_id}, 
        {"$set": worker_doc}, 
        upsert=True
    )
    logger.info(f"Worker {worker.worker_id} registered with lease TTL {redis_manager.lease_ttl}s")
    return {"status": "registered", "heartbeat_interval": 5}

@router.post("/workers/{worker_id}/heartbeat", response_model=WorkerHeartbeatResponse)
async def worker_heartbeat(worker_id: str, pool_id: str = Query("public_pool")):
    """Ephemeral sliding-window heartbeat renewal (called every 5s by workers)."""
    redis_manager.renew_lease(worker_id, pool_id)
    await db.db.workers.update_one(
        {"worker_id": worker_id},
        {"$set": {"status": "online", "last_heartbeat": datetime.now(timezone.utc).isoformat()}}
    )
    return {"status": "acknowledged", "acknowledged": True}

@router.get("/workers")
async def list_workers():
    """Lists all cluster workers and checks their real-time Redis lease status."""
    active_worker_ids = set(redis_manager.get_active_workers())
    workers = []
    cursor = db.db.workers.find().sort("worker_id", 1)
    async for w in cursor:
        w["_id"] = str(w["_id"])
        # Node is strictly online if it holds an active Redis lease
        is_live = w["worker_id"] in active_worker_ids
        w["is_live"] = is_live
        w["status"] = "online" if is_live else "offline"
        workers.append(w)
    return {"workers": workers, "active_count": len(active_worker_ids)}
