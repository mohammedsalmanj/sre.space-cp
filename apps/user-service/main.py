from fastapi import FastAPI
import os
import random
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI(title="SRE-Space | User Service")

tracer = trace.get_tracer(__name__)

users_db = {
    "guest": {"name": "Guest User", "tier": "Bronze"},
    "admin": {"name": "Admin User", "tier": "Gold"},
    "sre-tester": {"name": "SRE Tester", "tier": "Platinum"}
}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/user/{user_id}")
async def get_user(user_id: str):
    with tracer.start_as_current_span("fetch_user_profile") as span:
        span.set_attribute("user.id", user_id)
        
        # Simulate a small delay
        import time
        time.sleep(random.uniform(0.1, 0.3))
        
        user = users_db.get(user_id)
        if not user:
            span.set_status(trace.Status(trace.StatusCode.ERROR, "User Not Found"))
            return {"error": "User not found"}, 404
            
        return user

FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
