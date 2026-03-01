# 🛠️ SRE-Space: Operational Resolution Skills

This document defines the **Standard Engineering Procedures (SEP)** for the SRE agents when performing autonomous remediation across various infrastructure stacks.

---

## ☁️ Cloud & Infrastructure Adapters

SRE-Space utilizes a modular **Adapter Pattern** to interface with different cloud providers and orchestration layers. This ensures that a single **Brain Agent** can reason about a fault, while specialized **Infrastructure Adapters** execute the fix.

### 1. 📂 AWS (Elastic Beanstalk & EC2)
- **Role**: High-availability compute management.
- **Capabilities**:
    - **Resource Scaling**: Automated horizontal scaling via AWS CLI for Beanstalk environments.
    - **Health Retrieval**: Direct polling of AWS Health APIs to confirm resource saturation.
    - **Lifecycle Hooks**: Restarting application server instances during critical memory leaks.

### 2. 🎡 Kubernetes (K8s) Standard
- **Role**: Microservice orchestration and state management.
- **Capabilities**:
    - **Rolling Restarts**: Executing `kubectl rollout restart` for services with transient failure signatures.
    - **Resource Limits**: Hot-patching `requests` and `limits` in Deployment YAMLs when OOM (Out Of Memory) kills are detected.
    - **Pod Triage**: Automated deletion of stuck termination pods.

### 3. 🕸️ GCP (Google Computing Engine)
- **Role**: Global infrastructure and synthetic testing.
- **Capabilities**:
    - **Instance Reset**: Performing hard resets on GCE instances failing readiness checks.
    - **VPC Traffic**: Identifying network congestion and proposing routing rule updates.

---

## 🧩 Remediation Logic: The "Fixer" Skillset

When an anomaly is Orientated (via Brain), the **Fixer Agent** performs the following operational steps:

1. **Snapshot**: Capture the current infrastructure SHA or Instance State before action.
2. **Execute**: Call the relevant adapter (`AWS`, `K8s`, `GCP`) based on the service's `env` and `namespace`.
3. **Verify**: Perform a 60-second health audit after the fix.
4. **Rollback**: If metrics do not improve, automatically revert to the pre-fix snapshot. 

---

## 🏛️ Stack Governance

Every autonomous action is governed by the **Guardrail Agent**, which ensures:
- **No Direct main-branch pushes** (always via Remediation Branches).
- **No deletion of production datasets** (Read-only on DBs).
- **Cost Awareness**: Scaling up is limited to +100% capacity to avoid runaway billing.

---
**🌌 SRE-Space: Transforming Static Infrastructure into Active, Self-Healing Operations.**
