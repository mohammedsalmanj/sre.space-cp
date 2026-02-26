import os
import sys
import subprocess
import shutil

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("="*60)
    print("      🛰️  SRE-Space - CONTROL PLANE - Setup Suite 🛰️")
    print("="*60)
    print("\n")

def check_dependencies():
    print("Step 1: Dependency Check...")
    dependencies = {
        "Docker": ["docker", "--version"],
        "Python 3.10+": ["python", "--version"], # Basic check, script is running so python exists
    }
    
    for name, cmd in dependencies.items():
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {name} detected.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {name} not found. Please install it before proceeding.")
            sys.exit(1)

def get_keys():
    print("\nStep 2: Environment Configuration...")
    openai_key = input("Enter OPENAI_API_KEY: ").strip()
    pinecone_key = input("Enter PINECONE_API_KEY: ").strip()
    return openai_key, pinecone_key

def select_mode():
    print("\nStep 3: Mode Selection")
    print("1. Testing Locally (Simulated/Sandbox)")
    print("2. Deploying to Production (Real Cloud)")
    
    choice = input("\nSelect an option (1 or 2): ").strip()
    if choice == '1':
        return "simulation"
    elif choice == '2':
        return "production"
    else:
        print("Invalid choice. Defaulting to simulation.")
        return "simulation"

def main():
    clear_screen()
    print_banner()
    check_dependencies()
    
    openai_key, pinecone_key = get_keys()
    mode = select_mode()
    
    env_content = f"""# SRE-Space generated config
OPENAI_API_KEY={openai_key}
PINECONE_API_KEY={pinecone_key}
STACK_TYPE={mode}
ENV={'local' if mode == 'simulation' else 'prod'}
VECTOR_DB_PROVIDER=pinecone
PINECONE_INDEX_NAME=sre-space-memory
PINECONE_ENVIRONMENT=us-east-1
SIMULATION_MODE={'true' if mode == 'simulation' else 'false'}
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("\n" + "="*60)
    print("✅ Configuration saved to .env")
    if mode == "simulation":
        print("🚀 Ready to test! Run 'docker-compose up -d' and open the dashboard.")
    else:
        print("🛰️  Production Mode Active. Follow the instructions in the UI 'Deploy to Prod' tab.")
    print("="*60)

if __name__ == "__main__":
    main()
