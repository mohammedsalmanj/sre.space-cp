import os
import json
import time
from typing import Annotated, TypedDict, List, Dict
from langgraph.graph import StateGraph, END
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
import chromadb
from openai import OpenAI

# --- Pillar 1: LangGraph (The Cyclic Loop) ---

class SREState(TypedDict):
    incident_id: str
    current_trace_buffer: List[Dict]
    remediation_attempts: int
    memory_context: str
    status: str
    diagnosis: str
    mitigation_plan: str
    health_check: str # "Passed" or "Failed"

def scout_node(state: SREState):
    print(f"--- Scout: Detecting Anomaly for #{state['incident_id']} ---")
    # In practice, this would fetch real telemetry
    return {"status": "Anomaly Detected"}

def brain_node(state: SREState):
    print(f"--- Brain: Diagnosing #{state['incident_id']} (Attempt {state['remediation_attempts']}) ---")
    
    # OTel Instrumentation (Pillar 3)
    tracer = trace.get_tracer("sre_space.brain")
    with tracer.start_as_current_span("brain_diagnosis") as span:
        thought_process = "Analyzing trace patterns... Latency spike detected in quote-service."
        span.add_event("sre_space.diagnosis", {
            "incident_id": state['incident_id'],
            "thought": thought_process,
            "remediation_attempt": state['remediation_attempts']
        })
        
        # Simulating diagnosis logic
        diagnosis = "Potential DB Connection Pool Exhaustion"
        return {"diagnosis": diagnosis, "mitigation_plan": "Increment DB pool size"}

def fixer_node(state: SREState):
    print(f"--- Fixer: Applying Mitigation for #{state['incident_id']} ---")
    # Simulate applying a fix
    # Logic: if attempts < 2, fail health check to demonstrate the loop
    health = "Failed" if state['remediation_attempts'] < 1 else "Passed"
    return {
        "health_check": health, 
        "remediation_attempts": state['remediation_attempts'] + 1
    }

def should_retry(state: SREState):
    if state["health_check"] == "Failed" and state["remediation_attempts"] < 3:
        return "brain"
    return END

# Define Graph
workflow = StateGraph(SREState)
workflow.add_node("scout", scout_node)
workflow.add_node("brain", brain_node)
workflow.add_node("fixer", fixer_node)

workflow.set_entry_point("scout")
workflow.add_edge("scout", "brain")
workflow.add_edge("brain", "fixer")
workflow.add_conditional_edges("fixer", should_retry)

app = workflow.compile()

# --- Pillar 3: Telemetry-Injected Reasoning (OTel Snippet) ---

def instrument_brain_agent():
    """
    Example of how to inject 'thoughts' into Jaeger traces.
    """
    tracer = trace.get_tracer("sre_space.brain")
    
    def analyze_with_otel(incident_data):
        with tracer.start_as_current_span("analyze_incident") as span:
            # The 'Thought' injection
            brain_thought = "Tracing shows 504 Gateway Timeout in policy-service. Checking downstream deps."
            span.add_event("sre_space.diagnosis", {
                "reasoning": brain_thought,
                "confidence": 0.95
            })
            span.set_attribute("sre_space.rca", "Dependency Timeout")
            return "Diagnosis Complete"

# --- Pillar 4: Trace-Vector Memory (ChromaDB + RAG) ---

def flatten_trace(trace_json: Dict) -> str:
    """
    Flattens a JSON Jaeger trace into a structural string for embedding.
    """
    lines = []
    spans = trace_json.get("spans", [])
    for span in spans:
        operation = span.get("operationName", "unknown")
        duration = span.get("duration", 0) / 1000 # to ms
        tags = {t["key"]: t["value"] for t in span.get("tags", [])}
        error = tags.get("error", "false")
        lines.append(f"Span: {operation} | Duration: {duration}ms | Error: {error}")
    return "\n".join(lines)

def store_trace_vector(incident_id: str, trace_json: Dict):
    """
    Generates embedding for flattened trace and stores in ChromaDB.
    """
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="trace_vectors")
    
    flattened_text = flatten_trace(trace_json)
    # Note: Using OpenAI for real embeddings in practice
    collection.add(
        documents=[flattened_text],
        ids=[incident_id],
        metadatas=[{"incident_id": incident_id, "timestamp": time.time()}]
    )

# --- Pillar 2: Jules Architectural Guardrails (Outline) ---

"""
JULES CANARY PR VALIDATION LOGIC:

1. Agent identifies a structural refactor (e.g., Circuit Breaker).
2. Agent creates a new branch 'jules-feat-circuit-breaker'.
3. Agent generates a K6 script (load_test.js) targeting the specific microservice.
4. CI Workflow (triggered via Github Actions):
   a. Deploy PR code to a temporary 'scratch' container.
   b. Run 'k6 run load_test.js' against the scratch container.
   c. Compare P95 response times against 'main' branch baseline.
5. If Load Test passes (e.g., < 200ms P95 + 0% Errors):
   - Comment on PR with 'K6 Load Test Passed'.
   - Enable 'Human Approval' button.
6. If Load Test fails:
   - Close PR automatically or request Brain Agent to refine the fix.
   - Jules NEVER merges to main directly.
"""

if __name__ == "__main__":
    # Example execution of the graph
    initial_state = {
        "incident_id": "INC-404",
        "current_trace_buffer": [],
        "remediation_attempts": 0,
        "memory_context": "",
        "status": "Starting",
        "diagnosis": "",
        "mitigation_plan": "",
        "health_check": ""
    }
    # app.invoke(initial_state) # Skipped to avoid missing dependencies in sandbox
    print("SRE-Space Control Plane Upgrade Definitions Initialized.")
