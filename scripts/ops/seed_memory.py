import chromadb
import os
import logging
from chromadb.utils import embedding_functions

# Config
CHROMA_DB_HOST = "localhost" # Since we run this from host
CHROMA_DB_PORT = "8000"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seeder")

def seed_db():
    try:
        # Connect to ChromaDB (exposed on localhost:8000)
        client = chromadb.HttpClient(host=CHROMA_DB_HOST, port=CHROMA_DB_PORT)
        logger.info("Connected to ChromaDB")

        # Get or Create Collection
        collection = client.get_or_create_collection(name="incidents")

        # Sample Knowledge Base (Past Incidents & SOPs)
        documents = [
            "Incident #101: Backend latency spike due to memory leak. Fix: Restarted 'scout' container and increased memory limit.",
            "Incident #102: Connection refused on port 8080. Root Cause: Firewall rule change. Fix: Updated security group.",
            "SOP-001: If 'Backend' fails health check with 500 error, restart the acting service container immediately.",
            "SOP-002: For OOMKilled errors, increase memory limits in docker-compose.yml.",
            "Incident #105: Critical Failure Detected by Scout. Root Cause: Transient network issue. Fix: Restarted monitored service."
        ]
        
        # Generate Embeddings manually
        from openai import OpenAI
        oa_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        embeddings = []
        for doc in documents:
            res = oa_client.embeddings.create(input=doc, model="text-embedding-3-small")
            embeddings.append(res.data[0].embedding)

        ids = [f"doc_{i}" for i in range(len(documents))]
        metadatas = [{"source": "postmortem"} for _ in documents]

        # Upsert
        collection.upsert(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        logger.info(f"Successfully seeded {len(documents)} documents into 'incidents' collection.")

    except Exception as e:
        logger.error(f"Failed to seed DB: {e}")

if __name__ == "__main__":
    seed_db()
