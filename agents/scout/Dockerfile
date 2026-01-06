FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y nodejs npm gcc librdkafka-dev && \
    npm install -g @modelcontextprotocol/server-github && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --default-timeout 100 mcp confluent-kafka requests

COPY . .

CMD ["python", "main.py"]
