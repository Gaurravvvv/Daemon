import uuid
from typing import List

class TaskSplitter:
    @staticmethod
    def partition_job(job_id: str, raw_data_url: str, job_type: str, parameters: dict, split_count: int, compute_mode: str = "any") -> List[dict]:
        """
        Splits a job into multiple micro-tasks.
        Each task carries the compute_mode so workers can check eligibility.
        """
        tasks = []
        for i in range(split_count):
            task_id = f"{job_id}-task-{uuid.uuid4().hex[:6]}"
            task = {
                "job_id": job_id,
                "task_id": task_id,
                "job_type": job_type,
                "raw_data_url": raw_data_url,
                "chunk_index": i,
                "total_chunks": split_count,
                "compute_mode": compute_mode,
                "parameters": parameters
            }
            tasks.append(task)
            
        return tasks
