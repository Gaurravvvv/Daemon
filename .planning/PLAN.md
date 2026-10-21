# DaeMon: Master Execution Plan (`PLAN.md`)

> **Document Type:** Master Execution Plan (`PLAN.md`)  
> **Status:** Pending Review / Ready for Execution  
> **Target System:** DaeMon Distributed Compute Grid  
> **Execution Strategy:** Dependency-Aware Wave Execution across 6 Phases  

---

## 1. Roadmap Overview & Execution Waves

```mermaid
flowchart TD
    subgraph Wave_1 ["Wave 1: Core Foundation & Bug Fixes"]
        P1["Phase 1: Container Connectivity Fix<br/>(Uvicorn 0.0.0.0 & Gateway Routing)"]
    end

    subgraph Wave_2 ["Wave 2: Polymorphic Strategy Implementation"]
        P2A["Phase 2A: Matrix Multiplication Strategy<br/>(worker/strategies/matrix_strategy.py)"]
        P2B["Phase 2B: Cryptographic PoW Search Strategy<br/>(worker/strategies/crypto_strategy.py)"]
    end

    subgraph Wave_3 ["Wave 3: Aggregation & Resilience Engines"]
        P3["Phase 3: Real Result Aggregation & Output Stitching<br/>(orchestrator/core/aggregator.py)"]
        P4["Phase 4: Sub-15s Churn Resilience & Heartbeat Failover<br/>(Redis TTL & Reaper Coroutine)"]
    end

    subgraph Wave_4 ["Wave 4: Live Telemetry & Observability"]
        P5["Phase 5: Real-Time WebSockets & Telemetry<br/>(FastAPI /ws & Next.js Terminal)"]
    end

    subgraph Wave_5 ["Wave 5: Evaluation & Capstone Presentation"]
        P6["Phase 6: Multi-Worker Demonstration & Speedup Benchmarks<br/>(Amdahl's Law Curves & Defense Testbed)"]
    end

    Wave_1 --> Wave_2
    Wave_2 --> Wave_3
    Wave_3 --> Wave_4
    Wave_4 --> Wave_5
```

---

## 2. Phase-by-Phase Detailed Task Specifications

### Phase 1: Core Container Connectivity Fix (Unblocking Problem #3)

#### 🎯 Goal:
Eliminate the loopback rejection error so volunteer worker containers running inside Docker can seamlessly register with the host Orchestrator, stream chunks from MinIO, and report real-time execution events.

#### 📋 Tasks:

- [ ] **Task 1.1: Rebind Orchestrator to All Network Interfaces (`0.0.0.0`)**
  - **Files:** `start_grid.bat`, `orchestrator/main.py`
  - **Action:** Update the Uvicorn launch command to include `--host 0.0.0.0 --port 8000`. Add logging in `orchestrator/main.py` confirming binding to all network interfaces.
  - **Rationale:** Allows requests originating from Docker's virtual gateway adapter (`192.168.65.x` or bridge network) to be accepted rather than dropped by Windows loopback protection.

- [ ] **Task 1.2: Standardize Worker Docker Environment & Gateway Flags**
  - **Files:** `worker/Dockerfile`, `dashboard/src/app/(dashboard)/worker/job/[id]/page.tsx`, `dashboard/src/app/(dashboard)/orchestrator/page.tsx`
  - **Action:** Ensure Docker run commands use `--add-host=host.docker.internal:host-gateway` and pass correct environment variables:
    ```bash
    docker run --rm -it --gpus all \
      --add-host=host.docker.internal:host-gateway \
      -e ORCHESTRATOR_URL="http://host.docker.internal:8000" \
      -e RABBITMQ_URL="amqp://guest:guest@host.docker.internal:5672/" \
      -e MINIO_URL="http://host.docker.internal:9090" \
      -e POOL_ID="public_pool" \
      daemon-worker
    ```

- [ ] **Task 1.3: Verification Smoke Test**
  - **Action:** Boot grid via `start_grid.bat`, run 1 Docker worker, and verify that the worker registers in MongoDB and its `SYSTEM` join event appears live on the Next.js dashboard terminal.

---

### Phase 2: Polymorphic Workload Strategies (Real Math & Crypto Engines)

#### 🎯 Goal:
Fulfill the polymorphic compute grid contract by implementing genuine Block Matrix Multiplication and Cryptographic Nonce Search, moving completely beyond simulated dummy math.

#### 📋 Tasks:

- [ ] **Task 2.1: Implement Distributed Block Matrix Multiplication Strategy**
  - **File:** `worker/strategies/matrix_strategy.py`
  - **Inputs:** `matrix_chunk_i.json` containing sub-block row slice $A_{\text{slice}}$ and column matrix $B$.
  - **Computation:** Load into `numpy.ndarray` float64 arrays, compute dot product $C_{\text{block}} = A_{\text{slice}} \times B$ using high-performance BLAS.
  - **Output:** Save serialized JSON block to MinIO:
    `minio://daemon-jobs/{job_id}/results/{task_id}_matrix_block_{chunk_index}.json`.

- [ ] **Task 2.2: Implement Cryptographic Proof-of-Work (PoW) Search Strategy**
  - **File:** `worker/strategies/crypto_strategy.py`
  - **Inputs:** Target difficulty prefix (e.g., `"0000"`), header string, and keyspace range $[S_j, E_j]$ from `crypto_batch_i.json`.
  - **Computation:** Fast iterative SHA-256 loop:
    $$\text{hash} = \text{hashlib.sha256}(\text{header} + \text{str}(nonce)).\text{hexdigest}()$$
  - **Early Termination:** Check periodically (or via thread event) for early abort broadcast. If matching hash is found, immediately emit success event and trigger early abort.

- [ ] **Task 2.3: Wire Dynamic Strategy Dispatch in Task Consumer**
  - **File:** `worker/consumer.py`
  - **Action:** Update `process_message` to route `job_type == "image"` to `ImageProcessingStrategy`, `job_type == "math"` to `MatrixMultiplicationStrategy`, and `job_type == "crypto"` to `CryptoSearchStrategy`.

- [ ] **Task 2.4: Implement Early-Abort AMQP Signal Channel**
  - **Files:** `orchestrator/api/routes.py`, `worker/consumer.py`
  - **Action:** When a worker finds the golden nonce, call `POST /api/v1/jobs/{job_id}/abort`. The orchestrator publishes an `ABORT` message to the RabbitMQ exchange, causing sibling workers on that job to cancel remaining computation.

---

### Phase 3: True Result Aggregation & Output Stitching

#### 🎯 Goal:
Transform the placeholder mock stitcher into an automated assembly engine that produces verified, downloadable final deliverables.

#### 📋 Tasks:

- [ ] **Task 3.1: Build Domain-Specific Stitching Handlers**
  - **File:** `orchestrator/core/aggregator.py`
  - **Image Stitcher:** Download all edge and enhanced images from MinIO. If horizontal slices with overlap margins were used, crop the 1-pixel overlap and concatenate vertically via Pillow. Package into `{job_id}_final_images.zip`.
  - **Matrix Stitcher:** Download all sub-block JSONs, allocate composite matrix $C$ of shape $(N, N)$, place each sub-block into its coordinate slice, and serialize to compressed `.npz` and `.csv`.
  - **Crypto Stitcher:** Consolidate hash rate, verified nonce, and execution metrics into `{job_id}_proof_of_work.json`.

- [ ] **Task 3.2: Automate Completion Trigger in Task Complete Endpoint**
  - **File:** `orchestrator/api/routes.py`
  - **Action:** In `/api/v1/jobs/{job_id}/task_complete`, when `completed_chunks >= total_chunks`:
    - Mark job status as `stitching`.
    - Invoke `StateAggregator.stitch_results(job_id)`.
    - Upload `{job_id}_final.zip` to MinIO.
    - Set job status to `completed` and update `final_result_url`.
    - Emit `[SUCCESS] All chunks stitched into final artifact.` event to the dashboard.

- [ ] **Task 3.3: Verify Streaming Download Endpoint**
  - **File:** `orchestrator/api/routes.py` (`/api/v1/jobs/{job_id}/download`)
  - **Action:** Ensure the download endpoint delivers the assembled `{job_id}_final.zip` directly to the browser with proper Content-Disposition headers.

---

### Phase 4: Sub-15s Churn Resilience & Heartbeat Failover

#### 🎯 Goal:
Activate the Redis TTL sliding-window lease mechanism to guarantee automated, deterministic recovery from unannounced worker disconnects without pipeline stall.

#### 📋 Tasks:

- [ ] **Task 4.1: Worker Background Heartbeat Telemetry Thread**
  - **File:** `worker/main.py`
  - **Action:** Spawn a background daemon thread that sends an HTTP heartbeat every 5 seconds:
    `POST /api/v1/workers/{worker_id}/heartbeat` with payload `{cpu_percent, ram_percent, current_task_id}`.

- [ ] **Task 4.2: Implement Orchestrator Heartbeat Endpoint with Redis TTL**
  - **File:** `orchestrator/api/routes.py`
  - **Action:** On receiving heartbeat, write ephemeral key to Redis:
    `SET worker:<worker_id>:lease "active" EX 15`  
    Update worker document in MongoDB with latest metrics and timestamp.

- [ ] **Task 4.3: Implement Background Reaper Loop**
  - **File:** `orchestrator/core/aggregator.py`
  - **Action:** In `monitor_jobs()` loop (running every 3 seconds):
    - Scan active workers registered in MongoDB.
    - For each worker, check `redis_client.ttl(f"worker:{worker_id}:lease")`.
    - If TTL <= 0 or key does not exist:
      - Set worker status to `offline` in MongoDB.
      - Find any tasks assigned to this worker in `in_progress` state.
      - If task retry count $r_j < 3$:
        - Increment $r_j \leftarrow r_j + 1$.
        - Re-publish task manifest to RabbitMQ queue.
        - Emit warning event: `"[WARNING] Worker {id} timed out. Chunk #{k} re-queued (retry {r}/3)."`
      - Else:
        - Mark task `failed`.

---

### Phase 5: Real-Time WebSockets & Telemetry Refinement

#### 🎯 Goal:
Replace HTTP interval polling with a high-efficiency, full-duplex WebSocket stream for instant sub-second terminal log delivery and live hardware gauges.

#### 📋 Tasks:

- [ ] **Task 5.1: Implement FastAPI WebSocket Hub**
  - **File:** `orchestrator/api/routes.py`
  - **Action:** Create `ConnectionManager` class and endpoint `@router.websocket("/ws/jobs/{job_id}")`.
  - **Mechanics:** Store active WebSocket connections per `job_id`. Whenever `_emit_event()` is called, immediately broadcast JSON to all connected clients.

- [ ] **Task 5.2: Connect Next.js Terminal Component to WebSocket**
  - **File:** `dashboard/src/app/(dashboard)/orchestrator/job/[id]/page.tsx`
  - **Action:** Replace `setInterval` event fetcher with a persistent `new WebSocket(...)` connection. Implement auto-reconnect logic with exponential backoff.

- [ ] **Task 5.3: Add Real-Time Hardware Telemetry Gauges to UI**
  - **File:** `dashboard/src/app/(dashboard)/worker/page.tsx`
  - **Action:** Display live CPU utilization bar, VRAM usage, and active compute mode chip (`[GPU: CUDA 12.4]` or `[CPU Mode]`) driven by real-time heartbeat data.

---

### Phase 6: Multi-Worker Demonstration & Speedup Benchmark Suite

#### 🎯 Goal:
Produce concrete empirical speedup figures, throughput charts, and a rock-solid demonstration runbook for the capstone project evaluation and defense.

#### 📋 Tasks:

- [ ] **Task 6.1: Build Automated Benchmark Script**
  - **File:** `tests/run_benchmark_suite.py`
  - **Action:** Programmatically submits standard test workloads across 1, 2, and 4 worker nodes:
    - 100-image Sobel convolution batch.
    - 2048x2048 Matrix Multiplication.
    - SHA-256 Nonce Mining difficulty `00000`.
  - Records total execution time $T_1, T_2, T_4$, computes empirical speedup $S(P) = T_1 / T_P$, and outputs comparison tables.

- [ ] **Task 6.2: Produce Speedup Curves & Charts**
  - **Action:** Generate matplotlib / seaborn visual plots showing:
    - Speedup vs. Number of Nodes (comparing against theoretical Amdahl's Law curve).
    - GPU vs. CPU processing time comparison.
    - RabbitMQ broker memory stability vs. payload size.

- [ ] **Task 6.3: Create Step-by-Step Defense Runbook**
  - **File:** `DEMO_RUNBOOK.md`
  - **Action:** Create a scripted walkthrough for the final presentation, including the live "Worker Kill" resilience test and 1-click artifact download.

---

## 3. Scope Fences & Guardrails

- **Strictly in Scope:**
  - Fixing container-to-orchestrator communication via `0.0.0.0`.
  - Real Matrix Multiplication strategy using NumPy BLAS.
  - Real SHA-256 PoW strategy with early abort signal.
  - Automated stitching of completed chunks into a final ZIP in MinIO.
  - Redis 15s TTL heartbeat leasing with automated task re-queueing.
  - WebSocket event streaming in FastAPI and Next.js.
  - Benchmark evaluation script for Amdahl's Law validation.

- **Out of Scope (Post-Capstone Enhancements):**
  - Multi-datacenter WAN peering across dynamic public IPs (focus is LAN / Docker edge cluster).
  - Byzantine fault tolerance / zero-knowledge proof verification of worker calculations (trusted volunteer model).
  - Kubernetes / K8s Helm charts (defeats the lightweight volunteer ethos).
