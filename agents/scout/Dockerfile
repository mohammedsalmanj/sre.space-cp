FROM python:3.10-slim

WORKDIR /app

RUN pip install mcp openai requests opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

COPY . .

CMD ["python", "main.py"]
