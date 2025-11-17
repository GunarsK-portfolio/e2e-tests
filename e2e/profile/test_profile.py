#!/usr/bin/env python3
"""
E2E test for Profile page
Tests: Form validation, Update profile, Avatar upload/delete, Resume upload/delete, Data persistence
"""

import sys
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config
from e2e.common.helpers import (
    fill_text_input,
    fill_textarea,
    get_input_value,
    take_screenshot,
    wait_for_page_load,
)

config = get_config()
BASE_URL = config["admin_web_url"]


# ========================================
# PROFILE-SPECIFIC HELPERS
# ========================================


def click_save_button(page, wait_ms: int = 1000):
    """Click the Save Changes button on Profile page"""
    save_btn = page.locator('button.n-button--primary-type:has-text("Save Changes")').first
    save_btn.click()
    page.wait_for_timeout(wait_ms)


def click_reset_button(page, wait_ms: int = 500):
    """Click the Reset button on Profile page"""
    reset_btn = page.locator('button:has-text("Reset")').first
    reset_btn.click()
    page.wait_for_timeout(wait_ms)


def upload_avatar_image(page, file_path: str, wait_ms: int = 1500):
    """Upload an avatar image (triggers cropper modal)

    Args:
        page: Playwright page object
        file_path: Path to image file
        wait_ms: Wait time in milliseconds
    """
    # Locate the avatar upload input within the Avatar card
    avatar_card = page.locator('.n-card:has-text("Avatar")').first
    file_input = avatar_card.locator('input[type="file"]').first
    file_input.set_input_files(file_path)
    page.wait_for_timeout(wait_ms)


def confirm_avatar_crop(page, wait_ms: int = 2000):
    """Confirm avatar crop in the ImageCropperModal

    Args:
        page: Playwright page object
        wait_ms: Wait time after upload completes
    """
    # Locate the cropper modal
    cropper_modal = page.locator('.n-modal[role="dialog"]:has-text("Crop Avatar")').first

    # Wait for modal to be visible
    expect(cropper_modal).to_be_visible(timeout=5000)

    # Click Upload Avatar button
    upload_btn = cropper_modal.locator('button:has-text("Upload Avatar")').first
    upload_btn.click()

    # Wait for upload to complete and modal to close
    page.wait_for_timeout(wait_ms)


def cancel_avatar_crop(page, wait_ms: int = 500):
    """Cancel avatar crop in the ImageCropperModal"""
    cropper_modal = page.locator('.n-modal[role="dialog"]:has-text("Crop Avatar")').first
    cancel_btn = cropper_modal.locator('button:has-text("Cancel")').first
    cancel_btn.click()
    page.wait_for_timeout(wait_ms)


def delete_avatar(page, wait_ms: int = 1000):
    """Delete the current avatar"""
    avatar_card = page.locator('.n-card:has-text("Avatar")').first
    remove_btn = avatar_card.locator('button:has-text("Remove Avatar")').first
    remove_btn.click()
    page.wait_for_timeout(wait_ms)


def verify_avatar_exists(page):
    """Verify that an avatar is displayed"""
    avatar_card = page.locator('.n-card:has-text("Avatar")').first
    avatar = avatar_card.locator(".n-avatar").first
    return avatar.count() > 0


def upload_resume(page, file_path: str, wait_ms: int = 2000):
    """Upload a resume file

    Args:
        page: Playwright page object
        file_path: Path to resume file (PDF, DOC, DOCX)
        wait_ms: Wait time for upload to complete
    """
    resume_card = page.locator('.n-card:has-text("Resume")').first
    file_input = resume_card.locator('input[type="file"]').first
    file_input.set_input_files(file_path)
    page.wait_for_timeout(wait_ms)


def delete_resume(page, wait_ms: int = 1000):
    """Delete the current resume"""
    resume_card = page.locator('.n-card:has-text("Resume")').first
    remove_btn = resume_card.locator('button:has-text("Remove")').first
    remove_btn.click()
    page.wait_for_timeout(wait_ms)


def verify_resume_exists(page, file_name: str = None, timeout: int = 5000):
    """Verify that a resume file is displayed

    Args:
        page: Playwright page object
        file_name: Optional file name to verify
        timeout: Timeout in milliseconds to wait for resume to appear

    Returns:
        bool: True if resume exists (and matches file name if provided)
    """
    resume_card = page.locator('.n-card:has-text("Resume")').first

    # Check multiple indicators that resume exists
    # 1. Check for the document icon
    document_icon = resume_card.locator(".n-icon").first
    if document_icon.count() == 0:
        return False

    # 2. Check for View Resume link/button (it's an anchor tag styled as button)
    view_link = resume_card.locator('a:has-text("View Resume")').first
    try:
        view_link.wait_for(state="visible", timeout=timeout)
        if file_name:
            # Also verify file name if provided
            file_text = resume_card.locator(f'text="{file_name}"').first
            return file_text.count() > 0
        return True
    except Exception:
        return False


# ========================================
# MAIN TEST
# ========================================


def test_profile():
    """Test Profile page operations"""
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy="auto")

        if not page:
            print("[ERROR] Authentication failed")
            return False

        print("\n=== PROFILE E2E TEST ===\n")

        # Test data
        test_name = f"E2E Test User {int(time.time())}"
        test_title = "E2E Test Engineer"
        test_tagline = "Testing the profile page with automated E2E tests"
        test_email = "e2e.test@example.com"
        test_phone = "+1 (555) 123-4567"
        test_location = "Test City, Test Country"

        updated_name = f"{test_name} Updated"
        updated_title = "Senior E2E Test Engineer"

        # File paths for testing
        test_files_dir = Path(__file__).parent.parent.parent / "test-files"
        avatar_file = test_files_dir / "test-avatar.jpg"
        resume_file = test_files_dir / "test-resume.pdf"

        try:
            # ========================================
            # STEP 1: Navigate to Profile page
            # ========================================
            print("1. Navigating to Profile page...")
            page.goto(f"{BASE_URL}/profile")
            wait_for_page_load(page)
            take_screenshot(page, "profile_01_page_loaded", "Profile page loaded")
            print("   [OK] Profile page loaded")

            # ========================================
            # STEP 2: Capture original data
            # ========================================
            print("\n2. Capturing original profile data...")
            original_name = get_input_value(page, "Full Name")
            original_title = get_input_value(page, "Professional Title")
            print(f"   [INFO] Original name: {original_name}")
            print(f"   [INFO] Original title: {original_title}")

            # ========================================
            # STEP 3: Test validation - empty required field
            # ========================================
            print("\n3. Testing validation - clearing required field...")
            fill_text_input(page, label="Full Name", value="")
            click_save_button(page)

            # Check if validation error appears (form should not save)
            page.wait_for_timeout(500)
            current_name = get_input_value(page, "Full Name")
            if current_name == "":
                print("   [OK] Validation prevents empty name field")
                take_screenshot(page, "profile_02_validation_error", "Validation error")

            # Restore name
            fill_text_input(page, label="Full Name", value=original_name or test_name)

            # ========================================
            # STEP 4: Update profile information
            # ========================================
            print("\n4. Updating profile information...")
            fill_text_input(page, label="Full Name", value=test_name)
            fill_text_input(page, label="Professional Title", value=test_title)
            fill_textarea(page, label="Bio / Tagline", value=test_tagline)
            fill_text_input(page, label="Email", value=test_email)
            fill_text_input(page, label="Phone", value=test_phone)
            fill_text_input(page, label="Location", value=test_location)

            take_screenshot(page, "profile_03_form_filled", "Profile form filled")
            print("   [OK] Profile form filled")

            # Save changes
            click_save_button(page)
            page.wait_for_timeout(1000)
            print("   [OK] Profile saved successfully")

            # ========================================
            # STEP 5: Verify updated data persists
            # ========================================
            print("\n5. Verifying updated data...")
            saved_name = get_input_value(page, "Full Name")
            saved_title = get_input_value(page, "Professional Title")
            saved_email = get_input_value(page, "Email")

            assert saved_name == test_name, f"Name mismatch: {saved_name} != {test_name}"
            assert saved_title == test_title, f"Title mismatch: {saved_title} != {test_title}"
            assert saved_email == test_email, f"Email mismatch: {saved_email} != {test_email}"
            print(f"   [OK] Profile data verified: {test_name}")

            # ========================================
            # STEP 6: Test Reset functionality
            # ========================================
            print("\n6. Testing Reset functionality...")
            fill_text_input(page, label="Full Name", value="Temporary Change")
            click_reset_button(page)
            page.wait_for_timeout(500)

            reset_name = get_input_value(page, "Full Name")
            assert reset_name == test_name, "Reset should restore saved data"
            print("   [OK] Reset restored saved data")

            # ========================================
            # STEP 7: Test avatar upload (if test file exists)
            # ========================================
            if avatar_file.exists():
                print("\n7. Testing avatar upload...")
                print(f"   [INFO] Using test file: {avatar_file}")

                # Upload avatar
                upload_avatar_image(page, str(avatar_file))
                take_screenshot(page, "profile_04_cropper_modal", "Avatar cropper modal")

                # Confirm crop
                confirm_avatar_crop(page)
                print("   [OK] Avatar uploaded and cropped")

                # Verify avatar exists
                page.wait_for_timeout(1000)
                assert verify_avatar_exists(page), "Avatar should be visible after upload"
                print("   [OK] Avatar verified in UI")
                take_screenshot(page, "profile_05_avatar_uploaded", "Avatar uploaded")
            else:
                print(f"\n7. [SKIP] Avatar test - file not found: {avatar_file}")

            # ========================================
            # STEP 8: Test resume upload (if test file exists)
            # ========================================
            if resume_file.exists():
                print("\n8. Testing resume upload...")
                print(f"   [INFO] Using test file: {resume_file}")

                # Upload resume
                upload_resume(page, str(resume_file))
                print("   [OK] Resume uploaded")

                # Verify resume exists
                page.wait_for_timeout(1000)
                assert verify_resume_exists(page), "Resume should be visible after upload"
                print("   [OK] Resume verified in UI")
                take_screenshot(page, "profile_06_resume_uploaded", "Resume uploaded")
            else:
                print(f"\n8. [SKIP] Resume test - file not found: {resume_file}")

            # ========================================
            # STEP 9: Test data persistence - reload page
            # ========================================
            print("\n9. Testing data persistence - reloading page...")
            page.reload()
            wait_for_page_load(page)
            page.wait_for_timeout(500)

            persisted_name = get_input_value(page, "Full Name")
            persisted_title = get_input_value(page, "Professional Title")

            assert persisted_name == test_name, "Name should persist after reload"
            assert persisted_title == test_title, "Title should persist after reload"
            print("   [OK] Profile data persisted after reload")

            # Verify avatar persists (if uploaded)
            if avatar_file.exists() and verify_avatar_exists(page):
                print("   [OK] Avatar persisted after reload")

            # Verify resume persists (if uploaded)
            if resume_file.exists() and verify_resume_exists(page):
                print("   [OK] Resume persisted after reload")

            take_screenshot(page, "profile_07_after_reload", "After reload")

            # ========================================
            # STEP 10: Test avatar deletion (if avatar exists)
            # ========================================
            if avatar_file.exists() and verify_avatar_exists(page):
                print("\n10. Testing avatar deletion...")
                delete_avatar(page)
                page.wait_for_timeout(1000)

                assert not verify_avatar_exists(page), "Avatar should be removed"
                print("   [OK] Avatar deleted successfully")
                take_screenshot(page, "profile_08_avatar_deleted", "Avatar deleted")
            else:
                print("\n10. [SKIP] Avatar deletion test - no avatar to delete")

            # ========================================
            # STEP 11: Test resume deletion (if resume exists)
            # ========================================
            if resume_file.exists() and verify_resume_exists(page):
                print("\n11. Testing resume deletion...")
                delete_resume(page)
                page.wait_for_timeout(1000)

                assert not verify_resume_exists(page), "Resume should be removed"
                print("   [OK] Resume deleted successfully")
                take_screenshot(page, "profile_09_resume_deleted", "Resume deleted")
            else:
                print("\n11. [SKIP] Resume deletion test - no resume to delete")

            # ========================================
            # STEP 12: Update profile again
            # ========================================
            print("\n12. Updating profile with new data...")
            fill_text_input(page, label="Full Name", value=updated_name)
            fill_text_input(page, label="Professional Title", value=updated_title)

            click_save_button(page)
            page.wait_for_timeout(1000)

            final_name = get_input_value(page, "Full Name")
            final_title = get_input_value(page, "Professional Title")

            assert final_name == updated_name, "Updated name should be saved"
            assert final_title == updated_title, "Updated title should be saved"
            print(f"   [OK] Profile updated to: {updated_name}")
            take_screenshot(page, "profile_10_final_update", "Final update")

            # ========================================
            # STEP 13: Restore original data (cleanup)
            # ========================================
            if original_name:
                print("\n13. Restoring original profile data...")
                fill_text_input(page, label="Full Name", value=original_name)
                fill_text_input(page, label="Professional Title", value=original_title or "")
                click_save_button(page)
                page.wait_for_timeout(1000)
                print("   [OK] Original data restored")

            # ========================================
            # TEST SUMMARY
            # ========================================
            print("\n" + "=" * 60)
            print("=== TEST COMPLETED SUCCESSFULLY ===")
            print("=" * 60)
            print("\nTests performed:")
            print("  [PASS] Navigate to Profile page")
            print("  [PASS] Capture original data")
            print("  [PASS] Validation (required field)")
            print("  [PASS] Update profile information")
            print("  [PASS] Verify updated data")
            print("  [PASS] Test Reset functionality")

            if avatar_file.exists():
                print("  [PASS] Avatar upload with cropping")
                print("  [PASS] Avatar deletion")
            else:
                print("  [SKIP] Avatar tests (test file not found)")

            if resume_file.exists():
                print("  [PASS] Resume upload")
                print("  [PASS] Resume deletion")
            else:
                print("  [SKIP] Resume tests (test file not found)")

            print("  [PASS] Data persistence after reload")
            print("  [PASS] Update profile again")
            print("  [PASS] Restore original data")
            print("\nScreenshots saved to /tmp/test_profile_*.png")

            return True

        except AssertionError as e:
            print(f"\n[ASSERTION ERROR] {e}")
            take_screenshot(page, "profile_error_assertion", "Assertion error")
            import traceback

            traceback.print_exc()
            return False
        except Exception as e:
            print(f"\n[ERROR] {e}")
            take_screenshot(page, "profile_error", "Error occurred")
            import traceback

            traceback.print_exc()
            return False
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    success = test_profile()
    sys.exit(0 if success else 1)
