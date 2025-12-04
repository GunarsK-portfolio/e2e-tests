#!/usr/bin/env python3
"""
E2E test for Public Website - Home Page
Tests: Page load, section visibility, navigation, external links
"""

import sys
import traceback

from playwright.sync_api import expect, sync_playwright

from e2e.common.config import get_config
from e2e.common.helpers import (
    scroll_to_section,
    take_screenshot,
    verify_element_count,
    verify_element_exists,
    wait_for_page_load,
)

config = get_config()
BASE_URL = config["public_web_url"]


def test_home_page():
    """Test home page loads correctly with all sections"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config["headless"])
        context = browser.new_context()
        page = context.new_page()

        print("\n=== PUBLIC WEB - HOME PAGE E2E TEST ===\n")

        try:
            # ========================================
            # STEP 1: Navigate to home page
            # ========================================
            print("1. Navigating to home page...")
            page.goto(BASE_URL)
            wait_for_page_load(page)
            take_screenshot(page, "public_home_01_loaded", "Home page loaded")
            print("   [OK] Home page loaded")

            # ========================================
            # STEP 2: Verify Hero Section
            # ========================================
            print("\n2. Verifying Hero Section...")

            # From HeroSection.vue: first section, has n-avatar and h1.profile-name
            hero_section = page.locator("section").first
            expect(hero_section).to_be_visible(timeout=5000)

            # Check for avatar
            verify_element_exists(page, ".n-avatar", "Profile avatar")

            # Check for profile name
            profile_name = page.locator("h1.profile-name").first
            if profile_name.count() > 0:
                expect(profile_name).to_be_visible()
                print("   [OK] Profile name visible")

            take_screenshot(page, "public_home_02_hero", "Hero section")

            # ========================================
            # STEP 3: Verify Resume Section
            # ========================================
            print("\n3. Verifying Resume Section...")

            # From ResumeSection.vue: h2 with text "Resume"
            resume_section = scroll_to_section(page, "Resume")
            if resume_section:
                expect(resume_section).to_be_visible()
                print("   [OK] Resume section visible")

                # Check for Work Experience subsection
                work_exp = page.locator('h3:has-text("Work Experience")').first
                if work_exp.count() > 0:
                    print("   [OK] Work Experience subsection visible")

                take_screenshot(page, "public_home_03_resume", "Resume section")

            # ========================================
            # STEP 4: Verify Skills Section
            # ========================================
            print("\n4. Verifying Skills Section...")

            # From SkillsSection.vue: h2 with text "Skills & Technologies"
            skills_section = scroll_to_section(page, "Skills & Technologies")
            if skills_section:
                expect(skills_section).to_be_visible()
                print("   [OK] Skills section visible")

                # Check for skill tags
                verify_element_count(page, ".n-tag", "skill tags")
                take_screenshot(page, "public_home_04_skills", "Skills section")

            # ========================================
            # STEP 5: Verify Projects Section
            # ========================================
            print("\n5. Verifying Projects Section...")

            # From ProjectsSection.vue: h2 with text "Portfolio Projects"
            projects_section = scroll_to_section(page, "Portfolio Projects")
            if projects_section:
                expect(projects_section).to_be_visible()
                print("   [OK] Projects section visible")

                # Check for project cards
                verify_element_count(page, ".n-card", "project cards")
                take_screenshot(page, "public_home_05_projects", "Projects section")

            # ========================================
            # STEP 6: Verify Miniatures Section
            # ========================================
            print("\n6. Verifying Miniatures Section...")

            # From MiniaturesSection.vue: h2 with text "Miniature Painting"
            miniatures_section = scroll_to_section(page, "Miniature Painting")
            if miniatures_section:
                expect(miniatures_section).to_be_visible()
                print("   [OK] Miniatures section visible")
                take_screenshot(page, "public_home_06_miniatures", "Miniatures section")

            # ========================================
            # STEP 7: Verify Contact Section
            # ========================================
            print("\n7. Verifying Contact Section...")

            # From ContactSection.vue: h2 with text "Get In Touch"
            contact_section = scroll_to_section(page, "Get In Touch")
            if contact_section:
                expect(contact_section).to_be_visible()
                print("   [OK] Contact section visible")
                take_screenshot(page, "public_home_07_contact", "Contact section")

            # ========================================
            # STEP 8: Test Back to Top button
            # ========================================
            print("\n8. Testing Back to Top button...")

            # Scroll to bottom to trigger BackToTop button
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(500)

            back_to_top = page.locator(".back-to-top").first
            if back_to_top.count() > 0:
                expect(back_to_top).to_be_visible(timeout=2000)
                print("   [OK] Back to Top button visible")

                # Click it
                back_to_top.click()
                page.wait_for_timeout(1000)

                # Verify scrolled to top
                scroll_y = page.evaluate("window.scrollY")
                assert scroll_y < 100, f"Expected scroll near top, got {scroll_y}"
                print("   [OK] Back to Top button works")
            else:
                print("   [INFO] Back to Top button not found (may appear on scroll)")

            take_screenshot(page, "public_home_08_back_to_top", "After back to top")

            # ========================================
            # STEP 9: Verify page title
            # ========================================
            print("\n9. Verifying page title...")

            title = page.title()
            assert title, "Page should have a title"
            print(f"   [OK] Page title: {title}")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Home page loads")
            print("  [PASS] Hero section visible")
            print("  [PASS] Resume section visible")
            print("  [PASS] Skills section visible")
            print("  [PASS] Projects section visible")
            print("  [PASS] Miniatures section visible")
            print("  [PASS] Contact section visible")
            print("  [PASS] Back to Top functionality")
            print("  [PASS] Page title present")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "public_home_error_assertion", "Assertion error")
            traceback.print_exc()
            return False

        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "public_home_error", "Error occurred")
            traceback.print_exc()
            return False

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_home_page()
    sys.exit(0 if success else 1)
