import pika
import json
import logging

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            # Connects to the local RabbitMQ Docker container
            parameters = pika.URLParameters('amqp://guest:guest@localhost:5672/')
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info("Successfully connected to RabbitMQ.")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")

    def publish_task(self, pool_id: str, task_payload: dict):
        if not self.channel:
            self.connect()
            
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

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed.")

rabbitmq_client = RabbitMQClient()
