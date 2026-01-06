FROM python:3.10-slim

WORKDIR /app

# Install System Deps
RUN apt-get update && apt-get install -y \
    nodejs npm gcc librdkafka-dev \
    && npm install -g @modelcontextprotocol/server-github \
    && rm -rf /var/lib/apt/lists/*

# Install Python Deps
# Added sentence-transformers for local RAG
RUN pip install --default-timeout 100 \
    mcp confluent-kafka requests openai chromadb sentence-transformers

# Select which agent to run at runtime via CMD
# Or we can inherit this.
COPY shared /app/shared
# Copies all agents; logic is separated by runtime command
COPY agents_new /app/agents_new

# Environment needs to know where shared library is
ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["python", "agents_new/scout.py"]
