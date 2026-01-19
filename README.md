# 🌌 SRE-Space: The Cognitive Reliability Engine v3.0

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/AI-LangGraph-FF6F00?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Infra-Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

**SRE-Space** is an autonomous "Immune System" for microservice architectures. It transforms monitoring from a human-reactive pager hell into a **Cognitive Control Plane** where AI agents detect, diagnose, and remediate incidents using real-world telemetry.

---

## 🏗️ The Execution Model: "Hybrid Autonomy"

One of the key nuances of SRE-Space v3.0 is its **Hybrid Execution Model**. Unlike monolithic apps, SRE-Space splits the world into two layers:

### 1. The Infrastructure Layer (Docker Engine) 🐳
The "Body" of the system. We use Docker to run the heavy-duty ecosystem that provides the agents with their "Senses" and "Memory":
*   **Jaeger**: Provides the Distributed Tracing data (The Senses).
*   **OTel Collector**: Aggregates telemetry from all microservices.
*   **Kafka**: Acts as the nervous system for real-time event streaming.
*   **ChromaDB**: The Long-term Vector Memory (The Brain's RAG layer).

### 2. The Logic Layer (Python / Uvicorn) 🐍
The "Mind" of the system. The Agents (Scout, Brain, Fixer, Jules) run as a **LangGraph State Machine** inside the FastAPI application.
*   **Uvicorn** starts the server.
*   When a request comes in, the **LangGraph Engine** initiates a "Healing Loop."
*   Agents call out to the Docker-hosted services (Kafka/OTel) to make decisions.

---

## 🕵️ Detailed Agent Nuances (LangGraph Workflow)

The system doesn't just run code; it follows a **Directed Acyclic Graph (DAG)** of reasoning:

1.  **Scout (The Trigger)**: Scout monitors the OTel trace flow. It specifically looks for `error=true` tags in span attributes. When detected, it snapshots the state and passes it to the next node.
2.  **Brain (The Analysis)**: The Brain agent retrieves the stack trace from the Docker-hosted Jaeger instance. It uses its RAG memory to see if this error has happened before.
3.  **Fixer (The Action)**: The Fixer is responsible for remediation. Because it runs in the Python environment, it can trigger external commands, update configs, or send signals back to Docker.
4.  **Jules (The Hardening)**: Jules performs the "Post-Mortem." It updates the vector store in ChromaDB so the system "learns" from the incident.

---

## 🚀 How to Run (Step-by-Step Nuances)

To get SRE-Space fully operational, you must follow this two-stage startup:

### Phase 1: Spin up the Infrastructure (Docker)
Ensure Docker Desktop/Engine is running. This sets up the environment that the agents will monitor.
```bash
docker-compose up -d
```
*Wait ~30 seconds for Kafka and ChromaDB to initialize.*

### Phase 2: Start the Cognitive Engine (Python)
Now that the infra is alive, start the "Mind" of the system.
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the FastAPI Control Plane
uvicorn main:app --reload --port 8000
```

### Phase 3: Access & Test
*   **UI Dashboard**: `http://localhost:8000`
*   **Jaeger Traces**: `http://localhost:16686`
*   **Vector API**: `http://localhost:8000` (ChromaDB)

---

## 📚 Agentic RAG: How Memory is Handled

RAG (Retrieval-Augmented Generation) is the key to enterprise scaling. 

*   **Storage**: Every time an agent fixes a bug, the resolution and the trace logs are converted into an embedding and stored in **ChromaDB**.
*   **Retrieval**: During a new incident, the **Brain Agent** sends the current error message to ChromaDB. It retrieves the **Top 3 similar incidents**.
*   **Benefit**: This reduces the "Search Space" for fixes. The system doesn't "guess"; it remembers.

---

## ⚡ Scaling Nuances

*   **Production OTel**: In a real production environment, your microservices (Java, Go, Node) would send traces to the `otel-collector` hosted in Docker. SRE-Space would then monitor that central collector.
*   **Agent Parallelism**: LangGraph allows SRE-Space to handle multiple incidents simultaneously without blocking the main event loop.
*   **Vercel Nuance**: When deploying to Vercel, the "Logic Layer" (FastAPI) is serverless. It connects to your managed Infrastructure Cloud (e.g., Aiven for Kafka, Pinecone for RAG, or a hosted Jaeger instance).

---

## 🧪 Validating the Loop
1.  Open the Dashboard.
2.  Click **"Inject Chaos"**.
3.  Observe the logs:
    *   **Scout** detects the injected trace via Docker.
    *   **Brain** pulls the error from the OTel infra.
    *   **Fixer** applies the patch.
    *   **Jules** archives the lesson.

---

> "Monitoring is about knowing. SRE-Space is about solving." 🌌
