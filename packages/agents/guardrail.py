from datetime import datetime

def guardrail_agent(state):
    """Agent: Guardrail (Safety Enforcer)"""
    logs = state.get("logs", [])
    if not state["error_spans"]: return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] [DECIDE] Evaluating safety of remediation action...")
    
    if state["confidence_score"] < 0.75:
        state["decision"] = "REQUIRE_APPROVAL"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] Confidence too low ({state['confidence_score']}). Blocking auto-fix.")
    else:
        state["decision"] = "ALLOW"
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [GUARDRAIL] Action ALLOWED. Action is reversible and safe.")

    state["logs"] = logs
    return state
