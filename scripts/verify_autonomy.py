import requests
import json
import time

BASE_URL = "http://localhost:8001"

def run_test(anomaly_type):
    print(f"\n--- TESTING {anomaly_type.upper()} AUTONOMY ---")
    try:
        url = f"{BASE_URL}/api/sre-loop?anomaly=true&type={anomaly_type}"
        with requests.get(url, stream=True, timeout=30) as r:
            if r.status_code == 200:
                print(f"SRE Loop ({anomaly_type}) Started. Streaming logs:")
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

if __name__ == "__main__":
    # 1. Test Infra Autonomy (Scale)
    run_test("infra")
    
    time.sleep(2)
    
    # 2. Test Code Autonomy (PR/Merge)
    run_test("code")
