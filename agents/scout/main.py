import os
import asyncio
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scout")

# Config
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
TARGET_REPO = "mohammedsalmanj/sre.space-cp" # Adjust if dynamically needed

async def run_scout():
    logger.info("Scout Agent starting... Initializing MCP Client.")

    if not GITHUB_TOKEN:
        logger.error("GITHUB_PERSONAL_ACCESS_TOKEN is missing!")
        return

    # Connection parameters for the GitHub MCP Server
    server_params = StdioServerParameters(
        command="mcp-server-github",
        args=[],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN}
    )

    import requests
    target_url = os.getenv("TARGET_URL")
    component = "Policy Service" if target_url else "Backend"

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            logger.info("Connected to GitHub MCP Server.")

            while True:
                try:
                    logger.info(f"Checking system health at {target_url or 'Simulation'}...")
                    
                    health_ok = True
                    if target_url:
                        try:
                            resp = requests.get(target_url, timeout=5)
                            health_ok = resp.status_code == 200
                        except:
                            health_ok = False
                    else:
                        health_ok = False # Simulation

                    if not health_ok:
                        logger.warning(f"Failure detected on {component}! Creating Incident Issue...")
                        result = await session.call_tool(
                            "create_issue",
                            arguments={
                                "owner": "mohammedsalmanj",
                                "repo": "sre.space-cp",
                                "title": f"[INCIDENT] Critical Failure: {component}",
                                "body": f"Scout Agent detected a health check failure on **{component}**.\n\n**Severity**: High\n**Endpoint**: {target_url or 'N/A'}"
                            }
                        )
                        logger.info(f"Issue Created: {result.content}")
                        await asyncio.sleep(3600) 
                    else:
                        await asyncio.sleep(30)
                
                except Exception as e:
                    logger.error(f"Error in Scout loop: {e}")
                    await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_scout())
