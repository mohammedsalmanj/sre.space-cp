FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc librdkafka-dev && rm -rf /var/lib/apt/lists/*

RUN pip install fastapi uvicorn confluent-kafka opentelemetry-api opentelemetry-sdk \
    opentelemetry-instrumentation-fastapi opentelemetry-exporter-otlp requests

COPY . .

# OTel Defaults
ENV OTEL_SERVICE_NAME=quote-service
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317

EXPOSE 8001

CMD ["python", "main.py"]
