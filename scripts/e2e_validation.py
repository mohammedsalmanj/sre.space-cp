import requests
import time
import sys
import os

# Configuration
API_URL = os.getenv("SRE_API_URL", "http://localhost:8001")
GITHUB_REPO = "mohammedsalmanj/sre.space-cp"

def validate_e2e():
    print("🚀 Starting SRE-Space E2E Validation...")
    
    # 1. Check System Health
    print("🔍 Step 1: Checking System Health...")
    try:
        res = requests.get(f"{API_URL}/system/health")
        res.raise_for_status()
        health = res.json()
        print(f"✅ System Healthy. Mode: {health['mode']}, Bus: {health['event_bus']}")
    except Exception as e:
        print(f"❌ System Health Check Failed: {e}")
        sys.exit(1)

    # 2. Inject Failure
    print("🔍 Step 2: Injecting Deterministic Failure (500)...")
    try:
        res = requests.post(f"{API_URL}/demo/inject-failure?type=500")
        res.raise_for_status()
        print("✅ Failure Injected.")
    except Exception as e:
        print(f"❌ Failure Injection Failed: {e}")
        sys.exit(1)

    # 3. Monitor Recovery Loop
    print("🔍 Step 3: Monitoring Autonomous Recovery Loop...")
    # We will poll the Git Activity until we see a new PR or Issue
    max_retries = 30
    found_pr = False
    found_merge = False
    
    for i in range(max_retries):
        try:
            res = requests.get(f"{API_URL}/api/git-activity")
            activity = res.json()
            
            # Look for recent auto-fix activity
            for item in activity:
                if "[AUTO-FIX]" in item["title"] or "PR" in item["title"]:
                    if item["state"] == "open":
                        found_pr = True
                        print(f"⏳ Detected Open PR/Issue: #{item['number']} - {item['title']}")
                    elif item["state"] == "closed" or item["state"] == "merged":
                        found_merge = True
                        print(f"✅ Detected Merged/Closed PR: #{item['number']}")
                        break
            
            if found_merge:
                break
        except Exception as e:
            print(f"⚠️ Polling warning: {e}")
            
        time.sleep(5)
        print(f"  ({i+1}/{max_retries}) Waiting for GitOps completion...")

    if not found_merge:
        print("❌ E2E Timeout: Recovery loop did not complete within 150 seconds.")
        sys.exit(1)

    print("\n" + "="*40)
    print("🎉 E2E PASS: System Autonomous loop verified.")
    print("="*40)

if __name__ == "__main__":
    validate_e2e()
