import os
import asyncio
import logging
import json
import re
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brain")

GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

async def analyze_incident(title, body, traces="No trace data available yet."):
    prompt = f"""
    You are the Brain Agent of SRE-Space. 
    Analyze this incident:
    Title: {title}
    Details: {body}
    Traces: {traces}

    Provide:
    1. Root Cause Analysis (RCA).
    2. Recommended Fix.
    3. MITIGATION command for the Fixer Agent:
       - MITIGATION: RESTART [container_name]
       - MITIGATION: PR [branch] | [title] | [change_description]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a senior SRE agent."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

async def run_brain():
    logger.info("Brain Agent starting...")

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
                        title = issue.get("title")
                        body = issue.get("body", "")

                        if "[INCIDENT]" in title and number not in processed_issues and "Brain Agent Diagnosis" not in body:
                            logger.info(f"Diagnosing Incident #{number}")
                            diagnosis = await analyze_incident(title, body)
                            
                            await session.call_tool("add_issue_comment", arguments={
                                "owner": "mohammedsalmanj", "repo": "sre.space-cp", "issue_number": number,
                                "body": f"## 🧠 Brain Agent Diagnosis\n\n{diagnosis}"
                            })
                            
                            new_body = f"{body}\n\n---\n## 🧠 Brain Agent Diagnosis\n\n{diagnosis}"
                            await session.call_tool("update_issue", arguments={
                                "owner": "mohammedsalmanj", "repo": "sre.space-cp", "issue_number": number, "body": new_body
                            })
                            processed_issues.add(number)

                    await asyncio.sleep(30)
                except Exception as e:
                    logger.error(f"Brain Error: {e}")
                    await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(run_brain())
