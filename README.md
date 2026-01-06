# SRE-Space Platform

## Mission Manifest
This monorepo contains the SRE-Space platform, a 4-agent autonomous SRE team.

## Directory Structure
- `agents/scout/`: Monitoring & Anomaly Detection (OTel/New Relic).
- `agents/brain/`: RCA & Diagnosis (GPT-4o).
- `agents/memory/`: RAG Knowledge Base (ChromaDB).
- `agents/fixer/`: Autonomous Mitigation.
- `infra/`: Docker Compose and OTel Config.
- `.github/`: Issue templates and Workflows.

## Initialization

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.10+
- GitHub Personal Access Token (PAT) with `repo` scope.
- OpenAI API Key.
- New Relic License Key.

### 2. Configuration
Create a `.env` file in the root directory (or ensure these variables are set in your environment):

```bash
NEW_RELIC_LICENSE_KEY=your_nr_key
OPENAI_API_KEY=your_openai_key
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat
```

### 3. Startup
Run the mission control stack:
```bash
cd infra
docker compose -f mission-control.yml up -d --build
```

### 4. GitHub MCP Integration
To fully enable the agents to interact with GitHub:
1. Ensure the `GITHUB_PERSONAL_ACCESS_TOKEN` is valid.
2. The platform is configured to use the `mcp` python library.
3. Ensure your local environment or the agent containers have network access to GitHub.

## Workflow
1. **Scout** detects a failure and opens an issue.
2. **Brain** analyzes the issue using logs and GPT-4o, posting an RCA comment.
3. **Memory** suggests fixes based on past incidents.
4. **Fixer** restarts the service and opens a PR for config updates.
