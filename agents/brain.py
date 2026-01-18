from openai import OpenAI
import os
import asyncio
import logging
import json
import time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from shared.schemas import Incident

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brain")

GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

client = OpenAI(api_key=OPENAI_API_KEY)

async def generate_post_mortem(title, body, issue_number):
    prompt = f"""
    You are the Brain Agent of SRE-Space. A fix has been verified for the following incident.
    Write a professional SRE Post-Mortem in Markdown.
    
    Incident Title: {title}
    Full Incident Logs: {body}
    
    STRICTLY ATTRIBUTE ACTIONS TO AI AGENTS (Autonomous Resolution):
    - Scout Agent: Detected the anomaly (provide timestamp).
    - Brain Agent: Performed Deep Span Analysis, identified Root Cause, and instructed Fixer.
    - Fixer Agent: Executed the automated mitigation (PR or Restart).
    - Memory Agent: Indexed this event for future pattern matching.

    Do NOT use phrases like "The team investigated", "On-call engineers", or "Manual intervention".
    This was a 100% AI-driven resolution.
    
    Use this structure:
    # Incident Post-Mortem: PM-{issue_number}
    ## Incident Summary
    ## Detailed Timeline (Autonomous Execution)
    ## Root Cause (AI Analysis)
    ## Resolution (Auto-Healing)
    ## Lessons Learned (Knowledge Base Update)
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are the AI Brain Agent of SRE-Space. You write detailed post-mortems for incidents resolved entirely by AI agents. NEVER mention human SREs/teams."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

async def analyze_incident(title, body, traces="No trace data available yet."):
    incident_obj = Incident(
        id=str(int(time.time())),
        title=title,
        description=body,
        severity="High",
        status="Investigating",
        service="InsuranceCloud"
    )
    
    prompt = f"""
    You are the Brain Agent of SRE-Space. 
    Analyze this incident object:
    {incident_obj.to_dict()}
    
    Traces: {traces}

    DEEP SPAN ANALYSIS:
    - If traces indicate a 'db_query' > 500ms, it is a Database/Latency issue.
    - If traces indicate a 'http_request' timeout, it is a Service Crash/Resource Limit.
    - If traces show high volume, it might be OOM/Saturation.

    Provide:
    1. Root Cause Analysis (RCA).
    2. Recommended Fix.
    3. MITIGATION command for the Fixer Agent:
       - MITIGATION: RESTART [container_name] (For Crashes, OOM, Leaks)
       - MITIGATION: PR [branch] | [title] | [change_description] (For Config, Limits, Latency tuning)
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a senior SRE agent focus on cost-efficient diagnosis."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

async def run_brain():
    logger.info("Brain Agent v4 starting... Learning Loop Active.")

    server_params = StdioServerParameters(
        command="mcp-server-github",
        args=[],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            while True:
                try:
                    result = await session.call_tool("list_issues", arguments={"owner": "mohammedsalmanj", "repo": "sre.space-cp", "state": "open"})
                    issues = json.loads(result.content[0].text)

                    for issue in issues:
                        number = issue.get("number")
                        title = issue.get("title")
                        body = issue.get("body", "")

                        # Scenario 1: New Incident Diagnosis
                        if "[INCIDENT]" in title and "Brain Agent Diagnosis" not in body:
                            logger.info(f"Diagnosing Incident #{number}")
                            diagnosis = await analyze_incident(title, body)
                            await session.call_tool("add_issue_comment", arguments={
                                "owner": "mohammedsalmanj", "repo": "sre.space-cp", "issue_number": number,
                                "body": f"## 🧠 Brain Agent Diagnosis\n\n{diagnosis}"
                            })
                            # Append to body to mark as diagnosed (mental state)
                            new_body = f"{body}\n\n---\n## 🧠 Brain Agent Diagnosis\n\n{diagnosis}"
                            await session.call_tool("update_issue", arguments={
                                "owner": "mohammedsalmanj", "repo": "sre.space-cp", "issue_number": number, "body": new_body
                            })

                        # Scenario 2: Detect Recovery (Signal from Fixer via Label)
                        labels = [l["name"] for l in issue.get("labels", [])]
                        is_fixed = "Status: Fixed" in labels
                        
                        if is_fixed:
                            logger.info(f"🚀 RECOVERY DETECTED for #{number}. Initiating Learning Loop...")
                            
                            # Extract potential Trace ID from body if exists, or just provide a search link
                            trace_link = f"http://localhost:16686/search?service=quote-service"
                            pm_content = await generate_post_mortem(title, f"{body}\n\nObservability: {trace_link}", number)
                            
                            # Save to persistent history for Memory Agent (Auto-Learning)
                            history_path = f"/app/shared/history/PM-{time.strftime('%Y%m%d')}-{number}.md"
                            os.makedirs(os.path.dirname(history_path), exist_ok=True)
                            with open(history_path, "w") as f:
                                f.write(pm_content)
                            
                            # Post final report and close via MCP
                            await session.call_tool("add_issue_comment", arguments={
                                "owner": "mohammedsalmanj", "repo": "sre.space-cp", "issue_number": number,
                                "body": f"## 📝 AUTOMATED POST-MORTEM\n\n{pm_content}\n\n---\n**🔍 Trace Analysis**: [View in Jaeger]({trace_link})\n**Status: AI-Resolved**"
                            })
                            
                            await session.call_tool("update_issue", arguments={
                                "owner": "mohammedsalmanj", "repo": "sre.space-cp", "issue_number": number, 
                                "state": "closed",
                                "labels": ["Status: AI-Resolved", "Learning: Indexed"]
                            })
                            logger.info(f"✅ Learning Loop Complete for Incident #{number}.")

                    await asyncio.sleep(30)
                except Exception as e:
                    logger.error(f"Brain Error: {e}", exc_info=True)
                    await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(run_brain())
