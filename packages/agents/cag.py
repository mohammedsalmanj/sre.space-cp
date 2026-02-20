from datetime import datetime

CAG_FAST_CACHE = {
    "HTTP 500: Database connection pool exhausted": {
        "root_cause": "System Saturation: DB Pool Exhaustion",
        "remediation": "SCALE: Increase pool size",
        "remediation_type": "infra",
        "confidence": 0.95
    },
    "HTTP 500: ZeroDivisionError in quote calculator": {
        "root_cause": "Logic Bug: Unhandled zero divisor in math module",
        "remediation": "PATCH: Add guard for zero divisor in quote_service.py",
        "remediation_type": "code",
        "confidence": 0.98
    }
}

def cag_agent(state):
    """
    Agent: CAG (Context-Aware Guide / Fast Cache)
    """
    logs = state.get("logs", [])
    if not state["error_spans"]: return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] Checking Tier-1 Fast Cache for incident FAQ...")
    msg = state["error_spans"][0]["exception.message"]
    
    # Check if the error signature exists in our pre-defined knowledge base
    if msg in CAG_FAST_CACHE:
        known = CAG_FAST_CACHE[msg]
        state["root_cause"] = known["root_cause"]
        state["remediation"] = known["remediation"]
        state["remediation_type"] = known.get("remediation_type", "other")
        state["confidence_score"] = known["confidence"]
        state["cache_hit"] = True
        
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] INSTANT-HIT. Known incident signature.")
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] Attempting to raise incident via GitHub...")
        
        # We raise a GitHub incident immediately because CAG hits are highly reliable
        try:
            from packages.shared.github_service import GitHubService
            from packages.shared.reporting import format_full_incident_report
            gh = GitHubService()
            issue_title = f"[INCIDENT] {state.get('service', 'System')} - {state['root_cause'][:50]}..."
            issue_body = format_full_incident_report(state)
            
            # Create the tracked issue on GitHub
            gh_res = gh.create_issue(title=issue_title, body=issue_body, labels=["incident", "cag-hit"])
            if "number" in gh_res:
                state["incident_number"] = gh_res["number"]
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] Incident Raised (Cache Hit) -> #{gh_res['number']}")
        except Exception as e:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] Warning: GitHub reporting failed: {str(e)}")
    else:
        # If no match is found, we set cache_hit to False so the graph routes to Brain (LLM)
        state["cache_hit"] = False
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CAG] Cache Miss. Escalating to Brain...")

    state["logs"] = logs
    return state
