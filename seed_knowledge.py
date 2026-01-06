import chromadb
import os
# from openai import OpenAI # Removed OpenAI import

# Initialize OpenAI # Removed OpenAI client initialization
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB
chroma_client = chromadb.HttpClient(host="localhost", port=8000)

from openai import OpenAI
import os

# Initialize OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    api_key = api_key.strip()
client = OpenAI(api_key=api_key)

def get_embedding(text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def seed():
    # Delete if exists to avoid duplicates
    try:
        chroma_client.delete_collection("sre_knowledge")
    except:
        pass
    
    collection = chroma_client.create_collection("sre_knowledge")

    patterns = [
        {
            "id": "KB-001",
            "doc": "INCIDENT: Low Conversion Rate. ROOT CAUSE: Event delay in Kafka or Consumer lag. FIX: Check policy-service consumer group lag. RESTART: policy-service.",
            "meta": {"topic": "conversion", "service": "kafka"}
        },
        {
            "id": "KB-002",
            "doc": "INCIDENT: Quote requested but no policy created. ROOT CAUSE: Schema mismatch in Kafka headers preventing trace propagation. FIX: Ensure all producers use OTel propagator. PR: Update opentelemetry-instrumentation-fastapi version.",
            "meta": {"topic": "traces", "service": "quote-service"}
        },
        {
            "id": "KB-003",
            "doc": "INCIDENT: Policy Service 500 error. ROOT CAUSE: User service unavailable during validation. FIX: Implement circuit breaker in policy-service. PR: Add resilience4j or similar pattern.",
            "meta": {"topic": "resilience", "service": "user-service"}
        }
    ]

    ids = [p["id"] for p in patterns]
    docs = [p["doc"] for p in patterns]
    metas = [p["meta"] for p in patterns]
    embeddings = [get_embedding(p["doc"]) for p in patterns]

    collection.add(
        ids=ids,
        documents=docs,
        metadatas=metas,
        embeddings=embeddings
    )
    print(f"Successfully seeded {len(patterns)} SRE knowledge patterns into ChromaDB.")

if __name__ == "__main__":
    seed()
