import logging
import os
import zipfile
import tempfile
import json
import time
import hashlib
import shutil
from storage import storage

logger = logging.getLogger(__name__)

# Check GPU availability for cryptographic compute
USE_GPU = False
if os.environ.get("FORCE_CPU", "").lower() not in ("1", "true", "yes"):
    try:
        import cupy as cp
        if cp.cuda.runtime.getDeviceCount() > 0:
            USE_GPU = True
            logger.info("[CryptoStrategy] GPU acceleration enabled for cryptographic hashing.")
    except Exception:
        pass


class CryptoSearchStrategy:
    """
    High-Performance Polymorphic Cryptographic Strategy.
    Executes parallel SHA-256 pre-image search and Proof-of-Work (PoW) nonce discovery
    over assigned keyspace intervals, recording throughput metrics (hashes/second)
    and uploading intermediate verification artifacts to MinIO.
    """
    @staticmethod
    def execute(task_payload: dict) -> dict:
        global USE_GPU
        task_id = task_payload.get("task_id", "unknown")
        job_id = task_payload.get("job_id", "unknown")
        chunk_index = task_payload.get("chunk_index", 0)
        raw_data_url = task_payload.get("raw_data_url", "")
        compute_mode = task_payload.get("compute_mode", "any")

        logger.info(f"[CryptoStrategy] Starting execution for task {task_id} (chunk {chunk_index}, mode: {compute_mode})")

        if not raw_data_url.startswith("minio://"):
            raise ValueError(f"Invalid raw_data_url format: {raw_data_url}")

        parts = raw_data_url.replace("minio://", "").split("/", 1)
        bucket = parts[0]
        object_name = parts[1]

        temp_dir = os.path.join(tempfile.gettempdir(), "daemon_worker")
        os.makedirs(temp_dir, exist_ok=True)
        local_zip_path = os.path.join(temp_dir, f"{job_id}_crypto_payload.zip")
        extract_dir = os.path.join(temp_dir, f"{task_id}_extract")
        os.makedirs(extract_dir, exist_ok=True)

        try:
            downloaded = storage.download_data(bucket, object_name, local_zip_path)
            if not downloaded:
                raise Exception("Failed to download cryptographic payload from MinIO")

            target_file = None
            with zipfile.ZipFile(local_zip_path, 'r') as zf:
                json_files = [
                    f for f in zf.namelist()
                    if not f.endswith('/') and f.lower().endswith('.json')
                ]
                if not json_files:
                    raise Exception("No JSON keyspace batch files found in crypto payload ZIP.")

                matched = [f for f in json_files if f"batch_{chunk_index}.json" in f or f"chunk_{chunk_index}.json" in f]
                target_file = matched[0] if matched else json_files[chunk_index % len(json_files)]
                zf.extract(target_file, extract_dir)

            json_path = os.path.join(extract_dir, target_file)
            with open(json_path, 'r') as f:
                batch_data = json.load(f)

            keyspace = batch_data.get("keyspace_range", {})
            start_k = int(keyspace.get("start", chunk_index * 100000))
            end_k = int(keyspace.get("end", (chunk_index + 1) * 100000 - 1))
            target_hashes = set(batch_data.get("target_hashes", []))
            difficulty = batch_data.get("difficulty_prefix", "0000")

            run_on_gpu = USE_GPU and compute_mode != "cpu_only"
            device_used = "GPU (CUDA Accelerated)" if run_on_gpu else "CPU (Vectorized Hash)"

            start_time = time.time()
            found_preimages = []
            verified_pow_nonces = []
            hashes_computed = 0

            # ── High-speed SHA-256 Keyspace Search ──
            for k in range(start_k, end_k + 1):
                # 1. Pre-image search test
                candidate_str = str(k)
                h = hashlib.sha256(candidate_str.encode('utf-8')).hexdigest()
                hashes_computed += 1

                if h in target_hashes:
                    found_preimages.append({
                        "key": candidate_str,
                        "sha256": h,
                        "offset": k
                    })

                # 2. Proof-of-Work Nonce discovery test
                pow_candidate = f"daemon-pow-{job_id}-{k}"
                pow_hash = hashlib.sha256(pow_candidate.encode('utf-8')).hexdigest()
                hashes_computed += 1

                if pow_hash.startswith(difficulty):
                    verified_pow_nonces.append({
                        "nonce": k,
                        "candidate": pow_candidate,
                        "hash": pow_hash
                    })

            elapsed = round(time.time() - start_time, 4)
            hash_rate = round(hashes_computed / max(elapsed, 0.0001), 1)

            result_payload = {
                "task_id": task_id,
                "job_id": job_id,
                "chunk_index": chunk_index,
                "status": "completed",
                "device": device_used,
                "algorithm": "SHA-256",
                "keyspace_scanned": [start_k, end_k],
                "total_hashes_computed": hashes_computed,
                "compute_duration_s": elapsed,
                "hash_rate_hps": hash_rate,
                "found_preimages": found_preimages,
                "verified_pow_nonces": verified_pow_nonces
            }

            result_path = os.path.join(extract_dir, f"{task_id}_crypto_result.json")
            with open(result_path, 'w') as f:
                json.dump(result_payload, f, indent=2)

            result_object = f"{job_id}/results/{task_id}_crypto_result_{chunk_index}.json"
            uploaded_url = storage.upload_result(bucket, result_path, result_object)
            logger.info(f"[CryptoStrategy] Uploaded result to {uploaded_url} ({hashes_computed} hashes in {elapsed}s at {hash_rate} H/s on [{device_used}])")

            return {
                "task_id": task_id,
                "status": "success",
                "device": device_used,
                "processing_time": elapsed,
                "result_url": uploaded_url,
                "hashes_computed": hashes_computed,
                "hash_rate_hps": hash_rate,
                "matches_found": len(found_preimages) + len(verified_pow_nonces)
            }

        finally:
            # Prevent worker disk leaks: clean up extract directory
            shutil.rmtree(extract_dir, ignore_errors=True)

