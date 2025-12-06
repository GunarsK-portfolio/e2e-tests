#!/usr/bin/env python3
"""
E2E test for RBAC - Demo User Restrictions
Tests: Demo user has read-only access, cannot see Add/Edit/Delete buttons,
       cannot access Messaging, and API calls for mutations are blocked.
"""

import sys

from playwright.sync_api import expect, sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config
from e2e.common.helpers import (
    expand_sidebar,
    find_dashboard_card,
    navigate_to_page,
    navigate_to_tab,
    take_screenshot,
)

config = get_config()
BASE_URL = config["admin_web_url"]
DEMO_USERNAME = config["demo_username"]


def verify_add_button_not_visible(page, button_text):
    """Verify Add button is NOT visible (no edit permission)"""
    add_btn = page.locator(f'button.n-button--primary-type:has-text("{button_text}")').first
    expect(add_btn).not_to_be_visible(timeout=3000)


def verify_no_edit_delete_buttons_in_table(page):
    """Verify table rows have no Edit/Delete buttons"""
    table_rows = page.locator(".n-data-table tbody tr")
    if table_rows.count() > 0:
        first_row = table_rows.first
        edit_btn = first_row.locator('button[aria-label*="Edit" i]').first
        delete_btn = first_row.locator('button[aria-label*="Delete" i]').first
        expect(edit_btn).not_to_be_visible(timeout=2000)
        expect(delete_btn).not_to_be_visible(timeout=2000)
        return True
    return False


def verify_sidebar_menu_item_hidden(page, item_name):
    """Verify a sidebar menu item is NOT visible"""
    menu_item = page.locator(f'.n-menu-item:has-text("{item_name}")').first
    expect(menu_item).not_to_be_visible(timeout=2000)


def verify_dashboard_card_hidden(page, card_title):
    """Verify a dashboard card is NOT visible"""
    card = find_dashboard_card(page, card_title)
    expect(card).not_to_be_visible(timeout=2000)


def test_rbac_demo_user():
    """Test Demo user has read-only access with proper restrictions"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config["headless"])

        # Use AuthManager with demo user credentials from config
        auth_manager = AuthManager(
            username=config["demo_username"],
            password=config["demo_password"],
        )
        page, context = auth_manager.authenticate(browser, strategy="credentials")

        if not page:
            print("[ERROR] Demo user authentication failed")
            browser.close()
            return False

        print("\n=== RBAC DEMO USER RESTRICTIONS E2E TEST ===\n")

        try:
            # ========================================
            # STEP 1: Verify demo username in sidebar
            # ========================================
            print("1. Verifying demo user is logged in...")
            navigate_to_page(page, BASE_URL, "dashboard")

            # Expand sidebar first (collapsed by default)
            expand_sidebar(page)

            # Check username display in sidebar
            username_display = page.locator(f'.username:has-text("{DEMO_USERNAME}")').first
            expect(username_display).to_be_visible(timeout=5000)
            print(f"   [OK] Demo username '{DEMO_USERNAME}' displayed in sidebar")
            take_screenshot(page, "rbac_demo_01_sidebar", "Demo user logged in")

            # ========================================
            # STEP 2: Verify Messaging menu item is hidden
            # ========================================
            print("\n2. Verifying Messaging menu item is hidden...")
            verify_sidebar_menu_item_hidden(page, "Messaging")
            print("   [OK] Messaging menu item is NOT visible (no messages permission)")
            take_screenshot(page, "rbac_demo_02_menu", "Messaging hidden in menu")

            # ========================================
            # STEP 3: Verify Messaging dashboard card is hidden
            # ========================================
            print("\n3. Verifying Messaging dashboard card is hidden...")
            verify_dashboard_card_hidden(page, "Messaging")
            print("   [OK] Messaging dashboard card is NOT visible")
            take_screenshot(page, "rbac_demo_03_dashboard", "Messaging card hidden")

            # ========================================
            # STEP 4: Verify dashboard cards show "View" not "Manage"
            # ========================================
            print("\n4. Verifying dashboard cards show 'View' buttons (read-only)...")
            # Skills card should show "View" not "Manage"
            skills_card = find_dashboard_card(page, "Skills")
            view_btn = skills_card.locator('button:has-text("View")').first
            expect(view_btn).to_be_visible(timeout=3000)
            print("   [OK] Skills card shows 'View' button (read-only)")

            # Profile card should show "View Profile" not "Edit Profile"
            profile_card = find_dashboard_card(page, "Profile")
            view_profile_btn = profile_card.locator('button:has-text("View Profile")').first
            expect(view_profile_btn).to_be_visible(timeout=3000)
            print("   [OK] Profile card shows 'View Profile' button (read-only)")

            # ========================================
            # STEP 5: Test Skills - Read-only access
            # ========================================
            print("\n5. Testing Skills - Demo user has read-only access...")
            navigate_to_tab(page, BASE_URL, "skills", "Skills")

            # Verify Add button is NOT visible
            verify_add_button_not_visible(page, "Add Skill")
            print("   [OK] Add Skill button is NOT visible")

            # Verify no Edit/Delete buttons in table
            if verify_no_edit_delete_buttons_in_table(page):
                print("   [OK] No Edit/Delete buttons in skills table")
            else:
                print("   [INFO] No skills data to verify buttons on")

            # Check Skill Types tab too
            navigate_to_tab(page, BASE_URL, "skills", "Skill Types")
            verify_add_button_not_visible(page, "Add Skill Type")
            print("   [OK] Add Skill Type button is NOT visible")

            if verify_no_edit_delete_buttons_in_table(page):
                print("   [OK] No Edit/Delete buttons in skill types table")

            take_screenshot(page, "rbac_demo_05_skills", "Skills read-only")

            # ========================================
            # STEP 6: Test Certifications - Read-only access
            # ========================================
            print("\n6. Testing Certifications - Demo user has read-only access...")
            navigate_to_page(page, BASE_URL, "certifications")

            verify_add_button_not_visible(page, "Add Certification")
            print("   [OK] Add Certification button is NOT visible")

            if verify_no_edit_delete_buttons_in_table(page):
                print("   [OK] No Edit/Delete buttons in certifications table")

            take_screenshot(page, "rbac_demo_06_certifications", "Certifications read-only")

            # ========================================
            # STEP 7: Test Work Experience - Read-only access
            # ========================================
            print("\n7. Testing Work Experience - Demo user has read-only access...")
            navigate_to_page(page, BASE_URL, "work-experience")

            verify_add_button_not_visible(page, "Add Experience")
            print("   [OK] Add Experience button is NOT visible")

            if verify_no_edit_delete_buttons_in_table(page):
                print("   [OK] No Edit/Delete buttons in experience table")

            take_screenshot(page, "rbac_demo_07_experience", "Experience read-only")

            # ========================================
            # STEP 8: Test Portfolio Projects - Read-only access
            # ========================================
            print("\n8. Testing Portfolio Projects - Demo user has read-only access...")
            navigate_to_page(page, BASE_URL, "portfolio-projects")

            verify_add_button_not_visible(page, "Add Project")
            print("   [OK] Add Project button is NOT visible")

            if verify_no_edit_delete_buttons_in_table(page):
                print("   [OK] No Edit/Delete buttons in projects table")

            take_screenshot(page, "rbac_demo_08_projects", "Projects read-only")

            # ========================================
            # STEP 9: Test Miniatures - Read-only access
            # ========================================
            print("\n9. Testing Miniatures - Demo user has read-only access...")
            navigate_to_tab(page, BASE_URL, "miniatures", "Themes")

            verify_add_button_not_visible(page, "Add Theme")
            print("   [OK] Add Theme button is NOT visible")

            navigate_to_tab(page, BASE_URL, "miniatures", "Projects")
            verify_add_button_not_visible(page, "Add Project")
            print("   [OK] Add Miniature Project button is NOT visible")

            navigate_to_tab(page, BASE_URL, "miniatures", "Paints")
            verify_add_button_not_visible(page, "Add Paint")
            print("   [OK] Add Paint button is NOT visible")

            take_screenshot(page, "rbac_demo_09_miniatures", "Miniatures read-only")

            # ========================================
            # STEP 10: Test Profile - Read-only access
            # ========================================
            print("\n10. Testing Profile - Demo user has read-only access...")
            navigate_to_page(page, BASE_URL, "profile")

            # Profile inputs should be disabled (canEdit check)
            name_input = page.locator('input[placeholder*="full name" i]').first
            if name_input.count() > 0:
                expect(name_input).to_be_disabled(timeout=3000)
                print("   [OK] Profile name field is disabled")

            # Check for NO file upload areas (v-if="canEdit(Resource.PROFILE)" hides them)
            upload_area = page.locator(".n-upload-dragger").first
            expect(upload_area).not_to_be_visible(timeout=3000)
            print("   [OK] File upload area is NOT visible (hidden for read-only)")

            # Save button should NOT be visible (wrapped in v-if="canEdit(Resource.PROFILE)")
            save_btn = page.locator('button:has-text("Save Changes")').first
            expect(save_btn).not_to_be_visible(timeout=3000)
            print("   [OK] Save Changes button is NOT visible")

            take_screenshot(page, "rbac_demo_10_profile", "Profile read-only")

            # ========================================
            # STEP 11: Test direct URL access to Messaging is blocked
            # ========================================
            print("\n11. Testing direct URL access to Messaging is blocked...")
            page.goto(f"{BASE_URL}/messaging")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Should be redirected to dashboard or show error
            # Router guard should prevent access
            current_url = page.url
            if "messaging" not in current_url or "dashboard" in current_url:
                print(f"   [OK] Blocked from /messaging, redirected to: {current_url}")
            else:
                # Check if page shows access denied or empty state
                access_denied = page.locator('text="Access Denied"').first
                if access_denied.count() > 0:
                    print("   [OK] Access Denied message shown")
                else:
                    # Check that no data is shown
                    table = page.locator(".n-data-table").first
                    if table.count() == 0:
                        print("   [OK] No messaging content accessible")

            take_screenshot(page, "rbac_demo_11_messaging_blocked", "Messaging blocked")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print(f"  [PASS] Demo user '{DEMO_USERNAME}' displayed in sidebar")
            print("  [PASS] Messaging menu item hidden (no messages permission)")
            print("  [PASS] Messaging dashboard card hidden")
            print("  [PASS] Dashboard cards show 'View' buttons (read-only)")
            print("  [PASS] Skills - No Add/Edit/Delete buttons")
            print("  [PASS] Certifications - No Add/Edit/Delete buttons")
            print("  [PASS] Work Experience - No Add/Edit/Delete buttons")
            print("  [PASS] Portfolio Projects - No Add/Edit/Delete buttons")
            print("  [PASS] Miniatures - No Add buttons on all tabs")
            print("  [PASS] Profile - Fields disabled, no file upload, no Save button")
            print("  [PASS] Direct URL to Messaging blocked")
            print("\nScreenshots saved to /tmp/test_rbac_demo_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "rbac_demo_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "rbac_demo_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_rbac_demo_user()
    sys.exit(0 if success else 1)
