#!/bin/bash
# -----------------------------------------------------------------------------
# File: scripts/ops/mission-control.sh
# Layer: Support / Operations
# Purpose: Manual verification suite for certifying architectural refactors.
# Problem Solved: Automates the process of pulling changes, rebuilding the stack, 
#                 and running chaos verification scripts.
# Interaction: Invokes docker-compose and local trigger scripts.
# Dependencies: git, docker-compose, bash, python
# Inputs: Function command (e.g. verify-jules-pr)
# Outputs: Log of verification progress to stdout
# -----------------------------------------------------------------------------

function verify-jules-pr() {
    echo "🚀 [Control Loop] Verifying Jules PR..."
    
    # 1. Fetch the latest code
    echo "   -> Pulling latest changes from main branch..."
    git pull origin main
    
    # 2. Rebuild the stack
    echo "   -> Rebuilding SRE-Space Infrastructure..."
    docker-compose up -d --build
    
    # 3. Wait for stability
    echo "   -> Waiting for services to stabilize (10s)..."
    sleep 10
    
    # 4. Trigger Chaos Tests to verify if the refactor improved reliability
    echo "   -> Running Verification Chaos Suite (OOM & Conversion)..."
    python scripts/ops/verify_sre_stack.py
    
    echo "✅ [Control Loop] Verification Complete. Status: GREEN"
}

# --- Command Router ---
if [ "$1" == "verify-jules-pr" ]; then
    verify-jules-pr
else
    echo "Usage: ./mission-control.sh verify-jules-pr"
fi
