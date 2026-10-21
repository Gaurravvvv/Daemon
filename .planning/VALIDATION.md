# DaeMon: Quality Gates, Testing & Validation Protocols (`VALIDATION.md`)

> **Document Type:** Verification & Validation Matrix (`VALIDATION.md`)  
> **Status:** Active Reference / Quality Gate  
> **Purpose:** Formal verification criteria, test commands, and demonstration acceptance gates for all 6 execution phases.  

---

## 1. Quality Gates Summary by Phase

| Phase | Core Objective | Primary Verification Gate | Pass Criteria |
| :---: | :--- | :--- | :--- |
| **Phase 1** | Container Connectivity | Docker Worker Handshake & Event Feed | Container connects to `0.0.0.0:8000`, registers in MongoDB, and its join event appears in the Next.js UI terminal in <2s. |
| **Phase 2** | Polymorphic Strategies | Numerical & Hash Correctness | Matrix multiplication output matches single-node `np.matmul(A, B)` with zero numerical error; Crypto worker discovers valid golden nonce matching target difficulty. |
| **Phase 3** | Result Aggregation | Automated Output Reassembly | On 100% progress, master stitcher builds verified `{job_id}_final.zip` in MinIO; download link delivers full valid archive. |
| **Phase 4** | Sub-15s Churn Resilience | Hard Node Kill Chaos Test | Killing worker container mid-task triggers Redis TTL expiration, marks node `OFFLINE`, and re-assigns task to a healthy node in $\le 15.2\text{s}$ with zero data loss. |
| **Phase 5** | Real-Time Telemetry | WebSocket Latency & Connection Test | Dashboard receives chunk completion events in $<20\text{ms}$ over WebSocket without HTTP polling; automatic reconnect on connection drops. |
| **Phase 6** | Defense Demonstration | Empirical Amdahl's Law Scaling | Parallel speedup $S(P) \ge 3.5\times$ across 4 worker nodes; CuPy GPU achieves $>4\times$ speedup over CPU for 4K Sobel convolution. |

---

## 2. Detailed Verification Protocols by Phase

### Phase 1: Container Connectivity Verification

#### Protocol 1.1: Orchestrator Loopback vs. All-Interfaces Audit
- **Command:**
  ```powershell
  netstat -ano | findstr 8000
  ```
- **Expected Output:**
  `TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING`  
  *(Must NOT say `127.0.0.1:8000`)*.

#### Protocol 1.2: Container Handshake Verification
- **Execution:**
  1. Boot infrastructure via `start_grid.bat`.
  2. Launch containerized worker:
     ```bash
     docker run --rm -it \
       --add-host=host.docker.internal:host-gateway \
       -e ORCHESTRATOR_URL="http://host.docker.internal:8000" \
       -e RABBITMQ_URL="amqp://guest:guest@host.docker.internal:5672/" \
       -e MINIO_URL="http://host.docker.internal:9090" \
       -e POOL_ID="public_pool" \
       daemon-worker
     ```
- **Validation Checks:**
  - [ ] Terminal logs display: `Successfully registered node NODE-XXXXXX with Orchestrator.`
  - [ ] Querying MongoDB (`db.workers.find()`) shows document with `status: "online"`.
  - [ ] Next.js dashboard terminal at `http://localhost:5555/orchestrator` logs:
    `[SYSTEM] NODE-XXXXXX connected to pool 'public_pool' [CPU MODE]`.

---

### Phase 2: Polymorphic Strategy Verification

#### Protocol 2.1: Distributed Matrix Multiplication Accuracy Test
- **Input:** Two randomly generated $50 \times 50$ test matrices $A$ and $B$.
- **Validation Script:**
  ```python
  import json
  import numpy as np

  # 1. Compute ground truth on single node
  A = np.load("test_matrix_A.npy")
  B = np.load("test_matrix_B.npy")
  C_expected = np.matmul(A, B)

  # 2. Load assembled chunks from grid
  C_grid = np.load("grid_matrix_C.npy")

  # 3. Assert numerical equality within floating-point tolerance
  np.testing.assert_allclose(C_grid, C_expected, rtol=1e-5, atol=1e-8)
  print("✅ Matrix multiplication numerical validation PASSED!")
  ```
- **Pass Criteria:** Zero shape mismatch; `assert_allclose` passes with no numerical drift.

#### Protocol 2.2: Cryptographic SHA-256 Nonce Search & Early Abort Test
- **Input:** Target difficulty `"0000"`, Block Header `"DaeMon-Block-101"`.
- **Validation Steps:**
  1. Submit cryptographic job partitioned across 4 worker nodes.
  2. Monitor RabbitMQ exchange logs.
  3. When Worker 2 finds matching nonce $n^*$, inspect the digest:
     $$\text{SHA256}(\text{"DaeMon-Block-101"} + \text{str}(n^*)) \stackrel{?}{=} \text{"0000..."}$$
  4. Verify that Workers 1, 3, and 4 receive the `ABORT` signal and immediately terminate their loops.
- **Pass Criteria:**
  - Nonce hash strictly starts with `"0000"`.
  - Remaining workers cease hash computation within $500\text{ms}$ of discovery.

---

### Phase 3: Result Aggregation & Output Stitching Verification

#### Protocol 3.1: Automated Stitcher Trigger on 100% Progress
- **Execution:** Submit a 10-chunk image processing job (`payload.zip`).
- **Validation Checks:**
  - [ ] When completed chunks counter reaches 10/10, Orchestrator status automatically changes from `processing` to `stitching` and then `completed`.
  - [ ] MinIO bucket `daemon-jobs` contains key: `{job_id}_results.zip`.
  - [ ] Next.js dashboard displays green **"Download Final Result"** button.
  - [ ] Downloading and unzipping the archive reveals all 10 edge-detected (`edges_...`) and contrast-enhanced (`enhanced_...`) images.
  - [ ] No image in the bundle is corrupt (can be opened by Pillow/OpenCV with valid image headers).

---

### Phase 4: Sub-15s Churn Resilience & Fault Tolerance Verification

#### Protocol 4.1: The Live "Worker Kill" Chaos Test (Presentation Highlight)
This protocol validates that edge worker dropout does not crash or stall the distributed pipeline.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Jury / Evaluator
    participant W1 as Worker 1 (Active)
    participant W2 as Worker 2 (Target)
    participant Redis as Redis TTL Lease
    participant Orch as Master Reaper
    participant Rabbit as RabbitMQ Priority Queue

    Admin->>W2: Abruptly terminates container (Kill signal)
    Note over W2: Worker 2 dies mid-task on Chunk #4
    Note over Redis: No heartbeat received for 15s
    Redis-->>Orch: Key worker:W2:lease expires (TTL <= 0)
    Orch->>Orch: Reaper marks Worker 2 OFFLINE in MongoDB
    Orch->>Rabbit: Atomically re-publishes Chunk #4 (retry = 1)
    Orch-->>Admin: Dashboard displays: "[WARNING] W2 timed out. Chunk #4 re-queued"
    Rabbit->>W1: Active-pushes Chunk #4
    W1->>W1: Processes and uploads Chunk #4
    W1-->>Orch: Chunk #4 Complete
    Note over Admin: Job completes at 100% with ZERO data loss!
```

- **Pass Criteria:**
  - Time elapsed from worker kill to task re-dispatch is **strictly $\le 16.0$ seconds** (15s lease + 1s reaper interval).
  - Job reaches 100% completion without manual intervention.

---

### Phase 5: Real-Time WebSocket Telemetry Verification

#### Protocol 5.1: Latency & Reconnection Audit
- **Test:** Compare timestamp of worker `POST /task_complete` against timestamp of UI state update in browser DevTools.
- **Pass Criteria:**
  - Event propagation latency $\le 30\text{ms}$.
  - Simulating network drop in browser (turning network offline for 5s then online) automatically re-establishes the WebSocket connection without page reload.

---

### Phase 6: Capstone Defense Demonstration Runbook

Follow this scripted procedure during your final evaluation:

1. **Architecture & Infrastructure Walkthrough (2 mins):**
   - Open Docker Desktop: show 4 core containers (RabbitMQ, MinIO, Redis, Mongo).
   - Open MinIO Web Console (`http://localhost:9091`): show bucket `daemon-jobs`.
2. **Dashboard Overview (2 mins):**
   - Open `http://localhost:5555`: show Role Gateway (`/role-select`).
   - Log in as Orchestrator: show Active Jobs table, Queue Broker status, and metrics.
3. **Multi-Node Job Dispatch (3 mins):**
   - Click **"Deploy New Job"**: select `Image Processing`, compute mode `Hybrid`, attach `payload.zip`.
   - Show 2 terminal windows:
     - Terminal 1: Worker 1 running on NVIDIA GPU (CuPy CUDA 12.4).
     - Terminal 2: Worker 2 running on CPU (NumPy fallback).
   - Show live streaming events in the UI terminal: notice GPU node completes chunks in ~0.08s while CPU node completes in ~0.45s!
4. **Live Chaos Resilience Test (3 mins):**
   - Submit a 10-chunk job.
   - While chunks are processing, **kill Worker 2's terminal (`Ctrl+C` or `docker stop`)**.
   - Show the jury the live terminal: within 15 seconds, a yellow warning pops up:
     `[WARNING] NODE-XXXX timed out. Chunk #X re-queued.`
   - Show Worker 1 picking up the abandoned chunk and finishing the job at 100%.
5. **Download & Final Output Inspection (1 min):**
   - Click the green **"Download Results ZIP"** button.
   - Open the downloaded ZIP and show the finished edge-detected and enhanced images.
