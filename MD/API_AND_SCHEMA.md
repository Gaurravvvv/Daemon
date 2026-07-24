# API Endpoints & JSON Schemas

This document defines the communication contract between the Client (Admin Dashboard), the Master Orchestrator, and the Worker Daemons. 

Because we are using MinIO for object storage, notice how the payloads *never* contain raw data—only `URL` references!

---

## 1. REST API Endpoints (FastAPI Orchestrator)

These endpoints are exposed by the Master Orchestrator. They handle Client requests and initial Worker registration.

### `POST /api/v1/jobs/submit`
Used by the Admin Dashboard to submit a massive new job.
- **Request Payload:**
```json
{
  "job_name": "Massive Image Batch 1",
  "job_type": "image_processing",
  "pool_id": "user_1_private_pool",
  "raw_data_url": "minio://bucket-name/raw_dataset_1.zip",
  "parameters": {
    "filter_type": "grayscale",
    "resolution": "1080p"
  }
}
```
- **Response:** `202 Accepted` -> `{ "job_id": "job-abc-123", "status": "partitioning" }`

### `POST /api/v1/workers/register`
When you run `docker run daemon-worker`, the daemon immediately hits this endpoint to announce it is alive and ready to work.
- **Request Payload:**
```json
{
  "worker_id": "worker-node-77x",
  "pool_id": "user_1_private_pool",
  "hardware_specs": {
    "cpu_cores": 8,
    "memory_gb": 16
  }
}
```
- **Response:** `200 OK` -> `{ "assigned_routing_key": "queue_worker_77x", "status": "registered" }`

### `GET /api/v1/metrics/live` (or WebSockets)
Used by the React Admin Panel to draw the graphs and progress bars.
- **Response:**
```json
{
  "active_workers": 42,
  "jobs_in_progress": 2,
  "tasks_completed_per_second": 15.5,
  "system_health": "OPTIMAL"
}
```

---

## 2. Message Broker Payload Schemas (RabbitMQ)

This is the ultra-fast JSON communication happening over RabbitMQ.

### A. The "Push Task" Message (Orchestrator -> Worker)
The Orchestrator pushes this directly into the specific queue assigned to a worker.
```json
{
  "task_id": "task-xyz-889",
  "job_id": "job-abc-123",
  "job_type": "image_processing",
  "action": "EXECUTE",
  
  // The worker will download its specific chunk from this URL
  "chunk_data_url": "minio://bucket-name/chunks/job-abc-123/chunk-889.zip",
  
  "parameters": {
    "filter_type": "grayscale"
  }
}
```

### B. The "Task Result" Message (Worker -> Orchestrator)
Sent back to the Master when the worker finishes processing its chunk.
```json
{
  "worker_id": "worker-node-77x",
  "task_id": "task-xyz-889",
  "status": "COMPLETED",
  
  // The worker uploaded the finished result here, the Master will download and aggregate it
  "result_url": "minio://bucket-name/results/task-xyz-889-result.zip",
  
  "metrics": {
    "execution_time_seconds": 12.4
  }
}
```

### C. The "Heartbeat" Message (Worker -> Orchestrator)
Workers fire this off every 10 seconds. If the Orchestrator stops receiving this for 30 seconds, it assumes the Docker container crashed and reassigns the task.
```json
{
  "worker_id": "worker-node-77x",
  "current_task_id": "task-xyz-889",
  "status": "WORKING",
  "hardware_utilization": {
    "cpu_percent": 85,
    "ram_percent": 40
  }
}
```
