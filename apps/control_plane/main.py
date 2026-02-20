from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import asyncio
import json
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

import sys
import os
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from apps.control_plane.langgraph_logic import run_sre_loop
from packages.agents.jules import jules_agent

app = FastAPI(title="Insurance Platform | Autonomous Reliability Engine v3.0")
# Update templates path to be relative to the file location
templates = Jinja2Templates(directory=os.path.dirname(__file__))

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/quote")
async def get_quote(user_id: str = "unknown"):
    """Mock Quote Service endpoint for chaos testing."""
    import random
    # Simulate random failure
    if random.random() < 0.2 or user_id == "attacker":
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Database connection pool exhausted")
    return {"quote_id": f"Q-{random.randint(1000, 9999)}", "price": random.randint(100, 500), "status": "success"}

@app.get("/api/sre-loop")
async def sre_loop_stream(anomaly: bool = False, type: str = "infra", lang: str = "en"):
    """
    Triggers the SRE cognitive cycle and streams logs in real-time via Server-Sent Events (SSE).
    
    Args:
        anomaly (bool): If true, simulates a service failure to trigger the full repair loop.
        type (str): The type of anomaly ('infra' or 'code')
        lang (str): Language ('en' or 'ar')
    """
    async def event_generator():
        result = await run_sre_loop(is_anomaly=anomaly, anomaly_type=type, lang=lang)
        for log in result["logs"]:
            yield f"data: {json.dumps({'message': log})}\n\n"
            await asyncio.sleep(0.4) # Simulated delay for visual realism in dashboard
        yield f"data: {json.dumps({'message': '--- END OF LOOP ---', 'final_state': result['status']})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Daily Architectural Review Task (Simulated) ---
async def schedule_jules_daily_scan():
    """
    Background worker that runs Jules (The Architect) on a daily schedule.
    Jules performs high-level system checks that don't fit into the reactive incident loop.
    """
    while True:
        print(f"[SYSTEM] Jules Tier-3 Review Service: Initiating scheduled job...")
        try:
            # Jules runs independently of the LangGraph reactive cycle
            jules_agent() 
        except Exception as e:
            print(f"[SYSTEM] Jules Job Failed: {str(e)}")
        
        # In this demo, we sleep for 1 hour between checks to simulate a "daily" heartbeat
        print(f"[SYSTEM] Jules Tier-3 Review Service: Task complete. Sleeping for next window...")
        await asyncio.sleep(3600) 

@app.on_event("startup")
async def startup_event():
    """Starts background services upon FastAPI application startup."""
    asyncio.create_task(schedule_jules_daily_scan())

if __name__ == "__main__":
    # The application runs on port 8001 to avoid common port conflicts
    uvicorn.run(app, host="0.0.0.0", port=8001)
