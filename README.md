# E2E Tests

End-to-end tests for portfolio applications using Playwright and Python.

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
TEST_PUBLIC_WEB_URL=http://localhost

# Run tests
task test:admin                   # Admin-web tests
task test:public                  # Public-web tests
task test:admin:skills            # Individual test suite
```

## Prerequisites

- Python 3.12+
- Running services via Docker Compose
- Valid admin credentials in `.env` (for admin tests)

Start services:

```bash
cd ../infrastructure
docker-compose up -d
```

## Available Commands

### Testing

```bash
# Admin-web tests (require authentication)
task test:admin                   # All admin tests (browser visible)
task test:admin:headless          # All admin tests (headless mode)
task test:admin:auth              # Authentication flow
task test:admin:dashboard         # Dashboard navigation
task test:admin:profile           # Profile management
task test:admin:skills            # Skills CRUD
task test:admin:experience        # Work Experience CRUD
task test:admin:certifications    # Certifications CRUD
task test:admin:projects          # Portfolio Projects CRUD
task test:admin:paints            # Miniatures Paints CRUD
task test:admin:themes            # Miniatures Themes CRUD
task test:admin:miniatures        # Miniatures Projects CRUD
task test:admin:messaging         # Messaging CRUD
task test:admin:rbac              # All RBAC tests (admin + demo user)
task test:admin:rbac:admin        # RBAC admin walkthrough
task test:admin:rbac:demo         # RBAC demo user restrictions

# Public-web tests (no authentication required)
task test:public                  # All public tests (browser visible)
task test:public:headless         # All public tests (headless mode)
task test:public:home             # Home page
task test:public:projects         # Projects page
task test:public:contact          # Contact form
task test:public:gallery          # Miniatures gallery
task test:public:errors           # Error pages
```

### Code Quality

```bash
task lint                         # Run all linters (black, flake8, isort, pylint, mypy)
task format                       # Auto-format code
task ci:admin                     # Run all CI checks (admin tests)
task ci:public                    # Run all CI checks (public tests)
```

### Maintenance

```bash
task setup                        # Install dependencies
task setup:env                    # Create .env
task check:env                    # Verify configuration
task clean                        # Clean cache and screenshots
task list                         # List all test suites
```

## Test Suites

### Admin-Web Tests (13 suites)

- **Authentication Flow** (11 steps):
  - Login/logout functionality
  - Invalid credentials handling
  - Session persistence (reload and new tab)
  - Protected route access control
  - Re-login after logout

- **Dashboard Navigation** (11 steps):
  - Dashboard layout verification
  - Navigation to all feature pages (including Messaging)
  - Root URL redirect testing

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

- **Certifications** (11 steps):
  - Full CRUD with date validation
  - Credential ID and URL management
  - Status calculation (Valid/Expired/No Expiry)
  - Date validation (expiry must be after issue)
  - Multi-field search
  - Data persistence testing

- **Portfolio Projects** (13 steps):
  - Full CRUD operations
  - Category selection and ongoing project toggle
  - GitHub and Live Demo URL validation
  - Timeline management (start/end dates)
  - Search functionality
  - Data persistence testing

- **Miniatures - Themes** (9 steps):
  - Full CRUD operations
  - Cover image upload and removal
  - Display order management
  - Search by name and description
  - Data persistence testing

- **Miniatures - Paints** (9 steps):
  - Full CRUD operations
  - Color picker for hex values
  - Paint type and manufacturer management
  - Search by name and manufacturer
  - Data persistence testing

- **Miniatures - Projects** (9 steps):
  - Full CRUD operations
  - Theme association and project details
  - Multiple image uploads (up to 3)
  - Scale, manufacturer, difficulty tracking
  - Time spent and completion date management
  - Search by title and manufacturer
  - Data persistence testing

- **Messaging** (15 steps):
  - Recipients CRUD (create, edit, delete)
  - Email and name validation
  - Active/Inactive status toggle
  - Messages read-only viewing
  - Message details modal
  - Search by email, name, subject
  - Data persistence testing

- **RBAC - Admin Walkthrough** (12 steps):
  - Full admin permissions verification
  - All sidebar navigation items accessible
  - CRUD operations on all resources
  - File upload permissions (avatar, resume, images)
  - Delete operations confirmation
  - Permission indicators in UI

- **RBAC - Demo User Restrictions** (15 steps):
  - Limited sidebar navigation (hidden items)
  - Read-only access to permitted resources
  - View button instead of Edit for read-only
  - Hidden Add/Delete buttons
  - Hidden file upload sections
  - Modal opens in view-only mode (no Save button)
  - Blocked navigation to restricted pages
  - Permission-based UI element visibility

### Public-Web Tests (5 suites)

- **Home Page**:
  - Hero section with title and description
  - Skills display and types
  - Work experience section
  - Certifications display
  - Featured projects section
  - Contact CTA section
  - Back to top functionality
  - Page title verification

- **Projects Page**:
  - Featured Projects section on home
  - View All Projects button navigation
  - Projects page header and grid
  - Featured tags on projects
  - Project detail navigation
  - Navigation menu Projects link

- **Contact Form**:
  - Form field validation
  - Required field checks
  - Email format validation
  - Successful form submission
  - Error handling

- **Miniatures Gallery**:
  - Theme grid display
  - Theme detail navigation
  - Miniature detail pages
  - Image carousel/gallery
  - Paint colors section
  - Techniques section
  - Back navigation

- **Error Pages**:
  - 404 Not Found page
  - Navigation back to home
  - Contact link functionality

## Authentication

Admin tests use a multi-strategy auth system:

1. **Saved Context** (fastest) - Reuses browser session from previous run
2. **Credentials** - Auto-login from `.env`
3. **Manual** - Prompts for manual login if needed

After first login, context is saved for instant authentication.

## Configuration

See [.env.example](.env.example) for all available options with detailed comments.

For CI with HTTPS/Traefik, set `TEST_IGNORE_HTTPS_ERRORS=true` and use HTTPS URLs.

## CI/CD

```bash
task ci:admin                     # Linting + admin tests headless
task ci:public                    # Linting + public tests headless
```

GitHub Actions workflows:
- `admin-api`, `admin-web` repos run admin tests via `e2e.yml`
- `public-api`, `public-web` repos run public tests via `e2e.yml`

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
task test:admin                   # Re-authenticate
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
        browser = p.chromium.launch(headless=config["headless"])
        page, context = auth_manager.authenticate(browser, strategy='auto')

        # Test logic here

        context.close()
        browser.close()
```

Add task to `Taskfile.yml`:

```yaml
test:admin:new-feature:
  desc: Run new feature tests
  cmds:
    - python e2e/admin-web/new_feature/test_new_feature.py
```

## Test Statistics

| Test Suite | Steps | Coverage |
|------------|-------|----------|
| **Admin-Web Tests** | | |
| Authentication Flow | 11 | Login, logout, session management, protected routes |
| Dashboard Navigation | 10 | Page navigation, routing, layout verification |
| Profile Management | 14 | CRUD, avatar upload, resume upload, file deletion |
| Work Experience CRUD | 11 | CRUD, date handling, search |
| Skills CRUD | 19 | Dual-tab CRUD, skill types, associations |
| Certifications CRUD | 11 | CRUD, date validation, credential URLs, status |
| Portfolio Projects CRUD | 13 | CRUD, URL validation, categories, ongoing toggle |
| Miniatures Themes CRUD | 9 | CRUD, image upload/removal, search |
| Miniatures Paints CRUD | 9 | CRUD, color picker, manufacturer search |
| Miniatures Projects CRUD | 9 | CRUD, multi-image upload, theme association |
| Messaging CRUD | 15 | Recipients CRUD, messages viewing, search |
| RBAC Admin Walkthrough | 12 | Full permissions, all resources, file uploads |
| RBAC Demo User | 15 | Read-only access, hidden actions, view-only modals |
| **Public-Web Tests** | | |
| Home Page | 9 | Hero, skills, experience, certifications, featured projects |
| Projects Page | 8 | Featured section, View All, grid, detail navigation |
| Contact Form | 6 | Form validation, submission, error handling |
| Miniatures Gallery | 9 | Theme grid, detail pages, carousel, navigation |
| Error Pages | 4 | 404 page, navigation links |
| **TOTAL** | **~197 steps** | **18 comprehensive test suites** |

## Test Coverage

The test suites provide comprehensive coverage of the portfolio application:

- **Admin-Web**: Full CRUD lifecycle testing for all management views with form
  validation, error handling, and file uploads
- **Public-Web**: User journey testing including home page sections, contact form
  validation/submission, miniatures gallery navigation, and error page handling
- **Authentication**: Complete auth flow from login through session management to
  logout with persistence verification
- **RBAC**: Role-based access control testing for admin (full permissions) and demo
  user (read-only restrictions with hidden UI elements)

All critical user paths are covered with step-by-step verification and automated
screenshot capture for visual regression documentation.

## Test Assets

Test files are located in `test-files/`:
- `test-image.jpg` - Used for theme cover images and project image uploads
- `test-avatar.jpg` - Used for profile avatar upload testing
- `test-resume.pdf` - Used for profile resume upload testing

## Notes

- Tests run with browser visible by default
- Screenshots saved to system temp directory (configurable via TEST_SCREENSHOT_DIR)
- All tests are independent and can run in any order
- Test data uses timestamps for uniqueness
- Profile test restores original data after execution
- Helper-based pattern eliminates raw HTML selectors for better maintainability
