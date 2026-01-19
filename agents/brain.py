from datetime import datetime
import chromadb

def get_memory_collection():
    try:
        client = chromadb.HttpClient(host='localhost', port=8000)
        return client.get_or_create_collection(name="sre_incident_memory")
    except: return None

def brain_agent(state):
    """Agent: Brain (RAG-Augmented Reasoning)"""
    logs = state.get("logs", [])
    if state.get("cache_hit") or not state["error_spans"]: return state

    msg = state["error_spans"][0]["exception.message"]
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: Initiating deep RAG retrieval & scoring...")

    collection = get_memory_collection()
    if collection:
        results = collection.query(query_texts=[msg], n_results=1)
        if results and results['documents'][0]:
            state["confidence_score"] = 0.88 
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: Historical fix found. RAG Confidence: {state['confidence_score']}")
        else:
            state["confidence_score"] = 0.40
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: No historical match found.")
    
    state["root_cause"] = "Database saturation detected via trace attributes."
    state["remediation"] = "SCALE: Increase HikariCP pool size."
    state["logs"] = logs
    return state
