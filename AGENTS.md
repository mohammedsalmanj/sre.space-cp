# 🤖 SRE-Space: Cognitive Agent Roster v4.8

This document formalizes the **Standard Operating Procedure (SOP)** for the SRE-Space autonomous agent cluster. It defines the specialized roles within the OODA (Observe-Orient-Decide-Act) loop.

---

## ⚡ Agent Escalation Framework

SRE-Space utilizes a multi-tier agent hierarchy. In **Cloud Mode**, we run a streamlined core; in **Local Mode**, the full elite squad is activated.

| Agent | Tier | Responsibility | Deployment |
| :--- | :--- | :--- | :--- |
| **🕵️ Scout** | T1 | Anomaly Detection & Incident Initialization | All |
| **🧠 Brain** | T2 | Root Cause Analysis (RCA) & Trace Diagnosis | All |
| **🛠️ Fixer** | T2 | GitOps Patching & Deployment Triggering | All |
| **🛡️ Guardrail**| T2 | Policy Validation & Safety Verification | Local |
| **🏛️ CAG** | T2 | Cognitive Agent Guide (Architectural Integrity) | Local |
| **🤖 Jules** | T3 | Senior Architect / Structural Refactoring | Local |
| **🧑‍💻 Human** | T3 | Emergency Intervention & Final Approval | All |
| **📊 Curator** | T3 | Post-Mortem Archiving & Vector Memory | All |

---

## 🔍 Deep-Dive: Node Logic

### 1️⃣ Scout Agent (Observe)
- **Primary Input**: Kafka Business Events / Health API.
- **Goal**: Identify a threshold breach (e.g., Error Rate > 5%).
- **Action**: Opens a **GitHub Issue** representing the "War Room" and transitions the graph to Orientation.

### 2️⃣ Brain Agent (Orient)
- **Primary Input**: OpenTelemetry Spans (Jaeger Traces).
- **Behavior**: GPT-4o powered reasoning analyzes the stack trace. 
- **Context**: Queries **ChromaDB** to see if a similar incident has occurred before. 
- **Output**: Generates a detailed RCA in Markdown.

### 3️⃣ Guardrail Agent (Decide)
- **Policy Check**: Validates if the proposed remediation deviates from the system's security profile.
- **Flow Control**: Can return the loop to **Brain** for further refinement or grant **ALLOW** for execution.

### 4️⃣ Fixer Agent (Act)
- **Tooling**: GitHub API, Docker CLI.
- **Remediation**: Creates a feature branch, applies the patch, and opens a **Pull Request**.
- **Self-Healing**: In Cloud Mode, calls the **Render Deploy Hook** to restart the service with the new SHA.

### 5️⃣ Google Jules (Evolve)
- **Trigger**: Activated for complex, multi-file architectural issues.
- **Capability**: Jules refactors entire modules to prevent class-level regressions.

---

## 📚 Persistence Strategy

SRE-Space doesn't just fix bugs; it **learns** architecture.
1.  **Incident Cycle**: Detection -> Patch -> Verification.
2.  **Memory Hook**: Every cycle concludes with the **Curator Agent** indexing the Post-Mortem into ChromaDB.
3.  **Cross-Incident Reasoning**: Brain agents use this memory to provide "Institutional Knowledge" to new agent instances.

**The result: A system that becomes more resilient with every failure.** 🚀