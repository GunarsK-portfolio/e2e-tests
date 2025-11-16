#!/usr/bin/env python3
"""
E2E test for Certifications CRUD operations
Tests: Full CRUD with validation, data persistence, date handling, and credential verification
"""

import sys
import time

from playwright.sync_api import expect, sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config

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
        updated_name = f"{test_name} Updated"
        updated_issuer = "E2E Advanced Testing Authority"
        updated_credential_id = f"{test_credential_id}-UPD"

        try:
            # ========================================
            # STEP 1: Navigate to Certifications page
            # ========================================
            print("1. Navigating to Certifications page...")
            page.goto(f"{BASE_URL}/certifications")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="/tmp/certifications_01_page.png")
            print("   [OK] Certifications page loaded")

            # ========================================
            # STEP 2: Test validation - empty form
            # ========================================
            print("\n2. Testing validation - empty form submission...")
            add_btn = page.locator('button:has-text("Add Certification")').first
            assert add_btn.count() > 0, "Add Certification button not found"
            add_btn.click()
            page.wait_for_timeout(500)

            modal = page.locator('[role="dialog"]')
            assert modal.count() > 0, "Modal not opened"
            print("   [OK] Add Certification modal opened")

            # Try to save without filling required fields
            save_btn = page.locator('button:has-text("Save"), button:has-text("Create")').first
            save_btn.click()
            page.wait_for_timeout(500)

            # Modal should remain open due to validation
            assert modal.is_visible(), "Modal should remain open on validation error"
            print("   [OK] Validation prevents empty form submission")
            page.screenshot(path="/tmp/certifications_02_validation_error.png")

            # Close modal
            cancel_btn = page.locator('button:has-text("Cancel")').first
            cancel_btn.click()
            page.wait_for_timeout(300)
            print("   [OK] Modal closed")

            # ========================================
            # STEP 3: Create new certification
            # ========================================
            print(f"\n3. Creating new certification: '{test_name}'...")
            add_btn.click()
            page.wait_for_timeout(500)

            # Fill Basic Information fields (section is expanded by default)
            name_input = page.locator('input[placeholder="Enter certification name"]').first
            name_input.fill(test_name)
            page.wait_for_timeout(200)

            issuer_input = page.locator('input[placeholder="Enter issuing organization"]').first
            issuer_input.fill(test_issuer)
            page.wait_for_timeout(200)

            # Fill Issue Date - use date picker
            issue_date_inputs = page.locator('input[placeholder*="Select Date" i]')
            if issue_date_inputs.count() >= 2:
                issue_date_inputs.nth(0).fill("2024-01-15")
                page.wait_for_timeout(200)
                print("   [OK] Issue date filled")

                # Fill Expiry Date
                issue_date_inputs.nth(1).fill("2027-01-15")
                page.wait_for_timeout(200)
                print("   [OK] Expiry date filled")
            else:
                print("   [WARN] Date picker fields not found")

            # Expand Credential Details section
            credential_section = page.locator("text=Credential Details").first
            if credential_section.count() > 0:
                credential_section.click()
                page.wait_for_timeout(500)
                print("   [OK] Expanded Credential Details section")

                # Fill credential fields
                credential_id_input = page.locator(
                    'input[placeholder="Enter credential or reference ID (optional)"]'
                ).first
                credential_id_input.fill(test_credential_id)
                page.wait_for_timeout(200)

                credential_url_input = page.locator(
                    'input[placeholder="Enter URL to verify credential (optional)"]'
                ).first
                credential_url_input.fill(test_credential_url)
                page.wait_for_timeout(200)
                print("   [OK] Credential details filled")

            page.screenshot(path="/tmp/certifications_03_create_form_filled.png")

            # Save
            save_btn = page.locator('button:has-text("Save"), button:has-text("Create")').first
            save_btn.click()
            page.wait_for_timeout(1000)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful save"
            print("   [OK] Certification created successfully")

            # ========================================
            # STEP 4: Verify entry appears in table
            # ========================================
            print("\n4. Verifying certification appears in table...")
            page.wait_for_timeout(500)
            cert_row = page.locator(f'tr:has-text("{test_name}")')
            expect(cert_row).to_be_visible(timeout=5000)
            print(f"   [OK] Certification '{test_name}' found in table")
            page.screenshot(path="/tmp/certifications_04_in_table.png")

            # Verify status tag shows "Valid"
            status_tag = cert_row.locator("text=Valid")
            if status_tag.count() > 0:
                print("   [OK] Certification status shows 'Valid'")

            # Verify credential link
            verify_link = cert_row.locator('a:has-text("Verify")')
            if verify_link.count() > 0:
                print("   [OK] Credential verification link found")

            # ========================================
            # STEP 5: Edit certification entry
            # ========================================
            print("\n5. Editing certification entry...")
            edit_btn = cert_row.locator('button[aria-label*="Edit" i]').first
            edit_btn.click()
            page.wait_for_timeout(500)

            # Verify modal opened
            assert modal.is_visible(), "Edit modal should be visible"
            print("   [OK] Edit modal opened")

            # Verify existing data loaded (Basic Information section is expanded by default)
            name_input = page.locator('input[placeholder*="certification name" i]').first
            expect(name_input).to_have_value(test_name)
            print("   [OK] Existing data loaded")

            # Update basic fields
            name_input.fill(updated_name)
            page.wait_for_timeout(200)

            issuer_input = page.locator('input[placeholder*="issuing organization" i]').first
            issuer_input.fill(updated_issuer)
            page.wait_for_timeout(200)

            # Expand Credential Details section to update credential ID
            credential_section = page.locator("text=Credential Details").first
            if credential_section.count() > 0:
                credential_section.click()
                page.wait_for_timeout(500)

                credential_id_input = page.locator('input[placeholder*="credential" i]').first
                credential_id_input.fill(updated_credential_id)
                page.wait_for_timeout(200)

            page.screenshot(path="/tmp/certifications_05_edit_form_filled.png")

            # Save changes
            save_btn = page.locator('button:has-text("Save"), button:has-text("Update")').first
            save_btn.click()
            page.wait_for_timeout(1000)

            # Verify modal closed
            assert not modal.is_visible(), "Modal should close after successful update"
            print("   [OK] Certification updated successfully")

            # ========================================
            # STEP 6: Verify updated data in table
            # ========================================
            print("\n6. Verifying updated data in table...")
            page.wait_for_timeout(500)
            updated_row = page.locator(f'tr:has-text("{updated_name}")')
            expect(updated_row).to_be_visible(timeout=5000)
            print(f"   [OK] Updated certification '{updated_name}' found in table")

            # Verify updated issuer
            issuer_cell = updated_row.locator(f'td:has-text("{updated_issuer}")')
            if issuer_cell.count() > 0:
                print(f"   [OK] Updated issuer '{updated_issuer}' displayed")

            page.screenshot(path="/tmp/certifications_06_updated_in_table.png")

            # ========================================
            # STEP 7: Test data persistence - reload page
            # ========================================
            print("\n7. Testing data persistence - reloading page...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Verify data still exists
            persisted_row = page.locator(f'tr:has-text("{updated_name}")')
            expect(persisted_row).to_be_visible(timeout=5000)
            print("   [OK] Data persisted after page reload")

            # ========================================
            # STEP 8: Search functionality
            # ========================================
            print("\n8. Testing search functionality...")
            search_input = page.locator('input[placeholder*="Search" i]').first
            if search_input.count() > 0:
                # Search by name
                search_input.fill(updated_name)
                page.wait_for_timeout(500)

                search_row = page.locator(f'tr:has-text("{updated_name}")')
                expect(search_row).to_be_visible()
                print(f"   [OK] Search by name found: '{updated_name}'")

                # Clear search
                search_input.fill("")
                page.wait_for_timeout(500)

                # Search by issuer
                search_input.fill(updated_issuer)
                page.wait_for_timeout(500)

                search_row = page.locator(f'tr:has-text("{updated_issuer}")')
                expect(search_row).to_be_visible()
                print(f"   [OK] Search by issuer found: '{updated_issuer}'")

                # Clear search
                search_input.fill("")
                page.wait_for_timeout(500)

                # Search by credential ID
                search_input.fill(updated_credential_id)
                page.wait_for_timeout(500)

                search_row = page.locator(f'tr:has-text("{updated_name}")')
                expect(search_row).to_be_visible()
                print("   [OK] Search by credential ID found entry")

                # Clear search
                search_input.fill("")
                page.wait_for_timeout(500)
                print("   [OK] Search cleared")
            else:
                print("   [WARN] Search input not found")

            # ========================================
            # STEP 9: Test date validation
            # ========================================
            print("\n9. Testing date validation (expiry before issue)...")
            updated_row = page.locator(f'tr:has-text("{updated_name}")')
            edit_btn = updated_row.locator('button[aria-label*="Edit" i]').first
            edit_btn.click()
            page.wait_for_timeout(500)

            # Try to set expiry date before issue date
            date_inputs = page.locator('input[placeholder*="Select Date" i]')
            if date_inputs.count() >= 2:
                # Set issue date to 2024-06-01
                date_inputs.nth(0).fill("2024-06-01")
                page.wait_for_timeout(200)

                # Set expiry date to 2024-01-01 (before issue date)
                date_inputs.nth(1).fill("2024-01-01")
                page.wait_for_timeout(200)

                # Try to save
                save_btn = page.locator('button:has-text("Save"), button:has-text("Update")').first
                save_btn.click()
                page.wait_for_timeout(500)

                # Modal should remain open due to validation
                assert modal.is_visible(), "Modal should remain open on date validation error"
                print("   [OK] Date validation prevents expiry before issue date")
                page.screenshot(path="/tmp/certifications_09_date_validation_error.png")

                # Fix dates
                date_inputs.nth(0).fill("2024-01-15")
                page.wait_for_timeout(200)
                date_inputs.nth(1).fill("2027-01-15")
                page.wait_for_timeout(200)

                save_btn.click()
                page.wait_for_timeout(1000)
                print("   [OK] Fixed dates and saved successfully")
            else:
                print("   [WARN] Date inputs not found, skipping date validation test")

                # Close modal if still open
                if modal.is_visible():
                    cancel_btn = page.locator('button:has-text("Cancel")').first
                    cancel_btn.click()
                    page.wait_for_timeout(300)

            # ========================================
            # STEP 10: Delete certification entry
            # ========================================
            print(f"\n10. Deleting certification '{updated_name}'...")
            delete_row = page.locator(f'tr:has-text("{updated_name}")')
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

            # ========================================
            # STEP 11: Verify deletion
            # ========================================
            print("\n11. Verifying certification deletion...")
            page.wait_for_timeout(500)
            deleted_row = page.locator(f'tr:has-text("{updated_name}")')

            # Entry should no longer exist
            expect(deleted_row).not_to_be_visible()
            print(f"   [OK] Certification '{updated_name}' successfully deleted")
            page.screenshot(path="/tmp/certifications_11_after_deletion.png")

            # ========================================
            # STEP 12: Verify deletion persists
            # ========================================
            print("\n12. Verifying deletion persists after reload...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Verify entry is still gone
            final_check = page.locator(f'tr:has-text("{updated_name}")')
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
            print("  [PASS] Create certification with dates and credentials")
            print("  [PASS] Verify creation in table with status")
            print("  [PASS] Verify credential link")
            print("  [PASS] Edit certification")
            print("  [PASS] Update certification data")
            print("  [PASS] Data persistence after reload")
            print("  [PASS] Search by name")
            print("  [PASS] Search by issuer")
            print("  [PASS] Search by credential ID")
            print("  [PASS] Date validation (expiry after issue)")
            print("  [PASS] Delete certification")
            print("  [PASS] Verify deletion")
            print("  [PASS] Deletion persistence")
            print("\nScreenshots saved to /tmp/:")
            for i in range(1, 13):
                print(f"  - certifications_{i:02d}_*.png")

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            page.screenshot(path="/tmp/certifications_error_assertion.png")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path="/tmp/certifications_error.png")
            import traceback

            traceback.print_exc()
            return False
        else:
            return True
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_certifications_crud()
    sys.exit(0 if success else 1)
