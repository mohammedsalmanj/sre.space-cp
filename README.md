# 🌌 SRE-Space: Orbital Reliability Engine v4.8

**SRE-Space** is an autonomous, agentic reliability platform designed to transform "Alert-and-Wait" operations into "Detect-and-Heal" automation. It uses a stateful multi-agent system (LangGraph) to observe, diagnose, and remediate production incidents in real-time.

---

## 💡 The Problem We Solve
Traditional SRE operations are slowed down by:
1.  **Observability Fatigue**: Thousands of logs/traces that require human hours to correlate.
2.  **Repetitive Remediation**: Solving the same configuration or resource issues over and over.
3.  **High MTTR**: Response times depend on human availability and context-switching.

**SRE-Space solves this by providing a Cognitive Control Plane**:
-   **Autonomous Correlation**: Agents connect OpenTelemetry traces to root causes in seconds.
-   **Institutional Memory**: Uses RAG (Retrieval-Augmented Generation) to recall how similar incidents were fixed in the past.
-   **Self-Healing GitOps**: Automatically opens PRs with verified fixes and triggers redeployments.

---

## 🚀 Dual-Deployment Framework
Optimized for the modern cloud/local hybrid development lifecycle.

-   **Eye (Monitoring - Vercel)**: The **Liquid Glass Dashboard** provides a high-fidelity window into the agent's OODA loop through real-time telemetry streaming and GitHub veracity feeds.
-   **Mind (Execution - Render)**: The **Control Plane** (FastAPI) hosts the LangGraph engine, Vector Memory (ChromaDB), and Agent Squad, executing remediations in a secure, resource-aware container.

---

## 🛠️ Tech Stack
-   **Orchestration**: LangGraph (Stateful Multi-Agent Workflow).
-   **Intelligence**: GPT-4o-mini (Optimized for speed and cost).
-   **Observability**: OpenTelemetry + Jaeger (Tracing & Metrics).
-   **Event Bus**: Redis (Cloud) / Apache Kafka (Local).
-   **Persistence**: ChromaDB (Semantic Vector Store).
-   **Frontend**: Vanilla JS + CSS (Liquid Glass & Cyber-HUD Design).

---

## 🏁 Quick Start: Local Mode
```bash
# 1. Start the infrastructure (Kafka, ChromaDB, Jaeger)
docker-compose up -d

# 2. Configure Environment
cp .env.example .env # Add your keys

# 3. Launch the Control Plane
pip install -r requirements.txt
python apps/control_plane/main.py
```

## 📊 Deployment Tiers
| Feature | Local (Unleashed) | Cloud (Optimized) |
| :--- | :--- | :--- |
| **Agent Count** | 8 Agents | 5 Agents |
| **Memory** | Uncapped (up to 2GB) | 450MB Guardrail |
| **Event Bus** | Apache Kafka | Managed Redis |
| **Remediation** | Local Docker / Git | Github PR + Deploy Hooks |

---
**Build for 100% Uptime. Operated by Intelligence.** 🚀
