# 🌌 SRE-Space: Autonomous Reliability Engine

SRE-Space is a **Full-Spectrum Autonomous SRE Control Plane** that transforms manual operations into a self-healing, closed-loop observability engine.

## 🚀 The Problem
Modern microservices generate "Operational Toil"—human engineers spending hours diagnosing OOM kills, service timeouts, and configuration drift. Manual RCA is slow, and post-mortems are often forgotten.

## 💡 The Solution
A 100% AI-driven lifecycle that protects your business metrics:
1.  **Scout (Detect)**: Monitors CUJs (Conversion Rate), Latency, Saturation, and Errors concurrently.
2.  **Brain (Diagnose)**: Performs "Deep Span Analysis" on Jaeger traces to find root causes.
3.  **Fixer (Heal)**: Executes GitOps PRs with Auto-Merge to apply infrastructure and config changes.
4.  **Memory (Learn)**: Generates automated Post-Mortems and indexes them in ChromaDB for future pattern matching.

---

## 🛠️ Access Points (The Control Center)

| Component | URL | Purpose |
| :--- | :--- | :--- |
| **SRE Dashboard** | [http://localhost:3001](http://localhost:3001) | Real-time SRE metrics & Audit Log |
| **Jaeger Trace UI** | [http://localhost:16686](http://localhost:16686) | Deep Span analysis & Distributed Tracing |
| **GitHub Repo** | `mohammedsalmanj/sre.space-cp` | GitOps Audit Trail & Automated PRs |
| **Knowledge Base** | `ChromaDB :8000` | Incident memory & Vector embeddings |

---

## 🚦 How to Use

### 1. Start the Engine
```bash
# Clone the repo and start the stack
docker-compose up -d --build
```

### 2. Trigger "Chaos" (Test the AI)
Run the chaos suite to simulate a production failure:
```bash
# Simulate a Memory Leak (OOM)
python trigger_chaos.py oom

# Simulate a Business Logic Failure (Conversion Drop)
python trigger_chaos.py conversion
```

### 3. Watch the Magic
- **Scout** will create a GitHub Issue in seconds.
- **Brain** will comment with a "Deep Span" diagnosis.
- **Fixer** will create a PR, merge it, and trigger a deployment.
- **Memory** will close the issue with a professional AI-generated Post-Mortem.

---

## 🧬 Architecture
- **Tech**: FastAPI, Kafka, OpenTelemetry, Jaeger, ChromaDB, GitHub MCP.
- **Brain**: GPT-4o-Mini via OpenAI.
- **Remediation**: GitOps-driven via GitHub Pull Requests.

**"Built to reach 99.9% reliability without an on-call rotation."**
