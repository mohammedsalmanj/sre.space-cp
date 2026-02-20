import time
from collections import deque

# Store last 100 requests (timestamp, status_code, latency_ms)
REQUEST_HISTORY = deque(maxlen=100)

def track_request(status_code, latency_ms):
    REQUEST_HISTORY.append({
        "timestamp": time.time(),
        "status_code": status_code,
        "latency_ms": latency_ms
    })

def get_metrics():
    if not REQUEST_HISTORY:
        return {"error_rate": 0, "avg_latency": 0, "count": 0}
    
    # Analyze requests from the last 60 seconds
    now = time.time()
    recent = [r for r in REQUEST_HISTORY if now - r["timestamp"] < 60]
    
    if not recent:
        return {"error_rate": 0, "avg_latency": 0, "count": 0}
        
    errors = sum(1 for r in recent if r["status_code"] >= 500)
    latencies = [r["latency_ms"] for r in recent]
    
    return {
        "error_rate": errors / len(recent),
        "avg_latency": sum(latencies) / len(recent),
        "count": len(recent)
    }
