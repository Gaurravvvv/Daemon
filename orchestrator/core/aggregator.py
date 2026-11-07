import asyncio
import logging
import io
import json
import zipfile
import numpy as np
from datetime import datetime, timezone
from services.database import db
from services.storage import storage
from services.redis_client import redis_manager

logger = logging.getLogger(__name__)

class StateAggregator:
    @staticmethod
    async def stitch_results(job_id: str):
        """
        Gathers all micro-task output artifacts from MinIO, stitches them
        into a unified deliverable (composite matrix, consolidated crypto proof, 
        or organized image bundle), and writes the master deliverable archive.
        """
        logger.info(f"Stitching results for job {job_id}...")
        job = await db.db.jobs.find_one({"job_id": job_id})
        if not job:
            logger.warning(f"Job {job_id} not found for stitching.")
            return

        job_type = str(job.get("job_type", "image")).lower()
        files = storage.list_results(job_id)
        
        master_zip_buffer = io.BytesIO()
        summary_metadata = {
            "job_id": job_id,
            "job_name": job.get("job_name", ""),
            "job_type": job_type,
            "total_chunks": job.get("total_chunks", 0),
            "completed_chunks": job.get("completed_chunks", 0),
            "stitched_at": datetime.now(timezone.utc).isoformat(),
            "artifact_count": len(files)
        }

        try:
            with zipfile.ZipFile(master_zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                # 1. Math / Matrix Workloads: Stitch sub-blocks into full composite matrix
                if job_type in ("math", "matrix", "matrix_multiplication"):
                    slices = []
                    total_time_ms = 0
                    monte_carlo_estimates = []

                    for f in files:
                        file_bytes = storage.download_file(f["key"])
                        zf.writestr(f"chunks/{f['filename']}", file_bytes)
                        try:
                            data = json.loads(file_bytes.decode('utf-8'))
                            if "result_matrix_slice" in data:
                                slices.append((data.get("chunk_index", 0), np.array(data["result_matrix_slice"])))
                            if "compute_time_ms" in data:
                                total_time_ms += data["compute_time_ms"]
                            if "pi_monte_carlo" in data:
                                monte_carlo_estimates.append(data["pi_monte_carlo"])
                        except Exception:
                            pass

                    # Sort slices in chunk order and vertically stack
                    if slices:
                        slices.sort(key=lambda x: x[0])
                        full_matrix = np.vstack([s[1] for s in slices])
                        composite_result = {
                            "job_id": job_id,
                            "composite_shape": list(full_matrix.shape),
                            "frobenius_norm": float(np.linalg.norm(full_matrix)),
                            "total_compute_time_ms": total_time_ms,
                            "avg_monte_carlo_pi": round(float(np.mean(monte_carlo_estimates)), 6) if monte_carlo_estimates else None,
                            "matrix_elements": full_matrix.tolist()
                        }
                        composite_json = json.dumps(composite_result, indent=2).encode('utf-8')
                        zf.writestr("composite_matrix_result.json", composite_json)
                        summary_metadata["matrix_shape"] = list(full_matrix.shape)
                        summary_metadata["frobenius_norm"] = composite_result["frobenius_norm"]

                # 2. Cryptographic Workloads: Consolidate found keys & hash rates
                elif job_type in ("crypto", "cryptography", "pow"):
                    all_found = []
                    total_hashes = 0
                    total_duration = 0.0

                    for f in files:
                        file_bytes = storage.download_file(f["key"])
                        zf.writestr(f"batches/{f['filename']}", file_bytes)
                        try:
                            data = json.loads(file_bytes.decode('utf-8'))
                            if "found_preimages" in data:
                                all_found.extend(data["found_preimages"])
                            total_hashes += data.get("total_hashes_computed", 0)
                            total_duration += data.get("compute_duration_s", 0.0)
                        except Exception:
                            pass

                    crypto_summary = {
                        "job_id": job_id,
                        "total_preimages_found": len(all_found),
                        "found_preimages": all_found,
                        "total_hashes_computed": total_hashes,
                        "aggregate_duration_seconds": round(total_duration, 3),
                        "avg_cluster_hash_rate_hps": round(total_hashes / max(total_duration, 0.001), 1)
                    }
                    zf.writestr("consolidated_crypto_summary.json", json.dumps(crypto_summary, indent=2).encode('utf-8'))
                    summary_metadata["crypto_matches"] = len(all_found)
                    summary_metadata["total_hashes"] = total_hashes

                # 3. Image Workloads: Organize into edges & enhanced directories
                else:
                    for f in files:
                        file_bytes = storage.download_file(f["key"])
                        fname = f["filename"]
                        if "edges_" in fname:
                            zf.writestr(f"edges/{fname}", file_bytes)
                        elif "enhanced_" in fname:
                            zf.writestr(f"enhanced/{fname}", file_bytes)
                        else:
                            zf.writestr(f"raw/{fname}", file_bytes)

                # Write manifest summary into the master ZIP
                zf.writestr("MANIFEST.json", json.dumps(summary_metadata, indent=2).encode('utf-8'))

            master_zip_bytes = master_zip_buffer.getvalue()
            master_key = f"{job_id}/results/{job_id}_master_results.zip"
            final_url = storage.upload_bytes(master_zip_bytes, master_key, content_type="application/zip")

            await db.db.jobs.update_one(
                {"job_id": job_id},
                {"$set": {
                    "status": "completed",
                    "progress": 100,
                    "final_result_url": final_url,
                    "stitched": True,
                    "stitched_at": datetime.now(timezone.utc).isoformat()
                }}
            )

            # Emit success event to timeline
            event = {
                "job_id": job_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "ORCHESTRATOR",
                "level": "SUCCESS",
                "message": f"Artifacts successfully stitched into master archive ({len(files)} files, {len(master_zip_bytes)//1024} KB). Ready for download."
            }
            await db.db.job_events.insert_one(event)
            logger.info(f"Job {job_id} successfully stitched into {final_url}!")

        except Exception as e:
            logger.error(f"Failed to stitch results for job {job_id}: {e}", exc_info=True)


async def monitor_jobs():
    """
    Continuous background loop that:
    1. Monitors jobs where all tasks have finished to trigger the StateAggregator.
    2. Reaps expired worker leases (sub-15s TTL churn recovery) and updates worker registry status.
    """
    logger.info("Starting background state aggregator & node reaper loop...")
    redis_manager.connect()

    while True:
        try:
            # 1. Check for processing jobs that have completed all chunks but aren't stitched yet
            cursor = db.db.jobs.find({"status": "processing"})
            async for job in cursor:
                total = job.get("total_chunks", 1)
                completed = job.get("completed_chunks", 0)
                if completed >= total and total > 0:
                    logger.info(f"Job {job['job_id']} reached 100% completion ({completed}/{total}). Triggering stitcher...")
                    await StateAggregator.stitch_results(job["job_id"])

            # 2. Ephemeral Worker Churn Reaper: Update worker registry status based on active leases
            active_ids = set(redis_manager.get_active_workers())
            worker_cursor = db.db.workers.find({"status": "online"})
            async for worker in worker_cursor:
                wid = worker.get("worker_id")
                if wid and wid not in active_ids:
                    # Lease expired: mark offline
                    await db.db.workers.update_one(
                        {"worker_id": wid},
                        {"$set": {"status": "offline", "last_churn": datetime.now(timezone.utc).isoformat()}}
                    )
                    logger.info(f"[Node Reaper] Worker {wid} lease expired (churn detected). Node marked OFFLINE.")

        except Exception as e:
            logger.error(f"Error in aggregator & reaper loop: {e}")

        # Poll every 4 seconds
        await asyncio.sleep(4)
