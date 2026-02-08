# Deployment Analyzer Agent

An AI agent built with Strands framework that automatically analyzes web deployments and identifies breaking changes.

## Features

The agent includes 4 specialized tools:

1. **check_deployed_site** - Fetches and analyzes HTML structure, scripts, and styles
2. **test_javascript_functionality** - Tests if critical elements and event handlers exist
3. **compare_deployments** - Compares deployments to identify breaking changes
4. **check_common_issues** - Checks for missing files, broken links, and common problems

## Setup

1. Install dependencies:
```bash
cd agent
npm install
```

2. Configure credentials:

Copy `.env.example` to `.env` and add your credentials:

```bash
cp .env.example .env
```

For Anthropic Claude (configured):
- Set `ANTHROPIC_API_KEY` with your Anthropic API key
- Uses Claude 3.5 Sonnet model

3. Set your deployment URL in `.env`:
```
DEPLOYMENT_URL=https://your-username.github.io/your-repo/
```

## Usage

Run the agent:
```bash
npm start
```

The agent will analyze your deployment and report:
- Missing critical elements
- Broken JavaScript functionality
- CSS/styling issues
- Potential breaking changes

## Integration with CI/CD

Add this to your GitHub workflow to run automatically on deployment:

```yaml
- name: Analyze Deployment
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    AWS_REGION: us-east-1
    DEPLOYMENT_URL: ${{ steps.deployment.outputs.page_url }}
  run: |
    cd agent
    npm install
    npm start
```

## What It Detects

- Missing buttons or interactive elements
- JavaScript files not loading
- CSS files not loading
- Broken element IDs (count, increment, decrement, reset)
- CORS or resource loading issues
- Structural changes that break functionality
