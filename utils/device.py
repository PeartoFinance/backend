def parse_user_agent(ua_string: str) -> str:
    """
    Parses a raw User-Agent string into a friendly, human-readable format.
    Example: 'Chrome on Windows 10/11' or 'Safari on iPhone'
    """
    if not ua_string:
        return 'Unknown device'
        
    ua_lower = ua_string.lower()
    
    # Simple OS checking
    os_name = 'Unknown OS'
    if 'windows nt 10.0' in ua_lower:
        os_name = 'Windows 10/11'
    elif 'windows nt' in ua_lower:
        os_name = 'Windows'
    elif 'macintosh' in ua_lower or 'mac os x' in ua_lower:
        os_name = 'macOS'
    elif 'iphone' in ua_lower:
        os_name = 'iPhone'
    elif 'ipad' in ua_lower:
        os_name = 'iPad'
    elif 'android' in ua_lower:
        os_name = 'Android'
    elif 'linux' in ua_lower:
        os_name = 'Linux'
        
    # Simple browser/client checking
    browser = 'Web Browser'
    if 'postman' in ua_lower:
        browser = 'Postman'
    elif 'dart' in ua_lower:
        browser = 'Mobile App'
    elif 'edg' in ua_lower:
        browser = 'Edge'
    elif 'opr' in ua_lower or 'opera' in ua_lower:
        browser = 'Opera'
    elif 'chrome' in ua_lower and 'safari' in ua_lower:
        browser = 'Chrome'
    elif 'safari' in ua_lower and 'chrome' not in ua_lower:
        browser = 'Safari'
    elif 'firefox' in ua_lower:
        browser = 'Firefox'
        
    return f"{browser} on {os_name}"
