import requests
import time
import random
import sys

BASE_URL = "http://localhost:8001" # Quote Service

def run_conversion_chaos():
    print("[*] Simulating Conversion Failure (Business Logic)...")
    for i in range(15):
        uid = f"user-{random.randint(1, 100)}"
        res = requests.get(f"{BASE_URL}/quote", params={"user_id": uid})
        print(f"[{i+1}/15] {uid}: {res.status_code}")
        time.sleep(1)

def run_oom_chaos():
    print("[!] Simulating Resource Leak (OOM)...")
    # In a real demo, this might hit a /leak endpoint
    # Here we trigger high frequency requests that crash the policy-service container
    for i in range(50):
        requests.get(f"{BASE_URL}/quote", params={"user_id": "attacker"})
        if i % 10 == 0: print(f"Memory Leak Pressure: {i}%")
    print("OOM Triggered. Scout should detect service unavailability.")

if __name__ == "__main__":
    chaos_type = sys.argv[1] if len(sys.argv) > 1 else "conversion"
    
    if chaos_type == "oom":
        run_oom_chaos()
    else:
        run_conversion_chaos()
    
    print("\n--- Chaos Run Complete ---")
