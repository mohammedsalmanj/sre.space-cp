FROM infra-memory:latest

WORKDIR /app

RUN pip install fastapi uvicorn opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-exporter-otlp

COPY . .

# Environment variables for OTel
ENV OTEL_SERVICE_NAME=policy-service
ENV OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317

EXPOSE 8001

CMD ["python", "main.py"]
