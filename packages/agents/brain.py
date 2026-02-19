from datetime import datetime
import chromadb
import os
from openai import OpenAI

def get_memory_collection():
    try:
        host = os.getenv('CHROMA_DB_HOST', 'localhost')
        port = int(os.getenv('CHROMA_DB_PORT', 8000))
        client = chromadb.HttpClient(host=host, port=port)
        return client.get_or_create_collection(name="sre_incident_memory")
    except Exception as e:
        return None

def brain_agent(state):
    """Agent: Brain (RAG + OpenAI Reasoning)"""
    logs = state.get("logs", [])
    if state.get("cache_hit") or not state["error_spans"]: return state

    msg = state["error_spans"][0]["exception.message"]
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: Consulting RAG Memory for '{msg}'")

    # 1. Try RAG first (Fast/Cheap)
    collection = get_memory_collection()
    rag_hit = False
    if collection:
        try:
            results = collection.query(query_texts=[msg], n_results=1)
            if results and results['documents'] and results['documents'][0]:
                state["confidence_score"] = 0.88 
                state["root_cause"] = "Identified via historical match."
                state["remediation"] = results['metadatas'][0][0].get('solution', "Apply standard patch.")
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: RAG match found (Conf: 0.88)")
                rag_hit = True
        except:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: RAG query failed, escalating to LLM.")

    # 2. Use OpenAI Wisely (only if RAG fails or confidence is low)
    if not rag_hit:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("your_"):
            try:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: Escalating to OpenAI GPT-4o-mini for deep reasoning...")
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a specialized SRE diagnosis engine. Analyze the error and suggest a root cause and remediation."},
                        {"role": "user", "content": f"Error Message: {msg}\nService: {state.get('service')}"}
                    ],
                    max_tokens=150
                )
                analysis = response.choices[0].message.content
                state["confidence_score"] = 0.95
                state["root_cause"] = f"LLM Analysis: {analysis[:100]}..."
                state["remediation"] = "Follow LLM suggested patch (documented in logs)."
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: OpenAI Analysis Complete.")
            except Exception as e:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: OpenAI escalation failed: {str(e)}")
                state["root_cause"] = "Manual investigation required (API Failure)."
                state["remediation"] = "Manual check."
        else:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Brain: No OpenAI Key available for escalation.")
            state["root_cause"] = "Simulated: Database saturation."
            state["remediation"] = "SCALE: Increase pool size."

    state["logs"] = logs
    return state
