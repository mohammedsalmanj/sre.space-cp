import os
from dotenv import load_dotenv

load_dotenv()

# Block 1: Environment-Aware Logic
ENV = os.getenv("ENV", "local")  # cloud or local

# Infrastructure Defaults
if ENV == "cloud":
    EVENT_BUS = "redis"
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
else:
    EVENT_BUS = os.getenv("EVENT_BUS", "kafka")
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Vector Database (Embedded for both in this refactor to simplify)
CHROMA_DB_HOST = os.getenv("CHROMA_DB_HOST", "localhost")
CHROMA_DB_PORT = int(os.getenv("CHROMA_DB_PORT", 8000))

# Agent Constraints
MAX_LLM_CONCURRENCY = 5 if ENV == "local" else 2
MEMORY_LIMIT_MB = 2048 if ENV == "local" else 450
