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


def parent_exists(code: str) -> bool:
    """Checks if the parent of the given code exists in the chart of accounts."""
    df = load_accounts_df()
    code_str = str(code)
    length = len(code_str)

    # Determine parent code based on length (1, 3, 6, 9)
    if length == 3:
        parent_code = code_str[0]  # Parent of Category is Type
    elif length == 6:
        parent_code = code_str[:3]  # Parent of Account is Category
    elif length == 9:
        parent_code = code_str[:6]  # Parent of Sub-account is Account
    else:
        return False

    return parent_code in df["code"].values


# def delete_account_cascade(code: str):
#     """Deletes an account and all children that start with the same code prefix."""
#     df = load_accounts_df()
#     # Remove any account whose code starts with the target code
#     # e.g., deleting '101' will also remove '101001' and '101001001'
#     new_df = df[~df["code"].astype(str).str.startswith(str(code))]

#     # Use the existing save function (it handles column renaming/filtering)
#     # We pass it as a display-ready DF because save_accounts_to_csv expects UI column names
#     new_df.rename(columns={"code": "Code", "name": "Account Name"}, inplace=True)
#     save_accounts_to_csv(new_df)


def get_parent_for_code(code: str):
    """Returns the code of the parent for a given account code."""
    c_len = len(str(code))
    if c_len == 3:
        return str(code)[0]  # Parent of Category is Type (1)
    if c_len == 6:
        return str(code)[:3]  # Parent of Account is Category (3)
    if c_len == 9:
        return str(code)[:6]  # Parent of Sub-account is Account (6)
    return None


def get_potential_parents(target_level: str) -> pd.DataFrame:
    """Returns all accounts that can be parents for the target level."""
    df = load_accounts_df()
    # Map target level to the required parent code length
    parent_lengths = {"Category": 1, "Account": 3, "Sub-account": 6}
    req_len = parent_lengths.get(target_level)

    if req_len is None:
        return pd.DataFrame(columns=["code", "name"])

    mask = df["code"].str.len() == req_len
    return df[mask].copy()


def generate_next_code(parent_code: str, target_level: str) -> str:
    """Generates the next available code under a parent."""
    df = load_accounts_df()
    children = df[df["code"].str.startswith(parent_code)].copy()

    # Filter for children exactly at the target level length
    target_len = {"Category": 3, "Account": 6, "Sub-account": 9}[target_level]
    target_children = children[children["code"].str.len() == target_len]

    if target_children.empty:
        # First child: Parent + '01' or '001'
        suffix = "01" if target_len == 3 else "001"
        return f"{parent_code}{suffix}"

    # Increment the last existing child
    last_code = target_children["code"].sort_values().iloc[-1]
    prefix = str(last_code)[:-2] if target_len == 3 else str(last_code)[:-3]
    last_num = int(str(last_code)[-2:]) if target_len == 3 else int(str(last_code)[-3:])

    new_num = str(last_num + 1).zfill(2 if target_len == 3 else 3)
    return f"{prefix}{new_num}"


def delete_account_cascade(code: str):
    """Deletes an account and all its children recursively."""
    df = load_accounts_df()
    # Keep only rows that do NOT start with the deleted code
    new_df = df[~df["code"].astype(str).str.startswith(str(code))].copy()

    # Save using logic-consistent columns (code, name)
    new_df.to_csv(ACCOUNTS_CSV, index=False)
