import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

def test_connectivity():
    print("Testing OpenAI...")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    print(f"DEBUG: Key ends with: {api_key[-10:] if api_key else 'None'}")
    if not api_key:
        print("Error: OPENAI_API_KEY is empty")
        return
    
    client = OpenAI(api_key=api_key)
    try:
        models = client.models.list()
        print(f"OpenAI OK: Found {len(models.data)} models")
    except Exception as e:
        print(f"OpenAI Failed: {e}")

    print("\nTesting ChromaDB...")
    try:
        chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        collections = chroma_client.list_collections()
        print(f"ChromaDB OK: {len(collections)} collections found")
    except Exception as e:
        print(f"ChromaDB Failed: {e}")

if __name__ == "__main__":
    test_connectivity()
