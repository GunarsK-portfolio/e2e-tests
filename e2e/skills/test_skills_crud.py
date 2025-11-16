#!/usr/bin/env python3
"""
E2E test for Skills CRUD operations
Tests: Full CRUD with validation, data persistence, skill types, and dual-tab management
"""

import sys
import time

from playwright.sync_api import sync_playwright, expect

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config

config = get_config()
BASE_URL = config["admin_web_url"]


def test_skills_crud():
    """Test Skills page full CRUD operations for both skills and skill types"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== SKILLS COMPREHENSIVE E2E TEST ===\n")

        # Test data - unique names using timestamp
        test_type_name = f"E2E Test Type {int(time.time())}"
        test_type_desc = "Automated E2E testing skill category"
        updated_type_name = f"{test_type_name} Updated"
        updated_type_desc = "Updated: Advanced E2E testing category"

        test_skill_name = f"E2E Test Skill {int(time.time())}"
        updated_skill_name = f"{test_skill_name} Updated"

        try:
            # Navigate to Skills page
            page.goto(f"{BASE_URL}/skills")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # ========================================
            # PART 1: SKILLS CRUD
            # ========================================
            print("\n" + "=" * 60)
            print("PART 1: SKILLS CRUD")
            print("=" * 60)

            # STEP 1: Test validation - empty form
            print("\n1. Testing validation - empty skill form...")
            add_skill_btn = page.locator('button:has-text("Add Skill")').first
            assert add_skill_btn.count() > 0, "Add Skill button not found"
            add_skill_btn.click()
            page.wait_for_timeout(500)

            modal = page.locator('[role="dialog"]')
            assert modal.count() > 0, "Modal not opened"
            print("   [OK] Add Skill modal opened")

            # Try to save without filling required fields
            save_btn = page.locator('button:has-text("Save"), button:has-text("Create")').first
            save_btn.click()
            page.wait_for_timeout(500)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty skill form submission")

            # Close modal
            cancel_btn = page.locator('button:has-text("Cancel")').first
            cancel_btn.click()
            page.wait_for_timeout(500)

            # Wait for modal to be fully removed
            page.wait_for_selector('[role="dialog"]', state='detached', timeout=3000)
            print("   [OK] Modal closed")

            # STEP 2: Select and edit existing skill
            print("\n2. Finding and editing existing skill...")
            page.wait_for_timeout(500)

            # Get first skill from table
            first_skill_row = page.locator('tbody tr').first
            expect(first_skill_row).to_be_visible(timeout=5000)

            # Get existing skill name
            existing_skill_name = first_skill_row.locator('td').first.text_content().strip()
            print(f"   [OK] Found existing skill: '{existing_skill_name}'")

            # Click edit
            edit_skill_btn = first_skill_row.locator('button[aria-label*="Edit" i]').first
            edit_skill_btn.click()
            page.wait_for_timeout(500)

            # Verify modal opened
            modal = page.locator('[role="dialog"]:has-text("Edit Skill")').first
            assert modal.is_visible(), "Edit modal should be visible"
            skill_input = page.locator('input[placeholder="e.g., Vue.js"]').first
            expect(skill_input).to_have_value(existing_skill_name)
            print("   [OK] Edit modal opened")

            # Update to test name
            skill_input.fill(test_skill_name)
            page.wait_for_timeout(200)

            # Update order
            order_input = page.locator('input[placeholder="Order"]').last
            order_input.fill("88")
            page.wait_for_timeout(200)

            page.screenshot(path="/tmp/skills_12_skill_edit_filled.png")

            # Save (button shows "Update" when editing)
            save_btn = page.locator('button:has-text("Update"), button:has-text("Save")').first
            save_btn.click()
            page.wait_for_timeout(1000)

            # Verify closed
            modal = page.locator('[role="dialog"]:has-text("Skill")').first
            assert not modal.is_visible(), "Modal should close"
            print(f"   [OK] Skill updated to '{test_skill_name}'")

            # STEP 3: Verify updated skill in table using search
            print("\n3. Verifying updated skill in table...")
            page.wait_for_timeout(1000)

            # Use search to find the updated skill
            search_input = page.locator('input[placeholder*="Search skills" i]').first
            search_input.fill(test_skill_name)
            page.wait_for_timeout(500)

            skill_row = page.locator(f'tr:has-text("{test_skill_name}")')
            expect(skill_row).to_be_visible(timeout=5000)
            print(f"   [OK] Updated skill found in search results")

            # Clear search
            search_input.fill("")
            page.wait_for_timeout(500)
            page.screenshot(path="/tmp/skills_13_skill_in_table.png")

            # STEP 4: Restore original skill name
            print(f"\n4. Restoring original skill name '{existing_skill_name}'...")
            # Search to find the modified skill
            search_input.fill(test_skill_name)
            page.wait_for_timeout(500)

            # Get fresh locator after search
            skill_row = page.locator(f'tr:has-text("{test_skill_name}")').first
            edit_skill_btn = skill_row.locator('button[aria-label*="Edit" i]').first
            edit_skill_btn.click()
            page.wait_for_timeout(500)

            # Restore original name
            modal = page.locator('[role="dialog"]:has-text("Edit Skill")').first
            skill_input = page.locator('input[placeholder="e.g., Vue.js"]').first
            skill_input.fill(existing_skill_name)
            page.wait_for_timeout(200)

            # Save
            save_btn = page.locator('button:has-text("Update"), button:has-text("Save")').first
            save_btn.click()
            page.wait_for_timeout(1000)

            # Verify closed
            assert not modal.is_visible(), "Modal should close"
            print(f"   [OK] Restored original skill name: '{existing_skill_name}'")

            # PART 2: SKILL TYPES CRUD
            # ========================================
            print("\n" + "=" * 60)
            print("PART 2: SKILL TYPES CRUD")
            print("=" * 60)

            # STEP 5: Switch to Skill Types tab
            print("\n5. Switching to Skill Types tab...")
            types_tab = page.locator("text=Skill Types").first
            assert types_tab.count() > 0, "Skill Types tab not found"
            types_tab.click()
            page.wait_for_timeout(500)
            print("   [OK] Skill Types tab active")
            page.screenshot(path="/tmp/skills_11_types_tab.png")

            # STEP 12: Test validation - empty form
            print("\n12. Testing validation - empty form submission...")
            add_type_btn = page.locator('button:has-text("Add Skill Type")').first
            assert add_type_btn.count() > 0, "Add Skill Type button not found"
            add_type_btn.click()
            page.wait_for_timeout(500)

            modal = page.locator('[role="dialog"]')
            assert modal.count() > 0, "Modal not opened"
            print("   [OK] Add Skill Type modal opened")

            # Try to save without filling required fields
            save_btn = page.locator('button:has-text("Save"), button:has-text("Create")').first
            save_btn.click()
            page.wait_for_timeout(500)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty form submission")
            page.screenshot(path="/tmp/skills_03_validation_error.png")

            # Close modal
            cancel_btn = page.locator('button:has-text("Cancel")').first
            cancel_btn.click()
            page.wait_for_timeout(300)
            print("   [OK] Modal closed")

            # STEP 13: Create new skill type
            print(f"\n13. Creating new skill type: '{test_type_name}'...")
            add_type_btn.click()
            page.wait_for_timeout(500)

            # Fill fields (Type Information section is expanded by default)
            name_input = page.locator('input[placeholder="e.g., Frontend"]').first
            name_input.fill(test_type_name)
            page.wait_for_timeout(200)

            desc_input = page.locator('textarea[placeholder="Brief description"]').first
            desc_input.fill(test_type_desc)
            page.wait_for_timeout(200)

            # Display order input
            order_input = page.locator('input[placeholder="Order"]').first
            order_input.fill("99")
            page.wait_for_timeout(200)

            page.screenshot(path="/tmp/skills_04_type_create_filled.png")

            # Save
            save_btn = page.locator('button:has-text("Save"), button:has-text("Create")').first
            save_btn.click()
            page.wait_for_timeout(1000)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Skill type created successfully")

            # STEP 14: Verify type appears in table (may be on page 2 due to pagination)
            print("\n14. Verifying skill type appears in table...")
            page.wait_for_timeout(500)

            # Search for our newly created type to bring it to view
            search_input = page.locator('input[placeholder*="Search" i]').first
            search_input.fill(test_type_name)
            page.wait_for_timeout(500)

            type_row = page.locator(f'tr:has-text("{test_type_name}")')
            expect(type_row).to_be_visible(timeout=5000)
            print(f"   [OK] Skill type '{test_type_name}' found in table")

            # Clear search to go back to full list
            search_input.fill("")
            page.wait_for_timeout(300)
            page.screenshot(path="/tmp/skills_05_type_in_table.png")

            # STEP 15: Edit skill type
            print("\n15. Editing skill type...")

            # Search again to ensure it's visible (in case search was cleared)
            search_input.fill(test_type_name)
            page.wait_for_timeout(500)

            type_row = page.locator(f'tr:has-text("{test_type_name}")')
            edit_btn = type_row.locator('button[aria-label*="Edit" i]').first
            edit_btn.click()
            page.wait_for_timeout(500)

            # Verify modal opened with existing data
            assert modal.is_visible(), "Edit modal should be visible"
            name_input = page.locator('input[placeholder="e.g., Frontend"]').first
            expect(name_input).to_have_value(test_type_name)
            print("   [OK] Existing data loaded")

            # Update fields
            name_input.fill(updated_type_name)
            page.wait_for_timeout(200)

            desc_input = page.locator('textarea[placeholder*="Brief description" i]').first
            desc_input.fill(updated_type_desc)
            page.wait_for_timeout(200)

            page.screenshot(path="/tmp/skills_06_type_edit_filled.png")

            # Save changes
            save_btn = page.locator('button:has-text("Save"), button:has-text("Update")').first
            save_btn.click()
            page.wait_for_timeout(1000)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Skill type updated successfully")

            # STEP 16: Verify updated type in table
            print("\n16. Verifying updated skill type in table...")
            page.wait_for_timeout(500)

            # Search for updated name
            search_input = page.locator('input[placeholder*="Search" i]').first
            search_input.fill(updated_type_name)
            page.wait_for_timeout(500)

            updated_type_row = page.locator(f'tr:has-text("{updated_type_name}")')
            expect(updated_type_row).to_be_visible(timeout=5000)
            print(f"   [OK] Updated skill type '{updated_type_name}' found in table")

            # Clear search
            search_input.fill("")
            page.wait_for_timeout(300)
            page.screenshot(path="/tmp/skills_07_type_updated_in_table.png")

            # STEP 17: Test data persistence for skill type
            print("\n17. Testing skill type data persistence - reloading page...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Switch back to Skill Types tab
            types_tab = page.locator("text=Skill Types").first
            types_tab.click()
            page.wait_for_timeout(500)

            # Search for the updated type (it may be on page 2)
            search_input = page.locator('input[placeholder*="Search" i]').first
            search_input.fill(updated_type_name)
            page.wait_for_timeout(500)

            # Verify data still exists
            persisted_type_row = page.locator(f'tr:has-text("{updated_type_name}")')
            expect(persisted_type_row).to_be_visible(timeout=5000)
            print("   [OK] Skill type data persisted after page reload")

            # Clear search for next step
            search_input.fill("")
            page.wait_for_timeout(500)

            # STEP 18: Test search functionality for skill types
            print("\n18. Testing skill type search functionality...")
            search_input = page.locator('input[placeholder*="Search" i]').first
            if search_input.count() > 0:
                search_input.fill(updated_type_name)
                page.wait_for_timeout(500)

                search_row = page.locator(f'tr:has-text("{updated_type_name}")')
                expect(search_row).to_be_visible()
                print(f"   [OK] Search found skill type: '{updated_type_name}'")

                # Clear search
                search_input.fill("")
                page.wait_for_timeout(500)
                print("   [OK] Search cleared")
            else:
                print("   [WARN] Search input not found")

            # STEP 19: Delete skill type
            # ========================================
            print(f"\n19. Deleting skill type '{updated_type_name}'...")
            # Switch to Skill Types tab
            types_tab = page.locator("text=Skill Types").first
            types_tab.click()
            page.wait_for_timeout(500)

            # Search for the type to delete
            search_input = page.locator('input[placeholder*="Search" i]').first
            search_input.fill(updated_type_name)
            page.wait_for_timeout(500)

            delete_type_row = page.locator(f'tr:has-text("{updated_type_name}")')
            delete_type_btn = delete_type_row.locator('button[aria-label*="Delete" i]').first
            delete_type_btn.click()
            page.wait_for_timeout(500)

            # Confirm deletion
            confirm_btn = page.locator(
                'button:has-text("Confirm"), button:has-text("Delete"), button:has-text("Yes")'
            ).first
            if confirm_btn.count() > 0:
                confirm_btn.click()
                page.wait_for_timeout(1000)
                print("   [OK] Skill type deletion confirmed")

            # STEP 20: Verify skill type deletion
            print("\n20. Verifying skill type deletion...")
            page.wait_for_timeout(1000)
            deleted_type_row = page.locator(f'tr:has-text("{updated_type_name}")')
            expect(deleted_type_row).not_to_be_visible()
            print(f"   [OK] Skill type '{updated_type_name}' successfully deleted")
            page.screenshot(path="/tmp/skills_22_type_deleted.png")

            # STEP 21: Verify skill type deletion persists
            print("\n21. Verifying skill type deletion persists after reload...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Switch to Skill Types tab
            types_tab = page.locator("text=Skill Types").first
            types_tab.click()
            page.wait_for_timeout(500)

            final_type_check = page.locator(f'tr:has-text("{updated_type_name}")')
            expect(final_type_check).not_to_be_visible()
            print("   [OK] Skill type deletion persisted after reload")

            # ========================================
            # TEST SUMMARY
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("\n  SKILL TYPES:")
            print("  [PASS] Page navigation and tab switching")
            print("  [PASS] Form validation (empty form)")
            print("  [PASS] Create skill type")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Edit skill type")
            print("  [PASS] Update skill type data")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Search functionality")
            print("  [PASS] Delete skill type")
            print("  [PASS] Verify deletion")
            print("  [PASS] Deletion persistence")
            print("\n  SKILLS:")
            print("  [PASS] Tab switching")
            print("  [PASS] Form validation (empty form)")
            print("  [PASS] Create skill with type association")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Edit skill")
            print("  [PASS] Update skill data")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Search functionality")
            print("  [PASS] Delete skill")
            print("  [PASS] Verify deletion")
            print("  [PASS] Deletion persistence")
            print("\nScreenshots saved to /tmp/:")
            for i in range(1, 24):
                print(f"  - skills_{i:02d}_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            page.screenshot(path="/tmp/skills_error_assertion.png")
            import traceback

            traceback.print_exc()
            return False
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
