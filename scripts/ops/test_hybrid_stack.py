import sys
import os

# Ensure path is correct for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from packages.infrastructure_adapters.registry import registry

def test_hybrid_simulation():
    print("\n--- Hybrid Stack Simulation ---\n")
    
    # Simulate EC2 failure
    os.environ["STACK_TYPE"] = "ec2"
    adapter_ec2 = registry.get_adapter()
    telemetry_ec2 = adapter_ec2.collect()
    print(f"EC2 Adapter Service: {telemetry_ec2.service_name}")
    
    # Simulate K8s failure
    os.environ["STACK_TYPE"] = "eks"
    adapter_k8s = registry.get_adapter()
    telemetry_k8s = adapter_k8s.collect()
    print(f"K8s Adapter Service: {telemetry_k8s.service_name}")
    
    # Validation
    if "ec2" in telemetry_ec2.service_name and "k8s" in telemetry_k8s.service_name:
        print("[PASS]: Correct adapters loaded for different stack types in same runtime.")
    else:
        print("[FAIL]: Adapter cross-contamination or incorrect loading.")
        sys.exit(1)

if __name__ == "__main__":
    test_hybrid_simulation()
