import asyncio
import logging
import os
import chromadb
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memory")

# Config
CHROMADB_HOST = os.getenv("CHROMA_DB_HOST", "chromadb")
CHROMADB_PORT = os.getenv("CHROMA_DB_PORT", "8000")
GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

# Initialize Clients
try:
    chroma_client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    logger.info(f"Connected to ChromaDB at {CHROMADB_HOST}:{CHROMADB_PORT}")
except Exception as e:
    logger.error(f"Failed to connect to ChromaDB: {e}")
    chroma_client = None

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def query_knowledge_base(query_text):
    if not chroma_client:
        return "Memory Offline."
        
    logger.info(f"Querying knowledge base for: {query_text}")
    try:
        # Generate embedding
        response = openai_client.embeddings.create(input=query_text, model="text-embedding-3-small")
        embedding = response.data[0].embedding
        
        # Query Chroma
        collection = chroma_client.get_or_create_collection("incidents")
        results = collection.query(query_embeddings=[embedding], n_results=2)
        
        if not results['documents'] or not results['documents'][0]:
            return "No similar past incidents found."
            
        kb_text = "\n".join([str(doc) for doc in results['documents'][0]])
        return f"Found similar past incidents:\n{kb_text}"
    except Exception as e:
        logger.error(f"Error querying memory: {e}")
        return f"Error querying memory: {e}"

async def run_memory():
    logger.info("Memory Agent starting...")

    if not GITHUB_TOKEN:
        logger.error("Missing GITHUB_TOKEN")
        return

    # Connect to GitHub MCP
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
                    
                    issues_json = []
                    try:
                       if isinstance(result.content, list):
                            issues_json = json.loads(result.content[0].text)
                    except:
                        pass

                    for issue in issues_json:
                        number = issue.get("number")
                        title = issue.get("title")
                        
                        if number in processed_issues:
                            continue

                        # Memory acts if Brain has already diagnosed (look for brain comment) OR just generally on Incidents
                        # For simplicity, let's have Memory post initial context on any NEW Incident
                        if "[INCIDENT]" in title:
                            logger.info(f"Processing Incident #{number} for Memory Context")
                            
                            # Query Memory
                            memory_context = await query_knowledge_base(title + " " + issue.get("body", ""))
                            
                            # Post Comment
                            await session.call_tool(
                                "add_issue_comment", 
                                arguments={
                                    "owner": "mohammedsalmanj", 
                                    "repo": "sre.space-cp", 
                                    "issue_number": number, 
                                    "body": f"## 📚 Memory Agent Context\n\n{memory_context}"
                                }
                            )
                            processed_issues.add(number)
                    
                    await asyncio.sleep(60)

                except Exception as e:
                    logger.error(f"Memory Loop Error: {e}")
                    await asyncio.sleep(min(120, 30 * (1.5 ** (len(processed_issues) % 5))))

if __name__ == "__main__":
    asyncio.run(run_memory())
