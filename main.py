from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import asyncio
import json
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

from langgraph_logic import run_sre_loop

app = FastAPI(title="Insurance Platform | Autonomous Reliability Engine v3.0")
templates = Jinja2Templates(directory="templates")

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
async def sre_loop_stream(anomaly: bool = False):
    async def event_generator():
        result = await run_sre_loop(is_anomaly=anomaly)
        for log in result["logs"]:
            yield f"data: {json.dumps({'message': log})}\n\n"
            await asyncio.sleep(0.4)
        yield f"data: {json.dumps({'message': '--- END OF LOOP ---', 'final_state': result['status']})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Daily Architectural Review Task (Simulated) ---
async def schedule_jules_daily_scan():
    """Simulates Jules running at 09:30 AM GMT+5:30"""
    while True:
        # In a real app, use a proper scheduler like APScheduler
        # Here we just log the presence of the Tier-3 Authority
        print(f"[SYSTEM] Jules Tier-3 Review Service: Waiting for 09:30 AM GMT+5:30 window...")
        await asyncio.sleep(3600) # Check every hour

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(schedule_jules_daily_scan())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
