import asyncio
import logging
import os
import docker
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brain")

# Initialize Docker Client
try:
    docker_client = docker.from_env()
except Exception as e:
    logger.warning(f"Could not connect to Docker: {e}")
    docker_client = None

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analyze_incident(issue_id, issue_body):
    logger.info(f"Analyzing incident {issue_id}...")
    
    logs = ""
    if docker_client:
        # Fetch logs from a target container (e.g., the failing app)
        # For demo, we list containers or just grab tail of all
        try:
            containers = docker_client.containers.list()
            for c in containers:
                logs += f"--- Logs from {c.name} ---\n"
                logs += c.logs(tail=50).decode('utf-8', errors='ignore') + "\n"
        except Exception as e:
            logs = f"Error fetching logs: {e}"
    
    # RCA with GPT-4o
    prompt = f"Analyze the following incident and logs to find the Root Cause.\nIssue: {issue_body}\nLogs:\n{logs}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a Site Reliability Engineer responsible for performing Root Cause Analysis."},
                      {"role": "user", "content": prompt}]
        )
        rca = response.choices[0].message.content
        logger.info("RCA generated.")
        return rca
    except Exception as e:
        logger.error(f"OpenAI analysis failed: {e}")
        return "Could not perform RCA due to error."

async def run_brain():
    logger.info("Brain Agent starting... Listening for new incidents.")
    
    while True:
        try:
            # Poll for new issues via MCP (Mock/TODO)
            # issues = await mcp.call_tool("get_issues", state="open")
            # For each issue, check if already analyzed.
            
            # Simulated trigger
            # await analyze_incident(123, "App crashing with 500")
            # await mcp.call_tool("create_issue_comment", issue_number=123, body=rca)
            
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error in Brain loop: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(run_brain())
