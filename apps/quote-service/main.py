from fastapi import FastAPI, BackgroundTasks
import json
import os
import random
import time
from confluent_kafka import Producer
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.propagate import inject

app = FastAPI(title="SRE-Space | Quote Service")

# Kafka Config
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
producer_conf = {'bootstrap.servers': KAFKA_BROKER}
producer = Producer(producer_conf)

tracer = trace.get_tracer(__name__)

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/quote")
async def get_quote(background_tasks: BackgroundTasks, user_id: str = "guest"):
    with tracer.start_as_current_span("generate_quote") as span:
        quote_id = f"Q-{random.randint(1000, 9999)}"
        premium = random.randint(50, 500)
        
        span.set_attribute("quote.id", quote_id)
        span.set_attribute("user.id", user_id)
        
        event = {
            "quote_id": quote_id,
            "user_id": user_id,
            "premium": premium,
            "timestamp": time.time()
        }
        
        # Kafka Event with Context Propagation
        background_tasks.add_task(produce_event, event)
        
        trace_id = format(span.get_span_context().trace_id, '032x')
        return {"quote_id": quote_id, "premium": premium, "trace_id": trace_id}

@app.post("/api/v1/quote")
async def post_quote(background_tasks: BackgroundTasks, request: dict):
    with tracer.start_as_current_span("api_v1_quote") as span:
        policy_type = request.get("policy_type", "Life Insurance")
        user_id = request.get("user_id", "guest")
        
        quote_id = f"Q-{random.randint(1000, 9999)}"
        
        event = {
            "quote_id": quote_id,
            "user_id": user_id,
            "policy_type": policy_type,
            "timestamp": time.time(),
            "status": "INITIATED"
        }
        
        # Produce to mandatory topic
        producer.produce("insurance_events", key=quote_id, value=json.dumps(event))
        producer.flush()
        
        # Also trigger the legacy 'quote_requested' for backward compatibility
        background_tasks.add_task(produce_event, event)
        
        return {
            "quote_id": quote_id, 
            "status": "Quote initiated. Scout analyzing...",
            "trace_id": format(span.get_span_context().trace_id, '032x')
        }

def produce_event(event):
    headers = {}
    inject(headers) # Inject OTel context into headers
    
    # Convert headers from dict to list of tuples for confluent-kafka
    kafka_headers = [(k, str(v).encode()) for k, v in headers.items()]
    
    producer.produce(
        "quote_requested",
        key=event["quote_id"],
        value=json.dumps(event),
        headers=kafka_headers,
        callback=delivery_report
    )
    producer.flush()

FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
