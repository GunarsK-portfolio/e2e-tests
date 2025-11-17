#!/usr/bin/env python3
"""
E2E test for Miniatures Paints CRUD operations
Tests: Validation, Create, Edit, Search, Persistence, Delete
"""

import sys
import time

from playwright.sync_api import expect, sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config
from e2e.common.helpers import (
    clear_search,
    close_modal,
    delete_row,
    fill_color_picker,
    fill_text_input,
    navigate_to_tab,
    open_add_modal,
    open_edit_modal,
    save_modal,
    search_and_verify,
    search_table,
    select_dropdown_option,
    take_screenshot,
    verify_row_not_exists,
    wait_for_page_load,
)

config = get_config()
BASE_URL = config["admin_web_url"]


def test_paints_crud():
    """Test Miniatures Paints tab full CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== MINIATURES PAINTS E2E TEST ===\n")

        # Test data - unique paint name using timestamp
        test_paint_name = f"E2E Test Paint {int(time.time())}"
        test_manufacturer = "Citadel"
        test_color_hex = "#FF5733"

        updated_paint_name = f"{test_paint_name} Updated"
        updated_manufacturer = "Vallejo"
        updated_color_hex = "#33C1FF"

        try:
            # ========================================
            # STEP 1: Navigate to Miniatures > Paints tab
            # ========================================
            print("1. Navigating to Miniatures > Paints tab...")
            navigate_to_tab(page, BASE_URL, "miniatures", "Paints")
            take_screenshot(page, "paints_01_page", "Paints tab loaded")
            print("   [OK] Paints tab loaded")

            # ========================================
            # STEP 2: Test validation - empty form
            # ========================================
            print("\n2. Testing validation - empty paint form...")
            modal = open_add_modal(page, "Add Paint")
            print("   [OK] Add Paint modal opened")

            # Try to save without filling required fields
            save_modal(page)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty paint form submission")
            take_screenshot(page, "paints_02_validation_error", "Validation error shown")

            # Close modal
            close_modal(page)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Create new paint
            # ========================================
            print(f"\n3. Creating new paint: '{test_paint_name}'...")
            modal = open_add_modal(page, "Add Paint")

            # Fill form fields
            fill_text_input(page, label="Paint Name", value=test_paint_name)
            fill_text_input(page, label="Manufacturer", value=test_manufacturer)
            select_dropdown_option(page, modal, option_index=0, label="Paint Type")
            print("   [OK] Paint type selected")
            fill_color_picker(page, modal, test_color_hex, label="Color (Hex)")
            print("   [OK] Color selected")

            take_screenshot(page, "paints_03_create_form_filled", "Create form filled")

            # Save
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Paint created successfully")

            # ========================================
            # STEP 4: Verify entry appears in table
            # ========================================
            print("\n4. Verifying paint appears in table...")
            page.wait_for_timeout(500)

            # Search and verify the new paint
            search_and_verify(page, test_paint_name, "paint")

            clear_search(page)
            take_screenshot(page, "paints_04_in_table", "Paint in table")

            # ========================================
            # STEP 5: Edit paint entry
            # ========================================
            print("\n5. Editing paint entry...")

            # Search to find the paint
            search_table(page, test_paint_name)

            modal = open_edit_modal(page, test_paint_name)
            print("   [OK] Edit modal opened")

            # Verify existing data loaded
            name_input = page.locator('input[placeholder*="paint name" i]').first
            expect(name_input).to_have_value(test_paint_name)
            print("   [OK] Existing data loaded")

            # Update form fields
            fill_text_input(page, label="Paint Name", value=updated_paint_name)
            fill_text_input(page, label="Manufacturer", value=updated_manufacturer)
            fill_color_picker(page, modal, updated_color_hex, label="Color (Hex)")

            take_screenshot(page, "paints_05_edit_form_filled", "Edit form filled")

            # Save changes
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Paint updated successfully")

            # ========================================
            # STEP 6: Test search functionality
            # ========================================
            print("\n6. Testing search functionality...")

            # Search by paint name
            clear_search(page)
            search_and_verify(page, updated_paint_name, "paint")
            print(f"   [OK] Search by name found: '{updated_paint_name}'")
            take_screenshot(page, "paints_06a_search_by_name", "Search by name")

            # Search by manufacturer
            clear_search(page)
            search_and_verify(page, updated_manufacturer, "paint")
            print(f"   [OK] Search by manufacturer found: '{updated_manufacturer}'")
            take_screenshot(page, "paints_06b_search_by_manufacturer", "Search by manufacturer")

            # ========================================
            # STEP 7: Test data persistence - reload page
            # ========================================
            print("\n7. Testing data persistence - reloading page...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Navigate back to Paints tab
            navigate_to_tab(page, BASE_URL, "miniatures", "Paints")

            # Search and verify persistence
            search_and_verify(page, updated_paint_name, "paint")
            print("   [OK] Paint data persisted after reload")

            clear_search(page)
            take_screenshot(page, "paints_07_persisted", "Data persisted after reload")

            # ========================================
            # STEP 8: Delete paint entry
            # ========================================
            print(f"\n8. Deleting paint '{updated_paint_name}'...")

            search_table(page, updated_paint_name)
            delete_row(page, updated_paint_name)
            print("   [OK] Deletion confirmed")

            # ========================================
            # STEP 9: Verify deletion
            # ========================================
            print("\n9. Verifying paint deletion...")
            page.wait_for_timeout(500)
            clear_search(page)
            search_table(page, updated_paint_name)

            verify_row_not_exists(page, updated_paint_name, "paint")

            clear_search(page)
            take_screenshot(page, "paints_09_after_deletion", "After deletion")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Navigate to Paints tab")
            print("  [PASS] Validation (empty form)")
            print("  [PASS] Create paint with all fields")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Edit paint")
            print("  [PASS] Search by name")
            print("  [PASS] Search by manufacturer")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Delete paint")
            print("  [PASS] Verify deletion")
            print("\nScreenshots saved to /tmp/test_paints_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "paints_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "paints_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_paints_crud()
    sys.exit(0 if success else 1)
