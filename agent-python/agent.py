import os
import json
from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from baseline import compare_with_baseline, load_baseline

# Tool implementations
def check_deployed_site(url: str) -> str:
    """Fetches the deployed website and analyzes its HTML structure, scripts, and styles"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        analysis = {
            'status': response.status_code,
            'title': soup.title.string if soup.title else '',
            'scripts': [script.get('src', 'inline') for script in soup.find_all('script')],
            'stylesheets': [link.get('href') for link in soup.find_all('link', rel='stylesheet')],
            'buttons': [{'id': btn.get('id'), 'text': btn.get_text()} for btn in soup.find_all('button')],
            'hasCounter': bool(soup.find(id='count')),
            'bodyStructure': [child.name for child in soup.body.children if child.name],
        }
        
        return json.dumps(analysis, indent=2)
    except Exception as e:
        return f"Error fetching site: {str(e)}"


def test_javascript_functionality(url: str, expected_elements: list) -> str:
    """Tests if critical JavaScript functionality is working by checking for expected elements"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = {
            'elementsFound': [],
            'elementsMissing': [],
            'scriptsLoaded': len(soup.find_all('script')),
            'potentialIssues': [],
        }
        
        for element_id in expected_elements:
            if soup.find(id=element_id):
                results['elementsFound'].append(element_id)
            else:
                results['elementsMissing'].append(element_id)
                results['potentialIssues'].append(f"Missing expected element: #{element_id}")
        
        if not soup.find_all('script'):
            results['potentialIssues'].append('No JavaScript files found - functionality may be broken')
        
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error testing functionality: {str(e)}"


def compare_deployments(current_url: str, previous_url: str = None) -> str:
    """Compares two versions of the deployed site to identify breaking changes"""
    try:
        response = requests.get(current_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        current_analysis = {
            'scripts': len(soup.find_all('script')),
            'styles': len(soup.find_all('link', rel='stylesheet')),
            'buttons': len(soup.find_all('button')),
            'interactiveElements': len(soup.find_all(['button', 'input', 'select', 'textarea'])),
            'criticalIds': ['count', 'increment', 'decrement', 'reset'],
            'foundIds': [],
            'missingIds': [],
        }
        
        for element_id in current_analysis['criticalIds']:
            if soup.find(id=element_id):
                current_analysis['foundIds'].append(element_id)
            else:
                current_analysis['missingIds'].append(element_id)
        
        breaking_changes = []
        if current_analysis['missingIds']:
            breaking_changes.append(f"Missing critical elements: {', '.join(current_analysis['missingIds'])}")
        if current_analysis['scripts'] == 0:
            breaking_changes.append('No JavaScript files detected - counter functionality will not work')
        if current_analysis['buttons'] == 0:
            breaking_changes.append('No buttons found - user interaction is broken')
        
        return json.dumps({
            'currentAnalysis': current_analysis,
            'breakingChanges': breaking_changes,
            'status': 'HEALTHY' if not breaking_changes else 'ISSUES_DETECTED',
        }, indent=2)
    except Exception as e:
        return f"Error comparing deployments: {str(e)}"


def check_common_issues(url: str) -> str:
    """Checks for common deployment issues like missing files, broken links, or CORS problems"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        issues = []
        warnings = []
        
        # Check for external resources
        external_scripts = [script.get('src') for script in soup.find_all('script', src=True)]
        external_styles = [link.get('href') for link in soup.find_all('link', rel='stylesheet')]
        
        for src in external_scripts:
            if src and not src.startswith('http'):
                try:
                    full_url = requests.compat.urljoin(url, src)
                    requests.head(full_url, timeout=5)
                except:
                    issues.append(f"Script file not accessible: {src}")
        
        for href in external_styles:
            if href and not href.startswith('http'):
                try:
                    full_url = requests.compat.urljoin(url, href)
                    requests.head(full_url, timeout=5)
                except:
                    issues.append(f"Stylesheet not accessible: {href}")
        
        # Check for console errors indicators
        if not soup.find_all('script'):
            warnings.append('No JavaScript detected - ensure this is intentional')
        
        if not soup.find_all('link', rel='stylesheet') and not soup.find_all('style'):
            warnings.append('No CSS detected - page may appear unstyled')
        
        return json.dumps({
            'issues': issues,
            'warnings': warnings,
            'status': 'OK' if not issues else 'PROBLEMS_FOUND',
            'checkedAt': requests.utils.default_headers()['User-Agent'],
        }, indent=2)
    except Exception as e:
        return f"Error checking for issues: {str(e)}"


# Create Anthropic client
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Define tools for Anthropic
tools = [
    {
        'name': 'check_deployed_site',
        'description': 'Fetches the deployed website and analyzes its HTML structure, scripts, and styles',
        'input_schema': {
            'type': 'object',
            'properties': {
                'url': {'type': 'string', 'description': 'The URL of the deployed website to check'},
            },
            'required': ['url'],
        },
    },
    {
        'name': 'test_javascript_functionality',
        'description': 'Tests if critical JavaScript functionality is working by checking for expected elements and event handlers',
        'input_schema': {
            'type': 'object',
            'properties': {
                'url': {'type': 'string', 'description': 'The URL to test'},
                'expected_elements': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Array of element IDs that should exist',
                },
            },
            'required': ['url', 'expected_elements'],
        },
    },
    {
        'name': 'compare_deployments',
        'description': 'Compares two versions of the deployed site to identify breaking changes',
        'input_schema': {
            'type': 'object',
            'properties': {
                'current_url': {'type': 'string', 'description': 'URL of the current/new deployment'},
                'previous_url': {'type': 'string', 'description': 'URL of the previous deployment (optional)'},
            },
            'required': ['current_url'],
        },
    },
    {
        'name': 'check_common_issues',
        'description': 'Checks for common deployment issues like missing files, broken links, or CORS problems',
        'input_schema': {
            'type': 'object',
            'properties': {
                'url': {'type': 'string', 'description': 'The deployed site URL to check'},
            },
            'required': ['url'],
        },
    },
]


def run_agent(user_message: str):
    """Simple agent loop"""
    messages = [{'role': 'user', 'content': user_message}]
    
    system_prompt = """You are a deployment analysis expert. Your job is to:
1. Analyze deployed websites for potential breaking changes
2. Identify missing critical elements (buttons, scripts, styles)
3. Test functionality and report issues
4. Compare deployments to detect regressions
5. Provide clear, actionable feedback about deployment health

CRITICAL: For this counter app, you MUST verify these elements exist:
- Button with id="increment" (REQUIRED)
- Button with id="decrement" (REQUIRED)
- Button with id="reset" (REQUIRED)
- Element with id="count" (REQUIRED)
- JavaScript file (app.js) must be loading
- CSS file (style.css) must be loading

When analyzing a deployment:
- ALWAYS use the compare_deployments tool to check for all critical IDs
- ALWAYS check for the increment, decrement, and reset buttons
- Verify JavaScript and CSS files are loading
- Report ANY missing critical elements as BREAKING CHANGES
- Be specific about what's broken and how it impacts users"""
    
    max_iterations = 10
    
    for iteration in range(1, max_iterations + 1):
        response = client.messages.create(
            model='claude-3-haiku-20240307',
            max_tokens=4096,
            system=system_prompt,
            messages=messages,
            tools=tools,
        )
        
        print(f"\n[Iteration {iteration}]")
        
        # Add assistant response to messages
        messages.append({'role': 'assistant', 'content': response.content})
        
        # Check if we need to execute tools
        tool_uses = [block for block in response.content if block.type == 'tool_use']
        
        if not tool_uses:
            # No more tools to execute, we're done
            text_blocks = [block for block in response.content if block.type == 'text']
            for block in text_blocks:
                print(block.text)
            break
        
        # Execute tools
        tool_results = []
        
        for tool_use in tool_uses:
            print(f"🔧 Using tool: {tool_use.name}")
            print(f"   Input: {json.dumps(tool_use.input, indent=2)}")
            
            # Execute the appropriate tool
            if tool_use.name == 'check_deployed_site':
                result = check_deployed_site(tool_use.input['url'])
            elif tool_use.name == 'test_javascript_functionality':
                result = test_javascript_functionality(
                    tool_use.input['url'],
                    tool_use.input['expected_elements']
                )
            elif tool_use.name == 'compare_deployments':
                result = compare_deployments(
                    tool_use.input['current_url'],
                    tool_use.input.get('previous_url')
                )
            elif tool_use.name == 'check_common_issues':
                result = check_common_issues(tool_use.input['url'])
            else:
                result = f"Unknown tool: {tool_use.name}"
            
            print(f"   Result: {result[:200]}...")
            
            tool_results.append({
                'type': 'tool_result',
                'tool_use_id': tool_use.id,
                'content': result,
            })
        
        # Add tool results to messages
        messages.append({'role': 'user', 'content': tool_results})


if __name__ == '__main__':
    deployment_url = os.getenv('DEPLOYMENT_URL', 'https://your-username.github.io/your-repo/')
    
    print('🤖 Deployment Analyzer Agent Starting...\n')
    print(f'Analyzing deployment at: {deployment_url}\n')
    
    # Capture output for report
    import sys
    from io import StringIO
    
    # Save original stdout
    original_stdout = sys.stdout
    report_buffer = StringIO()
    
    # Redirect stdout to capture output
    sys.stdout = report_buffer
    
    try:
        run_agent(
            f"Analyze the deployment at {deployment_url} and identify any breaking changes or issues "
            f"that would prevent the counter functionality from working. Check for missing elements, "
            f"broken scripts, or other problems."
        )
    finally:
        # Restore stdout
        sys.stdout = original_stdout
        
        # Get the report
        report = report_buffer.getvalue()
        
        # Print to console
        print(report)
        
        # Save to file
        with open('analysis-report.txt', 'w') as f:
            f.write(f'Deployment Analysis Report\n')
            f.write(f'=' * 50 + '\n')
            f.write(f'URL: {deployment_url}\n')
            f.write(f'Timestamp: {requests.utils.default_headers()["User-Agent"]}\n')
            f.write(f'=' * 50 + '\n\n')
            f.write(report)
        
        print('\n📊 Analysis Complete!\n')
        print('📄 Report saved to: analysis-report.txt\n')
    
    # Check if there are breaking changes and exit with error code (OUTSIDE finally block)
    if 'ISSUES_DETECTED' in report or 'Missing' in report or 'missing' in report.lower():
        print('⚠️  WARNING: Breaking changes detected!')
        print('Review the analysis above for details.\n')
        # Exit with error code to fail the CI/CD pipeline
        sys.exit(1)
