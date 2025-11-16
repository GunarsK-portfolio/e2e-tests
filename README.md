# E2E Tests

End-to-end tests for portfolio admin web using Playwright and Python.

## Quick Start

```bash
# Setup
pip install -r requirements.txt
playwright install chromium
task setup:env                    # Create .env from template

# Edit .env with your credentials
TEST_ADMIN_USERNAME=admin
TEST_ADMIN_PASSWORD=your_password
TEST_ADMIN_WEB_URL=http://localhost:81

# Run tests
task test:all                     # All tests
task test:profile                 # Individual test suite
```

## Prerequisites

- Python 3.12+
- Running services (admin-web on port 81, admin-api on 8083)
- Valid admin credentials in `.env`

Start services:

```bash
cd ../infrastructure
docker-compose up -d
```

## Available Commands

### Testing

```bash
task test:all                     # All tests (browser visible)
task test:all:headless            # All tests (headless mode)
task test:profile                 # Profile management
task test:skills                  # Skills CRUD
task test:experience              # Work Experience CRUD
task test:certifications          # Certifications CRUD
task test:miniatures              # Miniatures CRUD
```

### Code Quality

```bash
task lint                         # Run all linters (black, flake8, isort, pylint, mypy)
task format                       # Auto-format code
task ci:all                       # Run all CI checks
```

### Maintenance

```bash
task setup                        # Install dependencies
task setup:env                    # Create .env
task check:env                    # Verify configuration
task clean                        # Clean cache and screenshots
task list                         # List all test suites
```

## Test Coverage

- **Profile** (14 steps):
  - Basic information and contact info updates
  - Avatar upload with image cropper
  - Resume upload (PDF/DOC/DOCX)
  - File deletion (avatar and resume)
  - Form validation
  - Data persistence testing

- **Work Experience** (11 steps):
  - Full CRUD operations
  - Date range handling (start/end dates)
  - "Currently working here" toggle
  - Search and filtering
  - Form validation
  - Data persistence testing

- **Skills** (13 steps):
  - Dual-tab CRUD (Skills + Skill Types)
  - Skill type association
  - Form validation
  - Search functionality
  - Display order management
  - Data persistence testing

- **Certifications** (12 steps):
  - Full CRUD with date validation
  - Credential ID and URL management
  - Status calculation (Valid/Expired/No Expiry)
  - Date validation (expiry must be after issue)
  - Multi-field search
  - Data persistence testing

- **Portfolio Projects** (12 steps):
  - Full CRUD operations
  - Category selection
  - GitHub and Live Demo URL validation
  - Short and detailed descriptions
  - Search functionality
  - Data persistence testing

- **Authentication Flow** (11 steps):
  - Login/logout functionality
  - Invalid credentials handling
  - Session persistence (reload and new tab)
  - Protected route access control
  - Re-login after logout

- **Dashboard Navigation** (10 steps):
  - Dashboard layout verification
  - Navigation to all feature pages
  - Root URL redirect testing

## Authentication

Tests use a multi-strategy auth system:

1. **Saved Context** (fastest) - Reuses browser session from previous run
2. **Credentials** - Auto-login from `.env`
3. **Manual** - Prompts for manual login if needed

After first login, context is saved for instant authentication.

## Configuration

Edit `.env` file:

```bash
# Authentication
TEST_ADMIN_USERNAME=admin
TEST_ADMIN_PASSWORD=your_password

# URLs
TEST_ADMIN_WEB_URL=http://localhost:81
TEST_ADMIN_API_URL=http://localhost:8083

# Browser
TEST_HEADLESS=false
TEST_BROWSER=chromium
```

## CI/CD

```bash
task ci:all                       # Linting + headless tests
```

Configured with:

- GitHub Actions workflow (`.github/workflows/ci.yml`)
- CodeRabbit for automated reviews (`.coderabbit.yaml`)
- Renovate for dependency updates (`renovate.json`)

## Linting

All code passes with **pylint 10.00/10**:

- **black** - Code formatting (100 char line length)
- **flake8** - Style and syntax
- **isort** - Import sorting
- **pylint** - Static analysis
- **mypy** - Type checking

## Troubleshooting

**Authentication fails:**

```bash
task clean                        # Clear saved context
task check:env                    # Verify config
task test:all                     # Re-authenticate
```

**Services not running:**

```bash
docker ps                         # Check status
cd ../infrastructure
docker-compose up -d              # Start services
```

## Development

Add new test:

```python
from e2e.auth.auth_manager import AuthManager
from e2e.common.config import get_config
from playwright.sync_api import sync_playwright

def test_new_feature():
    with sync_playwright() as p:
        auth_manager = AuthManager()
        browser = p.chromium.launch(headless=False)
        page, context = auth_manager.authenticate(browser, strategy='auto')

        # Test logic here

        context.close()
        browser.close()
```

Add task to `Taskfile.yml`:

```yaml
test:new-feature:
  desc: Run new feature tests
  cmds:
    - python e2e/new_feature/test_new_feature.py
```

## Test Execution

### Run All Tests

```bash
python run_all_tests.py
```

This executes all tests in optimal order:
1. Authentication Flow (validates login/logout)
2. Dashboard Navigation (validates routing)
3. All CRUD tests (Profile, Skills, Work Experience, Certifications, Portfolio Projects)

### Run Individual Tests

```bash
# Authentication
python e2e/auth-flow/test_auth_flow.py

# Navigation
python e2e/dashboard/test_dashboard_navigation.py

# CRUD tests
python e2e/profile/test_profile.py
python e2e/skills/test_skills_crud.py
python e2e/experience/test_experience_crud.py
python e2e/certifications/test_certifications_crud.py
python e2e/portfolio-projects/test_portfolio_projects_crud.py
```

## Test Statistics

| Test Suite | Steps | Coverage |
|------------|-------|----------|
| Authentication Flow | 11 | Login, logout, session management, protected routes |
| Dashboard Navigation | 10 | Page navigation, routing, layout verification |
| Profile Management | 14 | CRUD, avatar upload, resume upload, file deletion |
| Work Experience CRUD | 11 | CRUD, date handling, search |
| Skills CRUD | 13 | Dual-tab CRUD, skill types, associations |
| Certifications CRUD | 12 | CRUD, date validation, credential URLs, status |
| Portfolio Projects CRUD | 12 | CRUD, URL validation, categories |
| **TOTAL** | **83 steps** | **7 comprehensive test suites** |

## Notes

- Tests run with browser visible by default
- Screenshots saved to system temp directory (configurable via TEST_SCREENSHOT_DIR)
- All tests are independent and can run in any order
- Test data uses timestamps for uniqueness
- Profile test restores original data after execution
- Miniatures test deferred for future enhancement (complex 3-tab structure)
