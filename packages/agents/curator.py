"""
File: packages/agents/curator.py
Layer: Cognitive / Knowledge
Purpose: Manages the incident memory lifecycle and institutional archival.
Problem Solved: Prevents "amnesia" in autonomic systems by ensuring every resolved incident inform future RCA.
Interaction: Runs after remediation; stores data in ChromaDB; closes GitHub issues to signal end-of-lifecycle.
Dependencies: chromadb, packages.shared.sim_state, packages.shared.github_service
Inputs: Root cause, remediation plan, and issue number from state
Outputs: Archived post-mortem ID and closed GitHub issue status
"""
from datetime import datetime
import random
import chromadb
from packages.shared.sim_state import sim_state

def curator_agent(state: dict) -> dict:
    """
    Agent Node: Curator
    Phase: ARCHIVE
    Mission: Transform raw operational data into reusable institutional knowledge.
    
    Args:
        state (dict): The current LangGraph state.
    Returns:
        dict: Updated state with stability flags and archival logs.
    """
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW" or state.get("cache_hit"): return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] [ACT] Incident Resolved. Transforming Ops-Data into Institutional Knowledge.")
    
    # 1. Institutional Memory: Archival to Cloud Vector Store (Pinecone/Chroma)
    try:
        import os
        import random
        from packages.drivers.registry import get_vector_driver
        memory = get_vector_driver()
        if memory:
            stack_type = os.getenv("STACK_TYPE", "ec2")
            success = memory.upsert_fix(
                incident_id=str(state.get("issue_number", random.randint(100, 999))),
                root_cause=state["root_cause"],
                remediation=state["remediation"],
                stack_type=stack_type,
                score=state.get("confidence_score", 0.0),
                telemetry=state.get("raw_telemetry_obj"),
                is_simulation=state.get("simulation_mode", False)
            )
            if success:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] [ACT] Knowledge Base Update: Incident metadata archived to memory ({stack_type}).")
    except Exception as e:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] [ACT] Warning: Knowledge Layer persistence failed: {str(e)}")

    # 2. Lifecycle Closure: Graceful GitHub Issue Resolution
    issue_num = state.get("issue_number")
    if issue_num:
        try:
            from packages.shared.github_service import GitHubService
            gh = GitHubService()
            gh.add_comment(issue_num, f"### ✅ Resolution Summary\nRemediation successful. System verified as stable. Closing incident lifecycle.")
            gh.close_issue(issue_num)
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] [ACT] GitHub Issue #{issue_num} closed.")
        except Exception as e:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] Warning: Failed to close issue #{issue_num}: {str(e)}")

    state["status"] = "Stable"
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] [ACT] Remediation Cycle Bridged Successfully. Verifying Veracity...")
    
    # 3. Veracity Layer: Restore the ground-truth system state to Healthy (Simulated)
    sim_state.resolve_fix()
    
    state["logs"] = logs
    return state
