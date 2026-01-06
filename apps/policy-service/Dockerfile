FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc librdkafka-dev && rm -rf /var/lib/apt/lists/*

RUN pip install --default-timeout 100 fastapi uvicorn confluent-kafka opentelemetry-api opentelemetry-sdk \
    opentelemetry-instrumentation-fastapi opentelemetry-exporter-otlp

COPY . .

ENV OTEL_SERVICE_NAME=policy-service
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317

EXPOSE 8002

CMD ["python", "main.py"]
