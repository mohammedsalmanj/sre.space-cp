"""
File: apps/control_plane/main.py
Layer: Application / Entry Point
Purpose: FastAPI-based interface for the SRE-Space control plane.
Problem Solved: Provides REST and Streaming (SSE) endpoints for chaos injection and real-time observability of the autonomic loop.
Interaction: Orchestrates the LangGraph SRE loop; connects to shared memory (ChromaDB) and simulation state.
Dependencies: fastapi, uvicorn, langchain, packages.shared.*, packages.agents.*
Inputs: Chaos injection requests (POST /demo/inject-failure)
Outputs: SSE event streams, system health logs, and GitHub activity snapshots
"""
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

# Initialize Environment Variables from .env file
load_dotenv()

# Add project root to sys.path to allow absolute imports from any level of the monorepo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from apps.control_plane.langgraph_logic import run_sre_loop
from apps.control_plane.config import ENV, MEMORY_LIMIT_MB
from packages.shared.sim_state import sim_state

# --- Observability & Logging Architecture ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [SRE-SPACE] %(message)s')
logger = logging.getLogger("sre.control_plane")

# App Initialization with environment-aware branding
app = FastAPI(title=f"SRE-Space | {ENV.upper()} Control Loop v5.0")

# --- Security & Connectivity (CORS Policy) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Operational Hardening: Proactive Memory Guard ---
@app.middleware("http")
async def memory_guard_middleware(request: Request, call_next):
    """
    Monitors process memory usage to prevent OOM termination in resource-constrained environments (e.g. Docker/Render/Lambda).
    """
    process = psutil.Process()
    mem_info = process.memory_info().rss / (1024 * 1024) # Conversion to MB
    if mem_info > MEMORY_LIMIT_MB:
        logger.warning(f"🔴 [MEMORY GUARD] Critical RAM Usage: {mem_info:.2f}MB. Threshold: {MEMORY_LIMIT_MB}MB.")
    return await call_next(request)

# Template configuration for serving integrated frontend components
templates = Jinja2Templates(directory=os.path.dirname(__file__))

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serve the Cyber-Insurance Playground's unified sensory control interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/system/health")
async def system_health() -> dict:
    """Core health-check endpoint for infrastructure monitoring systems."""
    return {
        "status": "healthy",
        "env": ENV,
        "env_stack": os.getenv("STACK_TYPE"),
        "has_pinecone": bool(os.getenv("PINECONE_API_KEY")),
        "memory_usage_mb": round(psutil.Process().memory_info().rss / (1024 * 1024), 2),
        "memory_limit_mb": MEMORY_LIMIT_MB,
        "version": "5.0.0"
    }

@app.post("/api/config/save")
async def save_config(request: Request) -> dict:
    """
    Saves infrastructure configuration to the .env file.
    Used by the onboarding modal to facilitate 'first-run' setup.
    """
    body = await request.json()
    stack_type = body.get("STACK_TYPE")
    pinecone_key = body.get("PINECONE_API_KEY")
    
    if not stack_type:
        return {"status": "error", "message": "STACK_TYPE is required"}

    # Update local environment
    os.environ["STACK_TYPE"] = stack_type
    if pinecone_key:
        os.environ["PINECONE_API_KEY"] = pinecone_key
    
    # Persist to .env file for portability
    try:
        env_path = os.path.join(os.path.dirname(__file__), "../../.env")
        with open(env_path, "a") as f:
            f.write(f"\nSTACK_TYPE={stack_type}")
            if pinecone_key:
                f.write(f"\nPINECONE_API_KEY={pinecone_key}")
        logger.info(f"✅ [CONFIG] Stack '{stack_type}' configured successfully.")
    except Exception as e:
        logger.error(f"❌ [CONFIG] Failed to persist .env: {e}")

    return {"status": "success", "message": f"Stack {stack_type} configured."}

from packages.infrastructure.simulation.chaos_engine import chaos_engine

@app.post("/demo/chaos/trigger")
async def trigger_chaos(request: Request) -> dict:
    """
    Triggers a specific fault profile via the Chaos Engine for OODA validation.
    """
    body = await request.json()
    fault_name = body.get("fault")
    if not fault_name:
        return {"status": "error", "message": "Fault name required."}
    
    chaos_engine.trigger_fault(fault_name)
    
    # 🏁 Triggering the Autonomic OODA Loop immediately via background task
    asyncio.create_task(run_sre_loop(is_anomaly=True, simulation_mode=True))
    
    return {"status": "success", "message": f"Chaos triggered: {fault_name}"}

@app.post("/demo/chaos/clear")
async def clear_chaos() -> dict:
    """Clears all active synthetic faults."""
    chaos_engine.clear_faults()
    return {"status": "success", "message": "Chaos cleared."}

@app.post("/demo/inject-failure")
async def inject_failure(request: Request) -> dict:
    """
    Entry point for synthetic chaos injection used during validation or demo cycles.
    
    Args:
        request (Request): Chaos metadata (e.g. {"type": "db_pool_exhaustion"}).
    Returns:
        dict: Confirmation of successful failure injection.
    """
    try:
        body = await request.json()
        chaos_type = body.get("type", "db_pool_exhaustion")
    except Exception:
        chaos_type = "db_pool_exhaustion"

    logger.info(f"🔥 [CHAOS] Synthetic {chaos_type.replace('_', ' ')} injected into policy-service.")
    sim_state.inject_failure(chaos_type)
    
    # 🏁 Triggering the Autonomic OODA Loop immediately via background task
    asyncio.create_task(run_sre_loop(is_anomaly=True, simulation_mode=False))
    
    return {"status": "success", "message": f"Failure injected: {chaos_type}", "type": chaos_type}

@app.post("/demo/sandbox/start")
async def start_sandbox() -> dict:
    """
    Activates the sandbox mode by triggering a mock database connection leak.
    Used for local testing without real cloud infrastructure.
    """
    try:
        # Create a trigger file for the mock-otel-generator container
        with open("/tmp/inject_leak", "w") as f:
            f.write("active")
        logger.info("🧪 [SANDBOX] Mock Database Leak Injected.")
        
        # Trigger the OODA loop
        asyncio.create_task(run_sre_loop(is_anomaly=True, simulation_mode=True))
        
        return {"status": "success", "message": "Sandbox active: DB Leak Injected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/quote")
async def get_quote(user_id: str = "unknown") -> dict:
    """
    Simulated business endpoint that reacts to the active infrastructure state.
    Solves the problem of demonstrating user-facing impact during SRE incidents.
    """
    import random
    from fastapi import HTTPException
    
    current = sim_state.get_state()
    if current["is_anomaly"] and current["failure_type"] == "db_pool_exhaustion":
        raise HTTPException(status_code=500, detail="Database connection pool exhausted")
    
    if random.random() < 0.2:
        raise HTTPException(status_code=500, detail="Sensory noise timeout")
        
    return {"quote_id": f"Q-{random.randint(1000, 9999)}", "price": random.randint(100, 500), "status": "success"}

@app.post("/demo/resolve")
async def resolve_system() -> dict:
    """Manual restoration endpoint for system testing."""
    sim_state.resolve_fix()
    return {"status": "success", "message": "System restored to healthy state."}

@app.get("/api/git-activity")
async def get_git_activity():
    """Provides a view into the GitOps remediation activity for the dashboard visualization."""
    from packages.shared.github_service import GitHubService
    gh = GitHubService()
    try:
        url = f"{gh.base_url}/repos/{gh.owner}/{gh.repo}/pulls?state=all&per_page=5"
        res = requests.get(url, headers=gh.headers, timeout=10)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/sre-loop")
async def sre_loop_stream(anomaly: bool = False, simulation: bool = False):
    """
    Streaming event source (SSE) for visualizing agent-based OODA reasoning in real-time.
    Enables transparency and auditability for autonomous SRE actions.
    """
    async def event_generator():
        result = await run_sre_loop(is_anomaly=anomaly, simulation_mode=simulation)
        for log in result["logs"]:
            yield f"data: {json.dumps({'message': log})}\n\n"
            await asyncio.sleep(0.4) # Visualization pacing for human readability
        yield f"data: {json.dumps({'message': '--- END OF LOOP ---', 'final_state': result['status']})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    # Standard Uvicorn startup logic for local development
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
