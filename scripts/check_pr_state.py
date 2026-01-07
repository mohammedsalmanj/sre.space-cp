import os
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    server_params = StdioServerParameters(
        command="mcp-server-github",
        args=[],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": token}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            try:
                result = await session.call_tool("get_pull_request", arguments={"owner": "mohammedsalmanj", "repo": "sre.space-cp", "pull_number": 139})
                pr = json.loads(result.content[0].text)
                print(f"PR #139 State: {pr.get('state')}, Merged: {pr.get('merged')}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
