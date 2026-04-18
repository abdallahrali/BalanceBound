"""
Application-wide configuration and constants.
"""

import os

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

ACCOUNTS_CSV = os.path.join(DATA_DIR, "accounts.csv")
OPENING_BALANCES_CSV = os.path.join(DATA_DIR, "opening_balances.csv")
SAMPLE_ENTRIES_JSON = os.path.join(DATA_DIR, "sample_entries.json")

# ─── App Metadata ─────────────────────────────────────────────────────────────
APP_TITLE = "Accounting System"
APP_ICON = "📊"
APP_VERSION = "1.0"

# ─── Account type prefixes ────────────────────────────────────────────────────
ACCOUNT_TYPE_MAP = {
    "1": "Asset",
    "2": "Liability/Equity",
    "3": "Expense",
    "4": "Revenue",
}

# Note: Renamed from ACCOUNT_TYPE_ARABIC to ACCOUNT_TYPE_LABELS for clarity in English
ACCOUNT_TYPE_LABELS = {
    "Asset": "Asset",
    "Liability/Equity": "Liability/Equity",
    "Expense": "Expense",
    "Revenue": "Revenue",
    "Other": "Other",
}

# ─── Leaf account code length (posting level) ─────────────────────────────────
LEAF_CODE_LENGTH = 9

# ─── Level labels ─────────────────────────────────────────────────────────────
CODE_LEVEL_LABELS = {
    1: "Type",  # e.g., "1"
    3: "Category",  # e.g., "101"
    6: "Account",  # e.g., "101001"
    9: "Sub-account",  # e.g., "101001001"
}

# ─── Navigation pages ─────────────────────────────────────────────────────────
PAGES = {
    "🏠 Dashboard": "dashboard",
    "📖 Chart of Accounts": "chart_of_accounts",
    "✍️ Journal Entries": "journal_entries",
    "⚖️ Trial Balance": "trial_balance",
    "💹 Income Statement": "income_statement",
    "🏛️ Balance Sheet": "balance_sheet",
}
