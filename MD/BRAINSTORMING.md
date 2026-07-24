# Daemon-Based Distributed Compute Grid

## 📖 Abstract
A decentralized distributed computing framework that harnesses the idle processing capacity of multiple networked machines to collaboratively execute large computational workloads. Inspired by volunteer-computing systems like BOINC.

## 🧩 Core Architecture
1. **Master Orchestrator**: The central brain. Accepts large computational jobs and partitions them into smaller, independent micro-tasks.
2. **Message Broker**: A high-throughput queuing system that reliably distributes these micro-tasks to available workers.
3. **Worker Daemons**: Lightweight, headless background processes installed on participating machines. They poll for work, execute using idle resources, and return results.
4. **Fault-Tolerant State Aggregator**: Reassembles returned micro-task results into the final output. Handles worker disconnections and task failures via automatic retries and reassignment.
5. **Analytics Dashboard**: A real-time UI displaying active workers, task completion rates, and system throughput.

## 🎯 Key Objectives
- [ ] Design a task-splitting algorithm to partition large jobs into independent micro-tasks.
- [ ] Implement a message broker-based queuing system for reliable task distribution.
- [ ] Build lightweight worker daemons capable of executing tasks and reporting results.
- [ ] Implement fault-tolerance mechanisms to handle worker failure/disconnection mid-task.
- [ ] Develop a real-time dashboard to visualize grid health and task progress.

## 🛠️ Proposed Technology Stack
- **Core Language**: Python
- **Message Broker**: Celery / RabbitMQ / Redis
- **Orchestrator API**: REST API (e.g., FastAPI, Flask, or Django)
- **Dashboard**: Streamlit (Python-native, quick to build) or React (more customizable)
- **Environment/Isolation**: Docker (optional for worker isolation)

---

## 🧠 Decisions & Documentation

We have finalized the core direction of the project based on our brainstorming:

1. **Polymorphic Workloads:** The grid will support *all* types of processing (Images, Math, Data).
2. **Active Push Model:** The Orchestrator will actively track workers and push tasks directly to them, rather than workers pulling from a generic pool.
3. **Tech Stack:** Python (FastAPI), RabbitMQ/Redis, MongoDB, **MinIO** (Object Storage), and React.js. Workers run in **Docker**.

### 📂 Detailed Documentation
For a deep dive into how these decisions are implemented, please refer to:
- 🏗️ **[Architecture & Tech Stack](file:///c:/Users/VICTUS/OneDrive/Desktop/Internship/Personal/DaeMon/ARCHITECTURE.md)**: Details the specific technologies (FastAPI, RabbitMQ, MongoDB) and system components.
- 🔄 **[System Workflow](file:///c:/Users/VICTUS/OneDrive/Desktop/Internship/Personal/DaeMon/WORKFLOW.md)**: Explains the step-by-step lifecycle of a job, from submission to partitioning, push-distribution, and final aggregation.
- 🔌 **[API & JSON Schemas](file:///c:/Users/VICTUS/OneDrive/Desktop/Internship/Personal/DaeMon/API_AND_SCHEMA.md)**: Details the REST endpoints and RabbitMQ payload structures.

---

## 🚀 Future Scope: The Compute Marketplace
If a user on the Vercel frontend has no friends to help them run workers, how do they get their tasks done? We can solve this by building a **Global Public Pool**:
1. **The Public Grid:** We allow anonymous users across the internet to download the Docker worker and run it attached to the `public_pool`. 
2. **Compute Credits (Economy):** To incentivize strangers to help, we introduce a credit system. When someone runs a worker on their laptop, they earn "Compute Tokens". 
3. **Spending Tokens:** When a user without friends needs a massive job done, they can spend their earned Compute Tokens to submit their job to the `public_pool`, and the anonymous workers will process it for them! This essentially turns the platform into a decentralized compute marketplace.

## 🖱️ Frictionless UI Onboarding
Instead of over-engineering a custom desktop app or browser-based WASM worker, we will keep the frontend lightweight and straightforward. 

When a user visits the "Global Job Board" and clicks a job they want to help with, the UI will simply present them with a modal containing:
1. **Instruction:** "Turn on Docker Desktop"
2. **Auto-Generated Command:** A pre-filled Docker command containing the Orchestrator URL and the specific Job ID.
   `(e.g., docker run -e ORCHESTRATOR_URL="..." -e TARGET_JOB="123" daemon-worker)`
3. **Copy Button:** A simple 1-click copy button. The user just pastes it into their terminal, and the automated magic begins.
