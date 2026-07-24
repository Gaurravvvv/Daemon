import os
import sys
import logging
from consumer import TaskConsumer

# Setup simple console logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Worker - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Fetch environment variables
    # For frictionless local development, we fallback to defaults
    orchestrator_url = os.environ.get("ORCHESTRATOR_URL", "http://localhost:8000")
    rabbitmq_url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    pool_id = os.environ.get("POOL_ID", "public_pool")
    
    logger.info("=========================================")
    logger.info("         DAEMON WORKER BOOTING           ")
    logger.info("=========================================")
    logger.info(f"Target Orchestrator: {orchestrator_url}")
    logger.info(f"Assigned Pool ID: {pool_id}")
    
    # Normally we would POST to Orchestrator to register here (Phase 1 endpoint)
    # requests.post(f"{orchestrator_url}/api/v1/workers/register", json={...})
    
    # Initialize and start consuming tasks
    consumer = TaskConsumer(pool_id=pool_id, orchestrator_url=orchestrator_url)
    consumer.connect(rabbitmq_url=rabbitmq_url)
    
    try:
        consumer.start_listening()
    except KeyboardInterrupt:
        logger.info("Worker shutting down gracefully...")
        if consumer.connection:
            consumer.connection.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
