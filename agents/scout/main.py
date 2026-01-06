import os
import asyncio
import json
import logging
from confluent_kafka import Consumer, KafkaError
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scout")

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

class ScoutMetrics:
    def __init__(self):
        self.quotes = 0
        self.purchases = 0

metrics = ScoutMetrics()

async def run_scout():
    logger.info("Scout Agent starting... Monitoring Conversion Loop.")

    if not GITHUB_TOKEN:
        logger.error("GITHUB_PERSONAL_ACCESS_TOKEN missing!")
        return

    # Kafka Setup
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'scout-agent',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(conf)
    consumer.subscribe(['quote_requested', 'policy_purchased'])

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

            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    # Periodic Check for conversion drop
                    await check_conversion(session)
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
                    
                    logger.info(f"Metrics Update: Quotes={metrics.quotes}, Purchases={metrics.purchases}")

async def check_conversion(session):
    if metrics.quotes > 10:
        rate = (metrics.purchases / metrics.quotes) * 100
        if rate < 30: # Alert if conversion is below 30%
            logger.warning(f"Conversion Drop Detected! Rate: {rate:.2f}%")
            
            # Create GitHub Incident
            await session.call_tool(
                "create_issue",
                arguments={
                    "owner": "mohammedsalmanj",
                    "repo": "sre.space-cp",
                    "title": "[INCIDENT] Low Conversion Rate in Insurance Cloud",
                    "body": f"The Scout Agent detected a conversion rate drop: **{rate:.2f}%**\n\n**Total Quotes**: {metrics.quotes}\n**Total Purchases**: {metrics.purchases}\n\nPlease analyze traces for failures in `policy-service`."
                }
            )
            # Reset metrics to avoid spamming
            metrics.quotes = 0
            metrics.purchases = 0
            await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(run_scout())
