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
        lambda c: not any(
            other != c and other.startswith(c) for other in codes
        )
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
    Break down assets into categories for charting.
    Uses only leaf accounts to avoid double counting.
    """
    leaf_mask = _get_leaf_mask(assets_df)
    leaf_assets = assets_df[leaf_mask].copy()

    codes = leaf_assets["Code"].astype(str)

    def _net(mask):
        return (
            leaf_assets.loc[mask, "Total - Debit"]
            - leaf_assets.loc[mask, "Total - Credit"]
        ).sum()

    labels = [
        "Fixed Assets",
        "Banks & Cash",
        "Inventory",
        "Accounts Receivable",
        "Other",
    ]
    values = [
        _net(codes.str.startswith("101")),
        _net(codes.str.startswith("102")),
        _net(codes.str.startswith("105")),
        _net(codes.str.startswith("103")),
        _net(~codes.str.startswith(("101", "102", "103", "105"))),
    ]
    return labels, values