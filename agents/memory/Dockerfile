FROM python:3.10-slim

WORKDIR /app

RUN pip install mcp openai chromadb requests

COPY . .

CMD ["python", "main.py"]
