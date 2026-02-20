# SRE-Space: The Autonomous Reliability Engine

### A Production-Grade Multi-Agent Control Plane for Self-Healing Infrastructure
[![Architecture: Master Portal](https://img.shields.io/badge/UI-Master_Portal-blue?style=for-the-badge)](https://github.com/mohammedsalmanj/sre.space-cp)
[![Reliability: LangGraph Loop](https://img.shields.io/badge/Loop-Hardened_OODA-green?style=for-the-badge)](https://github.com/mohammedsalmanj/sre.space-cp)

---

## 🌌 The Mission
**SRE-Space** is not just an application; it is an autonomous engineering supervisor. It transforms modern distributed systems from **Passive Observability** to **Active Autonomy**. By orchestrating a squad of 8 specialized agents via **LangGraph**, it creates a closed-loop system that identifies, diagnoses, and remediates infrastructure anomalies in real-time.

---

## 🏛️ The Master Portal Architecture
The entire platform is unified into a single, high-fidelity **Master Portal**, eliminating the friction of multi-url monitoring.

### 1. The Insurance Nexus (User Plane)
*   **Purpose**: A live enterprise underwriting application.
*   **Chaos controls**: Built-in Engineering Controls to inject real Database Saturation (500) and Latency spikes.

### 2. The SRE Intelligence Plane (Control Station)
*   **Purpose**: Real-time observability of the agentic cognitive flow.
*   **Capabilities**:
    *   **OODA Pulse Visualization**: Live tracking of the Observe → Orient → Decide → Act cycle.
    *   **Intelligence Stream**: A sub-second SSE terminal showing the raw cognitive thoughts of the agents.
    *   **GitOps Sync**: Real-time integration with the GitHub API to display autonomous PRs and Issues.

---

## 🤖 The agentic Squad (OODA Loop)

Our agents operate in a strict, high-confidence sequence:

| Phase | Agent | Role | Capability |
| :--- | :--- | :--- | :--- |
| **OBSERVE** | 🕵️ **Scout** | Telemetry Analyst | Samples real OTel traces and hardware metrics (`psutil`). |
| **ORIENT** | 🧠 **Brain** | RCA Synthesis | Synthesizes Root Cause using GPT-4 and RAG memory. |
| **DECIDE** | 🛡️ **Guardrail** | Safety Enforcer | Vetoes any fix that doesn't meet strict safety policies. |
| **ACT** | 🛠️ **Fixer** | GitOps Executor | Creates real GitHub branches, commits code, and merges PRs. |
| **AUDIT** | 🤖 **Jules** | Arch Reviewer | Performs daily architectural integrity scans. |

---

## 💎 Elite Features

*   **100% Real Autonomy**: No mocks. No fake data. The system physically modifies the GitHub repository state to apply fixes.
*   **Neural Bridge UI**: A "Frost Glass" design language that unifies the user app and the monitoring station.
*   **Memory Guard**: An active runtime governor that throttles agent execution to stay within Render's 512MB RAM limits.
*   **Unified Deployment**: Single-entry deployment via Docker, optimized for the Render (Backend) + Vercel (Monitor) architecture.

---

## 🚀 Quick Launch

1.  **Configure Environment**:
    ```bash
    GITHUB_PERSONAL_ACCESS_TOKEN=your_pat
    OPENAI_API_KEY=your_key
    ENV=cloud
    ```
2.  **Execute Backend**:
    ```bash
    python apps/control_plane/main.py
    ```
3.  **Access Portal**: Visit `http://localhost:8001` or your cloud URL to experience the self-healing loop.

---

## 🧪 Validation & Demo
For a step-by-step sequence on how to break the system and watch it heal, refer to the **[DEMO.md](./DEMO.md)**.

---
<div align="center">
  <b>Designed for Zero-Downtime. Driven by Cognitive Intelligence.</b><br>
  <i>SRE-Space Portal v5.5 (Final Release)</i>
</div>
