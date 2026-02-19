from datetime import datetime

CAG_FAST_CACHE = {
    "HTTP 500: Database connection pool exhausted": {
        "root_cause": "System Saturation: DB Pool Exhaustion",
        "remediation": "SCALE: Increase pool size",
        "confidence": 0.95
    }
}

def cag_agent(state):
    """Agent: CAG (Fast Cache)"""
    logs = state.get("logs", [])
    if not state["error_spans"]: return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] Checking Tier-1 Fast Cache for incident FAQ...")
    msg = state["error_spans"][0]["exception.message"]
    
    if msg in CAG_FAST_CACHE:
        known = CAG_FAST_CACHE[msg]
        state["root_cause"] = known["root_cause"]
        state["remediation"] = known["remediation"]
        state["confidence_score"] = known["confidence"]
        state["cache_hit"] = True
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] INSTANT-HIT. Known incident signature.")
    else:
        state["cache_hit"] = False
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] Cache Miss. Escalating to Brain...")

    state["logs"] = logs
    return state
