"""
Authentication helpers for E2E tests
"""


def login(page, email=None, password=None, base_url="http://localhost:5173"):
    """
    Attempt to login to admin-web
    Returns True if successful, False otherwise
    """
    print("\n🔐 Checking authentication...")

    page.goto(f"{base_url}/dashboard")
    page.wait_for_load_state("networkidle")

    # Check if we're redirected to login
    if "login" in page.url.lower():
        print("   ⚠️  Login required")

        if email and password:
            print("   📝 Attempting login...")
            email_input = page.locator('input[type="email"], input[placeholder*="email" i]').first
            password_input = page.locator('input[type="password"]').first

            if email_input.count() > 0 and password_input.count() > 0:
                email_input.fill(email)
                password_input.fill(password)

                # Find and click login button
                login_btn = page.locator(
                    'button[type="submit"], button:has-text("Login"), button:has-text("Sign in")'
                ).first
                if login_btn.count() > 0:
                    login_btn.click()
                    page.wait_for_load_state("networkidle")

                    # Check if login successful
                    if "dashboard" in page.url.lower():
                        print("   ✅ Login successful")
                        return True
                    else:
                        print("   ❌ Login failed")
                        return False
            return False
        else:
            print("   ⚠️  No credentials provided - please login manually or provide credentials")
            return False
    else:
        print("   ✅ Already authenticated")
        return True
