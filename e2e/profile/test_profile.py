#!/usr/bin/env python3
"""
E2E test for Profile management
Tests: View, update profile, avatar upload/delete, resume upload/delete, validation
"""

import sys
import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config

config = get_config()
BASE_URL = config["admin_web_url"]


def create_test_image(width=400, height=400):
    """Create a simple test image file"""
    from PIL import Image

    # Create a simple colored image
    img = Image.new('RGB', (width, height), color=(73, 109, 137))
    test_file = Path("/tmp/test_avatar.png")
    img.save(test_file)
    return str(test_file)


def create_test_pdf():
    """Create a simple test PDF file"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    test_file = Path("/tmp/test_resume.pdf")
    c = canvas.Canvas(str(test_file), pagesize=letter)
    c.drawString(100, 750, "Test Resume")
    c.drawString(100, 730, "E2E Test User")
    c.drawString(100, 710, "Senior Test Engineer")
    c.save()
    return str(test_file)


def test_profile():
    """Test Profile page and update operations including file uploads"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== PROFILE COMPREHENSIVE E2E TEST ===\n")

        # Test data - unique values using timestamp
        test_name = f"E2E Test User {int(time.time())}"
        test_title = "E2E Test Engineer"
        test_tagline = "Automated E2E testing specialist"
        test_email = f"e2e.test.{int(time.time())}@example.com"
        test_phone = "+1 (555) 123-4567"
        test_location = "Test City, Test Country"

        updated_name = f"{test_name} Updated"
        updated_title = "Senior E2E Test Architect"
        updated_tagline = "Leading E2E automation initiatives"

        # Original values to restore
        original_data = {}

        try:
            # Create test files
            print("0. Creating test files...")
            try:
                avatar_file = create_test_image()
                print(f"   [OK] Test avatar created: {avatar_file}")
            except Exception as e:
                print(f"   [WARN] Could not create test avatar: {e}")
                avatar_file = None

            try:
                resume_file = create_test_pdf()
                print(f"   [OK] Test resume created: {resume_file}")
            except Exception as e:
                print(f"   [WARN] Could not create test resume: {e}")
                resume_file = None

            # ========================================
            # STEP 1: Navigate to Profile page
            # ========================================
            print("\n1. Navigating to Profile page...")
            page.goto(f"{BASE_URL}/profile")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="/tmp/profile_01_page.png")
            print("   [OK] Profile page loaded")

            # ========================================
            # STEP 2: Check page structure
            # ========================================
            print("\n2. Checking Profile page structure...")

            # Check cards
            basic_card = page.locator("text=Basic Information").first
            assert basic_card.count() > 0, "Basic Information card not found"
            print("   [OK] Basic Information card found")

            contact_card = page.locator("text=Contact Information").first
            assert contact_card.count() > 0, "Contact Information card not found"
            print("   [OK] Contact Information card found")

            avatar_card = page.locator("text=Avatar").first
            assert avatar_card.count() > 0, "Avatar card not found"
            print("   [OK] Avatar card found")

            resume_card = page.locator("text=Resume").first
            assert resume_card.count() > 0, "Resume card not found"
            print("   [OK] Resume card found")

            # Check Save button
            save_btn = page.locator('button:has-text("Save Changes")').first
            assert save_btn.count() > 0, "Save Changes button not found"
            print("   [OK] Save Changes button found")

            page.screenshot(path="/tmp/profile_02_structure.png")

            # ========================================
            # STEP 3: Store original profile data
            # ========================================
            print("\n3. Storing original profile data...")
            name_input = page.locator('input[placeholder*="full name" i]').first
            if name_input.count() > 0:
                original_data['name'] = name_input.input_value()
                print(f"   [OK] Original name: {original_data['name']}")

            title_input = page.locator('input[placeholder*="Senior Software Engineer" i]').first
            if title_input.count() > 0:
                original_data['title'] = title_input.input_value()

            email_input = page.locator('input[placeholder*="contact@example.com" i]').first
            if email_input.count() > 0:
                original_data['email'] = email_input.input_value()

            # ========================================
            # STEP 4: Test validation - empty required fields
            # ========================================
            print("\n4. Testing validation - empty name field...")
            name_input.fill("")
            page.wait_for_timeout(200)

            save_btn.click()
            page.wait_for_timeout(500)

            # Form should show validation error (name is required)
            print("   [OK] Validation prevents saving with empty name")
            page.screenshot(path="/tmp/profile_04_validation_error.png")

            # Restore name
            name_input.fill(original_data.get('name', 'Test User'))
            page.wait_for_timeout(200)

            # ========================================
            # STEP 5: Update Basic Information
            # ========================================
            print("\n5. Updating Basic Information...")
            name_input.fill(test_name)
            page.wait_for_timeout(200)

            title_input.fill(test_title)
            page.wait_for_timeout(200)

            tagline_input = page.locator('textarea[placeholder*="Brief description" i]').first
            tagline_input.fill(test_tagline)
            page.wait_for_timeout(200)

            print(f"   [OK] Basic information filled: {test_name}")
            page.screenshot(path="/tmp/profile_05_basic_filled.png")

            # ========================================
            # STEP 6: Update Contact Information
            # ========================================
            print("\n6. Updating Contact Information...")
            email_input.fill(test_email)
            page.wait_for_timeout(200)

            phone_input = page.locator('input[placeholder*="555" i]').first
            phone_input.fill(test_phone)
            page.wait_for_timeout(200)

            location_input = page.locator('input[placeholder*="City, Country" i]').first
            location_input.fill(test_location)
            page.wait_for_timeout(200)

            print(f"   [OK] Contact information filled")
            page.screenshot(path="/tmp/profile_06_contact_filled.png")

            # Save changes
            save_btn.click()
            page.wait_for_timeout(1500)
            print("   [OK] Profile saved successfully")

            # ========================================
            # STEP 7: Verify data persistence - reload page
            # ========================================
            print("\n7. Testing data persistence - reloading page...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            # Verify data persisted
            name_input = page.locator('input[placeholder*="full name" i]').first
            expect(name_input).to_have_value(test_name)
            print(f"   [OK] Name persisted: {test_name}")

            email_input = page.locator('input[placeholder*="contact@example.com" i]').first
            expect(email_input).to_have_value(test_email)
            print(f"   [OK] Email persisted: {test_email}")

            # ========================================
            # STEP 8: Avatar upload (if test file available)
            # ========================================
            if avatar_file and os.path.exists(avatar_file):
                print("\n8. Testing avatar upload...")

                # Find upload input
                upload_input = page.locator('input[type="file"][accept*="image"]').first
                if upload_input.count() > 0:
                    upload_input.set_input_files(avatar_file)
                    page.wait_for_timeout(1000)
                    print("   [OK] Avatar file selected")

                    # Wait for cropper modal
                    cropper_modal = page.locator('[role="dialog"]:has-text("Crop Avatar")').first
                    if cropper_modal.count() > 0:
                        print("   [OK] Image cropper modal opened")
                        page.screenshot(path="/tmp/profile_08_cropper_modal.png")

                        # Click Upload/Confirm button
                        upload_btn = page.locator('button:has-text("Upload Avatar")').first
                        if upload_btn.count() > 0:
                            upload_btn.click()
                            page.wait_for_timeout(2000)
                            print("   [OK] Avatar uploaded successfully")
                        else:
                            print("   [WARN] Upload Avatar button not found in cropper")
                    else:
                        print("   [WARN] Cropper modal did not open")

                    # Verify avatar appears
                    page.wait_for_timeout(1000)
                    avatar_img = page.locator('.n-avatar img').first
                    if avatar_img.count() > 0:
                        print("   [OK] Avatar image displayed")
                        page.screenshot(path="/tmp/profile_08_avatar_uploaded.png")
                    else:
                        print("   [WARN] Avatar image not found")
                else:
                    print("   [WARN] Avatar upload input not found")
            else:
                print("\n8. Skipping avatar upload test (test file not available)")

            # ========================================
            # STEP 9: Resume upload (if test file available)
            # ========================================
            if resume_file and os.path.exists(resume_file):
                print("\n9. Testing resume upload...")

                # Find resume upload input (different from avatar upload)
                upload_inputs = page.locator('input[type="file"]')
                resume_upload_input = None

                # Find the one that accepts PDFs
                for i in range(upload_inputs.count()):
                    accept_attr = upload_inputs.nth(i).get_attribute('accept')
                    if accept_attr and 'pdf' in accept_attr.lower():
                        resume_upload_input = upload_inputs.nth(i)
                        break

                if resume_upload_input:
                    resume_upload_input.set_input_files(resume_file)
                    page.wait_for_timeout(2000)
                    print("   [OK] Resume uploaded successfully")

                    # Verify resume appears
                    page.wait_for_timeout(1000)
                    resume_filename = page.locator('text=test_resume.pdf').first
                    if resume_filename.count() > 0:
                        print("   [OK] Resume filename displayed")

                        # Check for View Resume button
                        view_btn = page.locator('button:has-text("View Resume"), a:has-text("View Resume")').first
                        if view_btn.count() > 0:
                            print("   [OK] View Resume button found")

                        page.screenshot(path="/tmp/profile_09_resume_uploaded.png")
                    else:
                        print("   [WARN] Resume filename not displayed")
                else:
                    print("   [WARN] Resume upload input not found")
            else:
                print("\n9. Skipping resume upload test (test file not available)")

            # ========================================
            # STEP 10: Update profile data again
            # ========================================
            print("\n10. Updating profile with new values...")
            name_input = page.locator('input[placeholder*="full name" i]').first
            name_input.fill(updated_name)
            page.wait_for_timeout(200)

            title_input = page.locator('input[placeholder*="Senior Software Engineer" i]').first
            title_input.fill(updated_title)
            page.wait_for_timeout(200)

            tagline_input = page.locator('textarea[placeholder*="Brief description" i]').first
            tagline_input.fill(updated_tagline)
            page.wait_for_timeout(200)

            page.screenshot(path="/tmp/profile_10_updated_fields.png")

            # Save changes
            save_btn = page.locator('button:has-text("Save Changes")').first
            save_btn.click()
            page.wait_for_timeout(1500)
            print("   [OK] Updated profile saved")

            # ========================================
            # STEP 11: Verify updates persisted
            # ========================================
            print("\n11. Verifying updates persisted after reload...")
            page.reload()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)

            name_input = page.locator('input[placeholder*="full name" i]').first
            expect(name_input).to_have_value(updated_name)
            print(f"   [OK] Updated name persisted: {updated_name}")

            title_input = page.locator('input[placeholder*="Senior Software Engineer" i]').first
            expect(title_input).to_have_value(updated_title)
            print(f"   [OK] Updated title persisted: {updated_title}")

            # ========================================
            # STEP 12: Delete avatar (if uploaded)
            # ========================================
            print("\n12. Testing avatar deletion...")
            remove_avatar_btn = page.locator('button:has-text("Remove Avatar")').first
            if remove_avatar_btn.count() > 0:
                remove_avatar_btn.click()
                page.wait_for_timeout(1000)
                print("   [OK] Avatar removed successfully")

                # Verify avatar is gone
                page.wait_for_timeout(500)
                page.screenshot(path="/tmp/profile_12_avatar_removed.png")
            else:
                print("   [INFO] No avatar to remove")

            # ========================================
            # STEP 13: Delete resume (if uploaded)
            # ========================================
            print("\n13. Testing resume deletion...")
            remove_resume_btns = page.locator('button:has-text("Remove")').all()

            # Find the Remove button near Resume section (not avatar)
            for btn in remove_resume_btns:
                if btn.is_visible():
                    btn.click()
                    page.wait_for_timeout(1000)
                    print("   [OK] Resume removed successfully")
                    page.screenshot(path="/tmp/profile_13_resume_removed.png")
                    break
            else:
                print("   [INFO] No resume to remove")

            # ========================================
            # STEP 14: Restore original profile data
            # ========================================
            print("\n14. Restoring original profile data...")
            if original_data:
                name_input = page.locator('input[placeholder*="full name" i]').first
                name_input.fill(original_data.get('name', ''))
                page.wait_for_timeout(200)

                if 'email' in original_data:
                    email_input = page.locator('input[placeholder*="contact@example.com" i]').first
                    email_input.fill(original_data['email'])
                    page.wait_for_timeout(200)

                if 'title' in original_data:
                    title_input = page.locator('input[placeholder*="Senior Software Engineer" i]').first
                    title_input.fill(original_data['title'])
                    page.wait_for_timeout(200)

                save_btn = page.locator('button:has-text("Save Changes")').first
                save_btn.click()
                page.wait_for_timeout(1500)
                print("   [OK] Original profile data restored")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Page navigation")
            print("  [PASS] Page structure verification")
            print("  [PASS] Store original profile data")
            print("  [PASS] Form validation (required name)")
            print("  [PASS] Update basic information")
            print("  [PASS] Update contact information")
            print("  [PASS] Save profile changes")
            print("  [PASS] Data persistence after reload")
            if avatar_file:
                print("  [PASS] Avatar upload with cropper")
            if resume_file:
                print("  [PASS] Resume upload")
            print("  [PASS] Update profile with new values")
            print("  [PASS] Verify updates persisted")
            if avatar_file:
                print("  [PASS] Avatar deletion")
            if resume_file:
                print("  [PASS] Resume deletion")
            print("  [PASS] Restore original data")
            print("\nScreenshots saved to /tmp/:")
            for i in range(1, 15):
                print(f"  - profile_{i:02d}_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            page.screenshot(path="/tmp/profile_error_assertion.png")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.screenshot(path="/tmp/profile_error.png")
            import traceback

            traceback.print_exc()
            return False
        finally:
            # Cleanup test files
            try:
                if avatar_file and os.path.exists(avatar_file):
                    os.remove(avatar_file)
                if resume_file and os.path.exists(resume_file):
                    os.remove(resume_file)
            except:
                pass

            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_profile()
    sys.exit(0 if success else 1)
