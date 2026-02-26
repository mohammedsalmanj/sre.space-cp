import sys
import os
from unittest.mock import MagicMock, patch

# Ensure path is correct for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from packages.agents.brain import brain_agent

def test_confidence_gate():
    print("\n--- Confidence Gate Enforcement Test ---\n")
    
    # 1. Simulate Low Confidence
    state = {
        "logs": [],
        "is_anomaly": True,
        "anomaly_frequency": 1,
        "decision": "ALLOW",
        "service": "policy-service",
        "namespace": "default",
        "env": "prod",
        "confidence_score": 1.0,
        "error_spans": [{"exception.message": "Critical Failure", "category": "Latency"}],
        "root_cause": "",
        "remediation": ""
    }

    os.environ["OPENAI_API_KEY"] = "sk-valid-key-for-test"

    with patch('packages.shared.github_service.GitHubService') as MockGH, \
         patch('packages.agents.brain.get_memory_collection') as MockChroma, \
         patch('packages.agents.brain.OpenAI') as MockOpenAI:
        
        gh_instance = MockGH.return_value
        gh_instance.create_issue.return_value = {"number": 505}
        
        # Force OpenAI to fail to get confidence < 0.85
        MockOpenAI.side_effect = Exception("Injected failure for testing")
        MockChroma.return_value = None
        
        # Brain should still create an issue but with "Escalated" label
        state = brain_agent(state)
        
        issue_called = gh_instance.create_issue.called
        if not issue_called:
            print("[FAIL]: Issue not created.")
            sys.exit(1)

        issue_args = gh_instance.create_issue.call_args[1]
        labels = issue_args.get("labels", [])
        
        print(f"Issue created with labels: {labels}")
        print(f"Confidence score: {state.get('confidence_score')}")
        
        # Validation
        passed_label = "Escalated" in labels
        
        if passed_label:
            print("[PASS]: 'Escalated' label applied for low confidence.")
        else:
            print("[FAIL]: 'Escalated' label missing.")
            sys.exit(1)

if __name__ == "__main__":
    test_confidence_gate()
