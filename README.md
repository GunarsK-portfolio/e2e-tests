# Portfolio Testing Suite

End-to-end testing for the portfolio project using Playwright and Python.

## Quick Start

1. **Set up environment**:

   ```bash
   task setup          # Install Playwright and dependencies
   task setup:env      # Create .env from template
   ```

2. **Edit .env with your credentials**:

   ```bash
   TEST_ADMIN_USERNAME=admin
   TEST_ADMIN_PASSWORD=your_password_here
   TEST_ADMIN_WEB_URL=http://localhost:81
   ```

3. **Run all tests**:

   ```bash
   task test:all       # Run all E2E tests
   ```

## Available Test Commands

### Run All Tests

```bash
task test:all              # Run all tests with browser visible
task test:all:headless     # Run all tests in headless mode (CI)
task test:all:interactive  # Run with confirmation prompt
```

### Run Individual Test Suites

```bash
task test:profile          # Profile management tests
task test:skills           # Skills CRUD tests
task test:experience       # Work Experience CRUD tests
task test:certifications   # Certifications/Education CRUD tests
task test:miniatures       # Miniatures comprehensive tests
```

### Setup and Maintenance

```bash
task setup                 # Install Playwright and browser
task setup:env             # Create .env from template
task check:env             # Verify .env configuration
task clean                 # Clean screenshots and auth cache
task clean:cache           # Clean Python cache files
task list                  # List all available test suites
```

## Project Structure

```text
testing/
├── e2e/                           # End-to-end tests
│   ├── common/                    # Shared utilities
│   │   ├── config.py              # Configuration management (.env loader)
│   │   └── helpers.py             # Common helper functions
│   ├── auth/                      # Authentication system
│   │   └── auth_manager.py        # Multi-strategy auth (context/credentials/manual)
│   ├── profile/                   # Profile management tests
│   │   └── test_profile.py
│   ├── skills/                    # Skills CRUD tests
│   │   └── test_skills_crud.py
│   ├── experience/                # Work Experience CRUD tests
│   │   └── test_experience_crud.py
│   ├── certifications/            # Certifications/Education CRUD tests
│   │   └── test_certifications_crud.py
│   └── miniatures/                # Miniatures feature tests
│       ├── test_miniatures_comprehensive.py
│       └── test_simple.py
├── run_all_tests.py               # Test suite runner
├── Taskfile.yml                   # Task automation
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore (excludes .env, .auth/)
└── README.md                      # This file
```

## Prerequisites

### 1. Python and Playwright

```bash
# Install Playwright
pip install playwright

# Install browser
playwright install chromium
```

Or use the setup task:

```bash
task setup
```

### 2. Running Services

Ensure these services are running (via Docker Compose):

- **admin-web** (frontend) on <http://localhost:81>
- **admin-api** (backend) on <http://localhost:8083>
- **PostgreSQL** database with migrations applied
- **Redis** for sessions

Start all services from the infrastructure repo:

```bash
cd infrastructure
docker-compose up -d
```

### 3. Authentication Configuration

Create and configure `.env` file:

```bash
task setup:env    # Creates .env from template
```

Edit `.env` with your credentials:

```bash
TEST_ADMIN_USERNAME=admin
TEST_ADMIN_PASSWORD=your_actual_password
TEST_ADMIN_WEB_URL=http://localhost:81
TEST_ADMIN_API_URL=http://localhost:8083
TEST_HEADLESS=false
TEST_BROWSER=chromium
```

## Test Coverage

### ✅ Implemented Tests

#### Profile Management

- Basic Information card (name, title, tagline)
- Contact Information card (email, phone, location)
- Avatar card and image upload
- Save functionality

#### Skills CRUD

- Skills tab with data table
- Skill Types tab with data table
- Add/Edit Skill modal (skill name, type, visibility, display order)
- Add/Edit Skill Type modal (name, description, display order)
- Search and filter functionality

#### Work Experience CRUD

- Experience list with data table
- Add/Edit Experience modal (company, position, description, start/end dates)
- "Currently working here" checkbox
- Date pickers for start and end dates
- Search and filter functionality

#### Certifications/Education CRUD

- Certifications list with data table
- Add/Edit Certification modal (name, issuer, issue/expiry dates, credential ID, URL)
- Date pickers for issue and expiry dates
- Search and filter functionality

#### Miniatures Comprehensive

- **Projects tab**: Add/Edit Project modal (title, theme, scale, manufacturer, difficulty, description, dates)
- **Themes tab**: Add/Edit Theme modal (name, description, display order)
- **Paints tab**: Add/Edit Paint modal (manufacturer, name, color code, type, finish)
- Tab navigation and data persistence
- Data tables with search and filter

### Authentication System

The test suite includes a sophisticated authentication manager with multiple strategies:

1. **Saved Context** (fastest): Reuses browser session/cookies from previous runs
2. **Credentials**: Automatic login using username/password from `.env`
3. **Manual Login**: Prompts user to login manually if other methods fail

After first successful login, subsequent test runs use saved context for instant authentication.

## Running Tests

### Run All Tests (Recommended)

```bash
task test:all
```

This runs all 5 test suites:

1. Profile Management
2. Skills CRUD
3. Work Experience CRUD
4. Certifications/Education CRUD
5. Miniatures Comprehensive

### Run Individual Tests

```bash
# Profile tests
task test:profile

# Skills tests
task test:skills

# Experience tests
task test:experience

# Certifications tests
task test:certifications

# Miniatures tests
task test:miniatures
```

### Or Run Directly with Python

```bash
# All tests
python run_all_tests.py --no-confirm

# Individual test
python e2e/profile/test_profile.py
```

## Test Output

### Screenshots

All tests save screenshots to `/tmp/` (or `C:\tmp\` on Windows) with descriptive names:

```text
profile_01_page.png
profile_02_contact.png
profile_03_avatar.png
skills_01_page.png
skills_02_skills_tab.png
skills_03_types_tab.png
...
```

### Test Results

The test runner provides detailed output:

```text
======================================================================
TEST SUITE SUMMARY
======================================================================

Total Tests: 5
Passed: 5
Failed: 0
Duration: 20.18 seconds

Passed Tests:
  - Profile Management
  - Skills CRUD
  - Work Experience CRUD
  - Certifications/Education CRUD
  - Miniatures Comprehensive
======================================================================
```

## Configuration Options

### Environment Variables

Configure via `.env` file:

```bash
# Authentication
TEST_ADMIN_USERNAME=admin
TEST_ADMIN_PASSWORD=your_password

# URLs
TEST_ADMIN_WEB_URL=http://localhost:81
TEST_ADMIN_API_URL=http://localhost:8083

# Browser Options
TEST_HEADLESS=false              # Set to 'true' for CI
TEST_BROWSER=chromium            # chromium, firefox, webkit
TEST_SLOW_MO=0                   # Milliseconds to slow down operations
TEST_TIMEOUT=30000               # Default timeout in ms

# Output
TEST_SCREENSHOT_DIR=/tmp         # Screenshot directory
```

### Headless Mode

For CI/CD or faster execution:

```bash
# Using task
task test:all:headless

# Or set in .env
TEST_HEADLESS=true
```

## CI/CD Integration

Run tests in CI environment:

```bash
task ci:all
```

This command:

1. Checks `.env` configuration
2. Runs all tests in headless mode
3. Exits with appropriate status code

## Troubleshooting

### Authentication Fails

```bash
# Clear saved authentication
task clean

# Verify .env configuration
task check:env

# Run test again - it will re-authenticate
task test:all
```

### Services Not Running

```bash
# Check if services are up
docker ps

# Start services
cd infrastructure
docker-compose up -d

# Check admin-web is accessible
curl http://localhost:81
```

### Python/Playwright Issues

```bash
# Reinstall Playwright
task setup

# Or manually
pip install --upgrade playwright
playwright install chromium
```

### Port Conflicts

If admin-web is not on port 81, update `.env`:

```bash
TEST_ADMIN_WEB_URL=http://localhost:YOUR_PORT
```

## Development

### Adding New Tests

1. Create test file in appropriate directory:

   ```bash
   touch e2e/new_feature/test_new_feature.py
   ```

2. Follow existing test patterns:

   ```python
   from auth.auth_manager import AuthManager
   from common.config import get_config

   def test_new_feature():
       with sync_playwright() as p:
           auth_manager = AuthManager()
           browser = p.chromium.launch(headless=False)
           page, context = auth_manager.authenticate(browser, strategy='auto')
           # ... your test logic
   ```

3. Add task to `Taskfile.yml`:

   ```yaml
   test:new-feature:
     desc: Run New Feature tests
     cmds:
       - python e2e/new_feature/test_new_feature.py
   ```

### Test Best Practices

- Use saved authentication (via AuthManager) to speed up tests
- Take screenshots at key steps for debugging
- Use descriptive test names and output messages
- Clean up resources in `finally` blocks
- Follow existing patterns for consistency

## Notes

- Tests run with browser visible by default (set `TEST_HEADLESS=true` for headless)
- Authentication context is saved after first login for fast re-runs
- Screenshots help debug failures
- All tests are independent and can run in any order
- Test data is not cleaned up automatically (you may need to manually delete test entries)

## Support

For issues or questions:

1. Check logs in test output
2. Review screenshots in `/tmp/`
3. Verify services are running: `docker ps`
4. Check `.env` configuration: `task check:env`
