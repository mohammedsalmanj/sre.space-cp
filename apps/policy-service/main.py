import json
import os
import time
from confluent_kafka import Consumer, Producer, KafkaError
from opentelemetry import trace
from opentelemetry.propagate import extract, inject
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI

app = FastAPI(title="SRE-Space | Policy Service")

# Kafka Config
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'policy-service-group',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(conf)
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

tracer = trace.get_tracer(__name__)

async def process_messages():
    consumer.subscribe(['quote_requested'])
    logger.info("Policy Service consuming 'quote_requested'...")

    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error(): continue

        # Extract OTel context from Kafka headers
        headers = dict((k, v.decode()) for k, v in (msg.headers() or []))
        ctx = extract(headers)

        with tracer.start_as_current_span("purchase_policy", context=ctx) as span:
            data = json.loads(msg.value().decode())
            quote_id = data.get("quote_id")
            user_id = data.get("user_id", "guest")
            
            # Call User Service to fetch profile (Distributed Trace Step #3)
            try:
                with tracer.start_as_current_span("call_user_service"):
                    user_res = requests.get(f"http://user-service:8003/user/{user_id}", timeout=2)
                    user_profile = user_res.json()
                    logger.info(f"Fetched user profile: {user_profile}")
            except Exception as e:
                logger.warning(f"Failed to fetch user profile: {e}")

            # Simulate processing
            time.sleep(0.5)
            
            # Chance of failure for demo
            if os.getenv("FAILURE_MODE") == "crash" or data.get("premium", 0) > 450:
                 span.set_status(trace.Status(trace.StatusCode.ERROR))
                 logger.error(f"High premium policy failed: {quote_id}")
                 continue

            purchase_event = {
                "policy_id": f"P-{quote_id}",
                "quote_id": quote_id,
                "status": "active"
            }

            # Produce Success Event
            out_headers = {}
            inject(out_headers)
            kafka_out_headers = [(k, str(v).encode()) for k, v in out_headers.items()]
            
            producer.produce(
                "policy_purchased",
                value=json.dumps(purchase_event),
                headers=kafka_out_headers
            )
            producer.flush()
            logger.info(f"Policy Purchased: {purchase_event['policy_id']}")

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("policy-service")

@app.on_event("startup")
async def startup_event():
    import asyncio
    asyncio.create_task(process_messages())

@app.get("/health")
async def health():
    return {"status": "healthy"}

FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
