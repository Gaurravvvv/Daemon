# Daemon Compute Grid: Master Implementation Plan

This master document outlines the entire architecture, prerequisites, file structure, and phased development plan for building the distributed compute grid.

---

## 1. Prerequisites & Environment Variables

To run the local development environment, **Docker Desktop** is required. We will use a `docker-compose.yml` file to spin up our infrastructure (RabbitMQ, Redis, MinIO, MongoDB).

**MinIO Specific Development Constraints:**
- **Credentials:** Username `Gaurav`
- **Volume Mount:** Mapped to the `D:\` drive (e.g., `D:\Daemon_Minio_Data`) to keep the primary C:\ drive clean.
- **Quota:** Hard limit of `20 GB` for local development.

**Global Environment Variables needed:**
- `ORCHESTRATOR_URL`: The network address of the FastAPI server (e.g., `http://localhost:8000`).
- `RABBITMQ_URL`: Connection string for the message broker (e.g., `amqp://guest:guest@localhost:5672/`).
- `REDIS_URL`: Connection string for real-time state caching.
- `MONGO_URI`: Connection string for persistent job/task tracking.
- `POOL_ID`: (Worker-specific) Used to assign a worker to a specific user's grid or the `public_pool`.

---

## 2. System Architecture & Tech Stack

- **Backend (Orchestrator)**: Python + FastAPI (Lightning fast, async REST APIs)
- **Worker Daemon**: Python (Headless process inside Docker)
- **Message Broker**: RabbitMQ (Handles the "Active Push" of tasks)
- **State & Cache**: Redis (Live registry of worker heartbeats)
- **Database**: MongoDB (Flexible schemas for diverse job types)
- **Object Storage**: MinIO (Handles massive data transfers off-broker)
- **Frontend Dashboard**: React.js (Next.js) + Tailwind CSS (Vercel/Linear minimalist aesthetic)

---

## 3. Workflow & UI Behavior

Here is exactly what happens when users interact with the system:

1. **Job Submission:**
   - The Admin goes to the React Dashboard and clicks **"Submit New Job"**.
   - A modal appears asking for a Job Name, Type (Math/Image/Data), and the raw data payload.
   - Upon clicking "Submit", the FastAPI Orchestrator accepts it, assigns a `Job ID`, and the UI instantly adds a new row to the "Active Jobs" table with a 0% progress bar.

2. **Frictionless Worker Onboarding:**
   - A volunteer visits the "Global Job Board" on the React frontend.
   - They see an active job and click the **"Help Compute"** button.
   - A modal pops up with a copy-pasteable command: `docker run -e ORCHESTRATOR_URL="..." -e TARGET_JOB="123" daemon-worker`.
   - The volunteer pastes this into their terminal. Their terminal instantly lights up with logs as the worker registers with the Orchestrator.

3. **Execution & UI Updates:**
   - The worker automatically downloads its data chunk from MinIO, computes it, and uploads the result.
   - As workers finish chunks, the Orchestrator updates Redis. 
   - The React Dashboard is connected via WebSockets, so the "Active Jobs" progress bar visually ticks up in real-time without the user having to refresh the page.

4. **Job Completion:**
   - When the progress bar hits 100%, the Orchestrator's internal "State Aggregator" stitches the files together.
   - The React UI replaces the progress bar with a green **"Download Final Result"** button, giving the Admin direct access to the finished MinIO file.

---

## 4. Proposed File Structure

We will structure the monolithic repository like this:

```text
DaeMon/
├── docker-compose.yml          # Spins up RabbitMQ, Redis, MinIO, and MongoDB
├── orchestrator/               # The FastAPI Backend
│   ├── requirements.txt
│   ├── main.py                 # FastAPI entry point
│   ├── api/                    # REST endpoint routers (/jobs, /workers)
│   ├── core/                   # Task Splitter & State Aggregator algorithms
│   ├── services/               # RabbitMQ publisher and MongoDB client wrappers
│   └── models/                 # Pydantic data schemas
├── worker/                     # The Python Worker Daemon
│   ├── Dockerfile              # Containerizes the worker for volunteers
│   ├── requirements.txt
│   ├── main.py                 # RabbitMQ consumer loop and Heartbeat sender
│   └── strategies/             # Plugin folder (math_strategy.py, image_strategy.py)
└── dashboard/                  # The Next.js Frontend
    ├── package.json
    ├── tailwind.config.js      # Uses the tokens from our Stitch UI designs
    ├── src/
    │   ├── components/         # Reusable buttons, modals, and charts
    │   ├── pages/              # Overview, Active Jobs, Worker Nodes
    │   └── lib/                # WebSocket hooks and API fetchers
```

---

## 5. Phased Development Plan

To ensure we build a stable system, we will execute the code generation in these precise phases:

### Phase 1: Core Infrastructure & Backend Foundation
- Write the `docker-compose.yml` to get our 4 core databases/brokers running locally. *Note: MinIO volume mapped to D:\ drive with 20GB limit.*
- Initialize the `orchestrator/` FastAPI project.
- Implement the Pydantic data models and basic MongoDB connection.

### Phase 2: The Orchestrator Brain
- Build the **Task Splitter** engine to partition jobs.
- Implement the RabbitMQ publisher to actively push tasks to specific routing keys.
- Build the `/workers/register` and `/jobs/submit` REST endpoints.

### Phase 3: The Worker Daemon
- Initialize the `worker/` Python project.
- Write the MinIO wrapper using `boto3` to auto-download and auto-upload chunks.
- Build the RabbitMQ listener to catch tasks and execute the correct Strategy.
- **Milestone:** Run a complete, headless end-to-end test (submit a job via `curl`, watch the worker process it).

### Phase 4: State Aggregation
- Build the Orchestrator background process that monitors Job status.
- Implement the stitching logic to combine all completed micro-task results into a final master file.

### Phase 5: The React Dashboard (The UI)
- Initialize the `dashboard/` Next.js project.
- Translate our `code.html` Stitch theme into reusable React components.
- Hook up the WebSockets so the dashboard accurately reflects the live state of the grid.
- Build the "Help Compute" copy-paste modal.
