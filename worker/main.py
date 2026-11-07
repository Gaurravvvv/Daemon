import os
import sys
import logging
import threading
import time
import requests
from consumer import TaskConsumer

# Setup simple console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Worker - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def probe_gpu() -> dict:
    """Detect GPU hardware, test kernel execution, and return info dict."""
    if os.environ.get("FORCE_CPU", "").lower() in ("1", "true", "yes"):
        return {"has_gpu": False, "reason": "FORCE_CPU environment variable enabled"}

    try:
        import cupy as cp  # type: ignore
        device_count = cp.cuda.runtime.getDeviceCount()
        if device_count == 0:
            return {"has_gpu": False, "reason": "No CUDA-capable device detected"}
        
        device_id = int(os.environ.get("GPU_DEVICE_ID", "0"))
        if device_id >= device_count:
            device_id = 0
        cp.cuda.Device(device_id).use()
        
        props = cp.cuda.runtime.getDeviceProperties(device_id)
        device_name = props.get("name", b"Unknown GPU")
        if isinstance(device_name, bytes):
            device_name = device_name.decode("utf-8", errors="replace")
        
        total_mem = props.get("totalGlobalMem", 0)
        vram_gb = round(total_mem / (1024**3), 1)
        
        cuda_ver = cp.cuda.runtime.runtimeGetVersion()
        cuda_major = cuda_ver // 1000
        cuda_minor = (cuda_ver % 1000) // 10

        # Smoke-test active GPU memory allocation & kernel execution
        test_arr = cp.zeros(2, dtype=cp.float32)
        test_arr += 1.0
        cp.cuda.Stream.null.synchronize()
        del test_arr
        cp.get_default_memory_pool().free_all_blocks()
        
        return {
            "has_gpu": True,
            "device_id": device_id,
            "device_name": device_name,
            "vram_gb": vram_gb,
            "cuda_version": f"{cuda_major}.{cuda_minor}",
            "device_count": device_count,
        }
    except ImportError:
        return {"has_gpu": False, "reason": "CuPy not installed"}
    except Exception as e:
        return {"has_gpu": False, "reason": f"CUDA compute test failed: {e}"}


def start_heartbeat_thread(orchestrator_url: str, worker_id: str, pool_id: str, interval: int = 5):
    """Background sliding-window heartbeat daemon (5s cadence, 15s server TTL)."""
    def _heartbeat_loop():
        while True:
            try:
                requests.post(
                    f"{orchestrator_url}/api/v1/workers/{worker_id}/heartbeat?pool_id={pool_id}",
                    timeout=3
                )
            except Exception:
                pass
            time.sleep(interval)

    t = threading.Thread(target=_heartbeat_loop, daemon=True, name="WorkerHeartbeat")
    t.start()
    logger.info(f"Heartbeat leasing thread online ({interval}s interval).")
    return t


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
    
    # Register worker with Orchestrator
    try:
        capabilities = ["math", "crypto"]
        if gpu_info["has_gpu"]:
            capabilities.extend(["image", "gpu"])
        else:
            capabilities.append("image")
            
        reg_payload = {
            "worker_id": consumer.worker_id,
            "pool_id": pool_id,
            "capabilities": capabilities,
            "system_info": {
                "has_gpu": gpu_info["has_gpu"],
                "gpu_name": gpu_info.get("device_name", "None"),
                "vram_gb": gpu_info.get("vram_gb", 0),
                "platform": sys.platform
            }
        }
        reg_res = requests.post(f"{orchestrator_url}/api/v1/workers/register", json=reg_payload, timeout=5)
        if reg_res.ok:
            heartbeat_interval = reg_res.json().get("heartbeat_interval", 5)
            logger.info(f"Successfully registered node {consumer.worker_id} with Orchestrator.")
            # Start background lease renewal
            start_heartbeat_thread(orchestrator_url, consumer.worker_id, pool_id, interval=heartbeat_interval)
    except Exception as e:
        logger.warning(f"Could not register worker with Orchestrator: {e}")
        # Start heartbeat anyway to recover if orchestrator boots shortly after
        start_heartbeat_thread(orchestrator_url, consumer.worker_id, pool_id, interval=5)

    try:
        consumer.start_listening()
    except KeyboardInterrupt:
        logger.info("Worker shutting down gracefully...")
        if consumer.connection:
            consumer.connection.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
