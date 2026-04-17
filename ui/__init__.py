"""
UI layer for the Arabic Accounting System.
Each submodule corresponds to a single page and exposes a `render()` function.
"""

from ui import (
    balance_sheet,
    chart_of_accounts,
    dashboard,
    income_statement,
    journal_entries,
    trial_balance,
)
from ui.sidebar import render_sidebar
from ui.styles import inject_css

# Page module registry — maps page keys to their modules
PAGE_MODULES = {
    "dashboard": dashboard,
    "chart_of_accounts": chart_of_accounts,
    "journal_entries": journal_entries,
    "trial_balance": trial_balance,
    "income_statement": income_statement,
    "balance_sheet": balance_sheet,
}


def render_page(page_key: str):
    """
    Render a page by its key.
    Raises KeyError if the page_key is not registered.
    """
    if page_key not in PAGE_MODULES:
        raise KeyError(
            f"Unknown page: '{page_key}'. Valid pages: {list(PAGE_MODULES.keys())}"
        )
    PAGE_MODULES[page_key].render()


__all__ = [
    "inject_css",
    "render_sidebar",
    "render_page",
    "PAGE_MODULES",
    # Individual page modules
    "dashboard",
    "chart_of_accounts",
    "journal_entries",
    "trial_balance",
    "income_statement",
    "balance_sheet",
]
