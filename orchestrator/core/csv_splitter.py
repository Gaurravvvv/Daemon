import os
import uuid
import logging
from typing import List, Dict, Any
from services.storage import storage

logger = logging.getLogger(__name__)

class CSVSplitter:
    """
    Streaming line-aware CSV partitioner.
    Splits arbitrary CSV datasets into N contiguous row-aligned chunks,
    distributing the original header row across all chunk slices to ensure
    standalone validity for worker nodes.
    """

    @staticmethod
    def partition_csv(
        job_id: str,
        csv_file_path: str,
        split_count: int = 10,
        rules: Dict[str, Any] = None
    ) -> List[dict]:
        rules = rules or {
            "deduplicate": True,
            "clean_headers": True,
            "standardize_nulls": True,
            "redact_pii": True,
            "standardize_dates": True,
            "null_threshold_pct": 80
        }

        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV file not found at: {csv_file_path}")

        # 1. First pass: extract header and count data rows
        logger.info(f"[CSVSplitter] Analyzing CSV structure for job {job_id}...")
        header_line = None
        total_data_rows = 0

        with open(csv_file_path, "r", encoding="utf-8", errors="replace") as f:
            for idx, line in enumerate(f):
                if idx == 0:
                    header_line = line
                else:
                    if line.strip():
                        total_data_rows += 1

        if not header_line:
            raise ValueError("Uploaded CSV file is empty or missing a header row.")

        logger.info(f"[CSVSplitter] Header found. Total data rows: {total_data_rows}. Slicing into {split_count} partitions...")

        # If data is small, adjust split count
        effective_splits = min(split_count, max(1, total_data_rows))
        rows_per_chunk = max(1, (total_data_rows + effective_splits - 1) // effective_splits)

        tasks = []
        temp_dir = os.path.dirname(csv_file_path)

        # 2. Second pass: stream rows into chunk files and upload directly to MinIO
        with open(csv_file_path, "r", encoding="utf-8", errors="replace") as f:
            # Skip header
            next(f, None)
            
            current_chunk_idx = 0
            current_chunk_rows = []

            for row_idx, line in enumerate(f):
                if not line.strip():
                    continue
                current_chunk_rows.append(line)

                if len(current_chunk_rows) >= rows_per_chunk or (row_idx + 1 == total_data_rows):
                    chunk_filename = f"chunk_{current_chunk_idx}.csv"
                    chunk_local_path = os.path.join(temp_dir, f"{job_id}_{chunk_filename}")

                    # Write chunk file: header + rows
                    with open(chunk_local_path, "w", encoding="utf-8", newline="") as chunk_f:
                        chunk_f.write(header_line)
                        chunk_f.writelines(current_chunk_rows)

                    # Upload chunk directly to MinIO
                    object_key = f"{job_id}/chunks/{chunk_filename}"
                    with open(chunk_local_path, "rb") as cf:
                        chunk_bytes = cf.read()
                    
                    minio_url = storage.upload_bytes(chunk_bytes, object_key, content_type="text/csv")

                    task_id = f"{job_id}-task-{uuid.uuid4().hex[:6]}"
                    task_manifest = {
                        "job_id": job_id,
                        "task_id": task_id,
                        "job_type": "csv_cleaning",
                        "raw_data_url": minio_url,
                        "chunk_index": current_chunk_idx,
                        "total_chunks": effective_splits,
                        "row_count": len(current_chunk_rows),
                        "compute_mode": "any",
                        "retry_count": 0,
                        "rules": rules
                    }
                    tasks.append(task_manifest)

                    # Clean local chunk temp file
                    try:
                        os.remove(chunk_local_path)
                    except Exception:
                        pass

                    current_chunk_idx += 1
                    current_chunk_rows = []

        logger.info(f"[CSVSplitter] Successfully created and staged {len(tasks)} CSV chunks in MinIO.")
        return tasks

