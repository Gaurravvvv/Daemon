import os
import sys
import logging
import requests
from consumer import TaskConsumer

# Setup simple console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Worker - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def probe_gpu() -> dict:
    """Detect GPU hardware and return info dict."""
    try:
        import cupy as cp  # type: ignore
        device_count = cp.cuda.runtime.getDeviceCount()
        if device_count == 0:
            return {"has_gpu": False}
        
        props = cp.cuda.runtime.getDeviceProperties(0)
        device_name = props.get("name", b"Unknown GPU")
        if isinstance(device_name, bytes):
            device_name = device_name.decode("utf-8", errors="replace")
        
        total_mem = props.get("totalGlobalMem", 0)
        vram_gb = round(total_mem / (1024**3), 1)
        
        cuda_ver = cp.cuda.runtime.runtimeGetVersion()
        cuda_major = cuda_ver // 1000
        cuda_minor = (cuda_ver % 1000) // 10
        
        return {
            "has_gpu": True,
            "device_name": device_name,
            "vram_gb": vram_gb,
            "cuda_version": f"{cuda_major}.{cuda_minor}",
            "device_count": device_count,
        }
    except ImportError:
        return {"has_gpu": False, "reason": "CuPy not installed"}
    except Exception as e:
        return {"has_gpu": False, "reason": str(e)}


def main():
    orchestrator_url = os.environ.get("ORCHESTRATOR_URL", "http://localhost:8000")
    rabbitmq_url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    pool_id = os.environ.get("POOL_ID", "public_pool")
    
    logger.info("=========================================")
    logger.info("         DAEMON WORKER BOOTING           ")
    logger.info("=========================================")
    logger.info(f"Target Orchestrator: {orchestrator_url}")
    logger.info(f"Assigned Pool ID: {pool_id}")
    
    # GPU Hardware Probe
    gpu_info = probe_gpu()
    if gpu_info["has_gpu"]:
        logger.info(f"GPU DETECTED: {gpu_info['device_name']} ({gpu_info['vram_gb']}GB VRAM, CUDA {gpu_info['cuda_version']})")
    else:
        logger.info(f"CPU MODE — No GPU detected ({gpu_info.get('reason', 'no CUDA device')})")
    
    # Initialize and start consuming tasks
    consumer = TaskConsumer(pool_id=pool_id, orchestrator_url=orchestrator_url, gpu_info=gpu_info)
    consumer.connect(rabbitmq_url=rabbitmq_url)
    
    logger.info(f"Worker ID: {consumer.worker_id}")
    
    # Build join message with hardware info
    if gpu_info["has_gpu"]:
        hw_tag = f"[GPU: {gpu_info['device_name']} ({gpu_info['vram_gb']}GB VRAM)]"
    else:
        hw_tag = "[CPU MODE]"
    
    join_msg = f"{consumer.worker_id} connected to pool '{pool_id}' {hw_tag}"
    
    # Broadcast join event to ALL active jobs on this pool
    try:
        res = requests.get(f"{orchestrator_url}/api/v1/jobs", timeout=5)
        if res.ok:
            jobs = res.json().get("jobs", [])
            for job in jobs:
                if job.get("pool_id") == pool_id and job.get("status") == "processing":
                    requests.post(
                        f"{orchestrator_url}/api/v1/jobs/{job['job_id']}/events",
                        json={
                            "source": "WORKER",
                            "level": "SYSTEM",
                            "message": join_msg,
                            "worker_id": consumer.worker_id,
                        },
                        timeout=3,
                    )
    except Exception as e:
        logger.warning(f"Could not broadcast join event: {e}")
    
    try:
        consumer.start_listening()
    except KeyboardInterrupt:
        logger.info("Worker shutting down gracefully...")
        if consumer.connection:
            consumer.connection.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
