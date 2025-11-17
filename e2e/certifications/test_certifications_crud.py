#!/usr/bin/env python3
"""
E2E test for Certifications CRUD operations
Tests: Validation, Create, Edit, Search, Persistence, Delete, Date validation
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


def test_certifications_crud():
    """Test Certifications page full CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== CERTIFICATIONS E2E TEST ===\n")

        # Test data - unique certification name using timestamp
        test_name = f"E2E Test Certification {int(time.time())}"
        test_issuer = "E2E Testing Authority"
        test_credential_id = f"CERT-E2E-{int(time.time())}"
        test_credential_url = "https://example.com/verify"
        test_issue_date = "2024-01-15"
        test_expiry_date = "2027-01-15"

        updated_name = f"{test_name} Updated"
        updated_issuer = "E2E Advanced Testing Authority"
        updated_credential_id = f"{test_credential_id}-UPD"

        # Date validation test data
        invalid_issue_date = "2024-06-01"
        invalid_expiry_date = "2024-01-01"

        try:
            # ========================================
            # STEP 1: Navigate to Certifications page
            # ========================================
            print("1. Navigating to Certifications page...")
            navigate_to_page(page, BASE_URL, "certifications")
            take_screenshot(page, "certifications_01_page", "Certifications page loaded")
            print("   [OK] Certifications page loaded")

            # ========================================
            # STEP 2: Test validation - empty form
            # ========================================
            print("\n2. Testing validation - empty form submission...")
            modal = open_add_modal(page, "Add Certification")
            print("   [OK] Add Certification modal opened")

            # Try to save without filling required fields
            save_modal(page)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty form submission")
            take_screenshot(page, "certifications_02_validation_error", "Validation error shown")

            # Close modal
            close_modal(page)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Create new certification
            # ========================================
            print(f"\n3. Creating new certification: '{test_name}'...")
            modal = open_add_modal(page, "Add Certification")

            # Fill Basic Information fields (section is expanded by default)
            fill_text_input(page, label="Certification Name", value=test_name)
            fill_text_input(page, label="Issuer", value=test_issuer)

            # Fill dates
            fill_date_input(page, label="Issue Date", date_value=test_issue_date)
            print("   [OK] Issue date filled")
            fill_date_input(page, label="Expiry Date", date_value=test_expiry_date)
            print("   [OK] Expiry date filled")

            # Expand Credential Details section
            expand_collapse_section(page, "Credential Details")
            fill_text_input(page, label="Credential ID", value=test_credential_id)
            fill_text_input(page, label="Credential URL", value=test_credential_url)
            print("   [OK] Credential details filled")

            take_screenshot(page, "certifications_03_create_form_filled", "Create form filled")

            # Save
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Certification created successfully")

            # ========================================
            # STEP 4: Verify entry appears in table
            # ========================================
            print("\n4. Verifying certification appears in table...")
            page.wait_for_timeout(500)

            # Search and verify the new certification
            cert_row = search_and_verify(page, test_name, "certification")

            # Verify status tag shows "Valid"
            assert verify_cell_contains(cert_row, "Valid", "Certification status shows 'Valid'")

            # Verify credential link
            verify_link = cert_row.locator('a:has-text("Verify")').first
            expect(verify_link).to_be_visible()
            print("   [OK] Credential verification link found")

            clear_search(page)
            take_screenshot(page, "certifications_04_in_table", "Certification in table")

            # ========================================
            # STEP 5: Edit certification entry
            # ========================================
            print("\n5. Editing certification entry...")

            # Search to find the certification
            search_table(page, test_name)

            modal = open_edit_modal(page, test_name)
            print("   [OK] Edit modal opened")

            # Verify existing data loaded
            name_input = page.locator('input[placeholder*="certification name" i]').first
            expect(name_input).to_have_value(test_name)
            print("   [OK] Existing data loaded")

            # Update basic fields
            fill_text_input(page, label="Certification Name", value=updated_name)
            fill_text_input(page, label="Issuer", value=updated_issuer)

            # Expand Credential Details section to update credential ID
            expand_collapse_section(page, "Credential Details")
            fill_text_input(page, label="Credential ID", value=updated_credential_id)

            take_screenshot(page, "certifications_05_edit_form_filled", "Edit form filled")

            # Save changes
            save_modal(page)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Certification updated successfully")

            # ========================================
            # STEP 6: Verify updated data in table
            # ========================================
            print("\n6. Verifying updated data in table...")
            page.wait_for_timeout(500)

            clear_search(page)
            updated_row = search_and_verify(page, updated_name, "updated certification")

            # Verify updated issuer
            assert verify_cell_contains(
                updated_row, updated_issuer, f"Updated issuer '{updated_issuer}' displayed"
            )

            clear_search(page)
            take_screenshot(page, "certifications_06_updated_in_table", "Updated in table")

            # ========================================
            # STEP 7: Test search functionality
            # ========================================
            print("\n7. Testing search functionality...")

            # Search by name
            search_and_verify(page, updated_name, "certification")
            print(f"   [OK] Search by name found: '{updated_name}'")
            take_screenshot(page, "certifications_07a_search_by_name", "Search by name")

            # Search by issuer
            clear_search(page)
            search_and_verify(page, updated_issuer, "certification")
            print(f"   [OK] Search by issuer found: '{updated_issuer}'")
            take_screenshot(page, "certifications_07b_search_by_issuer", "Search by issuer")

            clear_search(page)

            # ========================================
            # STEP 8: Test data persistence - reload page
            # ========================================
            print("\n8. Testing data persistence - reloading page...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Verify data still exists
            search_and_verify(page, updated_name, "certification")
            print("   [OK] Data persisted after page reload")

            clear_search(page)
            take_screenshot(page, "certifications_08_persisted", "Data persisted")

            # ========================================
            # STEP 9: Test date validation
            # ========================================
            print("\n9. Testing date validation (expiry before issue)...")
            modal = open_edit_modal(page, updated_name)

            # Try to set expiry date before issue date
            fill_date_input(page, label="Issue Date", date_value=invalid_issue_date)
            fill_date_input(page, label="Expiry Date", date_value=invalid_expiry_date)

            # Try to save
            save_modal(page)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on date validation error"
            print("   [OK] Date validation prevents expiry before issue date")
            take_screenshot(
                page, "certifications_09_date_validation_error", "Date validation error"
            )

            # Fix dates
            fill_date_input(page, label="Issue Date", date_value=test_issue_date)
            fill_date_input(page, label="Expiry Date", date_value=test_expiry_date)

            save_modal(page)
            print("   [OK] Fixed dates and saved successfully")

            # ========================================
            # STEP 10: Delete certification entry
            # ========================================
            print(f"\n10. Deleting certification '{updated_name}'...")
            delete_row(page, updated_name)
            print("   [OK] Deletion confirmed")

            # ========================================
            # STEP 11: Verify deletion
            # ========================================
            print("\n11. Verifying certification deletion...")
            page.wait_for_timeout(500)
            clear_search(page)
            search_table(page, updated_name)

            verify_row_not_exists(page, updated_name, "certification")

            clear_search(page)
            take_screenshot(page, "certifications_11_after_deletion", "After deletion")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Navigate to Certifications page")
            print("  [PASS] Validation (empty form)")
            print("  [PASS] Create certification with dates and credentials")
            print("  [PASS] Verify creation in table with status")
            print("  [PASS] Verify credential link")
            print("  [PASS] Edit certification")
            print("  [PASS] Update certification data")
            print("  [PASS] Search by name")
            print("  [PASS] Search by issuer")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Date validation (expiry after issue)")
            print("  [PASS] Delete certification")
            print("  [PASS] Verify deletion")
            print("\nScreenshots saved to /tmp/test_certifications_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "certifications_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "certifications_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_certifications_crud()
    sys.exit(0 if success else 1)
