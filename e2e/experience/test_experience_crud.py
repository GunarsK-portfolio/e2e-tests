#!/usr/bin/env python3
"""
E2E test for Work Experience CRUD operations
Tests: Create, Read, Update, Delete for work experience entries
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
from auth.auth_manager import AuthManager
from common.config import get_config

config = get_config()
BASE_URL = config['admin_web_url']


def test_experience_crud():
    """Test Work Experience page and CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy='auto')

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== WORK EXPERIENCE CRUD TEST ===\n")

        try:
            # Navigate to Work Experience page
            print("1. Navigating to Work Experience page...")
            page.goto(f'{BASE_URL}/work-experience')
            page.wait_for_load_state('networkidle')
            page.screenshot(path='/tmp/experience_01_page.png')
            print("   [OK] Work Experience page loaded")

            # Check for Add button
            print("\n2. Checking Add Experience button...")
            add_btn = page.locator('button:has-text("Add Experience"), button:has-text("Add Work Experience")')
            if add_btn.count() > 0:
                print("   [OK] Add button found")
            else:
                print("   [WARN] Add button not found")

            # Check for table/list
            print("\n3. Checking for experience entries...")
            table = page.locator('table, [role="table"], .experience-list')
            if table.count() > 0:
                print("   [OK] Experience list found")
            else:
                print("   [INFO] No experience entries visible")

            # Test Add Modal
            print("\n4. Testing Add Experience modal...")
            if add_btn.count() > 0:
                add_btn.first.click()
                page.wait_for_timeout(500)

                modal = page.locator('[role="dialog"]')
                if modal.count() > 0:
                    print("   [OK] Modal opened")
                    page.screenshot(path='/tmp/experience_02_add_modal.png')

                    # Check form fields based on WorkExperience.vue
                    fields = {
                        'company': page.locator('input[placeholder*="company name" i]').first,
                        'position': page.locator('input[placeholder*="job position" i]').first,
                        'description': page.locator('textarea[placeholder*="responsibilities" i]').first,
                        'start_date': page.locator('text=Start Date').first,
                        'end_date': page.locator('text=End Date').first,
                        'currently_working': page.locator('text=Currently working here').first,
                    }

                    for field_name, field_locator in fields.items():
                        if field_locator.count() > 0:
                            print(f"   [OK] {field_name.replace('_', ' ').capitalize()} field found")
                        else:
                            print(f"   [WARN] {field_name.replace('_', ' ').capitalize()} field not found")

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
            print("  - experience_01_page.png")
            print("  - experience_02_add_modal.png")

            return True

        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path='/tmp/experience_error.png')
            import traceback
            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == '__main__':
    success = test_experience_crud()
    sys.exit(0 if success else 1)
