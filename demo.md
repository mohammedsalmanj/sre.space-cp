# � SRE-Space: Orbital Demonstration Guide

This guide outlines five high-impact scenarios to demonstrate the **Autonomous Reliability Engine v4.8**.

---

## 🏗️ Demo Scenarios

### 1. The "DB Pool Exhaustion" Remediation
*   **The Problem**: The insurance app starts spiking with HTTP 500s due to database connection leaks.
*   **Agent Logic**: 
    - **Scout** detects the sudden drop in success metrics.
    - **Brain** identifies the specific "Pool Exceeded" trace in Jaeger.
    - **Fixer** creates a PR increasing the `DB_POOL_SIZE` and adds a connection-timeout guard.
*   **Verification**: The Dashboard badge turns Green, and the PR appears in the Veracity feed.

### 2. Semantic Memory Retrieval (Avoid Duplicated Work)
*   **The Problem**: A known "Redis Timeout" issue occurs for the second time.
*   **Agent Logic**: 
    - **Brain** queries **ChromaDB** with the current trace fingerprint.
    - It finds a previous Post-Mortem and realizes the fix is already known.
    - Instead of re-analyzing, it immediately executes the proven fix.
*   **Verification**: Show the "Memory Hit" log in the OODA Loop stream.

### 3. Resource-Aware Guardrail (Memory Safety)
*   **The Problem**: The agents are performing heavy reasoning, and the system nears the 512MB RAM limit on Render.
*   **Agent Logic**: 
    - **Memory Guard Middleware** triggers a log warning.
    - The **Guardrail Agent** detects the resource pressure.
    - It pauses non-essential background tasks (like Jules' deep clean) to prioritize the active hotfix.
*   **Verification**: Show the "Critical RAM" warning in the real-time logs.

### 4. GitOps Approval Flow (Human-in-the-Loop)
*   **The Problem**: A high-risk architectural change is proposed by Jules.
*   **Agent Logic**: 
    - The **Decision Node** classifies the fix as "HIGH_RISK".
    - It transitions the state to the **Human Agent** node.
    - The loop waits for a manual label on the GitHub Issue before proceeding.
*   **Verification**: The Dashboard shows "Awaiting Human Consent" and transitions only after approval.

### 5. Multi-Cloud Failover Demo
*   **The Problem**: Deployment happens in "Local Mode" but needs to simulate "Cloud" constraints.
*   **Agent Logic**: 
    - Toggle the `ENV` variable in `.env`.
    - Watch as the **Scout Agent** automatically switches from polling Kafka to polling the Health API.
    - Observe the fleet scaling down from 8 to 5 agents dynamically.
*   **Verification**: The "Deployment Badge" on the dashboard changes from Amber (LOCAL) to Blue (CLOUD).

---

## 🏁 Execution Steps

1. **Reset State**: Ensure all active PRs are merged or closed.
2. **Inject Chaos**: Use the **Insurance Playground** (Cyber-HUD) and click **🔥 INJECT CHAOS**.
3. **Monitor**: Open the **Control Loop Dashboard** (Liquid Glass) to watch the OODA stream live.
4. **Verify Veracity**: Click the PR card in the dashboard to view the generated SRE Post-Mortem on GitHub.

---
**Build for Resilience. Verified by Veracity.** 🚀
