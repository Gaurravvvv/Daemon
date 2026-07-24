import asyncio
import logging
from services.database import db

logger = logging.getLogger(__name__)

class StateAggregator:
    @staticmethod
    async def stitch_results(job_id: str):
        """
        Simulates combining all the micro-task results back into one master file.
        In production, this would download all chunks from MinIO, stitch them, 
        and upload a final `result.zip`.
        """
        logger.info(f"Stitching final results for job {job_id}...")
        await asyncio.sleep(1) # simulate I/O work
        logger.info(f"Job {job_id} successfully stitched!")
        
        # Mark job as completed
        await db.db.jobs.update_one(
            {"job_id": job_id}, 
            {"$set": {"status": "completed", "final_result_url": f"minio://public_pool/{job_id}-final.zip"}}
        )

async def monitor_jobs():
    """
    A continuous background loop that checks MongoDB for jobs 
    where all micro-tasks are finished, then triggers the stitcher.
    """
    logger.info("Starting background state aggregator loop...")
    while True:
        try:
            # Note: In a full production app, this would use Redis for fast lookups.
            # Here we simulate finding a job that is 'processing' but all its sub-tasks are done.
            # For Phase 4 MVP, we just mock the aggregation of any jobs stuck in 'processing' for too long.
            
            # (Dummy logic for now)
            # Find jobs that have been processing
            cursor = db.db.jobs.find({"status": "processing"})
            async for job in cursor:
                # Simulate that we detected all workers finished
                # We trigger the stitcher
                await StateAggregator.stitch_results(job["job_id"])
                
        except Exception as e:
            logger.error(f"Error in aggregator loop: {e}")
            
        # Poll every 5 seconds
        await asyncio.sleep(5)
