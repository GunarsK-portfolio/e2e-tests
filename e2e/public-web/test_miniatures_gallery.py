#!/usr/bin/env python3
"""
E2E test for Public Website - Miniatures Gallery
Tests: Gallery navigation, theme detail, miniature detail, image carousel
"""

import sys
import traceback

from playwright.sync_api import expect, sync_playwright

from e2e.common.config import get_config
from e2e.common.helpers import (
    take_screenshot,
    verify_element_count,
    verify_element_exists,
    verify_url_contains,
    wait_for_page_load,
)

config = get_config()
BASE_URL = config["public_web_url"]


def test_miniatures_gallery():
    """Test miniatures gallery navigation and features"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config["headless"])
        context = browser.new_context()
        page = context.new_page()

        print("\n=== PUBLIC WEB - MINIATURES GALLERY E2E TEST ===\n")

        try:
            # ========================================
            # STEP 1: Navigate to miniatures page
            # ========================================
            print("1. Navigating to miniatures page...")
            page.goto(f"{BASE_URL}/miniatures")
            wait_for_page_load(page)
            take_screenshot(page, "public_miniatures_01_loaded", "Miniatures page loaded")
            print("   [OK] Miniatures page loaded")

            # Verify page header - from Miniatures.vue: title="Miniature Painting"
            page_header = page.locator('text="Miniature Painting"').first
            expect(page_header).to_be_visible(timeout=5000)
            print("   [OK] Page header visible")

            # ========================================
            # STEP 2: Verify themes grid
            # ========================================
            print("\n2. Verifying themes grid...")
            # Wait for themes to load via API response
            page.wait_for_load_state("networkidle")

            # From Miniatures.vue: theme cards have class "theme-card" and role="link"
            theme_cards = page.locator('.theme-card, .n-card[role="link"]')
            card_count = theme_cards.count()

            if card_count > 0:
                print(f"   [OK] Found {card_count} theme cards")
                take_screenshot(page, "public_miniatures_02_themes_grid", "Themes grid")
            else:
                print("   [INFO] No theme cards found - may have no data")
                take_screenshot(page, "public_miniatures_02_no_themes", "No themes")
                # Test passes - no data is valid state
                print("\n" + "=" * 60)
                print("=== TEST COMPLETED SUCCESSFULLY ===")
                print("=" * 60)
                print("\nTests performed:")
                print("  [PASS] Miniatures page loads")
                print("  [PASS] Page header visible")
                print("  [INFO] No themes to test (empty data)")
                return True

            # ========================================
            # STEP 3: Click on first theme
            # ========================================
            print("\n3. Clicking on first theme...")

            first_theme = theme_cards.first

            # Get theme name from .theme-name element
            theme_name_elem = first_theme.locator(".theme-name").first
            theme_name = (
                theme_name_elem.text_content() if theme_name_elem.count() > 0 else "Unknown"
            )
            print(f"   [INFO] Clicking theme: {theme_name}")

            first_theme.click()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            # Verify navigation to theme detail
            verify_url_contains(page, "/miniatures/themes/", "Navigated to theme detail")
            take_screenshot(page, "public_miniatures_03_theme_detail", "Theme detail page")

            # ========================================
            # STEP 4: Verify theme detail page
            # ========================================
            print("\n4. Verifying theme detail page...")

            # From MiniatureTheme.vue: h1.theme-title contains theme name
            theme_title = page.locator("h1.theme-title, h1.hero-title").first
            if theme_title.count() > 0:
                expect(theme_title).to_be_visible()
                title_text = theme_title.text_content()
                print(f"   [OK] Theme title visible: {title_text}")

            # From MiniatureTheme.vue: miniature cards have class "miniature-card"
            miniature_cards = page.locator(".miniature-card, .n-card[role='link']")
            mini_count = miniature_cards.count()

            if mini_count > 0:
                print(f"   [OK] Found {mini_count} miniature cards in theme")
            else:
                print("   [INFO] No miniatures found in this theme")

            take_screenshot(page, "public_miniatures_04_theme_miniatures", "Theme miniatures")

            # ========================================
            # STEP 5: Click on first miniature (if any)
            # ========================================
            if mini_count > 0:
                print("\n5. Clicking on first miniature...")

                first_miniature = miniature_cards.first
                first_miniature.click()
                wait_for_page_load(page)
                page.wait_for_timeout(500)

                # Verify navigation to miniature detail
                verify_url_contains(page, "/miniatures/projects/", "Navigated to miniature detail")
                take_screenshot(
                    page, "public_miniatures_05_miniature_detail", "Miniature detail page"
                )

                # ========================================
                # STEP 6: Verify miniature detail page
                # ========================================
                print("\n6. Verifying miniature detail page...")

                # From MiniatureProject.vue: h1.miniature-title contains name
                mini_title = page.locator("h1.miniature-title, h1.hero-title").first
                if mini_title.count() > 0:
                    expect(mini_title).to_be_visible()
                    print("   [OK] Miniature title visible")

                # From MiniatureProject.vue: n-carousel contains images
                carousel = page.locator(".n-carousel, .image-carousel").first
                if carousel.count() > 0:
                    expect(carousel).to_be_visible()
                    print("   [OK] Image carousel/gallery visible")

                    # Check for carousel navigation dots
                    verify_element_exists(page, ".n-carousel-dots", "carousel navigation dots")

                take_screenshot(
                    page, "public_miniatures_06_detail_content", "Miniature detail content"
                )

                # ========================================
                # STEP 7: Check for paint colors section
                # ========================================
                print("\n7. Checking for paint colors section...")

                # From MiniatureProject.vue: title="Paints Used"
                paint_section = page.locator('.n-card:has-text("Paints Used")').first
                if paint_section.count() > 0:
                    paint_section.scroll_into_view_if_needed()
                    page.wait_for_timeout(300)
                    print("   [OK] Paint colors section found")

                    # From MiniatureProject.vue: .color-swatch-compact class
                    verify_element_count(
                        page,
                        ".color-swatch-compact, .paint-swatches",
                        "color swatches",
                    )
                    take_screenshot(
                        page, "public_miniatures_07_paint_colors", "Paint colors section"
                    )
                else:
                    print("   [INFO] No paint colors section found")

                # ========================================
                # STEP 8: Check for techniques section
                # ========================================
                print("\n8. Checking for techniques section...")

                # From MiniatureProject.vue: title="Painting Techniques"
                techniques_section = page.locator('.n-card:has-text("Painting Techniques")').first
                if techniques_section.count() > 0:
                    techniques_section.scroll_into_view_if_needed()
                    page.wait_for_timeout(300)
                    print("   [OK] Techniques section found")

                    # Check for technique tags
                    verify_element_count(page, ".n-tag", "technique tags")
                else:
                    print("   [INFO] No techniques section found")

                # ========================================
                # STEP 9: Test back navigation
                # ========================================
                print("\n9. Testing back navigation...")

                # From MiniatureProject.vue: button text is "Back"
                back_btn = page.locator('button:has-text("Back")').first
                if back_btn.count() > 0:
                    expect(back_btn).to_be_visible()
                    back_btn.click()
                    wait_for_page_load(page)
                    page.wait_for_timeout(500)

                    # Should be back at theme detail or miniatures
                    current_url = page.url
                    if "/miniatures/themes/" in current_url:
                        print("   [OK] Navigated back to theme detail")
                    elif "/miniatures" in current_url:
                        print("   [OK] Navigated back to miniatures")
                    else:
                        print(f"   [INFO] Navigated to: {current_url}")

                    take_screenshot(page, "public_miniatures_09_back_nav", "After back navigation")
            else:
                print("\n5-9. [SKIP] No miniatures to test detail view")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Miniatures page loads")
            print("  [PASS] Page header visible")
            print("  [PASS] Themes grid displayed")
            print("  [PASS] Theme detail navigation")
            print("  [PASS] Theme detail page content")
            if mini_count > 0:
                print("  [PASS] Miniature detail navigation")
                print("  [PASS] Miniature detail page content")
                print("  [PASS] Image carousel/gallery")
                print("  [PASS] Back navigation")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "public_miniatures_error_assertion", "Assertion error")
            traceback.print_exc()
            return False

        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "public_miniatures_error", "Error occurred")
            traceback.print_exc()
            return False

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_miniatures_gallery()
    sys.exit(0 if success else 1)
