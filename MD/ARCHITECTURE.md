# Architecture & Technology Stack

To support a polymorphic grid (handling Images, Math, and Data) and an active "Push" orchestrator model, we need a robust, scalable architecture.

## High-Level Architecture Diagram
*(Imagine a hub-and-spoke model where the Master is the hub and Workers are the spokes, connected via a high-speed message bus).*

1. **Client / Dashboard** <---> `REST API & WebSockets` <---> **Master Orchestrator**
2. **Master Orchestrator** <---> `Message Broker` <---> **Worker Daemons (Nodes 1 to N)**
3. **Master Orchestrator** <---> `State Database + In-Memory Cache`

---

## Network Topology & Connectivity
The workers **do not** strictly need to be on the same local network, but they *must* be able to reach the Master Orchestrator. You have two main deployment options:

1. **Local Area Network (LAN):** 
   - If you run the Orchestrator on your home/office WiFi (e.g., `192.168.1.50`), then yes, all worker machines must be connected to that same WiFi/network to communicate with it.
2. **Wide Area Network (The Internet):** 
   - If you host the Orchestrator on a cloud server (like AWS or DigitalOcean) OR if you expose your local machine to the internet (using a tool like **Ngrok** or **Cloudflare Tunnels**), workers can be located **anywhere in the world**. They just need a standard internet connection to reach your public Orchestrator URL (e.g., `https://my-daemon-grid.com`).

---

## The Technology Stack

### 1. Master Orchestrator (The Brain)
- **Framework:** Python with **FastAPI**
- **Why:** FastAPI is extremely fast, supports asynchronous programming natively (perfect for managing thousands of tasks and websocket connections), and auto-generates API documentation. 
- **Role:** Exposes endpoints for job submission, handles worker registration, runs the partitioning algorithms, and explicitly assigns/pushes tasks to workers.

### 2. Message Broker (The Nervous System)
- **Technology:** **RabbitMQ** (or Redis Pub/Sub)
- **Why:** Since we are using an **Active Push** model, RabbitMQ is excellent. The Orchestrator can create a specific queue/routing key for each registered worker (e.g., `worker_node_1_queue`) and push tasks directly to that specific machine.
- **Role:** Guarantees message delivery between the Orchestrator and the remote Worker Daemons, even over unstable networks.

### 3. Worker Daemons (The Muscle)
- **Framework:** Pure **Python** background processes (Headless).
- **Why:** Lightweight, easy to distribute, and can leverage Python's massive ecosystem for different task types.
  - *Images:* `Pillow` or `OpenCV`
  - *Math:* `numpy` or `sympy`
  - *Data:* `pandas`
- **Role:** Listens to its specific message queue, retrieves the raw data via a reference URL, executes the payload, and sends results/heartbeats back.
- **Deployment:** Fully containerized with **Docker**. This ensures a "zero-setup" experience for your personal machines—just run `docker run daemon-worker` and it instantly starts working.

### 4. Database & Storage (The Memory)
- **Primary DB:** **MongoDB** (NoSQL Document Store)
  - *Why:* Highly flexible for storing variable task payloads. Since we support Images, Math, and Data tasks, the payload schema will change per job. MongoDB handles this gracefully.
- **State/Cache:** **Redis**
  - *Why:* For fast, real-time state lookups. Redis will hold the live registry of all active workers, their heartbeats, and which exact task they are currently processing.
- **Object Storage (Massive Data):** **MinIO** (Free, Open-Source S3 Alternative)
  - *Why:* Industry standard for distributed task queues is to **never** pass large data through the message broker.
  - *Deployment:* **Self-Hosted Home Server (e.g., spare laptop)**. By hosting MinIO on a spare machine at home, the grid gets hundreds of gigabytes of enterprise-grade storage completely for free. The Orchestrator simply sends the MinIO *download URL* to the worker.

### 5. Analytics Dashboard & Admin Panel (The Eyes)
- **Technology:** **React.js** (via Vite or Next.js)
- **Why:** React combined with WebSockets is perfect for building a highly dynamic, real-time dashboard. It offers ultimate UI customization, smooth micro-animations, and a premium look and feel that we can completely control.
- **Role:** Acts as an **Admin Control Panel**. It visualizes Orchestrator metrics (live progress bars, worker health graphs, system throughput) AND provides manual controls to Pause Jobs, Kill Misbehaving Workers, and Submit New Jobs.

---

## The "Polymorphic" Task Engine
Because we are supporting multiple workloads, the Orchestrator will use a **Strategy Pattern** for splitting tasks:
1. **Image Strategy:** Splits a batch of 1,000 images into 100 tasks of 10 images each.
2. **Math Strategy:** Splits a search range (e.g., find primes between 1 and 1,000,000) into chunks of 10,000 numbers per task.
3. **Data Strategy:** Reads a large dataset (e.g., a massive CSV) and splits it by row indices or file chunks for parallel processing.
