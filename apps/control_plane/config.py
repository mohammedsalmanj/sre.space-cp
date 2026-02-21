import os
from dotenv import load_dotenv

load_dotenv()

# Block 1: Environment-Aware Logic
ENV = os.getenv("ENV", "local")  # cloud or local

# Agent Constraints
if ENV == "cloud":
    EVENT_BUS = "redis"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    MAX_LLM_CONCURRENCY = 2
    MEMORY_LIMIT_MB = 450
    # Block 2: Cloud-Optimized Core Agents
    ACTIVE_AGENTS = ["scout", "brain", "fixer", "human", "curator"]
else:
    EVENT_BUS = os.getenv("EVENT_BUS", "kafka")
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    MAX_LLM_CONCURRENCY = 5
    MEMORY_LIMIT_MB = 2048
    ACTIVE_AGENTS = ["scout", "cag", "brain", "guardrail", "fixer", "jules", "curator", "human"]

# Deployment Integrity
RENDER_DEPLOY_HOOK = os.getenv("RENDER_DEPLOY_HOOK", "")
