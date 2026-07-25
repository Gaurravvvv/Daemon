FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.11 + pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3.11 /usr/bin/python

WORKDIR /app

# Install dependencies first for Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker source code
COPY . .

# Environment variables that volunteers can pass via docker run
ENV ORCHESTRATOR_URL="http://host.docker.internal:8000"
ENV RABBITMQ_URL="amqp://guest:guest@host.docker.internal:5672/"
ENV MINIO_URL="http://host.docker.internal:9000"
ENV POOL_ID="public_pool"

# Start the worker
CMD ["python", "-u", "main.py"]
