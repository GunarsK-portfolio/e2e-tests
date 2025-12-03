"""
E2E test for Messaging CRUD operations
Tests: Recipients CRUD (validation, create, edit, search, delete)
       Messages viewing (read-only, search, view modal)
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
    fill_text_input,
    navigate_to_tab,
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


def toggle_switch(page, label: str, wait_ms: int = 200):
    """Toggle a switch component by form label

    Args:
        page: Playwright page object
        label: Form label text to identify the switch
        wait_ms: Wait time in milliseconds
    """
    form_item = page.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
    switch = form_item.locator(".n-switch").first
    expect(switch).to_be_visible()
    switch.click()
    page.wait_for_timeout(wait_ms)


def click_view_button(page, row, wait_ms: int = 500):
    """Click the view button for a specific row

    Args:
        page: Playwright page object
        row: Row locator (already selected)
        wait_ms: Wait time in milliseconds

    Returns:
        Modal locator
    """
    view_btn = row.locator('button.n-button--small-type[aria-label*="View" i]').first
    expect(view_btn).to_be_visible()
    view_btn.click()
    page.wait_for_timeout(wait_ms)

    modal = page.locator('.n-modal[role="dialog"]')
    expect(modal).to_be_visible()
    return modal


def close_view_modal(page, wait_ms: int = 300):
    """Close the view modal by clicking Close button"""
    close_btn = page.locator('.n-modal button:has-text("Close")').first
    close_btn.click()
    page.wait_for_timeout(wait_ms)


def test_messaging_crud():
    """Test Messaging page full CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=config["headless"])
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== MESSAGING E2E TEST ===\n")

        # Test data - unique recipient using timestamp
        timestamp = int(time.time())
        test_email = f"e2e-test-{timestamp}@example.com"
        test_name = f"E2E Test Recipient {timestamp}"

        updated_email = f"e2e-updated-{timestamp}@example.com"
        updated_name = f"E2E Updated Recipient {timestamp}"

        try:
            # ========================================
            # PART 1: RECIPIENTS CRUD
            # ========================================
            print("=" * 40)
            print("PART 1: RECIPIENTS CRUD")
            print("=" * 40)

            # ========================================
            # STEP 1: Navigate to Messaging page (Recipients tab)
            # ========================================
            print("\n1. Navigating to Messaging page (Recipients tab)...")
            navigate_to_tab(page, BASE_URL, "messaging", "Recipients")
            take_screenshot(page, "messaging_01_recipients_tab", "Recipients tab loaded")
            print("   [OK] Recipients tab loaded")

            # ========================================
            # STEP 2: Test validation - empty form
            # ========================================
            print("\n2. Testing validation - empty form submission...")
            modal = open_add_modal(page, "Add Recipient")
            print("   [OK] Add Recipient modal opened")

            # Try to save without filling required fields
            save_modal(page, wait_ms=500)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty form submission")
            take_screenshot(page, "messaging_02_validation_error", "Validation error shown")

            # Close modal
            close_modal(page)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Test validation - invalid email
            # ========================================
            print("\n3. Testing validation - invalid email format...")
            modal = open_add_modal(page, "Add Recipient")

            # Fill with invalid email
            fill_text_input(page, label="Email", value="invalid-email")

            # Try to save
            save_modal(page, wait_ms=500)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on email validation error"
            print("   [OK] Email validation prevents invalid email")
            take_screenshot(page, "messaging_03_email_validation", "Email validation error")

            # Close modal
            close_modal(page)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 4: Create new recipient
            # ========================================
            print(f"\n4. Creating new recipient: '{test_email}'...")
            modal = open_add_modal(page, "Add Recipient")

            # Fill form fields
            fill_text_input(page, label="Email", value=test_email)
            fill_text_input(page, label="Name", value=test_name)
            # Active switch is on by default

            take_screenshot(page, "messaging_04_create_form_filled", "Create form filled")

            # Save
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Recipient created successfully")

            # ========================================
            # STEP 5: Verify entry appears in table
            # ========================================
            print("\n5. Verifying recipient appears in table...")
            page.wait_for_timeout(500)

            # Search and verify the new recipient
            recipient_row = search_and_verify(page, test_email, "recipient")

            # Verify status tag shows "Active"
            assert verify_cell_contains(recipient_row, "Active", "Recipient status shows 'Active'")

            clear_search(page)
            take_screenshot(page, "messaging_05_in_table", "Recipient in table")

            # ========================================
            # STEP 6: Edit recipient entry
            # ========================================
            print("\n6. Editing recipient entry...")

            # Search to find the recipient
            search_table(page, test_email)

            modal = open_edit_modal(page, test_email)
            print("   [OK] Edit modal opened")

            # Verify existing data loaded - use form label to find the input
            email_form_item = page.locator(
                '.n-form-item:has(.n-form-item-label:has-text("Email"))'
            ).first
            email_input = email_form_item.locator("input").first
            expect(email_input).to_have_value(test_email)
            print("   [OK] Existing data loaded")

            # Update fields
            fill_text_input(page, label="Email", value=updated_email)
            fill_text_input(page, label="Name", value=updated_name)
            # Toggle active switch to inactive
            toggle_switch(page, "Active")

            take_screenshot(page, "messaging_06_edit_form_filled", "Edit form filled")

            # Save changes
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Recipient updated successfully")

            # ========================================
            # STEP 7: Verify updated data in table
            # ========================================
            print("\n7. Verifying updated data in table...")
            page.wait_for_timeout(500)

            clear_search(page)
            updated_row = search_and_verify(page, updated_email, "updated recipient")

            # Verify status tag shows "Inactive"
            assert verify_cell_contains(
                updated_row, "Inactive", "Recipient status shows 'Inactive'"
            )

            clear_search(page)
            take_screenshot(page, "messaging_07_updated_in_table", "Updated in table")

            # ========================================
            # STEP 8: Test search functionality
            # ========================================
            print("\n8. Testing search functionality...")

            # Search by email
            search_and_verify(page, updated_email, "recipient")
            print(f"   [OK] Search by email found: '{updated_email}'")
            take_screenshot(page, "messaging_08a_search_by_email", "Search by email")

            # Search by name
            clear_search(page)
            search_and_verify(page, updated_name, "recipient")
            print(f"   [OK] Search by name found: '{updated_name}'")
            take_screenshot(page, "messaging_08b_search_by_name", "Search by name")

            clear_search(page)

            # ========================================
            # STEP 9: Test data persistence - reload page
            # ========================================
            print("\n9. Testing data persistence - reloading page...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Navigate back to Recipients tab
            navigate_to_tab(page, BASE_URL, "messaging", "Recipients")

            # Verify data still exists
            search_and_verify(page, updated_email, "recipient")
            print("   [OK] Data persisted after page reload")

            clear_search(page)
            take_screenshot(page, "messaging_09_persisted", "Data persisted")

            # ========================================
            # PART 2: MESSAGES VIEW (READ-ONLY)
            # ========================================
            print("\n" + "=" * 40)
            print("PART 2: MESSAGES VIEW (READ-ONLY)")
            print("=" * 40)

            # ========================================
            # STEP 10: Navigate to Messages tab
            # ========================================
            print("\n10. Navigating to Messages tab...")
            messages_tab = page.locator('.n-tabs-tab:has-text("Messages")').first
            messages_tab.click()
            page.wait_for_timeout(500)
            take_screenshot(page, "messaging_10_messages_tab", "Messages tab loaded")
            print("   [OK] Messages tab loaded")

            # ========================================
            # STEP 11: View message details (if messages exist)
            # ========================================
            print("\n11. Testing message view functionality...")

            # Check if there are any messages in the table
            table_rows = page.locator(".n-data-table tbody tr")
            row_count = table_rows.count()

            if row_count > 0:
                # Get the first row's subject for identification
                first_row = table_rows.first
                subject_cell = first_row.locator("td").first
                subject_text = subject_cell.inner_text()

                # Click view button using helper
                view_modal = click_view_button(page, first_row)
                print(f"   [OK] View modal opened for message: '{subject_text[:30]}...'")

                # Verify modal title (parent card header, not nested card headers)
                modal_title = view_modal.locator("> .n-card-header .n-card-header__main")
                expect(modal_title).to_contain_text("Message Details")
                print("   [OK] Modal title is 'Message Details'")

                # Verify modal contains expected sections
                expect(view_modal.locator('text="Subject"')).to_be_visible()
                expect(view_modal.locator('text="From"')).to_be_visible()
                expect(view_modal.locator('text="Status"')).to_be_visible()
                print("   [OK] Modal contains expected fields")

                take_screenshot(page, "messaging_11_view_modal", "Message view modal")

                # Close modal
                close_view_modal(page)
                print("   [OK] View modal closed")
            else:
                print("   [INFO] No messages in table - skipping view test")
                take_screenshot(page, "messaging_11_no_messages", "No messages in table")

            # ========================================
            # STEP 12: Test messages search (if messages exist)
            # ========================================
            print("\n12. Testing messages search functionality...")

            if row_count > 0:
                # Get text from first row to search
                first_row = table_rows.first
                search_text = first_row.locator("td").first.inner_text()[:10]

                search_table(page, search_text)
                page.wait_for_timeout(500)

                # Verify search filters results
                filtered_rows = page.locator(".n-data-table tbody tr")
                assert filtered_rows.count() > 0, "Search should return results"
                print(f"   [OK] Search found {filtered_rows.count()} message(s)")

                clear_search(page)
                take_screenshot(page, "messaging_12_search_messages", "Messages search")
            else:
                print("   [INFO] No messages to search - skipping search test")

            # ========================================
            # PART 3: CLEANUP - DELETE RECIPIENT
            # ========================================
            print("\n" + "=" * 40)
            print("PART 3: CLEANUP")
            print("=" * 40)

            # ========================================
            # STEP 13: Navigate back to Recipients tab
            # ========================================
            print("\n13. Navigating back to Recipients tab...")
            recipients_tab = page.locator('.n-tabs-tab:has-text("Recipients")').first
            recipients_tab.click()
            page.wait_for_timeout(500)
            print("   [OK] Recipients tab loaded")

            # ========================================
            # STEP 14: Delete recipient entry
            # ========================================
            print(f"\n14. Deleting recipient '{updated_email}'...")
            search_table(page, updated_email)
            delete_row(page, updated_email)
            print("   [OK] Deletion confirmed")

            # ========================================
            # STEP 15: Verify deletion
            # ========================================
            print("\n15. Verifying recipient deletion...")
            page.wait_for_timeout(500)
            clear_search(page)
            search_table(page, updated_email)

            verify_row_not_exists(page, updated_email, "recipient")

            clear_search(page)
            take_screenshot(page, "messaging_15_after_deletion", "After deletion")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Navigate to Messaging page (Recipients tab)")
            print("  [PASS] Validation (empty form)")
            print("  [PASS] Validation (invalid email)")
            print("  [PASS] Create recipient with email and name")
            print("  [PASS] Verify creation in table with Active status")
            print("  [PASS] Edit recipient (change email, name, toggle status)")
            print("  [PASS] Verify update in table with Inactive status")
            print("  [PASS] Search by email")
            print("  [PASS] Search by name")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Navigate to Messages tab")
            print("  [PASS] View message details modal (if messages exist)")
            print("  [PASS] Messages search functionality (if messages exist)")
            print("  [PASS] Delete recipient")
            print("  [PASS] Verify deletion")
            print("\nScreenshots saved to /tmp/test_messaging_*.png")

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "messaging_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except (TimeoutError, RuntimeError, ValueError) as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "messaging_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        else:
            return True
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_messaging_crud()
    sys.exit(0 if success else 1)
