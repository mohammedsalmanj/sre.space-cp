# 🤖 SRE-Space: Cognitive Agent Roster v4.8

This document formalizes the **Standard Operating Procedure (SOP)** for the SRE-Space autonomous agent cluster. It defines the specialized roles within the OODA (Observe-Orient-Decide-Act) loop.

---

## ⚡ Agent Escalation Framework

SRE-Space utilizes a multi-tier agent hierarchy. In **Cloud Mode**, we run a streamlined core; in **Local Mode**, the full elite squad is activated.

| Agent | Tier | Responsibility | Deployment |
| :--- | :--- | :--- | :--- |
| **🕵️ Scout** | T1 | Anomaly Detection & Infrastructure Polling | All |
| **🧠 Brain** | T2 | Root Cause Analysis (RCA) & Adapter Command Generation | All |
| **🛠️ Fixer** | T2 | GitOps Patching & Cloud/K8s Remediation | All |
| **🛡️ Guardrail**| T2 | Policy Validation & Multi-Cloud Safety Verification | Local |
| **🏛️ CAG** | T2 | Cognitive Agent Guide (Architectural Integrity) | Local |
| **🤖 Jules** | T3 | Senior Architect / Structural Refactoring | Local |
| **🧑‍💻 Human** | T3 | Emergency Intervention & Final Approval | All |
| **📊 Curator** | T3 | Post-Mortem Archiving & Vector Memory Indexing | All |

---

## 🛠️ Infrastructure Adaptation Capabilities

SRE-Space agents are now equipped with **Operational Skills** to resolve incidents across diverse stacks:

### 🏙️ AWS Cloud Ops
- **EC2 Management**: Automated instance health checks and reset triggers.
- **Elastic Beanstalk**: Dynamic scaling and environment configuration hot-patching.

### 🎡 Kubernetes (K8s) Standard
- **Pod Remediation**: Automated restart and eviction based on crash-loop patterns.
- **Resource Patching**: Real-time updates to CPU/Memory limits to mitigate OOM errors.

### 🕸️ GCP (Google Cloud)
- **GCE Recovery**: Hard-reset and Snapshot-based recovery for GCE instances.
- **VPC Diagnostics**: Network route verification and latency reduction commands.

---

## 🔍 Deep-Dive: Node Logic (Enhanced)
...

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