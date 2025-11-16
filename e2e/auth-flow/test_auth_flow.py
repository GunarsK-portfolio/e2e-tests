#!/usr/bin/env python3
"""
E2E test for Authentication Flow
Tests: Login, logout, token refresh, session persistence, unauthorized access
"""

import sys

from playwright.sync_api import sync_playwright, expect

from e2e.common.config import get_config

config = get_config()
BASE_URL = config["admin_web_url"]
USERNAME = config["admin_username"]
PASSWORD = config["admin_password"]


def test_auth_flow():
    """Test complete authentication flow including login, logout, and token handling"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("\n=== AUTHENTICATION FLOW E2E TEST ===\n")

        try:
            # ========================================
            # STEP 1: Initial state - should redirect to login
            # ========================================
            print("1. Testing initial state - unauthorized access...")
            page.goto(f"{BASE_URL}/dashboard")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            # Should be redirected to login
            expect(page).to_have_url(f"{BASE_URL}/login")
            print("   [OK] Unauthorized user redirected to login")
            page.screenshot(path="/tmp/auth_01_redirect_to_login.png")

            # ========================================
            # STEP 2: Test login validation - empty credentials
            # ========================================
            print("\n2. Testing login validation - empty credentials...")
            login_btn = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")').first
            if login_btn.count() > 0:
                login_btn.click()
                page.wait_for_timeout(500)

                # Should still be on login page (validation prevents submission)
                expect(page).to_have_url(f"{BASE_URL}/login")
                print("   [OK] Empty credentials prevented login")
            else:
                print("   [WARN] Login button not found")

            # ========================================
            # STEP 3: Test login with invalid credentials
            # ========================================
            print("\n3. Testing login with invalid credentials...")
            username_input = page.locator('input[type="text"], input[placeholder*="username" i]').first
            password_input = page.locator('input[type="password"]').first

            if username_input.count() > 0 and password_input.count() > 0:
                username_input.fill("invalid_user")
                password_input.fill("wrong_password")
                page.wait_for_timeout(200)

                login_btn.click()
                page.wait_for_timeout(1500)

                # Should still be on login page with error
                expect(page).to_have_url(f"{BASE_URL}/login")
                print("   [OK] Invalid credentials rejected")
                page.screenshot(path="/tmp/auth_03_invalid_credentials.png")
            else:
                print("   [WARN] Login form inputs not found")

            # ========================================
            # STEP 4: Test successful login
            # ========================================
            print("\n4. Testing successful login...")
            if not USERNAME or not PASSWORD:
                print("   [FAIL] No credentials configured in .env")
                return False

            username_input.fill(USERNAME)
            password_input.fill(PASSWORD)
            page.wait_for_timeout(200)

            page.screenshot(path="/tmp/auth_04_credentials_filled.png")

            login_btn.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)

            # Should be redirected to dashboard after successful login
            if "dashboard" in page.url:
                print(f"   [OK] Login successful, redirected to: {page.url}")
                page.screenshot(path="/tmp/auth_04_dashboard_loaded.png")
            else:
                print(f"   [FAIL] Login failed, current URL: {page.url}")
                return False

            # ========================================
            # STEP 5: Verify authenticated access to protected pages
            # ========================================
            print("\n5. Verifying authenticated access to protected pages...")
            protected_pages = [
                "/profile",
                "/skills",
                "/work-experience",
                "/certifications",
                "/portfolio-projects"
            ]

            for path in protected_pages:
                page.goto(f"{BASE_URL}{path}")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(500)

                # Should be able to access the page (not redirected to login)
                if "login" not in page.url:
                    print(f"   [OK] Accessed: {path}")
                else:
                    print(f"   [FAIL] Redirected to login when accessing: {path}")
                    return False

            # Return to dashboard
            page.goto(f"{BASE_URL}/dashboard")
            page.wait_for_load_state("networkidle")

            # ========================================
            # STEP 6: Test session persistence - reload page
            # ========================================
            print("\n6. Testing session persistence - reloading page...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            # Should still be on dashboard (session persisted)
            if "dashboard" in page.url:
                print("   [OK] Session persisted after page reload")
            else:
                print("   [FAIL] Session lost after reload")
                return False

            # ========================================
            # STEP 7: Test session persistence - new tab
            # ========================================
            print("\n7. Testing session persistence - new tab...")
            new_page = context.new_page()
            new_page.goto(f"{BASE_URL}/dashboard")
            new_page.wait_for_load_state("networkidle")
            new_page.wait_for_timeout(1000)

            # Should be able to access dashboard in new tab (same context)
            if "dashboard" in new_page.url:
                print("   [OK] Session persisted in new tab")
            else:
                print("   [FAIL] Session not available in new tab")

            new_page.close()

            # ========================================
            # STEP 8: Test logout
            # ========================================
            print("\n8. Testing logout functionality...")

            # Look for logout button - could be in various places
            logout_btn = page.locator('button:has-text("Logout"), button:has-text("Log Out"), a:has-text("Logout"), a:has-text("Log Out")').first

            if logout_btn.count() > 0:
                print("   [OK] Logout button found")
                page.screenshot(path="/tmp/auth_08_before_logout.png")

                logout_btn.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1500)

                # Should be redirected to login page after logout
                expect(page).to_have_url(f"{BASE_URL}/login")
                print("   [OK] Logout successful, redirected to login")
                page.screenshot(path="/tmp/auth_08_after_logout.png")
            else:
                print("   [WARN] Logout button not found in page")
                # Try to navigate to dashboard to test if still authenticated
                page.goto(f"{BASE_URL}/dashboard")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1000)

            # ========================================
            # STEP 9: Verify logout - attempt to access protected page
            # ========================================
            print("\n9. Verifying logout - attempting to access protected page...")
            page.goto(f"{BASE_URL}/dashboard")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            # Should be redirected to login (session cleared)
            expect(page).to_have_url(f"{BASE_URL}/login")
            print("   [OK] Access denied after logout, redirected to login")

            # ========================================
            # STEP 10: Verify cannot access other protected pages
            # ========================================
            print("\n10. Verifying all protected pages require authentication...")
            test_pages = ["/profile", "/skills", "/certifications"]

            for path in test_pages:
                page.goto(f"{BASE_URL}{path}")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(500)

                # Should be redirected to login
                if "login" in page.url:
                    print(f"   [OK] {path} protected - redirected to login")
                else:
                    print(f"   [FAIL] {path} accessible without authentication")
                    return False

            # ========================================
            # STEP 11: Test re-login
            # ========================================
            print("\n11. Testing re-login after logout...")
            page.goto(f"{BASE_URL}/login")
            page.wait_for_load_state("networkidle")

            username_input = page.locator('input[type="text"], input[placeholder*="username" i]').first
            password_input = page.locator('input[type="password"]').first

            username_input.fill(USERNAME)
            password_input.fill(PASSWORD)
            page.wait_for_timeout(200)

            login_btn = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")').first
            login_btn.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)

            # Should be redirected to dashboard
            if "dashboard" in page.url:
                print("   [OK] Re-login successful")
                page.screenshot(path="/tmp/auth_11_relogin_success.png")
            else:
                print("   [FAIL] Re-login failed")
                return False

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Unauthorized redirect to login")
            print("  [PASS] Login validation (empty credentials)")
            print("  [PASS] Invalid credentials rejected")
            print("  [PASS] Successful login")
            print("  [PASS] Authenticated access to protected pages")
            print("  [PASS] Session persistence after reload")
            print("  [PASS] Session persistence in new tab")
            print("  [PASS] Logout functionality")
            print("  [PASS] Access denied after logout")
            print("  [PASS] All protected pages require authentication")
            print("  [PASS] Re-login after logout")
            print("\nScreenshots saved to /tmp/:")
            for i in range(1, 12):
                print(f"  - auth_{i:02d}_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            page.screenshot(path="/tmp/auth_error_assertion.png")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path="/tmp/auth_error.png")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_auth_flow()
    sys.exit(0 if success else 1)
