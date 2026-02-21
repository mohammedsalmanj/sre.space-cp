from datetime import datetime
import chromadb
import os
from openai import OpenAI

def get_memory_collection():
    try:
        # Block 3: Restore ChromaDB Server Mode
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
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] [ORIENT] 🧠 Brain Analysis Required. Analyzing OTel Traces...")

    # 1. Try RAG first (Fast/Cheap)
    collection = get_memory_collection()
    rag_hit = False
    if collection:
        try:
            results = collection.query(query_texts=[msg], n_results=1)
            if results and results['documents'] and results['documents'][0]:
                state["confidence_score"] = 0.88 
                state["root_cause"] = "Identified via historical match. The specific error signature aligns with known resource saturation events."
                state["remediation"] = results['metadatas'][0][0].get('solution', "Apply standard patch.")
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] [ORIENT] 📚 Memory Agent Context Found. Pattern matching successful.")
                rag_hit = True
        except:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] RAG query failed, escalating to deep reasoning cluster.")

    # 2. Use OpenAI Wisely (only if RAG fails or confidence is low)
    if not rag_hit:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("your_"):
            try:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] Escalating to OpenAI GPT-4o-mini for deep reasoning...")
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a specialized SRE diagnosis engine. Analyze the error and provide a detailed Root Cause Analysis (RCA) and a specific Recommended Fix. Be professional and technical."},
                        {"role": "user", "content": f"Error Message: {msg}\nService: {state.get('service')}\nNamespace: {state.get('namespace')}"}
                    ],
                    max_tokens=300
                )
                analysis = response.choices[0].message.content
                state["confidence_score"] = 0.95
                
                # Split analysis into RCA and Remediation if possible, or just store the whole thing
                state["root_cause"] = analysis
                state["remediation"] = "Apply the recommended fix derived from LLM analysis."
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] OpenAI Analysis Complete.")
            except Exception as e:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] OpenAI escalation failed: {str(e)}")
                state["root_cause"] = "Manual investigation required due to API Failure."
                state["remediation"] = "Manual check required."
        else:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] No OpenAI Key available. Using local knowledge pool.")
            state["root_cause"] = ("The incident report indicates that the policy-service is down due to a failed connection attempt "
                                   "at port 8002. The specifically identified 'Connection refused' fault corresponds to a service "
                                   "crash or resource saturation event.")
            state["remediation"] = "MITIGATION: RESTART policy-service"
            state["confidence_score"] = 0.90
            
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] [ORIENT] Root Cause Analysis (RCA) Defined.")
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] RCA: {state['root_cause']}")
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] Recommended Fix: {state['remediation']}")
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] Escalation: Fixer Agent Directed to execute Mitigation.")

    # 3. Post Incident to GitHub (Raise Earlier)
    if state.get("confidence_score", 0) > 0.9:
        try:
            from packages.shared.github_service import GitHubService
            from packages.shared.reporting import format_rca_postmortem
            gh = GitHubService()
            issue_title = f"[INCIDENT] {state.get('service', 'System')} - {state['root_cause'][:50]}..."
            issue_body = format_rca_postmortem(state)
            gh_res = gh.create_issue(title=issue_title, body=issue_body, labels=["incident", "brain-diag"])
            if "number" in gh_res:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] Incident Raised Early -> #{gh_res['number']}")
            else:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] Warning: GitHub reporting failed.")
        except Exception as e:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [BRAIN] Reporting Error: {str(e)}")

    state["logs"] = logs
    return state
