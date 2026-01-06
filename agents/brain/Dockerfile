FROM python:3.10-slim

WORKDIR /app

RUN pip install mcp openai requests docker

COPY . .

CMD ["python", "main.py"]
