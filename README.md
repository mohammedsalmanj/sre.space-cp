# SRE.Space | Reliability Control Plane 🌌

**SRE-Space** is a production-grade autonomic reliability engine. It autonomously observes, diagnoses, and remediates infrastructure anomalies using an 8-agent cognitive OODA loop.

---

## 🏛️ The Problem-Solution Core

| The Problem | The SRE-Space Solution |
| :--- | :--- |
| **Operational Amnesia** | Contextual memory via **Pinecone Cloud** for sub-second retrieval of past RCAs. |
| **Alert-Action Gap** | Autonomous **diagnostic-to-remediation** loop crushing MTTR from hours to minutes. |
| **Tool Fragmentation** | Unified **OpenTelemetry** telemetry ingestion regardless of the underlying Cloud Provider. |
| **Production Risk** | Safety-first **GitOps PRs** and mandatory infrastructure snapshots before any "Fix." |

---

## 🎨 The "Liquid Glass" Visual System
The control plane features a premium **Liquid Glass** aesthetic designed for clarity and professional operations:
- **Light/Frosted Theme**: High backdrop-blur (16px) with soft white-to-light-blue mesh gradients.
- **Enterprise SaaS Feel**: Minimalist typography and high-resolution infrastructure icons for AWS, GCP, and Kubernetes.
- **Real-Time Reasoning**: Transparent AI thought-streams visualized directly in the sensory intake HUD.

---

## 🚀 Key Architectural Pillars

### 1. Observe (Scout Agent)
Scout continuously monitors **OpenTelemetry** traces and metrics. It filters millions of signals into high-fidelity "anomaly spans" to prevent alert fatigue.

### 2. Orient (Brain Agent)
The Brain performs **Root Cause Analysis (RCA)**. It cross-references current telemetry with historical pattern-matches in Pinecone memory or escalates to a reasoning cluster (LLM) for novel faults.

### 3. Decide (Guardrail Agent)
Decide validates the proposed remediation. If confidence is $>0.85$ and within safety parameters, it authorizes the Fixer. Otherwise, it escalates to a human engineer.

### 4. Act (Fixer & Curator)
The Fixer generates a **GitOps patch** (Pull Request) and applies hot-remediation after taking a safety snapshot. The Curator then indexes the solution back into long-term memory.

---

## 🎮 Deployment & Onboarding

### Vercel + Render Bridge
- **Frontend (Dashboard)**: Hosted on Vercel (`sre-space-cp.vercel.app`).
- **Backend (Control Plane)**: Hosted on Render (FastAPI + LangGraph).
- **Communication**: Seamless direct link via `VITE_API_BASE`.

### Local Simulation (Sandbox)
1. `git clone https://github.com/mohammedsalmanj/sre.space-cp`
2. `docker-compose up -d --build`
3. Open `http://localhost:5173` (Vite) or `http://localhost:8001` (FastAPI).

---

## 👤 Credits
**Engineering Lead:** Mohammed Salman  
*SRE · AIOps Engineer*  
"Reasoning for High-Scale Reliability."

---
*SRE-Space: Transforming Anomalies into Uptime.*
