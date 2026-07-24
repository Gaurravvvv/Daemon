from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import uuid
import random
import logging
from pydantic import BaseModel
from models.schemas import JobSubmitRequest, JobSubmitResponse, WorkerRegisterRequest, WorkerRegisterResponse, VerifyPasswordRequest
from services.rabbitmq import rabbitmq_client
from services.storage import storage
from core.splitter import TaskSplitter
from services.database import db

router = APIRouter(prefix="/api/v1")
logger = logging.getLogger(__name__)

@router.get("/jobs")
async def list_jobs():
    jobs = []
    cursor = db.db.jobs.find().sort("_id", -1)
    async for document in cursor:
        document["_id"] = str(document["_id"])
        # Mock global progress for the UI if missing
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
    # Standard JSON submit (from phase 1)
    job_id = f"job-{random.randint(1000, 9999)}"
    
    job_doc = {
        "job_id": job_id,
        "job_name": job_request.job_name,
        "job_type": job_request.job_type,
        "status": "partitioning",
        "pool_id": job_request.pool_id,
        "raw_data_url": job_request.raw_data_url,
        "progress": 0
    }
    await db.db.jobs.insert_one(job_doc)
    
    tasks = TaskSplitter.partition_job(
        job_id=job_id, 
        raw_data_url=job_request.raw_data_url, 
        job_type=job_request.job_type,
        parameters=job_request.parameters,
        split_count=5
    )
    
    for task in tasks:
        rabbitmq_client.publish_task(
            pool_id=job_request.pool_id, 
            task_payload=task
        )
    
    await db.db.jobs.update_one({"job_id": job_id}, {"$set": {"status": "processing"}})
    return {"job_id": job_id, "status": "processing"}

@router.post("/jobs/upload_and_submit", status_code=202)
async def upload_and_submit(
    job_name: str = Form(...),
    job_type: str = Form(...),
    pool_id: str = Form(...),
    max_workers: int = Form(100),
    password: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    # 1. Generate unique Job ID
    job_id = f"job-{random.randint(1000, 9999)}"
    
    # 2. Upload the raw data to MinIO
    object_name = f"{job_id}/{file.filename}"
    raw_data_url = await storage.upload_file(file, object_name)
    
    # 3. Save Initial Job State to MongoDB
    job_doc = {
        "job_id": job_id,
        "job_name": job_name,
        "job_type": job_type,
        "status": "partitioning",
        "pool_id": pool_id,
        "raw_data_url": raw_data_url,
        "progress": 0
    }
    if password:
        job_doc["password"] = password
        
    await db.db.jobs.insert_one(job_doc)
    
    # 4. Partition the Job into Micro-Tasks
    # For a real pipeline, the splitter reads from raw_data_url and creates byte-range chunks.
    tasks = TaskSplitter.partition_job(
        job_id=job_id, 
        raw_data_url=raw_data_url, 
        job_type=job_type,
        parameters={"max_workers": max_workers},
        split_count=max_workers
    )
    
    # 5. Push Tasks to RabbitMQ
    for task in tasks:
        rabbitmq_client.publish_task(
            pool_id=pool_id, 
            task_payload=task
        )
    
    # 6. Update Status in DB
    await db.db.jobs.update_one({"job_id": job_id}, {"$set": {"status": "processing"}})
    
    return {"job_id": job_id, "status": "processing", "raw_data_url": raw_data_url}

@router.put("/jobs/{job_id}/halt")
async def halt_job(job_id: str):
    job = await db.db.jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    await db.db.jobs.update_one({"job_id": job_id}, {"$set": {"status": "halted"}})
    return {"status": "halted"}

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    job = await db.db.jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    await db.db.jobs.delete_one({"job_id": job_id})
    return {"status": "deleted"}

class TaskCompleteRequest(BaseModel):
    total_chunks: int

@router.post("/jobs/{job_id}/task_complete")
async def task_complete(job_id: str, req: TaskCompleteRequest):
    job = await db.db.jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    increment = max(1, int(100 / req.total_chunks))
    
    # Calculate new progress
    current_progress = job.get("progress", 0)
    new_progress = min(100, current_progress + increment)
    
    update_data = {"progress": new_progress}
    if new_progress >= 100:
        update_data["status"] = "completed"
        
    await db.db.jobs.update_one(
        {"job_id": job_id},
        {"$set": update_data}
    )
    return {"status": "success", "progress": new_progress}

@router.post("/workers/register", response_model=WorkerRegisterResponse)
async def register_worker(worker: WorkerRegisterRequest):
    worker_doc = worker.model_dump()
    worker_doc["status"] = "online"
    await db.db.workers.update_one(
        {"worker_id": worker.worker_id}, 
        {"$set": worker_doc}, 
        upsert=True
    )
    return {"status": "registered", "heartbeat_interval": 10}
