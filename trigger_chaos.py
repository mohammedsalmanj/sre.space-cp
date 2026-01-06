import requests
import time
import random

BASE_URL = "http://localhost:8001" # Quote Service

def trigger_chaos():
    print("[*] Triggering SRE-Space Chaos Simulation...")
    print(f"Target: {BASE_URL}")
    print("Generating 20 requests (expecting random failures for policies > $450)...")
    
    success_count = 0
    fail_count = 0

    for i in range(20):
        uid = f"user-{random.randint(1, 100)}"
        print(f"[{i+1}/20] Requesting Quote for {uid}...", end="")
        try:
            # Hit the Quote endpoint to start the event chain
            res = requests.get(f"{BASE_URL}/quote", params={"user_id": uid}, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                print(f" OK | Quote: {data.get('quote_id')} | Premium: ${data.get('premium')}")
                success_count += 1
            else:
                print(f" FAILED | Status: {res.status_code}")
                fail_count += 1
                
        except Exception as e:
            print(f" ERROR: {e}")
            fail_count += 1
        
        # Random delay to simulate real traffic
        time.sleep(random.uniform(0.5, 1.5))
        
    print("\n--- Chaos Run Complete ---")
    print(f"Requests Sent: 20")
    print(f"API Success: {success_count}")
    print(f"API Failures: {fail_count}")
    print("Check SRE Dashboard for 'policy-service' failure rates and Scout Incidents.")

if __name__ == "__main__":
    trigger_chaos()
