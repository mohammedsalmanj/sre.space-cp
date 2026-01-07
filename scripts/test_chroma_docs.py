import requests
import sys

try:
    resp = requests.get("http://chromadb:8000/docs", timeout=5)
    print(f"Status: {resp.status_code}")
    # print(f"Body: {resp.text[:100]}") 
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
