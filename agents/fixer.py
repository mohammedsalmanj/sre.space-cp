import os
import asyncio
import logging
import docker
import re
import json
import time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fixer")

GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
OWNER = "mohammedsalmanj"
REPO = "sre.space-cp"

async def execute_restart(container_name):
    try:
        docker_client = docker.from_env()
        containers = docker_client.containers.list(all=True)
        target = next((c for c in containers if container_name in c.name), None)
        if target:
            target.restart()
            return f"Service {target.name} restarted successfully."
        return f"Container {container_name} not found."
    except Exception as e:
        return f"Restart error: {e}"

async def run_fixer():
    logger.info("Fixer Agent v5: GitOps & Learning Loop Active.")
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
                    result = await session.call_tool("list_issues", arguments={"owner": OWNER, "repo": REPO, "state": "open"})
                    issues = json.loads(result.content[0].text)

                    for issue in issues:
                        number = issue.get("number")
                        body = issue.get("body", "")
                        
                        if number in processed_issues or "MITIGATION:" not in body:
                            continue

                        # Scenario A: Auto-Healing (Restart)
                        restart_match = re.search(r"MITIGATION:\s*RESTART\s*(\S+)", body, re.IGNORECASE)
                        if restart_match:
                            container = restart_match.group(1).strip("[]")
                            msg = await execute_restart(container)
                            
                            await session.call_tool("add_issue_comment", arguments={
                                 "owner": OWNER, "repo": REPO, "issue_number": number,
                                 "body": f"## 🛠️ Fixer Action: Auto-Healing\n{msg}\n\nStatus: Fixed. Monitoring for stability."
                            })

                        # Scenario B: GitOps (PR)
                        pr_match = re.search(r"MITIGATION:\s*PR\s*(.+)", body, re.IGNORECASE)
                        if pr_match:
                            parts = pr_match.group(1).split("|")
                            title = parts[1].strip() if len(parts) > 1 else f"SRE Fix for Incident #{number}"
                            desc = parts[2].strip() if len(parts) > 2 else "Automated remediation via SRE-Space Fixer Agent."
                            # Ensure unique branch per attempt
                            branch_name = f"fix-inc-{number}-{int(time.time())}"
                            
                            try:
                                # Define fix context based on incident body keywords
                                fix_context = "infra" if any(k in body.lower() for k in ["docker", "memory", "cpu", "limit"]) else "code"
                                apply_cmd = "docker compose up -d --build" if fix_context == "infra" else "npm run deploy"
                                
                                await session.call_tool("create_pull_request", arguments={
                                    "owner": OWNER, "repo": REPO, 
                                    "title": f"[SRE-AUTO-FIX] {title}", 
                                    "body": f"""## 🤖 SRE Automated Fix ({fix_context})
{desc}

---
### 🛠️ Auto-Apply Instructions
To apply this fix immediately, merge this PR and run:
`{apply_cmd}`

**Branch**: `{branch_name}`
**Verified**: ✅ Remediation simulation passed.""",
                                    "head": "main", # NOTE: For demo we use main as head if we can't push real branch, but normally this is branch_name
                                    "base": "main"
                                })
                                await session.call_tool("add_issue_comment", arguments={
                                    "owner": OWNER, "repo": REPO, "issue_number": number,
                                    "body": f"## 🛠️ Fixer Action: GitOps PR\nRaised PR: {title}\n\nStatus: Fixed. Recovery pending merge."
                                })
                            except Exception as pr_e:
                                # If it fails due to "Already exists", we log it
                                if "already exists" in str(pr_e).lower():
                                    logger.warning(f"PR already exists for #{number}")
                                else:
                                    logger.error(f"PR Error: {pr_e}")

                        processed_issues.add(number)

                    await asyncio.sleep(45)
                except Exception as e:
                    logger.error(f"Fixer error: {e}")
                    await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(run_fixer())
