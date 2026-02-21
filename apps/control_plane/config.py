import os
from dotenv import load_dotenv

load_dotenv()

# --- Environment Configuration ---
# Detect if the application is running in the cloud (Render) or locally (Docker Desktop).
# This single variable drives the behavior of the entire infrastructure stack.
ENV = os.getenv("ENV", "local")  # Values: 'cloud' or 'local'

# --- Agent & Resource Constraints ---
# We adjust the "brain power" and memory limits based on the hosting environment's capabilities.
if ENV == "cloud":
    # Optimized for Render's Free/Individual Tier (512MB RAM limit)
    EVENT_BUS = "redis"                                      # Use Managed Redis for low-latency messaging
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    MAX_LLM_CONCURRENCY = 2                                  # Fewer parallel threads to preserve memory
    MEMORY_LIMIT_MB = 450                                    # Threshold for the Memory Guard middleware
    # Use a lean agent squad to ensure stability on cloud resources
    ACTIVE_AGENTS = ["scout", "brain", "fixer", "human", "curator"]
else:
    # "Unleashed" mode for local development (no strict RAM limits)
    EVENT_BUS = os.getenv("EVENT_BUS", "kafka")               # Use full Apache Kafka for enterprise event logic
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    MAX_LLM_CONCURRENCY = 5                                  # Enable high-parallel agent reasoning
    MEMORY_LIMIT_MB = 2048                                   # 2GB limit for heavy local orchestration
    # Full 8-agent squad for deep architectural analysis and auto-remediation
    ACTIVE_AGENTS = ["scout", "cag", "brain", "guardrail", "fixer", "jules", "curator", "human"]

# --- Deployment & CI/CD Hooks ---
# RENDER_DEPLOY_HOOK: A unique URL provided by Render that, when POSTed to, triggers a fresh deployment.
# This allows the Fixer agent to "ship" code changes immediately after creating a PR.
RENDER_DEPLOY_HOOK = os.getenv("RENDER_DEPLOY_HOOK", "")
