import asyncio
import json
import os
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from confluent_kafka import Consumer, KafkaError
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket-bridge")

app = FastAPI()

# Kafka Config
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPICS = ["agent_thoughts", "incident_updates", "insurance_events", "remediation_log"]

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")

manager = ConnectionManager()

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def kafka_consumer_loop():
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'websocket-bridge-group',
        'auto.offset.reset': 'latest'
    }
    consumer = Consumer(conf)
    consumer.subscribe(TOPICS)

    logger.info(f"Subscribed to topics: {TOPICS}")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Kafka error: {msg.error()}")
                    break

            payload = msg.value().decode('utf-8')
            topic = msg.topic()
            
            logger.info(f"Received message from {topic}")
            
            broadcast_data = {
                "topic": topic,
                "data": json.loads(payload)
            }
            await manager.broadcast(json.dumps(broadcast_data))
            await asyncio.sleep(0) # Yield for other tasks
    finally:
        consumer.close()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(kafka_consumer_loop())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
