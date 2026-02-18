#!/usr/bin/env python3
"""
Quality validation checks for deployments
Detects UX, accessibility, and functional issues
"""
import requests
from bs4 import BeautifulSoup
import json


def check_quality_issues(url: str):
    """
    Comprehensive quality checks for deployment
    Returns issues categorized by severity
    """
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'warnings': []
        }
        
        # 1. Check for buttons without text (UX/Accessibility issue)
        buttons = soup.find_all('button')
        for btn in buttons:
            btn_text = btn.get_text(strip=True)
            btn_id = btn.get('id', 'unknown')
            btn_aria_label = btn.get('aria-label', '')
            
            if not btn_text and not btn_aria_label:
                issues['high'].append({
                    'type': 'EMPTY_BUTTON',
                    'element': f'button#{btn_id}' if btn_id != 'unknown' else 'button',
                    'message': f'Button with id="{btn_id}" has no text or aria-label',
                    'impact': 'Users cannot see what the button does. Screen readers cannot announce it.',
                    'fix': f'Add text inside the button or add aria-label attribute',
                    'code': f'<button id="{btn_id}">Add Text Here</button>'
                })
        
        # 2. Check for inputs without labels (Accessibility issue)
        inputs = soup.find_all('input')
        for inp in inputs:
            inp_id = inp.get('id', '')
            inp_type = inp.get('type', 'text')
            
            # Check if there's a label for this input
            if inp_id:
                label = soup.find('label', attrs={'for': inp_id})
                if not label and inp_type not in ['hidden', 'submit', 'button']:
                    issues['medium'].append({
                        'type': 'INPUT_WITHOUT_LABEL',
                        'element': f'input#{inp_id}',
                        'message': f'Input field "{inp_id}" has no associated label',
                        'impact': 'Screen readers cannot identify the input purpose',
                        'fix': f'Add <label for="{inp_id}">Label Text</label>'
                    })
        
        # 3. Check for images without alt text (Accessibility issue)
        images = soup.find_all('img')
        for img in images:
            if not img.get('alt'):
                src = img.get('src', 'unknown')
                issues['medium'].append({
                    'type': 'IMAGE_WITHOUT_ALT',
                    'element': f'img[src="{src}"]',
                    'message': f'Image has no alt text',
                    'impact': 'Screen readers cannot describe the image',
                    'fix': 'Add alt="description" attribute'
                })
        
        # 4. Check for missing page title
        if not soup.title or not soup.title.string.strip():
            issues['high'].append({
                'type': 'MISSING_PAGE_TITLE',
                'element': 'title',
                'message': 'Page has no title or empty title',
                'impact': 'Poor SEO, bad browser tab experience',
                'fix': 'Add <title>Your Page Title</title>'
            })
        
        # 5. Check for duplicate IDs (Critical HTML error)
        all_ids = [elem.get('id') for elem in soup.find_all(id=True)]
        duplicate_ids = [id for id in set(all_ids) if all_ids.count(id) > 1]
        
        for dup_id in duplicate_ids:
            issues['critical'].append({
                'type': 'DUPLICATE_ID',
                'element': f'#{dup_id}',
                'message': f'Multiple elements have id="{dup_id}"',
                'impact': 'JavaScript selectors will fail, invalid HTML',
                'fix': 'Ensure each ID is unique'
            })
        
        # 6. Check for buttons without IDs (if they need JS interaction)
        buttons_without_id = [btn for btn in buttons if not btn.get('id')]
        if buttons_without_id and len(soup.find_all('script')) > 0:
            issues['warnings'].append({
                'type': 'BUTTON_WITHOUT_ID',
                'count': len(buttons_without_id),
                'message': f'{len(buttons_without_id)} button(s) have no ID',
                'impact': 'May be harder to target with JavaScript',
                'fix': 'Add id attribute if button needs JavaScript interaction'
            })
        
        # 7. Check for empty links
        links = soup.find_all('a')
        for link in links:
            link_text = link.get_text(strip=True)
            href = link.get('href', '')
            
            if not link_text and not link.find('img'):
                issues['medium'].append({
                    'type': 'EMPTY_LINK',
                    'element': f'a[href="{href}"]',
                    'message': 'Link has no text or image',
                    'impact': 'Users cannot see what the link does',
                    'fix': 'Add text inside the link or use an image with alt text'
                })
        
        # 8. Check for missing meta viewport (Mobile responsiveness)
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport_meta:
            issues['low'].append({
                'type': 'MISSING_VIEWPORT',
                'element': 'meta[name="viewport"]',
                'message': 'Missing viewport meta tag',
                'impact': 'Page may not be mobile-responsive',
                'fix': 'Add <meta name="viewport" content="width=device-width, initial-scale=1.0">'
            })
        
        # 9. Check for missing language attribute
        html_tag = soup.find('html')
        if html_tag and not html_tag.get('lang'):
            issues['low'].append({
                'type': 'MISSING_LANG',
                'element': 'html',
                'message': 'HTML tag missing lang attribute',
                'impact': 'Screen readers may not use correct pronunciation',
                'fix': 'Add lang="en" to <html> tag'
            })
        
        # 10. Check for inline styles (Code quality)
        elements_with_style = soup.find_all(style=True)
        if len(elements_with_style) > 5:
            issues['warnings'].append({
                'type': 'EXCESSIVE_INLINE_STYLES',
                'count': len(elements_with_style),
                'message': f'{len(elements_with_style)} elements have inline styles',
                'impact': 'Harder to maintain, poor separation of concerns',
                'fix': 'Move styles to CSS file'
            })
        
        # Calculate summary
        total_issues = (
            len(issues['critical']) +
            len(issues['high']) +
            len(issues['medium']) +
            len(issues['low'])
        )
        
        return {
            'status': 'QUALITY_ISSUES_FOUND' if total_issues > 0 else 'QUALITY_OK',
            'url': url,
            'issues': issues,
            'summary': {
                'total_issues': total_issues,
                'critical': len(issues['critical']),
                'high': len(issues['high']),
                'medium': len(issues['medium']),
                'low': len(issues['low']),
                'warnings': len(issues['warnings'])
            }
        }
        
    except Exception as e:
        return {
            'status': 'ERROR',
            'message': f'Error checking quality: {str(e)}',
            'issues': {'critical': [], 'high': [], 'medium': [], 'low': [], 'warnings': []}
        }


def format_quality_report(result):
    """Format quality check results as readable report"""
    lines = []
    lines.append("=" * 60)
    lines.append("QUALITY VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append(f"URL: {result.get('url', 'N/A')}")
    lines.append(f"Status: {result['status']}")
    lines.append("")
    
    summary = result.get('summary', {})
    lines.append("SUMMARY:")
    lines.append(f"  Total Issues: {summary.get('total_issues', 0)}")
    lines.append(f"  Critical: {summary.get('critical', 0)}")
    lines.append(f"  High: {summary.get('high', 0)}")
    lines.append(f"  Medium: {summary.get('medium', 0)}")
    lines.append(f"  Low: {summary.get('low', 0)}")
    lines.append(f"  Warnings: {summary.get('warnings', 0)}")
    lines.append("")
    
    issues = result.get('issues', {})
    
    # Critical issues
    if issues.get('critical'):
        lines.append("🔴 CRITICAL ISSUES:")
        for issue in issues['critical']:
            lines.append(f"  - {issue['type']}: {issue['message']}")
            lines.append(f"    Impact: {issue['impact']}")
            lines.append(f"    Fix: {issue['fix']}")
            lines.append("")
    
    # High severity issues
    if issues.get('high'):
        lines.append("🟠 HIGH SEVERITY ISSUES:")
        for issue in issues['high']:
            lines.append(f"  - {issue['type']}: {issue['message']}")
            lines.append(f"    Impact: {issue['impact']}")
            lines.append(f"    Fix: {issue['fix']}")
            if 'code' in issue:
                lines.append(f"    Example: {issue['code']}")
            lines.append("")
    
    # Medium severity issues
    if issues.get('medium'):
        lines.append("🟡 MEDIUM SEVERITY ISSUES:")
        for issue in issues['medium']:
            lines.append(f"  - {issue['type']}: {issue['message']}")
            lines.append(f"    Impact: {issue['impact']}")
            lines.append(f"    Fix: {issue['fix']}")
            lines.append("")
    
    # Low severity issues
    if issues.get('low'):
        lines.append("🔵 LOW SEVERITY ISSUES:")
        for issue in issues['low']:
            lines.append(f"  - {issue['type']}: {issue['message']}")
            lines.append(f"    Fix: {issue['fix']}")
            lines.append("")
    
    # Warnings
    if issues.get('warnings'):
        lines.append("⚠️  WARNINGS:")
        for warning in issues['warnings']:
            lines.append(f"  - {warning['type']}: {warning['message']}")
            lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    url = os.getenv('DEPLOYMENT_URL', 'https://your-username.github.io/your-repo/')
    
    print(f"🔍 Running quality checks on: {url}\n")
    
    result = check_quality_issues(url)
    report = format_quality_report(result)
    
    print(report)
    
    # Save report
    with open('quality-report.txt', 'w') as f:
        f.write(report)
    
    print("\n📄 Report saved to: quality-report.txt")
    
    # Exit with error if critical or high issues found
    summary = result.get('summary', {})
    if summary.get('critical', 0) > 0 or summary.get('high', 0) > 0:
        print("\n❌ Quality check FAILED: Critical or high severity issues found")
        exit(1)
    else:
        print("\n✅ Quality check PASSED")
        exit(0)
