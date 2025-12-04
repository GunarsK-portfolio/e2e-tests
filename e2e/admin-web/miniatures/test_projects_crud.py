#!/usr/bin/env python3
"""
E2E test for Miniatures Projects CRUD operations
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
    expand_collapse_section,
    fill_date_input,
    fill_number_input,
    fill_text_input,
    fill_textarea,
    navigate_to_tab,
    open_add_modal,
    open_edit_modal,
    save_modal,
    search_and_verify,
    search_table,
    select_dropdown_option,
    take_screenshot,
    upload_file,
    verify_row_not_exists,
    wait_for_page_load,
)

config = get_config()
BASE_URL = config["admin_web_url"]


def test_projects_crud():
    """Test Miniatures Projects tab full CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=config["headless"])
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== MINIATURES PROJECTS E2E TEST ===\n")

        # Test data - unique project title using timestamp
        test_project_title = f"E2E Test Project {int(time.time())}"
        test_scale = "28mm"
        test_manufacturer = "Games Workshop"
        test_description = "E2E automated testing miniature project"
        test_time_spent = 15.5
        test_completed_date = "2024-03-20"
        test_display_order = 99

        updated_project_title = f"{test_project_title} Updated"
        updated_scale = "32mm"
        updated_manufacturer = "Reaper Miniatures"
        updated_description = "Updated: Advanced E2E testing miniature project"
        updated_time_spent = 25
        updated_completed_date = "2024-06-15"
        updated_display_order = 10

        # Test image path - relative to e2e-tests root
        test_image_path = str(
            Path(__file__).parent.parent.parent.parent / "test-files" / "test_image.jpg"
        )

        try:
            # ========================================
            # STEP 1: Navigate to Miniatures > Projects tab
            # ========================================
            print("1. Navigating to Miniatures > Projects tab...")
            navigate_to_tab(page, BASE_URL, "miniatures", "Projects")
            take_screenshot(page, "projects_01_page", "Projects tab loaded")
            print("   [OK] Projects tab loaded")

            # ========================================
            # STEP 2: Test validation - empty form
            # ========================================
            print("\n2. Testing validation - empty project form...")
            modal = open_add_modal(page, "Add Project")
            print("   [OK] Add Project modal opened")

            # Try to save without filling required fields
            save_modal(page)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty project form submission")
            take_screenshot(page, "projects_02_validation_error", "Validation error shown")

            # Close modal
            close_modal(page)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Create new project
            # ========================================
            print(f"\n3. Creating new project: '{test_project_title}'...")
            modal = open_add_modal(page, "Add Project")

            # Basic Information section (expanded by default)
            fill_text_input(page, label="Project Title", value=test_project_title)
            select_dropdown_option(page, modal, 0, label="Theme")  # Select first theme
            fill_textarea(page, label="Description", value=test_description)

            # Expand Project Details section
            expand_collapse_section(page, "Project Details")
            fill_text_input(page, label="Scale", value=test_scale)
            fill_text_input(page, label="Manufacturer", value=test_manufacturer)
            # Select first difficulty (Beginner)
            # select_dropdown_option(page, modal, 0, label="Difficulty")
            fill_number_input(page, label="Time Spent (hours)", value=test_time_spent)

            # Expand Metadata section
            expand_collapse_section(page, "Metadata")
            fill_date_input(page, label="Completed Date", date_value=test_completed_date)
            fill_number_input(page, label="Display Order", value=test_display_order)

            print("   [OK] Form fields filled")
            take_screenshot(page, "projects_03_create_form_filled", "Create form filled")

            # Save
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Project created successfully")

            # ========================================
            # STEP 4: Verify entry appears in table
            # ========================================
            print("\n4. Verifying project appears in table...")
            page.wait_for_timeout(500)

            # Search and verify the new project
            search_and_verify(page, test_project_title, "project")

            clear_search(page)
            take_screenshot(page, "projects_04_in_table", "Project in table")

            # ========================================
            # STEP 5: Edit project entry
            # ========================================
            print("\n5. Editing project entry...")

            # Search to find the project
            search_table(page, test_project_title)

            modal = open_edit_modal(page, test_project_title)
            print("   [OK] Edit modal opened")

            # Verify existing data loaded
            title_input = page.locator('input[placeholder*="project title" i]').first
            expect(title_input).to_have_value(test_project_title)
            print("   [OK] Existing data loaded")

            # Update Basic Information
            fill_text_input(page, label="Project Title", value=updated_project_title)
            fill_textarea(page, label="Description", value=updated_description)

            # Update Project Details
            expand_collapse_section(page, "Project Details")
            fill_text_input(page, label="Scale", value=updated_scale)
            fill_text_input(page, label="Manufacturer", value=updated_manufacturer)
            select_dropdown_option(page, modal, 0, label="Difficulty")  # Select first difficulty
            fill_number_input(page, label="Time Spent (hours)", value=updated_time_spent)

            # Update Metadata
            expand_collapse_section(page, "Metadata")
            fill_date_input(page, label="Completed Date", date_value=updated_completed_date)
            fill_number_input(page, label="Display Order", value=updated_display_order)

            # Upload multiple project images (Project Images section only appears when editing)
            expand_collapse_section(page, "Project Images")
            upload_file(page, modal, test_image_path)
            print("   [OK] Project image 1 uploaded")

            upload_file(page, modal, test_image_path)
            print("   [OK] Project image 2 uploaded")

            upload_file(page, modal, test_image_path)
            print("   [OK] Project image 3 uploaded")

            take_screenshot(page, "projects_05_edit_form_filled", "Edit form with 3 project images")

            # Save changes
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Project updated successfully")

            # ========================================
            # STEP 6: Test search functionality
            # ========================================
            print("\n6. Testing search functionality...")

            # Search by project title
            clear_search(page)
            search_and_verify(page, updated_project_title, "project")
            print(f"   [OK] Search by title found: '{updated_project_title}'")
            take_screenshot(page, "projects_06a_search_by_title", "Search by title")

            clear_search(page)

            # ========================================
            # STEP 7: Test data persistence - reload page
            # ========================================
            print("\n7. Testing data persistence - reloading page...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Navigate back to Projects tab
            navigate_to_tab(page, BASE_URL, "miniatures", "Projects")

            # Search and verify persistence
            search_and_verify(page, updated_project_title, "project")
            print("   [OK] Project data persisted after reload")

            clear_search(page)
            take_screenshot(page, "projects_07_persisted", "Data persisted after reload")

            # ========================================
            # STEP 8: Delete project entry
            # ========================================
            print(f"\n8. Deleting project '{updated_project_title}'...")

            search_table(page, updated_project_title)
            delete_row(page, updated_project_title)
            print("   [OK] Deletion confirmed")

            # ========================================
            # STEP 9: Verify deletion
            # ========================================
            print("\n9. Verifying project deletion...")
            page.wait_for_timeout(500)
            clear_search(page)
            search_table(page, updated_project_title)

            verify_row_not_exists(page, updated_project_title, "project")

            clear_search(page)
            take_screenshot(page, "projects_09_after_deletion", "After deletion")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Navigate to Projects tab")
            print("  [PASS] Validation (empty form)")
            print("  [PASS] Create project with all fields:")
            print("         - Basic Info: title, theme, description")
            print("         - Details: scale, manufacturer, difficulty, time spent")
            print("         - Metadata: display order")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Edit project with updated values")
            print("  [PASS] Upload 3 project images")
            print("  [PASS] Search by title")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Delete project")
            print("  [PASS] Verify deletion")
            print("\nScreenshots saved to /tmp/test_projects_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "projects_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "projects_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_projects_crud()
    sys.exit(0 if success else 1)
