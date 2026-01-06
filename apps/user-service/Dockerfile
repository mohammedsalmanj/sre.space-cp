FROM python:3.10-slim

WORKDIR /app

RUN pip install fastapi uvicorn opentelemetry-api opentelemetry-sdk \
    opentelemetry-instrumentation-fastapi opentelemetry-exporter-otlp requests

COPY . .

ENV OTEL_SERVICE_NAME=user-service
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317

EXPOSE 8003

CMD ["python", "main.py"]
