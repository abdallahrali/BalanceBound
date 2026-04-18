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


def get_code_level(code: str) -> int:
    """Return level based on code length."""
    return len(str(code))


def add_account(code: str, name: str, parent_code: str = None) -> tuple[bool, str]:
    """
    Add a new account to the chart of accounts.
    Returns (success, message).
    """
    df = load_accounts_df()
    code = str(code).strip()
    name = str(name).strip()
    
    if not code or not name:
        return False, "Code and name are required"
    
    if code in df["code"].values:
        return False, f"Account code '{code}' already exists"
    
    if parent_code:
        parent_code = str(parent_code).strip()
        if parent_code not in df["code"].values:
            return False, f"Parent account '{parent_code}' does not exist"
        parent_level = get_code_level(parent_code)
        new_level = get_code_level(code)
        if new_level != parent_level + 1:
            return False, f"Invalid level: code length should be {parent_level + 1} (parent level is {parent_level})"
    
    new_row = pd.DataFrame({"code": [code], "name": [name]})
    df = pd.concat([df, new_row], ignore_index=True)
    df = df.sort_values("code").reset_index(drop=True)
    df.to_csv(ACCOUNTS_CSV, index=False)
    return True, f"Account '{name}' added successfully"


def delete_account(code: str, cascade: bool = True) -> tuple[bool, str]:
    """
    Delete an account from the chart of accounts.
    If cascade=True, also delete all child accounts.
    Returns (success, message).
    """
    df = load_accounts_df()
    code = str(code).strip()
    
    if code not in df["code"].values:
        return False, f"Account '{code}' does not exist"
    
    if cascade:
        mask = df["code"].str.startswith(code)
        deleted_count = mask.sum()
        df = df[~mask]
        df.to_csv(ACCOUNTS_CSV, index=False)
        return True, f"Deleted account '{code}' and {deleted_count - 1} child account(s)"
    else:
        child_mask = df["code"].str.startswith(code + "0") | (df["code"].str.startswith(code) & (df["code"].str.len() > len(code)))
        has_children = child_mask.any()
        if has_children:
            return False, "Cannot delete account with child accounts. Use cascade=True or remove children first."
        df = df[df["code"] != code]
        df.to_csv(ACCOUNTS_CSV, index=False)
        return True, f"Account '{code}' deleted successfully"


def get_available_parents(level: int) -> list[tuple[str, str]]:
    """
    Return list of (code, name) for accounts that can be parents for a given level.
    Level 1: Main (no parent needed)
    Level 2: Group (parent is Main - code length 1)
    Level 3: Category (parent is Group - code length 2)
    Level 4: Account (parent is Category - code length 3)
    Level 9: Sub-account (parent is Account - code length 4)
    """
    df = load_accounts_df()
    parent_length = level - 1
    if parent_length == 0:
        return []
    parents = df[df["code"].str.len() == parent_length]
    return list(zip(parents["code"], parents["name"]))