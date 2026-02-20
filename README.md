<div align="center">
  <h1>🌌 SRE-Space: The Cognitive Reliability Engine v3.5</h1>
  <p><i>"Self-Healing Infrastructure through Multi-Agent Cognitive Cycles"</i></p>

  [![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![LangGraph](https://img.shields.io/badge/AI-LangGraph-FF6F00?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
  [![OpenAI](https://img.shields.io/badge/LLM-GPT--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
  [![ChromaDB](https://img.shields.io/badge/Memory-ChromaDB-white?style=for-the-badge&logo=googlechrome&logoColor=black)](https://www.trychroma.com/)
  [![OpenTelemetry](https://img.shields.io/badge/Tracing-OTel-F46800?style=for-the-badge&logo=opentelemetry&logoColor=white)](https://opentelemetry.io/)
</div>

---

## 🚀 The Vision
**SRE-Space** is not just a monitoring tool; it's an autonomous **Cognitive Control Plane**. It replaces traditional "alert-and-wait" workflows with a high-fidelity **Agentic Repair Loop**. 

Powered by **LangGraph**, it orchestrates a specialized squad of agents that simulate human SRE reasoning—detecting anomalies via OpenTelemetry, diagnosing root causes using RAG (Retrieval-Augmented Generation), and executing remediations through GitOps and Docker automation.

---

## 🏛️ System Architecture
The platform is a split-brain architecture where sensory input (Body) feeds agentic intelligence (Mind).

```mermaid
graph TD
    subgraph "Mind (Cognitive Control Plane)"
        Logic[LangGraph Squad Engine]
        Brain[GPT-4o Reasoning]
        Guard[Policy Guardrails]
    end

    subgraph "Body (Infrastructure & Sensors)"
        OTel[OTel Collector]
        Jaeger[Jaeger Tracing]
        Kafka[Kafka Event Bus]
        DB[(ChromaDB Memory)]
    end

    subgraph "Target Environment (Production)"
        Apps[Microservices Hub]
        Apps -->|Spans| OTel
    end

    OTel --> Jaeger
    Logic -->|Sensory Intake| OTel
    Logic -->|Cognitive Retrieval| DB
    Logic -->|Reasoning Escalation| Brain
    Logic -->|Policy Check| Guard
    Logic -->|GitOps Action| Apps
```

---

## 🤖 The 8-Agent High-Availability Squad

We have modularized intelligence into specialized roles, each with a specific technical authority:

| Agent | Module | Mission | Authority |
| :--- | :--- | :--- | :--- |
| **🕵️ Scout** | `packages/agents/scout.py` | Detection | Polls OTel traces for latency spikes and 5xx errors. |
| **⚡ CAG** | `packages/agents/cag.py` | Tier-1 Fix | Checks "Fast Cache" for instant FAQ-style remediations. |
| **🧠 Brain** | `packages/agents/brain.py` | RCA | Deep reasoning via RAG + OpenAI for complex failures. |
| **🛡️ Guardrail**| `packages/agents/guardrail.py`| Safety | Blocks non-compliant or low-confidence actions. |
| **🛠️ Fixer** | `packages/agents/fixer.py` | Execution | Standardized GitOps commits & Docker patch deployment. |
| **🤖 Jules** | `packages/agents/jules.py` | Hardening | Tier-3 Arch Authority for code-level design refactors. |
| **🧹 Curator** | `packages/agents/curator.py` | Memory | Tags and compresses postmortems into ChromaDB. |
| **🚨 Human** | `packages/agents/human.py` | HITL | Triggers email alerts if an issue repeats > 3 times. |

---

## 🛡️ Guardrails & Safety
Autonomous systems require trust. SRE-Space implements three layers of protection:
1. **Mathematical Confidence:** Agents must exceed a 0.85 confidence score to act.
2. **Policy Guardrail:** Validates that the remediation doesn't violate cluster constraints.
3. **Human-in-the-Loop (HITL):** If a loop is detected or an issue persists, the system halts and notifies **mohammedsalmanj@outlook.com**.

---

## 🛠️ Tech Stack
- **AI Orchestration:** LangGraph (Stateful Multi-Agent).
- **Core LLM:** OpenAI GPT-4o-mini.
- **Observability:** OpenTelemetry (OTLP) + Jaeger.
- **Event Bus:** Apache Kafka (Kraft Mode).
- **Vector Database:** ChromaDB.
- **Web Layer:** FastAPI (Async logic with Real-time SSE).

---

## 🌌 High-Autonomy Features (The "Fix Path" Evolution)

SRE-Space has evolved from simple logging to **Autonomous Operations**. The engine now differentiates between incident types and manages the entire GitOps lifecycle:

### ⚡ Unified GitOps Lifecycle (Standard for ALL Fixes)
Whether it's a code patch OR an infrastructure change, the engine follows a strict engineering protocol:
1. **🌿 Branching**: Automatically creates a unique fix branch (e.g., `fix-inc-441`).
2. **💾 Commits**: Prepares and pushes standardized, traceable commits.
3. **✅ Pull Requests**: Opens a PR on GitHub for full observability.
4. **🤝 Autonomous Merge**: Verifies the fix against safety policies and executes a Squash-Merge into `main`.
5. **📦 Deployment**: Triggers the rollout of the patched service or scaled infrastructure.

### 🌀 Parallel Autonomous Paths
- **Code Path**: Detects logic bugs (e.g., `ZeroDivisionError`) and executes a full GitOps cycle.
- **Infra Path**: Detects saturation/scaling issues and applies direct operational adjustments via IaC.

---

## 🛠️ Performance-First Design
- **⚡ Bolt Optimization**: The LangGraph state machine is **pre-compiled and cached** at the module level, eliminating cold-start latency (reduction of ~20ms per loop).
- **🚀 Real-time Streaming**: Incident reports are streamed via Server-Sent Events (SSE) for sub-second dashboard feedback.

---

## 🏛️ Monorepo Architecture
SRE-Space is organized as a unified monorepo for maximum traceability and component reuse.

- **`apps/`**: Deployable services.
  - `control_plane/`: The LangGraph squad engine and core API.
- **`packages/`**: Shared logic and libraries.
  - `agents/`: The 8-agent squad logic (Scout, CAG, Brain, Guardrail, Fixer, Curator, Human, Jules).
  - `shared/`: Common GitOps, GitHub, and reporting utilities.
- **`infra/`**: Infrastructure-as-Code (Docker Compose, Otel configuration).
- **`scripts/`**: Automation, verification, and chaos testing utilities.

---

## ⚡ Getting Started (Verification)

### 1. Launch & Start
```bash
docker-compose up -d
python apps/control_plane/main.py
```

### 2. Run the Autonomy Suite
Verify both **Infra** and **Code** autonomous paths in one command:
```bash
python scripts/verify_autonomy.py
```

### 3. Verify Jules (The Architect)
Trigger a standalone architectural review:
```bash
python scripts/verify_jules.py
```

---

<div align="center">
  <p><i>"Monitoring tells you that you have a problem. SRE-Space makes sure you don't have it again."</i></p>
  <b>🌌 Built for the Future of Autonomous Operations</b>
</div>
