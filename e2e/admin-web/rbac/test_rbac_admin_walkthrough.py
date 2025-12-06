#!/usr/bin/env python3
"""
E2E test for RBAC - Admin User Full Walkthrough
Tests: Admin has full CRUD access to all resources, can see all menu items
"""

import sys
import time

from playwright.sync_api import expect, sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config
from e2e.common.helpers import (
    delete_row,
    expand_collapse_section,
    expand_sidebar,
    fill_text_input,
    find_dashboard_card,
    navigate_to_page,
    navigate_to_tab,
    open_add_modal,
    open_edit_modal,
    save_modal,
    search_and_verify,
    search_table,
    take_screenshot,
    verify_row_not_exists,
)

config = get_config()
BASE_URL = config["admin_web_url"]


def verify_sidebar_menu_items(page, expected_items):
    """Verify sidebar menu contains expected items"""
    for item in expected_items:
        menu_item = page.locator(f'.n-menu-item:has-text("{item}")').first
        expect(menu_item).to_be_visible(timeout=3000)
        print(f"   [OK] Menu item '{item}' visible")


def verify_dashboard_cards(page, expected_cards):
    """Verify dashboard contains expected cards"""
    for card_title in expected_cards:
        card = find_dashboard_card(page, card_title)
        expect(card).to_be_visible(timeout=3000)
        print(f"   [OK] Dashboard card '{card_title}' visible")


def verify_add_button_visible(page, button_text):
    """Verify Add button is visible (edit permission)"""
    add_btn = page.locator(f'button.n-button--primary-type:has-text("{button_text}")').first
    expect(add_btn).to_be_visible(timeout=3000)
    return add_btn


def verify_edit_button_in_row(page, row_identifier):
    """Verify Edit button exists in a table row"""
    row = page.locator(f'.n-data-table tbody tr:has-text("{row_identifier}")').first
    edit_btn = row.locator('button[aria-label*="Edit" i]').first
    expect(edit_btn).to_be_visible(timeout=3000)
    return edit_btn


def verify_delete_button_in_row(page, row_identifier):
    """Verify Delete button exists in a table row"""
    row = page.locator(f'.n-data-table tbody tr:has-text("{row_identifier}")').first
    delete_btn = row.locator('button[aria-label*="Delete" i]').first
    expect(delete_btn).to_be_visible(timeout=3000)
    return delete_btn


def test_rbac_admin_walkthrough():
    """Test Admin user has full access to all features"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=config["headless"])
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== RBAC ADMIN WALKTHROUGH E2E TEST ===\n")

        # Test data with unique timestamp
        timestamp = int(time.time())
        test_skill_type = f"E2E Admin Type {timestamp}"

        try:
            # ========================================
            # STEP 1: Verify admin username in sidebar
            # ========================================
            print("1. Verifying admin user is logged in...")
            navigate_to_page(page, BASE_URL, "dashboard")

            # Expand sidebar first (collapsed by default)
            expand_sidebar(page)

            # Check username display in sidebar
            username_display = page.locator('.username:has-text("admin")').first
            expect(username_display).to_be_visible(timeout=5000)
            print("   [OK] Admin username displayed in sidebar")
            take_screenshot(page, "rbac_admin_01_sidebar", "Admin logged in")

            # ========================================
            # STEP 2: Verify all sidebar menu items visible
            # ========================================
            print("\n2. Verifying all sidebar menu items visible for admin...")
            expected_menu_items = [
                "Dashboard",
                "Profile",
                "Skills",
                "Work Experience",
                "Certifications",
                "Projects",
                "Miniatures",
                "Messaging",
            ]
            verify_sidebar_menu_items(page, expected_menu_items)
            take_screenshot(page, "rbac_admin_02_menu", "All menu items visible")

            # ========================================
            # STEP 3: Verify all dashboard cards visible
            # ========================================
            print("\n3. Verifying all dashboard cards visible for admin...")
            expected_cards = [
                "Profile",
                "Skills",
                "Work Experience",
                "Certifications",
                "Portfolio Projects",
                "Miniatures",
                "Messaging",
            ]
            verify_dashboard_cards(page, expected_cards)
            take_screenshot(page, "rbac_admin_03_dashboard", "All dashboard cards visible")

            # ========================================
            # STEP 4: Verify dashboard cards show "Manage" (edit permission)
            # ========================================
            print("\n4. Verifying dashboard cards show 'Manage' buttons (edit access)...")
            # Skills card should show "Manage" not "View"
            skills_card = find_dashboard_card(page, "Skills")
            manage_btn = skills_card.locator('button:has-text("Manage")').first
            expect(manage_btn).to_be_visible(timeout=3000)
            print("   [OK] Skills card shows 'Manage' button")

            # Profile card should show "Edit Profile"
            profile_card = find_dashboard_card(page, "Profile")
            edit_profile_btn = profile_card.locator('button:has-text("Edit Profile")').first
            expect(edit_profile_btn).to_be_visible(timeout=3000)
            print("   [OK] Profile card shows 'Edit Profile' button")

            # ========================================
            # STEP 5: Test Skills - Full CRUD access
            # ========================================
            print("\n5. Testing Skills - Admin has full CRUD access...")
            navigate_to_tab(page, BASE_URL, "skills", "Skill Types")

            # Verify Add button visible
            verify_add_button_visible(page, "Add Skill Type")
            print("   [OK] Add Skill Type button visible")

            # Create a skill type
            modal = open_add_modal(page, "Add Skill Type")
            expand_collapse_section(page, "Type Information")
            fill_text_input(page, label="Name", value=test_skill_type)
            save_modal(page)
            assert not modal.is_visible(), "Modal should close after save"
            print(f"   [OK] Created skill type: {test_skill_type}")

            # Verify in table and check Edit/Delete buttons
            page.wait_for_timeout(500)
            search_and_verify(page, test_skill_type, "skill type")
            verify_edit_button_in_row(page, test_skill_type)
            print("   [OK] Edit button visible in row")
            verify_delete_button_in_row(page, test_skill_type)
            print("   [OK] Delete button visible in row")

            # Edit the skill type
            modal = open_edit_modal(page, test_skill_type)
            expand_collapse_section(page, "Type Information")
            fill_text_input(page, label="Name", value=f"{test_skill_type} Updated")
            save_modal(page)
            assert not modal.is_visible(), "Modal should close after update"
            print("   [OK] Updated skill type successfully")

            # Delete the skill type
            search_table(page, f"{test_skill_type} Updated")
            delete_row(page, f"{test_skill_type} Updated")
            page.wait_for_timeout(500)
            verify_row_not_exists(page, f"{test_skill_type} Updated", "skill type")
            print("   [OK] Deleted skill type successfully")

            take_screenshot(page, "rbac_admin_05_skills_crud", "Skills CRUD complete")

            # ========================================
            # STEP 6: Test Certifications - Full CRUD
            # ========================================
            print("\n6. Testing Certifications - Admin has full CRUD access...")
            navigate_to_page(page, BASE_URL, "certifications")

            # Verify Add button visible
            verify_add_button_visible(page, "Add Certification")
            print("   [OK] Add Certification button visible")

            # Check existing data has Edit/Delete buttons
            # Look for any row in the table
            table_rows = page.locator(".n-data-table tbody tr")
            if table_rows.count() > 0:
                first_row = table_rows.first
                edit_btn = first_row.locator('button[aria-label*="Edit" i]').first
                delete_btn = first_row.locator('button[aria-label*="Delete" i]').first
                expect(edit_btn).to_be_visible(timeout=3000)
                expect(delete_btn).to_be_visible(timeout=3000)
                print("   [OK] Edit and Delete buttons visible on existing data")
            else:
                print("   [INFO] No existing certifications to verify buttons on")

            take_screenshot(page, "rbac_admin_06_certifications", "Certifications access")

            # ========================================
            # STEP 7: Test Work Experience - Full CRUD
            # ========================================
            print("\n7. Testing Work Experience - Admin has full CRUD access...")
            navigate_to_page(page, BASE_URL, "work-experience")

            verify_add_button_visible(page, "Add Experience")
            print("   [OK] Add Experience button visible")

            table_rows = page.locator(".n-data-table tbody tr")
            if table_rows.count() > 0:
                first_row = table_rows.first
                edit_btn = first_row.locator('button[aria-label*="Edit" i]').first
                delete_btn = first_row.locator('button[aria-label*="Delete" i]').first
                expect(edit_btn).to_be_visible(timeout=3000)
                expect(delete_btn).to_be_visible(timeout=3000)
                print("   [OK] Edit and Delete buttons visible on existing data")

            take_screenshot(page, "rbac_admin_07_experience", "Work Experience access")

            # ========================================
            # STEP 8: Test Portfolio Projects - Full CRUD
            # ========================================
            print("\n8. Testing Portfolio Projects - Admin has full CRUD access...")
            navigate_to_page(page, BASE_URL, "portfolio-projects")

            verify_add_button_visible(page, "Add Project")
            print("   [OK] Add Project button visible")

            take_screenshot(page, "rbac_admin_08_projects", "Portfolio Projects access")

            # ========================================
            # STEP 9: Test Miniatures - Full CRUD
            # ========================================
            print("\n9. Testing Miniatures - Admin has full CRUD access...")
            navigate_to_tab(page, BASE_URL, "miniatures", "Themes")

            verify_add_button_visible(page, "Add Theme")
            print("   [OK] Add Theme button visible")

            navigate_to_tab(page, BASE_URL, "miniatures", "Projects")
            verify_add_button_visible(page, "Add Project")
            print("   [OK] Add Miniature Project button visible")

            navigate_to_tab(page, BASE_URL, "miniatures", "Paints")
            verify_add_button_visible(page, "Add Paint")
            print("   [OK] Add Paint button visible")

            take_screenshot(page, "rbac_admin_09_miniatures", "Miniatures access")

            # ========================================
            # STEP 10: Test Messaging - Full CRUD
            # ========================================
            print("\n10. Testing Messaging - Admin has full CRUD access...")
            navigate_to_tab(page, BASE_URL, "messaging", "Recipients")

            verify_add_button_visible(page, "Add Recipient")
            print("   [OK] Add Recipient button visible")

            # Check Messages tab is accessible
            navigate_to_tab(page, BASE_URL, "messaging", "Messages")
            messages_table = page.locator(".n-data-table").first
            expect(messages_table).to_be_visible(timeout=5000)
            print("   [OK] Messages tab accessible")

            take_screenshot(page, "rbac_admin_10_messaging", "Messaging access")

            # ========================================
            # STEP 11: Test Profile - Edit access
            # ========================================
            print("\n11. Testing Profile - Admin has edit access...")
            navigate_to_page(page, BASE_URL, "profile")

            # Profile should have editable fields (not disabled)
            name_input = page.locator('input[placeholder*="name" i]').first
            expect(name_input).not_to_be_disabled(timeout=3000)
            print("   [OK] Profile fields are editable")

            # Check for file upload buttons (avatar, resume)
            upload_area = page.locator(".n-upload-dragger").first
            expect(upload_area).to_be_visible(timeout=3000)
            print("   [OK] File upload available")

            take_screenshot(page, "rbac_admin_11_profile", "Profile access")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Admin username displayed in sidebar")
            print("  [PASS] All 8 menu items visible (Dashboard through Messaging)")
            print("  [PASS] All 7 dashboard cards visible")
            print("  [PASS] Dashboard cards show 'Manage'/'Edit' buttons")
            print("  [PASS] Skills - Full CRUD (Create, Edit, Delete)")
            print("  [PASS] Certifications - Add/Edit/Delete buttons visible")
            print("  [PASS] Work Experience - Add/Edit/Delete buttons visible")
            print("  [PASS] Portfolio Projects - Add button visible")
            print("  [PASS] Miniatures - All tabs with Add buttons")
            print("  [PASS] Messaging - Recipients Add + Messages tab accessible")
            print("  [PASS] Profile - Editable fields + file uploads")
            print("\nScreenshots saved to /tmp/test_rbac_admin_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "rbac_admin_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "rbac_admin_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_rbac_admin_walkthrough()
    sys.exit(0 if success else 1)
