from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import random
import time
from datetime import datetime

# Initialize FastAPI
app = FastAPI(title="Insurance Platform | Autonomous Reliability Engine v3.0")

# Setup Templates
templates = Jinja2Templates(directory="templates")

# Mock Agents for Demo (Refactor logic from agents/ folder if needed, 
# but keeping it simple for single-file deployment reliability)
class Agent:
    def __init__(self, name, role, color):
        self.name = name
        self.role = role
        self.color = color

    def log(self, message):
        return {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "role": self.role,
            "color": self.color,
            "message": message
        }

scout = Agent("Scout", "Watchdog", "#10b981") # Green
brain = Agent("Brain", "Strategist", "#8b5cf6") # Purple
fixer = Agent("Fixer", "Mechanic", "#ef4444") # Red

async def generate_telemetry(policy_type: str):
    """Simulates the Agent Squad analyzing a request."""
    yield f"data: {json.dumps(scout.log(f'Intercepted {policy_type} quote request. Verifying business tiers...'))}\n\n"
    await asyncio.sleep(0.8)
    
    yield f"data: {json.dumps(brain.log(f'Tracing request ID {random.randint(1000,9999)}. Correlating span latency...'))}\n\n"
    await asyncio.sleep(1.2)
    
    # Simulate a random "incident" or normal flow
    if random.random() < 0.3:
        yield f"data: {json.dumps(scout.log('ALERT: Anomaly detected! High latency on policy-service.'))}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps(brain.log('Root Cause: Memory saturation in container 8b2f.'))}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps(fixer.log('Initiating auto-scale vertically. Applying patch 3.1...'))}\n\n"
        await asyncio.sleep(1.0)
        yield f"data: {json.dumps(fixer.log('Remediation successful. System health restored.'))}\n\n"
    else:
        yield f"data: {json.dumps(scout.log('Health check passed. No anomalies.'))}\n\n"
    
    yield f"data: {json.dumps(brain.log(f'Quote generated successfully. Premium calculated.'))}\n\n"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/quote-stream")
async def stream_quote(policy_type: str = "General"):
    return StreamingResponse(generate_telemetry(policy_type), media_type="text/event-stream")

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "v3.0"}
