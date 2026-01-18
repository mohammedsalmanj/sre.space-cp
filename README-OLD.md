# SRE-Space Control Plane - Last Known Good Configuration (LKGC)

**Verification Date**: 2026-01-18
**Status**: ✅ GO for Phase 2 Migration
**Verifier**: Anti-Gravity (Senior SRE Safeguard)

## 1. Service Mesh Status
| Service | Status | Port | Version |
| :--- | :--- | :--- | :--- |
| **Kafka** | 🟢 Up | 9092 | `apache/kafka:latest` |
| **Jaeger** | 🟢 Up | 16686 (UI) | `jaegertracing/all-in-one:latest` |
| **OTel Collector** | 🟢 Up | 4317/4318 | `otel/opentelemetry-collector-contrib` |
| **ChromaDB** | 🟢 Up | 8000 | `chromadb/chroma:latest` |
| **Mock API** | 🟢 Up | 8080 | Custom (Node.js) |
| **Frontend** | 🟢 Up | 3001 | Nginx/Static |
| **Quote Service** | 🟢 Up | 8001 | Python/FastAPI |
| **Policy Service** | 🟢 Up | 8002 | Python/FastAPI |
| **User Service** | 🟢 Up | 8003 | Python/FastAPI |

## 2. Agent Ecosystem
| Agent | Role | Status | Model |
| :--- | :--- | :--- | :--- |
| **Scout** | Anomaly Detection | 🟢 Active | Logic-based (Kafka/HTTP) |
| **Brain** | RCA & Diagnosis | 🟢 Active | `gpt-4o-mini` |
| **Fixer** | Remediation (GitOps) | 🟢 Active | Logic-based (Docker/GitHub) |
| **Memory** | Long-term Patterns | 🟢 Active | ChromaDB Vector Store |

## 3. Environment Configuration
### Critical Environment Variables
- `GITHUB_PERSONAL_ACCESS_TOKEN`: Required for Agent GitOps.
- `NEW_RELIC_LICENSE_KEY`: Configured for OTel export.
- `OPENAI_API_KEY`: Required for Brain Agent reasoning.
- `KAFKA_BOOTSTRAP_SERVERS`: `kafka:9092`

### Network Topology
- **Docker Network**: `sre-cp_default`
- **DNS**: Containers use Google DNS (`8.8.8.8`) for external connectivity.

## 4. Verification Log
- **Service Integrity**: All 5 core services verified via `docker compose ps`.
- **Telemetry**: Trace data confirmed flowing to `http://localhost:16686`.
- **Agent Loop**:
    1.  `trigger_chaos.py` successfully injected 500-errors/conversion drop.
    2.  **Scout** detected the anomaly and raised a GitHub Issue.
    3.  **Brain** analyzed the issue using `gpt-4o-mini` and posted a diagnosis.
    4.  **Fixer** recognized the mitigation strategy and executed cleanup/remediation.

## 5. Migration Notes
- Ensure `docker-compose.yml` does not contain JSON metadata wrappers (fixed during verification).
- Agents require `curl` in their Docker image for health checks and MCP connectivity (patched).
