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
    
    Provide a Root Cause Analysis and a Recommended Fix.
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
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            logger.info("Connected to GitHub MCP.")

            processed_issues = set()

            while True:
                try:
                    # Poll for open issues
                    # Note: You might need to adjust the filter based on available tools
                    result = await session.call_tool("list_issues", arguments={"owner": "mohammedsalmanj", "repo": "sre.space-cp", "state": "open"})
                    
                    # Parse result (assuming JSON string or list)
                    # This part depends on the exact return format of the MCP tool
                    import json
                    try:
                        # The tool output is likely a text string we need to parse if it's not a dict
                        # For safety, let's assume we get a string and try to load it, or it's a list.
                        issues_data = result.content
                        if isinstance(issues_data, list):
                            # It returns a list of Content objects, usually text
                            issues_json = json.loads(issues_data[0].text)
                        else:
                            issues_json = [] 
                    except:
                        logger.warning("Could not parse issues list.")
                        issues_json = []

                    for issue in issues_json:
                        number = issue.get("number")
                        title = issue.get("title")
                        
                        if number in processed_issues:
                            continue

                        if "[INCIDENT]" in title:
                            logger.info(f"New Incident Found: #{number}")
                            
                            # Analyze
                            rca = await analyze_incident(title, issue.get("body", ""))
                            
                            # Post Comment
                            await session.call_tool(
                                "create_issue_comment", 
                                arguments={
                                    "owner": "mohammedsalmanj", 
                                    "repo": "sre.space-cp", 
                                    "issue_number": number, 
                                    "body": f"## 🧠 Brain Agent Diagnosis\n\n{rca}"
                                }
                            )
                            processed_issues.add(number)
                    
                    await asyncio.sleep(60)

                except Exception as e:
                    logger.error(f"Brain Loop Error: {e}")
                    await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(run_brain())
