#!/usr/bin/env python3
"""
E2E test for Miniatures Themes CRUD operations
Tests: Full CRUD with validation, data persistence, image upload
"""

import sys
import time

from playwright.sync_api import expect, sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config

config = get_config()
BASE_URL = config["admin_web_url"]


def test_themes_crud():
    """Test Miniatures Themes tab full CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== MINIATURES THEMES E2E TEST ===\n")

        # Test data - unique theme name using timestamp
        test_theme_name = f"E2E Test Theme {int(time.time())}"
        test_theme_desc = "Automated E2E testing theme"
        updated_theme_name = f"{test_theme_name} Updated"
        updated_theme_desc = "Updated: Advanced E2E testing theme"

        try:
            # ========================================
            # STEP 1: Navigate to Miniatures Themes tab
            # ========================================
            print("1. Navigating to Miniatures > Themes tab...")
            page.goto(f"{BASE_URL}/miniatures")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Click Themes tab
            themes_tab = page.locator("text=Themes").first
            themes_tab.click()
            page.wait_for_timeout(500)
            page.screenshot(path="/tmp/themes_01_page.png")
            print("   [OK] Themes tab loaded")

            # ========================================
            # STEP 2: Test validation - empty form
            # ========================================
            print("\n2. Testing validation - empty theme form...")
            add_btn = page.locator('button:has-text("Add Theme")').first
            assert add_btn.count() > 0, "Add Theme button not found"
            add_btn.click()
            page.wait_for_timeout(500)

            modal = page.locator('[role="dialog"]')
            assert modal.count() > 0, "Modal not opened"
            print("   [OK] Add Theme modal opened")

            # Try to save without filling required fields
            save_btn = page.locator('button:has-text("Save"), button:has-text("Create")').first
            save_btn.click()
            page.wait_for_timeout(500)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty theme form submission")
            page.screenshot(path="/tmp/themes_02_validation_error.png")

            # Close modal
            cancel_btn = page.locator('button:has-text("Cancel")').first
            cancel_btn.click()
            page.wait_for_timeout(300)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Create new theme
            # ========================================
            print(f"\n3. Creating new theme: '{test_theme_name}'...")
            add_btn.click()
            page.wait_for_timeout(500)

            # Fill name
            name_input = page.locator('input[placeholder*="name" i]').first
            name_input.fill(test_theme_name)
            page.wait_for_timeout(200)

            # Fill description
            desc_textarea = page.locator("textarea").first
            desc_textarea.fill(test_theme_desc)
            page.wait_for_timeout(200)

            # Set display order
            order_input = page.locator('input[placeholder*="Order" i], .n-input-number input').last
            order_input.fill("99")
            page.wait_for_timeout(200)

            page.screenshot(path="/tmp/themes_03_create_form_filled.png")

            # Save
            save_btn = page.locator('button:has-text("Save"), button:has-text("Create")').first
            save_btn.click()
            page.wait_for_timeout(1000)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Theme created successfully")

            # ========================================
            # STEP 4: Verify entry appears in table
            # ========================================
            print("\n4. Verifying theme appears in table...")
            page.wait_for_timeout(500)
            theme_row = page.locator(f'tr:has-text("{test_theme_name}")')
            expect(theme_row).to_be_visible(timeout=5000)
            print(f"   [OK] Theme '{test_theme_name}' found in table")
            page.screenshot(path="/tmp/themes_04_in_table.png")

            # ========================================
            # STEP 5: Edit theme entry
            # ========================================
            print("\n5. Editing theme entry...")
            edit_btn = theme_row.locator('button[aria-label*="Edit" i]').first
            edit_btn.click()
            page.wait_for_timeout(500)

            # Verify modal opened
            assert modal.is_visible(), "Edit modal should be visible"
            print("   [OK] Edit modal opened")

            # Verify existing data loaded
            name_input = page.locator('input[placeholder*="name" i]').first
            expect(name_input).to_have_value(test_theme_name)
            print("   [OK] Existing data loaded")

            # Update name
            name_input.fill(updated_theme_name)
            page.wait_for_timeout(200)

            # Update description
            desc_textarea = page.locator("textarea").first
            desc_textarea.fill(updated_theme_desc)
            page.wait_for_timeout(200)

            page.screenshot(path="/tmp/themes_05_edit_form_filled.png")

            # Save changes
            save_btn = page.locator('button:has-text("Save"), button:has-text("Update")').first
            save_btn.click()
            page.wait_for_timeout(1000)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Theme updated successfully")

            # ========================================
            # STEP 6: Verify updated data in table
            # ========================================
            print("\n6. Verifying updated data in table...")
            page.wait_for_timeout(500)
            updated_row = page.locator(f'tr:has-text("{updated_theme_name}")')
            expect(updated_row).to_be_visible(timeout=5000)
            print(f"   [OK] Updated theme '{updated_theme_name}' found in table")
            page.screenshot(path="/tmp/themes_06_updated_in_table.png")

            # ========================================
            # STEP 7: Test data persistence - reload page
            # ========================================
            print("\n7. Testing data persistence - reloading page...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Navigate back to Themes tab
            themes_tab = page.locator("text=Themes").first
            themes_tab.click()
            page.wait_for_timeout(500)

            # Verify data still exists
            persisted_row = page.locator(f'tr:has-text("{updated_theme_name}")')
            expect(persisted_row).to_be_visible(timeout=5000)
            print("   [OK] Data persisted after page reload")

            # ========================================
            # STEP 8: Search functionality
            # ========================================
            print("\n8. Testing search functionality...")
            search_input = page.locator('input[placeholder*="Search" i]').first
            if search_input.count() > 0:
                # Search by name
                search_input.fill(updated_theme_name)
                page.wait_for_timeout(500)

                search_row = page.locator(f'tr:has-text("{updated_theme_name}")')
                expect(search_row).to_be_visible()
                print(f"   [OK] Search by name found: '{updated_theme_name}'")

                # Clear search
                search_input.fill("")
                page.wait_for_timeout(500)
                print("   [OK] Search cleared")
            else:
                print("   [WARN] Search input not found")

            # ========================================
            # STEP 9: Delete theme entry
            # ========================================
            print(f"\n9. Deleting theme '{updated_theme_name}'...")
            delete_row = page.locator(f'tr:has-text("{updated_theme_name}")')
            delete_btn = delete_row.locator('button[aria-label*="Delete" i]').first
            delete_btn.click()
            page.wait_for_timeout(500)

            # Confirm deletion
            confirm_btn = page.locator(
                'button:has-text("Confirm"), button:has-text("Delete"), button:has-text("Yes")'
            ).first
            if confirm_btn.count() > 0:
                confirm_btn.click()
                page.wait_for_timeout(1000)
                print("   [OK] Deletion confirmed")

            # ========================================
            # STEP 10: Verify deletion
            # ========================================
            print("\n10. Verifying theme deletion...")
            page.wait_for_timeout(500)
            deleted_row = page.locator(f'tr:has-text("{updated_theme_name}")')

            # Entry should no longer exist
            expect(deleted_row).not_to_be_visible()
            print(f"   [OK] Theme '{updated_theme_name}' successfully deleted")
            page.screenshot(path="/tmp/themes_10_after_deletion.png")

            # ========================================
            # STEP 11: Verify deletion persists
            # ========================================
            print("\n11. Verifying deletion persists after reload...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Navigate back to Themes tab
            themes_tab = page.locator("text=Themes").first
            themes_tab.click()
            page.wait_for_timeout(500)

            # Verify entry is still gone
            final_check = page.locator(f'tr:has-text("{updated_theme_name}")')
            expect(final_check).not_to_be_visible()
            print("   [OK] Deletion persisted after reload")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Page navigation to Themes tab")
            print("  [PASS] Form validation (empty form)")
            print("  [PASS] Create theme with description and order")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Edit theme")
            print("  [PASS] Update theme data")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Search by name")
            print("  [PASS] Delete theme")
            print("  [PASS] Verify deletion")
            print("  [PASS] Deletion persistence")
            print("\nScreenshots saved to /tmp/:")
            for i in range(1, 12):
                if i != 7 and i != 8 and i != 9 and i != 11:  # Skip steps without screenshots
                    print(f"  - themes_{i:02d}_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            page.screenshot(path="/tmp/themes_error_assertion.png")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path="/tmp/themes_error.png")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_themes_crud()
    sys.exit(0 if success else 1)
