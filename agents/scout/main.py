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
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            logger.info("Connected to GitHub MCP Server.")

            # List tools to verify connection
            tools = await session.list_tools()
            logger.info(f"Available tools: {[t.name for t in tools.tools]}")

            while True:
                try:
                    logger.info("Checking system health...")
                    # Simulating a check - in reality, query OTel Metric
                    health_ok = False # FORCE FAILURE for Demo

                    if not health_ok:
                        logger.warning("Failure detected! Creating Incident Issue...")
                        
                        # Call GitHub MCP to create issue
                        result = await session.call_tool(
                            "create_issue",
                            arguments={
                                "owner": "mohammedsalmanj",
                                "repo": "sre.space-cp",
                                "title": "[INCIDENT] Critical Failure Detected by Scout",
                                "body": "Scout Agent detected a health check failure (Simulation).\n\n**Severity**: High\n**Component**: Backend"
                            }
                        )
                        logger.info(f"Issue Created: {result.content}")
                        
                        # Wait a long time so we don't spam issues
                        await asyncio.sleep(3600) 
                    else:
                        await asyncio.sleep(30)
                
                except Exception as e:
                    logger.error(f"Error in Scout loop: {e}")
                    await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_scout())
