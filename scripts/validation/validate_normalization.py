"""
File: scripts/validation/validate_normalization.py
Layer: Operations / Validation
Purpose: Verifies that all infrastructure adapters adhere to the universal telemetry schema.
Problem Solved: Ensures cognitive agents (Brain/Scout) can work across heterogeneous stacks without logic duplication.
Interaction: Probes the Infrastructure Adapter Registry and validates output against Pydantic models.
Dependencies: sys, os, pydantic, packages.infrastructure.*
Inputs: STACK_TYPE environment variables
Outputs: Summary table of schema consistency
"""
import sys
import os
import json
from pydantic import ValidationError

# Ensure monorepo root is in the lookup path for absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from packages.infrastructure.registry import registry
from packages.infrastructure.base import NormalizedTelemetry

def validate_adapters():
    """
    Core validation logic: Iterates through all supported stacks and verifies telemetry consistency.
    """
    stacks = ["ec2", "eks", "gce", "beanstalk"]
    results = []
    all_passed = True

    print("\n--- 🔹 Telemetry Normalization Parity Check ---\n")
    print(f"{'Stack':<12} | {'Status':<10} | {'Schema Match'}")
    print("-" * 45)

    for stack in stacks:
        # Load the specific stack environment
        os.environ["STACK_TYPE"] = stack
        adapter = registry.get_adapter()
        
        try:
            # Execute sensory collection
            telemetry = adapter.collect()
            
            # Pydantic handles validation during initialization (Data Integrity)
            data = telemetry.model_dump()
            required_keys = [
                "service_name", "error_rate", "latency_p95", 
                "cpu_usage", "memory_usage", "disk_usage", 
                "trace_id", "timestamp"
            ]
            
            # Explicit Schema Check
            missing = [k for k in required_keys if k not in data]
            if missing:
                results.append({"stack": stack, "status": "FAIL", "msg": f"Missing keys: {missing}"})
                all_passed = False
            else:
                results.append({"stack": stack, "status": "PASS", "msg": "Identified unified schema"})
        
        except ValidationError as e:
            results.append({"stack": stack, "status": "FAIL", "msg": f"Pydantic Validation Error: {str(e)}"})
            all_passed = False
        except Exception as e:
            results.append({"stack": stack, "status": "FAIL", "msg": f"Unexpected Error: {str(e)}"})
            all_passed = False

    # Result Presentation
    for res in results:
        print(f"{res['stack']:<12} | {res['status']:<10} | {res['msg']}")

    if not all_passed:
        print("\n❌ [FAIL] VALIDATION FAILED: Schema inconsistency detected across infrastructure adapters.")
        sys.exit(1)
    else:
        print("\n✅ [PASS] VALIDATION PASSED: All adapters are fully compliant with the universal telemetry schema.")

if __name__ == "__main__":
    validate_adapters()
