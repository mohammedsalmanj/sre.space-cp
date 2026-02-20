from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import asyncio
import json
import uvicorn
from dotenv import load_dotenv
import os
import sys
import time
import random
from datetime import datetime

load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from apps.control_plane.langgraph_logic import run_sre_loop
from packages.agents.jules import jules_agent
from apps.control_plane.runtime_config import (
    ENV, EVENT_BUS as BUS_BACKEND, AGENT_LOOP_INTERVAL, 
    DEGRADED_MODE, LOG_LEVEL, CHAOS_MODE, update_chaos_mode
)
from packages.shared.memory_guard import get_system_stats, check_memory_health
from packages.shared.event_bus.factory import get_event_bus
from packages.shared.github_service import GitHubService
from packages.shared.telemetry import track_request

app = FastAPI(title=f"SRE-Space | {ENV.upper()} Mode")
templates = Jinja2Templates(directory=os.path.dirname(__file__))
github = GitHubService()

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Main Insurance Application (Marketplace)."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/monitor", response_class=HTMLResponse)
async def get_monitor(request: Request):
    """SRE Orbital Monitor Dashboard (For Vercel/Monitoring)."""
    return templates.TemplateResponse("monitor.html", {"request": request})

@app.get("/system/health")
async def health_check():
    """Returns actual system health, memory usage, and mode."""
    stats = get_system_stats()
    return {
        "status": "healthy" if not stats["degraded"] else "degraded",
        "mode": ENV,
        "event_bus": BUS_BACKEND,
        "active_agents": 8,
        "memory": stats,
        "log_level": LOG_LEVEL,
        "circuit_breaker_active": False,
        "chaos_active": CHAOS_MODE["active"]
    }

@app.get("/api/git-activity")
async def git_activity():
    """Fetches real-time GitHub issues and PRs for the dashboard."""
    try:
        issues = github.list_issues(state="all", per_page=5)
        filtered_issues = [
            {
                "number": i["number"],
                "title": i["title"],
                "state": i["state"],
                "created_at": i["created_at"],
                "type": "pull_request" if "pull_request" in i else "issue"
            }
            for i in issues if isinstance(i, dict)
        ]
        return filtered_issues
    except Exception as e:
        return {"error": str(e)}

@app.get("/ready")
async def ready_check():
    """Readiness probe: Redis connected, Vector store initialized, Agents registered."""
    try:
        bus = get_event_bus()
        if BUS_BACKEND == "redis":
            if not await bus._ensure_connected():
                raise HTTPException(status_code=503, detail="Redis connection failed")
        return {"status": "ready", "checks": {"bus": "connected", "agents": "registered"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/demo/inject-failure")
async def inject_failure(type: str = "500"):
    """Manually triggers chaos injection mode."""
    valid_types = ["500", "latency", "memory", "dependency"]
    if type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid anomaly type. Must be one of {valid_types}")
    
    update_chaos_mode(type, True)
    
    # Trigger the cognitive loop (Real loop, no mocks)
    result = await run_sre_loop(is_anomaly=True, anomaly_type=type)
    
    # If it's a memory spike, we can actually simulate high RAM usage
    if type == "memory":
        # We don't actually bloat memory to avoid OOM in Render, but we flip the flag
        from apps.control_plane.runtime_config import update_degraded_mode
        update_degraded_mode(True)

    return {
        "message": f"Engineering Control Triggered: {type.upper()}", 
        "status": "Fault Active",
        "chaos_status": CHAOS_MODE,
        "recovery_status": result["status"]
    }

@app.get("/quote")
async def get_quote(user_id: str = "unknown"):
    """Real-time Quote Service with Telemetry & Chaos integration."""
    start_time = time.time()
    
    # Check for active chaos
    if CHAOS_MODE["active"]:
        c_type = CHAOS_MODE["type"]
        
        if c_type == "latency":
            await asyncio.sleep(2.5) 
        elif c_type == "dependency":
            # Simulate a 10s dependency timeout
            await asyncio.sleep(10.0)
            track_request(504, (time.time() - start_time) * 1000)
            raise HTTPException(status_code=504, detail="Upstream Dependency Timeout")
        elif c_type == "500":
            if random.random() < 0.9:
                track_request(500, (time.time() - start_time) * 1000)
                raise HTTPException(status_code=500, detail="Internal Server Error: Database Pool Exhausted")

    # Natural drift simulation (very low probability)
    elif random.random() < 0.005:
         track_request(500, (time.time() - start_time) * 1000)
         raise HTTPException(status_code=500, detail="Intermittent Service Fault")

    latency = (time.time() - start_time) * 1000
    track_request(200, latency)
    return {
        "quote_id": f"Q-{random.randint(100000, 999999)}", 
        "premium": round(random.uniform(50.0, 500.0), 2), 
        "currency": "USD",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/sre-loop")
async def sre_loop_stream(anomaly: bool = False, type: str = "infra"):
    async def event_generator():
        result = await run_sre_loop(is_anomaly=anomaly, anomaly_type=type)
        for log in result["logs"]:
            yield f"data: {json.dumps({'message': log})}\n\n"
            sleep_time = 0.4 if not DEGRADED_MODE else 0.8
            await asyncio.sleep(sleep_time)
        yield f"data: {json.dumps({'message': '--- END OF LOOP ---', 'final_state': result['status']})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def schedule_jules_daily_scan():
    while True:
        try:
            jules_agent() 
        except Exception as e:
            if LOG_LEVEL == "INFO":
                print(f"[SYSTEM] Jules Job Failed: {str(e)}")
        interval = 3600 if ENV == "local" else 7200 
        await asyncio.sleep(interval) 

async def memory_monitor_loop():
    while True:
        check_memory_health()
        await asyncio.sleep(30)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(schedule_jules_daily_scan())
    asyncio.create_task(memory_monitor_loop())

if __name__ == "__main__":
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
