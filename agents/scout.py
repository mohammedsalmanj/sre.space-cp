import os
import asyncio
import json
import logging
import time
import requests
from confluent_kafka import Consumer, KafkaError
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scout")

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()

# Kafka Producer for Reactive Stream
from confluent_kafka import Producer
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def broadcast_event(topic, data):
    try:
        producer.produce(topic, value=json.dumps(data))
        producer.flush()
    except Exception as e:
        logger.error(f"Failed to broadcast to {topic}: {e}")

SERVICES = {
    "policy-service": "http://policy-service:8002/health",
    "quote-service": "http://quote-service:8001/health",
    "user-service": "http://user-service:8003/health"
}

class ScoutMetrics:
    def __init__(self):
        self.quotes = 0
        self.purchases = 0

metrics = ScoutMetrics()

# --- WATCHER: LATENCY & SATURATION (Simulated via Health Endpoint) ---
async def watcher_infrastructure(session):
    while True:
        incident_triggered = False
        context = []
        for name, url in SERVICES.items():
            try:
                start = time.time()
                res = requests.get(url, timeout=2)
                duration = (time.time() - start) * 1000
                
                # Latency Check
                if duration > 1000: # 1s threshold
                    context.append(f"{name}: High Latency ({duration:.0f}ms)")
                    incident_triggered = True
                
                # Saturation/Health Check
                if res.status_code != 200:
                    context.append(f"{name}: Unhealthy (Status {res.status_code})")
                    incident_triggered = True
                    
            except Exception as e:
                context.append(f"{name}: DOWN ({str(e)})")
                incident_triggered = True
        
        if incident_triggered:
            error_summary = "; ".join(context)
            logger.warning(f"Infrastructure Incident: {error_summary}")
            await create_incident(session, "Infrastructure", error_summary, "Latency/Saturation")
            await asyncio.sleep(300) # Cooldown
            
        await asyncio.sleep(10)

# --- WATCHER: CUJ (Conversion Loop) ---
async def watcher_cuj(session):
    while True:
        # Check every 30 seconds
        if metrics.quotes > 5:
            rate = (metrics.purchases / metrics.quotes) * 100
            logger.info(f"CUJ Watcher: Conversion Rate {rate:.2f}% ({metrics.purchases}/{metrics.quotes})")
            
            if rate < 50:
                logger.warning(f"CRITICAL: Conversion Drop Detected! Rate: {rate:.2f}%")
                await create_incident(
                    session, 
                    "Business Logic", 
                    f"Conversion Rate dropped to {rate:.2f}% (Threshold: 50%).\nQuotes: {metrics.quotes}, Purchases: {metrics.purchases}",
                    "CUJ Failure"
                )
                metrics.quotes, metrics.purchases = 0, 0
                await asyncio.sleep(300)
        await asyncio.sleep(10)

async def create_incident(session, trigger_type, error_digest, category):
    # Capture snapshot of all metrics for context
    snapshot = f"""
    **Trigger**: {trigger_type}
    **Error**: {error_digest}
    **Category**: {category}
    **Current Conversion**: {(metrics.purchases/metrics.quotes*100) if metrics.quotes > 0 else 0:.1f}%
    **Timestamp**: {time.ctime()}
    """
    
    logger.info(f"Creating Incident: {trigger_type}")
    try:
        await session.call_tool(
            "create_issue",
            arguments={
                "owner": "mohammedsalmanj",
                "repo": "sre.space-cp",
                "title": f"[INCIDENT] {category}: {trigger_type} Alert",
                "body": f"## 🚨 SRE Scout Alert\n\n{snapshot}\n\n**Brain Analysis Required**"
            }
        )
        broadcast_event("incident_updates", {
            "status": "OPEN",
            "message": f"{category}: {trigger_type} Alert",
            "trigger": trigger_type,
            "timestamp": time.time()
        })
    except Exception as e:
        logger.error(f"Failed to create incident: {e}")

async def run_scout():
    logger.info("Universal Catcher (Scout v2) starting...")

    if not GITHUB_TOKEN:
        logger.error("GITHUB_PERSONAL_ACCESS_TOKEN missing!")
        return

    # Kafka Setup
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'scout-agent',
        'auto.offset.reset': 'earliest'
    }
    try:
        consumer = Consumer(conf)
        consumer.subscribe(['quote_requested', 'policy_purchased'])
    except Exception as e:
        logger.error(f"Kafka Connection Failed: {e}")
        return

    # MCP Setup
    server_params = StdioServerParameters(
        command="mcp-server-github",
        args=[],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            logger.info("Connected to GitHub MCP.")

            # Start concurrent watchers
            asyncio.create_task(watcher_infrastructure(session))
            asyncio.create_task(watcher_cuj(session))
            
            # Main Kafka Loop (Event Watcher)
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue
                if msg.error():
                    if msg.error().code() != KafkaError._PARTITION_EOF:
                        logger.error(f"Kafka Error: {msg.error()}")
                else:
                    topic = msg.topic()
                    if topic == 'quote_requested':
                        metrics.quotes += 1
                    elif topic == 'policy_purchased':
                        metrics.purchases += 1
                    logger.info(f"Event: {topic}")

if __name__ == "__main__":
    asyncio.run(run_scout())
