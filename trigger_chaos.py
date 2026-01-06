import requests
import time
import random

BASE_URL = "http://localhost:8001" # Quote Service

def trigger_chaos():
    print("Triggering Chaos: Generating requests...")
    
    for i in range(10):
        uid = f"user-{random.randint(1, 100)}"
        print(f"[{i+1}/10] Requesting health check or simulation...")
        try:
            # The current running infra-policy-service is on port 8001
            res = requests.get(f"http://localhost:8001/health")
            print(f"   Response: {res.status_code}")
        except Exception as e:
            print(f"   Error: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    trigger_chaos()
