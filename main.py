from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from langgraph_logic import run_sre_loop

app = FastAPI(title="Insurance Platform | Autonomous Reliability Engine v3.0")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/sre-loop")
async def sre_loop_stream(anomaly: bool = False):
    """
    Streams the LangGraph SRE state transitions in real-time.
    """
    async def event_generator():
        # Execute the LangGraph loop
        # For a truly real-time 'streaming' experience of steps, 
        # normally we'd consume the graph's stream of events.
        # Here we simulate the streaming of the final gathered logs for simplicity in single-thread.
        
        result = await run_sre_loop(is_anomaly=anomaly)
        
        for log in result["logs"]:
            yield f"data: {json.dumps({'message': log})}\n\n"
            await asyncio.sleep(0.5) # Simulate time passing between steps
            
        yield f"data: {json.dumps({'message': '--- END OF LOOP ---', 'final_state': result['status']})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
def health():
    return {"status": "online", "engine": "LangGraph SRE v3.0"}
