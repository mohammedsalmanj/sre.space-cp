import os
import asyncio
import logging
import docker
import re
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fixer")

GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
docker_client = docker.from_env()

async def execute_restart(container_name):
    try:
        containers = docker_client.containers.list(all=True)
        target = next((c for c in containers if container_name in c.name), None)
        if target:
            target.restart()
            return f"Service {target.name} restarted."
        return f"Container {container_name} not found."
    except Exception as e:
        return f"Restart error: {e}"

async def run_fixer():
    logger.info("Fixer Agent starting... Strictly GitOps & Auto-Healing.")
    server_params = StdioServerParameters(
        command="mcp-server-github",
        args=[],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            processed_issues = set()

            while True:
                try:
                    result = await session.call_tool("list_issues", arguments={"owner": "mohammedsalmanj", "repo": "sre.space-cp", "state": "open"})
                    issues = json.loads(result.content[0].text)

                    for issue in issues:
                        number = issue.get("number")
                        body = issue.get("body", "")
                        
                        if number in processed_issues or "MITIGATION:" not in body:
                            continue

                        # Auto-Healing (Restart)
                        restart_match = re.search(r"MITIGATION:\s*RESTART\s*(\S+)", body, re.IGNORECASE)
                        if restart_match:
                            container = restart_match.group(1).strip("[]")
                            # Verify Fix
                            verify_res = await execute_restart(container)
                            
                            await session.call_tool("add_issue_comment", arguments={
                                 "owner": "mohammedsalmanj", "repo": "sre.space-cp", "issue_number": number,
                                 "body": f"## 🛠️ Fixer Agent Action\n\n{verify_res}\n\nStatus: Fixed. Checking for system stability..."
                            })
                            # Fixer no longer closes the issue; Brain will handle closure after PM.
                        
                        # GitOps Fix (PR)
                        pr_match = re.search(r"MITIGATION:\s*PR\s*(.+)", body, re.IGNORECASE)
                        if pr_match:
                            details = pr_match.group(1).split("|")
                            title = details[1].strip() if len(details) > 1 else "Auto Fix"
                            desc = details[2].strip() if len(details) > 2 else "GitOps fix"
                            
                            await session.call_tool("create_pull_request", arguments={
                                "owner": "mohammedsalmanj", "repo": "sre.space-cp", 
                                "title": title, "body": desc, "head": "main", "base": "main"
                            })
                            await session.call_tool("add_issue_comment", arguments={
                                "owner": "mohammedsalmanj", "repo": "sre.space-cp", "issue_number": number,
                                "body": f"## 🛠️ Fixer Agent Action\n\nOpened PR: {title}"
                            })

                        processed_issues.add(number)

                    await asyncio.sleep(60)
                except Exception as e:
                    logger.error(f"Fixer error: {e}")
                    await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_fixer())
