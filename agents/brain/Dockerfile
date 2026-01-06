FROM python:3.10-slim

WORKDIR /app

# Install Node.js (required for GitHub MCP Server)
RUN apt-get update && apt-get install -y nodejs npm git && \
    npm install -g @modelcontextprotocol/server-github

RUN pip install mcp openai requests docker

COPY . .

CMD ["python", "main.py"]
