# DaeMon: Project Blueprint (`PROJECT.md`)

> **Project Name:** DaeMon (Distributed Compute Grid)  
> **Repository:** `Gaurravvvv/Daemon`  
> **Current Version:** v1.0.0-beta  
> **Status:** Active Implementation (~70% Complete)  
> **Capstone Context:** Final Year B.E. Project, Department of Artificial Intelligence & Data Science, MET Bhujbal Knowledge City, Institute of Engineering, Nashik, India.  

---

## 1. Vision & Core Value Proposition

**DaeMon** is a frictionless, containerized distributed computing grid engineered to harvest idle, dormant computing gigacycles across consumer laptops, laboratory workstations, and enterprise edge devices to execute massive polymorphic computational tasks at near-zero incremental infrastructure cost.

### Core Problems Solved:
1. **Cloud Cost Prohibitive:** Avoids recurring hourly VM/GPU charges and egress tariffs on commercial clouds (AWS/GCP/Azure).
2. **Edge Hardware Underutilized:** Harnesses consumer edge PCs that operate at $<20\%$ average utilization.
3. **Turnaround Latency Gap:** Replaces legacy volunteer pull polling (hours/days in BOINC) with **sub-second active-push scheduling** over AMQP.
4. **Message Broker Saturation:** Decouples lightweight control manifests (RabbitMQ) from heavy binary tensors and images (MinIO S3).
5. **High Edge Churn:** Overcomes unannounced machine disconnects via **sub-15s sliding-window Redis TTL lease recovery**.

---

## 2. Core Stakeholders & Roles

- **Grid Administrator / Researcher:** Submits polymorphic jobs, configures hardware compute mode (`any`, `gpu_only`, `cpu_only`), partitions datasets, monitors real-time Gantt timeline progress, halts rogue jobs, and downloads stitched deliverables.
- **Volunteer Node:** Donates idle compute capacity by running a zero-setup containerized daemon (`docker run daemon-worker`). Automatically audits local CPU/GPU hardware, executes tasks in a hermetic sandbox, and uploads artifacts.

---

## 3. High-Level Subsystems Inventory

1. **Control Plane (`orchestrator/`):** FastAPI master coordinator, Task Splitter, State Aggregator, MongoDB database, Redis cache.
2. **Decoupled Transport Plane:** RabbitMQ message broker for control manifests; MinIO S3 object storage for binary payloads.
3. **Execution Plane (`worker/`):** Python daemon, CuPy CUDA 12.4 GPU acceleration, NumPy BLAS CPU engine, strategy plugins.
4. **Presentation & Telemetry Tier (`dashboard/`):** Next.js 15+ App Router, Tailwind CSS dark terminal UI, multi-role portal.
