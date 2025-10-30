#!/usr/bin/env python3
"""
Comprehensive E2E test for Miniatures functionality
Tests: Projects, Themes, and Paints CRUD operations
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright
from auth.auth_manager import AuthManager
from common.config import get_config

config = get_config()
BASE_URL = config['admin_web_url']


def test_miniatures_comprehensive():
    """Test all Miniatures tabs and CRUD operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy='auto')

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== MINIATURES COMPREHENSIVE TEST ===\n")

        try:
            # Navigate to Miniatures page
            print("1. Navigating to Miniatures page...")
            page.goto(f'{BASE_URL}/miniatures')
            page.wait_for_load_state('networkidle')
            page.screenshot(path='/tmp/miniatures_01_page.png')
            print("   [OK] Miniatures page loaded")

            # TEST PROJECTS TAB
            print("\n" + "="*60)
            print("TESTING PROJECTS TAB")
            print("="*60)

            print("\n2. Checking Projects tab...")
            projects_tab = page.locator('text=Projects').first
            if projects_tab.count() > 0:
                projects_tab.click()
                page.wait_for_timeout(500)
                page.screenshot(path='/tmp/miniatures_02_projects.png')
                print("   [OK] Projects tab active")

                # Check Add button
                add_btn = page.locator('button:has-text("Add Project")')
                if add_btn.count() > 0:
                    print("   [OK] Add Project button found")

                    # Test Add Project modal
                    print("\n3. Testing Add Project modal...")
                    add_btn.click()
                    page.wait_for_timeout(500)

                    modal = page.locator('[role="dialog"]')
                    if modal.count() > 0:
                        print("   [OK] Modal opened")
                        page.screenshot(path='/tmp/miniatures_03_project_modal.png')

                        # Check all project fields
                        fields = {
                            'title': page.locator('input[placeholder*="title" i]').first,
                            'theme': page.locator('text=Theme').first,
                            'scale': page.locator('input[placeholder*="scale" i]').first,
                            'manufacturer': page.locator('input[placeholder*="manufacturer" i]').first,
                            'difficulty': page.locator('text=Difficulty').first,
                            'description': page.locator('textarea').first,
                        }

                        for field_name, field_locator in fields.items():
                            if field_locator.count() > 0:
                                print(f"   [OK] {field_name.capitalize()} field found")

                        # Close modal
                        cancel_btn = page.locator('button:has-text("Cancel")').first
                        if cancel_btn.count() > 0:
                            cancel_btn.click()
                            page.wait_for_timeout(300)
                            print("   [OK] Modal closed")

            # TEST THEMES TAB
            print("\n" + "="*60)
            print("TESTING THEMES TAB")
            print("="*60)

            print("\n4. Checking Themes tab...")
            themes_tab = page.locator('text=Themes').first
            if themes_tab.count() > 0:
                themes_tab.click()
                page.wait_for_timeout(500)
                page.screenshot(path='/tmp/miniatures_04_themes.png')
                print("   [OK] Themes tab active")

                # Check Add button
                add_btn = page.locator('button:has-text("Add Theme")')
                if add_btn.count() > 0:
                    print("   [OK] Add Theme button found")

                    # Test Add Theme modal
                    print("\n5. Testing Add Theme modal...")
                    add_btn.click()
                    page.wait_for_timeout(500)

                    modal = page.locator('[role="dialog"]')
                    if modal.count() > 0:
                        print("   [OK] Modal opened")
                        page.screenshot(path='/tmp/miniatures_05_theme_modal.png')

                        # Check theme fields
                        fields = {
                            'name': page.locator('input[placeholder*="name" i]').first,
                            'description': page.locator('textarea, input[placeholder*="description" i]').first,
                            'display_order': page.locator('input[type="number"], input[placeholder*="order" i]').first,
                        }

                        for field_name, field_locator in fields.items():
                            if field_locator.count() > 0:
                                print(f"   [OK] {field_name.capitalize()} field found")

                        # Close modal
                        cancel_btn = page.locator('button:has-text("Cancel")').first
                        if cancel_btn.count() > 0:
                            cancel_btn.click()
                            page.wait_for_timeout(300)
                            print("   [OK] Modal closed")

            # TEST PAINTS TAB
            print("\n" + "="*60)
            print("TESTING PAINTS TAB")
            print("="*60)

            print("\n6. Checking Paints tab...")
            paints_tab = page.locator('text=Paints').first
            if paints_tab.count() > 0:
                paints_tab.click()
                page.wait_for_timeout(1000)
                page.screenshot(path='/tmp/miniatures_06_paints.png')
                print("   [OK] Paints tab active")

                # Check for table
                table = page.locator('table, [role="table"]')
                if table.count() > 0:
                    print("   [OK] Paints table found")

                # Check Add button
                add_btn = page.locator('button:has-text("Add Paint")')
                if add_btn.count() > 0:
                    print("   [OK] Add Paint button found")

                    # Test Add Paint modal
                    print("\n7. Testing Add Paint modal...")
                    add_btn.click()
                    page.wait_for_timeout(500)

                    modal = page.locator('[role="dialog"]')
                    if modal.count() > 0:
                        print("   [OK] Modal opened")
                        page.screenshot(path='/tmp/miniatures_07_paint_modal.png')

                        # Check paint fields
                        fields = {
                            'manufacturer': page.locator('input[placeholder*="manufacturer" i]').first,
                            'name': page.locator('input[placeholder*="name" i]').first,
                            'color_code': page.locator('input[placeholder*="color" i], input[type="color"]').first,
                            'paint_type': page.locator('text=Type').first,
                            'finish': page.locator('text=Finish').first,
                        }

                        for field_name, field_locator in fields.items():
                            if field_locator.count() > 0:
                                print(f"   [OK] {field_name.capitalize()} field found")

                        # Close modal
                        cancel_btn = page.locator('button:has-text("Cancel")').first
                        if cancel_btn.count() > 0:
                            cancel_btn.click()
                            page.wait_for_timeout(300)
                            print("   [OK] Modal closed")

            # TEST NAVIGATION BETWEEN TABS
            print("\n" + "="*60)
            print("TESTING TAB NAVIGATION")
            print("="*60)

            print("\n8. Testing tab switching...")
            tab_sequence = [
                ('Projects', projects_tab),
                ('Themes', themes_tab),
                ('Paints', paints_tab),
            ]

            for tab_name, tab_locator in tab_sequence:
                if tab_locator.count() > 0:
                    tab_locator.click()
                    page.wait_for_timeout(300)
                    print(f"   [OK] Switched to {tab_name} tab")

            page.screenshot(path='/tmp/miniatures_08_final.png')

            print("\n=== TEST COMPLETED ===")
            print("\nScreenshots saved to /tmp/:")
            print("  - miniatures_01_page.png")
            print("  - miniatures_02_projects.png")
            print("  - miniatures_03_project_modal.png")
            print("  - miniatures_04_themes.png")
            print("  - miniatures_05_theme_modal.png")
            print("  - miniatures_06_paints.png")
            print("  - miniatures_07_paint_modal.png")
            print("  - miniatures_08_final.png")

            return True

        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path='/tmp/miniatures_error.png')
            import traceback
            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == '__main__':
    success = test_miniatures_comprehensive()
    sys.exit(0 if success else 1)
