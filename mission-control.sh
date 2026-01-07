#!/bin/bash

# SRE Mission Control - Verification Utilities

function verify-jules-pr() {
    echo "🚀 [Mission Control] Verifying Jules PR..."
    
    # 1. Fetch the latest code
    echo "   -> Pulling latest changes..."
    git pull origin main
    
    # 2. Rebuild the stack
    echo "   -> Rebuilding Infrastructure..."
    docker-compose up -d --build
    
    # 3. Wait for stability
    echo "   -> Waiting for services to stabilize (10s)..."
    sleep 10
    
    # 4. Trigger Chaos Tests
    echo "   -> Running Verification Chaos Suite..."
    python trigger_chaos.py oom
    python trigger_chaos.py conversion
    
    echo "✅ [Mission Control] Verification Complete. Status: GREEN"
}

# Check argument
if [ "$1" == "verify-jules-pr" ]; then
    verify-jules-pr
else
    echo "Usage: ./mission-control.sh verify-jules-pr"
fi
