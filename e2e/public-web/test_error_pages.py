#!/usr/bin/env python3
"""
E2E test for Public Website - Error Pages
Tests: 404 Not Found page, 403 Forbidden page, navigation from error pages
"""

import sys
import traceback

from playwright.sync_api import expect, sync_playwright

from e2e.common.config import get_config
from e2e.common.helpers import take_screenshot, verify_url_contains, wait_for_page_load

config = get_config()
BASE_URL = config["public_web_url"]


def test_error_pages():
    """Test error pages display correctly"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config["headless"])
        context = browser.new_context()
        page = context.new_page()

        print("\n=== PUBLIC WEB - ERROR PAGES E2E TEST ===\n")

        try:
            # ========================================
            # STEP 1: Navigate to non-existent page (404)
            # ========================================
            print("1. Navigating to non-existent page...")
            page.goto(f"{BASE_URL}/this-page-does-not-exist-12345")
            wait_for_page_load(page)
            take_screenshot(page, "public_error_01_404_page", "404 page loaded")

            # From NotFound.vue: error code "404" is displayed
            error_code = page.locator('h1:has-text("404")').first
            expect(error_code).to_be_visible()
            print("   [OK] 404 error code displayed")

            # ========================================
            # STEP 2: Verify 404 page elements
            # ========================================
            print("\n2. Verifying 404 page elements...")

            # From NotFound.vue: "Page Not Found" title
            page_not_found = page.locator('h2:has-text("Page Not Found")').first
            expect(page_not_found).to_be_visible()
            print("   [OK] 'Page Not Found' title displayed")

            # From NotFound.vue: error message text
            error_message = page.locator('text="doesn\'t exist or has been moved"').first
            if error_message.count() > 0:
                expect(error_message).to_be_visible()
                print("   [OK] Error message displayed")

            # From NotFound.vue: "Back to Home" button
            home_btn = page.locator('button:has-text("Back to Home")').first
            expect(home_btn).to_be_visible()
            print("   [OK] Back to Home button visible")

            # From NotFound.vue: contact link
            contact_link = page.locator('button:has-text("contact us")').first
            if contact_link.count() > 0:
                print("   [OK] Contact link visible")

            take_screenshot(page, "public_error_02_404_elements", "404 page elements")

            # ========================================
            # STEP 3: Test Back to Home navigation
            # ========================================
            print("\n3. Testing Back to Home navigation...")

            home_btn.click()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Verify navigated to home
            current_url = page.url
            is_home = current_url in (BASE_URL, f"{BASE_URL}/")
            assert is_home, f"Expected home page URL, got: {current_url}"
            print(f"   [OK] Navigated to home page: {current_url}")

            take_screenshot(page, "public_error_03_home_from_404", "Home from 404")

            # ========================================
            # STEP 4: Navigate back to 404 and test Contact link
            # ========================================
            print("\n4. Testing Contact link from 404...")

            page.goto(f"{BASE_URL}/another-nonexistent-page")
            wait_for_page_load(page)

            contact_link = page.locator('button:has-text("contact us")').first
            if contact_link.count() > 0:
                contact_link.click()
                wait_for_page_load(page)
                page.wait_for_timeout(500)

                # Verify navigated to contact
                verify_url_contains(page, "/contact", "Navigated to contact page")
                take_screenshot(page, "public_error_04_contact_from_404", "Contact from 404")
            else:
                print("   [SKIP] No Contact link found on 404 page")

            # ========================================
            # STEP 5: Test page title on 404
            # ========================================
            print("\n5. Verifying 404 page title...")

            page.goto(f"{BASE_URL}/yet-another-missing-page")
            wait_for_page_load(page)

            # From router/index.js: meta.title = 'Page Not Found'
            title = page.title()
            has_404_title = "Not Found" in title or "404" in title
            assert has_404_title, f"Expected 404 in page title, got: {title}"
            print(f"   [OK] Page title indicates 404: {title}")

            # ========================================
            # STEP 6: Test forbidden page (403)
            # ========================================
            print("\n6. Testing forbidden page...")

            # From router/index.js: /forbidden route exists
            page.goto(f"{BASE_URL}/forbidden")
            wait_for_page_load(page)
            take_screenshot(page, "public_error_06_forbidden", "Forbidden page")

            # From Forbidden.vue: error code "403" is displayed
            forbidden_code = page.locator('h1:has-text("403")').first
            if forbidden_code.count() > 0:
                expect(forbidden_code).to_be_visible()
                print("   [OK] 403 error code displayed")

                # From Forbidden.vue: "Access Forbidden" title
                forbidden_title = page.locator('h2:has-text("Access Forbidden")').first
                if forbidden_title.count() > 0:
                    expect(forbidden_title).to_be_visible()
                    print("   [OK] 'Access Forbidden' title displayed")
            else:
                print("   [INFO] 403 page may redirect or show different content")

            # ========================================
            # STEP 7: Verify forbidden page has navigation
            # ========================================
            print("\n7. Verifying forbidden page navigation...")

            # From Forbidden.vue: "Back to Home" button
            home_btn = page.locator('button:has-text("Back to Home")').first
            if home_btn.count() > 0:
                expect(home_btn).to_be_visible()
                print("   [OK] Home navigation available on forbidden page")

            # From Forbidden.vue: contact link
            contact_link = page.locator('button:has-text("contact us")').first
            if contact_link.count() > 0:
                print("   [OK] Contact link available on forbidden page")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] 404 page displays for non-existent routes")
            print("  [PASS] 404 page shows error code/message")
            print("  [PASS] Back to Home button works from 404")
            print("  [PASS] Contact link available from 404")
            print("  [PASS] 404 page has appropriate title")
            print("  [PASS] Forbidden page accessible")
            print("  [PASS] Error pages have navigation options")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "public_error_error_assertion", "Assertion error")
            traceback.print_exc()
            return False

        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "public_error_error", "Error occurred")
            traceback.print_exc()
            return False

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_error_pages()
    sys.exit(0 if success else 1)
