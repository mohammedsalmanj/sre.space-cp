import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import requests

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

def verify_stack():
    results = {}
    
    # 1. Verify ChromaDB
    print("[?] Testing ChromaDB...")
    try:
        host = os.getenv('CHROMA_DB_HOST', 'localhost')
        port = int(os.getenv('CHROMA_DB_PORT', 8000))
        client = chromadb.HttpClient(host=host, port=8000)
        client.heartbeat()
        results['ChromaDB'] = "[V] Connected"
    except Exception as e:
        results['ChromaDB'] = f"[X] Failed: {str(e)}"

    # 2. Verify OpenAI
    print("[?] Testing OpenAI Key...")
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or "your_key" in api_key:
            results['OpenAI'] = "[!] Missing Key"
        else:
            client = OpenAI(api_key=api_key)
            # Simple test call
            client.models.list()
            results['OpenAI'] = "[V] Key Valid"
    except Exception as e:
        results['OpenAI'] = f"[X] Failed: {str(e)}"

    # 3. Verify GitHub Token
    print("[?] Testing GitHub Token...")
    try:
        token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
        if not token or "your_token" in token:
            results['GitHub'] = "[!] Missing Token"
        else:
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/user", headers=headers)
            if response.status_code == 200:
                results['GitHub'] = f"[V] Valid (User: {response.json().get('login')})"
            else:
                results['GitHub'] = f"[X] Invalid (Status: {response.status_code})"
    except Exception as e:
        results['GitHub'] = f"[X] Failed: {str(e)}"

    print("\n--- SRE STACK HEALTH REPORT ---")
    for service, status in results.items():
        print(f"{service:12}: {status}")

if __name__ == "__main__":
    verify_stack()
