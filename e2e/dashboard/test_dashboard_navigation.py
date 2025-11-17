#!/usr/bin/env python3
"""
E2E test for Dashboard Navigation
Tests: Dashboard layout, navigation cards, routing to all pages
"""

import sys

from playwright.sync_api import expect, sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config
from e2e.common.helpers import click_dashboard_card_button, find_dashboard_card, take_screenshot

config = get_config()
BASE_URL = config["admin_web_url"]


def navigate_to_dashboard(page):
    """Navigate to dashboard (local helper for this test)"""
    page.goto(f"{BASE_URL}/dashboard")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(500)


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
            navigate_to_dashboard(page)
            take_screenshot(page, "dashboard_01_page", "Dashboard page loaded")
            print("   [OK] Dashboard page loaded")

            # ========================================
            # STEP 2: Verify Dashboard title and structure
            # ========================================
            print("\n2. Verifying Dashboard structure...")

            # Check for page title
            page_title = page.locator("text=Content Management").first
            expect(page_title).to_be_visible()
            print("   [OK] Dashboard title 'Content Management' found")

            # Check for navigation cards
            cards = page.locator(".n-card")
            expect(cards).to_have_count(6)
            print(f"   [OK] Found {cards.count()} navigation cards")

            take_screenshot(page, "dashboard_02_structure", "Dashboard structure verified")

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
                navigate_to_dashboard(page)

                # Verify card exists
                card = find_dashboard_card(page, nav_test["name"])
                expect(card).to_be_visible()

                # Click the navigation button in the card
                click_dashboard_card_button(page, nav_test["name"], nav_test["button_text"])

                # Verify navigation occurred
                expect(page).to_have_url(f"{BASE_URL}{nav_test['url']}")
                print(f"   [OK] Navigated to {nav_test['name']}: {page.url}")

                screenshot_name = (
                    f"dashboard_{step_num:02d}_{nav_test['name'].lower().replace(' ', '_')}"
                )
                take_screenshot(page, screenshot_name, f"Navigated to {nav_test['name']}")

                step_num += 1

            # ========================================
            # STEP 9: Return to Dashboard and verify
            # ========================================
            print(f"\n{step_num}. Returning to Dashboard...")
            navigate_to_dashboard(page)

            # Verify we're on dashboard
            expect(page).to_have_url(f"{BASE_URL}/dashboard")
            print(f"   [OK] Successfully returned to Dashboard: {page.url}")
            take_screenshot(page, "dashboard_09_final", "Returned to Dashboard")

            # ========================================
            # STEP 10: Test direct URL access to root
            # ========================================
            print(f"\n{step_num + 1}. Testing root URL redirect to Dashboard...")
            page.goto(f"{BASE_URL}/")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Root should redirect to dashboard
            expect(page).to_have_url(f"{BASE_URL}/dashboard")
            print("   [OK] Root URL redirects to Dashboard")

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
            print("\nScreenshots saved to /tmp/test_dashboard_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "dashboard_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "dashboard_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_dashboard_navigation()
    sys.exit(0 if success else 1)
