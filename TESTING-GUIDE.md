# Testing the AI-Gated Deployment

## Current State

Your repository is ready to test the AI-gated deployment workflow. The current `index.html` has intentional issues that should trigger the AI analysis to block deployment.

## Issues in Current Code

```html
<button id="increment">Decrement</button>  <!-- ❌ Misleading: says Decrement but ID is increment -->
<button id="decrement">Decrement</button>  <!-- ❌ Duplicate: same text as above -->
```

## Expected Behavior

When you push this code, the workflow should:

1. ✅ **Static Analysis** - Pass (buttons have IDs and text)
2. ❌ **AI Analysis** - FAIL (detect ambiguous/misleading buttons)
3. ⏸️ **Approval Gate** - WAIT (require manual override)
4. ⏹️ **Deploy Production** - BLOCKED

## Test Scenarios

### Test 1: Push Current Code (Should Block)

```bash
# The current code should be blocked
git add .
git commit -m "Test: AI should block this deployment"
git push
```

**Expected Result:**
- Workflow runs
- AI detects issues
- Deployment blocked
- Comment posted with detailed reasoning

**Check:**
1. Go to Actions tab
2. Click on the workflow run
3. See `ai-analysis` job fail
4. See `approval-gate` job waiting
5. See `deploy-production` job skipped
6. Check commit comments for AI analysis report

### Test 2: Override the Block

If AI blocks deployment (as expected):

```
1. Go to Actions tab
2. Click "AI-Gated Deployment" workflow
3. Click "Run workflow" button
4. Fill in:
   ✅ Override AI analysis failures: checked
   📝 Reason: "Testing override mechanism - will fix in next commit"
5. Click "Run workflow"
```

**Expected Result:**
- Workflow runs again
- AI analysis still fails
- Approval gate passes (override)
- Deploys to production with warning
- Comment posted documenting override

### Test 3: Fix Issues and Deploy Clean

```bash
# Fix the HTML
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Web App</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>Welcome to My Web App</h1>
        <p class="subtitle">A minimal deployment demo</p>
        
        <div class="counter-section">
            <h2>Counter: <span id="count">0</span></h2>
            <div class="button-group">
                <button id="increment">Increment</button>
                <button id="decrement">Decrement</button>
                <button id="reset">Reset</button>
            </div>
        </div>
        
        <footer>
            <p>Deployed via GitHub Actions</p>
        </footer>
    </div>
    
    <script src="app.js"></script>
</body>
</html>
EOF

git add index.html
git commit -m "Fix: clarify button labels"
git push
```

**Expected Result:**
- Workflow runs
- Static analysis passes
- AI analysis passes
- Approval gate skipped (not needed)
- Deploys automatically
- Comment posted with success

## What to Look For

### In GitHub Actions UI

**Job Status:**
```
✅ static-analysis
❌ ai-analysis (if issues found)
⏸️ approval-gate (if blocked)
⏹️ deploy-production (if blocked)
```

**Job Logs:**
- `static-analysis`: See quality_checks.py output
- `ai-analysis`: See AI reasoning about UX issues
- `approval-gate`: See override status
- `deploy-production`: See deployment result

### In Commit Comments

**When Blocked:**
```markdown
🤖 AI Deployment Analysis

Status: ❌ BLOCKED
Critical/High Issues: 2

🚨 Issues Found:

AMBIGUOUS BUTTONS (HIGH)
Issue: Button with id="increment" has text "Decrement"...
Fix: Change button text to match its function

DUPLICATE LABELS (HIGH)
Issue: Two buttons both labeled "Decrement"...
Fix: Use distinct labels for different actions
```

**When Overridden:**
```markdown
⚠️ AI Analysis Override

Overridden by: @your-username
Reason: Testing override mechanism
Commit: abc123
Time: 2026-02-18T...
```

**When Passed:**
```markdown
✅ Production Deployment

Status: Deployed successfully
URL: https://your-username.github.io/your-repo/
All AI checks passed.
```

### In Artifacts

Download artifacts from workflow run:
- `quality-report`: Static analysis results
- `ai-analysis-report`: Full AI reasoning (JSON)

## Troubleshooting

### Workflow doesn't run

**Check:**
```bash
# Verify workflow file exists
ls -la .github/workflows/ai-gated-deployment.yml

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/ai-gated-deployment.yml'))"
```

### AI analysis fails to run

**Check:**
1. Go to Settings → Secrets → Actions
2. Verify `ANTHROPIC_API_KEY` exists
3. Check API key has credits at https://console.anthropic.com/

### Can't override

**Check:**
1. Go to Settings → Environments
2. Verify `production-override` environment exists
3. Check you have write permissions to repository

### Staging deployment fails

**Note:** The workflow deploys to `gh-pages-staging` branch for analysis. This is separate from your main `gh-pages` branch. If staging fails, check:

```bash
# See if staging branch exists
git ls-remote origin gh-pages-staging

# GitHub Pages settings
# Settings → Pages → ensure gh-pages is source (not gh-pages-staging)
```

## Quick Commands

### View workflow status
```bash
gh run list --workflow=ai-gated-deployment.yml
```

### View latest run logs
```bash
gh run view --log
```

### Trigger manual override
```bash
gh workflow run ai-gated-deployment.yml \
  -f override_ai_check=true \
  -f override_reason="Testing override"
```

### Download artifacts
```bash
gh run download <run-id>
```

## Next Steps

1. **Push current code** to see AI block deployment
2. **Review AI reasoning** in commit comments
3. **Test override** mechanism
4. **Fix issues** and see clean deployment
5. **Monitor** override patterns over time

## Success Criteria

✅ AI detects the ambiguous buttons
✅ Deployment is blocked
✅ Detailed reasoning is shown
✅ Override mechanism works
✅ Fixed code deploys automatically
✅ All decisions are documented

**Your AI-gated deployment is ready to test!** 🚀
