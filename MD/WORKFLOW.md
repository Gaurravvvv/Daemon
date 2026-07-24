# System Workflow

This document outlines the step-by-step lifecycle of a computational job in the Daemon-Based Distributed Compute Grid. Because we are using an **Active Push** model and supporting multiple job types, the workflow is highly orchestrated.

## 1. Job Submission (The Client)
- A user or external system submits a massive "Job" to the Master Orchestrator via a REST API endpoint.
- The submission includes the job type (e.g., Image Processing, Math, Data), the raw data (or pointers/URLs to the data), and required execution parameters.

## 2. Job Partitioning (Master Orchestrator)
- The Orchestrator receives the Job and assigns it a unique `JobID`.
- The Orchestrator uses a **Task Splitter** specific to the job type to break the massive job down.
  - *Example:* A job to process 10,000 images is split into 1,000 `Micro-Tasks` (10 images per task).
- Each `Micro-Task` is stored in the database with a status of `PENDING`.

## 3. Worker Discovery & Registration (How they find you)
As the Admin, you do **not** need to manually search for workers or know their IP addresses. The workers will always find you. Here is how:
- The Master Orchestrator is hosted at a known IP address or domain (e.g., `http://192.168.1.50:8000`).
- When you (or someone else) runs the Docker container on a personal machine, you pass that address as an environment variable:
  `docker run -e ORCHESTRATOR_URL="http://192.168.1.50:8000" daemon-worker`
- The Worker Daemon boots up, reads that URL, and immediately sends a `POST` request to the Orchestrator saying "I'm alive, here are my hardware specs."
- The Orchestrator accepts the registration, creates a dedicated RabbitMQ queue for that worker, and adds the worker to the live Redis registry of `AVAILABLE` workers.
- The worker instantly appears on your Admin React Dashboard as a new node ready for work!

## 4. Task Pushing (The Active Push Model)
- **Active Push:** Instead of workers randomly pulling tasks from a generic queue, the Orchestrator actively looks at its list of `AVAILABLE` workers.
- The Orchestrator pushes a specific `Micro-Task` directly to a specific Worker Daemon via the Message Broker (using worker-specific routing channels).
- The Orchestrator updates its state database: The task is now `IN_PROGRESS`, and it explicitly records exactly *which* worker owns it.

## 5. Task Execution (Worker Daemon)
- The Worker receives the task, parses the payload, and begins execution in an isolated thread or process using the host machine's idle resources.
- As it works, the Worker sends periodic "Heartbeats" or "Progress Updates" back to the Orchestrator.

## 6. Result Aggregation & Fault Tolerance
- **Success:** Once a task is done, the Worker pushes the result back. The Orchestrator marks the task as `COMPLETED`, saves the partial result, marks the Worker as `AVAILABLE` again, and immediately pushes the next task.
- **Failure/Disconnection:** If the Orchestrator misses heartbeats from a Worker for a set duration (e.g., 30 seconds), it marks the Worker as `OFFLINE`. The assigned `Micro-Task` is automatically reset to `PENDING` and actively pushed to a different, healthy worker.

## 7. Job Completion
- The **State Aggregator** constantly monitors the status of all micro-tasks for a given `JobID`.
- Once all tasks are `COMPLETED`, the Aggregator stitches the partial results together (e.g., merging processed CSV chunks, aggregating math results, finalizing a zip of images).
- The final result is made available to the client, and the Job is marked as `FINISHED`.

## 8. Real-Time Dashboard
- Throughout this entire lifecycle, the frontend dashboard is connected to the Orchestrator via WebSockets.
- It displays live metrics: Active vs. Offline Workers, Tasks Pending vs. Completed, Overall Job Progress (%), and System Throughput.
