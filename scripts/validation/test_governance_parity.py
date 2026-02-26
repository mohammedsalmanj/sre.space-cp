import sys
import os
from unittest.mock import MagicMock, patch

# Ensure path is correct for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from packages.agents.scout import scout_agent
from packages.agents.brain import brain_agent
from packages.agents.fixer import fixer_agent

def test_governance_parity():
    stacks = ["ec2", "eks"]
    results = []

    print("\n--- Governance Flow Parity Test ---\n")

    for stack in stacks:
        print(f"Testing Stack: {stack.upper()}")
        os.environ["STACK_TYPE"] = stack
        
        # Initial State
        state = {
            "logs": [],
            "is_anomaly": True,
            "anomaly_frequency": 1,
            "decision": "ALLOW",
            "service": "policy-service",
            "namespace": "default",
            "env": "prod",
            "confidence_score": 0.95,
            "error_spans": [],
            "root_cause": "",
            "remediation": ""
        }

        # Mock External Services
        with patch('packages.shared.github_service.GitHubService') as MockGH, \
             patch('packages.agents.brain.get_memory_collection') as MockChroma, \
             patch('packages.agents.brain.OpenAI') as MockOpenAI:
            
            # Setup mocks
            gh_instance = MockGH.return_value
            gh_instance.create_issue.return_value = {"number": 101}
            gh_instance.get_ref.return_value = {"object": {"sha": "mock-sha"}}
            gh_instance.create_ref.return_value = {}
            gh_instance.update_file.return_value = {}
            gh_instance.create_pr.return_value = {"number": 202}

            MockChroma.return_value = None # Force fallback to local/openAI logic

            # 1. Scout
            state = scout_agent(state)
            
            # 2. Brain (Issue Creation)
            state = brain_agent(state)
            
            # Check if issue was created BEFORE remediation
            issue_called = gh_instance.create_issue.called
            
            # 3. Fixer (PR Creation)
            state = fixer_agent(state)
            
            # Validation logic
            pr_called = gh_instance.create_pr.called
            
            if issue_called and pr_called:
                pr_args = gh_instance.create_pr.call_args[1]
                pr_body = pr_args.get("body", "")
                
                # Check for "Fixes #101" (Directive 2)
                has_fix_ref = "Fixes #101" in pr_body
                
                # Check for "audit_command" (Directive 2)
                has_audit = "Audit Trail" in pr_body
                
                if has_fix_ref and has_audit:
                    results.append({"stack": stack, "status": "PASS", "msg": "Governance flow intact: Issue -> Branch -> PR with audit/ref."})
                else:
                    results.append({"stack": stack, "status": "FAIL", "msg": f"Missing components in PR. Fixes ref: {has_fix_ref}, Audit: {has_audit}"})
            else:
                results.append({"stack": stack, "status": "FAIL", "msg": f"Governance chain broken. Issue: {issue_called}, PR: {pr_called}"})

    for res in results:
        status_symbol = "✅" if res['status'] == "PASS" else "❌"
        print(f"{status_symbol} {res['stack'].upper()}: {res['msg']}")

    if any(r['status'] == "FAIL" for r in results):
        sys.exit(1)
    else:
        print("\n✅ GOVERNANCE PARITY ACHIEVED.")

if __name__ == "__main__":
    test_governance_parity()
