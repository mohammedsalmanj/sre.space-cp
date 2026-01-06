# Use local image to bypass Docker Hub issues
FROM infra-brain:latest

WORKDIR /app

# Node.js and MCP are already installed in the base image!
# Just add Fixer specific dependencies (docker SDK)
RUN pip install docker

COPY . .

CMD ["python", "main.py"]
