from datetime import datetime
import random
import chromadb
from packages.shared.sim_state import sim_state

def curator_agent(state):
    """Agent: Memory Curator (Memory Lifecycle)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW" or state["cache_hit"]: return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] [ACT] Incident Resolved. Transforming Ops-Data into Institutional Knowledge.")
    
    try:
        import os
        host = os.getenv('CHROMA_DB_HOST', 'localhost')
        port = int(os.getenv('CHROMA_DB_PORT', 8000))
        client = chromadb.HttpClient(host=host, port=port)
        collection = client.get_or_create_collection(name="sre_incident_memory")
        if collection:
            doc_id = f"PM-{datetime.now().strftime('%S%M')}"
            collection.add(
                documents=[f"RCA: {state['root_cause']} | Mitigation: {state['remediation']}"],
                metadatas=[{"solution": state['remediation']}],
                ids=[doc_id]
            )
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] [ACT] Knowledge Base Update: Post-Mortem {doc_id} archived.")
    except:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] [ACT] Warning: Knowledge Layer offline. Skipping persistence.")

    state["status"] = "Stable"
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] [ACT] Remediation Cycle Bridged Successfully. Verifying Veracity...")
    
    # Veracity Layer: Restore the ground-truth system state to Healthy
    sim_state.resolve_fix()
    
    state["logs"] = logs
    return state
