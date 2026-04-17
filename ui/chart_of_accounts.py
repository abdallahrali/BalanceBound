"""
Chart of Accounts page UI.
"""

import streamlit as st

from logic.accounts import build_accounts_display_df


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>📖 Chart of Accounts</h1>
      <p>Full guide of all accounts and their classifications</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "🔍 Search for an account (by name or code)", placeholder="Search here..."
    )

    # Returns DF with columns: "Code", "Account Name", "Type", "Level"
    df = build_accounts_display_df()

    if search:
        mask = df["Account Name"].str.contains(search, case=False, na=False) | df[
            "Code"
        ].astype(str).str.contains(search)
        df = df[mask]

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🏦 Assets",
            "⚖️ Liabilities & Equity",
            "📉 Expenses",
            "💰 Revenues",
        ]
    )

    # Must match values returned by get_account_type_label in logic/accounts.py
    type_labels = ["Asset", "Liability/Equity", "Expense", "Revenue"]
    tabs = [tab1, tab2, tab3, tab4]

    for tab, type_label in zip(tabs, type_labels):
        with tab:
            subset = df[df["Type"] == type_label][["Code", "Account Name", "Level"]]
            st.dataframe(subset, use_container_width=True, hide_index=True, height=500)
