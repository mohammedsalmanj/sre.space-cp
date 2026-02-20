from datetime import datetime
import random
import chromadb

def curator_agent(state):
    """Agent: Memory Curator (Memory Lifecycle)"""
    logs = state.get("logs", [])
    if state["decision"] != "ALLOW" or state["cache_hit"]: return state

    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] Incident unique. Archiving Knowledge into ChromaDB.")
    
    try:
        import os
        host = os.getenv('CHROMA_DB_HOST', 'localhost')
        port = int(os.getenv('CHROMA_DB_PORT', 8000))
        client = chromadb.HttpClient(host=host, port=port)
        collection = client.get_or_create_collection(name="sre_incident_memory")
        if collection:
            doc_id = f"inc-{random.randint(1000, 9999)}"
            collection.add(
                documents=[f"Issue: {state['root_cause']} | Fix: {state['remediation']}"],
                ids=[doc_id]
            )
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] Indexing complete ID: {doc_id}")
    except:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [CURATOR] Memory Layer unreachable.")

    state["status"] = "Stable"
    state["logs"] = logs
    return state
