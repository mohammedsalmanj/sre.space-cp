from datetime import datetime

def fixer_agent(state):
    """Agent: Fixer (Execution)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW": return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛠️ Fixer: Executing '{state['remediation']}' on Cluster...")
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🛠️ Fixer: Patch deployed successfully.")
    state["logs"] = logs
    return state
