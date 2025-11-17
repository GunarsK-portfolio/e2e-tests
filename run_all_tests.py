#!/usr/bin/env python3
"""
Test Suite Runner
Runs all E2E tests for the portfolio admin web application
"""

import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


class TestRunner:
    """Manages and runs all E2E tests"""

    def __init__(self):
        self.testing_dir = Path(__file__).parent
        self.results = []
        self.start_time = None
        self.end_time = None

    def run_test(self, test_path, test_name):
        """Run a single test file"""
        print("\n" + "=" * 70)
        print(f"Running: {test_name}")
        print("=" * 70)

        try:
            # Set PYTHONPATH to include the testing directory so imports work
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.testing_dir)

            result = subprocess.run(
                [sys.executable, str(test_path)],
                cwd=str(self.testing_dir),
                capture_output=False,  # Show output in real-time
                timeout=300,  # 5 minute timeout per test
                check=False,  # Don't raise exception on non-zero exit
                env=env,  # Pass modified environment
            )

            success = result.returncode == 0
            self.results.append(
                {
                    "name": test_name,
                    "path": test_path,
                    "success": success,
                    "returncode": result.returncode,
                }
            )

            return success

        except subprocess.TimeoutExpired:
            print("\n[TIMEOUT] Test exceeded 5 minute timeout")
            self.results.append(
                {
                    "name": test_name,
                    "path": test_path,
                    "success": False,
                    "returncode": -1,
                    "error": "Timeout",
                }
            )
            return False

        except (OSError, PermissionError) as e:
            print(f"\n[ERROR] Failed to run test: {e}")
            print(f"Traceback:\n{traceback.format_exc()}")
            self.results.append(
                {
                    "name": test_name,
                    "path": test_path,
                    "success": False,
                    "returncode": -1,
                    "error": str(e),
                }
            )
            return False

    def run_all_tests(self):
        """Run all available E2E tests"""
        self.start_time = datetime.now(timezone.utc)

        tests = [
            # Authentication must run first
            (self.testing_dir / "e2e" / "auth-flow" / "test_auth_flow.py", "Authentication Flow"),
            # Navigation
            (
                self.testing_dir / "e2e" / "dashboard" / "test_dashboard_navigation.py",
                "Dashboard Navigation",
            ),
            # CRUD tests - can run in any order
            (self.testing_dir / "e2e" / "profile" / "test_profile.py", "Profile Management"),
            (self.testing_dir / "e2e" / "skills" / "test_skills_crud.py", "Skills CRUD"),
            (
                self.testing_dir / "e2e" / "experience" / "test_experience_crud.py",
                "Work Experience CRUD",
            ),
            (
                self.testing_dir / "e2e" / "certifications" / "test_certifications_crud.py",
                "Certifications CRUD",
            ),
            (
                self.testing_dir / "e2e" / "portfolio-projects" / "test_portfolio_projects_crud.py",
                "Portfolio Projects CRUD",
            ),
            # Miniatures CRUD tests
            (
                self.testing_dir / "e2e" / "miniatures" / "test_paints_crud.py",
                "Miniatures Paints CRUD",
            ),
            (
                self.testing_dir / "e2e" / "miniatures" / "test_themes_crud.py",
                "Miniatures Themes CRUD",
            ),
            (
                self.testing_dir / "e2e" / "miniatures" / "test_projects_crud.py",
                "Miniatures Projects CRUD",
            ),
        ]

        print("\n" + "=" * 70)
        print("PORTFOLIO E2E TEST SUITE")
        print("=" * 70)
        print(f"Starting test run at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total tests: {len(tests)}")

        for test_path, test_name in tests:
            if test_path.exists():
                self.run_test(test_path, test_name)
            else:
                print(f"\n[SKIP] Test not found: {test_path}")
                self.results.append(
                    {
                        "name": test_name,
                        "path": test_path,
                        "success": False,
                        "error": "Test file not found",
                    }
                )

        self.end_time = datetime.now(timezone.utc)
        return self.print_summary()

    def print_summary(self):
        """Print test execution summary"""
        duration = (self.end_time - self.start_time).total_seconds()

        print("\n" + "=" * 70)
        print("TEST SUITE SUMMARY")
        print("=" * 70)

        passed = sum(1 for r in self.results if r["success"])
        failed = len(self.results) - passed

        print(f"\nTotal Tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Duration: {duration:.2f} seconds")

        if failed > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result["success"]:
                    error_msg = result.get(
                        "error", f"Exit code: {result.get('returncode', 'unknown')}"
                    )
                    print(f"  - {result['name']}: {error_msg}")

        print("\nPassed Tests:")
        for result in self.results:
            if result["success"]:
                print(f"  - {result['name']}")

        print("\n" + "=" * 70)

        return passed == len(self.results)


def main():
    """Main entry point"""
    runner = TestRunner()

    # Skip confirmation if running non-interactively or --no-confirm flag
    if "--no-confirm" in sys.argv or not sys.stdin.isatty():
        print("\n" + "=" * 70)
        print("PORTFOLIO E2E TEST SUITE")
        print("=" * 70)
        print("\nRunning all E2E tests...")
    else:
        print("\n" + "=" * 70)
        print("PORTFOLIO E2E TEST SUITE")
        print("=" * 70)
        print("\nThis will run all E2E tests for the portfolio admin web.")
        print("Each test will open a browser window.")
        print("\nPress Enter to continue or Ctrl+C to cancel...")

        try:
            input()
        except KeyboardInterrupt:
            print("\n\nTest run cancelled.")
            return 1

    all_passed = runner.run_all_tests()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
