import logging
import time

logger = logging.getLogger(__name__)

class DummyMathStrategy:
    """
    A simulated mathematical strategy for processing tasks.
    In reality, this would run heavy CPU computations on data downloaded from MinIO.
    """
    @staticmethod
    def execute(task_payload: dict) -> dict:
        task_id = task_payload.get("task_id", "unknown")
        logger.info(f"Starting computation for task {task_id}")
        
        # Simulate heavy CPU work
        time.sleep(2)
        
        # Simulated result
        result = {
            "task_id": task_id,
            "status": "completed",
            "result_data": "simulated_math_output",
            "compute_time_ms": 2000
        }
        
        logger.info(f"Completed computation for task {task_id}")
        return result
