FROM python:3.13-slim

WORKDIR /app

# Install dependencies first for Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker source code
COPY . .

# Environment variables that volunteers can pass via docker run
ENV ORCHESTRATOR_URL="http://host.docker.internal:8000"
ENV RABBITMQ_URL="amqp://guest:guest@host.docker.internal:5672/"
ENV POOL_ID="public_pool"

# Start the worker
CMD ["python", "-u", "main.py"]
