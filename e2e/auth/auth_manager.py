"""
Authentication Manager for E2E Tests

Supports multiple authentication strategies:
1. Credentials from .env via config module
2. Saved browser context (cookies/session)
3. Manual login prompt (only in interactive mode)
"""

import sys
from pathlib import Path

from e2e.common.config import get_config


class AuthManager:
    """Manages authentication for E2E tests"""

    def __init__(self, base_url=None, username=None, password=None):
        """
        Initialize AuthManager with optional custom credentials.

        Args:
            base_url: Optional base URL override
            username: Optional username override (uses config if not provided)
            password: Optional password override (uses config if not provided)
        """
        self.config = get_config()
        self.base_url = base_url or self.config["admin_web_url"]
        self.context_path = Path(__file__).parent / ".auth" / "context.json"
        self.credentials = {
            "username": username or self.config["admin_username"],
            "password": password or self.config["admin_password"],
        }

    def ensure_auth_directory(self):
        """Ensure .auth directory exists for storing context"""
        self.context_path.parent.mkdir(parents=True, exist_ok=True)

    def save_context(self, context):
        """Save browser context (cookies/session) for reuse"""
        self.ensure_auth_directory()
        context.storage_state(path=str(self.context_path))
        print(f"   [OK] Saved auth context to {self.context_path}")

    def load_context(self, browser):
        """Load saved browser context if available"""
        if self.context_path.exists():
            try:
                context = browser.new_context(
                    storage_state=str(self.context_path),
                    ignore_https_errors=self.config.get("ignore_https_errors", False),
                )
                print("   [OK] Loaded saved auth context")
                return context
            except Exception as e:
                print(f"   [WARN] Could not load saved context: {e}")
        return None

    def login_with_credentials(self, page, username=None, password=None):
        """Login using provided credentials or stored credentials"""
        creds = (
            {"username": username, "password": password}
            if username and password
            else self.credentials
        )

        if not creds["username"] or not creds["password"]:
            print("   [FAIL] No credentials available")
            return False

        print(f"   [INFO] Attempting login with username: {creds['username']}")

        # Navigate to login page
        page.goto(f"{self.base_url}/login")
        page.wait_for_load_state("networkidle")

        # Fill form - login uses username field
        username_input = page.locator('input[type="text"], input[placeholder*="username" i]').first
        password_input = page.locator('input[type="password"]').first

        if username_input.count() == 0 or password_input.count() == 0:
            print("   [FAIL] Login form not found")
            return False

        username_input.fill(creds["username"])
        password_input.fill(creds["password"])

        # Submit
        login_btn = page.locator(
            'button[type="submit"], button:has-text("Login"), button:has-text("Sign in")'
        ).first
        if login_btn.count() > 0:
            login_btn.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)  # Wait for redirect

            # Check success
            if "dashboard" in page.url or "login" not in page.url:
                print("   [OK] Login successful")
                return True
            else:
                print("   [FAIL] Login failed - still on login page")
                return False
        else:
            print("   [FAIL] Login button not found")
            return False

    def login_manual(self, page):
        """Prompt user to login manually (only in interactive mode)"""
        # Check if running in non-interactive mode (CI, piped input, etc.)
        if not sys.stdin.isatty():
            print("   [FAIL] Manual login not available in non-interactive mode")
            return False

        print("\n" + "=" * 60)
        print("MANUAL LOGIN REQUIRED")
        print("=" * 60)
        print(f"1. A browser window is open at: {page.url}")
        print("2. Please login manually in the browser")
        print("3. After successful login, press Enter here")
        print("=" * 60)
        input("\nPress Enter after logging in...")

        # Verify login
        page.wait_for_load_state("networkidle")
        if "login" not in page.url:
            print("   [OK] Manual login successful")
            return True
        else:
            print("   [FAIL] Still on login page")
            return False

    def authenticate(self, browser, strategy="auto"):
        """
        Authenticate using specified strategy

        Strategies:
        - 'auto': Try credentials first (validation), fallback to saved context
        - 'context': Use saved context only
        - 'credentials': Use credentials only
        - 'manual': Manual login only
        """
        print("\n[AUTH] Starting authentication...")
        print(f"[AUTH] Base URL: {self.base_url}")

        # For 'auto' strategy: prefer credentials over saved context to ensure validation
        # Only use saved context if credentials are not provided
        if strategy == "auto" and self.credentials["username"]:
            # Credentials are available, use them (don't trust saved context)
            context = browser.new_context(
                ignore_https_errors=self.config.get("ignore_https_errors", False)
            )
            page = context.new_page()

            if self.login_with_credentials(page):
                self.save_context(context)
                return page, context

            # Credentials failed - fail immediately, don't try manual login
            print("   [FAIL] Credentials invalid")
            page.close()
            context.close()
            raise RuntimeError(
                "Authentication failed: Invalid credentials in .env file. "
                "Check TEST_ADMIN_USERNAME and TEST_ADMIN_PASSWORD."
            )

        # Try saved context (if context strategy, or if auto with no credentials)
        if strategy in ["auto", "context"]:
            context = self.load_context(browser)
            if context:
                page = context.new_page()
                page.goto(f"{self.base_url}/dashboard")
                page.wait_for_load_state("networkidle")

                if "login" not in page.url:
                    print("   [OK] Authenticated using saved context")
                    return page, context

                print("   [INFO] Saved context expired, trying other methods...")
                page.close()
                context.close()

        # Create new context
        context = browser.new_context(
            ignore_https_errors=self.config.get("ignore_https_errors", False)
        )
        page = context.new_page()

        # Try credentials (if credentials strategy - auto already tried above)
        if strategy == "credentials" and self.credentials["username"]:
            if self.login_with_credentials(page):
                self.save_context(context)
                return page, context

        # Manual login (if auto or manual strategy, or if previous methods failed)
        if strategy in ["auto", "manual"]:
            page.goto(f"{self.base_url}/login")
            page.wait_for_load_state("networkidle")

            if self.login_manual(page):
                self.save_context(context)
                return page, context

        print("   [FAIL] All authentication methods failed")
        page.close()
        context.close()
        raise RuntimeError(
            "Authentication failed: All authentication methods exhausted. "
            "Check credentials in .env or run tests interactively."
        )


def authenticate_for_testing(browser, base_url=None, strategy="auto"):
    """
    Convenience function for test scripts

    Raises RuntimeError if authentication fails
    Returns: (page, context) tuple
    """
    auth_manager = AuthManager(base_url)
    return auth_manager.authenticate(browser, strategy)
