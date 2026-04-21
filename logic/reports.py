"""
Financial reporting logic: trial balance, income statement, balance sheet.
"""

import pandas as pd
import streamlit as st

from logic.accounts import get_account_type, get_accounts_dict


def format_currency(val: float) -> str:
    """Format a number for display; zero shows as dash, negatives in parentheses."""
    if val == 0:
        return "-"
    elif val < 0:
        return f"({abs(val):,.0f})"
    return f"{val:,.0f}"


def _get_leaf_mask(df: pd.DataFrame) -> pd.Series:
    """
    Returns a boolean mask that is True only for leaf accounts
    (accounts that have no children in the same DataFrame).
    """
    codes = df["Code"].tolist()
    return df["Code"].apply(
        lambda c: not any(other != c and other.startswith(c) for other in codes)
    )


def compute_trial_balance() -> pd.DataFrame:
    """
    Compute trial balance with hierarchical roll-up.
    Returns a DataFrame with all balance columns.
    """
    accounts = get_accounts_dict()
    balances: dict[str, dict] = {}

    # Initialize ALL accounts in the dictionary
    for code in accounts.keys():
        balances[code] = {"ob_dr": 0, "ob_cr": 0, "mv_dr": 0, "mv_cr": 0}

    # 1. Opening balances (Leaf levels)
    for code, bal in st.session_state.opening_balances.items():
        if code not in balances:
            balances[code] = {"ob_dr": 0, "ob_cr": 0, "mv_dr": 0, "mv_cr": 0}
        balances[code]["ob_dr"] += bal["dr"]
        balances[code]["ob_cr"] += bal["cr"]

    # 2. Movement from entries (Leaf levels)
    for entry in st.session_state.entries:
        for line in entry["lines"]:
            code = line["code"]
            if code not in balances:
                balances[code] = {"ob_dr": 0, "ob_cr": 0, "mv_dr": 0, "mv_cr": 0}
            balances[code]["mv_dr"] += line["dr"]
            balances[code]["mv_cr"] += line["cr"]

    # 3. Hierarchical Roll-up (Bottom-up)
    # Sort codes by length descending so children (len 9) roll up to parents (len 6, 3, 1)
    sorted_codes = sorted(list(balances.keys()), key=len, reverse=True)
    for code in sorted_codes:
        parent_code = None
        # Determine parent based on specific code lengths in accounts.csv
        if len(code) == 9:
            parent_code = code[:6]
        elif len(code) == 6:
            parent_code = code[:3]
        elif len(code) == 3:
            parent_code = code[:1]

        if parent_code and parent_code in balances:
            balances[parent_code]["ob_dr"] += balances[code]["ob_dr"]
            balances[parent_code]["ob_cr"] += balances[code]["ob_cr"]
            balances[parent_code]["mv_dr"] += balances[code]["mv_dr"]
            balances[parent_code]["mv_cr"] += balances[code]["mv_cr"]

    rows = []
    # Sort ascending for Top-Down display in the UI
    for code in sorted(list(balances.keys())):
        b = balances[code]
        tb_dr = b["ob_dr"] + b["mv_dr"]
        tb_cr = b["ob_cr"] + b["mv_cr"]
        bal = tb_dr - tb_cr

        # Only display accounts that have activity or balances
        if tb_dr == 0 and tb_cr == 0 and b["ob_dr"] == 0 and b["ob_cr"] == 0:
            continue

        # Add visual indentation based on account level
        indent = ""
        if len(code) == 3:
            indent = "   "
        elif len(code) == 6:
            indent = "      "
        elif len(code) == 9:
            indent = "         "

        rows.append(
            {
                "Code": code,
                "Account Name": indent + accounts.get(code, code),
                "Opening Balance - Debit": b["ob_dr"],
                "Opening Balance - Credit": b["ob_cr"],
                "Movement - Debit": b["mv_dr"],
                "Movement - Credit": b["mv_cr"],
                "Total - Debit": tb_dr,
                "Total - Credit": tb_cr,
                "Balance": abs(bal),
                "Balance Type": "Debit" if bal >= 0 else "Credit",
                "Account Type": get_account_type(code),
                "Level": len(code),
            }
        )
    return pd.DataFrame(rows)


def count_accounts() -> pd.DataFrame:
    """
    Compute trial balance with hierarchical roll-up.
    Returns a DataFrame with all balance columns.
    """
    accounts = get_accounts_dict()
    balances: dict[str, dict] = {}

    # Initialize ALL accounts in the dictionary
    for code in accounts.keys():
        balances[code] = {"ob_dr": 0, "ob_cr": 0, "mv_dr": 0, "mv_cr": 0}

    # 3. Hierarchical Roll-up (Bottom-up)
    # Sort codes by length descending so children (len 9) roll up to parents (len 6, 3, 1)
    sorted_codes = sorted(list(balances.keys()), key=len, reverse=True)
    for code in sorted_codes:
        parent_code = None
        # Determine parent based on specific code lengths in accounts.csv
        if len(code) == 9:
            parent_code = code[:6]
        elif len(code) == 6:
            parent_code = code[:3]
        elif len(code) == 3:
            parent_code = code[:1]

    rows = []
    # Sort ascending for Top-Down display in the UI
    for code in sorted(list(balances.keys())):

        # Add visual indentation based on account level
        indent = ""
        if len(code) == 3:
            indent = "   "
        elif len(code) == 6:
            indent = "      "
        elif len(code) == 9:
            indent = "         "

        rows.append(
            {
                "Code": code,
                "Account Name": indent + accounts.get(code, code),
                "Account Type": get_account_type(code),
                "Level": len(code),
            }
        )
    return pd.DataFrame(rows)


def get_income_statement_data(tb: pd.DataFrame) -> dict:
    """
    Extract income statement figures from a trial balance DataFrame.
    Uses only leaf accounts to avoid double counting.
    """
    rev_df = tb[tb["Account Type"] == "Revenue"].copy()
    exp_df = tb[tb["Account Type"] == "Expense"].copy()

    rev_leaf_mask = _get_leaf_mask(rev_df)
    exp_leaf_mask = _get_leaf_mask(exp_df)

    total_rev = rev_df.loc[rev_leaf_mask, "Balance"].sum()
    total_exp = exp_df.loc[exp_leaf_mask, "Balance"].sum()
    net_income = total_rev - total_exp

    return {
        "rev_df": rev_df,
        "exp_df": exp_df,
        "total_rev": total_rev,
        "total_exp": total_exp,
        "net_income": net_income,
    }


def get_balance_sheet_data(tb: pd.DataFrame) -> dict:
    """
    Extract balance sheet figures from a trial balance DataFrame.
    Uses only leaf accounts to avoid double counting.
    """
    assets_df = tb[tb["Account Type"] == "Asset"].copy()
    liab_df = tb[tb["Account Type"] == "Liability/Equity"].copy()
    rev_df = tb[tb["Account Type"] == "Revenue"]
    exp_df = tb[tb["Account Type"] == "Expense"]

    # Net income from leaf accounts only
    rev_leaf_mask = _get_leaf_mask(rev_df)
    exp_leaf_mask = _get_leaf_mask(exp_df)
    net_income = (
        rev_df.loc[rev_leaf_mask, "Balance"].sum()
        - exp_df.loc[exp_leaf_mask, "Balance"].sum()
    )

    # Assets & Liabilities from leaf accounts only
    assets_leaf_mask = _get_leaf_mask(assets_df)
    liab_leaf_mask = _get_leaf_mask(liab_df)

    total_assets = (
        assets_df.loc[assets_leaf_mask, "Total - Debit"]
        - assets_df.loc[assets_leaf_mask, "Total - Credit"]
    ).sum()

    total_liab = (
        liab_df.loc[liab_leaf_mask, "Total - Credit"]
        - liab_df.loc[liab_leaf_mask, "Total - Debit"]
    ).sum() + net_income

    return {
        "assets_df": assets_df,
        "liab_df": liab_df,
        "net_income": net_income,
        "total_assets": total_assets,
        "total_liab": total_liab,
    }


def get_asset_breakdown(assets_df: pd.DataFrame) -> tuple[list[str], list[float]]:
    """
    Break down assets into their dynamic categories for charting.
    Uses leaf accounts to calculate values, grouped by their 3-digit category parent.
    """
    # 1. Create a mapping of 3-digit Category Codes to their actual Account Names
    # e.g., {"101": "Fixed Assets", "102": "Banks & Cash"}
    category_rows = assets_df[assets_df["Code"].str.len() == 3]
    category_map = dict(zip(category_rows["Code"], category_rows["Account Name"]))

    # 2. Get only the leaf accounts to calculate actual balances without double counting
    leaf_mask = _get_leaf_mask(assets_df)
    leaf_assets = assets_df[leaf_mask].copy()

    # 3. Calculate net balance (Debit - Credit for Assets)
    leaf_assets["Net_Balance"] = (
        leaf_assets["Total - Debit"] - leaf_assets["Total - Credit"]
    )

    # 4. Find the 3-digit parent category code for every leaf account
    leaf_assets["Category_Code"] = leaf_assets["Code"].astype(str).str[:3]

    # 5. Group the net balances by these category codes
    grouped_assets = leaf_assets.groupby("Category_Code")["Net_Balance"].sum()

    labels = []
    values = []

    # 6. Build the final lists, converting codes to their proper names
    for cat_code, total in grouped_assets.items():
        if total > 0:  # Only include categories that actually have a positive balance
            # Get the real name from our map, fallback to just the code if not found
            cat_name = category_map.get(cat_code, f"Category {cat_code}")
            labels.append(cat_name)
            values.append(total)

    return labels, values


def get_liab_breakdown(liab_df: pd.DataFrame) -> tuple[list[str], list[float]]:
    """
    Break down liabilities and equity into their dynamic categories for charting.
    Uses leaf accounts to calculate values, grouped by their 3-digit category parent.
    """
    # Map 3-digit Category Codes to their Account Names
    category_rows = liab_df[liab_df["Code"].str.len() == 3]
    category_map = dict(zip(category_rows["Code"], category_rows["Account Name"]))

    # Get only the leaf accounts to avoid double counting
    leaf_mask = _get_leaf_mask(liab_df)
    leaf_liab = liab_df[leaf_mask].copy()

    # Net balance for liabilities/equity is Total Credit - Total Debit
    leaf_liab["Net_Balance"] = leaf_liab["Total - Credit"] - leaf_liab["Total - Debit"]
    leaf_liab["Category_Code"] = leaf_liab["Code"].astype(str).str[:3]

    # Group by category code
    grouped_liab = leaf_liab.groupby("Category_Code")["Net_Balance"].sum()

    labels = []
    values = []

    for cat_code, total in grouped_liab.items():
        if total > 0:  # Only chart categories with a positive balance
            cat_name = category_map.get(cat_code, f"Category {cat_code}")
            labels.append(cat_name)
            values.append(total)

    return labels, values
