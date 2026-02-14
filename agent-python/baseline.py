#!/usr/bin/env python3
"""
Baseline management for deployment tracking
"""
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup


def capture_baseline(url: str, baseline_file: str = 'baseline.json'):
    """Capture the current deployment as a baseline"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        baseline = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'structure': {
                'title': soup.title.string if soup.title else '',
                'scripts': [script.get('src', 'inline') for script in soup.find_all('script')],
                'stylesheets': [link.get('href') for link in soup.find_all('link', rel='stylesheet')],
                'buttons': [
                    {
                        'id': btn.get('id'),
                        'text': btn.get_text().strip(),
                        'classes': btn.get('class', [])
                    }
                    for btn in soup.find_all('button')
                ],
                'inputs': [
                    {
                        'id': inp.get('id'),
                        'type': inp.get('type'),
                        'name': inp.get('name')
                    }
                    for inp in soup.find_all('input')
                ],
                'critical_ids': [
                    elem.get('id')
                    for elem in soup.find_all(id=True)
                    if elem.get('id')
                ],
                'element_counts': {
                    'buttons': len(soup.find_all('button')),
                    'inputs': len(soup.find_all('input')),
                    'forms': len(soup.find_all('form')),
                    'links': len(soup.find_all('a')),
                    'images': len(soup.find_all('img')),
                    'scripts': len(soup.find_all('script')),
                    'styles': len(soup.find_all('link', rel='stylesheet')),
                }
            }
        }
        
        # Save baseline
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        print(f"✅ Baseline captured successfully!")
        print(f"   URL: {url}")
        print(f"   Buttons: {len(baseline['structure']['buttons'])}")
        print(f"   Critical IDs: {len(baseline['structure']['critical_ids'])}")
        print(f"   Saved to: {baseline_file}")
        
        return baseline
        
    except Exception as e:
        print(f"❌ Error capturing baseline: {str(e)}")
        return None


def load_baseline(baseline_file: str = 'baseline.json'):
    """Load the baseline from file"""
    if not os.path.exists(baseline_file):
        return None
    
    try:
        with open(baseline_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading baseline: {str(e)}")
        return None


def compare_with_baseline(current_url: str, baseline_file: str = 'baseline.json'):
    """Compare current deployment with baseline"""
    baseline = load_baseline(baseline_file)
    
    if not baseline:
        return {
            'status': 'NO_BASELINE',
            'message': 'No baseline found. Run baseline.py to create one.',
            'regressions': [],
            'improvements': [],
        }
    
    try:
        # Fetch current deployment
        response = requests.get(current_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        current = {
            'buttons': [
                {
                    'id': btn.get('id'),
                    'text': btn.get_text().strip()
                }
                for btn in soup.find_all('button')
            ],
            'critical_ids': [
                elem.get('id')
                for elem in soup.find_all(id=True)
                if elem.get('id')
            ],
            'scripts': [script.get('src', 'inline') for script in soup.find_all('script')],
            'stylesheets': [link.get('href') for link in soup.find_all('link', rel='stylesheet')],
        }
        
        # Compare
        regressions = []
        improvements = []
        
        # Check for missing buttons
        baseline_button_ids = {btn['id'] for btn in baseline['structure']['buttons'] if btn['id']}
        current_button_ids = {btn['id'] for btn in current['buttons'] if btn['id']}
        
        missing_buttons = baseline_button_ids - current_button_ids
        new_buttons = current_button_ids - baseline_button_ids
        
        if missing_buttons:
            regressions.append({
                'type': 'MISSING_BUTTONS',
                'severity': 'HIGH',
                'details': f"Missing buttons: {', '.join(missing_buttons)}",
                'items': list(missing_buttons)
            })
        
        if new_buttons:
            improvements.append({
                'type': 'NEW_BUTTONS',
                'details': f"New buttons added: {', '.join(new_buttons)}",
                'items': list(new_buttons)
            })
        
        # Check for missing critical IDs
        baseline_ids = set(baseline['structure']['critical_ids'])
        current_ids = set(current['critical_ids'])
        
        missing_ids = baseline_ids - current_ids
        new_ids = current_ids - baseline_ids
        
        if missing_ids:
            regressions.append({
                'type': 'MISSING_ELEMENTS',
                'severity': 'HIGH',
                'details': f"Missing element IDs: {', '.join(missing_ids)}",
                'items': list(missing_ids)
            })
        
        if new_ids:
            improvements.append({
                'type': 'NEW_ELEMENTS',
                'details': f"New element IDs: {', '.join(new_ids)}",
                'items': list(new_ids)
            })
        
        # Check for missing scripts
        baseline_scripts = set(baseline['structure']['scripts'])
        current_scripts = set(current['scripts'])
        
        missing_scripts = baseline_scripts - current_scripts
        if missing_scripts:
            regressions.append({
                'type': 'MISSING_SCRIPTS',
                'severity': 'CRITICAL',
                'details': f"Missing JavaScript files: {', '.join(missing_scripts)}",
                'items': list(missing_scripts)
            })
        
        # Check for missing stylesheets
        baseline_styles = set(baseline['structure']['stylesheets'])
        current_styles = set(current['stylesheets'])
        
        missing_styles = baseline_styles - current_styles
        if missing_styles:
            regressions.append({
                'type': 'MISSING_STYLES',
                'severity': 'MEDIUM',
                'details': f"Missing CSS files: {', '.join(missing_styles)}",
                'items': list(missing_styles)
            })
        
        return {
            'status': 'REGRESSIONS_FOUND' if regressions else 'HEALTHY',
            'baseline_timestamp': baseline['timestamp'],
            'regressions': regressions,
            'improvements': improvements,
            'summary': {
                'total_regressions': len(regressions),
                'total_improvements': len(improvements),
                'critical_issues': len([r for r in regressions if r.get('severity') == 'CRITICAL']),
                'high_issues': len([r for r in regressions if r.get('severity') == 'HIGH']),
            }
        }
        
    except Exception as e:
        return {
            'status': 'ERROR',
            'message': f"Error comparing with baseline: {str(e)}",
            'regressions': [],
            'improvements': [],
        }


if __name__ == '__main__':
    import sys
    from dotenv import load_dotenv
    load_dotenv()
    
    url = os.getenv('DEPLOYMENT_URL', 'https://your-username.github.io/your-repo/')
    
    if len(sys.argv) > 1 and sys.argv[1] == 'capture':
        # Capture baseline
        print(f"📸 Capturing baseline from: {url}\n")
        capture_baseline(url)
    else:
        # Compare with baseline
        print(f"🔍 Comparing deployment with baseline...\n")
        result = compare_with_baseline(url)
        print(json.dumps(result, indent=2))
