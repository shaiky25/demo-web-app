# Deployment Analyzer Agent (Python)

An AI agent built with Anthropic's Claude that automatically analyzes web deployments and identifies breaking changes.

## Features

The agent includes 4 specialized tools:

1. **check_deployed_site** - Fetches and analyzes HTML structure, scripts, and styles
2. **test_javascript_functionality** - Tests if critical elements and event handlers exist
3. **compare_deployments** - Compares deployments to identify breaking changes
4. **check_common_issues** - Checks for missing files, broken links, and common problems

## Setup

1. Create a virtual environment:
```bash
cd agent-python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
```

Edit `.env` and add:
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `DEPLOYMENT_URL` - Your GitHub Pages URL

## Usage

Run the agent:
```bash
python agent.py
```

The agent will analyze your deployment and report:
- Missing critical elements
- Broken JavaScript functionality
- CSS/styling issues
- Potential breaking changes

## Integration with CI/CD

Update your GitHub workflow to use Python:

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Install Dependencies
  working-directory: ./agent-python
  run: pip install -r requirements.txt

- name: Run Deployment Analysis
  working-directory: ./agent-python
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    DEPLOYMENT_URL: ${{ needs.deploy.outputs.deployment_url }}
  run: python agent.py
```

## What It Detects

- Missing buttons or interactive elements
- JavaScript files not loading
- CSS files not loading
- Broken element IDs (count, increment, decrement, reset)
- CORS or resource loading issues
- Structural changes that break functionality
