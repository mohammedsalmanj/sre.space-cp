# 🚀 SRE-Space: End-to-End Validation Guide

This document provides a comprehensive workflow for testing and validating the **SRE-Space** platform. Following these steps will demonstrate the full **OODA loop** (Observe, Orient, Decide, Act) and verify the 100% real GitOps lifecycle.

## 📋 Prerequisites

Before starting, ensure your system is configured with:
1.  **Environment Sync**: Valid `OPENAI_API_KEY` and `GITHUB_PERSONAL_ACCESS_TOKEN` in your `.env` file.
2.  **Service Uplink**: The backend is running (`python apps/control_plane/main.py`).
3.  **Control Station**: Access the **Orbital Monitor** at `http://localhost:8001/monitor` (or your Vercel URL).
4.  **User Plane**: Access the **Insurance Marketplace** at `http://localhost:8001/`.

---

## 🧪 Phase 1: Nominal Operations

1.  **Marketplace Access**: Open the Insurance Marketplace.
2.  **Generate Quote**: Fill out the form and click **"Calculate Premium Trace"**.
3.  **Verify Telemetry**: 
    *   Confirm the quote is generated instantly.
    *   Observe the "OTel Span Emitted" log showing a unique trace ID.
4.  **Monitor Health**:
    *   Switch to the **Orbital Monitor**.
    *   Verify "System Integrity" is **NOMINAL** (Blue dot).
    *   Confirm Memory and Mode stats are updating every 3 seconds.

---

## 💥 Phase 2: Fault Injection (The 500 Test)

1.  **Inject Fault**: On the Marketplace sidebar, click **"500 Errors"**.
2.  **Observe Alert**: A browser alert will confirm the Engineering Control is triggered.
3.  **Trigger Failure**: Attempt to "Calculate Premium Trace" again. 
    *   **EXPECTED**: The form should fail with a red "System Anomaly Detected" message.
4.  **Monitor OODA Loop**:
    *   Switch to the **Orbital Monitor**.
    *   Observe the **Observe (Scout)** bar lighting up in blue.
    *   Watch the **Cognitive Trace** stream logs specifically identifying the `CRITICAL_ERROR_RATE`.

---

## 🧠 Phase 3: Autonomous RCA & Decisioning

1.  **Deep Analysis**:
    *   In the monitor, watch the **Orient (CAG/Brain)** bar activate.
    *   The logs will show the Brain engaging GPT-4 for "RCA synthesis".
2.  **Safety Check**:
    *   Observe the **Decide (Guardrail)** phase.
    *   The logs will confirm `POLICY_BYPASS` as the remediation is deemed safe.
3.  **GitHub Sync**:
    *   Check your GitHub sidebar in the monitor.
    *   A new **[INCIDENT]** issue should appear in real-time, created by the Brain agent.

---

## 🛠️ Phase 4: GitOps Action & Self-Healing

1.  **Remediation**:
    *   Observe the **Act (Fixer)** bar activate.
    *   Logs will stream: `BRANCH_PROVISIONED`, `COMMITTED`, and `PR_VALIDATED`.
2.  **Verify Pull Request**:
    *   Refresh the GitOps feed in the monitor or check your repo directly.
    *   You will see a PR with the title **[AUTONOMOUS-FIX]**.
3.  **Autonomous Merge**:
    *   The Fixer will automatically merge the PR.
    *   Logs will show: `SUCCESS: Remediated state merged. Resetting fault state.`
4.  **System Recovery**:
    *   The **Orbital Monitor** will return the status to **NOMINAL**.
    *   Return to the **Marketplace** and generate a new quote.
    *   **EXPECTED**: The quote flow is now 100% functional again.

---

## 📉 Phase 5: Resource Degradation (The Memory Test)

1.  **Trigger Spike**: On the Marketplace, click **"Memory Spike"**.
2.  **Verify Status**:
    *   In the monitor, observe the Operational Status change to **DEGRADED MODE**.
    *   The Memory Pressure bar will turn red/orange.
3.  **Observe Throttle**:
    *   Logs will indicate that the SRE loop is now running with "conservative heuristics" to save RAM.
4.  **Manual Recovery**: The system will stay in degraded mode until memory pressure normalizes (simulated).

---

## 🏁 Validation Checkpoint

The test is successful if:
- [ ] No fake/mock data was used (confirmed by checking your real GitHub repo).
- [ ] The full OODA loop completed from failure injection to autonomous merge.
- [ ] The Marketplace recovered without a manual server restart.
- [ ] The Vercel Dashboard remained synced via SSE the entire time.
