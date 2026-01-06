from fastapi import FastAPI, HTTPException
import uvicorn
import os
import random
import time
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI(title="Insure.Space Policy Service")

# Simulation of Failure State
FAILURE_MODE = os.getenv("FAILURE_MODE", "normal")

@app.post("/chaos/crash")
async def trigger_crash():
    global FAILURE_MODE
    FAILURE_MODE = "crash"
    return {"message": "Crash mode activated"}

@app.post("/chaos/normal")
async def trigger_normal():
    global FAILURE_MODE
    FAILURE_MODE = "normal"
    return {"message": "Normal mode activated"}

@app.get("/health")
async def health():
    if FAILURE_MODE == "crash":
        time.sleep(10) # Simulate hang
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return {"status": "healthy"}

@app.get("/policies")
async def get_policies():
    return [
        {"id": 1, "type": "Car Insurance", "premium": 150},
        {"id": 2, "type": "Life Insurance", "premium": 250},
        {"id": 3, "type": "Home Insurance", "premium": 300},
        {"id": 4, "type": "Health Insurance", "premium": 400},
        {"id": 5, "type": "Travel Insurance", "premium": 50},
        {"id": 6, "type": "Pet Insurance", "premium": 30}
    ]

@app.post("/purchase")
async def purchase_policy(policy_id: int):
    if FAILURE_MODE == "latency":
        time.sleep(random.uniform(2, 5))
    return {"message": "Policy purchased successfully", "id": policy_id}

FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
