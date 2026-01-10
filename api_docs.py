from flask import Flask, render_template_string
import sys
import os
import json
import inspect
import re

# Add the current directory to sys.path so we can import the app
sys.path.append(os.getcwd())

try:
    from app import app as main_app
except ImportError:
    print("Error: Could not find app.py in the current directory.")
    sys.exit(1)

docs_app = Flask(__name__)

def extract_api_details(view_func):
    """
    Analyzes the source code of a route to extract:
    1. Required Headers (Auth, etc.)
    2. Request Body Keys
    3. Response Keys
    """
    try:
        source = inspect.getsource(view_func)
    except Exception:
        return {}, {}, {}

    headers = {}
    body = {}
    response = {}

    # 1. Detect Headers
    if '@auth_required' in source:
        headers['Authorization'] = 'Bearer <jwt_token>'
    if '@admin_required' in source:
        headers['Authorization'] = 'Bearer <admin_token>'
    
    # Detect manual header gets like request.headers.get('X-User-Email')
    header_matches = re.findall(r"request\.headers\.get\(['\"]([^'\"]+)['\"]", source)
    for h in header_matches:
        if h != 'Authorization': # Skip if we already added it
            headers[h] = f"<{h.lower().replace('-', '_')}>"

    # 2. Detect Request Body
    # Patterns: data.get('key'), data['key'], request.json.get('key')
    body_patterns = [
        r"data\.get\(['\"]([^'\"]+)['\"]",
        r"data\[['\"]([^'\"]+)['\"]\]",
        r"request\.json\.get\(['\"]([^'\"]+)['\"]",
        r"request\.get_json\(\)\.get\(['\"]([^'\"]+)['\"]"
    ]
    for pattern in body_patterns:
        matches = re.findall(pattern, source)
        for m in matches:
            body[m] = f"string" # Placeholder

    # 3. Detect Response
    # Look for jsonify({...}) or dicts inside jsonify
    # This is a simple heuristic
    response_match = re.search(r"jsonify\(\{([\s\S]*?)\}\)", source)
    if response_match:
        # Extract keys from the jsonify dict content
        content = response_match.group(1)
        # Find keys like 'token': ... or 'user': ...
        keys = re.findall(r"['\"]([^'\"]+)['\"]\s*:", content)
        for k in keys:
            response[k] = "..."

    return headers, body, response

# Manual Overrides for complex routes
MANUAL_DOCS = {
    '/api/auth/login': {
        'request': {'email': 'user@example.com', 'password': 'password123'},
        'response': {'token': 'eyJ...', 'user': {'id': 1, 'role': 'user'}}
    },
    '/api/auth/signup': {
        'request': {'name': 'John', 'email': 'john@example.com', 'password': 'pass'},
        'response': {'message': 'User created', 'token': '...'}
    }
}

@docs_app.route('/')
def index():
    routes = []
    for rule in main_app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue
        
        rule_str = str(rule)
        methods = [m for m in rule.methods if m not in ('OPTIONS', 'HEAD')]
        view_func = main_app.view_functions[rule.endpoint]
        
        # Auto-extract details
        headers, body, response = extract_api_details(view_func)
        
        # Apply manual overrides
        manual = MANUAL_DOCS.get(rule_str, {})
        if 'request' in manual: body = manual['request']
        if 'response' in manual: response = manual['response']
        if 'headers' in manual: headers.update(manual['headers'])

        # Format for display
        routes.append({
            'rule': rule_str,
            'methods': methods,
            'headers': json.dumps(headers, indent=2) if headers else None,
            'request': json.dumps(body, indent=2) if body else None,
            'response': json.dumps(response, indent=2) if response else None,
            'endpoint': rule.endpoint
        })
    
    routes.sort(key=lambda x: x['rule'])

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pearto API Docs</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background: #f8fafc; color: #334155; padding: 40px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
            .header { padding: 15px 20px; background: #f1f5f9; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; }
            .method { font-weight: bold; padding: 4px 8px; border-radius: 4px; color: white; margin-right: 10px; font-size: 0.8rem; }
            .GET { background: #3b82f6; } .POST { background: #10b981; } .DELETE { background: #ef4444; } .PATCH { background: #f59e0b; }
            .url { font-family: monospace; font-size: 1rem; font-weight: 600; color: #1e293b; }
            .body { padding: 20px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
            .section h4 { margin: 0 0 10px 0; font-size: 0.75rem; text-transform: uppercase; color: #64748b; }
            pre { background: #0f172a; color: #38bdf8; padding: 10px; border-radius: 6px; overflow-x: auto; font-size: 0.85rem; margin: 0; }
            .empty { color: #94a3b8; font-style: italic; font-size: 0.9rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="margin-bottom: 30px;">🍐 Pearto API Documentation</h1>
            {% for r in routes %}
            <div class="card">
                <div class="header">
                    {% for m in r.methods %}<span class="method {{m}}">{{m}}</span>{% endfor %}
                    <span class="url">{{ r.rule }}</span>
                </div>
                <div class="body">
                    <div class="section">
                        <h4>Headers</h4>
                        {% if r.headers %}<pre>{{ r.headers }}</pre>{% else %}<span class="empty">No headers required</span>{% endif %}
                    </div>
                    <div class="section">
                        <h4>Request Body</h4>
                        {% if r.request %}<pre>{{ r.request }}</pre>{% else %}<span class="empty">No body required</span>{% endif %}
                    </div>
                    <div class="section">
                        <h4>Response</h4>
                        {% if r.response %}<pre>{{ r.response }}</pre>{% else %}<span class="empty">Unknown</span>{% endif %}
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, routes=routes)

if __name__ == '__main__':
    print("Server running on http://localhost:5001")
    docs_app.run(port=5001)
