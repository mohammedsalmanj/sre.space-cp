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

# Initialize Environment Variables
load_dotenv()

# Add project root to sys.path to allow absolute imports from any directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from apps.control_plane.langgraph_logic import run_sre_loop
from apps.control_plane.config import ENV, MEMORY_LIMIT_MB

# --- Observability & Logging Setup ---
# Standardizing logs for the OODA loop (Observe-Orient-Decide-Act)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [SRE-SPACE] %(message)s')
logger = logging.getLogger("sre.control_plane")

# App Initialization with dynamic title based on the deployment mode
app = FastAPI(title=f"SRE-Space | {ENV.upper()} Control Loop v5.0")

# --- Security & Connectivity (CORS) ---
# Enable Cross-Origin Resource Sharing to allow the Vercel-hosted dashboard 
# to communicate with the Render-hosted backend smoothly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Operational Hardening: Memory Guard ---
# Render's free tier has a 512MB limit. This middleware monitors the process RSS memory
# and warns the system if it nears the limit, allowing for proactive sensory failover.
@app.middleware("http")
async def memory_guard_middleware(request: Request, call_next):
    process = psutil.Process()
    mem_info = process.memory_info().rss / (1024 * 1024) # MB
    if mem_info > MEMORY_LIMIT_MB:
        logger.warning(f"🔴 [MEMORY GUARD] Critical RAM Usage: {mem_info:.2f}MB. Threshold: {MEMORY_LIMIT_MB}MB.")
    return await call_next(request)

# Template configuration for serving the Insurance Playground UI
templates = Jinja2Templates(directory=os.path.dirname(__file__))

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serve the cyber-insurance playground UI."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/system/health")
async def system_health():
    """Health check for the Vercel Monitor to visualize environment settings."""
    process = psutil.Process()
    return {
        "status": "healthy",
        "env": ENV,
        "memory_usage_mb": round(psutil.Process().memory_info().rss / (1024 * 1024), 2),
        "memory_limit_mb": MEMORY_LIMIT_MB,
        "version": "4.5.1"
    }

from packages.shared.sim_state import sim_state

@app.post("/demo/inject-failure")
async def inject_failure(request: Request):
    """
    Simulate a production incident. 
    Triggers: 1. Global state change 2. Background SRE agent loop via LangGraph.
    """
    try:
        body = await request.json()
        chaos_type = body.get("type", "db_pool_exhaustion")
    except:
        chaos_type = "db_pool_exhaustion"

    logger.info(f"🔥 [CHAOS] Synthetic {chaos_type.replace('_', ' ')} injected into policy-service.")
    sim_state.inject_failure(chaos_type)
    
    # Fire and forget: SRE loop starts detecting the trace immediately
    asyncio.create_task(run_sre_loop(is_anomaly=True))
    
    return {"status": "success", "message": f"Failure injected: {chaos_type}", "type": chaos_type}

@app.get("/quote")
async def get_quote(user_id: str = "unknown"):
    """Mock Quote Endpoint that reacts to chaos injections."""
    import random
    from fastapi import HTTPException
    
    current = sim_state.get_state()
    # Check if the system is currently under simulated failure
    if current["is_anomaly"] and current["failure_type"] == "db_pool_exhaustion":
        raise HTTPException(status_code=500, detail="Database connection pool exhausted")
    
    # Simulated 20% random noise failure for higher baseline observability
    if random.random() < 0.2:
        raise HTTPException(status_code=500, detail="Sensory noise timeout")
        
    return {"quote_id": f"Q-{random.randint(1000, 9999)}", "price": random.randint(100, 500), "status": "success"}

@app.post("/demo/resolve")
async def resolve_system():
    """Manual trigger to restore system health."""
    sim_state.resolve_fix()
    return {"status": "success", "message": "System restored."}

@app.get("/api/git-activity")
async def get_git_activity():
    """Interface for the dashboard to show real GitHub PR veracity data."""
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
    """Streaming endpoint (SSE) to visualize agent OODA reasoning in the UI."""
    async def event_generator():
        result = await run_sre_loop(is_anomaly=anomaly)
        for log in result["logs"]:
            yield f"data: {json.dumps({'message': log})}\n\n"
            await asyncio.sleep(0.4) # Control flow for readable demo visualization
        yield f"data: {json.dumps({'message': '--- END OF LOOP ---', 'final_state': result['status']})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    # Standard Uvicorn entry point
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
