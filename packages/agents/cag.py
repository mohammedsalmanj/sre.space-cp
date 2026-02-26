"""
File: packages/agents/cag.py
Layer: Cognitive / Fast-Path Reasoning
Purpose: Instant pattern matching for known, high-confidence error signatures.
Problem Solved: Reduces MTTR (Mean Time To Repair) by bypassing expensive and slow LLM reasoning for routine outages.
Interaction: Sits between Scout and Brain; handles "Fast-Path" resolution; hands off to Brain on cache miss.
Dependencies: datetime
Inputs: Error spans from Scout
Outputs: Instant RCA and remediation plan if a match is found
"""
from datetime import datetime

# Block 1: The CAG Fast Cache
# Maps known error signatures to instant remediation strategies to skip LLM latency.
CAG_FAST_CACHE = {
    "policy-service: DOWN (HTTPConnectionPool(host='policy-service', port=8002): Max retries exceeded with url: /health (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7fc73dbd4a60>: Failed to establish a new connection: [Errno 111] Connection refused')))": {
        "root_cause": "The policy-service health check failed with 'Connection refused'. This typically indicates a crashed service container or an OOM event.",
        "remediation": "MITIGATION: RESTART policy-service",
        "confidence": 0.98
    }
}

def cag_agent(state: dict) -> dict:
    """
    Agent Node: CAG (Cognitive Agent Guide)
    Phase: ORIENT (Fast-Path)
    Mission: Provide sub-second diagnosis for common enterprise failure signatures.
    
    Args:
        state (dict): The current LangGraph state.
    Returns:
        dict: Updated state with cache_hit status and potential diagnosis.
    """
    logs = state.get("logs", [])
    if not state.get("error_spans"): return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] [ORIENT] Analyzing incident signature against Tier-1 Global Cache...")
    msg = state["error_spans"][0]["exception.message"]
    
    # 1. Pattern Matching: Check if the error is a known quantity
    if msg in CAG_FAST_CACHE:
        known = CAG_FAST_CACHE[msg]
        state["root_cause"] = known["root_cause"]
        state["remediation"] = known["remediation"]
        state["confidence_score"] = known["confidence"]
        state["cache_hit"] = True
        
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] [ORIENT] 🟢 INSTANT-HIT: Known Infrastructure Pattern Detected.")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] RCA: {state['root_cause']}")
    else:
        # 2. Hand-off: If unknown, the OODA loop continues to the Brain Agent
        state["cache_hit"] = False
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] [ORIENT] Cache Miss. Cognitive escalation required.")

    state["logs"] = logs
    return state
