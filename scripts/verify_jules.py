import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from packages.agents.jules import jules_agent
from dotenv import load_dotenv

load_dotenv()

def test_jules():
    print("--- TESTING JULES AGENT (STANDALONE) ---")
    try:
        # Run Jules manually
        logs = jules_agent()
        print("\nJules Execution Logs:")
        for log in logs:
            print(f"  {log}")
        
        print("\n✅ Jules execution complete. Check your GitHub repository for a new '[DAILY-REVIEW]' issue.")
    except Exception as e:
        print(f"❌ Jules failed: {e}")

if __name__ == "__main__":
    test_jules()
