"""
Account chart loading and lookup utilities.
"""

import pandas as pd

from config import (
    ACCOUNT_TYPE_LABELS,
    ACCOUNT_TYPE_MAP,
    ACCOUNTS_CSV,
    CODE_LEVEL_LABELS,
    LEAF_CODE_LENGTH,
)


def load_accounts_df() -> pd.DataFrame:
    """Load the chart of accounts from CSV into a DataFrame."""
    df = pd.read_csv(ACCOUNTS_CSV, dtype={"code": str})
    return df


def get_accounts_dict() -> dict:
    """Return {code: name} dictionary for all accounts."""
    df = load_accounts_df()
    return dict(zip(df["code"], df["name"]))


def get_leaf_accounts() -> list[tuple[str, str]]:
    """Return list of (code, name) for leaf-level (posting) accounts."""
    df = load_accounts_df()
    mask = df["code"].str.len() == LEAF_CODE_LENGTH
    return list(zip(df.loc[mask, "code"], df.loc[mask, "name"]))


def get_account_type(code: str) -> str:
    """Determine account type from leading digit."""
    code = str(code)
    for prefix, acct_type in ACCOUNT_TYPE_MAP.items():
        if code.startswith(prefix):
            return acct_type
    return "Other"


def get_account_type_label(code: str) -> str:
    """Return the English label for an account's type."""
    eng = get_account_type(code)
    return ACCOUNT_TYPE_LABELS.get(eng, "Other")


def get_code_level_label(code: str) -> str:
    """Return level label based on code length."""
    return CODE_LEVEL_LABELS.get(len(str(code)), "")


def build_accounts_display_df() -> pd.DataFrame:
    """Build a display-ready DataFrame with type and level columns."""
    df = load_accounts_df()
    # Renaming columns to English for the UI
    df.rename(columns={"code": "Code", "name": "Account Name"}, inplace=True)
    df["Type"] = df["Code"].apply(get_account_type_label)
    df["Level"] = df["Code"].apply(get_code_level_label)
    return df
