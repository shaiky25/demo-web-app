# How the Agent Detects Issues

## Current System: Two-Layer Detection

### Layer 1: Hardcoded Expectations (Current)

The agent has **hardcoded knowledge** of what elements should exist:

```python
# In agent.py - compare_deployments function
'criticalIds': ['count', 'increment', 'decrement', 'reset']
```

**How it works:**
1. Agent fetches the deployed site
2. Checks if these specific IDs exist
3. Reports missing ones as breaking changes

**Pros:**
- ✅ Simple and explicit
- ✅ Works immediately without setup
- ✅ Good for single-purpose apps

**Cons:**
- ❌ Only works for THIS app
- ❌ Needs code changes for each project
- ❌ Can't detect regressions from previous versions
- ❌ Doesn't know if something NEW is missing

### Layer 2: Baseline Tracking (Recommended)

The `baseline.py` system **learns** what should exist by capturing a working version:

```python
# Baseline captures EVERYTHING automatically
{
  "buttons": [
    {"id": "increment", "text": "Increment"},
    {"id": "decrement", "text": "Decrement"},
    {"id": "reset", "text": "Reset"}
  ],
  "critical_ids": ["count", "increment", "decrement", "reset"],
  "scripts": ["app.js"],
  "stylesheets": ["style.css"]
}
```

**How it works:**
1. Capture baseline from working deployment
2. On new deployment, compare against baseline
3. Report ANY differences as regressions or improvements

**Pros:**
- ✅ Works for ANY web app
- ✅ No code changes needed
- ✅ Detects ALL regressions automatically
- ✅ Tracks improvements too
- ✅ Historical tracking

**Cons:**
- ⚠️ Requires initial baseline capture
- ⚠️ Needs baseline updates when adding features

## Comparison Example

### Scenario: Missing Increment Button

**Hardcoded Approach:**
```
Agent checks: ['count', 'increment', 'decrement', 'reset']
Found: ['count', 'decrement', 'reset']
Missing: ['increment']
Result: ❌ BREAKING CHANGE
```

**Baseline Approach:**
```
Baseline had: ['count', 'increment', 'decrement', 'reset']
Current has: ['count', 'decrement', 'reset']
Regression: Missing button 'increment' (was present on 2026-02-08)
Result: ❌ REGRESSION DETECTED
```

## How to Ensure Baseline Tracking

### Step 1: Capture Baseline (One Time)

When your app is fully working:

```bash
cd agent-python
python baseline.py capture
```

This creates `baseline.json` with the current state.

### Step 2: Commit Baseline

```bash
git add baseline.json
git commit -m "Add deployment baseline"
git push
```

### Step 3: Automatic Comparison

Every deployment now compares against this baseline:

```
New Deploy → Compare with baseline.json → Report regressions
```

### Step 4: Update Baseline (When Adding Features)

After successfully adding a new feature:

```bash
# Capture new baseline
python baseline.py capture

# Commit updated baseline
git add baseline.json
git commit -m "Update baseline: added save button"
git push
```

## What Gets Tracked

### Automatically Tracked Elements

| Element Type | What's Tracked | Severity if Missing |
|--------------|----------------|---------------------|
| Buttons | ID, text, classes | HIGH |
| Inputs | ID, type, name | HIGH |
| Scripts | File paths | CRITICAL |
| Stylesheets | File paths | MEDIUM |
| All IDs | Every element with an ID | HIGH |
| Element Counts | Total buttons, inputs, forms, etc. | INFO |

### Detection Examples

**Missing Button:**
```json
{
  "type": "MISSING_BUTTONS",
  "severity": "HIGH",
  "details": "Missing buttons: increment",
  "items": ["increment"]
}
```

**Missing JavaScript:**
```json
{
  "type": "MISSING_SCRIPTS",
  "severity": "CRITICAL",
  "details": "Missing JavaScript files: app.js",
  "items": ["app.js"]
}
```

**New Feature Added:**
```json
{
  "type": "NEW_BUTTONS",
  "details": "New buttons added: save",
  "items": ["save"]
}
```

## Workflow Integration

### Local Development

```bash
# 1. Make changes
vim index.html

# 2. Test against baseline
python baseline.py

# 3. If regressions found, fix them
# 4. If new features added, update baseline
python baseline.py capture
```

### CI/CD Pipeline

```yaml
# In GitHub Actions
- name: Compare with Baseline
  run: python baseline.py
  
- name: Fail if Regressions
  run: |
    if grep -q "REGRESSIONS_FOUND" baseline-report.txt; then
      echo "❌ Regressions detected!"
      exit 1
    fi
```

## Best Practices

### ✅ DO:
- Capture baseline from a working, tested deployment
- Update baseline when intentionally adding features
- Commit baseline.json to version control
- Review baseline changes in pull requests
- Keep baseline in sync with production

### ❌ DON'T:
- Update baseline when tests are failing
- Capture baseline from broken deployments
- Ignore regression warnings
- Update baseline to "fix" failing tests
- Delete baseline.json

## Migration Path

### Current State (Hardcoded)
```
Agent → Hardcoded IDs → Check deployment → Report issues
```

### Future State (Baseline)
```
Agent → Load baseline → Compare deployment → Report regressions
```

### Migration Steps

1. **Keep hardcoded checks** as fallback
2. **Add baseline system** alongside
3. **Capture initial baseline** from production
4. **Test both systems** in parallel
5. **Switch to baseline** as primary
6. **Remove hardcoded checks** (optional)

## Summary

| Question | Answer |
|----------|--------|
| How does agent know what's broken? | Compares against baseline.json |
| What if no baseline exists? | Falls back to hardcoded checks |
| How to track previous releases? | Baseline.json is versioned in git |
| What if I add a new feature? | Update baseline after successful deploy |
| How to prevent false positives? | Only update baseline from working versions |
| Can I have multiple baselines? | Yes, one per environment (prod, staging) |

**The baseline system ensures you always compare against the last known working version, automatically detecting ANY regression without manual configuration.** 🎯
