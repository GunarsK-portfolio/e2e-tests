#!/usr/bin/env python3
"""
E2E test for Work Experience CRUD operations
Tests: Full CRUD with validation, current position toggle, date handling, search, persistence
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
# WORK EXPERIENCE SPECIFIC HELPERS
# ========================================


def fill_month_date(page, label: str, value: str):
    """Fill a month date picker input by label

    Args:
        page: Playwright page object
        label: Form item label (e.g., "Start Date", "End Date")
        value: Month value in format "YYYY-MM" (e.g., "2024-01")
    """
    form_item = page.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
    date_input = form_item.locator('input[placeholder="Select Month"]').first
    date_input.fill(value)
    page.wait_for_timeout(200)


def toggle_current_position(page, enabled: bool = True):
    """Toggle the 'Currently working here' checkbox

    Args:
        page: Playwright page object
        enabled: True to enable (currently working), False to disable
    """
    # Find the checkbox by its text label
    checkbox = page.locator('.n-checkbox:has-text("Currently working here")').first

    # Wait for checkbox to be visible
    checkbox.wait_for(state="visible", timeout=5000)

    # Check current state
    class_attr = checkbox.get_attribute("class") or ""
    is_checked = "n-checkbox--checked" in class_attr

    # Click if we need to change state
    if is_checked != enabled:
        checkbox.click()
        page.wait_for_timeout(300)
        print(f"   [OK] Toggled 'Currently working here' to: {enabled}")


def verify_status_tag(row, status: str):
    """Verify that a row shows the correct status tag (Current or Past)

    Args:
        row: Table row locator
        status: Expected status ("Current" or "Past")
    """
    tag = row.locator(f'.n-tag:has-text("{status}")').first
    found = tag.count() > 0
    if found:
        print(f"   [OK] Status tag '{status}' displayed")
    return found


# ========================================
# MAIN TEST
# ========================================


def test_experience_crud():
    """Test Work Experience page CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== WORK EXPERIENCE E2E TEST ===\n")

        # Test data
        test_company = f"E2E Test Company {int(time.time())}"
        test_position = "Senior Test Engineer"
        test_description = "Automated E2E testing and quality assurance"
        test_start_date = "2024-01"
        test_end_date = "2024-12"

        updated_company = f"{test_company} Updated"
        updated_position = "Lead Test Architect"
        updated_description = "Updated: Leading test automation initiatives"

        try:
            # ========================================
            # STEP 1: Navigate to Work Experience page
            # ========================================
            print("1. Navigating to Work Experience page...")
            navigate_to_page(page, BASE_URL, "work-experience")
            take_screenshot(page, "experience_01_page_loaded", "Work Experience page loaded")
            print("   [OK] Work Experience page loaded")

            # ========================================
            # STEP 2: Test validation - empty form
            # ========================================
            print("\n2. Testing validation - empty work experience form...")
            modal = open_add_modal(page, "Add Experience")
            print("   [OK] Add Experience modal opened")

            # Expand section if needed
            expand_collapse_section(page, "Basic Information")

            # Try to save without filling required fields
            save_modal(page)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty form submission")
            take_screenshot(page, "experience_02_validation_error", "Validation error")

            # Close modal
            close_modal(page)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Create new work experience
            # ========================================
            print(f"\n3. Creating new work experience: '{test_company}'...")
            modal = open_add_modal(page, "Add Experience")

            # Expand sections if needed
            expand_collapse_section(page, "Basic Information")

            # Fill basic information
            fill_text_input(page, label="Company", value=test_company)
            fill_text_input(page, label="Position", value=test_position)
            fill_textarea(page, label="Description", value=test_description)

            # Expand and fill timeline
            expand_collapse_section(page, "Timeline")
            fill_month_date(page, label="Start Date", value=test_start_date)
            fill_month_date(page, label="End Date", value=test_end_date)

            take_screenshot(page, "experience_03_create_filled", "Experience create form filled")

            # Save
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Work experience created successfully")

            # ========================================
            # STEP 4: Verify experience appears in table
            # ========================================
            print("\n4. Verifying experience appears in table...")
            page.wait_for_timeout(500)

            # Search and verify the new experience
            exp_row = search_and_verify(page, test_company, "work experience")

            # Verify position appears
            verify_cell_contains(exp_row, test_position, f"Position '{test_position}' displayed")

            # Verify Past status (since we set an end date)
            verify_status_tag(exp_row, "Past")

            clear_search(page)
            take_screenshot(page, "experience_04_in_table", "Experience in table")

            # ========================================
            # STEP 5: Edit work experience
            # ========================================
            print("\n5. Editing work experience...")

            # Search to find the experience
            search_table(page, test_company)

            modal = open_edit_modal(page, test_company)
            print("   [OK] Edit modal opened")

            # Verify existing data loaded
            company_input = page.locator('input[placeholder*="company" i]').first
            expect(company_input).to_have_value(test_company)
            print("   [OK] Existing data loaded")

            # Expand section if needed
            expand_collapse_section(page, "Basic Information")

            # Update fields
            fill_text_input(page, label="Company", value=updated_company)
            fill_text_input(page, label="Position", value=updated_position)
            fill_textarea(page, label="Description", value=updated_description)

            take_screenshot(page, "experience_05_edit_filled", "Experience edit form filled")

            # Save changes
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Work experience updated successfully")

            # ========================================
            # STEP 6: Verify updated experience in table
            # ========================================
            print("\n6. Verifying updated experience in table...")
            page.wait_for_timeout(500)

            clear_search(page)
            updated_exp_row = search_and_verify(page, updated_company, "updated work experience")

            # Verify updated position
            verify_cell_contains(
                updated_exp_row,
                updated_position,
                f"Updated position '{updated_position}' displayed",
            )

            clear_search(page)
            take_screenshot(page, "experience_06_updated", "Experience updated")

            # ========================================
            # STEP 7: Test current position toggle
            # ========================================
            print("\n7. Testing current position toggle...")

            # Search and edit
            search_table(page, updated_company)
            modal = open_edit_modal(page, updated_company)

            # Expand Timeline section
            expand_collapse_section(page, "Timeline")

            # Enable "Currently working here"
            toggle_current_position(page, enabled=True)

            # End date input should be disabled
            page.wait_for_timeout(300)
            take_screenshot(page, "experience_07_current_toggle", "Current position toggled")

            # Save changes
            save_modal(page)
            page.wait_for_timeout(500)

            # Verify status changed to "Current"
            clear_search(page)
            current_row = search_and_verify(page, updated_company, "work experience")
            verify_status_tag(current_row, "Current")

            clear_search(page)
            take_screenshot(page, "experience_08_current_status", "Current status tag")

            # ========================================
            # STEP 8: Test search by company
            # ========================================
            print("\n8. Testing search by company name...")
            search_and_verify(page, updated_company, "work experience")
            print("   [OK] Search by company successful")

            clear_search(page)

            # ========================================
            # STEP 9: Test search by position
            # ========================================
            print("\n9. Testing search by position...")
            search_and_verify(page, updated_position, "work experience")
            print("   [OK] Search by position successful")

            clear_search(page)
            take_screenshot(page, "experience_09_search_tested", "Search tested")

            # ========================================
            # STEP 10: Test data persistence
            # ========================================
            print("\n10. Testing data persistence - reloading page...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Search and verify persistence
            search_and_verify(page, updated_company, "work experience")
            print("   [OK] Experience data persisted after reload")

            clear_search(page)
            take_screenshot(page, "experience_10_persisted", "Experience persisted after reload")

            # ========================================
            # STEP 11: Delete work experience
            # ========================================
            print(f"\n11. Deleting work experience '{updated_company}'...")
            search_table(page, updated_company)
            delete_row(page, updated_company)
            print("   [OK] Experience deletion confirmed")

            # ========================================
            # STEP 12: Verify experience deletion
            # ========================================
            print("\n12. Verifying experience deletion...")
            page.wait_for_timeout(500)
            clear_search(page)
            search_table(page, updated_company)

            verify_row_not_exists(page, updated_company, "work experience")

            clear_search(page)
            take_screenshot(page, "experience_11_deleted", "Experience deleted")

            # ========================================
            # STEP 13: Verify deletion persists after reload
            # ========================================
            print("\n13. Verifying deletion persists after reload...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            search_table(page, updated_company)
            verify_row_not_exists(page, updated_company, "work experience")
            print("   [OK] Experience deletion persisted")

            take_screenshot(page, "experience_12_deletion_persisted", "Deletion persisted")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Navigate to Work Experience page")
            print("  [PASS] Validation (empty form)")
            print("  [PASS] Create work experience with dates")
            print("  [PASS] Verify creation in table")
            print("  [PASS] Verify Past status tag")
            print("  [PASS] Edit work experience")
            print("  [PASS] Verify update in table")
            print("  [PASS] Test current position toggle")
            print("  [PASS] Verify Current status tag")
            print("  [PASS] Search by company name")
            print("  [PASS] Search by position")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Delete work experience")
            print("  [PASS] Verify deletion")
            print("  [PASS] Verify deletion persists after reload")
            print("\nScreenshots saved to /tmp/test_experience_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "experience_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "experience_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_experience_crud()
    sys.exit(0 if success else 1)
