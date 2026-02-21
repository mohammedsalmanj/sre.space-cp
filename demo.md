# 📡 SRE-Space: Demonstration Guide

This guide walks you through the autonomous recovery cycle, from local orchestration to cloud-scale remediation.

---

## 🏗️ Step 1: Local Setup (The 'Unleashed' Experience)

To experience the full 8-agent squad with deep architectural reasoning, we recommend running SRE-Space locally using our optimized cluster.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/mohammedsalmanj/sre.space-cp.git
    cd sre.space-cp
    ```

2.  **Spin up the Cluster**:
    ```bash
    docker-compose up -d
    ```

3.  **Access the HUD**:
    Open `http://localhost:8001` to view the local Control Loop.

---

## 🔥 Step 2: Chaos Injection

SRE-Space is a reactive engine. Let's force it to act.

1.  **Navigate to the Chaos Lab**:
    In the Dashboard, click on the **🧪 Chaos Lab** tab.

2.  **Inject a Failure**:
    Click on **INJECT: DB POOL EXHAUSTION**. 

3.  **Watch the OODA Loop**:
    Switch back to the **📊 Dashboard**. You will see:
    - **[SCOUT]** Detecting the fault.
    - **[BRAIN]** Analyzing context and drafting a fix.
    - **[FIXER]** Executing the patch.

---

## 🛡️ Step 3: The Proof

Observe the logs and verify the remediation PR on GitHub to confirm the autonomous action.

---
**Build for Resilience. Verified by Veracity.** 🚀
