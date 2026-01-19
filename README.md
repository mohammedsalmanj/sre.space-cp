# 🌌 SRE-Space: The Cognitive Reliability Engine v3.0

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/AI-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-black.svg)](https://vercel.com/)

**SRE-Space** is an autonomous "Immune System" for microservice architectures. It transforms traditional monitoring—where humans react to alerts—into a **Cognitive Control Plane** where AI agents detect, diagnose, fix, and harden the system in real-time.

---

## 🏛️ System Philosophy: "The True North"

Most SRE tools stop at visibility. SRE-Space completes the loop. By integrating **LangGraph** (agent orchestration) with **OpenTelemetry** (deep visibility), the system doesn't just see a problem; it understands the "Why" and executes the "How."

### The 4 Pillars of Autonomy:
1.  **Observability-Driven**: No action is taken without OTel trace evidence.
2.  **Cyclic Reasoning**: Agents iterate through a LangGraph state machine.
3.  **Self-Healing**: Automated remediation without human pagers.
4.  **Persistent Memory**: Using RAG to learn from every historical incident.

---

## 🧠 How LangGraph Works (The Agent Squad)

The system uses a directed cyclic graph (LangGraph) to manage the lifecycle of an incident. Each agent is a node in this graph.

### 1. 🕵️ Scout Agent (Detection)
Scout is the "Watchman." It continuously polls **OpenTelemetry Spans**.
*   **Trigger**: High latency or HTTP 5XX spikes.
*   **Logic**: If Scout finds an error span, it snapshots the trace-id and transitions the state to the **Brain**.

### 2. 🧠 Brain Agent (Diagnostics)
The Brain is the "Strategist." It performs **Root Cause Analysis (RCA)**.
*   **Logic**: It extracts `exception.message` and `stacktrace` from OTel.
*   **Inference**: It determines if the failure is code-level (logic bug), infra-level (OOM/CPU), or data-level (DB timeout).

### 3. 🛠️ Fixer Agent (Remediation)
The Mechanic. It executes the suggested fix.
*   **Actions**: Restarts services, increases connection pools, or rolls back bad deployments.
*   **Verification**: It loops back to Scout to ensure the state has returned to "Nominal."

### 4. 🤖 Jules Agent (Hardening/Refactoring)
The Architect. Jules looks at the incident retrospectively.
*   **Logic**: It applies **Robustness Patterns** (Circuit Breakers, Retries, Hedged Requests) to prevent the same failure mode tomorrow.

---

## 📚 Memory Handling (Agentic RAG)

Scaling reliability requires remembering the past. SRE-Space handles knowledge via **Retrieval-Augmented Generation (RAG)**:

1.  **Knowledge Ingestion**: Every successful fixation is stored as a **"Post-Mortem Document"** in a vector database (e.g., ChromaDB).
2.  **Semantic Search**: When the Brain sees a new error, it queries the database for "Similar historical traces."
3.  **Few-Shot Remediation**: The Brain uses these historical results to verify its current remediation plan, ensuring that if a fix worked in 2024, it is utilized in 2026.

---

## ⚡ Scaling to the Enterprise

While this repository is a unified control plane, SRE-Space is designed to scale:

*   **Vertical Scaling**: The FastAPI backend is lightweight and stateless, allowing it to run in Kubernetes Sidecars or specialized Control-Plane pods.
*   **Horizontal Scaling**: In high-traffic environments, the **Scout** can be decoupled using **Kafka**. Real microservices emit traces to Kafka, which SRE-Space consumes as an event stream.
*   **Distributed Memory**: The RAG layer can be backed by a distributed Vector Cluster, allowing multiple SRE-Space instances across global regions to share "Reliability Lessons."

---

## 🛠️ Tech Stack & Setup

### Core Stack:
- **Language**: Python 3.9+
- **Agent Framework**: LangGraph (LangChain)
- **Backend**: FastAPI / Uvicorn / Jinja2
- **Observability**: OpenTelemetry SDK
- **Design**: Vanilla CSS / Tailwind (Glassmorphic)

### Local Development:
1.  **Clone & Install**:
    ```bash
    git clone https://github.com/mohammedsalmanj/sre.space-cp.git
    cd sre.space-cp
    pip install -r requirements.txt
    ```
2.  **Run the Control Plane**:
    ```bash
    uvicorn main:app --reload --port 8000
    ```
3.  **Access Dashboard**: Open `http://localhost:8000`

---

## 🧪 Chaos Lab (Testing)

Test the engine's intelligence by using the **"Inject Chaos"** button on the UI.
*   It forces a `HTTP 500: Database connection timeout` into the telemetry stream.
*   Watch the **Agent Squad Console** as Scout detects it and the subsequent agents restore the "Stable" state.

---

## ☁️ Deployment

The project is optimized for **Vercel** via `vercel.json`. It uses the `@vercel/python` runtime to serve the FastAPI app and LangGraph engine as serverless functions.

**Dashboard URL**: [https://sre-space-cp.vercel.app/](https://sre-space-cp.vercel.app/)

---

> "Monitoring tells you something is wrong. SRE-Space makes it right." 🌌
