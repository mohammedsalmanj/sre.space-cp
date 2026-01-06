# Use local image to bypass Docker Hub issues
FROM infra-memory:latest

WORKDIR /app

# Node.js and MCP are already in the base image
RUN pip install docker

COPY . .

CMD ["python", "main.py"]
