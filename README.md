# AI-Protected Web App Deployment

A demonstration of AI-powered deployment quality gates using GitHub Actions and Claude AI.

## What This Is

This is a simple counter web app that showcases an advanced deployment system:

- ✅ **AI Analysis** - Claude AI reviews every deployment for UX issues
- ✅ **Quality Gates** - Blocks deployment if critical issues found
- ✅ **Detailed Reasoning** - Shows why deployment was blocked
- ✅ **Developer Override** - Allows manual approval with reason
- ✅ **Audit Trail** - Tracks all deployment decisions

## Features

### Web App
- Simple counter functionality
- Clean, responsive design
- Automatic deployment to GitHub Pages

### AI Deployment System
- **Static Analysis** - Fast scripted checks (empty buttons, missing IDs, etc.)
- **AI Reasoning** - Deep UX analysis (ambiguous labels, confusing flow, accessibility)
- **Staging Deployment** - Tests on live staging before production
- **Approval Gate** - Requires manual override if issues found
- **Feedback Loop** - Learn from AI suggestions over time

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd <your-repo>
```

### 2. Add Anthropic API Key

1. Get API key from https://console.anthropic.com/
2. Go to repository Settings → Secrets → Actions
3. Add secret: `ANTHROPIC_API_KEY` = your key

### 3. Enable GitHub Pages

1. Go to Settings → Pages
2. Set Source to "GitHub Actions"
3. Save

### 4. Create Environment

1. Go to Settings → Environments
2. Create environment: `production-override`
3. Save

### 5. Push Code

```bash
git add .
git commit -m "Initial deployment"
git push
```

The AI-gated deployment will run automatically!

## How It Works

```
┌─────────────────┐
│   Push Code     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Static Analysis │ ← quality_checks.py (2 sec)
└────────┬────────┘
         ↓
┌─────────────────┐
│  AI Analysis    │ ← ai_reasoning_checks.py (30 sec)
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
│ Manual Approve│
└───┬───────────┘
    │
    ↓
┌──────────┐
│  DEPLOY  │
└──────────┘
```

## Example: AI Catches Issues

### Bad Code (Blocked)
```html
<button id="increment">Decrement</button>  <!-- ❌ Misleading -->
<button id="decrement">Decrement</button>  <!-- ❌ Duplicate -->
```

**AI Analysis:**
```
❌ BLOCKED: MISLEADING LABEL (CRITICAL)
Button says "Decrement" but ID is "increment"
Users will be confused when it does the opposite

❌ BLOCKED: AMBIGUOUS BUTTONS (HIGH)
Two buttons both say "Decrement"
Users can't distinguish between them
```

**Result:** Deployment blocked, detailed feedback provided

### Good Code (Deployed)
```html
<button id="increment">Increment</button>  <!-- ✅ Clear -->
<button id="decrement">Decrement</button>  <!-- ✅ Distinct -->
```

**AI Analysis:**
```
✅ PASSED: No critical issues
All buttons have clear, distinct labels
Functionality matches button text
```

**Result:** Deployed automatically

## Documentation

### Quick Start
- **[QUICK-START.md](QUICK-START.md)** - Get running in 5 minutes
- **[SYSTEM-OVERVIEW.md](SYSTEM-OVERVIEW.md)** - Complete architecture diagram

### Getting Started
- **[TESTING-GUIDE.md](TESTING-GUIDE.md)** - How to test the AI-gated deployment
- **[AI-GATED-DEPLOYMENT-GUIDE.md](AI-GATED-DEPLOYMENT-GUIDE.md)** - Complete setup and usage guide

### Understanding the System
- **[AGENT-FEEDBACK-GUIDE.md](AGENT-FEEDBACK-GUIDE.md)** - How to interpret AI feedback
- **[HOW-AGENT-DETECTS-ISSUES.md](HOW-AGENT-DETECTS-ISSUES.md)** - How the AI agent works
- **[AI-VS-SCRIPTED-CHECKS.md](AI-VS-SCRIPTED-CHECKS.md)** - When to use AI vs scripted checks

### Advanced Topics
- **[WORKFLOW-COMPARISON.md](WORKFLOW-COMPARISON.md)** - Compare all available workflows
- **[DEPLOYMENT-STRATEGIES.md](DEPLOYMENT-STRATEGIES.md)** - Different deployment approaches
- **[SCALING-TO-LARGE-APPS.md](SCALING-TO-LARGE-APPS.md)** - Scale beyond simple apps
- **[BASELINE-TRACKING-GUIDE.md](BASELINE-TRACKING-GUIDE.md)** - How baseline tracking works
- **[QUALITY-DETECTION-GUIDE.md](QUALITY-DETECTION-GUIDE.md)** - Quality check details

### Troubleshooting
- **[DEPLOYMENT-FIX.md](DEPLOYMENT-FIX.md)** - Common issues and fixes

## Project Structure

```
.
├── index.html                          # Web app
├── style.css                           # Styles
├── app.js                              # JavaScript
├── .github/
│   └── workflows/
│       ├── ai-gated-deployment.yml     # Main workflow (active)
│       ├── analyze-then-deploy.yml     # Alternative (disabled)
│       └── staging-production-flow.yml # Alternative (disabled)
└── agent-python/
    ├── agent.py                        # Main agent
    ├── quality_checks.py               # Static analysis
    ├── ai_reasoning_checks.py          # AI analysis
    ├── baseline.py                     # Baseline tracking
    └── requirements.txt                # Python dependencies
```

## Local Development

### Run the Web App
```bash
# Just open in browser
open index.html
```

### Test Quality Checks
```bash
cd agent-python
pip install -r requirements.txt
python quality_checks.py
```

### Test AI Analysis
```bash
cd agent-python
export ANTHROPIC_API_KEY=your-key
export DEPLOYMENT_URL=file://$PWD/../index.html
python ai_reasoning_checks.py
```

### Run Full Agent
```bash
cd agent-python
export ANTHROPIC_API_KEY=your-key
export DEPLOYMENT_URL=https://your-username.github.io/your-repo/
python agent.py
```

## Workflows

### Active Workflow
- **ai-gated-deployment.yml** - Runs on every push, blocks if issues found

### Reference Workflows (Manual Only)
- **analyze-then-deploy.yml** - Simple static analysis before deploy
- **staging-production-flow.yml** - Multi-environment deployment

See [WORKFLOW-COMPARISON.md](WORKFLOW-COMPARISON.md) for details.

## Override Mechanism

If AI blocks deployment but you disagree:

```
1. Go to Actions tab
2. Click "AI-Gated Deployment"
3. Click "Run workflow"
4. Check "Override AI analysis failures"
5. Enter reason: "False positive - buttons are in separate sections"
6. Click "Run workflow"
```

All overrides are logged and tracked.

## What Makes This Special

### Traditional CI/CD
```
Push → Run Tests → Deploy
```
- Only catches technical errors
- Misses UX issues
- No reasoning provided

### AI-Gated Deployment
```
Push → Static Checks → AI Analysis → Deploy (if passed)
```
- Catches technical AND UX errors
- Provides detailed reasoning
- Learns from patterns
- Allows informed overrides

## Real-World Applications

This system can be adapted for:

- **E-commerce** - Catch confusing checkout flows
- **SaaS Apps** - Detect unclear onboarding
- **Admin Dashboards** - Find ambiguous actions
- **Mobile Apps** - Identify accessibility issues
- **Documentation** - Spot confusing instructions

See [SCALING-TO-LARGE-APPS.md](SCALING-TO-LARGE-APPS.md) for examples.

## Technologies Used

- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** GitHub Actions, GitHub Pages
- **AI:** Anthropic Claude 3 Haiku
- **Analysis:** Python, BeautifulSoup, Requests
- **Quality:** Custom scripted checks + AI reasoning

## Contributing

This is a demonstration project, but feel free to:
- Fork and adapt for your needs
- Suggest improvements
- Share your use cases
- Report issues

## License

MIT License - feel free to use this in your projects!

## Learn More

- [Anthropic Claude API](https://docs.anthropic.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [GitHub Pages](https://pages.github.com/)
- [Web Accessibility](https://www.w3.org/WAI/)

## Credits

Built to demonstrate AI-powered deployment quality gates.

**Key Insight:** AI can catch UX issues that scripted checks miss, but humans should make the final decision.

---

**Ready to test?** See [TESTING-GUIDE.md](TESTING-GUIDE.md) to get started! 🚀
