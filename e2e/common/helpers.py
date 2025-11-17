"""
Common helper functions for E2E tests
"""

import tempfile
from pathlib import Path

from playwright.sync_api import Page

# ========================================
# CONSTANTS
# ========================================

LABEL_OR_PLACEHOLDER_REQUIRED_ERROR = "Either 'label' or 'placeholder' must be provided"

# ========================================
# SCREENSHOT AND PAGE HELPERS
# ========================================


def take_screenshot(page, name, description=""):
    """Take a screenshot with consistent naming"""
    temp_dir = Path(tempfile.gettempdir())
    path = temp_dir / f"test_{name}.png"
    page.screenshot(path=str(path))
    if description:
        print(f"   [SCREENSHOT] {description}: {path}")
    return str(path)


def wait_for_page_load(page):
    """Wait for page to fully load"""
    page.wait_for_load_state("networkidle")


def check_element_exists(page, selector, name=""):
    """Check if element exists and return count"""
    count = page.locator(selector).count()
    if count > 0:
        print(f"   ✅ {name or 'Element'} found ({count})")
    else:
        print(f"   ⚠️  {name or 'Element'} not found")
    return count > 0


# ========================================
# FORM INPUT HELPERS
# ========================================


def fill_text_input(
    page: Page, placeholder: str = None, value: str = None, label: str = None, wait_ms: int = 200
):
    """Fill a text input field by label (preferred) or placeholder (fallback)

    Args:
        page: Playwright page object
        placeholder: Input placeholder text (partial match, case-insensitive)
        value: Value to fill
        label: Form label text to identify the input (preferred method)
        wait_ms: Wait time in milliseconds
    """
    if label:
        # Find the form item by label text
        form_item = page.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
        input_field = form_item.locator("input").first
    elif placeholder:
        # Fallback to placeholder-based selection
        input_field = page.locator(f'input[placeholder*="{placeholder}" i]').first
    else:
        raise ValueError(LABEL_OR_PLACEHOLDER_REQUIRED_ERROR)

    input_field.fill(value)
    page.wait_for_timeout(wait_ms)


def fill_text_input_exact(
    page: Page,
    placeholder: str = None,
    value: str = None,
    label: str = None,
    exact: bool = True,
    wait_ms: int = 200,
):
    """Fill a text input field by label (preferred) or exact placeholder match (fallback)

    Args:
        page: Playwright page object
        placeholder: Input placeholder text (exact match)
        value: Value to fill
        label: Form label text to identify the input (preferred method)
        exact: Whether to use exact match for placeholder (default: True)
        wait_ms: Wait time in milliseconds
    """
    if label:
        # Find the form item by label text
        form_item = page.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
        input_field = form_item.locator("input").first
    elif placeholder:
        # Fallback to placeholder-based selection
        if exact:
            input_field = page.locator(f'input[placeholder="{placeholder}"]').first
        else:
            input_field = page.locator(f'input[placeholder*="{placeholder}" i]').first
    else:
        raise ValueError(LABEL_OR_PLACEHOLDER_REQUIRED_ERROR)

    input_field.fill(value)
    page.wait_for_timeout(wait_ms)


def fill_textarea(
    page: Page, placeholder: str = None, value: str = None, label: str = None, wait_ms: int = 200
):
    """Fill a textarea field by label (preferred) or placeholder (fallback)

    Args:
        page: Playwright page object
        placeholder: Textarea placeholder text (partial match, case-insensitive)
        value: Value to fill
        label: Form label text to identify the textarea (preferred method)
        wait_ms: Wait time in milliseconds
    """
    if label:
        # Find the form item by label text
        form_item = page.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
        textarea = form_item.locator("textarea").first
    elif placeholder:
        # Fallback to placeholder-based selection
        textarea = page.locator(f'textarea[placeholder*="{placeholder}" i]').first
    else:
        raise ValueError(LABEL_OR_PLACEHOLDER_REQUIRED_ERROR)

    textarea.fill(value)
    page.wait_for_timeout(wait_ms)


def fill_number_input(
    page: Page,
    placeholder: str = None,
    value: int | str = None,
    label: str = None,
    wait_ms: int = 200,
):
    """Fill a number input field by label (preferred) or placeholder (fallback)

    Args:
        page: Playwright page object
        placeholder: Input placeholder text (partial match, case-insensitive)
        value: Numeric value to fill
        label: Form label text to identify the input (preferred method)
        wait_ms: Wait time in milliseconds
    """
    if label:
        # Find the form item by label text
        form_item = page.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
        input_field = form_item.locator("input").first
    elif placeholder:
        # Fallback to placeholder-based selection
        input_field = page.locator(f'input[placeholder*="{placeholder}" i]').first
    else:
        raise ValueError(LABEL_OR_PLACEHOLDER_REQUIRED_ERROR)

    input_field.fill(str(value))
    page.wait_for_timeout(wait_ms)


def fill_date_input(
    page: Page, label: str = None, date_value: str = None, index: int = None, wait_ms: int = 200
):
    """Fill a date input field by label or index

    Args:
        page: Playwright page object
        label: Form label text to identify the date picker (e.g., "Issue Date", "Expiry Date")
        date_value: Date in format "YYYY-MM-DD"
        index: Fallback index of date picker (0-based) if label not provided
        wait_ms: Wait time in milliseconds
    """
    if label:
        # Find the form item by label text
        form_item = page.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
        date_input = form_item.locator('input[placeholder*="Select Date" i]').first
        if date_input.count() > 0:
            date_input.fill(date_value)
            page.wait_for_timeout(wait_ms)
            return True
    elif index is not None:
        # Fallback to index-based selection
        date_inputs = page.locator('input[placeholder*="Select Date" i]')
        if date_inputs.count() > index:
            date_inputs.nth(index).fill(date_value)
            page.wait_for_timeout(wait_ms)
            return True
    return False


def select_dropdown_option(
    page: Page, modal, option_index: int = 0, label: str = None, wait_ms: int = 300
):
    """Select an option from a dropdown (NSelect component)

    Args:
        page: Playwright page object
        modal: Modal locator
        option_index: Index of option to select (default: 0)
        label: Optional label text to identify specific dropdown (e.g., "Theme", "Difficulty")
        wait_ms: Wait time in milliseconds
    """
    if label:
        # Find the form item by label text (in .n-form-item-label element)
        form_item = modal.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
        dropdown = form_item.locator(".n-select").first
    else:
        # Fallback to first select in modal
        dropdown = modal.locator(".n-select").first

    dropdown.click()
    page.wait_for_timeout(wait_ms)

    options = page.locator(".n-base-select-option")
    options.nth(option_index).click()
    page.wait_for_timeout(200)


def fill_color_picker(page: Page, modal, hex_color: str, label: str = None, wait_ms: int = 300):
    """Fill the color picker with a hex color value

    Args:
        page: Playwright page object
        modal: Modal locator
        hex_color: Hex color value (e.g., "#FF5733")
        label: Form label text to identify the color picker (optional)
        wait_ms: Wait time in milliseconds
    """
    if label:
        # Find the form item by label text
        form_item = modal.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
        color_picker = form_item.locator(".n-color-picker-trigger").first
    else:
        # Fallback to first color picker in modal
        color_picker = modal.locator(".n-color-picker-trigger").first

    # Open color picker
    color_picker.click()
    page.wait_for_timeout(wait_ms)

    # Fill hex value
    hex_input = page.locator('input[placeholder*="HEX" i]').first
    hex_input.fill(hex_color)
    page.wait_for_timeout(200)

    # Confirm color selection
    confirm_btn = page.locator('button:has-text("Confirm")').first
    confirm_btn.click()
    page.wait_for_timeout(wait_ms)


def upload_file(page: Page, modal, file_path: str, wait_ms: int = 1000):
    """Upload a file using NUpload component"""
    # Target the file input within the upload component
    # NUpload creates a hidden file input that we need to interact with
    file_input = modal.locator('input[type="file"]').first
    file_input.set_input_files(file_path)
    page.wait_for_timeout(wait_ms)


def remove_uploaded_file(page: Page, modal, button_text: str = "Remove Image", wait_ms: int = 500):
    """Remove an uploaded file by clicking the remove button"""
    # Target small error-type button with specific text
    remove_btn = modal.locator(
        f'button.n-button--small-type.n-button--error-type:has-text("{button_text}")'
    ).first
    if remove_btn.count() > 0:
        remove_btn.click()
        page.wait_for_timeout(wait_ms)
        return True
    return False


def verify_file_uploaded(modal, file_name: str | None = None):
    """Verify that a file has been uploaded by checking for avatar or file info"""
    # Check for avatar (image preview)
    avatar = modal.locator(".n-avatar").first
    if avatar.count() > 0:
        if file_name:
            # Also verify file name is displayed
            file_info = modal.locator(f'.file-info:has-text("{file_name}")').first
            return file_info.count() > 0
        return True
    return False


# ========================================
# SEARCH HELPERS
# ========================================


def search_table(page: Page, search_term: str, wait_ms: int = 500):
    """Search in the table using the search input"""
    # Target SearchInput component by class and placeholder
    search_input = page.locator('.search-input input[placeholder*="Search" i]').first
    if search_input.count() > 0:
        search_input.fill(search_term)
        page.wait_for_timeout(wait_ms)
    else:
        print("   [WARN] Search input not found")


def clear_search(page: Page, wait_ms: int = 500):
    """Clear the search input"""
    # Target SearchInput component by class and placeholder
    search_input = page.locator('.search-input input[placeholder*="Search" i]').first
    if search_input.count() > 0:
        search_input.fill("")
        page.wait_for_timeout(wait_ms)


# ========================================
# MODAL HELPERS
# ========================================


def open_add_modal(page: Page, button_text: str, wait_ms: int = 500):
    """Open an Add modal by button text (e.g., 'Add Paint', 'Add Skill')"""
    # Target primary button with exact text (AddButton component)
    add_btn = page.locator(f'button.n-button--primary-type:has-text("{button_text}")').first
    assert add_btn.count() > 0, f"{button_text} button not found"
    add_btn.click()
    page.wait_for_timeout(wait_ms)

    # Target Naive UI modal dialog
    modal = page.locator('.n-modal[role="dialog"]')
    assert modal.count() > 0, "Modal not opened"
    return modal


def close_modal(page: Page, wait_ms: int = 300):
    """Close the modal by clicking Cancel"""
    # Target Cancel button within modal footer (ModalFooter component)
    cancel_btn = page.locator('.n-modal button:has-text("Cancel")').first
    cancel_btn.click()
    page.wait_for_timeout(wait_ms)


def save_modal(page: Page, wait_ms: int = 1000):
    """Save/Create/Update in the modal"""
    # Target primary button in modal footer (ModalFooter component - Create/Update button)
    save_btn = page.locator(
        '.n-modal button.n-button--primary-type:has-text("Create"), '
        '.n-modal button.n-button--primary-type:has-text("Update"), '
        '.n-modal button.n-button--primary-type:has-text("Save")'
    ).first
    save_btn.click()
    page.wait_for_timeout(wait_ms)


def open_edit_modal(page: Page, row_identifier: str, wait_ms: int = 500):
    """Open the edit modal for a specific row by text identifier"""
    row = find_table_row(page, row_identifier)
    # Target small button with Edit aria-label (createActionsRenderer creates these)
    edit_btn = row.locator('button.n-button--small-type[aria-label*="Edit" i]').first
    edit_btn.click()
    page.wait_for_timeout(wait_ms)

    # Target Naive UI modal dialog
    modal = page.locator('.n-modal[role="dialog"]')
    assert modal.is_visible(), "Edit modal should be visible"
    return modal


# ========================================
# TABLE ACTION HELPERS
# ========================================


def find_table_row(page: Page, row_identifier: str):
    """Find a table row by text identifier"""
    # Target data table body row
    return page.locator(f'.n-data-table tbody tr:has-text("{row_identifier}")')


def delete_row(page: Page, row_identifier: str, wait_ms: int = 500):
    """Delete a row with confirmation"""
    row = find_table_row(page, row_identifier)
    # Target small error-type button with Delete aria-label (createActionsRenderer creates these)
    delete_btn = row.locator('button.n-button--small-type[aria-label*="Delete" i]').first
    delete_btn.click()
    page.wait_for_timeout(wait_ms)

    # Confirm deletion in dialog
    confirm_btn = page.locator(
        '.n-dialog button:has-text("Confirm"), '
        '.n-dialog button:has-text("Delete"), '
        '.n-dialog button:has-text("Yes")'
    ).first
    if confirm_btn.count() > 0:
        confirm_btn.click()
        page.wait_for_timeout(1000)


# ========================================
# NAVIGATION HELPERS
# ========================================


def navigate_to_page(page: Page, base_url: str, route: str, wait_ms: int = 500):
    """Navigate to a specific page

    Args:
        page: Playwright page object
        base_url: Base URL (e.g., "http://localhost:3000")
        route: Route to navigate to (e.g., "certifications", "work-experience")
        wait_ms: Wait time after navigation
    """
    page.goto(f"{base_url}/{route}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(wait_ms)


def navigate_to_tab(page: Page, base_url: str, route: str, tab_name: str, wait_ms: int = 500):
    """Navigate to a specific page and click a tab"""
    page.goto(f"{base_url}/{route}")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(wait_ms)

    # Target the tab by its label within the n-tabs-tab structure
    tab = page.locator(f'.n-tabs-tab:has-text("{tab_name}")').first
    # Wait for tab to be visible before clicking
    tab.wait_for(state="visible", timeout=5000)
    tab.click()
    page.wait_for_timeout(wait_ms)


def expand_collapse_section(page: Page, section_name: str, wait_ms: int = 300):
    """Expand a collapsed section by clicking its header"""
    # Target n-collapse-item header by title text
    collapse_header = page.locator(
        f'.n-collapse-item:has-text("{section_name}") .n-collapse-item__header'
    ).first
    if collapse_header.count() > 0:
        # Check if already expanded by looking for the expanded class
        parent_item = page.locator(f'.n-collapse-item:has-text("{section_name}")').first
        is_expanded = "n-collapse-item--active" in (parent_item.get_attribute("class") or "")

        if not is_expanded:
            collapse_header.click()
            page.wait_for_timeout(wait_ms)


# ========================================
# DASHBOARD NAVIGATION HELPERS
# ========================================


def find_dashboard_card(page: Page, card_title: str):
    """Find a dashboard navigation card by its title

    Args:
        page: Playwright page object
        card_title: The card title text (e.g., "Profile", "Skills")

    Returns:
        Locator for the card element
    """
    return page.locator(f'.n-card:has(h3.card-title:has-text("{card_title}"))').first


def click_dashboard_card_button(page: Page, card_title: str, button_text: str, wait_ms: int = 500):
    """Click a button within a specific dashboard card

    Args:
        page: Playwright page object
        card_title: The card title to identify which card
        button_text: The button text to click
        wait_ms: Wait time after click in milliseconds
    """
    card = find_dashboard_card(page, card_title)
    button = card.locator(f'button:has-text("{button_text}")').first
    button.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(wait_ms)


# ========================================
# GENERAL INPUT VALUE HELPERS
# ========================================


def get_input_value(page: Page, label: str):
    """Get the current value of an input field by label

    Args:
        page: Playwright page object
        label: Form label text to identify the input

    Returns:
        str: Current input value
    """
    form_item = page.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
    input_field = form_item.locator("input").first
    return input_field.input_value()


def get_textarea_value(page: Page, label: str):
    """Get the current value of a textarea field by label

    Args:
        page: Playwright page object
        label: Form label text to identify the textarea

    Returns:
        str: Current textarea value
    """
    form_item = page.locator(f'.n-form-item:has(.n-form-item-label:has-text("{label}"))').first
    textarea = form_item.locator("textarea").first
    return textarea.input_value()


# ========================================
# VERIFICATION HELPERS
# ========================================


def verify_row_exists(page: Page, identifier: str, entity_name: str = "entry", timeout: int = 5000):
    """Verify that a table row with specific text exists

    Args:
        page: Playwright page object
        identifier: Text to identify the row
        entity_name: Name of entity for logging (e.g., "skill", "certification")
        timeout: Timeout in milliseconds

    Returns:
        Locator: The found row locator
    """
    from playwright.sync_api import expect

    row = page.locator(f'tr:has-text("{identifier}")').first
    expect(row).to_be_visible(timeout=timeout)
    print(f"   [OK] {entity_name} '{identifier}' found in table")
    return row


def verify_row_not_exists(page: Page, identifier: str, entity_name: str = "entry"):
    """Verify that a table row does not exist

    Args:
        page: Playwright page object
        identifier: Text to identify the row
        entity_name: Name of entity for logging
    """
    from playwright.sync_api import expect

    row = page.locator(f'tr:has-text("{identifier}")').first
    expect(row).not_to_be_visible()
    print(f"   [OK] {entity_name} '{identifier}' not found in table")


def search_and_verify(
    page: Page,
    search_term: str,
    entity_name: str = "entry",
    timeout: int = 5000,
    wait_ms: int = 500,
):
    """Search for an item and verify it appears in results

    Args:
        page: Playwright page object
        search_term: Term to search for
        entity_name: Name of entity for logging
        timeout: Timeout for verification in milliseconds
        wait_ms: Wait time after search

    Returns:
        Locator: The found row locator
    """
    search_table(page, search_term, wait_ms)
    return verify_row_exists(page, search_term, entity_name, timeout)


def verify_cell_contains(row, text: str, description: str | None = None):
    """Verify that a row contains specific text in any cell

    Args:
        row: Row locator
        text: Text to find in cells
        description: Optional description for logging

    Returns:
        bool: True if cell with text found
    """
    cell = row.locator(f'td:has-text("{text}")').first
    found = cell.count() > 0
    if found and description:
        print(f"   [OK] {description}")
    return found
