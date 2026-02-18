"""
Example app configuration for large applications
This shows how to scale the agent beyond simple hardcoded checks
"""

# Example 1: Simple Counter App (Current)
SIMPLE_APP_CONFIG = {
    "name": "Counter App",
    "type": "static",
    "critical_elements": {
        "buttons": ["increment", "decrement", "reset"],
        "displays": ["count"]
    }
}

# Example 2: E-Commerce Platform
ECOMMERCE_CONFIG = {
    "name": "E-Commerce Platform",
    "type": "SPA",
    "framework": "React",
    
    "pages": {
        "home": {
            "path": "/",
            "title": "Home - MyStore",
            "components": ["header", "hero", "featured-products", "footer"],
            "critical": True
        },
        "products": {
            "path": "/products",
            "title": "Products - MyStore",
            "components": ["header", "filters", "product-grid", "pagination"],
            "critical": True
        },
        "product_detail": {
            "path": "/product/:id",
            "title_pattern": "* - MyStore",
            "components": ["header", "product-image", "product-info", "add-to-cart", "reviews"],
            "critical": True
        },
        "cart": {
            "path": "/cart",
            "title": "Shopping Cart - MyStore",
            "components": ["header", "cart-items", "cart-summary", "checkout-button"],
            "critical": True
        },
        "checkout": {
            "path": "/checkout",
            "title": "Checkout - MyStore",
            "components": ["header", "shipping-form", "payment-form", "order-summary"],
            "critical": True
        }
    },
    
    "api_endpoints": [
        {"path": "/api/products", "method": "GET", "critical": True},
        {"path": "/api/product/:id", "method": "GET", "critical": True},
        {"path": "/api/cart", "method": "GET", "critical": True},
        {"path": "/api/cart", "method": "POST", "critical": True},
        {"path": "/api/checkout", "method": "POST", "critical": True}
    ],
    
    "user_flows": {
        "purchase": {
            "name": "Complete Purchase Flow",
            "steps": [
                {"action": "visit", "page": "products"},
                {"action": "click", "element": "product-card"},
                {"action": "click", "element": "add-to-cart"},
                {"action": "visit", "page": "cart"},
                {"action": "click", "element": "checkout-button"},
                {"action": "fill", "form": "shipping-form"},
                {"action": "fill", "form": "payment-form"},
                {"action": "click", "element": "submit-order"},
                {"action": "verify", "element": "order-confirmation"}
            ],
            "critical": True
        }
    },
    
    "performance": {
        "page_load_max_ms": 3000,
        "api_response_max_ms": 1000,
        "lighthouse_min_score": 80
    }
}

# Example 3: SaaS Dashboard
SAAS_DASHBOARD_CONFIG = {
    "name": "Analytics Dashboard",
    "type": "SPA",
    "framework": "Vue",
    
    "pages": {
        "login": {
            "path": "/login",
            "components": ["login-form", "forgot-password-link"],
            "critical": True
        },
        "dashboard": {
            "path": "/dashboard",
            "components": ["sidebar", "header", "metrics-cards", "charts", "data-table"],
            "critical": True,
            "requires_auth": True
        },
        "reports": {
            "path": "/reports",
            "components": ["sidebar", "header", "report-filters", "report-viewer"],
            "critical": True,
            "requires_auth": True
        },
        "settings": {
            "path": "/settings",
            "components": ["sidebar", "header", "settings-tabs", "save-button"],
            "critical": False,
            "requires_auth": True
        }
    },
    
    "api_endpoints": [
        {"path": "/api/auth/login", "method": "POST", "critical": True},
        {"path": "/api/dashboard/metrics", "method": "GET", "critical": True},
        {"path": "/api/reports", "method": "GET", "critical": True},
        {"path": "/api/user/settings", "method": "GET", "critical": False}
    ],
    
    "user_flows": {
        "login_and_view_dashboard": {
            "steps": [
                {"action": "visit", "page": "login"},
                {"action": "fill", "form": "login-form", "fields": ["email", "password"]},
                {"action": "click", "element": "login-button"},
                {"action": "verify", "page": "dashboard"},
                {"action": "verify", "element": "metrics-cards"}
            ],
            "critical": True
        }
    },
    
    "data_requirements": {
        "dashboard_metrics": {
            "endpoint": "/api/dashboard/metrics",
            "required_fields": ["total_users", "revenue", "active_sessions"],
            "response_time_max_ms": 500
        }
    }
}

# Example 4: Multi-Page Blog
BLOG_CONFIG = {
    "name": "Tech Blog",
    "type": "multi-page",
    "framework": "Next.js",
    
    "pages": {
        "home": {
            "path": "/",
            "components": ["header", "hero", "post-grid", "footer"],
            "critical": True
        },
        "blog_post": {
            "path": "/blog/:slug",
            "components": ["header", "article-content", "author-bio", "comments", "footer"],
            "critical": True
        },
        "about": {
            "path": "/about",
            "components": ["header", "about-content", "footer"],
            "critical": False
        }
    },
    
    "seo_requirements": {
        "meta_tags": ["description", "og:title", "og:description", "og:image"],
        "structured_data": ["Article", "Person"],
        "sitemap": "/sitemap.xml",
        "robots_txt": "/robots.txt"
    },
    
    "performance": {
        "first_contentful_paint_ms": 1500,
        "time_to_interactive_ms": 3000,
        "cumulative_layout_shift": 0.1
    }
}

# How to use these configs:

def get_config_for_app(app_type):
    """Get configuration based on app type"""
    configs = {
        "simple": SIMPLE_APP_CONFIG,
        "ecommerce": ECOMMERCE_CONFIG,
        "saas": SAAS_DASHBOARD_CONFIG,
        "blog": BLOG_CONFIG
    }
    return configs.get(app_type, SIMPLE_APP_CONFIG)


def validate_deployment_against_config(url, config):
    """
    Validate deployment against app configuration
    This replaces hardcoded checks with config-driven validation
    """
    issues = []
    
    # Check all critical pages
    for page_name, page_config in config.get("pages", {}).items():
        if page_config.get("critical", False):
            page_url = f"{url}{page_config['path']}"
            
            # Verify page loads
            try:
                response = requests.get(page_url)
                if response.status_code != 200:
                    issues.append({
                        "severity": "CRITICAL",
                        "type": "PAGE_NOT_FOUND",
                        "page": page_name,
                        "url": page_url
                    })
                    continue
                
                # Verify components exist
                soup = BeautifulSoup(response.text, 'html.parser')
                for component in page_config.get("components", []):
                    # Check if component exists (by class, id, or data attribute)
                    if not soup.find(class_=component) and not soup.find(id=component):
                        issues.append({
                            "severity": "HIGH",
                            "type": "MISSING_COMPONENT",
                            "page": page_name,
                            "component": component
                        })
            
            except Exception as e:
                issues.append({
                    "severity": "CRITICAL",
                    "type": "PAGE_ERROR",
                    "page": page_name,
                    "error": str(e)
                })
    
    # Check API endpoints
    for endpoint in config.get("api_endpoints", []):
        if endpoint.get("critical", False):
            api_url = f"{url}{endpoint['path']}"
            try:
                # Simple health check (would need auth for real apps)
                response = requests.request(endpoint["method"], api_url, timeout=5)
                if response.status_code >= 500:
                    issues.append({
                        "severity": "CRITICAL",
                        "type": "API_ERROR",
                        "endpoint": endpoint["path"],
                        "status_code": response.status_code
                    })
            except Exception as e:
                issues.append({
                    "severity": "CRITICAL",
                    "type": "API_UNREACHABLE",
                    "endpoint": endpoint["path"],
                    "error": str(e)
                })
    
    return issues


# Example usage:
if __name__ == "__main__":
    import json
    
    print("Example App Configurations:\n")
    
    print("1. Simple Counter App:")
    print(json.dumps(SIMPLE_APP_CONFIG, indent=2))
    print("\n" + "="*60 + "\n")
    
    print("2. E-Commerce Platform:")
    print(json.dumps(ECOMMERCE_CONFIG, indent=2))
    print("\n" + "="*60 + "\n")
    
    print("3. SaaS Dashboard:")
    print(json.dumps(SAAS_DASHBOARD_CONFIG, indent=2))
    print("\n" + "="*60 + "\n")
    
    print("4. Blog:")
    print(json.dumps(BLOG_CONFIG, indent=2))
