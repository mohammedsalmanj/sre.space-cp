import asyncio
import json
import os
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from packages.shared.event_bus.factory import get_event_bus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket-bridge")

app = FastAPI()

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

async def event_callback(topic, payload):
    logger.info(f"Received message from {topic}")
    broadcast_data = {
        "topic": topic,
        "data": payload
    }
    await manager.broadcast(json.dumps(broadcast_data))

async def bridge_loop():
    bus = get_event_bus()
    logger.info(f"Starting event bus bridge with {type(bus).__name__}")
    await bus.subscribe(TOPICS, event_callback)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(bridge_loop())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
