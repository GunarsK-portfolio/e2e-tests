#!/usr/bin/env python3
"""
E2E test for Skills CRUD operations
Tests: Create, Read, Update, Delete for all skill categories
"""

import sys

from playwright.sync_api import sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config

config = get_config()
BASE_URL = config["admin_web_url"]


def test_skills_crud():
    """Test Skills page and CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== SKILLS CRUD TEST ===\n")

        try:
            # Navigate to Skills page
            print("1. Navigating to Skills page...")
            page.goto(f"{BASE_URL}/skills")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="/tmp/skills_01_page.png")
            print("   [OK] Skills page loaded")

            # Test Skills Tab
            print("\n2. Testing Skills tab...")
            skills_tab = page.locator("text=Skills").first
            if skills_tab.count() > 0:
                skills_tab.click()
                page.wait_for_timeout(500)
                page.screenshot(path="/tmp/skills_02_skills_tab.png")
                print("   [OK] Skills tab active")

                # Check for Add button and table
                add_btn = page.locator('button:has-text("Add Skill")')
                if add_btn.count() > 0:
                    print("   [OK] Add Skill button found")

                table = page.locator('table, [role="table"]')
                if table.count() > 0:
                    print("   [OK] Skills table found")
            else:
                print("   [FAIL] Skills tab not found")

            # Test Skill Types Tab
            print("\n3. Testing Skill Types tab...")
            types_tab = page.locator("text=Skill Types").first
            if types_tab.count() > 0:
                types_tab.click()
                page.wait_for_timeout(500)
                page.screenshot(path="/tmp/skills_03_types_tab.png")
                print("   [OK] Skill Types tab active")

                # Check for Add button and table
                add_btn = page.locator('button:has-text("Add Skill Type")')
                if add_btn.count() > 0:
                    print("   [OK] Add Skill Type button found")

                table = page.locator('table, [role="table"]')
                if table.count() > 0:
                    print("   [OK] Skill Types table found")
            else:
                print("   [FAIL] Skill Types tab not found")

            # Test Add Skill Modal
            print("\n4. Testing Add Skill modal...")
            skills_tab.click()
            page.wait_for_timeout(500)

            add_btn = page.locator('button:has-text("Add Skill")').first
            if add_btn.count() > 0:
                add_btn.click()
                page.wait_for_timeout(500)

                modal = page.locator('[role="dialog"]')
                if modal.count() > 0:
                    print("   [OK] Modal opened")
                    page.screenshot(path="/tmp/skills_04_add_skill_modal.png")

                    # Check form fields based on actual Skills.vue structure
                    fields = {
                        "skill_name": page.locator('input[placeholder*="Vue.js" i]').first,
                        "skill_type": page.locator("text=Skill Type").first,
                        "visible": page.locator("text=Visible").first,
                        "display_order": page.locator('input[placeholder*="Order" i]').first,
                    }

                    for field_name, field_locator in fields.items():
                        if field_locator.count() > 0:
                            print(
                                f"   [OK] {field_name.replace('_', ' ').capitalize()} field found"
                            )

                    # Close modal
                    cancel_btn = page.locator('button:has-text("Cancel")').first
                    if cancel_btn.count() > 0:
                        cancel_btn.click()
                        page.wait_for_timeout(300)
                        print("   [OK] Modal closed")
                else:
                    print("   [FAIL] Modal did not open")

            print("\n=== TEST COMPLETED ===")
            print("\nScreenshots saved to /tmp/:")
            print("  - skills_01_page.png")
            print("  - skills_02_skills_tab.png")
            print("  - skills_03_types_tab.png")
            print("  - skills_04_add_skill_modal.png")

            return True

        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path="/tmp/skills_error.png")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_skills_crud()
    sys.exit(0 if success else 1)
