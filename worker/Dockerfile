FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# NVIDIA Container Runtime settings
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Install Python 3 + pip + build headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app

# Install dependencies first for Docker caching
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Copy worker source code
COPY . .

# Environment variables that volunteers can pass via docker run
ENV ORCHESTRATOR_URL="http://host.docker.internal:8000"
ENV RABBITMQ_URL="amqp://guest:guest@host.docker.internal:5672/"
ENV MINIO_URL="http://host.docker.internal:9090"
ENV POOL_ID="public_pool"

# Start the worker
CMD ["python", "-u", "main.py"]
