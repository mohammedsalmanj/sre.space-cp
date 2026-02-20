import os

# --- Runtime Configuration Layer ---
# This module centralizes all environment-based settings for SRE-Space.
# It supports two modes: 'local' (performance) and 'cloud' (optimization for Render).

# ENVIRONMENT MODE
ENV = os.getenv("ENV", "local")  # 'local' or 'cloud'

# EVENT BUS BACKEND
# LOCAL: Kafka (High throughput)
# CLOUD: Redis (Free tier compatible)
EVENT_BUS = os.getenv("EVENT_BUS", "kafka" if ENV == "local" else "redis")

# RESOURCE MANAGEMENT
MAX_LLM_CONCURRENCY = int(os.getenv("MAX_LLM_CONCURRENCY", 5 if ENV == "local" else 1))
AGENT_LOOP_INTERVAL = int(os.getenv("AGENT_LOOP_INTERVAL", 5 if ENV == "local" else 15))

# OBSERVABILITY
TRACE_SAMPLING_RATE = float(os.getenv("TRACE_SAMPLING_RATE", 1.0 if ENV == "local" else 0.1))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") # Production hardening requires INFO visibility

# MEMORY GUARD (Critical for 512MB environments)
MEMORY_THRESHOLD_MB = int(os.getenv("MEMORY_THRESHOLD_MB", 400)) # Aggressive for 512MB RAM
DEGRADED_MODE = False

def update_degraded_mode(is_degraded: bool):
    global DEGRADED_MODE, MAX_LLM_CONCURRENCY, AGENT_LOOP_INTERVAL, TRACE_SAMPLING_RATE
    DEGRADED_MODE = is_degraded
    if is_degraded:
        MAX_LLM_CONCURRENCY = 1
        AGENT_LOOP_INTERVAL = 30
        TRACE_SAMPLING_RATE = 0.05
    else:
        MAX_LLM_CONCURRENCY = int(os.getenv("MAX_LLM_CONCURRENCY", 5 if ENV == "local" else 1))
        AGENT_LOOP_INTERVAL = int(os.getenv("AGENT_LOOP_INTERVAL", 5 if ENV == "local" else 15))
        TRACE_SAMPLING_RATE = float(os.getenv("TRACE_SAMPLING_RATE", 1.0 if ENV == "local" else 0.1))
