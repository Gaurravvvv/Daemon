from fastapi import APIRouter, HTTPException
import uuid
import logging
from models.schemas import JobSubmitRequest, JobSubmitResponse, WorkerRegisterRequest, WorkerRegisterResponse
from services.rabbitmq import rabbitmq_client
from core.splitter import TaskSplitter
from services.database import db

router = APIRouter(prefix="/api/v1")
logger = logging.getLogger(__name__)

@router.post("/jobs/submit", response_model=JobSubmitResponse, status_code=202)
async def submit_job(job_request: JobSubmitRequest):
    # 1. Generate unique Job ID
    job_id = f"job-{uuid.uuid4().hex[:8]}"
    
    # 2. Save Initial Job State to MongoDB
    job_doc = {
        "job_id": job_id,
        "job_name": job_request.job_name,
        "status": "partitioning",
        "pool_id": job_request.pool_id
    }
    await db.db.jobs.insert_one(job_doc)
    
    # 3. Partition the Job into Micro-Tasks
    tasks = TaskSplitter.partition_job(
        job_id=job_id, 
        raw_data_url=job_request.raw_data_url, 
        parameters=job_request.parameters
    )
    
    # 4. Push Tasks to RabbitMQ
    for task in tasks:
        rabbitmq_client.publish_task(
            pool_id=job_request.pool_id, 
            task_payload=task
        )
    
    # 5. Update Status in DB
    await db.db.jobs.update_one({"job_id": job_id}, {"$set": {"status": "processing"}})
    
    return {"job_id": job_id, "status": "processing"}

@router.post("/workers/register", response_model=WorkerRegisterResponse)
async def register_worker(worker: WorkerRegisterRequest):
    # Save worker info to DB (simulating Redis presence for now)
    worker_doc = worker.model_dump()
    worker_doc["status"] = "online"
    await db.db.workers.update_one(
        {"worker_id": worker.worker_id}, 
        {"$set": worker_doc}, 
        upsert=True
    )
    
    return {"status": "registered", "heartbeat_interval": 10}
