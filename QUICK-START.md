# Quick Start Guide

Get your AI-gated deployment running in 5 minutes!

## Prerequisites

- GitHub repository
- Anthropic API key ([get one here](https://console.anthropic.com/))

## Setup Steps

### 1. Add API Key (1 minute)

```
1. Go to your repository on GitHub
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: ANTHROPIC_API_KEY
5. Value: your-api-key-here
6. Click "Add secret"
```

### 2. Enable GitHub Pages (30 seconds)

```
1. Go to Settings → Pages
2. Under "Build and deployment"
3. Source: GitHub Actions
4. Click "Save"
```

### 3. Create Environment (30 seconds)

```
1. Go to Settings → Environments
2. Click "New environment"
3. Name: production-override
4. Click "Configure environment"
5. Click "Save protection rules"
```

### 4. Push Code (30 seconds)

```bash
git add .
git commit -m "Setup AI-gated deployment"
git push
```

### 5. Watch It Work! (2 minutes)

```
1. Go to Actions tab
2. Click on the running workflow
3. Watch the jobs execute:
   ✅ static-analysis
   ✅ ai-analysis
   ✅ deploy-production
```

## What Happens Next

### If Code is Good ✅
```
Push → Analyze → Deploy
```
- Takes ~2 minutes
- Deploys automatically
- Comment posted with success

### If Code Has Issues ❌
```
Push → Analyze → Block → Wait for Override
```
- Takes ~1 minute to block
- Comment posted with detailed reasoning
- You decide: fix or override

## Test It

### Test 1: See AI Block Deployment

The current `index.html` has intentional issues:
```html
<button id="increment">Decrement</button>  <!-- Wrong text! -->
```

Push this code and watch AI block it:
```bash
git push
```

Check Actions tab - should see deployment blocked with reasoning.

### Test 2: Approve Override via Issue

```
1. Go to Issues tab
2. Find the auto-created issue
3. Comment: approve: Testing override mechanism
4. Wait ~30 seconds
5. Deployment proceeds
```

Should deploy with warning and issue closes.

### Test 3: Fix and Deploy Clean

```bash
# Fix the HTML
sed -i '' 's/<button id="increment">Decrement/<button id="increment">Increment/' index.html

git add index.html
git commit -m "Fix: correct button label"
git push
```

Should deploy automatically without blocking.

## Common Issues

### "Workflow not running"

**Check:**
```bash
# Verify workflow file exists
ls .github/workflows/ai-gated-deployment.yml

# Check it's valid YAML
python -c "import yaml; yaml.safe_load(open('.github/workflows/ai-gated-deployment.yml'))"
```

### "AI analysis failed"

**Check:**
1. API key is set correctly
2. API key has credits
3. Staging deployment succeeded

### "Can't override"

**Check:**
1. Environment `production-override` exists
2. You have write permissions
3. Provided override reason

## Next Steps

### Learn More
- **[TESTING-GUIDE.md](TESTING-GUIDE.md)** - Detailed testing scenarios
- **[AGENT-FEEDBACK-GUIDE.md](AGENT-FEEDBACK-GUIDE.md)** - Understanding AI feedback
- **[AI-GATED-DEPLOYMENT-GUIDE.md](AI-GATED-DEPLOYMENT-GUIDE.md)** - Complete documentation

### Customize
- Adjust severity thresholds
- Add custom quality checks
- Configure staging URL
- Add Slack notifications

### Scale Up
- See [SCALING-TO-LARGE-APPS.md](SCALING-TO-LARGE-APPS.md)
- Add component-based analysis
- Implement user flow testing
- Add performance monitoring

## Summary

✅ **5 minutes** to set up
✅ **AI protection** on every deployment
✅ **Detailed reasoning** when blocked
✅ **Override capability** when needed
✅ **Audit trail** of all decisions

**You're ready to go!** 🚀

Questions? Check the documentation or open an issue.
