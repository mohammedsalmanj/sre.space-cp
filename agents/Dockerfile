FROM python:3.10-slim

WORKDIR /app

# Install System Deps
RUN apt-get update && apt-get install -y \
    nodejs npm gcc librdkafka-dev curl \
    && npm install -g @modelcontextprotocol/server-github \
    && rm -rf /var/lib/apt/lists/*

# Install Python Deps
RUN pip install --no-cache-dir --default-timeout 1000 \
    mcp confluent-kafka requests openai chromadb docker pydantic langgraph opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

# Select which agent to run at runtime via CMD
# Or we can inherit this.
COPY shared /app/shared
# Copies all agents; logic is separated by runtime command
COPY agents /app/agents

# Environment needs to know where shared library is
ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["python", "agents/scout.py"]
