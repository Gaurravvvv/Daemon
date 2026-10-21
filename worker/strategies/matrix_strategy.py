import logging
import os
import zipfile
import tempfile
import json
import time
import numpy as np
from storage import storage

logger = logging.getLogger(__name__)

# Check GPU availability for matrix multiplication
USE_GPU = False
if os.environ.get("FORCE_CPU", "").lower() not in ("1", "true", "yes"):
    try:
        import cupy as cp
        if cp.cuda.runtime.getDeviceCount() > 0:
            USE_GPU = True
            logger.info("[MatrixStrategy] CuPy GPU acceleration enabled for matrix operations.")
    except Exception:
        pass


class MatrixMultiplicationStrategy:
    """
    High-Performance Distributed Block Matrix Multiplication Strategy.
    Computes C_slice = A_row_slice @ B using BLAS / CuPy GPU,
    benchmarks numerical properties, and uploads the sub-block result to MinIO.
    """
    @staticmethod
    def execute(task_payload: dict) -> dict:
        global USE_GPU
        task_id = task_payload.get("task_id", "unknown")
        job_id = task_payload.get("job_id", "unknown")
        chunk_index = task_payload.get("chunk_index", 0)
        raw_data_url = task_payload.get("raw_data_url", "")
        compute_mode = task_payload.get("compute_mode", "any")

        logger.info(f"[MatrixStrategy] Starting execution for task {task_id} (chunk: {chunk_index}, mode: {compute_mode})")

        # 1. Parse MinIO URL
        if not raw_data_url.startswith("minio://"):
            raise ValueError(f"Invalid raw_data_url format: {raw_data_url}")

        parts = raw_data_url.replace("minio://", "").split("/", 1)
        bucket = parts[0]
        object_name = parts[1]

        # 2. Download ZIP payload
        temp_dir = os.path.join(tempfile.gettempdir(), "daemon_worker")
        os.makedirs(temp_dir, exist_ok=True)
        local_zip_path = os.path.join(temp_dir, f"{job_id}_math_payload.zip")

        downloaded = storage.download_data(bucket, object_name, local_zip_path)
        if not downloaded:
            raise Exception("Failed to download math payload from MinIO")

        # 3. Extract the target matrix partition
        extract_dir = os.path.join(temp_dir, f"{task_id}_extract")
        os.makedirs(extract_dir, exist_ok=True)

        target_file = None
        with zipfile.ZipFile(local_zip_path, 'r') as zf:
            json_files = [
                f for f in zf.namelist()
                if not f.endswith('/') and f.lower().endswith('.json')
            ]
            if not json_files:
                raise Exception("No JSON partition files found in math payload ZIP.")

            # Match chunk_index or pick modulo
            matched = [f for f in json_files if f"chunk_{chunk_index}.json" in f or f"partition_{chunk_index}.json" in f]
            target_file = matched[0] if matched else json_files[chunk_index % len(json_files)]
            zf.extract(target_file, extract_dir)

        json_path = os.path.join(extract_dir, target_file)
        with open(json_path, 'r') as f:
            partition_data = json.load(f)

        # 4. Extract matrices
        matrix_a_slice = np.array(partition_data.get("matrix_A_row_slice", []), dtype=np.float64)
        matrix_b = np.array(partition_data.get("matrix_B", []), dtype=np.float64)
        monte_carlo_samples = partition_data.get("monte_carlo_samples", 50000)

        device_used = "CPU (NumPy BLAS)"
        start_time = time.time()

        # 5. Compute Matrix Product: C_slice = A_slice @ B
        run_on_gpu = USE_GPU and compute_mode != "cpu_only"
        if run_on_gpu:
            try:
                import cupy as cp
                a_gpu = cp.asarray(matrix_a_slice)
                b_gpu = cp.asarray(matrix_b)
                c_gpu = cp.matmul(a_gpu, b_gpu)
                c_slice = cp.asnumpy(c_gpu)
                del a_gpu, b_gpu, c_gpu
                cp.get_default_memory_pool().free_all_blocks()
                device_used = "GPU (CuPy CUDA)"
            except Exception as e:
                logger.warning(f"[MatrixStrategy] GPU matmul failed ({e}), falling back to CPU")
                c_slice = np.matmul(matrix_a_slice, matrix_b)
                device_used = "CPU (fallback)"
        else:
            c_slice = np.matmul(matrix_a_slice, matrix_b)

        # 6. Monte Carlo numerical simulation workload
        if monte_carlo_samples > 0:
            rand_points = np.random.uniform(-1.0, 1.0, (min(monte_carlo_samples, 100000), 2))
            inside_circle = np.sum((rand_points[:, 0]**2 + rand_points[:, 1]**2) <= 1.0)
            pi_estimate = 4.0 * inside_circle / len(rand_points)
        else:
            pi_estimate = 3.14159

        elapsed_seconds = round(time.time() - start_time, 4)
        elapsed_ms = int(elapsed_seconds * 1000)

        # Numerical integrity checks
        frobenius_norm = float(np.linalg.norm(c_slice))

        result_payload = {
            "task_id": task_id,
            "job_id": job_id,
            "chunk_index": chunk_index,
            "status": "completed",
            "operation": "distributed_block_matrix_multiplication",
            "device": device_used,
            "slice_shape": list(c_slice.shape),
            "frobenius_norm": frobenius_norm,
            "pi_monte_carlo": round(float(pi_estimate), 6),
            "compute_time_ms": elapsed_ms,
            "result_matrix_slice": c_slice.tolist()
        }

        # 7. Upload result JSON to MinIO
        result_path = os.path.join(extract_dir, f"{task_id}_matrix_result.json")
        with open(result_path, 'w') as f:
            json.dump(result_payload, f)

        result_object = f"{job_id}/results/{task_id}_matrix_block_{chunk_index}.json"
        uploaded_url = storage.upload_result(bucket, result_path, result_object)
        logger.info(f"[MatrixStrategy] Uploaded result to {uploaded_url} in {elapsed_seconds}s on [{device_used}]")

        return {
            "task_id": task_id,
            "status": "success",
            "device": device_used,
            "processing_time": elapsed_seconds,
            "result_url": uploaded_url,
            "frobenius_norm": frobenius_norm
        }
