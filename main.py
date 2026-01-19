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

# Mock Agent Logic for real-time visuals
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
    # Step 1: Scout intercepts
    yield f"data: {json.dumps(scout.log(f'Intercepted {policy_type} quote request from user_session.'))}\n\n"
    await asyncio.sleep(0.6)
    
    # Step 2: Brain analyzes
    trace_id = f"trace-{random.randint(10000,99999)}"
    yield f"data: {json.dumps(brain.log(f'Tracing request ID {trace_id}. Correlating microservice latency...'))}\n\n"
    await asyncio.sleep(1.0)
    
    # Step 3: Probabilistic Failure Simulation
    if random.random() < 0.2:
        yield f"data: {json.dumps(scout.log('ALERT: High latency detected in policy-service (900ms).'))}\n\n"
        await asyncio.sleep(0.5)
        yield f"data: {json.dumps(brain.log('Root Cause: Memory saturation in container. Recommending vertical scaling.'))}\n\n"
        await asyncio.sleep(0.8)
        yield f"data: {json.dumps(fixer.log('Initiating auto-scale. Patching deployment config...'))}\n\n"
        await asyncio.sleep(1.0)
        yield f"data: {json.dumps(fixer.log('Remediation successful. Health restored.'))}\n\n"
    else:
        yield f"data: {json.dumps(scout.log('Health check passed. No anomalies detected.'))}\n\n"
    
    # Step 4: Conclusion
    yield f"data: {json.dumps(brain.log(f'Quote calculated for {policy_type}. Serving response.'))}\n\n"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/quote-stream")
async def stream_quote(policy_type: str = "General"):
    return StreamingResponse(generate_telemetry(policy_type), media_type="text/event-stream")

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "v3.0"}
