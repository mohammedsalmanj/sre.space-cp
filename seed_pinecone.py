import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "")))

from packages.drivers.registry import get_vector_driver

def seed_pinecone():
    load_dotenv()
    driver = get_vector_driver()
    
    incidents = [
        {
            "id": "inc-ec2-disk-001",
            "rca": "EBS volume reached 99% utilization causing I/O lockup on EC2 instance.",
            "fix": "Execute AWS SSM command to run disk cleanup script and alert DevOps for volume expansion.",
            "stack": "ec2",
            "score": 0.95
        },
        {
            "id": "inc-k8s-crash-002",
            "rca": "Pod entering CrashLoopBackOff due to missing environment variables during rollout.",
            "fix": "Revert GitOps deployment to previous stable SHA. Restart failing Pod.",
            "stack": "kubernetes",
            "score": 0.88
        },
        {
            "id": "inc-gce-burn-003",
            "rca": "High CPU utilization (99%) on GCE instance due to rogue background process.",
            "fix": "Restart GCE instance via gcloud compute instances reset.",
            "stack": "gce",
            "score": 0.92
        },
        {
            "id": "inc-sim-mem-004",
            "rca": "Memory leak detected in application layer leading to OutOfMemoryError.",
            "fix": "Scale application tier up by 1 unit and restart affected nodes. Create investigation PR.",
            "stack": "local",
            "score": 0.85
        }
    ]
    
    try:
        if driver.__class__.__name__ != "PineconeMemoryDriver":
            print(f"Driver is {driver.__class__.__name__}. Skipping Pinecone seed.")
            return

        print(f"Seeding {len(incidents)} records into Pinecone...")
        for inc in incidents:
            driver.upsert_fix(
                incident_id=inc["id"],
                root_cause=inc["rca"],
                remediation=inc["fix"],
                stack_type=inc["stack"],
                score=inc["score"]
            )
        print("Done seeding Pinecone.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    seed_pinecone()
