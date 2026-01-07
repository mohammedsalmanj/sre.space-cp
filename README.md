# 🌌 SRE-Space: The Autonomous Reliability Engine (Deep Dive)

SRE-Space is a cutting-edge AIOps platform that replaces traditional on-call rotations with a team of specialized AI agents. Unlike standard monitoring, SRE-Space is **agentic**: it doesn't just alert; it investigates, codes, merges, and learns.

---

## 🏗️ System Architecture

### 1. The Protected Microservices (The Application)
The "Cloud Insurance" app consists of three interconnected services and a frontend:
- **Quote Service (`apps/quote-service`)**: The entry point. It receives quote requests, communicates with downstream services, and emits events to Kafka (e.g., `quote_requested`, `quote_purchased`).
- **Policy Service (`apps/policy-service`)**: Handles policy generation and risk assessment.
- **User Service (`apps/user-service`)**: Manages customer profiles.
- **Frontend (`apps/frontend`)**: A glassmorphic SRE dashboard providing real-time visibility into "Conversion Rate" (Purchases vs. Quotes).

### 2. The SRE Agent Team (The Intelligence)
Four collaborative agents work in a closed-loop to maintain a **99.9% CUJ (Critical User Journey) success rate**:

#### 🔍 Scout Agent (The Observer)
- **Role**: Continuous Monitoring & Incident Creation.
- **Capabilities**: 
    - **Watchers**: Runs concurrent threads for **CUJ Monitoring** (Kafka consumption), **Latency tracking**, **Saturation/Infrastructure checks**, and **API Error detection**.
    - **Incident Orchestrator**: When a threshold is breached (e.g., Conversion < 50%), it gathers system snapshots and opens a **GitHub Issue** as the central source of truth.

#### 🧠 Brain Agent (The Analyst)
- **Role**: Deep Span Analysis & Remediation Strategy.
- **Capabilities**:
    - **Trace Analysis**: Utilizes OpenTelemetry traces from **Jaeger** to identify the exact service or database query causing bottlenecks.
    - **Heuristic Reasoning**: Connects "Symptom" (Conversion Drop) to "Root Cause" (e.g., Policy Service OOM).
    - **Orchestration**: Directs the Fixer Agent by commenting `MITIGATION: PR` or `MITIGATION: RESTART` on the GitHub issue.

#### 🛠️ Fixer Agent (The Engineer)
- **Role**: GitOps & Automated Remediation.
- **Capabilities**:
    - **Auto-Healing**: Executes `docker-restart` for transient crashes or memory leaks.
    - **GitOps Lifecycle**: For configuration or infrastructure changes, it creates a new branch, commits the fix, raises a **Pull Request**, and executes an **Auto-Merge (Squash)**.
    - **Hygiene**: Maintains a "Top 5" branch policy, deleting legacy remediation branches after successful deployment.

#### 📚 Memory Agent (The Librarian)
- **Role**: Knowledge Loop & Pattern Matching.
- **Capabilities**:
    - **ChromaDB Integration**: Stores every incident and Post-Mortem as vector embeddings.
    - **Context Injection**: Provides the Brain Agent with "Historical Context" if a similar incident has occurred before, accelerating resolution time.

---

## 🚦 Infrastructure Components

| Tech | Role in Project | URL |
| :--- | :--- | :--- |
| **Kafka** | Event bus for business metrics (Quotes/Purchases). | `localhost:9092` |
| **Jaeger** | Distributed tracing backend for bottleneck identification. | `localhost:16686` |
| **ChromaDB** | Vector database for long-term incident memory. | `localhost:8000` |
| **GitHub MCP** | The "Hands" of the agents to create issues, PRs, and comments. | GitHub Repository |
| **Otel-Collector** | Central pipe for telemetry from all microservices. | `localhost:4317` |

---

## 🔄 The Autonomous Recovery Lifecycle

1.  **Detection**: `trigger_chaos.py` kills the Policy Service. **Scout** detects the health check failure.
2.  **Alerting**: Scout opens a GitHub Issue: `[INCIDENT] Infrastructure Alert`.
3.  **Diagnosis**: **Brain** performs Deep Span Analysis, identifies the dead service, and comments `MITIGATION: RESTART policy-service`.
4.  **Action**: **Fixer** reads the command, restarts the container, and labels the issue `Status: Fixed`.
5.  **Audit/Learning**: **Brain** detects recovery, generates a Markdown **Post-Mortem**, and **Memory** indexes it into the Knowledge Base.
6.  **Deployment**: Any PR created by Fixer triggers the `.github/workflows/deploy-infra.yml` for automated rollout.

---

## 🧪 Chaos Testing Suite
Test the AI's resilience using the `trigger_chaos.py` script:
- `oom`: Simulates a memory leak/saturation high-pressure event.
- `conversion`: Simulates a business logic failure where quotes happen but purchases stop.
- `latency`: Simulates slow network responses in downstream services.

---

## 🛠️ Developer Setup

### Environment Variables (.env)
```bash
GITHUB_PERSONAL_ACCESS_TOKEN=your_pat
OPENAI_API_KEY=your_key
REPO_OWNER=mohammedsalmanj
REPO_NAME=sre.space-cp
```

### Installation
```bash
# 1. Start all infra and agents
docker compose up -d --build

# 2. Monitor Agent Logs
docker logs -f sre-cp-scout-1
docker logs -f sre-cp-brain-1
docker logs -f sre-cp-fixer-1
```

**SRE-Space is a prototype for the future of "No-Ops" - where the infrastructure manages itself through a decentralized team of AI professionals.**
