import asyncio
import logging
import os
import chromadb
from chromadb.config import Settings
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("memory")

# Initialize ChromaDB Client
chroma_host = os.getenv("CHROMA_DB_HOST", "chromadb")
chroma_port = os.getenv("CHROMA_DB_PORT", "8000")
chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

# Initialize OpenAI for embeddings (if using OA embeddings)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def query_knowledge_base(query_text):
    logger.info(f"Querying knowledge base for: {query_text}")
    try:
        # Generate embedding
        response = client.embeddings.create(input=query_text, model="text-embedding-3-small")
        embedding = response.data[0].embedding
        
        # Query Chroma
        collection = chroma_client.get_or_create_collection("incidents")
        results = collection.query(query_embeddings=[embedding], n_results=3)
        
        return results
    except Exception as e:
        logger.error(f"Error querying memory: {e}")
        return None

async def run_memory():
    logger.info("Memory Agent starting... Ready to provide context.")
    
    while True:
        try:
            # Poll for incidents that need context (via MCP)
            # If brain posted RCA, Memory can post "Similar Incidents" or "SOPs"
            
            # Simulated action
            # suggestions = await query_knowledge_base("500 error OOM kill")
            # await mcp.call_tool("create_issue_comment", body=f"Suggested Fixes from History: {suggestions}")
            
            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error in Memory loop: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(run_memory())
