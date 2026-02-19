FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from root
COPY . .

# Set PYTHONPATH to include the root for packages
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8001

# Default command
CMD ["python", "apps/control-plane/main.py"]
