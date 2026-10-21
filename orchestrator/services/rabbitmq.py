import os
import pika
import json
import logging

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

    def connect(self):
        try:
            parameters = pika.URLParameters(self.url)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Successfully connected to RabbitMQ.")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None

    def publish_task(self, pool_id: str, task_payload: dict):
        if not self.connection or self.connection.is_closed or not self.channel or self.channel.is_closed:
            self.connect()
            
        if not self.channel:
            raise ConnectionError("Cannot publish task: RabbitMQ channel is not available.")

        try:
            # Ensure the queue for this pool exists
            self.channel.queue_declare(queue=pool_id, durable=True)
            
            # Publish the task
            self.channel.basic_publish(
                exchange='',
                routing_key=pool_id,
                body=json.dumps(task_payload),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            logger.info(f"Published task to queue '{pool_id}'")
        except Exception as e:
            logger.warning(f"Publish failed ({e}), reconnecting and retrying...")
            self.connect()
            if not self.channel:
                raise ConnectionError("Reconnection to RabbitMQ failed.")
            self.channel.queue_declare(queue=pool_id, durable=True)
            self.channel.basic_publish(
                exchange='',
                routing_key=pool_id,
                body=json.dumps(task_payload),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
            logger.info(f"Successfully re-published task to queue '{pool_id}'")

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed.")

rabbitmq_client = RabbitMQClient()
