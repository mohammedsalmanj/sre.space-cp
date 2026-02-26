"""
File: scripts/debug/test_pinecone.py
Purpose: Verifies Pinecone connectivity and basic CRUD operations for incident memory.
"""
import os
import sys
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from packages.drivers.registry import get_vector_driver

def test_pinecone_ops():
    load_dotenv()
    print("🌲 Starting Pinecone Connectivity Test...")
    
    try:
        driver = get_vector_driver()
        print(f"✅ Driver initialized: {driver.__class__.__name__}")
        
        if driver.__class__.__name__ != "PineconeMemoryDriver":
            print("❌ Error: Expected PineconeMemoryDriver but got something else. Check .env and API key.")
            return

        # 1. Test Upsert
        print("📝 Testing Upsert...")
        success = driver.upsert_fix(
            incident_id="test-incident-999",
            root_cause="Database pool exhaustion due to leaked connections.",
            remediation="MITIGATION: RESTART policy-service",
            stack_type="ec2",
            score=0.95
        )
        
        if success:
            print("✅ Upsert successful.")
        else:
            print("❌ Upsert failed.")
            return

        # 2. Test Query
        print("🔍 Testing Query...")
        # Give Pinecone a second to ingest (usually nearly instant but for test reliability)
        import time
        time.sleep(2)
        
        results = driver.query_memory(
            query_text="Database pool exhaustion",
            stack_type="ec2",
            top_k=1
        )
        
        if results:
            print(f"✅ Query successful. Found {len(results)} matches.")
            print(f"📄 Top Match: {results[0].get('root_cause')}")
            print(f"🛠️ Remediation: {results[0].get('remediation')}")
        else:
            print("❌ Query returned no results. Data might still be indexing or query failed.")

    except Exception as e:
        print(f"💥 Unexpected Error during Pinecone test: {e}")

if __name__ == "__main__":
    test_pinecone_ops()
