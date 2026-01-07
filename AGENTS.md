SRE-Space: Operational Intelligence Roster

This document defines the Standard Operating Procedure (SOP) for the SRE-Space autonomous agent cluster.
It formalizes how operational intelligence flows through the system, including agent responsibilities, telemetry boundaries, and escalation paths required to maintain reliability at scale.

SRE-Space is designed to behave like a mature SRE organization, not a collection of scripts.

⚡ Interaction Flow: From Signal to Architecture

SRE-Space follows a deliberate, staged progression from runtime signal to long-term system improvement.

Detection
Scout identifies abnormal system behavior (e.g., sustained latency increase in the Policy Service).

Analysis
Brain performs trace-driven RCA and isolates the dominant contributor (e.g., inefficient database query).

Remediation
Fixer applies a bounded mitigation (e.g., connection pool restart or configuration adjustment).

Escalation
If the behavior persists or indicates structural risk, the jules-fix label is applied, triggering architectural refactoring.

This flow ensures speed first, safety always, and architecture only when justified.

🟢 Runtime Operations Cluster (Tier 1 & Tier 2)

These agents form the continuous operations layer.
They handle the majority of reliability work without human intervention.

Agent	Core Specialization	Operational Logic	Key Tooling
Scout	Watchdog	Real-time interpretation of business SLIs and service health	Kafka, OTel Metrics
Brain	Principal Analyst	Root Cause Analysis via telemetry correlation	Jaeger, ChromaDB
Fixer	Ops Executor	Controlled remediation and GitOps state management	GitHub MCP, Docker
1️⃣ Scout Agent — The Observer

Focus: Service Health & Conversion Yield

Scout continuously evaluates:

Kafka event streams for business SLIs (e.g., quotes vs purchases)

latency trends and saturation signals

service availability and restart patterns

When Critical User Journeys (CUJ) degrade beyond tolerance, Scout automatically opens a GitHub Issue containing telemetry context and timestamps.

Scout does not diagnose or fix.
Its responsibility is to validate that something meaningful has changed.

2️⃣ Brain Agent — The Strategist

Focus: Intelligent Diagnostics & Decision Making

Brain consumes the context surfaced by Scout and performs:

Deep Span Analysis to identify the dominant execution bottleneck

correlation of traces, metrics, and historical behavior

classification of the issue as transient, systemic, or architectural

Brain does not execute changes directly.
Instead, it produces explicit remediation intent, guiding downstream action.

3️⃣ Fixer Agent — The Mechanic

Focus: Self-Healing Execution & Change Control

Fixer applies Brain’s decisions using bounded and auditable actions:

runtime mitigations for short-lived conditions

GitOps pull requests for persistent configuration or infrastructure changes

Fixer maintains strict hygiene:

controlled branch lifecycle

squash merges

rollback-ready history

No permanent change bypasses version control.

🔴 Architectural Evolution Layer (Tier 3)

Not all problems should be solved through automation.

SRE-Space includes an explicit architectural escalation tier for issues that indicate deeper systemic risk.

4️⃣ Google Jules — Senior SRE Architect (Asynchronous)

Jules represents Tier-3 escalation, responsible for deep, multi-file refactoring that goes beyond configuration tuning.

Activation

Explicit jules-fix label

Scheduled maintenance window (default: 05:00)

Primary Objective

Improve long-term stability and resilience through:

circuit breakers

retry and backoff strategies

caching and query optimization

architectural simplification

Jules operates asynchronously and intentionally — mirroring how real SRE teams escalate from operations to architecture.

🛡️ Critical Guardrails for Jules

To preserve observability integrity and operational continuity, Jules operates under strict constraints:

OpenTelemetry Integrity
otel_setup.py must not be removed or bypassed.
All new logic must remain fully instrumented.

Event Contract Stability
Kafka headers and event semantics must remain backward-compatible.

Verification Discipline
Every PR must include:

a summary of architectural changes

expected impact on Mean Time to Recovery (MTTR)

Automation may evolve — visibility must not regress.

📊 Shared Knowledge Base (Memory)

All agents read from and contribute to a central ChromaDB vector store.

This ensures:

architectural changes made by Jules are immediately visible to Brain

repeated RCA loops are avoided

operational knowledge compounds over time

Example:

A refactor performed at 05:00 is part of Brain’s reasoning context by 09:00.

Memory is the mechanism that turns operations into learning, not just recovery.

🧠 Why This Model Is Effective

This structure enforces:

fast response without reckless automation

clear separation of responsibility

explicit escalation for complex problems

long-term system improvement

SRE-Space does not attempt to “self-heal everything.”
It automates what should be automated and escalates what should be designed.