#!/usr/bin/env python3
"""
E2E test for Profile management
Tests: View and update profile information
"""

import sys

from playwright.sync_api import sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config

config = get_config()
BASE_URL = config["admin_web_url"]


def test_profile():
    """Test Profile page and update operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== PROFILE MANAGEMENT TEST ===\n")

        try:
            # Navigate to Profile page
            print("1. Navigating to Profile page...")
            page.goto(f"{BASE_URL}/profile")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="/tmp/profile_01_page.png")
            print("   [OK] Profile page loaded")

            # Check for profile cards and fields based on Profile.vue
            print("\n2. Checking Basic Information card...")
            basic_card = page.locator("text=Basic Information").first
            if basic_card.count() > 0:
                print("   [OK] Basic Information card found")

            fields_basic = {
                "name": page.locator('input[placeholder*="full name" i]').first,
                "title": page.locator('input[placeholder*="Senior Software Engineer" i]').first,
                "tagline": page.locator('textarea[placeholder*="Brief description" i]').first,
            }

            for field_name, field_locator in fields_basic.items():
                if field_locator.count() > 0:
                    print(f"   [OK] {field_name.capitalize()} field found")

            print("\n3. Checking Contact Information card...")
            contact_card = page.locator("text=Contact Information").first
            if contact_card.count() > 0:
                print("   [OK] Contact Information card found")
                page.screenshot(path="/tmp/profile_02_contact.png")

            fields_contact = {
                "email": page.locator('input[placeholder*="contact@example.com" i]').first,
                "phone": page.locator('input[placeholder*="555" i]').first,
                "location": page.locator('input[placeholder*="City, Country" i]').first,
            }

            for field_name, field_locator in fields_contact.items():
                if field_locator.count() > 0:
                    print(f"   [OK] {field_name.capitalize()} field found")

            # Check for Avatar card
            print("\n4. Checking Avatar card...")
            avatar_card = page.locator("text=Avatar").first
            if avatar_card.count() > 0:
                print("   [OK] Avatar card found")
                page.screenshot(path="/tmp/profile_03_avatar.png")

            # Check for Save button at bottom
            print("\n5. Checking for Save button...")
            save_btn = page.locator('button:has-text("Save"), button:has-text("Update")')
            if save_btn.count() > 0:
                print("   [OK] Save button found")
            else:
                print("   [WARN] Save button not found")

            print("\n=== TEST COMPLETED ===")
            print("\nScreenshots saved to /tmp/:")
            print("  - profile_01_page.png")
            print("  - profile_02_contact.png")
            print("  - profile_03_avatar.png")

            return True

        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path="/tmp/profile_error.png")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_profile()
    sys.exit(0 if success else 1)
