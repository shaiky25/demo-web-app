#!/usr/bin/env python3
"""
AI-Powered Reasoning Checks
These go beyond scripted rules to understand context and UX issues
"""
import json
from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup
import os


def ai_ux_analysis(url: str, anthropic_api_key: str):
    """
    Use AI to analyze UX issues that scripted checks can't catch
    """
    # Fetch the page
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract page structure for AI analysis
    page_context = {
        "title": soup.title.string if soup.title else "",
        "buttons": [
            {
                "id": btn.get('id', 'no-id'),
                "text": btn.get_text(strip=True),
                "classes": btn.get('class', []),
                "aria_label": btn.get('aria-label', ''),
                "context": str(btn.parent)[:200]  # Parent element for context
            }
            for btn in soup.find_all('button')
        ],
        "inputs": [
            {
                "id": inp.get('id', 'no-id'),
                "type": inp.get('type', 'text'),
                "placeholder": inp.get('placeholder', ''),
                "label": find_label_for_input(soup, inp)
            }
            for inp in soup.find_all('input')
        ],
        "headings": [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])],
        "page_structure": get_page_structure(soup)
    }
    
    # Ask AI to analyze UX issues
    client = Anthropic(api_key=anthropic_api_key)
    
    prompt = f"""You are a UX expert analyzing a web page for usability issues.

Page Context:
{json.dumps(page_context, indent=2)}

Analyze this page and identify UX issues that would confuse users, including:

1. AMBIGUOUS BUTTONS: Multiple buttons with the same or similar text that do different things
   - Example: Two "Save" buttons where one saves draft and one publishes
   - Users won't know which to click

2. UNCLEAR LABELS: Button/input text that doesn't clearly indicate what it does
   - Example: "Submit" button without context of what's being submitted
   - Example: "OK" vs "Confirm Payment"

3. MISSING CONTEXT: Interactive elements without sufficient surrounding context
   - Example: A "Delete" button without indicating what will be deleted

4. CONFUSING GROUPING: Related actions not grouped together or unrelated actions grouped
   - Example: "Save" and "Cancel" buttons far apart
   - Example: "Login" button in the middle of unrelated content

5. INCONSISTENT PATTERNS: Similar actions with different labels
   - Example: "Remove" in one place, "Delete" in another for same action

6. ACCESSIBILITY ISSUES: Elements that screen readers can't properly announce
   - Example: Icon-only buttons without aria-labels

For each issue found, provide:
- Type of issue
- Severity (CRITICAL, HIGH, MEDIUM, LOW)
- Specific elements involved
- Why it's confusing for users
- Suggested fix

Return your analysis as a JSON array of issues."""

    response = client.messages.create(
        model='claude-3-haiku-20240307',
        max_tokens=4096,
        messages=[{
            'role': 'user',
            'content': prompt
        }]
    )
    
    # Parse AI response
    ai_analysis = response.content[0].text
    
    # Try to extract JSON from response
    try:
        # Find JSON in the response
        start = ai_analysis.find('[')
        end = ai_analysis.rfind(']') + 1
        if start != -1 and end > start:
            issues = json.loads(ai_analysis[start:end])
        else:
            # If no JSON, create structured response from text
            issues = [{
                "type": "AI_ANALYSIS",
                "severity": "INFO",
                "analysis": ai_analysis
            }]
    except:
        issues = [{
            "type": "AI_ANALYSIS",
            "severity": "INFO",
            "analysis": ai_analysis
        }]
    
    return {
        "status": "ANALYZED",
        "page_context": page_context,
        "ai_insights": issues,
        "raw_analysis": ai_analysis
    }


def ai_functional_reasoning(url: str, anthropic_api_key: str):
    """
    Use AI to understand if the page functionality makes sense
    """
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get page content
    page_html = soup.prettify()[:5000]  # First 5000 chars
    
    client = Anthropic(api_key=anthropic_api_key)
    
    prompt = f"""You are analyzing a web application for logical consistency and user experience.

Page HTML (excerpt):
{page_html}

Analyze this page and identify issues where:

1. FUNCTIONALITY DOESN'T MATCH LABELS
   - Button says "Save" but might do something else
   - Form says "Login" but has registration fields

2. MISSING CRITICAL FUNCTIONALITY
   - Counter app without increment button
   - Shopping cart without checkout button
   - Form without submit button

3. ILLOGICAL FLOW
   - "Next" button before filling required fields
   - "Confirm" without showing what's being confirmed

4. CONTRADICTORY ELEMENTS
   - "Read-only" field with an edit button
   - "Disabled" state but still clickable

5. INCOMPLETE FEATURES
   - Search box without search button
   - Filter options without apply button

Think like a user trying to accomplish a task. What would confuse or frustrate them?

Return specific, actionable issues with severity levels."""

    response = client.messages.create(
        model='claude-3-haiku-20240307',
        max_tokens=2048,
        messages=[{
            'role': 'user',
            'content': prompt
        }]
    )
    
    return {
        "status": "ANALYZED",
        "functional_analysis": response.content[0].text
    }


def ai_compare_with_baseline(current_url: str, baseline_data: dict, anthropic_api_key: str):
    """
    Use AI to understand if changes make sense
    """
    # Fetch current page
    response = requests.get(current_url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    current_buttons = [
        {
            "id": btn.get('id', 'no-id'),
            "text": btn.get_text(strip=True)
        }
        for btn in soup.find_all('button')
    ]
    
    baseline_buttons = baseline_data.get('structure', {}).get('buttons', [])
    
    client = Anthropic(api_key=anthropic_api_key)
    
    prompt = f"""You are analyzing changes between two versions of a web application.

BASELINE (Previous Working Version):
Buttons: {json.dumps(baseline_buttons, indent=2)}

CURRENT (New Version):
Buttons: {json.dumps(current_buttons, indent=2)}

Analyze the changes and identify:

1. REMOVED FUNCTIONALITY
   - Buttons that existed before but are gone now
   - Impact on users who relied on that feature

2. CHANGED BEHAVIOR
   - Buttons with same ID but different text (might confuse users)
   - Buttons with same text but different IDs (might break bookmarks/scripts)

3. AMBIGUOUS ADDITIONS
   - New buttons with unclear purpose
   - New buttons that duplicate existing functionality

4. UX REGRESSIONS
   - Changes that make the app harder to use
   - Changes that remove clarity

For each issue, explain:
- What changed
- Why it might be a problem
- Impact on users
- Suggested fix

Be specific about which buttons and what the user experience impact is."""

    response = client.messages.create(
        model='claude-3-haiku-20240307',
        max_tokens=2048,
        messages=[{
            'role': 'user',
            'content': prompt
        }]
    )
    
    return {
        "status": "COMPARED",
        "baseline_buttons": baseline_buttons,
        "current_buttons": current_buttons,
        "ai_insights": response.content[0].text
    }


def find_label_for_input(soup, input_elem):
    """Find label associated with input"""
    input_id = input_elem.get('id')
    if input_id:
        label = soup.find('label', attrs={'for': input_id})
        if label:
            return label.get_text(strip=True)
    return None


def get_page_structure(soup):
    """Get high-level page structure"""
    return {
        "has_header": bool(soup.find(['header', 'nav'])),
        "has_footer": bool(soup.find('footer')),
        "has_main": bool(soup.find('main')),
        "form_count": len(soup.find_all('form')),
        "button_count": len(soup.find_all('button')),
        "link_count": len(soup.find_all('a'))
    }


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    url = os.getenv('DEPLOYMENT_URL', 'https://your-username.github.io/your-repo/')
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set")
        exit(1)
    
    print("🧠 Running AI-Powered UX Analysis...\n")
    
    # Run UX analysis
    ux_result = ai_ux_analysis(url, api_key)
    print("=" * 60)
    print("UX ANALYSIS")
    print("=" * 60)
    print(json.dumps(ux_result, indent=2))
    
    print("\n" + "=" * 60)
    print("FUNCTIONAL REASONING")
    print("=" * 60)
    
    # Run functional analysis
    func_result = ai_functional_reasoning(url, api_key)
    print(func_result['functional_analysis'])
    
    # Save results
    with open('ai-analysis-report.json', 'w') as f:
        json.dump({
            "ux_analysis": ux_result,
            "functional_analysis": func_result
        }, f, indent=2)
    
    print("\n📄 Full report saved to: ai-analysis-report.json")
