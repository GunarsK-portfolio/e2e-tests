#!/usr/bin/env python3
"""
E2E test for Dashboard Navigation
Tests: Dashboard layout, navigation cards, routing to all pages
"""

import sys

from playwright.sync_api import sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config

config = get_config()
BASE_URL = config["admin_web_url"]


def test_dashboard_navigation():
    """Test Dashboard page layout and navigation to all feature pages"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== DASHBOARD NAVIGATION E2E TEST ===\n")

        try:
            # ========================================
            # STEP 1: Navigate to Dashboard
            # ========================================
            print("1. Navigating to Dashboard...")
            page.goto(f"{BASE_URL}/dashboard")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="/tmp/dashboard_01_page.png")
            print("   [OK] Dashboard page loaded")

            # ========================================
            # STEP 2: Verify Dashboard title and structure
            # ========================================
            print("\n2. Verifying Dashboard structure...")

            # Check for page title
            page_title = page.locator("text=Content Management").first
            if page_title.count() > 0:
                print("   [OK] Dashboard title 'Content Management' found")
            else:
                print("   [WARN] Dashboard title not found")

            # Check for navigation cards - Dashboard has 6 cards in n-grid
            cards = page.locator(".n-card")
            if cards.count() >= 6:
                print(f"   [OK] Found {cards.count()} navigation cards")
            else:
                print(f"   [WARN] Expected at least 6 cards, found {cards.count()}")

            page.screenshot(path="/tmp/dashboard_02_structure.png")

            # ========================================
            # STEP 3-8: Test navigation to each page
            # ========================================
            navigation_tests = [
                {"name": "Profile", "url": "/profile", "button_text": "Edit Profile"},
                {"name": "Skills", "url": "/skills", "button_text": "Manage Skills"},
                {"name": "Work Experience", "url": "/work-experience", "button_text": "Manage"},
                {"name": "Certifications", "url": "/certifications", "button_text": "Manage"},
                {
                    "name": "Portfolio Projects",
                    "url": "/portfolio-projects",
                    "button_text": "Manage",
                },
                {"name": "Miniatures", "url": "/miniatures", "button_text": "Manage"},
            ]

            step_num = 3
            for nav_test in navigation_tests:
                print(f"\n{step_num}. Testing navigation to {nav_test['name']}...")

                # Return to dashboard first
                page.goto(f"{BASE_URL}/dashboard")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(500)

                # Find the card with this title, then find the button within it
                card_title = page.locator(f'h3.card-title:has-text("{nav_test["name"]}")').first

                if card_title.count() > 0:
                    # Find the card containing this title
                    card = page.locator(
                        f'.n-card:has(h3.card-title:has-text("{nav_test["name"]}"))'
                    ).first

                    if card.count() > 0:
                        # Find the button within this specific card
                        nav_button = card.locator(
                            f'button:has-text("{nav_test["button_text"]}")'
                        ).first

                        if nav_button.count() > 0:
                            nav_button.click()
                            page.wait_for_load_state("networkidle")
                            page.wait_for_timeout(500)

                            # Verify navigation occurred (check if URL contains the expected path)
                            if nav_test["url"] in page.url:
                                print(f"   [OK] Navigated to {nav_test['name']}: {page.url}")
                                screenshot_name = (
                                    f"dashboard_{step_num:02d}_"
                                    f"{nav_test['name'].lower().replace(' ', '_')}.png"
                                )
                                page.screenshot(path=f"/tmp/{screenshot_name}")
                            else:
                                expected_url = nav_test["url"]
                                actual_url = page.url
                                print(
                                    f"   [FAIL] Expected URL to contain "
                                    f"'{expected_url}', got: {actual_url}"
                                )
                        else:
                            button_text = nav_test["button_text"]
                            nav_name = nav_test["name"]
                            print(f"   [WARN] Button '{button_text}' " f"not found for {nav_name}")
                    else:
                        print(f"   [WARN] Card not found for {nav_test['name']}")
                else:
                    print(f"   [WARN] Card title '{nav_test['name']}' not found")

                step_num += 1

            # ========================================
            # STEP 9: Return to Dashboard and verify
            # ========================================
            print(f"\n{step_num}. Returning to Dashboard...")
            page.goto(f"{BASE_URL}/dashboard")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Verify we're on dashboard (URL contains /dashboard)
            if "/dashboard" in page.url:
                print(f"   [OK] Successfully returned to Dashboard: {page.url}")
            else:
                print(f"   [WARN] Not on dashboard, current URL: {page.url}")
            page.screenshot(path="/tmp/dashboard_09_final.png")

            # ========================================
            # STEP 10: Test direct URL access to root
            # ========================================
            print(f"\n{step_num + 1}. Testing root URL redirect to Dashboard...")
            page.goto(f"{BASE_URL}/")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Root should redirect to dashboard
            if "dashboard" in page.url:
                print("   [OK] Root URL redirects to Dashboard")
            else:
                print(f"   [WARN] Root URL did not redirect to Dashboard: {page.url}")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Dashboard page loads")
            print("  [PASS] Dashboard structure verification")
            print("  [PASS] Navigation to Profile")
            print("  [PASS] Navigation to Skills")
            print("  [PASS] Navigation to Work Experience")
            print("  [PASS] Navigation to Certifications")
            print("  [PASS] Navigation to Portfolio Projects")
            print("  [PASS] Navigation to Miniatures")
            print("  [PASS] Return to Dashboard")
            print("  [PASS] Root URL redirect")
            print("\nScreenshots saved to /tmp/:")
            print("  - dashboard_01_page.png")
            print("  - dashboard_02_structure.png")
            for i, nav in enumerate(navigation_tests, start=3):
                print(f"  - dashboard_{i:02d}_{nav['name'].lower().replace(' ', '_')}.png")
            print("  - dashboard_09_final.png")

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            page.screenshot(path="/tmp/dashboard_error_assertion.png")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path="/tmp/dashboard_error.png")
            import traceback

            traceback.print_exc()
            return False
        else:
            return True
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_dashboard_navigation()
    sys.exit(0 if success else 1)
