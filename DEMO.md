# 🚀 SRE-Space: End-to-End Master Portal Guide

This document defines the validation sequence for the **Unified SRE-Space Master Portal**. Gone are the multiple URLs—everything you need is on the root index page.

## 📋 Prerequisites
1.  **Environment**: `OPENAI_API_KEY` and `GITHUB_PERSONAL_ACCESS_TOKEN` must be set in `.env`.
2.  **App Launch**: Run `python apps/control_plane/main.py` and visit `http://localhost:8001`.

---

## 🧪 Phase 1: The "Nominal" Flow
1.  **Generate Quote**: Fill the form in the **"Policy Underwriting"** section and click **"Generate Coverage Flow"**.
2.  **Verify Success**: The "Quote Reference" should appear in a dark slate card. System Integrity should remain **Blue (Nominal)**.

---

## 💥 Phase 2: The "Chaos" Breach
1.  **Trigger Fault**: In the **"Fault Injection Console"** (bottom left), click **"Trigger 500"**.
2.  **Observe Uplink**: 
    *   The **System Integrity** dot will turn **Orange (Breach)**.
    *   The **SRE Intelligence Stream** (Terminal) will wake up and show `[SCOUT] [OBSERVE] 🛰️ Uplink signal matching active injection profile`.
3.  **Confirm Failure**: Try to generate a quote again. It will return a red "Infrastructure Breach" alert.

---

## 🧠 Phase 3: Autonomous Remediation (The Loop)
1.  **Watch the OODA Pulse**:
    *   Top-right bars (Observe → Orient → Decide → Act) will light up in sequence.
2.  **Read the Thoughts**:
    *   `[BRAIN]` will analyze the signature.
    *   `[GUARDRAIL]` will evaluate policy (Look for `POLICY_BYPASS: Execution permitted`).
    *   `[FIXER]` will create a **Real GitHub Branch and PR**.
3.  **Check GitOps**:
    *   The **"Real-Time GitOps"** feed (far right) will update to show a new PR titled `[AUTONOMOUS-FIX]`.

---

## ✅ Phase 4: Self-Healing Verification
1.  **Wait for Merge**: The terminal will show `SUCCESS: Remediated state merged`.
2.  **System Recovery**: The Integrity dot will turn back to **Blue**.
3.  **Final Test**: Click **"Generate Coverage Flow"** once more.
    *   **EXPECTED**: The quote flow works perfectly again.

---

## 🏁 Validation Complete
The test is successful if:
- [ ] You saw the agents work in the same window (No tab switching).
- [ ] A real GitHub PR was created and merged autonomously.
- [ ] The app self-healed the 500 fault without a manual restart.
