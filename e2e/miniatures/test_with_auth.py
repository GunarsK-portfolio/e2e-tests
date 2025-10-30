#!/usr/bin/env python3
"""
E2E test for Miniatures with authentication
"""

import sys

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:81"


def test_miniatures_with_auth():
    """Test Miniatures page with authentication"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("\n=== MINIATURES E2E TEST (WITH AUTH) ===\n")

        try:
            # Step 1: Login
            print("1. Logging in...")
            page.goto(f"{BASE_URL}/login")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="/tmp/auth_01_login.png")

            # Fill login form (you need to provide credentials)
            print("   Please enter credentials in the browser window...")
            print("   (Or press Enter to skip and use existing session)")
            input()

            # Check if we're on dashboard
            if "dashboard" not in page.url:
                print("   Attempting to navigate to dashboard...")
                page.goto(f"{BASE_URL}/dashboard")
                page.wait_for_load_state("networkidle")

            if "login" in page.url:
                print("   [FAIL] Still on login page - authentication required")
                print("   Please login manually in the browser, then press Enter")
                input()

            page.screenshot(path="/tmp/auth_02_after_login.png")
            print("   [OK] Authenticated")

            # Step 2: Navigate to Miniatures
            print("\n2. Navigating to Miniatures...")
            page.goto(f"{BASE_URL}/miniatures")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            page.screenshot(path="/tmp/auth_03_miniatures.png")
            print("   [OK] Miniatures page loaded")

            # Step 3: Check for tabs
            print("\n3. Checking for tabs...")

            # Look for tab elements
            projects_tab = page.locator(
                '[role="tab"]:has-text("Projects"), .n-tab:has-text("Projects"), text=Projects'
            ).first
            themes_tab = page.locator(
                '[role="tab"]:has-text("Themes"), .n-tab:has-text("Themes"), text=Themes'
            ).first
            paints_tab = page.locator(
                '[role="tab"]:has-text("Paints"), .n-tab:has-text("Paints"), text=Paints'
            ).first

            print(f"   Projects tab: {'Found' if projects_tab.count() > 0 else 'Not found'}")
            print(f"   Themes tab: {'Found' if themes_tab.count() > 0 else 'Not found'}")
            print(f"   Paints tab: {'Found' if paints_tab.count() > 0 else 'Not found'}")

            # Print page text for debugging
            print("\n   Page content (first 500 chars):")
            print("   " + page.text_content("body")[:500])

            # Step 4: Try to click Paints tab
            if paints_tab.count() > 0:
                print("\n4. Clicking Paints tab...")
                paints_tab.click()
                page.wait_for_timeout(1500)
                page.screenshot(path="/tmp/auth_04_paints_tab.png", full_page=True)
                print("   [OK] Paints tab clicked")

                # Check for Add Paint button
                add_paint = page.locator('button:has-text("Add Paint")')
                if add_paint.count() > 0:
                    print("   [OK] Add Paint button found")

                    # Check for table
                    table = page.locator('table, [role="table"]')
                    if table.count() > 0:
                        print("   [OK] Table found")
                else:
                    print("   [WARN] Add Paint button not found")
            else:
                print("\n4. [SKIP] Cannot test Paints tab - tab not found")

            print("\n=== TEST COMPLETED ===")
            print("\nScreenshots saved to /tmp/ with prefix 'auth_'")

            return True

        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path="/tmp/auth_error.png")
            import traceback

            traceback.print_exc()
            return False
        finally:
            print("\nPress Enter to close browser...")
            input()
            browser.close()


if __name__ == "__main__":
    success = test_miniatures_with_auth()
    sys.exit(0 if success else 1)
