"""
File: apps/control_plane/config.py
Layer: Application / Configuration
Purpose: Centralized environment-aware configuration for the SRE-Space control plane.
Problem Solved: Manages resource constraints (RAM limits), feature flags (active agents), and connectivity strings (Redis/Kafka) across multi-cloud and local environments.
Interaction: Imported by main.py and langgraph_logic.py to drive runtime behavior.
Dependencies: os, python-dotenv
Inputs: Environment variables (.env)
Outputs: Global configuration constants
"""
import os
from dotenv import load_dotenv

# Initialize basic environment discovery
load_dotenv()

# --- Operational Mode ---
# Drives the behavior of the entire infrastructure stack (Observability & Remediation).
ENV = os.getenv("ENV", "local")  # Possible Values: 'cloud', 'local'

# --- Resource Orchestration & Constraints ---
# We adjust the "brain power" and RAM limits based on the runtime environment's footprint.
if ENV == "cloud":
    # Optimized for Cloud Hosting (e.g. Render / Heroku / Lambda)
    EVENT_BUS = "redis"                                      
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    MAX_LLM_CONCURRENCY = 2                                  
    MEMORY_LIMIT_MB = 450                                    # Proactive threshold for process protection
    # Lean AI squad optimized for low-resource stability
    ACTIVE_AGENTS = ["scout", "brain", "fixer", "human", "curator"]
else:
    # 'Power-User' mode for local Docker/Kubernetes development
    EVENT_BUS = os.getenv("EVENT_BUS", "kafka")               
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    MAX_LLM_CONCURRENCY = 5                                  
    MEMORY_LIMIT_MB = 2048                                   # Full local orchestration headroom
    # The full 8-agent cognitive squad for comprehensive Reliability Engineering
    ACTIVE_AGENTS = ["scout", "cag", "brain", "guardrail", "fixer", "jules", "curator", "human"]

# --- Automated Governance & Deployment Hooks ---
# Hook URL for triggering CI/CD pipelines (e.g. Render/GitHub Actions) after a GitOps patch.
RENDER_DEPLOY_HOOK = os.getenv("RENDER_DEPLOY_HOOK", "")
