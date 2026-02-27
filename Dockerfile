# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Container hardening: Non-root user and curl for healthcheck
RUN groupadd -r sre && useradd -r -g sre sreuser && \
    apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder --chown=sreuser:sre /root/.local /home/sreuser/.local
COPY --chown=sreuser:sre . .

# Environment setup
ENV PATH=/home/sreuser/.local/bin:$PATH
ENV PYTHONPATH=/app

# Proper logging
ENV PYTHONUNBUFFERED=1

# Memory optimizations/limits
ENV MALLOC_ARENA_MAX=2
ENV PYTHONMALLOC=malloc
ENV WORKERS=1

# Change to non-root user
USER sreuser

EXPOSE 10000

# Container Hardening: Healthcheck endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://0.0.0.0:${PORT:-10000}/system/health || exit 1

# Start uvicorn
CMD ["sh", "-c", "uvicorn apps.control_plane.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers ${WORKERS:-1}"]
