#!/usr/bin/env python3
"""
Simple E2E test for Miniatures functionality
Windows-compatible (no emojis)
"""

import sys

from playwright.sync_api import sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config

config = get_config()
BASE_URL = config["admin_web_url"]


def test_miniatures():
    """Test Miniatures page and tabs"""
    with sync_playwright() as p:
        auth_manager = AuthManager()

        print("\n=== MINIATURES E2E TEST ===\n")
        print("Authenticating...")

        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        try:
            # Step 1: Go to dashboard
            print("\n1. Navigating to dashboard...")
            page.goto(f"{BASE_URL}/dashboard")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="/tmp/01_dashboard.png")
            print("   [OK] Dashboard loaded")

            # Step 2: Navigate to Miniatures
            print("\n2. Navigating to Miniatures...")
            page.goto(f"{BASE_URL}/miniatures")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="/tmp/02_miniatures.png")
            print("   [OK] Miniatures page loaded")

            # Step 3: Check Projects tab
            print("\n3. Checking Projects tab...")
            projects_tab = page.locator("text=Projects").first
            if projects_tab.count() > 0:
                print("   [OK] Projects tab found")
                add_project = page.locator('button:has-text("Add Project")')
                if add_project.count() > 0:
                    print("   [OK] Add Project button found")
            else:
                print("   [FAIL] Projects tab not found")

            # Step 4: Switch to Themes
            print("\n4. Testing Themes tab...")
            themes_tab = page.locator("text=Themes").first
            if themes_tab.count() > 0:
                themes_tab.click()
                page.wait_for_timeout(500)
                page.screenshot(path="/tmp/03_themes.png")
                print("   [OK] Themes tab clicked")

                add_theme = page.locator('button:has-text("Add Theme")')
                if add_theme.count() > 0:
                    print("   [OK] Add Theme button found")
            else:
                print("   [FAIL] Themes tab not found")

            # Step 5: Switch to Paints
            print("\n5. Testing Paints tab...")
            paints_tab = page.locator("text=Paints").first
            if paints_tab.count() > 0:
                paints_tab.click()
                page.wait_for_timeout(1000)  # Wait for data
                page.screenshot(path="/tmp/04_paints.png")
                print("   [OK] Paints tab clicked")

                add_paint = page.locator('button:has-text("Add Paint")')
                if add_paint.count() > 0:
                    print("   [OK] Add Paint button found")

                # Check for table
                table = page.locator('table, [role="table"]')
                if table.count() > 0:
                    print("   [OK] Paints table found")
            else:
                print("   [FAIL] Paints tab not found")

            # Step 6: Test Add Paint modal
            print("\n6. Testing Add Paint modal...")
            if add_paint.count() > 0:
                add_paint.click()
                page.wait_for_timeout(500)

                modal = page.locator('[role="dialog"]')
                if modal.count() > 0:
                    print("   [OK] Modal opened")
                    page.screenshot(path="/tmp/05_modal.png")

                    # Check fields
                    name_input = page.locator('input[placeholder*="paint name" i]').first
                    if name_input.count() > 0:
                        print("   [OK] Name field found")

                    # Close modal
                    cancel = page.locator('button:has-text("Cancel")').first
                    if cancel.count() > 0:
                        cancel.click()
                        print("   [OK] Modal closed")
                else:
                    print("   [FAIL] Modal did not open")

            print("\n=== TEST COMPLETED ===")
            print("\nScreenshots saved to /tmp/:")
            print("  - 01_dashboard.png")
            print("  - 02_miniatures.png")
            print("  - 03_themes.png")
            print("  - 04_paints.png")
            print("  - 05_modal.png")

            return True

        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path="/tmp/error.png")
            import traceback

            traceback.print_exc()
            return False
        finally:
            print("\nPress Enter to close browser...")
            input()
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_miniatures()
    sys.exit(0 if success else 1)
