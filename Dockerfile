# --- Stage 1: Build ---
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies for psutil and confluent-kafka
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Stage 2: Final ---
FROM python:3.11-slim

WORKDIR /app

# Install runtime libraries for confluent-kafka
RUN apt-get update && apt-get install -y --no-install-recommends \
    librdkafka1 \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Environment setup
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose control plane port (defaulting to 10000 for Render)
EXPOSE 10000

# Render requirement: Dynamic port binding via shell form
CMD ["sh", "-c", "uvicorn apps.control_plane.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
