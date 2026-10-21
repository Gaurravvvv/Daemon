import logging
import time
import json
import os
import tempfile
from storage import storage

logger = logging.getLogger(__name__)

class DummyMathStrategy:
    """
    A mathematical strategy for processing tasks.
    Runs CPU/Math computation and uploads the result artifact to MinIO.
    """
    @staticmethod
    def execute(task_payload: dict) -> dict:
        task_id = task_payload.get("task_id", "unknown")
        job_id = task_payload.get("job_id", "unknown")
        chunk_index = task_payload.get("chunk_index", 0)
        raw_data_url = task_payload.get("raw_data_url", "")
        
        logger.info(f"Starting computation for task {task_id}")
        
        start_time = time.time()
        # Simulate compute work
        time.sleep(1.5)
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        result = {
            "task_id": task_id,
            "job_id": job_id,
            "chunk_index": chunk_index,
            "status": "completed",
            "compute_time_ms": elapsed_ms,
            "output": f"Batch compute partition {chunk_index} verified and resolved successfully."
        }
        
        # Upload result JSON to MinIO so results are downloadable
        try:
            bucket = "daemon-jobs"
            if raw_data_url.startswith("minio://"):
                parts = raw_data_url.replace("minio://", "").split("/", 1)
                if parts:
                    bucket = parts[0]
                    
            temp_dir = os.path.join(tempfile.gettempdir(), "daemon_worker")
            os.makedirs(temp_dir, exist_ok=True)
            result_path = os.path.join(temp_dir, f"{task_id}_result.json")
            
            with open(result_path, "w") as f:
                json.dump(result, f, indent=2)
                
            storage.upload_result(bucket, result_path, f"{job_id}/results/{task_id}_math_result.json")
            logger.info(f"Uploaded math result to MinIO: {job_id}/results/{task_id}_math_result.json")
        except Exception as e:
            logger.warning(f"Could not upload result artifact to MinIO: {e}")
        
        logger.info(f"Completed computation for task {task_id}")
        return result
