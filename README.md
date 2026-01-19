# 🌌 SRE-Space: The Cognitive Reliability Engine v3.0

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/AI-LangGraph-FF6F00?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![OpenAI](https://img.shields.io/badge/LLM-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![ChromaDB](https://img.shields.io/badge/Memory-ChromaDB-white?style=for-the-badge&logo=googlechrome&logoColor=black)](https://www.trychroma.com/)
[![OpenTelemetry](https://img.shields.io/badge/Tracing-OTel-F46800?style=for-the-badge&logo=opentelemetry&logoColor=white)](https://opentelemetry.io/)
[![Vercel](https://img.shields.io/badge/Cloud-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com/)

**SRE-Space** is an autonomous, self-healing **Cognitive Control Plane** designed for high-availability microservice ecosystems. It moves beyond simple alerts by orchestrating a modular squad of AI agents that detect anomalies, reason through root causes, enforce safety guardrails, and architecturally harden the system—all without human intervention.

---

## 🏛️ Diagram 1: System Topology (Mind & Body)

SRE-Space is architected as a **Hybrid Control Plane**. The **Body** handles sensory data and persistence, while the **Mind** executes the agentic reasoning loop.

```mermaid
graph TD
    subgraph "Control Plane (The Mind - Python/LangGraph)"
        UI[Glassmorphic Dashboard]
        Logic[LangGraph Squad Engine]
        UI <-->|SSE Streaming| Logic
    end

    subgraph "Infrastructure (The Body - Docker/K8s)"
        subgraph "Sensory Organs (OTel Stack)"
            Collector[OTel Collector]
            Jaeger[Jaeger UI]
        end
        subgraph "Nervous System (Events & Memory)"
            Kafka[Kafka Event Bus]
            Chroma[(ChromaDB Vector Store)]
        end
    end

    %% Connections
    Logic -.->|Poll Spans| Collector
    Logic -.->|Query/Archive| Chroma
    Collector -->|Export| Jaeger
    
    style Logic fill:#1e1b4b,stroke:#4338ca,color:#fff,stroke-width:3px
    style Collector fill:#064e3b,stroke:#059669,color:#fff
    style Chroma fill:#831843,stroke:#db2777,color:#fff
```

---

## 🤖 Diagram 2: The 7-Agent Squad Workflow

We have modularized our intelligence into a **Directed Acyclic Graph (DAG)** of specialized agents. Each node handles a specific stage of the incident lifecycle.

```mermaid
graph LR
    A[🕵️ Scout] --> B[⚡ CAG]
    B -- Cache Hit --> D[🛡️ Guardrail]
    B -- Cache Miss --> C[🧠 Brain]
    C --> D
    D -- ALLOW --> E[🛠️ Fixer]
    D -- BLOCK --> F[🤖 Jules]
    E --> F
    F --> G[🧹 Curator]
    G --> END((STABLE))

    style B fill:#f59e0b,color:#000
    style D fill:#ef4444,color:#fff
    style G fill:#06b6d4,color:#fff
```

---

## 🧠 Diagram 3: Agentic RAG & Memory Curation

SRE-Space implements a **Tiered Memory Layer** to ensure the system never fixes the same bug twice. We use semantic similarity to bridge the gap between "Raw Logs" and "Actionable Knowledge."

```mermaid
sequenceDiagram
    participant B as Brain Agent
    participant C as ChromaDB (Memory)
    participant J as Jules Agent
    participant MC as Memory Curator

    Note over B,C: Incident Occurs
    B->>C: Query for similar Error Signatures
    C-->>B: Return Top 3 Remediation Plans
    Note over B: Score Confidence (Sim + Success + Recency)
    
    Note over J,MC: Post-Fix Hardening
    J->>MC: Evaluation: Was the fix successful?
    MC->>C: Archive: Merge/Store High-Signal Lesson
```

---

## 🏛️ Diagram 4: Jules Tier-3 Architectural Authority

**Jules** operates as the "Senior Architect" of the squad. While other agents fight fires, Jules eliminates the arsonist by redesigning the system architecture.

```mermaid
graph TD
    Trigger{Systemic Failure?}
    Trigger -- No --> Idle[Nominal Monitoring]
    Trigger -- Yes --> Analyze[Deep Code Refactor]
    
    subgraph "Architectural Optimization"
        Analyze --> CB[Circuit Breaker Injection]
        Analyze --> QO[Query Optimization]
        Analyze --> ACL[Adaptive Concurrency Limits]
    end

    CB & QO & ACL --> Review[Daily Review @ 09:30 AM]
```

---

## 🤖 The Squad: Technical Authority Matrix

| Agent | Icon | Module | Mission | Authority |
| :--- | :---: | :--- | :--- | :--- |
| **Scout** | 🕵️ | `scout.py` | Detection | Monitors OTel spans for failures/latency. |
| **CAG** | ⚡ | `cag.py` | Latency | Tier-1 Flash Cache for FAQ-style incidents. |
| **Brain** | 🧠 | `brain.py` | Diagnosis | RCA using OpenAI GPT-4o-mini & ChromaDB. |
| **Guardrail**| 🛡️ | `guardrail.py` | Safety | Enforces policy & confidence scores > 0.75. |
| **Fixer** | 🛠️ | `fixer.py` | Recovery | Executes code patches and resource scaling. |
| **Jules** | 🤖 | `jules.py` | Hardening | Tier-3 authority for deep system refactors. |
| **Curator** | 🧹 | `curator.py` | Memory | Cleans and tags Knowledge into Vector store. |

---

## ⚡ Technical Stack & Tooling

*   **Logic Engine**: LangGraph (Stateful, Multi-Agent Orchestration).
*   **LLM Power**: OpenAI GPT-4o-mini (Reasoning & Refactoring).
*   **Observability**: OpenTelemetry (OTLP) + Jaeger (Distributed Tracing).
*   **Vector Database**: ChromaDB (Incident Signature Memory).
*   **Nervous System**: Kafka (Real-time Event Streaming).
*   **Web Framework**: FastAPI (Asynchronous logic with SSE streaming).

---

## 🚀 Getting Started

### 1. Prerequisite: The Body (Docker)
Initialize the infrastructure that provides the sensors and memory:
```bash
docker-compose up -d
```

### 2. Prerequisite: The Mind (Python)
Install the logic dependencies and start the Control Plane:
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Verification: The Chaos Lab
Click **"Inject Chaos"** on the [Dashboard](http://localhost:8000). Monitor the **7-Agent Console** to see the system traverse from detection via Scout to long-term memory archiving via Curator.

---

## ☁️ Deployment
The Control Plane is continuously deployed via Vercel.
**Live Hub**: [https://sre-space-cp.vercel.app/](https://sre-space-cp.vercel.app/)

---

> "Monitoring tells you that you have a problem. SRE-Space makes sure you don't have it again." 🌌
