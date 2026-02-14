# Baseline Tracking System

## How the Agent Currently Knows What's Broken

### Current Approach: Hardcoded Expectations ❌

The agent currently uses **hardcoded** critical elements in `agent.py`:

```python
'criticalIds': ['count', 'increment', 'decrement', 'reset']
```

**Problems:**
- Only works for THIS specific app
- Doesn't scale to other projects
- Can't detect regressions from previous working versions
- Manual updates needed for each new feature

## Better Approach: Baseline Tracking ✅

I've created `baseline.py` which implements proper baseline tracking:

### How It Works

```
┌─────────────────┐
│  First Deploy   │  ← Capture baseline (all working features)
│   (Baseline)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  New Deploy     │  ← Compare against baseline
│   (Current)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Detect Changes │
│  - Missing IDs  │  ← Regressions = FAIL
│  - New IDs      │  ← Improvements = OK
│  - Missing JS   │  ← Critical = FAIL
└─────────────────┘
```

## Setup Instructions

### Step 1: Capture Initial Baseline

When your app is working correctly, capture it as the baseline:

```bash
cd agent-python
source venv/bin/activate
python baseline.py capture
```

This creates `baseline.json` with:
- All button IDs
- All element IDs
- JavaScript files
- CSS files
- Element counts

**Example baseline.json:**
```json
{
  "url": "https://shaiky25.github.io/demo-web-app/",
  "timestamp": "2026-02-08T17:30:00",
  "structure": {
    "buttons": [
      {"id": "increment", "text": "Increment"},
      {"id": "decrement", "text": "Decrement"},
      {"id": "reset", "text": "Reset"}
    ],
    "critical_ids": ["count", "increment", "decrement", "reset"],
    "scripts": ["app.js"],
    "stylesheets": ["style.css"]
  }
}
```

### Step 2: Test Baseline Comparison

```bash
python baseline.py
```

This compares current deployment against baseline and shows:
- ✅ What's still working
- ❌ What's missing (regressions)
- ➕ What's new (improvements)

### Step 3: Integrate with CI/CD

Update `.github/workflows/deploy-with-python-analysis.yml`:

```yaml
- name: Download Previous Baseline
  continue-on-error: true
  uses: actions/download-artifact@v4
  with:
    name: deployment-baseline
    path: agent-python/

- name: Run Deployment Analysis
  working-directory: ./agent-python
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    DEPLOYMENT_URL: ${{ needs.deploy.outputs.deployment_url }}
  run: |
    # Compare with baseline first
    python baseline.py > baseline-report.txt || true
    # Then run AI agent
    python agent.py

- name: Upload New Baseline
  if: success()
  uses: actions/upload-artifact@v4
  with:
    name: deployment-baseline
    path: agent-python/baseline.json
    retention-days: 90
```

## Usage Examples

### Example 1: Detect Missing Button

**Baseline has:**
- increment button ✅
- decrement button ✅
- reset button ✅

**New deployment missing increment:**
```json
{
  "status": "REGRESSIONS_FOUND",
  "regressions": [
    {
      "type": "MISSING_BUTTONS",
      "severity": "HIGH",
      "details": "Missing buttons: increment"
    }
  ]
}
```

### Example 2: Detect Missing JavaScript

**Baseline has:**
- app.js ✅

**New deployment missing app.js:**
```json
{
  "regressions": [
    {
      "type": "MISSING_SCRIPTS",
      "severity": "CRITICAL",
      "details": "Missing JavaScript files: app.js"
    }
  ]
}
```

### Example 3: New Feature Added

**Baseline has:**
- 3 buttons

**New deployment has:**
- 4 buttons (added "save" button)

```json
{
  "status": "HEALTHY",
  "improvements": [
    {
      "type": "NEW_BUTTONS",
      "details": "New buttons added: save"
    }
  ]
}
```

## Baseline Management

### When to Update Baseline

✅ **Update baseline when:**
- Adding new features intentionally
- Refactoring with same functionality
- After successful deployment with improvements

❌ **Don't update baseline when:**
- Tests are failing
- Regressions detected
- Deployment has issues

### Update Baseline Command

```bash
# After successful deployment
python baseline.py capture
git add baseline.json
git commit -m "Update baseline after adding new feature"
git push
```

### Multiple Baselines (Advanced)

For different environments:

```bash
# Production baseline
python baseline.py capture --file baseline-prod.json

# Staging baseline  
python baseline.py capture --file baseline-staging.json

# Compare against specific baseline
python baseline.py --baseline baseline-prod.json
```

## Integration with AI Agent

The AI agent can use baseline data to:

1. **Automatic Detection**: No hardcoded expectations needed
2. **Smart Analysis**: Understands what changed and why
3. **Better Reporting**: "Missing increment button (was present in baseline from 2026-02-08)"

### Updated Agent Tool

```python
{
  'name': 'compare_with_baseline',
  'description': 'Compare current deployment with baseline to detect regressions',
  'input_schema': {
    'type': 'object',
    'properties': {
      'current_url': {'type': 'string'},
      'baseline_file': {'type': 'string', 'default': 'baseline.json'}
    }
  }
}
```

## Benefits

### ✅ Automatic Regression Detection
- No manual configuration per project
- Detects ANY change from working version
- Works for any web app

### ✅ Historical Tracking
- Know when features were added/removed
- Track deployment history
- Audit trail of changes

### ✅ Scalable
- Works for simple apps (3 buttons)
- Works for complex apps (100+ elements)
- No code changes needed per project

### ✅ CI/CD Integration
- Baseline stored as artifact
- Automatic comparison on each deploy
- Fail deployment on regressions

## Summary

| Approach | Pros | Cons |
|----------|------|------|
| **Hardcoded** (current) | Simple, explicit | Not scalable, manual updates |
| **Baseline** (recommended) | Automatic, scalable, historical | Needs initial setup |

**Recommendation:** Use baseline tracking for production deployments. It provides automatic regression detection without manual configuration.

## Quick Start

```bash
# 1. Capture baseline from working deployment
cd agent-python
python baseline.py capture

# 2. Make changes and test
# ... edit code ...

# 3. Compare new version
python baseline.py

# 4. If good, update baseline
python baseline.py capture

# 5. Commit baseline
git add baseline.json
git commit -m "Update baseline"
```

Now your agent will automatically detect ANY regression from the working baseline! 🎉
