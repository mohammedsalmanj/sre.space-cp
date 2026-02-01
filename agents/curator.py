from datetime import datetime
import random
from agents.brain import get_memory_collection

def curator_agent(state):
    """Agent: Memory Curator (Memory Lifecycle)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW" or state["cache_hit"]:
        return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧹 Curator: Incident unique. 📚 Archiving Knowledge into ChromaDB.")
    
    try:
        collection = get_memory_collection()
        if collection:
            doc_id = f"inc-{random.randint(1000, 9999)}"
            collection.add(
                documents=[f"Issue: {state['root_cause']} | Fix: {state['remediation']}"],
                ids=[doc_id]
            )
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧹 Curator: Indexing complete ID: {doc_id}")
    except Exception:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧹 Curator: Memory Layer unreachable.")

    state["status"] = "Stable"
    state["logs"] = logs
    return state
