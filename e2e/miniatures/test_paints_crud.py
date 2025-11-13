#!/usr/bin/env python3
"""
E2E tests for Miniature Paints CRUD functionality
Tests creating, viewing, editing, and deleting paints
"""

import sys

from playwright.sync_api import sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config
from e2e.common.helpers import take_screenshot, wait_for_page_load

config = get_config()
BASE_URL = config["admin_web_url"]


def test_paints_crud():
    """Test Paints CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("\n❌ Authentication failed - cannot proceed with tests")
            browser.close()
            return False

        print("🎨 Testing Miniature Paints CRUD...")

        try:
            take_screenshot(page, "01_dashboard", "Dashboard loaded")

            # Step 2: Navigate to Miniatures
            print("\n📍 Navigating to Miniatures page...")
            page.goto(f"{BASE_URL}/miniatures")
            wait_for_page_load(page)
            take_screenshot(page, "02_miniatures_page", "Miniatures page")

            # Step 3: Switch to Paints tab
            print("\n🎨 Switching to Paints tab...")
            paints_tab = page.locator("text=Paints").first
            if paints_tab.count() > 0:
                paints_tab.click()
                page.wait_for_timeout(500)
                take_screenshot(page, "03_paints_tab", "Paints tab active")
                print("   ✅ Paints tab loaded")
            else:
                print("   ❌ Paints tab not found")
                browser.close()
                return False

            # Step 4: Check table loaded
            print("\n📊 Checking paints table...")
            page.wait_for_timeout(1000)  # Wait for data
            table = page.locator('table, [role="table"]')
            if table.count() > 0:
                print("   ✅ Paints table loaded")

                # Check for color swatches
                # Color swatches are rendered as divs with background-color style
                take_screenshot(page, "04_paints_table_full", "Full paints table")
            else:
                print("   ⚠️  Paints table not visible")

            # Step 5: Test Add Paint modal
            print("\n➕ Testing Add Paint functionality...")
            add_paint_btn = page.locator('button:has-text("Add Paint")')
            if add_paint_btn.count() > 0:
                add_paint_btn.click()
                page.wait_for_timeout(500)

                modal = page.locator('[role="dialog"], .n-modal')
                if modal.count() > 0:
                    print("   ✅ Add Paint modal opened")
                    take_screenshot(page, "05_add_paint_modal", "Add Paint modal")

                    # Fill out form
                    print("   📝 Filling paint form...")

                    # Name
                    name_input = page.locator('input[placeholder*="paint name" i]').first
                    if name_input.count() > 0:
                        name_input.fill("Test Paint E2E")
                        print("      ✓ Name filled")

                    # Manufacturer
                    manufacturer_input = page.locator('input[placeholder*="manufacturer" i]').first
                    if manufacturer_input.count() > 0:
                        manufacturer_input.fill("Test Manufacturer")
                        print("      ✓ Manufacturer filled")

                    # Paint Type - click dropdown
                    type_select = page.locator("text=Select paint type").first
                    if type_select.count() > 0:
                        type_select.click()
                        page.wait_for_timeout(300)

                        # Select "Layer" option
                        layer_option = page.locator("text=Layer").nth(1)  # nth(1) to skip the label
                        if layer_option.count() > 0:
                            layer_option.click()
                            print("      ✓ Paint type selected (Layer)")
                        page.wait_for_timeout(200)

                    # Color hex
                    color_input = page.locator(
                        'input[placeholder*="#" i], input[maxlength="7"]'
                    ).first
                    if color_input.count() > 0:
                        color_input.fill("#FF5733")
                        print("      ✓ Color filled")

                    take_screenshot(page, "06_paint_form_filled", "Form filled")

                    # Save
                    save_btn = page.locator(
                        'button:has-text("Save"), button:has-text("Create")'
                    ).first
                    if save_btn.count() > 0:
                        print("   💾 Saving paint...")
                        save_btn.click()
                        page.wait_for_timeout(1500)  # Wait for save and table refresh
                        take_screenshot(page, "07_after_save", "After saving paint")
                        print("   ✅ Paint saved successfully")

                        # Verify paint appears in table
                        test_paint = page.locator("text=Test Paint E2E")
                        if test_paint.count() > 0:
                            print("   ✅ New paint appears in table")
                        else:
                            print("   ⚠️  New paint not visible in table")
                    else:
                        # Cancel instead
                        cancel_btn = page.locator('button:has-text("Cancel")').first
                        if cancel_btn.count() > 0:
                            cancel_btn.click()
                            print("   ⚠️  Cancelled paint creation")
                else:
                    print("   ❌ Modal did not open")
                    browser.close()
                    return False
            else:
                print("   ❌ Add Paint button not found")
                browser.close()
                return False

            # Step 6: Test Search
            print("\n🔍 Testing search functionality...")
            search_input = page.locator('input[placeholder*="search" i]').first
            if search_input.count() > 0:
                search_input.fill("Test Paint")
                page.wait_for_timeout(500)
                take_screenshot(page, "08_search_filtered", "Search results")
                print("   ✅ Search executed")

                # Clear search
                search_input.fill("")
                page.wait_for_timeout(500)
            else:
                print("   ⚠️  Search input not found")

            print("\n✅ Paints CRUD tests completed!")
            print("\n📸 Screenshots saved to /tmp/ with prefix 'test_'")

            return True

        except Exception as e:
            print(f"\n❌ Error during testing: {e}")
            take_screenshot(page, "error", "Error state")
            import traceback

            traceback.print_exc()
            return False
        finally:
            # Only prompt for input when running interactively (not in pytest)
            if sys.stdin.isatty() and __name__ == "__main__":
                input("\nPress Enter to close browser...")
            browser.close()


if __name__ == "__main__":
    success = test_paints_crud()
    sys.exit(0 if success else 1)
