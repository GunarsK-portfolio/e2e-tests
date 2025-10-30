"""
Common helper functions for E2E tests
"""

def take_screenshot(page, name, description=""):
    """Take a screenshot with consistent naming"""
    path = f'/tmp/test_{name}.png'
    page.screenshot(path=path)
    if description:
        print(f"   📸 {description}: {path}")
    return path

def wait_for_page_load(page):
    """Wait for page to fully load"""
    page.wait_for_load_state('networkidle')

def check_element_exists(page, selector, name=""):
    """Check if element exists and return count"""
    count = page.locator(selector).count()
    if count > 0:
        print(f"   ✅ {name or 'Element'} found ({count})")
    else:
        print(f"   ⚠️  {name or 'Element'} not found")
    return count > 0
