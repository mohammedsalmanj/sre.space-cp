# 🌌 SRE-Space: Orbital Demo Guide

Follow these steps to demonstrate the **Autonomous Reliability Engine v4.7** in action.

## 🏁 Phase 1: Environment Setup
Ensure your local or cloud infrastructure is active.

1. **Launch Stack (Local)**:
   ```bash
   docker-compose up -d
   python apps/control_plane/main.py
   ```
2. **Access Dashboard**:
   - Open your Vercel URL or `apps/dashboard/index.html`.
   - Verify the **Deployment Mode** badge (LOCAL or CLOUD).

---

## 🎭 Phase 2: The "Chaos Incident" Simulation

### Step 1: Inject Failure
You can trigger a failure via the API or the Render/Local UI.
```bash
# Using curl (Replace with local/render URL)
curl -X POST http://localhost:8001/demo/inject-failure
```

### Step 2: Watch the OODA Loop Live
Switch to the **Mission Control Dashboard**:
- **[OBSERVE]**: The Scout agent detects the DB Pool Exhaustion trace.
- **[ORIENT]**: The Brain agent analyzes the impact and consultations ChromaDB memory.
- **[DECIDE]**: Guardrail validates the remediation policy.
- **[ACT]**: Fixer agent creates a timestamped GitHub PR.

### Step 3: Verify on GitHub
- Go to the repository PRs tab.
- Show the automatically opened PR with the **SRE Post-Mortem**.
- *Note*: In Cloud Mode, the Fixer will also trigger the **Render Deploy Hook** to restart the service with the new configuration.

---

## 🏛️ Technical Transparency
| Component | Cloud Mode (Optimized) | Local Mode (Unleashed) |
| :--- | :--- | :--- |
| **Event Bus** | Redis | Apache Kafka |
| **Logic** | 5 Core Agents | 8-Agent High-Availability Squad |
| **Memory** | 450MB Guardrail | Uncapped (up to 2GB) |
| **Concurrency**| 2 LLM Threads | 5 LLM Threads |

---
**🌌 Built for the Future of Autonomous Operations.**
