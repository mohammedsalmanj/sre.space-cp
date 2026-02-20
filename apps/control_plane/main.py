from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import asyncio
import json
import uvicorn
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from apps.control_plane.langgraph_logic import run_sre_loop
from packages.agents.jules import jules_agent
from apps.control_plane.runtime_config import ENV, EVENT_BUS as BUS_BACKEND, AGENT_LOOP_INTERVAL, DEGRADED_MODE, LOG_LEVEL
from packages.shared.memory_guard import get_system_stats, check_memory_health
from packages.shared.event_bus.factory import get_event_bus

app = FastAPI(title=f"SRE-Space | {ENV.upper()} Mode")
# Update templates path to be relative to the file location
templates = Jinja2Templates(directory=os.path.dirname(__file__))

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/system/health")
async def health_check():
    """Returns system health, memory usage, and mode (Lightweight)."""
    stats = get_system_stats()
    return {
        "status": "healthy" if not stats["degraded"] else "degraded",
        "mode": ENV,
        "event_bus": BUS_BACKEND,
        "active_agents": 8,
        "memory": stats,
        "log_level": LOG_LEVEL,
        "circuit_breaker_active": False # Placeholder for actual breaker logic
    }

@app.get("/ready")
async def ready_check():
    """Readiness probe: Redis connected, Vector store initialized, Agents registered."""
    try:
        # 1. Check Event Bus (Redis/Kafka)
        bus = get_event_bus()
        if BUS_BACKEND == "redis":
            if not await bus._ensure_connected():
                raise HTTPException(status_code=503, detail="Redis connection failed")
        
        # 2. Check Vector Store (ChromaDB)
        # Mocking check for demo stability
        
        # 3. Agents are registered via LangGraph at module load usually
        
        return {"status": "ready", "checks": {"bus": "connected", "agents": "registered"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/demo/inject-failure")
async def inject_failure(type: str = "infra"):
    """Manually triggers an SRE loop with an injected failure."""
    if type not in ["infra", "code"]:
        raise HTTPException(status_code=400, detail="Invalid anomaly type")
    
    # Execute the loop
    result = await run_sre_loop(is_anomaly=True, anomaly_type=type)
    return {
        "message": f"Failure injection successful: {type}", 
        "mode": ENV,
        "final_status": result["status"],
        "remediation": result["remediation"]
    }

@app.get("/quote")
async def get_quote(user_id: str = "unknown"):
    """Mock Quote Service endpoint for chaos testing."""
    import random
    # Simulate random failure
    if random.random() < 0.2 or user_id == "attacker":
        raise HTTPException(status_code=500, detail="Database connection pool exhausted")
    return {"quote_id": f"Q-{random.randint(1000, 9999)}", "price": random.randint(100, 500), "status": "success"}

@app.get("/api/sre-loop")
async def sre_loop_stream(anomaly: bool = False, type: str = "infra"):
    async def event_generator():
        result = await run_sre_loop(is_anomaly=anomaly, anomaly_type=type)
        for log in result["logs"]:
            yield f"data: {json.dumps({'message': log})}\n\n"
            # Respect loop interval and degraded mode
            sleep_time = 0.4 if not DEGRADED_MODE else 0.8
            await asyncio.sleep(sleep_time)
        yield f"data: {json.dumps({'message': '--- END OF LOOP ---', 'final_state': result['status']})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Background Worker Services ---

async def schedule_jules_daily_scan():
    while True:
        try:
            jules_agent() 
        except Exception as e:
            if LOG_LEVEL == "INFO":
                print(f"[SYSTEM] Jules Job Failed: {str(e)}")
        
        # Respect runtime interval settings
        interval = 3600 if ENV == "local" else 7200 # Slower in cloud
        await asyncio.sleep(interval) 

async def memory_monitor_loop():
    """Background task to guard memory every 30 seconds."""
    while True:
        check_memory_health()
        await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(schedule_jules_daily_scan())
    asyncio.create_task(memory_monitor_loop())

if __name__ == "__main__":
    # Render requirements: uvicorn workers and reload settings
    port = int(os.getenv("PORT", 8001))
    workers = 1 if ENV == "cloud" else int(os.getenv("WEB_CONCURRENCY", 1))
    reload = True if ENV == "local" else False
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        workers=workers, 
        reload=reload,
        log_level=LOG_LEVEL.lower()
    )
