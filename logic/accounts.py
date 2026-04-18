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




def save_accounts_to_csv(df: pd.DataFrame):
    """
    Saves the updated DataFrame back to the accounts.csv file.
    It handles renaming columns back to the CSV format.
    """
    # Create a copy to avoid modifying the UI dataframe
    save_df = df.copy()
    
    # Rename columns back to original CSV format (code, name)
    # only if they were renamed for display
    if "Code" in save_df.columns:
        save_df.rename(columns={"Code": "code"}, inplace=True)
    if "Account Name" in save_df.columns:
        save_df.rename(columns={"Account Name": "name"}, inplace=True)
        
    # We only want to save 'code' and 'name' columns to the CSV
    # (Type and Level are calculated dynamically, so we don't save them)
    save_df = save_df[["code", "name"]]
    
    # Save to CSV
    save_df.to_csv(ACCOUNTS_CSV, index=False)