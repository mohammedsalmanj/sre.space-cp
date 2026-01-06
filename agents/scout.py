import os
import asyncio
import json
import logging
import time
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

import requests

SERVICES = {
    "policy-service": "http://policy-service:8002/health",
    "quote-service": "http://quote-service:8001/health",
    "user-service": "http://user-service:8003/health"
}

async def check_service_health(session):
    for name, url in SERVICES.items():
        try:
            res = requests.get(url, timeout=2)
            if res.status_code != 200:
                logger.warning(f"CRITICAL: {name} is UNHEALTHY (Status: {res.status_code})")
                await create_health_incident(session, name, f"Status Code: {res.status_code}")
        except Exception as e:
            logger.error(f"CRITICAL: {name} is DOWN (Error: {e})")
            await create_health_incident(session, name, str(e))

async def create_health_incident(session, service, error):
    await session.call_tool(
        "create_issue",
        arguments={
            "owner": "mohammedsalmanj",
            "repo": "sre.space-cp",
            "title": f"[INCIDENT] Service Down: {service}",
            "body": f"The Scout Agent detected that `{service}` is unavailable or unhealthy.\n\n"
                    f"**Error**: {error}\n"
                    f"**Timestamp**: {time.ctime()}\n\n"
                    f"**Possible Cause**: Resource Leak (OOM), Network Partition, or Process Crash.\n"
                    f"Brain Agent please diagnose and trigger RESTART if necessary."
        }
    )
    logger.info(f"Health Incident Created for {service}.")
    await asyncio.sleep(60) # Cooldown

async def check_conversion(session):
    await check_service_health(session) # Mix in health checks
    if metrics.quotes > 5:
        rate = (metrics.purchases / metrics.quotes) * 100
        logger.info(f"Checking Conversion Health: {rate:.2f}% ({metrics.purchases}/{metrics.quotes})")
        
        if rate < 50:
            logger.warning(f"CRITICAL: Conversion Drop Detected! Rate: {rate:.2f}%")
            await session.call_tool(
                "create_issue",
                arguments={
                    "owner": "mohammedsalmanj",
                    "repo": "sre.space-cp",
                    "title": f"[INCIDENT] SRE-Space Conversion Drop: {rate:.2f}%",
                    "body": f"The Scout Agent detected a business logic failure in the Insurance Cloud.\n\n"
                            f"**Metric**: Conversion Rate (Quotes -> Purchases)\n"
                            f"**Current Rate**: {rate:.2f}%\n"
                            f"**Threshold**: 50.00%\n\n"
                            f"Possible Root Causes: Latency in `policy-service`, Kafka consumer lag, or `user-service` validation errors."
                }
            )
            metrics.quotes, metrics.purchases = 0, 0
            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(run_scout())
