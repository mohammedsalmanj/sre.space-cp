from datetime import datetime

def jules_agent(state):
    """Agent: Jules (Hardening)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW": return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Jules: Hardening architecture (Applied Circuit Breaker).")
    state["logs"] = logs
    return state
