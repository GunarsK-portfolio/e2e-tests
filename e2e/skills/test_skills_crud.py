#!/usr/bin/env python3
"""
E2E test for Skills CRUD operations
Tests: Skill Types CRUD, Skills CRUD with type association, validation, search, persistence
"""

import sys
import time

from playwright.sync_api import sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config
from e2e.common.helpers import (
    clear_search,
    close_modal,
    delete_row,
    expand_collapse_section,
    fill_number_input,
    fill_text_input,
    fill_textarea,
    get_input_value,
    navigate_to_tab,
    open_add_modal,
    open_edit_modal,
    save_modal,
    search_and_verify,
    search_table,
    select_dropdown_option,
    take_screenshot,
    verify_cell_contains,
    verify_row_not_exists,
    wait_for_page_load,
)

config = get_config()
BASE_URL = config["admin_web_url"]


def test_skills_crud():
    """Test Skills page CRUD operations for both Skill Types and Skills"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== SKILLS E2E TEST ===\n")

        # Test data
        test_type_name = f"E2E Test Type {int(time.time())}"
        test_type_desc = "Automated E2E testing skill category"
        updated_type_name = f"{test_type_name} Updated"
        updated_type_desc = "Updated E2E testing category"

        test_skill_name = f"E2E Test Skill {int(time.time())}"
        updated_skill_name = f"{test_skill_name} Updated"

        try:
            # ========================================
            # PART 1: SKILL TYPES CRUD
            # ========================================
            print("\n" + "=" * 60)
            print("PART 1: SKILL TYPES CRUD")
            print("=" * 60)

            # ========================================
            # STEP 1: Navigate to Skills page and Skill Types tab
            # ========================================
            print("\n1. Navigating to Skills page and Skill Types tab...")
            navigate_to_tab(page, BASE_URL, "skills", "Skill Types")
            take_screenshot(page, "skills_01_types_tab", "Skill Types tab loaded")
            print("   [OK] Skill Types tab active")

            # ========================================
            # STEP 2: Test validation - empty skill type form
            # ========================================
            print("\n2. Testing validation - empty skill type form...")
            modal = open_add_modal(page, "Add Skill Type")
            print("   [OK] Add Skill Type modal opened")

            # Expand section if needed
            expand_collapse_section(page, "Type Information")

            # Try to save without filling required fields
            save_modal(page)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty form submission")
            take_screenshot(page, "skills_02_validation_error", "Validation error")

            # Close modal
            close_modal(page)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Create new skill type
            # ========================================
            print(f"\n3. Creating new skill type: '{test_type_name}'...")
            modal = open_add_modal(page, "Add Skill Type")

            # Expand section if needed
            expand_collapse_section(page, "Type Information")

            # Fill form fields
            fill_text_input(page, label="Name", value=test_type_name)
            fill_textarea(page, label="Description", value=test_type_desc)
            fill_number_input(page, label="Display Order", value=99)

            take_screenshot(page, "skills_03_type_create_filled", "Type create form filled")

            # Save
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Skill type created successfully")

            # ========================================
            # STEP 4: Verify skill type appears in table
            # ========================================
            print("\n4. Verifying skill type appears in table...")
            page.wait_for_timeout(500)

            # Search and verify the new type
            type_row = search_and_verify(page, test_type_name, "skill type")

            # Verify description
            verify_cell_contains(
                type_row, test_type_desc, f"Description '{test_type_desc}' displayed"
            )

            clear_search(page)
            take_screenshot(page, "skills_04_type_in_table", "Skill type in table")

            # ========================================
            # STEP 5: Edit skill type
            # ========================================
            print("\n5. Editing skill type...")

            # Search to find the type
            search_table(page, test_type_name)

            modal = open_edit_modal(page, test_type_name)
            print("   [OK] Edit modal opened")

            # Verify existing data loaded
            # Expand section first to access the field
            expand_collapse_section(page, "Type Information")
            current_value = get_input_value(page, "Name")
            assert (
                current_value == test_type_name
            ), f"Expected '{test_type_name}', got '{current_value}'"
            print("   [OK] Existing data loaded")

            # Update fields
            fill_text_input(page, label="Name", value=updated_type_name)
            fill_textarea(page, label="Description", value=updated_type_desc)

            take_screenshot(page, "skills_05_type_edit_filled", "Type edit form filled")

            # Save changes
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Skill type updated successfully")

            # ========================================
            # STEP 6: Verify updated skill type in table
            # ========================================
            print("\n6. Verifying updated skill type in table...")
            page.wait_for_timeout(500)

            clear_search(page)
            updated_type_row = search_and_verify(page, updated_type_name, "updated skill type")

            # Verify updated description
            verify_cell_contains(
                updated_type_row, updated_type_desc, "Updated description displayed"
            )

            clear_search(page)
            take_screenshot(page, "skills_06_type_updated", "Skill type updated")

            # ========================================
            # STEP 7: Test skill type data persistence
            # ========================================
            print("\n7. Testing skill type data persistence - reloading page...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Navigate back to Skill Types tab
            navigate_to_tab(page, BASE_URL, "skills", "Skill Types")

            # Search and verify persistence
            search_and_verify(page, updated_type_name, "skill type")
            print("   [OK] Skill type data persisted after reload")

            clear_search(page)
            take_screenshot(page, "skills_07_type_persisted", "Type persisted after reload")

            # ========================================
            # PART 2: SKILLS CRUD
            # ========================================
            print("\n" + "=" * 60)
            print("PART 2: SKILLS CRUD")
            print("=" * 60)

            # ========================================
            # STEP 8: Switch to Skills tab
            # ========================================
            print("\n8. Switching to Skills tab...")
            navigate_to_tab(page, BASE_URL, "skills", "Skills")
            print("   [OK] Skills tab active")
            take_screenshot(page, "skills_08_skills_tab", "Skills tab loaded")

            # ========================================
            # STEP 9: Test validation - empty skill form
            # ========================================
            print("\n9. Testing validation - empty skill form...")
            modal = open_add_modal(page, "Add Skill")
            print("   [OK] Add Skill modal opened")

            # Expand section if needed
            expand_collapse_section(page, "Skill Information")

            # Try to save without filling required fields
            save_modal(page)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty skill form submission")

            # Close modal
            close_modal(page)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 10: Create new skill with type association
            # ========================================
            print(f"\n10. Creating new skill: '{test_skill_name}'...")
            modal = open_add_modal(page, "Add Skill")

            # Expand section if needed
            expand_collapse_section(page, "Skill Information")

            # Fill form fields
            fill_text_input(page, label="Skill Name", value=test_skill_name)

            # Select skill type (our newly created type)
            select_dropdown_option(page, modal, option_index=0, label="Skill Type")
            print("   [OK] Skill type selected")

            # Set display order
            fill_number_input(page, label="Display Order", value=88)

            take_screenshot(page, "skills_09_skill_create_filled", "Skill create form filled")

            # Save
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Skill created successfully")

            # ========================================
            # STEP 11: Verify skill appears in table
            # ========================================
            print("\n11. Verifying skill appears in table...")
            page.wait_for_timeout(500)

            # Search and verify the new skill
            search_and_verify(page, test_skill_name, "skill")

            clear_search(page)
            take_screenshot(page, "skills_10_skill_in_table", "Skill in table")

            # ========================================
            # STEP 12: Edit skill
            # ========================================
            print("\n12. Editing skill...")

            # Search to find the skill
            search_table(page, test_skill_name)

            modal = open_edit_modal(page, test_skill_name)
            print("   [OK] Edit modal opened")

            # Verify existing data loaded
            # Expand section first to access the field
            expand_collapse_section(page, "Skill Information")
            current_value = get_input_value(page, "Skill Name")
            assert (
                current_value == test_skill_name
            ), f"Expected '{test_skill_name}', got '{current_value}'"
            print("   [OK] Existing data loaded")

            # Update skill name
            fill_text_input(page, label="Skill Name", value=updated_skill_name)

            take_screenshot(page, "skills_11_skill_edit_filled", "Skill edit form filled")

            # Save changes
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Skill updated successfully")

            # ========================================
            # STEP 13: Verify updated skill in table
            # ========================================
            print("\n13. Verifying updated skill in table...")
            page.wait_for_timeout(500)

            clear_search(page)
            search_and_verify(page, updated_skill_name, "updated skill")

            clear_search(page)
            take_screenshot(page, "skills_12_skill_updated", "Skill updated")

            # ========================================
            # STEP 14: Test skill data persistence
            # ========================================
            print("\n14. Testing skill data persistence - reloading page...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Should land on Skills tab by default
            search_and_verify(page, updated_skill_name, "skill")
            print("   [OK] Skill data persisted after reload")

            clear_search(page)
            take_screenshot(page, "skills_13_skill_persisted", "Skill persisted after reload")

            # ========================================
            # STEP 15: Delete skill
            # ========================================
            print(f"\n15. Deleting skill '{updated_skill_name}'...")
            search_table(page, updated_skill_name)
            delete_row(page, updated_skill_name)
            print("   [OK] Skill deletion confirmed")

            # ========================================
            # STEP 16: Verify skill deletion
            # ========================================
            print("\n16. Verifying skill deletion...")
            page.wait_for_timeout(500)
            clear_search(page)
            search_table(page, updated_skill_name)

            verify_row_not_exists(page, updated_skill_name, "skill")

            clear_search(page)
            take_screenshot(page, "skills_14_skill_deleted", "Skill deleted")

            # ========================================
            # STEP 17: Delete skill type
            # ========================================
            print(f"\n17. Deleting skill type '{updated_type_name}'...")

            # Navigate to Skill Types tab
            navigate_to_tab(page, BASE_URL, "skills", "Skill Types")

            search_table(page, updated_type_name)
            delete_row(page, updated_type_name)
            print("   [OK] Skill type deletion confirmed")

            # ========================================
            # STEP 18: Verify skill type deletion
            # ========================================
            print("\n18. Verifying skill type deletion...")
            page.wait_for_timeout(500)
            clear_search(page)
            search_table(page, updated_type_name)

            verify_row_not_exists(page, updated_type_name, "skill type")

            clear_search(page)
            take_screenshot(page, "skills_15_type_deleted", "Skill type deleted")

            # ========================================
            # STEP 19: Verify deletions persist after reload
            # ========================================
            print("\n19. Verifying deletions persist after reload...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Check skill type
            navigate_to_tab(page, BASE_URL, "skills", "Skill Types")
            search_table(page, updated_type_name)
            verify_row_not_exists(page, updated_type_name, "skill type")
            print("   [OK] Skill type deletion persisted")

            # Check skill
            navigate_to_tab(page, BASE_URL, "skills", "Skills")
            search_table(page, updated_skill_name)
            verify_row_not_exists(page, updated_skill_name, "skill")
            print("   [OK] Skill deletion persisted")

            take_screenshot(page, "skills_16_deletions_persisted", "Deletions persisted")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("\n  SKILL TYPES:")
            print("  [PASS] Navigate to Skill Types tab")
            print("  [PASS] Validation (empty form)")
            print("  [PASS] Create skill type")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Edit skill type")
            print("  [PASS] Verify update in table")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Delete skill type")
            print("  [PASS] Verify deletion")
            print("\n  SKILLS:")
            print("  [PASS] Navigate to Skills tab")
            print("  [PASS] Validation (empty form)")
            print("  [PASS] Create skill with type association")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Edit skill")
            print("  [PASS] Verify update in table")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Delete skill")
            print("  [PASS] Verify deletion")
            print("\n  OVERALL:")
            print("  [PASS] Verify deletions persist after reload")
            print("\nScreenshots saved to /tmp/test_skills_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "skills_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "skills_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_skills_crud()
    sys.exit(0 if success else 1)
