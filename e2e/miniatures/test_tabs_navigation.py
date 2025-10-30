#!/usr/bin/env python3
"""
E2E tests for Miniatures tab navigation
Tests switching between Projects, Themes, and Paints tabs
"""

import sys

from playwright.sync_api import sync_playwright

from e2e.auth.login import login
from e2e.common.helpers import take_screenshot, wait_for_page_load

BASE_URL = "http://localhost:5173"


def test_tabs_navigation():
    """Test navigation between Miniatures tabs"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("🗂️  Testing Miniatures Tabs Navigation...")

        try:
            # Login
            if not login(page, base_url=BASE_URL):
                print("\n❌ Authentication failed")
                browser.close()
                return False

            # Navigate to Miniatures
            print("\n📍 Navigating to Miniatures...")
            page.goto(f"{BASE_URL}/miniatures")
            wait_for_page_load(page)
            take_screenshot(page, "tabs_01_initial", "Initial Miniatures page")

            # Test 1: Projects tab (default)
            print("\n1️⃣  Testing Projects tab (default)...")
            projects_tab = page.locator("text=Projects").first
            if projects_tab.count() > 0:
                print("   ✅ Projects tab visible")
                add_project_btn = page.locator('button:has-text("Add Project")')
                if add_project_btn.count() > 0:
                    print("   ✅ Add Project button found")
                    take_screenshot(page, "tabs_02_projects", "Projects tab")
            else:
                print("   ❌ Projects tab not found")

            # Test 2: Themes tab
            print("\n2️⃣  Testing Themes tab...")
            themes_tab = page.locator("text=Themes").first
            if themes_tab.count() > 0:
                themes_tab.click()
                page.wait_for_timeout(500)
                print("   ✅ Switched to Themes tab")

                add_theme_btn = page.locator('button:has-text("Add Theme")')
                if add_theme_btn.count() > 0:
                    print("   ✅ Add Theme button found")
                take_screenshot(page, "tabs_03_themes", "Themes tab")
            else:
                print("   ❌ Themes tab not found")

            # Test 3: Paints tab
            print("\n3️⃣  Testing Paints tab...")
            paints_tab = page.locator("text=Paints").first
            if paints_tab.count() > 0:
                paints_tab.click()
                page.wait_for_timeout(500)
                print("   ✅ Switched to Paints tab")

                add_paint_btn = page.locator('button:has-text("Add Paint")')
                if add_paint_btn.count() > 0:
                    print("   ✅ Add Paint button found")

                # Wait for table to load
                page.wait_for_timeout(1000)
                take_screenshot(page, "tabs_04_paints", "Paints tab")
            else:
                print("   ❌ Paints tab not found")

            # Test 4: Switch back to Projects
            print("\n4️⃣  Testing switching back to Projects...")
            projects_tab = page.locator("text=Projects").first
            if projects_tab.count() > 0:
                projects_tab.click()
                page.wait_for_timeout(500)
                print("   ✅ Switched back to Projects tab")
                take_screenshot(page, "tabs_05_back_to_projects", "Back to Projects")

            print("\n✅ Tab navigation tests completed!")
            return True

        except Exception as e:
            print(f"\n❌ Error: {e}")
            take_screenshot(page, "tabs_error", "Error state")
            return False
        finally:
            input("\nPress Enter to close browser...")
            browser.close()


if __name__ == "__main__":
    success = test_tabs_navigation()
    sys.exit(0 if success else 1)
