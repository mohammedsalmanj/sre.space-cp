import asyncio
import logging
import os
import docker
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brain")

# Initialize Clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

try:
    docker_client = docker.from_env()
except Exception:
    logger.warning("Docker socket not connected. Logs will be mocked.")
    docker_client = None

async def analyze_incident(title, body):
    logger.info(f"Analyzing incident: {title}")
    
    # 1. Fetch Context (Logs)
    logs = "System Check: FAILED. Error: 500 Internal Server Error in module 'Backend'. Stack trace: ..."
    if docker_client:
        try:
            # simple mock: grab logs from a random container if available
            containers = docker_client.containers.list(limit=1)
            if containers:
                logs = containers[0].logs(tail=20).decode('utf-8', errors='ignore')
        except:
            pass

    # 2. RCA with GPT-4o
    prompt = f"""
    You are the SRE Brain. Analyze this incident:
    Title: {title}
    Description: {body}
    Logs: {logs}
    
    1. Provide a concise Root Cause Analysis.
    2. Suggest a Recommended Fix.
    3. IMPORTANT: If an immediate automated mitigation is possible (e.g., restarting a container), start a line with:
       MITIGATION: RESTART [container_name]
    
    4. If a permanent code fix is identified (e.g., bump memory in YAML), start a line with:
       MITIGATION: PR [branch_name] | [title] | [body]
       (where body is the code change description).
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI Error: {e}")
        return "RCA Failed: OpenAI API Error."

async def run_brain():
    logger.info("Brain Agent starting...")
    
    if not GITHUB_TOKEN:
        logger.error("Missing GITHUB_TOKEN")
        return

    # Connect to GitHub MCP
    server_params = StdioServerParameters(
        command="mcp-server-github",
        args=[],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Log available tools for debugging
            response = await session.list_tools()
            logger.info(f"Available Tools: {[t.name for t in response.tools]}")

            processed_issues = set()

            while True:
                try:
                    # Poll for open issues
                    result = await session.call_tool("list_issues", arguments={"owner": "mohammedsalmanj", "repo": "sre.space-cp", "state": "open"})
                    
                    import json
                    try:
                        issues_json = json.loads(result.content[0].text)
                    except Exception as e:
                        logger.warning(f"Could not parse issues list: {e}")
                        issues_json = []

                    for issue in issues_json:
                        number = issue.get("number")
                        title = issue.get("title")
                        body = issue.get("body", "")
                        
                        logger.info(f"Checking Issue: #{number} - {title}")
                        
                        if number in processed_issues:
                            continue

                        # Check if already diagnosed by checking description or comments (we'll just use processed_issues for now)
                        if "[INCIDENT]" in title:
                            logger.info(f"New Incident Found: #{number}")
                            
                            # Analyze
                            rca = await analyze_incident(title, body)
                            
                            # 1. Post Comment
                            await session.call_tool(
                                "add_issue_comment", 
                                arguments={
                                    "owner": "mohammedsalmanj", 
                                    "repo": "sre.space-cp", 
                                    "issue_number": number, 
                                    "body": f"## 🧠 Brain Agent Diagnosis\n\n{rca}"
                                }
                            )

                            # 2. Update issue body to include diagnosis for Fixer agent searchability
                            new_body = f"{body}\n\n---\n## 🧠 Brain Agent Diagnosis\n\n{rca}"
                            await session.call_tool(
                                "update_issue",
                                arguments={
                                    "owner": "mohammedsalmanj",
                                    "repo": "sre.space-cp",
                                    "issue_number": number,
                                    "body": new_body
                                }
                            )

                            processed_issues.add(number)
                    
                    await asyncio.sleep(60)

                except Exception as e:
                    logger.error(f"Brain Loop Error: {e}")
                    # Exponential backoff for transient network issues
                    await asyncio.sleep(min(120, 30 * (1.5 ** (len(processed_issues) % 5))))

if __name__ == "__main__":
    asyncio.run(run_brain())
