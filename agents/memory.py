import os
import asyncio
import logging
import json
import chromadb
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from shared.schemas import Incident

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memory")

CHROMA_HOST = os.getenv("CHROMA_DB_HOST", "chromadb")
CHROMA_PORT = int(os.getenv("CHROMA_DB_PORT", "8000"))
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# SRE-Space: OpenAI Embeddings (Fallback due to network)
from openai import OpenAI

# Initialize OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text):
    text = text.replace("\n", " ")
    return openai_client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

async def run_memory():
    logger.info("Memory Agent v4 starting... Autonomous Learning Loop Active.")

    # Chroma Client
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    try:
        collection = chroma_client.get_collection("sre_knowledge")
    except:
        collection = chroma_client.create_collection("sre_knowledge")
        logger.info("Created new knowledge collection.")

    server_params = StdioServerParameters(
        command="mcp-server-github",
        args=[],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN}
    )

    history_dir = "/app/shared/history"
    processed_pm_files = set()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            processed_issues = set()

            while True:
                try:
                    # PATH 1: Context Retrieval (Reactive)
                    result = await session.call_tool("list_issues", arguments={"owner": "mohammedsalmanj", "repo": "sre.space-cp", "state": "open"})
                    issues = json.loads(result.content[0].text)

                    for issue in issues:
                        number = issue.get("number")
                        title = issue.get("title")
                        body = issue.get("body", "")

                        if "[INCIDENT]" in title and number not in processed_issues and "Memory Agent Context" not in body:
                            logger.info(f"Retrieving context for Incident #{number}")
                            query_text = f"{title} {body}"
                            query_embedding = get_embedding(query_text)
                            results = collection.query(query_embeddings=[query_embedding], n_results=2)
                            context_str = "\n".join(results['documents'][0]) if results['documents'] else "No similar past incidents found."
                            
                            await session.call_tool("add_issue_comment", arguments={
                                "owner": "mohammedsalmanj", "repo": "sre.space-cp", "issue_number": number,
                                "body": f"## 📚 Memory Agent Context\n\n**Found Patterns:**\n{context_str}"
                            })
                            processed_issues.add(number)

                    # PATH 2: Autonomous Learning (Proactive)
                    if os.path.exists(history_dir):
                        for pm_file in os.listdir(history_dir):
                            if pm_file.endswith(".md") and pm_file not in processed_pm_files:
                                logger.info(f"Learning from new Post-Mortem: {pm_file}")
                                pm_path = os.path.join(history_dir, pm_file)
                                with open(pm_path, "r") as f:
                                    pm_content = f.read()
                                
                                # Extract RCA and Resolution for Knowledge Base
                                # Simplified: ingest entire PM content
                                pm_id = pm_file.replace(".md", "")
                                collection.upsert(
                                    ids=[pm_id],
                                    embeddings=[get_embedding(pm_content)],
                                    documents=[pm_content],
                                    metadatas=[{"type": "post_mortem", "file": pm_file}]
                                )
                                processed_pm_files.add(pm_file)
                                logger.info(f"Successfully learned from {pm_file}. Knowledge Base updated.")

                    await asyncio.sleep(45)
                except Exception as e:
                    logger.error(f"Memory Error: {e}")
                    await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(run_memory())
