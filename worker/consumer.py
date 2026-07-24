import pika
import json
import logging
import os
import requests
from strategies.dummy_math import DummyMathStrategy
from strategies.image_processing import ImageProcessingStrategy

logger = logging.getLogger(__name__)

class TaskConsumer:
    def __init__(self, pool_id: str, orchestrator_url: str):
        self.pool_id = pool_id
        self.orchestrator_url = orchestrator_url
        self.connection = None
        self.channel = None

    def connect(self, rabbitmq_url: str):
        try:
            parameters = pika.URLParameters(rabbitmq_url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Ensure the queue exists
            self.channel.queue_declare(queue=self.pool_id, durable=True)
            logger.info(f"Worker connected to RabbitMQ. Listening on pool: {self.pool_id}")
            
            # Set QOS so worker only gets 1 task at a time
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.pool_id,
                on_message_callback=self.process_message
            )
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")

    def process_message(self, ch, method, properties, body):
        try:
            task_payload = json.loads(body)
            task_id = task_payload.get('task_id')
            job_id = task_payload.get('job_id')
            logger.info(f"Received task: {task_id}")
            
            # Check if job is halted or completed
            try:
                job_res = requests.get(f"{self.orchestrator_url}/api/v1/jobs/{job_id}")
                if job_res.ok:
                    job_data = job_res.json()
                    if job_data.get("status") in ["halted", "completed"]:
                        logger.info(f"Job {job_id} is {job_data.get('status')}. Discarding task {task_id}.")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
            except Exception as e:
                logger.warning(f"Failed to check job status, proceeding with task: {e}")
            
            # Execute the correct strategy based on job type
            job_type = task_payload.get("job_type", "math")
            
            if job_type == "image":
                result = ImageProcessingStrategy.execute(task_payload)
            else:
                result = DummyMathStrategy.execute(task_payload)
            
            # Acknowledge the message (removes it from queue)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
            # Ping Orchestrator to update progress
            job_id = task_payload.get("job_id")
            total_chunks = task_payload.get("total_chunks", 10)
            
            try:
                requests.post(
                    f"{self.orchestrator_url}/api/v1/jobs/{job_id}/task_complete",
                    json={"total_chunks": total_chunks}
                )
                logger.info(f"Pinged Orchestrator with completion for task {task_payload.get('task_id')}")
            except Exception as ping_err:
                logger.error(f"Failed to ping orchestrator: {ping_err}")
                
            logger.info(f"Successfully processed and acknowledged task {task_payload.get('task_id')}")
            
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            # Reject message and requeue so another worker can try it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_listening(self):
        if self.channel:
            logger.info("Starting to consume tasks...")
            self.channel.start_consuming()
