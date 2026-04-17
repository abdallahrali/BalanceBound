"""
Trial Balance page UI.
"""

import io

import streamlit as st

from logic.reports import compute_trial_balance, format_currency


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>⚖️ Trial Balance</h1>
      <p>View balances for all accounts across different periods</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tb = compute_trial_balance()

    if tb.empty:
        st.info("No data to display. Please add journal entries first.")
        return

    # Summary metrics
    total_ob_dr = tb["Opening Balance - Debit"].sum()
    total_mv_dr = tb["Movement - Debit"].sum()
    total_tb_dr = tb["Total - Debit"].sum()
    total_tb_cr = tb["Total - Credit"].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Opening Balance (Debit)", format_currency(total_ob_dr))
    c2.metric("Total Movement (Debit)", format_currency(total_mv_dr))
    c3.metric("Trial Balance Total (Debit)", format_currency(total_tb_dr))

    is_balanced = abs(total_tb_dr - total_tb_cr) < 0.01
    if is_balanced:
        st.success("✅ The trial balance is balanced")
    else:
        st.error(
            f"❌ The trial balance is not balanced — Difference: "
            f"{format_currency(abs(total_tb_dr - total_tb_cr))}"
        )

    st.markdown("---")

    # Display table
    display_cols = [
        "Opening Balance - Debit",
        "Opening Balance - Credit",
        "Movement - Debit",
        "Movement - Credit",
        "Total - Debit",
        "Total - Credit",
        "Balance",
    ]

    display_tb = tb.copy()
    for col in display_cols:
        display_tb[col] = display_tb[col].apply(format_currency)

    st.dataframe(
        display_tb[
            [
                "Code",
                "Account Name",
                "Account Type",
                *display_cols,
                "Balance Type",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=600,
    )
