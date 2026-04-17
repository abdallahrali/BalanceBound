"""
Logic layer for the Accounting System.
Exposes core business logic: account lookups, journal operations, and reporting.
"""

from logic.accounts import (
    get_account_type_label,  # Renamed from get_account_type_arabic
)
from logic.accounts import (
    build_accounts_display_df,
    get_account_type,
    get_accounts_dict,
    get_code_level_label,
    get_leaf_accounts,
    load_accounts_df,
)
from logic.journal import (
    add_je_line,
    delete_journal_entry,
    get_all_entries,
    init_session_state,
    remove_je_line,
    reset_je_lines,
    save_journal_entry,
    validate_je_lines,
)
from logic.reports import (
    compute_trial_balance,
    format_currency,
    get_asset_breakdown,
    get_balance_sheet_data,
    get_income_statement_data,
)

__all__ = [
    # accounts
    "load_accounts_df",
    "get_accounts_dict",
    "get_leaf_accounts",
    "get_account_type",
    "get_account_type_label",  # Renamed from get_account_type_arabic
    "get_code_level_label",
    "build_accounts_display_df",
    # journal
    "init_session_state",
    "reset_je_lines",
    "add_je_line",
    "remove_je_line",
    "validate_je_lines",
    "save_journal_entry",
    "delete_journal_entry",
    "get_all_entries",
    # reports
    "compute_trial_balance",
    "format_currency",
    "get_income_statement_data",
    "get_balance_sheet_data",
    "get_asset_breakdown",
]
