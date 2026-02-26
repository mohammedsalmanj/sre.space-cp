import requests
import json
import time

BASE_URL = "http://localhost:8001"

print("--- 1. Triggering Chaos (Simulation) ---")
try:
    # Trigger error
    res = requests.get(f"{BASE_URL}/quote", params={"user_id": "attacker"}, timeout=5)
    print(f"Chaos Response: {res.status_code}") # Expect 500
except requests.exceptions.RequestException as e:
    print(f"Chaos check failed (could be expected if server crashed): {e}")

print("\n--- 2. Running SRE Loop ---")
try:
    with requests.get(f"{BASE_URL}/api/sre-loop", params={"anomaly": "true"}, stream=True, timeout=30) as r:
        if r.status_code == 200:
            print("SRE Loop Started. Streaming logs:")
            for line in r.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: "):
                        data = json.loads(decoded[6:])
                        print(f"  [LOG] {data.get('message')}")
                        if "final_state" in data:
                            print(f"\nFinal State: {data['final_state']}")
        else:
            print(f"Failed to start loop: {r.status_code}")
except Exception as e:
    print(f"Error running loop: {e}")
