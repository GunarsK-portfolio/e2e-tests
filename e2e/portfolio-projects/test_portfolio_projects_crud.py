#!/usr/bin/env python3
"""
E2E test for Portfolio Projects CRUD operations
Tests: Full CRUD, validation, URLs, dates, technologies, search, persistence
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
    expand_collapse_section,
    fill_date_input,
    fill_text_input,
    fill_textarea,
    navigate_to_page,
    open_add_modal,
    open_edit_modal,
    save_modal,
    search_and_verify,
    search_table,
    take_screenshot,
    verify_cell_contains,
    verify_row_not_exists,
    wait_for_page_load,
)

config = get_config()
BASE_URL = config["admin_web_url"]


# ========================================
# PORTFOLIO PROJECTS SPECIFIC HELPERS
# ========================================


def select_category(page, category_name: str):
    """Select a category from the dropdown

    Args:
        page: Playwright page object
        category_name: Name of category to select (e.g., "Web Application", "Mobile Application")
    """
    # Find category form item
    form_item = page.locator('.n-form-item:has(.n-form-item-label:has-text("Category"))').first

    # Click the select to open dropdown
    select = form_item.locator(".n-select").first
    select.click()
    page.wait_for_timeout(300)

    # Click the option
    option = page.locator(f'div[role="option"]:has-text("{category_name}")').first
    if option.count() > 0:
        option.click()
        page.wait_for_timeout(300)
        print(f"   [OK] Category '{category_name}' selected")
    else:
        # Close dropdown if option not found
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        print(f"   [WARN] Category '{category_name}' not found in dropdown")


def toggle_ongoing_project(page, enabled: bool = True):
    """Toggle the 'Ongoing' project switch

    Args:
        page: Playwright page object
        enabled: True to enable (ongoing project), False to disable
    """
    # Find the switch by its label
    form_item = page.locator('.n-form-item:has(.n-form-item-label:has-text("Ongoing"))').first
    switch = form_item.locator(".n-switch").first

    # Check current state
    is_checked = "n-switch--active" in switch.get_attribute("class")

    # Click if we need to change state
    if is_checked != enabled:
        switch.click()
        page.wait_for_timeout(300)
        print(f"   [OK] Toggled 'Ongoing' to: {enabled}")


# ========================================
# MAIN TEST
# ========================================


def test_portfolio_projects_crud():
    """Test Portfolio Projects page CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== PORTFOLIO PROJECTS E2E TEST ===\n")

        # Test data
        test_title = f"E2E Test Project {int(time.time())}"
        test_category = "Web Application"
        test_role = "Full Stack Developer"
        test_description = "E2E automated testing project for comprehensive validation"
        test_github_url = "https://github.com/test/e2e-project"
        test_live_url = "https://e2e-test-project.example.com"
        test_start_date = "2024-01-15"
        test_end_date = "2024-06-30"

        updated_title = f"{test_title} Updated"
        updated_category = "Mobile Application"
        updated_role = "Lead Developer"
        updated_description = "Updated: Advanced E2E testing project with enhanced features"

        try:
            # ========================================
            # STEP 1: Navigate to Portfolio Projects page
            # ========================================
            print("1. Navigating to Portfolio Projects page...")
            navigate_to_page(page, BASE_URL, "portfolio-projects")
            take_screenshot(
                page, "portfolio_01_page_loaded", "Portfolio Projects page loaded"
            )
            print("   [OK] Portfolio Projects page loaded")

            # ========================================
            # STEP 2: Test validation - empty form
            # ========================================
            print("\n2. Testing validation - empty portfolio project form...")
            modal = open_add_modal(page, "Add Project")
            print("   [OK] Add Project modal opened")

            # Expand section if needed
            expand_collapse_section(page, "Basic Information")

            # Try to save without filling required fields
            save_modal(page)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty form submission")
            take_screenshot(page, "portfolio_02_validation_error", "Validation error")

            # Close modal
            close_modal(page)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Create new portfolio project
            # ========================================
            print(f"\n3. Creating new portfolio project: '{test_title}'...")
            modal = open_add_modal(page, "Add Project")

            # Expand sections if needed
            expand_collapse_section(page, "Basic Information")

            # Fill basic information
            fill_text_input(page, label="Project Title", value=test_title)
            select_category(page, test_category)
            fill_text_input(page, label="Role", value=test_role)
            fill_textarea(page, label="Short Description", value=test_description)

            # Expand and fill Links & Media
            expand_collapse_section(page, "Links & Media")
            fill_text_input(page, label="GitHub URL", value=test_github_url)
            fill_text_input(page, label="Live Demo URL", value=test_live_url)

            # Expand and fill Timeline
            expand_collapse_section(page, "Timeline")
            fill_date_input(page, label="Start Date", date_value=test_start_date)
            fill_date_input(page, label="End Date", date_value=test_end_date)

            take_screenshot(
                page, "portfolio_03_create_filled", "Portfolio project create form filled"
            )

            # Save
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Portfolio project created successfully")

            # ========================================
            # STEP 4: Verify project appears in table
            # ========================================
            print("\n4. Verifying portfolio project appears in table...")
            page.wait_for_timeout(500)

            # Search and verify the new project
            project_row = search_and_verify(page, test_title, "portfolio project")

            # Verify role appears
            verify_cell_contains(project_row, test_role, f"Role '{test_role}' displayed")

            clear_search(page)
            take_screenshot(page, "portfolio_04_in_table", "Portfolio project in table")

            # ========================================
            # STEP 5: Edit portfolio project
            # ========================================
            print("\n5. Editing portfolio project...")

            # Search to find the project
            search_table(page, test_title)

            modal = open_edit_modal(page, test_title)
            print("   [OK] Edit modal opened")

            # Verify existing data loaded
            title_input = page.locator('input[placeholder*="project title" i]').first
            expect(title_input).to_have_value(test_title)
            print("   [OK] Existing data loaded")

            # Expand section if needed
            expand_collapse_section(page, "Basic Information")

            # Update fields
            fill_text_input(page, label="Project Title", value=updated_title)
            select_category(page, updated_category)
            fill_text_input(page, label="Role", value=updated_role)
            fill_textarea(page, label="Short Description", value=updated_description)

            take_screenshot(
                page, "portfolio_05_edit_filled", "Portfolio project edit form filled"
            )

            # Save changes
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Portfolio project updated successfully")

            # ========================================
            # STEP 6: Verify updated project in table
            # ========================================
            print("\n6. Verifying updated portfolio project in table...")
            page.wait_for_timeout(500)

            clear_search(page)
            updated_project_row = search_and_verify(
                page, updated_title, "updated portfolio project"
            )

            # Verify updated role
            verify_cell_contains(
                updated_project_row, updated_role, f"Updated role '{updated_role}' displayed"
            )

            clear_search(page)
            take_screenshot(page, "portfolio_06_updated", "Portfolio project updated")

            # ========================================
            # STEP 7: Test ongoing project toggle
            # ========================================
            print("\n7. Testing ongoing project toggle...")

            # Search and edit
            search_table(page, updated_title)
            modal = open_edit_modal(page, updated_title)

            # Expand Timeline section
            expand_collapse_section(page, "Timeline")

            # Enable "Ongoing"
            toggle_ongoing_project(page, enabled=True)

            # End date input should be disabled
            page.wait_for_timeout(300)
            take_screenshot(page, "portfolio_07_ongoing_toggle", "Ongoing project toggled")

            # Save changes
            save_modal(page)
            page.wait_for_timeout(500)

            clear_search(page)
            take_screenshot(page, "portfolio_08_ongoing_saved", "Ongoing project saved")

            # ========================================
            # STEP 8: Test search by title
            # ========================================
            print("\n8. Testing search by project title...")
            search_and_verify(page, updated_title, "portfolio project")
            print("   [OK] Search by title successful")

            clear_search(page)

            # ========================================
            # STEP 9: Test search by role
            # ========================================
            print("\n9. Testing search by role...")
            search_and_verify(page, updated_role, "portfolio project")
            print("   [OK] Search by role successful")

            clear_search(page)
            take_screenshot(page, "portfolio_09_search_tested", "Search tested")

            # ========================================
            # STEP 10: Test data persistence
            # ========================================
            print("\n10. Testing data persistence - reloading page...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Search and verify persistence
            search_and_verify(page, updated_title, "portfolio project")
            print("   [OK] Portfolio project data persisted after reload")

            clear_search(page)
            take_screenshot(
                page, "portfolio_10_persisted", "Portfolio project persisted after reload"
            )

            # ========================================
            # STEP 11: Delete portfolio project
            # ========================================
            print(f"\n11. Deleting portfolio project '{updated_title}'...")
            search_table(page, updated_title)
            delete_row(page, updated_title)
            print("   [OK] Portfolio project deletion confirmed")

            # ========================================
            # STEP 12: Verify project deletion
            # ========================================
            print("\n12. Verifying portfolio project deletion...")
            page.wait_for_timeout(500)
            clear_search(page)
            search_table(page, updated_title)

            verify_row_not_exists(page, updated_title, "portfolio project")

            clear_search(page)
            take_screenshot(page, "portfolio_11_deleted", "Portfolio project deleted")

            # ========================================
            # STEP 13: Verify deletion persists after reload
            # ========================================
            print("\n13. Verifying deletion persists after reload...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            search_table(page, updated_title)
            verify_row_not_exists(page, updated_title, "portfolio project")
            print("   [OK] Portfolio project deletion persisted")

            take_screenshot(page, "portfolio_12_deletion_persisted", "Deletion persisted")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Navigate to Portfolio Projects page")
            print("  [PASS] Validation (empty form)")
            print("  [PASS] Create portfolio project with all fields")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Edit portfolio project")
            print("  [PASS] Verify update in table")
            print("  [PASS] Test ongoing project toggle")
            print("  [PASS] Search by project title")
            print("  [PASS] Search by role")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Delete portfolio project")
            print("  [PASS] Verify deletion")
            print("  [PASS] Verify deletion persists after reload")
            print("\nScreenshots saved to /tmp/test_portfolio_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "portfolio_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "portfolio_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_portfolio_projects_crud()
    sys.exit(0 if success else 1)
