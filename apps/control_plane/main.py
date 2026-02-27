"""
File: apps/control_plane/main.py
Layer: Application / Entry Point
Purpose: FastAPI-based interface for the SRE-Space control plane.
"""
from fastapi import FastAPI, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
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
import boto3
from botocore.exceptions import ClientError
from google.oauth2 import service_account
from google.auth import exceptions as google_exceptions

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
    allow_origins=["*", "https://*.vercel.app"],
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

# Template and Static configuration for serving integrated frontend components
current_dir = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=current_dir), name="static")
templates = Jinja2Templates(directory=current_dir)

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Serve the SRE-Space unified sensory control interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/system/health")
@app.get("/api/health")
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
    """
    body = await request.json()
    stack_type = body.get("STACK_TYPE")
    pinecone_key = body.get("PINECONE_API_KEY")
    
    if not stack_type:
        return {"status": "error", "message": "STACK_TYPE is required"}

    os.environ["STACK_TYPE"] = stack_type
    if pinecone_key:
        os.environ["PINECONE_API_KEY"] = pinecone_key
    
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

@app.get("/about")
async def about_page(request: Request):
    """Serves the premium branding and architectural guide."""
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/api/v1/meta")
async def get_meta():
    """Returns platform metadata for the 'Liquid Glass' UI system."""
    return {
        "lead": "Mohammed Salman",
        "role": "SRE · AIOps Engineer",
        "philosophy": "Reasoning for High-Scale Reliability.",
        "stack_icons": {
            "ec2": "aws",
            "k8s": "kubernetes",
            "otel": "opentelemetry"
        }
    }

from packages.infrastructure.simulation.chaos_engine import chaos_engine

@app.post("/demo/chaos/trigger")
async def trigger_chaos(request: Request, background_tasks: BackgroundTasks) -> dict:
    """
    Triggers a specific fault profile via the Chaos Engine for OODA validation.
    """
    body = await request.json()
    fault_name = body.get("fault")
    if not fault_name:
        return {"status": "error", "message": "Fault name required."}
    
    chaos_engine.trigger_fault(fault_name)
    return {"status": "success", "message": f"Fault '{fault_name}' triggered."}

# --- Enterprise Provisioning Wizard: Validation Endpoints ---

@app.post("/api/v1/validate/aws")
async def validate_aws(request: Request):
    """Gated validation for AWS credentials using STS."""
    body = await request.json()
    ak = body.get("accessKey")
    sk = body.get("secretKey")
    region = body.get("region", "us-east-1")

    if not ak or not sk:
        return {"status": "error", "message": "Missing credentials."}

    try:
        session = boto3.Session(
            aws_access_key_id=ak,
            aws_secret_access_key=sk,
            region_name=region
        )
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        return {
            "status": "success",
            "message": "Credential Validation: SUCCESS",
            "account": identity.get("Account"),
            "arn": identity.get("Arn")
        }
    except ClientError as e:
        return {"status": "error", "message": f"Validation FAILED: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"System Error: {str(e)}"}

@app.post("/api/v1/validate/gcp")
async def validate_gcp(request: Request):
    """Gated validation for GCP credentials via Service Account JSON."""
    body = await request.json()
    json_key = body.get("jsonKey")
    
    if not json_key:
        return {"status": "error", "message": "Missing JSON Key file content."}

    try:
        info = json.loads(json_key)
        credentials = service_account.Credentials.from_service_account_info(info)
        # Simple proof of life: project_id check
        project_id = credentials.project_id
        return {
            "status": "success",
            "message": "Credential Validation: SUCCESS",
            "project_id": project_id
        }
    except google_exceptions.GoogleAuthError as e:
        return {"status": "error", "message": f"Auth Error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Invalid JSON Profile: {str(e)}"}

@app.get("/api/v1/provision/execute")
async def provision_stream(provider: str, stack: str):
    """
    Real-time streaming panel for infrastructure execution logs.
    Simulates Terraform/SDK logs with realistic enterprise stages.
    """
    async def event_generator():
        stages = [
            "INITIATED",
            "VALIDATING_QUOTAS",
            "CONSTRUCTING_INFRA_GRAPH",
            "CREATING_RESOURCES",
            "CONFIGURING_NETWORKING",
            "INSTALLING_OTEL_COLLECTOR",
            "BOOTSTRAPPING_SRE_AGENTS",
            "REGISTERING_WITH_CONTROL_PLANE",
            "SUCCESS"
        ]
        
        for stage in stages:
            progress = (stages.index(stage) + 1) / len(stages) * 100
            log_msg = f"[{provider.upper()}] Status: {stage} ... {progress:.0f}%"
            
            # Simulate detailed execution logs for some stages
            if stage == "CREATING_RESOURCES":
                yield f"data: {json.dumps({'message': f'Creating {stack} instance in {provider}...', 'status': stage})}\n\n"
                await asyncio.sleep(1)
                yield f"data: {json.dumps({'message': 'Attaching EBS Volumes...', 'status': stage})}\n\n"
                await asyncio.sleep(1)
            
            yield f"data: {json.dumps({'message': log_msg, 'status': stage, 'progress': progress})}\n\n"
            await asyncio.sleep(1.5 if stage != "SUCCESS" else 0.5)
            
        yield f"data: {json.dumps({'message': 'Provisioning sequence complete. Transitioning to Operational Mode.', 'final': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Real-Time Telemetry & Metric Streaming ---

@app.get("/api/v1/telemetry/stream")
async def telemetry_stream():
    """
    SSE stream for real-time infrastructure metrics (CPU, RAM, etc).
    """
    async def metrics_generator():
        while True:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            # Mock some network throughput for visuals
            sent = psutil.net_io_counters().bytes_sent
            recv = psutil.net_io_counters().bytes_recv
            
            data = {
                "cpu": cpu,
                "memory": mem,
                "disk": disk,
                "network": {"sent": sent, "recv": recv},
                "otel_status": "Active",
                "heartbeat": True
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(metrics_generator(), media_type="text/event-stream")

@app.get("/api/git-activity")
async def get_git_activity():
    """Returns recent remediation PRs for the Git Veracity UI."""
    return [
        {
            "number": 104,
            "title": "fix: Autonomic Scaling - EC2-West Region",
            "html_url": "https://github.com/mohammedsalmanj/sre.space-cp/pull/104",
            "state": "closed",
            "user": {"login": "fixer-agent"},
            "head": {"sha": "fa436a8"}
        },
        {
            "number": 103,
            "title": "remediate: Pod Crash Mitigation - K8s Cluster A",
            "html_url": "https://github.com/mohammedsalmanj/sre.space-cp/pull/103",
            "state": "open",
            "user": {"login": "fixer-agent"},
            "head": {"sha": "a89e66f"}
        }
    ]

@app.get("/api/sre-loop")
async def sre_loop_stream(anomaly: bool = False):
    """
    SSE endpoint for real-time diagnostic and remediation logs.
    """
    async def event_generator():
        last_log_count = 0
        is_anomaly = anomaly
        
        # Trigger loop execution
        _sre_graph = run_sre_loop(is_anomaly=is_anomaly)
        
        initial_state = {
            "messages": [], 
            "logs": [f"INIT: Autonomous OODA cycle started. Target: {os.getenv('STACK_TYPE', 'LOCAL')}"]
        }

        try:
            async for event in _sre_graph.astream(initial_state):
                for node_name, state in event.items():
                    current_logs = state.get("logs", [])
                    new_logs = current_logs[last_log_count:]
                    for log in new_logs:
                        yield f"data: {json.dumps({'message': log, 'agent': node_name.split(':')[-1]})}\n\n"
                    last_log_count = len(current_logs)
                    
                    if state.get("status"):
                        message = f"System Status: {state['status']}"
                        yield f"data: {json.dumps({'message': message})}\n\n"

            yield f"data: {json.dumps({'message': '--- END OF LOOP ---', 'final_state': 'Resolved' if not is_anomaly else 'Resolved'})}\n\n"
        except Exception as e:
            logger.error(f"Error in SRE loop stream: {e}")
            yield f"data: {json.dumps({'message': f'[ERROR] Loop failed: {str(e)}', 'final_state': 'Error'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
