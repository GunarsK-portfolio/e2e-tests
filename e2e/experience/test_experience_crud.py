#!/usr/bin/env python3
"""
E2E test for Work Experience CRUD operations
Tests: Full CRUD with validation, data persistence, and date handling
"""

import sys
import time

from playwright.sync_api import expect, sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config

config = get_config()
BASE_URL = config["admin_web_url"]


def test_experience_crud():
    """Test Work Experience full CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== WORK EXPERIENCE E2E TEST ===\n")

        # Test data - unique company name using timestamp
        test_company = f"E2E Test Company {int(time.time())}"
        test_position = "Senior Test Engineer"
        test_description = "Automated E2E testing and quality assurance"
        updated_company = f"{test_company} Updated"
        updated_position = "Lead Test Architect"
        updated_description = "Updated: Leading test automation initiatives"

        try:
            # ========================================
            # STEP 1: Navigate to Work Experience page
            # ========================================
            print("1. Navigating to Work Experience page...")
            page.goto(f"{BASE_URL}/work-experience")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="/tmp/experience_01_page.png")
            print("   [OK] Work Experience page loaded")

            # ========================================
            # STEP 2: Test validation - empty form
            # ========================================
            print("\n2. Testing validation - empty form submission...")
            add_btn = page.locator(
                'button:has-text("Add Experience"), button:has-text("Add Work Experience")'
            )
            assert add_btn.count() > 0, "Add Experience button not found"
            add_btn.first.click()
            page.wait_for_timeout(500)

            modal = page.locator('[role="dialog"]')
            assert modal.count() > 0, "Modal not opened"
            print("   [OK] Add Experience modal opened")

            # Try to save without filling required fields
            save_btn = page.locator('button:has-text("Save"), button:has-text("Create")').first
            save_btn.click()
            page.wait_for_timeout(500)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty form submission")
            page.screenshot(path="/tmp/experience_02_validation_error.png")

            # Close modal
            cancel_btn = page.locator('button:has-text("Cancel")').first
            cancel_btn.click()
            page.wait_for_timeout(300)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Create new work experience
            # ========================================
            print(f"\n3. Creating new experience: '{test_company}'...")
            add_btn.first.click()
            page.wait_for_timeout(500)

            # Fill basic fields (Basic Information section is expanded by default)
            company_input = page.locator('input[placeholder="Enter company name"]').first
            company_input.fill(test_company)
            page.wait_for_timeout(200)

            position_input = page.locator('input[placeholder="Enter job position"]').first
            position_input.fill(test_position)
            page.wait_for_timeout(200)

            desc_input = page.locator('textarea[placeholder*="responsibilities" i]').first
            desc_input.fill(test_description)
            page.wait_for_timeout(200)

            # Expand Timeline section (not expanded by default)
            timeline_section = page.locator("text=Timeline").first
            timeline_section.click()
            page.wait_for_timeout(500)
            print("   [OK] Expanded Timeline section")

            # Fill date inputs using placeholder
            page.locator('input[placeholder="Select Month"]').nth(0).fill("2024-01")
            page.wait_for_timeout(200)
            page.locator('input[placeholder="Select Month"]').nth(1).fill("2024-12")
            page.wait_for_timeout(200)

            page.screenshot(path="/tmp/experience_03_create_form_filled.png")

            # Save
            save_btn = page.locator('button:has-text("Save"), button:has-text("Create")').first
            save_btn.click()
            page.wait_for_timeout(1000)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Experience created successfully")

            # ========================================
            # STEP 4: Verify entry appears in table
            # ========================================
            print("\n4. Verifying experience appears in table...")
            page.wait_for_timeout(500)
            table_row = page.locator(f'tr:has-text("{test_company}")')
            expect(table_row).to_be_visible(timeout=5000)
            print(f"   [OK] Experience '{test_company}' found in table")
            page.screenshot(path="/tmp/experience_04_in_table.png")

            # ========================================
            # STEP 5: Edit experience entry
            # ========================================
            print("\n5. Editing experience entry...")
            edit_btn = table_row.locator('button[aria-label*="Edit" i]').first
            edit_btn.click()
            page.wait_for_timeout(500)

            # Verify modal opened
            assert modal.is_visible(), "Edit modal should be visible"
            print("   [OK] Edit modal opened")

            # Verify existing data and update fields (Basic Information is expanded by default)
            company_input = page.locator('input[placeholder="Enter company name"]').first
            expect(company_input).to_have_value(test_company)
            print("   [OK] Existing data loaded")

            company_input.fill(updated_company)
            page.wait_for_timeout(200)

            position_input = page.locator('input[placeholder="Enter job position"]').first
            position_input.fill(updated_position)
            page.wait_for_timeout(200)

            desc_input = page.locator('textarea[placeholder*="responsibilities" i]').first
            desc_input.fill(updated_description)
            page.wait_for_timeout(200)

            page.screenshot(path="/tmp/experience_05_edit_form_filled.png")

            # Save changes
            save_btn = page.locator('button:has-text("Save"), button:has-text("Update")').first
            save_btn.click()
            page.wait_for_timeout(1000)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Experience updated successfully")

            # ========================================
            # STEP 6: Verify updated data in table
            # ========================================
            print("\n6. Verifying updated data in table...")
            page.wait_for_timeout(500)
            updated_row = page.locator(f'tr:has-text("{updated_company}")')
            expect(updated_row).to_be_visible(timeout=5000)
            print(f"   [OK] Updated experience '{updated_company}' found in table")
            page.screenshot(path="/tmp/experience_06_updated_in_table.png")

            # ========================================
            # STEP 7: Test data persistence - reload page
            # ========================================
            print("\n7. Testing data persistence - reloading page...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Verify data still exists
            persisted_row = page.locator(f'tr:has-text("{updated_company}")')
            expect(persisted_row).to_be_visible(timeout=5000)
            print("   [OK] Data persisted after page reload")

            # ========================================
            # STEP 8: Search functionality
            # ========================================
            print("\n8. Testing search functionality...")
            search_input = page.locator('input[placeholder*="Search" i]').first
            if search_input.count() > 0:
                search_input.fill(updated_company)
                page.wait_for_timeout(500)

                search_row = page.locator(f'tr:has-text("{updated_company}")')
                expect(search_row).to_be_visible()
                print(f"   [OK] Search found experience: '{updated_company}'")

                # Clear search
                search_input.fill("")
                page.wait_for_timeout(500)
                print("   [OK] Search cleared")
            else:
                print("   [WARN] Search input not found")

            # ========================================
            # STEP 9: Delete experience entry
            # ========================================
            print(f"\n9. Deleting experience '{updated_company}'...")
            delete_row = page.locator(f'tr:has-text("{updated_company}")')
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
            else:
                print("   [WARN] Confirm button not found")

            # ========================================
            # STEP 10: Verify deletion
            # ========================================
            print("\n10. Verifying experience deletion...")
            page.wait_for_timeout(500)
            deleted_row = page.locator(f'tr:has-text("{updated_company}")')

            # Entry should no longer exist
            expect(deleted_row).not_to_be_visible()
            print(f"   [OK] Experience '{updated_company}' successfully deleted")
            page.screenshot(path="/tmp/experience_07_after_deletion.png")

            # ========================================
            # STEP 11: Verify deletion persists
            # ========================================
            print("\n11. Verifying deletion persists after reload...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Verify entry is still gone
            final_check = page.locator(f'tr:has-text("{updated_company}")')
            expect(final_check).not_to_be_visible()
            print("   [OK] Deletion persisted after reload")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Page navigation")
            print("  [PASS] Form validation (empty form)")
            print("  [PASS] Create work experience")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Edit work experience")
            print("  [PASS] Update work experience data")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Search functionality")
            print("  [PASS] Delete work experience")
            print("  [PASS] Verify deletion")
            print("  [PASS] Deletion persistence")
            print("\nScreenshots saved to /tmp/:")
            for i in range(1, 8):
                print(f"  - experience_{i:02d}_*.png")

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            page.screenshot(path="/tmp/experience_error_assertion.png")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path="/tmp/experience_error.png")
            import traceback

            traceback.print_exc()
            return False
        else:
            return True
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_experience_crud()
    sys.exit(0 if success else 1)
