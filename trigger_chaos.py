import requests
import time
import random

BASE_URL = "http://localhost:8001" # Quote Service

def trigger_chaos():
    print("🚀 Triggering SRE-Space Chaos: Generating High-Premium Quotes (Policy will fail)...")
    
    for i in range(20):
        # We target high-premium quotes to trigger the simulated failure in Policy Service
        # User ID is randomized
        uid = f"user-{random.randint(1, 100)}"
        print(f"[{i+1}/20] Requesting quote for {uid}...")
        try:
            res = requests.get(f"{BASE_URL}/quote?user_id={uid}")
            data = res.json()
            print(f"   Response: {data}")
        except Exception as e:
            print(f"   Error: {e}")
        
        time.sleep(1)

    print("\n✅ Chaos Loop Finished. Wait for Scout Agent to detect conversion drop.")

if __name__ == "__main__":
    trigger_chaos()
