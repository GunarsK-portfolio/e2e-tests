#!/usr/bin/env python3
"""
E2E test for Miniatures Themes CRUD operations
Tests: Validation, Create, Edit, Search, Persistence, Delete
"""

import sys
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config
from e2e.common.helpers import (
    clear_search,
    close_modal,
    delete_row,
    fill_number_input,
    fill_text_input,
    fill_textarea,
    navigate_to_tab,
    open_add_modal,
    open_edit_modal,
    remove_uploaded_file,
    save_modal,
    search_and_verify,
    search_table,
    take_screenshot,
    upload_file,
    verify_file_uploaded,
    verify_row_not_exists,
    wait_for_page_load,
)

config = get_config()
BASE_URL = config["admin_web_url"]


def test_themes_crud():
    """Test Miniatures Themes tab full CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=config["headless"])
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

        # Test image path - relative to test file
        test_image_path = str(Path(__file__).parent.parent.parent / "test-files" / "test_image.jpg")

        try:
            # ========================================
            # STEP 1: Navigate to Miniatures > Themes tab
            # ========================================
            print("1. Navigating to Miniatures > Themes tab...")
            navigate_to_tab(page, BASE_URL, "miniatures", "Themes")
            take_screenshot(page, "themes_01_page", "Themes tab loaded")
            print("   [OK] Themes tab loaded")

            # ========================================
            # STEP 2: Test validation - empty form
            # ========================================
            print("\n2. Testing validation - empty theme form...")
            modal = open_add_modal(page, "Add Theme")
            print("   [OK] Add Theme modal opened")

            # Try to save without filling required fields
            save_modal(page)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty theme form submission")
            take_screenshot(page, "themes_02_validation_error", "Validation error shown")

            # Close modal
            close_modal(page)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Create new theme
            # ========================================
            print(f"\n3. Creating new theme: '{test_theme_name}'...")
            modal = open_add_modal(page, "Add Theme")

            # Fill form fields
            fill_text_input(page, label="Theme Name", value=test_theme_name)
            fill_textarea(page, label="Description", value=test_theme_desc)

            # Upload cover image
            upload_file(page, modal, test_image_path)
            assert verify_file_uploaded(modal), "Cover image should be uploaded"
            print("   [OK] Cover image uploaded")

            fill_number_input(page, label="Display Order", value=99)
            print("   [OK] Form fields filled")

            take_screenshot(page, "themes_03_create_form_filled", "Create form with image")

            # Save
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Theme created successfully")

            # ========================================
            # STEP 4: Verify entry appears in table
            # ========================================
            print("\n4. Verifying theme appears in table...")
            page.wait_for_timeout(500)

            # Search and verify the new theme
            search_and_verify(page, test_theme_name, "theme")

            clear_search(page)
            take_screenshot(page, "themes_04_in_table", "Theme in table")

            # ========================================
            # STEP 5: Edit theme entry
            # ========================================
            print("\n5. Editing theme entry...")

            # Search to find the theme
            search_table(page, test_theme_name)

            modal = open_edit_modal(page, test_theme_name)
            print("   [OK] Edit modal opened")

            # Verify existing data loaded
            name_input = page.locator('input[placeholder*="Enter theme name" i]').first
            expect(name_input).to_have_value(test_theme_name)
            assert verify_file_uploaded(modal), "Cover image should still be present"
            print("   [OK] Existing data loaded with cover image")

            # Update form fields
            fill_text_input(page, label="Theme Name", value=updated_theme_name)
            fill_textarea(page, label="Description", value=updated_theme_desc)

            # Test image removal
            assert remove_uploaded_file(page, modal, "Remove Image"), "Should remove cover image"
            assert not verify_file_uploaded(modal), "Cover image should be removed"
            print("   [OK] Cover image removed")

            # Re-upload the image
            upload_file(page, modal, test_image_path)
            assert verify_file_uploaded(modal), "Cover image should be re-uploaded"
            print("   [OK] Cover image re-uploaded")

            take_screenshot(page, "themes_05_edit_form_filled", "Edit form with re-uploaded image")

            # Save changes
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Theme updated successfully")

            # ========================================
            # STEP 6: Test search functionality
            # ========================================
            print("\n6. Testing search functionality...")

            # Search by theme name
            clear_search(page)
            search_and_verify(page, updated_theme_name, "theme")
            print(f"   [OK] Search by name found: '{updated_theme_name}'")
            take_screenshot(page, "themes_06a_search_by_name", "Search by name")

            # Search by description
            clear_search(page)
            search_and_verify(page, updated_theme_desc, "theme")
            print("   [OK] Search by description found")
            take_screenshot(page, "themes_06b_search_by_description", "Search by description")

            # ========================================
            # STEP 7: Test data persistence - reload page
            # ========================================
            print("\n7. Testing data persistence - reloading page...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Navigate back to Themes tab
            navigate_to_tab(page, BASE_URL, "miniatures", "Themes")

            # Search and verify persistence
            search_and_verify(page, updated_theme_name, "theme")
            print("   [OK] Theme data persisted after reload")

            clear_search(page)
            take_screenshot(page, "themes_07_persisted", "Data persisted after reload")

            # ========================================
            # STEP 8: Delete theme entry
            # ========================================
            print(f"\n8. Deleting theme '{updated_theme_name}'...")

            search_table(page, updated_theme_name)
            delete_row(page, updated_theme_name)
            print("   [OK] Deletion confirmed")

            # ========================================
            # STEP 9: Verify deletion
            # ========================================
            print("\n9. Verifying theme deletion...")
            page.wait_for_timeout(500)
            clear_search(page)
            search_table(page, updated_theme_name)

            verify_row_not_exists(page, updated_theme_name, "theme")

            clear_search(page)
            take_screenshot(page, "themes_09_after_deletion", "After deletion")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Navigate to Themes tab")
            print("  [PASS] Validation (empty form)")
            print("  [PASS] Create theme with description, cover image, and order")
            print("  [PASS] Upload cover image")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Edit theme")
            print("  [PASS] Verify cover image persisted")
            print("  [PASS] Remove cover image")
            print("  [PASS] Re-upload cover image")
            print("  [PASS] Search by name")
            print("  [PASS] Search by description")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Delete theme")
            print("  [PASS] Verify deletion")
            print("\nScreenshots saved to /tmp/test_themes_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "themes_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "themes_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_themes_crud()
    sys.exit(0 if success else 1)
