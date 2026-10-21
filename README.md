# DaeMon Compute Grid

<div align="center">

![DaeMon Banner](https://img.shields.io/badge/DaeMon-Distributed%20Compute%20Grid-0052CC?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js 15](https://img.shields.io/badge/Next.js%2015-000000?style=for-the-badge&logo=next.js&logoColor=white)
![NVIDIA CUDA](https://img.shields.io/badge/CUDA%2012.4-76B900?style=for-the-badge&logo=nvidia&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO%20S3-C72C48?style=for-the-badge&logo=minio&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

**A Frictionless, Containerized Distributed Compute Grid for Volunteer Resource Aggregation**

*Aggregate idle consumer laptops, enterprise workstations, and edge GPUs into an ultra-low-latency, fault-tolerant parallel computing powerhouse at near-zero incremental infrastructure cost.*

</div>

---

## 📑 Table of Contents
1. [Project Overview & Motivation](#-project-overview--motivation)
2. [Key Architectural Innovations](#-key-architectural-innovations)
3. [System Architecture Diagram](#-system-architecture-diagram)
4. [Subsystem Breakdown](#-subsystem-breakdown)
5. [End-to-End Execution Lifecycle](#-end-to-end-execution-lifecycle)
6. [Hardware Acceleration (GPU vs. CPU)](#-hardware-acceleration-gpu-vs-cpu)
7. [Supported Workload Types (Polymorphic Engine)](#-supported-workload-types-polymorphic-engine)
8. [Quick Start (1-Click Run)](#-quick-start-1-click-run)
9. [Manual Step-by-Step Installation](#-manual-step-by-step-installation)
10. [Volunteer Worker Onboarding (Docker & Local)](#-volunteer-worker-onboarding-docker--local)
11. [Generating Test Datasets & Payloads](#-generating-test-datasets--payloads)
12. [API Reference & Message Contracts](#-api-reference--message-contracts)
13. [Repository File Structure](#-repository-file-structure)
14. [Academic Research Context](#-academic-research-context)

---

## 💡 Project Overview & Motivation

Modern computational workloads—such as high-resolution image processing, computer vision, scientific matrix multiplication, and cryptographic searches—demand immense computing power. Traditionally, researchers and developers turn to hyperscale commercial clouds (AWS, GCP, Azure), which incur steep hourly virtual machine and GPU charges, egress tariffs, and vendor lock-in.

Paradoxically, **billions of gigacycles of compute capacity sit idle** across personal laptops, academic computer laboratories, and local edge devices, which typically operate at less than **15%–20% average utilization**.

**DaeMon** bridges this divide by providing:
- **Volunteer Computing Without Friction:** Volunteers can join the grid using a single copy-paste Docker command or Python daemon script without manual dependency setup.
- **Interactive Turnaround Time:** Unlike legacy volunteer grids (e.g., BOINC) that operate on coarse batch pull horizons (hours or days), DaeMon achieves **sub-second task dispatch** and real-time execution tracking.
- **Enterprise-Grade Fault Tolerance:** Dynamic edge node churn (laptops closing, network dropouts) is automatically resolved via sub-15-second failover recovery loops.

---

## ⚡ Key Architectural Innovations

### 1. Active-Push Scheduling vs. Passive Pull
Legacy volunteer computing systems rely on clients periodically polling a central server over HTTP. DaeMon flips this model: the FastAPI Master evaluates registered, idle workers and **actively pushes** targeted micro-task manifests directly to dedicated AMQP routing queues in RabbitMQ with `prefetch_count=1`. This eliminates polling latencies and delivers immediate responsiveness.

### 2. Decoupled Control and Data Planes
Passing multi-megabyte binary images or matrices through a message broker causes memory exhaustion, buffer bloat, and broker crashes. DaeMon cleanly decouples:
- **Control Plane:** Lightweight JSON task manifests (~1–2 KB) pass through **RabbitMQ**.
- **Data Plane:** Heavy binary payloads (ZIPs, tensors, raw images) are staged directly in **MinIO S3 Object Storage**. Workers stream data directly via HTTP/2 using presigned URLs, completely bypassing the message queue.

### 3. Sub-15-Second Churn Resilience & Heartbeat Leasing
Consumer devices disconnect unpredictably. Instead of heavy consensus protocols (Raft/Paxos/etcd) or conservative 300-second eviction timeouts (Kubernetes), DaeMon utilizes an **ephemeral sliding-window Redis TTL lease model**:
- Workers transmit heartbeats every **5 seconds**.
- Redis maintains a lease key with a **15-second TTL**.
- If a node drops out, the lease expires, the node is marked `OFFLINE`, and orphaned in-progress tasks are atomically requeued and pushed to healthy nodes with zero data loss.

### 4. Hermetic Docker Sandboxing & GPU Acceleration
Workers execute tasks inside isolated Docker containers governed by Linux `cgroups v2` resource quotas (capping CPU shares and RAM). For nodes with NVIDIA GPUs, workers compile and execute CUDA kernels using **CuPy**; for CPU-only nodes, execution automatically falls back to vectorized **NumPy** routines.

---

## 🏗️ System Architecture Diagram

```mermaid
flowchart TD
    %% Actors
    Admin([Administrator / Researcher])
    Volunteer([Volunteer Compute Node])

    %% UI & Control Plane
    subgraph UI_Layer ["Client & Telemetry Layer"]
        UI["Next.js 15+ Web Dashboard<br/>(Port: 5555)"]
    end

    subgraph Orchestrator_Tier ["Master Orchestration Control Plane"]
        FastAPI["FastAPI Orchestrator<br/>(Port: 8000)"]
        Splitter["Task Partitioning Engine<br/>(Domain Decomposition)"]
        Aggregator["State Aggregator & Stitcher"]
        Mongo[("MongoDB<br/>Metadata & Jobs<br/>(Port: 27017)")]
        Redis[("Redis<br/>Heartbeat Registry<br/>(Port: 6379)")]
    end

    %% Messaging & Storage
    subgraph Infra_Tier ["Decoupled Messaging & Storage Planes"]
        RabbitMQ[("RabbitMQ Broker<br/>AMQP: 5672 | UI: 15672")]
        MinIO[("MinIO Object Storage<br/>S3 API: 9090 | Console: 9091")]
    end

    %% Worker Plane
    subgraph Worker_Tier ["Distributed Worker Execution Plane"]
        W_GPU["Worker Node 1 (GPU)<br/>CUDA 12.4 + CuPy Kernel"]
        W_CPU["Worker Node 2 (CPU)<br/>Vectorized NumPy Engine"]
    end

    %% Flow Connections
    Admin -->|1. Uploads Payload & Config| UI
    UI -->|2. Multipart REST API| FastAPI
    FastAPI -->|3. Save Initial State| Mongo
    FastAPI -->|4. Stage Raw Payload ZIP| MinIO
    FastAPI -->|5. Partition into Micro-Tasks| Splitter
    Splitter -->|6. Push JSON Task Manifests| RabbitMQ

    Volunteer -->|One-Line Docker Run| W_GPU
    W_GPU -->|Register Specs & Heartbeat| FastAPI
    FastAPI -->|Write Ephemeral Lease TTL| Redis

    RabbitMQ -.->|7. Active Push Task| W_GPU
    RabbitMQ -.->|7. Active Push Task| W_CPU

    W_GPU <-->|8. Stream Chunk & Upload Artifact| MinIO
    W_CPU <-->|8. Stream Chunk & Upload Artifact| MinIO

    W_GPU -->|9. Task Complete & Event Stream| FastAPI
    W_CPU -->|9. Task Complete & Event Stream| FastAPI
    FastAPI -->|10. Real-time Progress & Event Log| UI

    Aggregator -->|11. Verify & Stitch Chunks| MinIO
    UI -->|12. Stream Final Downloadable ZIP| Admin
```

---

## 🧩 Subsystem Breakdown

### 1. Master Orchestrator (`/orchestrator`)
The brain of the system, implemented in **FastAPI** (Python 3.10+):
- **Task Partitioning (`core/splitter.py`):** Decomposes monolithic tasks into $N$ atomic micro-tasks with assigned chunk indices, MinIO storage pointers, and hardware constraints (`compute_mode`: `any`, `gpu_only`, or `cpu_only`).
- **State Aggregator (`core/aggregator.py`):** Monitors completed task queues, verifies output checksums, and coordinates final artifact assembly.
- **Event Logging Engine (`api/routes.py`):** Captures granular execution events from both orchestrator and worker nodes, exposing endpoints for real-time dashboard terminal streaming.
- **REST Endpoints:** Handles job uploads, cancellations, worker registrations, password-protected job verification, and result streaming.

### 2. Worker Daemon (`/worker`)
The execution engine that runs headlessly on volunteer machines:
- **Hardware Probing (`main.py`):** At startup, runs an active CUDA smoke-test (allocating and computing on device tensors). Detects GPU model, VRAM capacity, and driver version.
- **Task Consumer (`consumer.py`):** Listens to dedicated RabbitMQ queues (`prefetch_count=1`), verifies compute eligibility, and reports live progress back to the master.
- **Dynamic Demotion:** If a GPU kernel fails or encounters an unexpected CUDA exception, the node dynamically demotes itself to CPU mode to prevent claiming subsequent `gpu_only` tasks.

### 3. Object Storage & Message Broker
- **MinIO S3:** Self-hosted high-throughput object storage mapped to local disk storage (`D:\Daemon_Minio_Data`). Eliminates cloud storage fees.
- **RabbitMQ:** Enterprise AMQP message broker with persistent queues and guaranteed delivery.
- **Redis:** Sub-millisecond in-memory cache for sliding-window worker heartbeat leases.
- **MongoDB:** Flexible document store persisting polymorphic job schemas, execution timelines, and worker metadata.

### 4. Real-Time Command Dashboard (`/dashboard`)
A **Next.js 15+ (App Router)** and **Tailwind CSS** control center:
- **Role Gateway (`/role-select`):** Switch between Grid Admin (Orchestrator) and Volunteer Worker modes.
- **Orchestrator Control Center (`/orchestrator`):** Submit jobs, view aggregate cluster compute power, monitor active jobs, halt jobs, and download final results.
- **Live Terminal Feed (`/orchestrator/job/[id]`):** Streaming event terminal displaying chunk pickup, execution durations, hardware tags (`[GPU: RTX 3060]`), and progress percentages.
- **Worker View (`/worker`):** Node hardware status, assigned pool, active tasks, and copy-paste onboarding snippets.

---

## 🔄 End-to-End Execution Lifecycle

```text
[1. Job Submit] ───► [2. Stage MinIO] ───► [3. Partition Splitter] ───► [4. RabbitMQ Push]
                                                                                │
                                                                                ▼
[8. Download ZIP] ◄── [7. 100% Complete] ◄── [6. Progress Ack] ◄── [5. Worker Compute]
```

1. **Job Submission:** The Admin selects job type (Image / Math / Crypto), uploads `payload.zip`, selects target pool (`public_pool`), and sets compute mode.
2. **Staging:** Orchestrator streams `payload.zip` directly to MinIO and writes a `processing` document into MongoDB.
3. **Partitioning:** `TaskSplitter` breaks the job into $N$ micro-task manifests carrying metadata and MinIO URLs.
4. **Active Push:** Manifests are published to RabbitMQ.
5. **Worker Execution:** Available workers claim tasks, download their specific chunk slice from MinIO, execute through the appropriate strategy on GPU or CPU, and upload result artifacts (`edges_...`, `enhanced_...`, or JSON results) back to MinIO.
6. **Progress Acknowledgment:** The worker calls `/api/v1/jobs/{job_id}/task_complete`, incrementing the database counter and emitting real-time event logs.
7. **Job Completion:** Once progress hits 100%, the job is marked `completed`.
8. **Result Download:** The UI transforms the progress indicator into a green **"Download Results ZIP"** button, streaming all combined results to the client.

---

## 🚀 Hardware Acceleration (GPU vs. CPU)

DaeMon natively supports heterogeneous clusters containing mixed GPU and CPU hardware:

```
                  ┌────────────────────────────────┐
                  │ Task Received by Worker Daemon │
                  └───────────────┬────────────────┘
                                  ▼
                    Is task marked 'gpu_only'?
                                  │
                    ┌─────────────┴─────────────┐
                    │ YES                       │ NO
                    ▼                           ▼
            Does node have CUDA?        Is GPU available?
            ┌───────┴───────┐           ┌───────┴───────┐
            │ YES           │ NO        │ YES           │ NO
            ▼               ▼           ▼               ▼
      Execute CuPy     NACK & Requeue Execute CuPy Execute NumPy
      CUDA Kernel      for GPU node   CUDA Kernel  Vectorized CPU
```

- **GPU Acceleration (CuPy):** Compiles 2D spatial convolution kernels directly into CUDA machine code. Executes edge detection and contrast enhancement entirely in GPU VRAM with zero host CPU intervention.
- **CPU Fallback (NumPy):** For machines without dedicated GPUs, tasks run using vectorized BLAS/NumPy CPU operations.
- **Compute Modes Available During Job Submission:**
  - `any` (Hybrid): Work is distributed across both GPU and CPU workers.
  - `gpu_only`: Tasks are strictly routed to CUDA-enabled GPU nodes. CPU nodes automatically skip and requeue these tasks.
  - `cpu_only`: Forces lightweight CPU execution.

---

## 🔬 Supported Workload Types (Polymorphic Engine)

| Workload Type | Strategy File | Description & Math Operation | Primary Device |
| :--- | :--- | :--- | :--- |
| **Image Processing** | `worker/strategies/image_processing.py` | 2D Spatial Sobel Convolution ($G = \sqrt{G_x^2 + G_y^2}$) with 1-pixel boundary overlap padding + Contrast Enhancement. | **NVIDIA CUDA (CuPy)** / CPU (NumPy) |
| **Distributed Math** | `worker/strategies/dummy_math.py` | Distributed block matrix multiplication sub-block dot products ($C_{ij} = \sum A_{im} \cdot B_{mj}$) and Monte Carlo numerical simulations. | **CPU (NumPy / BLAS)** |
| **Cryptographic Search** | In Development | Parallel SHA-256 pre-image discovery and proof-of-work nonce search over partitioned keyspace sub-intervals with early-termination abort signals. | **CPU / GPU** |

---

## ⚡ Quick Start (1-Click Run)

The fastest way to boot up the entire grid (Docker Infrastructure, FastAPI Orchestrator, and Next.js Dashboard) on Windows:

```bash
# Double-click or run from PowerShell at the repository root:
.\start_grid.bat
```

> **Note:** The script starts the UI on **Port 5555** to avoid the common Windows Hyper-V port exclusion bug on port 3000. It will automatically launch Google Chrome to `http://localhost:5555`.

---

## 🛠️ Manual Step-by-Step Installation

If you prefer starting each service individually:

### 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- Python 3.10 or 3.11 installed.
- Node.js 18+ and npm installed.
- (Optional for GPU workers) NVIDIA Driver 550+ and CUDA 12.x.

### 2. Boot Up the Infrastructure
Spin up RabbitMQ, Redis, MongoDB, and MinIO:
```bash
docker-compose up -d
```

Verify that all 4 containers are healthy:
```bash
docker ps
```

| Service | Port | Management URL / Credentials |
| :--- | :--- | :--- |
| **RabbitMQ** | `5672` (AMQP), `15672` (Web UI) | `http://localhost:15672` (user: `guest` / pass: `guest`) |
| **MinIO** | `9090` (API), `9091` (Console) | `http://localhost:9091` (user: `Gaurav` / pass: `password123`) |
| **MongoDB** | `27017` | Standard Mongo connection: `mongodb://localhost:27017` |
| **Redis** | `6379` | In-memory key store |

### 3. Start the FastAPI Orchestrator
Open a new terminal:
```bash
cd orchestrator
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
Backend API will be online at: `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).

### 4. Start the Next.js Dashboard
Open a new terminal:
```bash
cd dashboard
npm install
npm run dev -- -p 5555
```
Visit `http://localhost:5555` in your browser.

---

## 💻 Volunteer Worker Onboarding (Docker & Local)

You can run worker nodes either natively via Python or containerized via Docker.

### Option A: Containerized via Docker (Recommended for Volunteers)

#### With NVIDIA GPU Acceleration (CUDA):
```bash
docker run --rm -it --gpus all \
  -e ORCHESTRATOR_URL="http://host.docker.internal:8000" \
  -e RABBITMQ_URL="amqp://guest:guest@host.docker.internal:5672/" \
  -e MINIO_URL="http://host.docker.internal:9090" \
  -e POOL_ID="public_pool" \
  daemon-worker
```

#### In CPU-Only Mode:
```bash
docker run --rm -it \
  -e ORCHESTRATOR_URL="http://host.docker.internal:8000" \
  -e RABBITMQ_URL="amqp://guest:guest@host.docker.internal:5672/" \
  -e MINIO_URL="http://host.docker.internal:9090" \
  -e POOL_ID="public_pool" \
  -e FORCE_CPU=1 \
  daemon-worker
```

### Option B: Running Natively on Host Python
```bash
cd worker
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run worker daemon
python main.py
```

---

## 🧪 Generating Test Datasets & Payloads

Pre-built dataset generator scripts are located in the repository root:

```bash
# 1. Generate 10 sample images and package into payload.zip
python generate_test_images.py

# 2. Generate 10 numerical matrix partitions into math_payload.zip
python generate_math_payload.py

# 3. Generate 10 SHA-256 keyspace slices into crypto_payload.zip
python generate_crypto_payload.py
```

### Testing a Job via the Dashboard:
1. Navigate to `http://localhost:5555/orchestrator`.
2. Click **"Submit New Job"**.
3. Choose **Job Type** (e.g., `Image Processing`), select **Compute Mode** (`Hybrid`, `GPU Only`, or `CPU Only`), and set **Pool ID** (`public_pool`).
4. Attach `payload.zip` and click **Submit**.
5. Watch the real-time progress bar tick up and monitor the live terminal log as workers process chunks!

---

## 📡 API Reference & Message Contracts

### Core REST Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/jobs` | Lists all active and completed jobs. |
| `POST` | `/api/v1/jobs/upload_and_submit` | Multipart form submission: uploads raw payload to MinIO, slices tasks, and publishes to RabbitMQ. |
| `GET` | `/api/v1/jobs/{job_id}` | Retrieves detailed status, progress, and metadata for a specific job. |
| `PUT` | `/api/v1/jobs/{job_id}/halt` | Halts execution of an in-progress job. |
| `DELETE` | `/api/v1/jobs/{job_id}` | Deletes job record and associated event logs. |
| `POST` | `/api/v1/jobs/{job_id}/task_complete`| Called by workers upon finishing a chunk to atomically increment progress. |
| `GET` | `/api/v1/jobs/{job_id}/events` | Returns real-time event logs for dashboard streaming (`?after=<iso_timestamp>`). |
| `GET` | `/api/v1/jobs/{job_id}/results` | Lists processed output files stored in MinIO. |
| `GET` | `/api/v1/jobs/{job_id}/download` | Packages all result artifacts into an in-memory ZIP and streams download to user. |
| `POST` | `/api/v1/workers/register` | Registers a worker node, recording CPU, GPU, and VRAM specifications. |

### RabbitMQ Task Manifest Schema (Orchestrator ➔ Worker)
```json
{
  "task_id": "job-1042-task-a1b2c3",
  "job_id": "job-1042",
  "job_type": "image",
  "raw_data_url": "minio://daemon-jobs/job-1042/payload.zip",
  "chunk_index": 0,
  "total_chunks": 10,
  "compute_mode": "any",
  "parameters": {
    "max_workers": 10
  }
}
```

---

## 📁 Repository File Structure

```text
DaeMon/
├── docker-compose.yml              # Multi-container infrastructure definition (RabbitMQ, Redis, Mongo, MinIO)
├── start_grid.bat                  # Automated 1-click batch startup script for Windows
├── README.md                       # Comprehensive project documentation
├── IMPLEMENTATION_PLAN.md          # Phased development master plan
├── .gitignore                      # Git exclusion rules
│
├── orchestrator/                   # Backend Control Plane (FastAPI)
│   ├── main.py                     # Application entry point, lifespan, CORS configuration
│   ├── requirements.txt            # Python dependencies (fastapi, uvicorn, motor, boto3, pika)
│   ├── api/
│   │   └── routes.py               # REST endpoints for jobs, worker registry, events, downloads
│   ├── core/
│   │   ├── splitter.py             # Domain decomposition task partitioner
│   │   └── aggregator.py           # Background state aggregator and chunk stitching logic
│   ├── models/
│   │   └── schemas.py              # Pydantic request and response models
│   └── services/
│       ├── database.py             # Async MongoDB client wrapper (motor)
│       ├── rabbitmq.py             # Pika RabbitMQ connection and publisher
│       └── storage.py              # MinIO S3 client wrapper (boto3)
│
├── worker/                         # Headless Worker Execution Daemon
│   ├── Dockerfile                  # CUDA 12.4 container definition with CuPy runtime
│   ├── requirements.txt            # Python dependencies (pika, boto3, requests, cupy, pillow)
│   ├── main.py                     # Startup sequence, CUDA smoke-test, orchestrator handshake
│   ├── consumer.py                 # AMQP consumer loop, compute mode gating, event dispatch
│   ├── storage.py                  # MinIO chunk downloader and result uploader
│   └── strategies/                 # Polymorphic execution strategy plugins
│       ├── image_processing.py     # Sobel convolution & contrast enhancement (CuPy GPU / NumPy CPU)
│       └── dummy_math.py           # Distributed matrix multiplication & math simulations
│
├── dashboard/                      # Next.js 15+ Real-Time Web Telemetry Dashboard
│   ├── package.json                # Dependencies (Next.js 15, React 19, Tailwind CSS, Lucide icons)
│   ├── src/app/
│   │   ├── layout.tsx              # Root HTML layout and ThemeProvider wrapper
│   │   ├── globals.css             # Dark terminal design system and animations
│   │   ├── page.tsx                # Automatic redirect to /role-select
│   │   ├── role-select/page.tsx    # Multi-role login gateway (Admin vs. Worker)
│   │   └── (dashboard)/
│   │       ├── layout.tsx          # Dashboard shell with dynamic header and status badges
│   │       ├── orchestrator/       # Admin control panel: metrics, active jobs, submit modal
│   │       │   └── job/[id]/       # Real-time job inspection with live streaming terminal
│   │       └── worker/             # Volunteer worker dashboard and execution feeds
│   │           └── job/[id]/       # Worker-specific live task view
│
├── generate_test_images.py         # Test generator: 10 images -> payload.zip
├── generate_math_payload.py        # Test generator: 10 matrix blocks -> math_payload.zip
├── generate_crypto_payload.py      # Test generator: 10 keyspace slices -> crypto_payload.zip
│
├── MD/                             # Architectural design & protocol documentation
│   ├── ARCHITECTURE.md             # Network topology, push vs. pull, technology choices
│   ├── API_AND_SCHEMA.md           # Formal JSON payloads and message formats
│   ├── WORKFLOW.md                 # Detailed job lifecycle breakdown
│   └── BRAINSTORMING.md            # Initial design notes
│
└── survey paper/                   # Academic survey paper, diagrams, and evaluation methodology
```

---

## 🎓 Academic Research Context

This project represents the final 4th-year engineering capstone project:
- **Title:** *DaeMon: A Resilient, Containerized Distributed Compute Grid with Active-Push Scheduling, Decoupled Storage, and Fault-Tolerant Edge Orchestration*
- **Institution:** Department of Artificial Intelligence and Data Science, MET Bhujbal Knowledge City, Institute of Engineering, Nashik, India.
- **Academic Documents Included:**
  - `DaeMon_Project_Abstract.docx` / `.pdf`: Formal 1-page academic abstract.
  - `survey paper/DaeMon_Survey_Paper.docx` / `.pdf`: Full IEEE conference paper format survey document with theoretical formulation, extended Amdahl's Law derivation, and empirical evaluations.
