# AI-Gated Deployment with Override

## What This Does

Your deployment is now **protected by AI analysis** with the ability to override when needed.

```
┌─────────────────┐
│   Push Code     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Static Analysis │ ← Fast checks (2 sec)
└────────┬────────┘
         ↓
┌─────────────────┐
│  AI Analysis    │ ← Deep reasoning (30 sec)
└────────┬────────┘
         ↓
    Has Issues?
         ↓
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    ↓         ↓
┌───────┐  ┌──────────┐
│ BLOCK │  │  DEPLOY  │
└───┬───┘  └──────────┘
    │
    ↓
┌───────────────┐
│ Need Override?│
└───┬───────────┘
    │
    ↓
┌───────────────┐
│ Manual Approve│ ← Developer decision
└───┬───────────┘
    │
    ↓
┌──────────┐
│  DEPLOY  │ ← With warning
└──────────┘
```

## How It Works

### Step 1: Automatic Analysis

When you push code:

1. **Static checks** run first (quality_checks.py)
   - Empty buttons
   - Missing IDs
   - Duplicate IDs
   - Technical validation

2. **AI analysis** runs second (ai_reasoning_checks.py)
   - Ambiguous labels
   - Confusing UX
   - User perspective
   - Accessibility issues

### Step 2: Decision Point

**If NO critical issues:**
- ✅ Deploys automatically
- ✅ Comment posted with success
- ✅ Users see new version

**If critical issues found:**
- ❌ Deployment BLOCKED
- 📝 Detailed report posted
- ⏸️ Waits for developer decision

### Step 3: Developer Override (Optional)

Developer can review and decide:

**Option A: Fix the issues**
```bash
# Fix the code
git add .
git commit -m "Fix: address AI analysis issues"
git push
# Triggers new analysis
```

**Option B: Override with reason**
```
1. Go to Actions tab
2. Click "AI-Gated Deployment"
3. Click "Run workflow"
4. Check "Override AI analysis failures"
5. Enter reason: "False positive - button text is intentional"
6. Click "Run workflow"
```

## Example Scenarios

### Scenario 1: Critical Issue Found

**Your code:**
```html
<button id="save-draft">Save</button>
<button id="save-publish">Save</button>
```

**AI Analysis:**
```
❌ BLOCKED: AMBIGUOUS BUTTONS (HIGH Severity)

Issue: Two buttons labeled "Save" perform different actions:
- save-draft: Saves privately
- save-publish: Publishes publicly

Users cannot distinguish between them. One misclick could 
publish content prematurely.

Fix: Use distinct labels:
- "Save Draft"
- "Publish Now"
```

**GitHub Actions:**
```
✅ static-analysis: PASSED
❌ ai-analysis: FAILED (critical issues)
⏸️ approval-gate: WAITING
⏹️ deploy-production: SKIPPED
```

**Comment on commit:**
```
🤖 AI Deployment Analysis

Status: ❌ BLOCKED
Critical/High Issues: 1

🚨 Issues Found:

AMBIGUOUS BUTTONS (HIGH)
Issue: Two buttons labeled "Save" perform different actions...
Fix: Use distinct labels like "Save Draft" and "Publish Now"

⚠️ Deployment Blocked

Options:
1. Fix the issues and push again
2. Override with manual approval
```

**What happens:**
- Deployment stops
- No code goes live
- Developer must decide

### Scenario 2: Developer Override

**Developer reviews and decides:**
> "This is a false positive. Both buttons are in different sections 
> of the page with clear context. Users won't be confused."

**Override process:**
1. Go to Actions → AI-Gated Deployment
2. Click "Run workflow"
3. Fill in:
   - ✅ Override AI analysis failures
   - Reason: "Buttons are in separate sections with clear context"
4. Click "Run workflow"

**GitHub Actions:**
```
✅ static-analysis: PASSED
⚠️ ai-analysis: FAILED (overridden)
✅ approval-gate: PASSED (manual override)
✅ deploy-production: DEPLOYED
```

**Comment on commit:**
```
⚠️ AI Analysis Override

Overridden by: @developer
Reason: Buttons are in separate sections with clear context
Commit: abc123
Time: 2026-02-14T10:30:00Z

Warning: This deployment was blocked by AI analysis but manually overridden.
Review the AI analysis report for details on the issues.
```

### Scenario 3: No Issues

**Your code:**
```html
<button id="increment">Increment</button>
<button id="decrement">Decrement</button>
<button id="reset">Reset</button>
```

**AI Analysis:**
```
✅ PASSED: No critical issues found

All buttons have clear, distinct labels.
Functionality matches button text.
No UX or accessibility issues detected.
```

**GitHub Actions:**
```
✅ static-analysis: PASSED
✅ ai-analysis: PASSED
⏭️ approval-gate: SKIPPED (not needed)
✅ deploy-production: DEPLOYED
```

**Comment on commit:**
```
✅ Production Deployment

Status: Deployed successfully
URL: https://user.github.io/repo/
Commit: abc123
Deployed by: @developer

✅ All AI checks passed.
```

## Setup Instructions

### 1. Add GitHub Environment

Create a protected environment for overrides:

1. Go to Settings → Environments
2. Click "New environment"
3. Name: `production-override`
4. Add protection rules:
   - ✅ Required reviewers (optional)
   - ✅ Wait timer: 0 minutes
5. Save

### 2. Add Anthropic API Key

1. Go to Settings → Secrets → Actions
2. Click "New repository secret"
3. Name: `ANTHROPIC_API_KEY`
4. Value: Your Anthropic API key
5. Save

### 3. Enable Workflow

```bash
# Add the new workflow
git add .github/workflows/ai-gated-deployment.yml

# Remove old workflows (optional)
git rm .github/workflows/deploy-with-python-analysis.yml

# Commit and push
git commit -m "Add AI-gated deployment with override"
git push
```

### 4. Test It

**Test 1: With issues (should block)**
```bash
# Create a file with ambiguous buttons
cat > test.html << 'EOF'
<button id="btn1">Save</button>
<button id="btn2">Save</button>
EOF

git add test.html
git commit -m "Test: ambiguous buttons"
git push

# Check Actions tab - should see BLOCKED
```

**Test 2: Override**
```
1. Go to Actions tab
2. Select "AI-Gated Deployment"
3. Click "Run workflow"
4. Check override box
5. Enter reason
6. Run

# Should deploy with warning
```

**Test 3: Fix and deploy**
```bash
# Fix the issue
cat > test.html << 'EOF'
<button id="btn1">Save Draft</button>
<button id="btn2">Publish</button>
EOF

git add test.html
git commit -m "Fix: clarify button labels"
git push

# Should deploy automatically
```

## Override Guidelines

### When to Override ✅

- False positives (AI misunderstood context)
- Intentional design decisions
- Temporary workarounds
- Time-critical hotfixes

### When NOT to Override ❌

- Real UX issues
- Accessibility violations
- User confusion risks
- "I'll fix it later" situations

### Override Best Practices

1. **Always provide a reason**
   - Explain why the AI is wrong
   - Document your decision
   - Help future developers understand

2. **Review the AI analysis carefully**
   - Don't dismiss without reading
   - Consider the user perspective
   - Think about edge cases

3. **Create a follow-up issue**
   - If overriding temporarily
   - Track technical debt
   - Plan to fix properly later

4. **Get a second opinion**
   - Ask teammate to review
   - Discuss in PR comments
   - Don't override alone for critical issues

## Monitoring Overrides

### View Override History

Check commit comments for:
```
⚠️ AI Analysis Override
```

### Track Override Rate

```bash
# Count overrides in last 30 days
gh api repos/:owner/:repo/commits \
  --jq '.[] | select(.commit.message | contains("Override"))' \
  | wc -l
```

### Review Override Reasons

Look for patterns:
- Frequent overrides = AI needs tuning
- Same reason repeated = Add exception rule
- No reason given = Improve process

## Configuration

### Adjust Severity Threshold

Edit `ai-gated-deployment.yml`:

```yaml
# Current: Block on CRITICAL or HIGH
if grep -qi "CRITICAL\|HIGH" ai-analysis.txt; then

# Stricter: Block on MEDIUM too
if grep -qi "CRITICAL\|HIGH\|MEDIUM" ai-analysis.txt; then

# Lenient: Only block on CRITICAL
if grep -qi "CRITICAL" ai-analysis.txt; then
```

### Require Multiple Approvers

In GitHub Environment settings:
```
production-override:
  required_reviewers: 2
  prevent_self_review: true
```

### Add Slack Notifications

```yaml
- name: Notify on Block
  if: needs.ai-analysis.outputs.has_critical_issues == 'true'
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -d '{"text":"🚨 Deployment blocked by AI analysis"}'
```

## Troubleshooting

### Issue: Workflow doesn't run

**Check:**
- Workflow file is in `.github/workflows/`
- YAML syntax is valid
- Branch name matches trigger

### Issue: AI analysis fails

**Check:**
- `ANTHROPIC_API_KEY` is set
- API key has credits
- Staging deployment succeeded

### Issue: Can't override

**Check:**
- Environment `production-override` exists
- You have permission to deploy
- Override reason is provided

### Issue: Override doesn't deploy

**Check:**
- Approval gate passed
- No other blocking conditions
- GitHub Pages is enabled

## Summary

### What You Get

✅ **Automatic AI analysis** on every push
✅ **Blocks deployment** if critical issues found
✅ **Detailed reasoning** in comments
✅ **Developer override** when needed
✅ **Audit trail** of all decisions
✅ **Protection** from bad deployments

### Workflow

```
Push → Analyze → Pass? → Deploy ✅
                   ↓
                  Fail
                   ↓
              Review AI report
                   ↓
            Fix or Override?
                   ↓
         ┌─────────┴─────────┐
         │                   │
        Fix                Override
         │                   │
         ↓                   ↓
    Push again          Provide reason
         │                   │
         └─────────┬─────────┘
                   ↓
                Deploy ✅
```

### Key Features

1. **AI reasoning** catches UX issues scripts miss
2. **Blocks deployment** to protect users
3. **Shows reasoning** so developers understand
4. **Allows override** for false positives
5. **Tracks decisions** for accountability

**Your deployment is now AI-protected with human oversight!** 🛡️🧠
