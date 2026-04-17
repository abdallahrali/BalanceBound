"""
Financial reporting logic: trial balance, income statement, balance sheet.
"""

import pandas as pd
import streamlit as st

from logic.accounts import get_account_type, get_accounts_dict


def format_currency(val: float) -> str:
    """Format a number for display; zero shows as dash."""
    if val == 0:
        return "-"
    return f"{val:,.0f}"


def compute_trial_balance() -> pd.DataFrame:
    """
    Compute trial balance from opening balances + journal entries.
    Returns a DataFrame with all balance columns.
    """
    accounts = get_accounts_dict()
    balances: dict[str, dict] = {}

    # Opening balances
    for code, bal in st.session_state.opening_balances.items():
        balances[code] = {
            "ob_dr": bal["dr"],
            "ob_cr": bal["cr"],
            "mv_dr": 0,
            "mv_cr": 0,
        }

    # Movement from entries
    for entry in st.session_state.entries:
        for line in entry["lines"]:
            code = line["code"]
            if code not in balances:
                balances[code] = {"ob_dr": 0, "ob_cr": 0, "mv_dr": 0, "mv_cr": 0}
            balances[code]["mv_dr"] += line["dr"]
            balances[code]["mv_cr"] += line["cr"]

    rows = []
    for code, b in balances.items():
        tb_dr = b["ob_dr"] + b["mv_dr"]
        tb_cr = b["ob_cr"] + b["mv_cr"]
        bal = tb_dr - tb_cr
        rows.append(
            {
                "Code": code,
                "Account Name": accounts.get(code, code),
                "Opening Balance - Debit": b["ob_dr"],
                "Opening Balance - Credit": b["ob_cr"],
                "Movement - Debit": b["mv_dr"],
                "Movement - Credit": b["mv_cr"],
                "Total - Debit": tb_dr,
                "Total - Credit": tb_cr,
                "Balance": abs(bal),
                "Balance Type": "Debit" if bal >= 0 else "Credit",
                "Account Type": get_account_type(code),
            }
        )
    return pd.DataFrame(rows)


def get_income_statement_data(tb: pd.DataFrame) -> dict:
    """
    Extract income statement figures from a trial balance DataFrame.
    Returns dict with revenue_df, expense_df, total_rev, total_exp, net_income.
    """
    rev_df = tb[tb["Account Type"] == "Revenue"].copy()
    exp_df = tb[tb["Account Type"] == "Expense"].copy()
    total_rev = rev_df["Balance"].sum()
    total_exp = exp_df["Balance"].sum()
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
    Returns dict with assets_df, liab_df, net_income, total_assets, total_liab.
    """
    assets_df = tb[tb["Account Type"] == "Asset"].copy()
    liab_df = tb[tb["Account Type"] == "Liability/Equity"].copy()
    rev_df = tb[tb["Account Type"] == "Revenue"]
    exp_df = tb[tb["Account Type"] == "Expense"]

    net_income = rev_df["Balance"].sum() - exp_df["Balance"].sum()
    total_assets = (assets_df["Total - Debit"] - assets_df["Total - Credit"]).sum()
    total_liab = (
        liab_df["Total - Credit"] - liab_df["Total - Debit"]
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
    Returns (labels, values).
    """
    codes = assets_df["Code"].astype(str)

    def _net(mask):
        return (
            assets_df.loc[mask, "Total - Debit"] - assets_df.loc[mask, "Total - Credit"]
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
