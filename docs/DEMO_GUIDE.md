# 🚀 SRE-Space: Interactive Demo Guide

Welcome to the **SRE-Space Control Plane**. This guide will walk you through the 8-agent OODA loop and help you onboard your first infrastructure stack.

---

## 🛠️ Quickstart Checklist

1.  **Link Cloud Infrastructure**: Select your stack (AWS, GCP, or K8s) in the onboarding modal and provide the required credentials.
2.  **Link Pinecone**: Ensure your `PINECONE_API_KEY` is active to enable the RAG-based Brain memory.
3.  **Trigger Chaos**: Use the "Chaos Lab" in the dashboard to inject a synthetic fault and watch the agents take action.

---

## 🧠 The 8-Agent OODA Loop: Under the Hood

When an incident occurs, SRE-Space transitions through four cognitive phases:

### 1. OBSERVE (Scout)
*   **What happens?** The **Scout Agent** polls your infrastructure via the Universal Adapter. It filters millions of OpenTelemetry spans into a high-fidelity health snapshot.
*   **Key Signal:** Any status marked `CRITICAL` or `DEGRADED` triggers the next phase.

### 2. ORIENT (Brain & CAG)
*   **What happens?** The **CAG (Cache Agent)** checks for recent duplicate signatures. If unique, the **Brain Agent** performs deep RCA.
*   **Memory Retrieval:** The Brain queries **Pinecone Cloud Memory** to see how similar incidents were resolved in the past.

### 3. DECIDE (Guardrail)
*   **What happens?** The **Guardrail Agent** analyzes the Brain's proposal. It calculates the **Blast Radius** and checks the **Confidence Score**. 
*   **Human-in-the-Loop:** If confidence is $<0.85$, the loop pauses for a human engineer to approve.

### 4. ACT (Fixer, Jules & Curator)
*   **What happens?** 
    *   **Fixer** takes a safety snapshot and opens a **Pull Request**.
    *   **Jules** performs a final architectural review.
    *   **Curator** closes the issue and saves the new solution back to Pinecone.

---

## 🎮 Demo Mode vs. Real Mode

*   **Real Mode**: Connects directly to your cloud providers and real OTel collectors.
*   **Demo Mode**: Uses the **Chaos Simulator** to feed pre-recorded "Gold Standard" telemetry. This allows you to see the "Perfect Remediation Loop" instantly without any cloud costs or latency.

---

## 🧪 Testing Your Configuration

To verify your setup is working:
1.  Open the **Chaos Lab** in the dashboard.
2.  Select **"AWS_EC2_DISK_FULL"**.
3.  Watch the **Sensory Intake** HUD.
4.  Look for the **"Memory Hit"** icon (🧠) in the Brain's logs—this confirms Pinecone connectivity.

---

**SRE-Space: Transforming Anomalies into Uptime.** 🌌
