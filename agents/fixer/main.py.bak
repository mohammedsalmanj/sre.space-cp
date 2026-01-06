import asyncio
import logging
import os
import docker
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fixer")

# Initialize Clients
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

try:
    docker_client = docker.from_env()
except Exception:
    logger.warning("Docker socket not connected. Mitigations will be mocked.")
    docker_client = None

async def execute_restart(container_name):
    logger.info(f"Attempting to restart {container_name}...")
    if not docker_client:
        return f"Mock Restart Success: {container_name}"
    
    try:
        # Find container by name (partial match)
        containers = docker_client.containers.list(all=True)
        target = next((c for c in containers if container_name in c.name), None)
        
        if target:
            target.restart()
            logger.info(f"Successfully restarted {target.name}")
            return f"Service {target.name} restarted successfully."
        else:
            return f"Container matching '{container_name}' not found."
    except Exception as e:
        logger.error(f"Restart Error: {e}")
        return f"Restart Failed: {e}"

async def run_fixer():
    logger.info("Fixer Agent starting... Ready to mitigate.")
    
    if not GITHUB_TOKEN:
        logger.error("Missing GITHUB_TOKEN")
        return

    server_params = StdioServerParameters(
        command="mcp-server-github",
        args=[],
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
                        
                        if number in processed_issues:
                            continue

                        # Check for brain diagnosis in body
                        if "[INCIDENT]" in title and "MITIGATION:" in body:
                            logger.info(f"Analyzing Brain Diagnosis for Issue #{number}")
                            brain_diagnosis = body
                            action_result = None

                            # 1. Restart Logic
                            if "MITIGATION: RESTART" in brain_diagnosis:
                                match = re.search(r"MITIGATION:\s*RESTART\s*(\S+)", brain_diagnosis, re.IGNORECASE)
                                container_to_restart = match.group(1).strip("[]").strip("'").strip("\"") if match else "scout"
                                
                                # Mapping
                                if "backend" in container_to_restart.lower() or "policy" in container_to_restart.lower():
                                    container_to_restart = "policy-service" # Specific for this demo
                                
                                action_result = await execute_restart(container_to_restart)

                            # 2. PR Logic
                            elif "MITIGATION: PR" in brain_diagnosis:
                                pr_match = re.search(r"MITIGATION:\s*PR\s*(.+)", brain_diagnosis, re.IGNORECASE)
                                if pr_match:
                                    pr_details = pr_match.group(1).split("|")
                                    pr_title = pr_details[1].strip() if len(pr_details) > 1 else f"Automated Fix for Issue #{number}"
                                    pr_body = pr_details[2].strip() if len(pr_details) > 2 else "Brain suggested code fix."
                                    
                                    try:
                                        await session.call_tool(
                                            "create_pull_request",
                                            arguments={
                                                "owner": "mohammedsalmanj",
                                                "repo": "sre.space-cp",
                                                "title": pr_title,
                                                "body": pr_body,
                                                "head": "main",
                                                "base": "main"
                                            }
                                        )
                                        action_result = f"🚀 Successfully created Pull Request: {pr_title}"
                                    except Exception as e:
                                        action_result = f"❌ Failed to create PR: {e}"

                            if action_result:
                                # Post Comment
                                await session.call_tool(
                                    "add_issue_comment", 
                                    arguments={
                                        "owner": "mohammedsalmanj", 
                                        "repo": "sre.space-cp", 
                                        "issue_number": number, 
                                        "body": f"## 🛠️ Fixer Agent Action\n\n{action_result}\n\n**Incident Status**: Resolved & Closed."
                                    }
                                )
                                # Close Issue
                                await session.call_tool(
                                    "update_issue",
                                    arguments={
                                        "owner": "mohammedsalmanj",
                                        "repo": "sre.space-cp",
                                        "issue_number": number,
                                        "state": "closed"
                                    }
                                )
                                processed_issues.add(number)
                            else:
                                # Diagnosis found but no action taken yet or unknown action
                                pass

                    await asyncio.sleep(60)

                except Exception as e:
                    logger.error(f"Fixer Loop Error: {e}")
                    await asyncio.sleep(min(120, 30 * (1.5 ** (len(processed_issues) % 5))))

if __name__ == "__main__":
    asyncio.run(run_fixer())
