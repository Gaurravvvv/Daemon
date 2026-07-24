import uuid
from typing import List

class TaskSplitter:
    @staticmethod
    def partition_job(job_id: str, raw_data_url: str, job_type: str, parameters: dict, split_count: int) -> List[dict]:
        """
        Simulates splitting a massive job into multiple micro-tasks.
        In a production scenario, this would read the MinIO file size and split byte-ranges.
        For now, it generates `split_count` dummy chunks based on max_workers.
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
                "parameters": parameters
            }
            tasks.append(task)
            
        return tasks
