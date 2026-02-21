from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import uvicorn
import requests
import psutil
import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from apps.control_plane.langgraph_logic import run_sre_loop
from apps.control_plane.config import ENV, MEMORY_LIMIT_MB

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("sre.control_plane")

app = FastAPI(title=f"SRE.Space | {ENV.upper()} Control Plane v4.5")

# Block 1: Multi-Cloud CORS Logic
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Block 4: Operational Hardening (Memory Guard)
@app.middleware("http")
async def memory_guard_middleware(request: Request, call_next):
    process = psutil.Process()
    mem_info = process.memory_info().rss / (1024 * 1024) # MB
    if mem_info > MEMORY_LIMIT_MB:
        logger.warning(f"🔴 [MEMORY GUARD] Critical RAM Usage: {mem_info:.2f}MB. Limit: {MEMORY_LIMIT_MB}MB.")
    return await call_next(request)

templates = Jinja2Templates(directory=os.path.dirname(__file__))

# Global System State for Demo
SYSTEM_STATE = {
    "is_anomaly": False,
    "failure_type": None
}

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/system/health")
async def system_health():
    """Endpoint for Vercel Dashboard to read environment and status."""
    process = psutil.Process()
    return {
        "status": "healthy",
        "env": ENV,
        "memory_usage_mb": round(process.memory_info().rss / (1024 * 1024), 2),
        "memory_limit_mb": MEMORY_LIMIT_MB,
        "version": "4.5.0"
    }

@app.post("/demo/inject-failure")
async def inject_failure():
    """Trigger a synthetic failure for the SRE demo loop."""
    logger.info("🔥 [CHAOS] Injecting synthetic failure into policy-service...")
    SYSTEM_STATE["is_anomaly"] = True
    SYSTEM_STATE["failure_type"] = "db_pool_exhaustion"
    
    # Block 2: Detect failure -> Trigger chain
    asyncio.create_task(run_sre_loop(is_anomaly=True))
    
    return {"message": "Failure injected. SRE loop triggered.", "type": "db_pool_exhaustion"}

@app.get("/quote")
async def get_quote(user_id: str = "unknown"):
    """Mock Quote Service endpoint for chaos testing."""
    import random
    from fastapi import HTTPException
    if SYSTEM_STATE["is_anomaly"] and SYSTEM_STATE["failure_type"] == "db_pool_exhaustion":
        raise HTTPException(status_code=500, detail="Database connection pool exhausted")
    elif random.random() < 0.2 or user_id == "attacker":
        raise HTTPException(status_code=500, detail="Database connection pool exhausted")
    return {"quote_id": f"Q-{random.randint(1000, 9999)}", "price": random.randint(100, 500), "status": "success"}

@app.get("/api/git-activity")
async def get_git_activity():
    """Fetches real PR activity for the dashboard."""
    from packages.shared.github_service import GitHubService
    gh = GitHubService()
    try:
        url = f"{gh.base_url}/repos/{gh.owner}/{gh.repo}/pulls?state=all&per_page=5"
        res = requests.get(url, headers=gh.headers, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/sre-loop")
async def sre_loop_stream(anomaly: bool = False):
    async def event_generator():
        result = await run_sre_loop(is_anomaly=anomaly)
        for log in result["logs"]:
            yield f"data: {json.dumps({'message': log})}\n\n"
            await asyncio.sleep(0.4)
        yield f"data: {json.dumps({'message': '--- END OF LOOP ---', 'final_state': result['status']})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
