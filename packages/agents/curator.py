from datetime import datetime
import random
import chromadb

def curator_agent(state):
    """
    Agent: Memory Curator (Memory Lifecycle Management)
    
    The Curator is responsible for the system's "long-term memory". 
    After a successful remediation, it takes the root cause and fix 
    and archives it into ChromaDB for future RAG-based analysis.
    """
    from packages.shared.agent_utils import add_agent_log
    
    # We only archive if the action was allowed and it's a new (non-cached) incident
    if state["decision"] != "ALLOW" or state["cache_hit"]: return state

    add_agent_log(state, "curator", "Incident unique. Archiving Knowledge into ChromaDB.")
    
    try:
        # Connect to ChromaDB memory layer
        client = chromadb.HttpClient(host='localhost', port=8000)
        collection = client.get_or_create_collection(name="sre_incident_memory")
        if collection:
            doc_id = f"inc-{random.randint(1000, 9999)}"
            # Index the technical details of the root cause and remediation
            collection.add(
                documents=[f"Issue: {state['root_cause']} | Fix: {state['remediation']}"],
                ids=[doc_id]
            )
            add_agent_log(state, "curator", f"Indexing complete ID: {doc_id}")
    except Exception as e:
        # Fail gracefully if the memory layer is down (non-critical path)
        add_agent_log(state, "curator", "Memory Layer unreachable. Skipping archiving.")

    state["status"] = "Stable"
    return state
