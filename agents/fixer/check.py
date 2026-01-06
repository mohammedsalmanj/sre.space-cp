import asyncio
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    token = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
    server_params = StdioServerParameters(
        command="mcp-server-github",
        args=[],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": token}
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool("list_issues", arguments={
                "owner": "mohammedsalmanj",
                "repo": "sre.space-cp",
                "state": "all"
            })
            issues = json.loads(res.content[0].text)
            for iss in issues:
                print(f"#{iss['number']} - {iss['state']} - {iss['title']}")

if __name__ == "__main__":
    asyncio.run(main())
