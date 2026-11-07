# DaeMon: System Requirements Matrix (`REQUIREMENTS.md`)

> **Document Type:** Scoped Requirements & Completion Audit (`REQUIREMENTS.md`)  
> **Repository:** `Gaurravvvv/Daemon`  
> **Status:** Current Snapshot (October 2026)  

---

## 1. Functional Requirements Audit

### Subsystem 1: Core Infrastructure & Staging
- [x] **REQ-1.1:** Containerized local infrastructure running RabbitMQ, Redis, MongoDB, and MinIO via `docker-compose.yml`. *(Completed)*
- [x] **REQ-1.2:** MinIO local persistent volume storage mapped to local disk (`D:\Daemon_Minio_Data`). *(Completed)*
- [x] **REQ-1.3:** Auto-creation of `daemon-jobs` bucket on orchestrator boot. *(Completed)*
- [x] **REQ-1.4:** 1-Click batch script startup (`start_grid.bat`) with Hyper-V port 5555 bypass. *(Completed)*

### Subsystem 2: Orchestration & Job Partitioning
- [x] **REQ-2.1:** REST API endpoint `/api/v1/jobs/upload_and_submit` supporting multipart payload uploads. *(Completed)*
- [x] **REQ-2.2:** Domain decomposition splitter engine generating $N$ independent micro-task manifests. *(Completed)*
- [x] **REQ-2.3:** Hardware compute mode tagging (`compute_mode`: `any`, `gpu_only`, `cpu_only`). *(Completed)*
- [x] **REQ-2.4:** Optional password protection for private cluster jobs (`/verify_password`). *(Completed)*
- [x] **REQ-2.5:** Job halt and cancellation endpoints (`/halt`, `/jobs/{id}`). *(Completed)*
- [ ] **REQ-2.6:** Domain-specific partition parameter injection for Matrix Blocks and Crypto Nonce ranges. *(In Progress)*
- [ ] **REQ-2.7:** Automated early-abort signal broadcast on RabbitMQ when crypto target is matched. *(Remaining)*

### Subsystem 3: Worker Execution & Hardware Acceleration
- [x] **REQ-3.1:** Active CUDA hardware smoke-test detecting GPU model, VRAM capacity, and driver version. *(Completed)*
- [x] **REQ-3.2:** Automatic fallback to NumPy vectorized CPU operations if CUDA device is absent. *(Completed)*
- [x] **REQ-3.3:** Task consumer listening to dedicated RabbitMQ pool queue with `prefetch_count=1`. *(Completed)*
- [x] **REQ-3.4:** Hardware eligibility gating: CPU workers NACK and requeue `gpu_only` tasks. *(Completed)*
- [x] **REQ-3.5:** Dynamic demotion: if a GPU kernel fails, worker demotes itself to CPU mode. *(Completed)*
- [x] **REQ-3.6:** Image Processing Strategy: 2D spatial Sobel convolution and contrast enhancement via CuPy/NumPy. *(Completed)*
- [x] **REQ-3.7:** Matrix Multiplication Strategy: High-performance block dot products via BLAS. *(Completed in `matrix_strategy.py`, pending consumer integration)*
- [ ] **REQ-3.8:** Cryptographic PoW Search Strategy: Parallel SHA-256 keyspace discovery. *(Remaining)*
- [ ] **REQ-3.9:** Worker recurring 5s heartbeat thread updating Redis lease keys. *(Remaining)*

### Subsystem 4: State Aggregation & Output Stitching
- [x] **REQ-4.1:** Worker `/task_complete` endpoint atomically incrementing progress and setting status to `completed` at 100%. *(Completed)*
- [x] **REQ-4.2:** Streaming download endpoint `/jobs/{job_id}/download` serving zipped artifacts from MinIO. *(Completed)*
- [ ] **REQ-4.3:** True Image Stitcher: Cropping 1-pixel overlap margins and reassembling full composite image. *(Remaining)*
- [ ] **REQ-4.4:** True Matrix Stitcher: Reconstructing full $N \times N$ composite matrix from sub-block JSONs. *(Remaining)*
- [ ] **REQ-4.5:** True Crypto Stitcher: Producing consolidated proof-of-work validation report. *(Remaining)*

### Subsystem 5: Resilience & Churn Fault Tolerance
- [ ] **REQ-5.1:** Redis ephemeral lease key `worker:{id}:lease` set with 15s TTL. *(Remaining)*
- [ ] **REQ-5.2:** Orchestrator 3s reaper loop scanning Redis active leases. *(Remaining)*
- [ ] **REQ-5.3:** Automated re-queueing of orphaned `in_progress` tasks to RabbitMQ when worker dies. *(Remaining)*
- [ ] **REQ-5.4:** Max retry count ceiling ($R_{\text{max}} = 3$) preventing infinite poison task loops. *(Remaining)*

### Subsystem 6: User Interface & Telemetry
- [x] **REQ-6.1:** Role Gateway (`/role-select`) separating Admin/Orchestrator and Volunteer Worker modes. *(Completed)*
- [x] **REQ-6.2:** Orchestrator Console displaying KPI metric cards, active jobs table, and submit modal. *(Completed)*
- [x] **REQ-6.3:** Real-time job inspector (`/orchestrator/job/[id]`) with live streaming terminal logs. *(Completed)*
- [x] **REQ-6.4:** Worker portal (`/worker` & `/worker/job/[id]`) with copy-paste Docker run snippet. *(Completed)*
- [ ] **REQ-6.5:** Upgrade terminal log streaming from HTTP interval polling (2s) to native WebSockets. *(Remaining)*
- [ ] **REQ-6.6:** Live hardware utilization telemetry gauges (CPU %, GPU %, RAM %) in worker cards. *(Remaining)*

### Subsystem 7: Empirical Benchmarking & Academic Defense
- [x] **REQ-7.1:** Synthetic dataset generators for Images, Matrix blocks, and Cryptography keyspaces. *(Completed)*
- [x] **REQ-7.2:** Formal 1-page Academic Abstract document (DOCX and PDF). *(Completed)*
- [x] **REQ-7.3:** Complete IEEE Conference Paper format Survey Paper with theoretical Amdahl's Law derivation. *(Completed)*
- [ ] **REQ-7.4:** Automated multi-worker benchmark test script (`run_benchmark_suite.py`). *(Remaining)*
- [ ] **REQ-7.5:** Capstone presentation demonstration runbook (`DEMO_RUNBOOK.md`). *(Remaining)*

---

## 2. Quantitative Completion Summary

```text
┌───────────────────────────────────────────────┬────────────┬─────────────┐
│ Subsystem Area                                │ Weight (%) │ Progress    │
├───────────────────────────────────────────────┼────────────┼─────────────┤
│ 1. Core Infrastructure & Staging              │ 10%        │ 100%        │
│ 2. Orchestration & Job Partitioning           │ 15%        │ 85%         │
│ 3. Worker Execution & Hardware Acceleration   │ 25%        │ 80%         │
│ 4. State Aggregation & Output Stitching       │ 15%        │ 40%         │
│ 5. Resilience & Churn Fault Tolerance         │ 15%        │ 20%         │
│ 6. User Interface & Telemetry                 │ 10%        │ 75%         │
│ 7. Benchmarking & Academic Defense Assets     │ 10%        │ 80%         │
├───────────────────────────────────────────────┼────────────┼─────────────┤
│ TOTAL WEIGHTED COMPLETION                     │ 100%       │ ~71%        │
└───────────────────────────────────────────────┴────────────┴─────────────┘
```
