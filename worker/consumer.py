import pika
import json
import logging
import os
import requests
import traceback
import uuid
import time
from strategies.dummy_math import DummyMathStrategy
from strategies.image_processing import ImageProcessingStrategy

logger = logging.getLogger(__name__)

class TaskConsumer:
    def __init__(self, pool_id: str, orchestrator_url: str, gpu_info: dict = None):
        self.pool_id = pool_id
        self.orchestrator_url = orchestrator_url
        self.worker_id = f"NODE-{uuid.uuid4().hex[:6].upper()}"
        self.gpu_info = gpu_info or {"has_gpu": False}
        self.connection = None
        self.channel = None

    def _emit(self, job_id: str, level: str, message: str):
        """Fire-and-forget event push to the Orchestrator."""
        try:
            requests.post(
                f"{self.orchestrator_url}/api/v1/jobs/{job_id}/events",
                json={
                    "source": "WORKER",
                    "level": level,
                    "message": message,
                    "worker_id": self.worker_id,
                },
                timeout=3,
            )
        except Exception:
            pass  # never let event logging kill the worker

    def connect(self, rabbitmq_url: str):
        try:
            parameters = pika.URLParameters(rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Ensure the queue exists
            self.channel.queue_declare(queue=self.pool_id, durable=True)
            logger.info(f"Created channel={self.channel.channel_number}")
            logger.info(f"Worker connected to RabbitMQ. Listening on pool: {self.pool_id}")
            
            # Set QOS so worker only gets 1 task at a time
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.pool_id,
                on_message_callback=self.process_message
            )
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")

    def _check_compute_eligibility(self, task_payload: dict) -> bool:
        """Check if this worker meets the job's compute_mode requirement."""
        compute_mode = task_payload.get("compute_mode", "any")
        
        if compute_mode == "gpu_only" and not self.gpu_info.get("has_gpu"):
            return False
        
        # cpu_only and any are always eligible
        return True

    def process_message(self, ch, method, properties, body):
        task_payload = None
        try:
            task_payload = json.loads(body)
            task_id = task_payload.get('task_id', 'unknown')
            job_id = task_payload.get('job_id', 'unknown')
            chunk_index = task_payload.get('chunk_index', '?')
            total_chunks = task_payload.get('total_chunks', 10)
            job_type = task_payload.get("job_type", "math")
            compute_mode = task_payload.get("compute_mode", "any")
            
            logger.info(f"Received task: {task_id} (job: {job_id}, compute: {compute_mode})")
            
            # ── Compute Mode Gate ──
            if not self._check_compute_eligibility(task_payload):
                logger.info(f"Task {task_id} requires GPU but this worker has no GPU. Requeuing...")
                self._emit(job_id, "WARNING", f"{self.worker_id} skipped chunk {chunk_index + 1} — requires GPU, this node is CPU-only. Requeued.")
                # NACK + requeue so a GPU worker can pick it up
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                return
            
            self._emit(job_id, "INFO", f"{self.worker_id} picked up chunk {chunk_index + 1}/{total_chunks}")
            
            # Check if job is halted or completed before doing work
            try:
                job_res = requests.get(
                    f"{self.orchestrator_url}/api/v1/jobs/{job_id}",
                    timeout=5
                )
                if job_res.ok:
                    job_data = job_res.json()
                    if job_data.get("status") in ["halted", "completed"]:
                        logger.info(f"Job {job_id} is {job_data.get('status')}. Discarding task {task_id}.")
                        self._emit(job_id, "WARNING", f"{self.worker_id} discarded chunk {chunk_index + 1} — job is {job_data.get('status').upper()}")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
            except requests.exceptions.RequestException as e:
                logger.warning(f"Could not reach orchestrator for status check, proceeding anyway: {e}")
            
            # Determine device tag for events
            device_tag = "GPU" if self.gpu_info.get("has_gpu") else "CPU"
            
            # Execute the correct strategy
            logger.info(f"Executing strategy '{job_type}' for task {task_id} on [{device_tag}]...")
            self._emit(job_id, "INFO", f"{self.worker_id} processing chunk {chunk_index + 1} [{device_tag}] (strategy: {job_type})")
            
            start_time = time.time()
            
            if job_type == "image":
                result = ImageProcessingStrategy.execute(task_payload)
            else:
                result = DummyMathStrategy.execute(task_payload)
            
            elapsed = round(time.time() - start_time, 2)
            actual_device = result.get("device", device_tag)
            
            logger.info(f"Strategy completed for task {task_id}. Result: {result.get('status', 'unknown')}")
            
            # Acknowledge the message (removes it from queue)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            # Ping Orchestrator to update progress
            try:
                resp = requests.post(
                    f"{self.orchestrator_url}/api/v1/jobs/{job_id}/task_complete",
                    json={"total_chunks": total_chunks},
                    timeout=5
                )
                if resp.ok:
                    progress_data = resp.json()
                    new_progress = progress_data.get('progress', '?')
                    logger.info(f"Progress updated for job {job_id}: {new_progress}%")
                    self._emit(job_id, "SUCCESS", f"{self.worker_id} completed chunk {chunk_index + 1}/{total_chunks} [{actual_device}] in {elapsed}s — progress: {new_progress}%")
                else:
                    logger.warning(f"Orchestrator returned {resp.status_code} for progress update")
                    self._emit(job_id, "SUCCESS", f"{self.worker_id} completed chunk {chunk_index + 1}/{total_chunks} [{actual_device}] in {elapsed}s")
            except requests.exceptions.RequestException as ping_err:
                logger.error(f"Failed to ping orchestrator for progress: {ping_err}")
                self._emit(job_id, "SUCCESS", f"{self.worker_id} completed chunk {chunk_index + 1}/{total_chunks} [{actual_device}] in {elapsed}s")
                
            logger.info(f"Task {task_id} fully complete.")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse task message body: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            logger.error(traceback.format_exc())
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            # Report failure
            if task_payload:
                job_id = task_payload.get("job_id")
                chunk_index = task_payload.get("chunk_index", "?")
                total_chunks = task_payload.get("total_chunks", 10)
                self._emit(job_id, "ERROR", f"{self.worker_id} FAILED on chunk {chunk_index + 1}: {str(e)[:100]}")
                try:
                    requests.post(
                        f"{self.orchestrator_url}/api/v1/jobs/{job_id}/task_complete",
                        json={"total_chunks": total_chunks},
                        timeout=5
                    )
                except Exception:
                    pass

    def start_listening(self):
        if self.channel:
            logger.info("Starting to consume tasks...")
            self.channel.start_consuming()
        else:
            logger.error("Cannot start listening - channel is not initialized. Check RabbitMQ connection.")
