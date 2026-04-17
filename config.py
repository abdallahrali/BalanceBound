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
APP_TITLE = "نظام المحاسبة | Accounting System"
APP_ICON = "📊"
APP_VERSION = "1.0"

# ─── Account type prefixes ────────────────────────────────────────────────────
ACCOUNT_TYPE_MAP = {
    "1": "Asset",
    "2": "Liability/Equity",
    "3": "Expense",
    "4": "Revenue",
}

ACCOUNT_TYPE_ARABIC = {
    "Asset": "أصول",
    "Liability/Equity": "التزامات وحقوق ملكية",
    "Expense": "مصروفات",
    "Revenue": "إيرادات",
    "Other": "أخرى",
}

# ─── Leaf account code length (posting level) ─────────────────────────────────
LEAF_CODE_LENGTH = 9

# ─── Level labels ─────────────────────────────────────────────────────────────
CODE_LEVEL_LABELS = {
    1: "رئيسي",
    2: "مجموعة",
    3: "فئة",
    4: "حساب",
    9: "حساب فرعي",
}

# ─── Navigation pages ─────────────────────────────────────────────────────────
PAGES = {
    "🏠 لوحة التحكم": "dashboard",
    "📖 دليل الحسابات": "chart_of_accounts",
    "✍️ القيود اليومية": "journal_entries",
    "⚖️ ميزان المراجعة": "trial_balance",
    "💹 قائمة الدخل": "income_statement",
    "🏛️ الميزانية العمومية": "balance_sheet",
}
