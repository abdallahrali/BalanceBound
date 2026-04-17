"""
Balance Sheet page UI.
"""

import plotly.graph_objects as go
import streamlit as st

from logic.reports import (
    compute_trial_balance,
    format_currency,
    get_asset_breakdown,
    get_balance_sheet_data,
)


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>🏛️ Balance Sheet</h1>
      <p>Statement of the company's financial position</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tb = compute_trial_balance()
    data = get_balance_sheet_data(tb)
    assets_df = data["assets_df"]
    liab_df = data["liab_df"]
    net_income = data["net_income"]
    total_assets = data["total_assets"]
    total_liab = data["total_liab"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏦 Assets")
        if not assets_df.empty:
            a_show = assets_df[["Code", "Account Name"]].copy()
            # Calculating net balance for assets (Debit - Credit)
            a_show["Balance"] = (
                assets_df["Total - Debit"] - assets_df["Total - Credit"]
            ).apply(format_currency)
            st.dataframe(a_show, use_container_width=True, hide_index=True)
        st.markdown(
            f"""
        <div style='background:#0f3460; color:white; padding:12px 16px; 
                    border-radius:8px; font-weight:700; font-size:16px;'>
          Total Assets: {format_currency(total_assets)}
        </div>""",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("### ⚖️ Liabilities & Equity")
        if not liab_df.empty:
            l_show = liab_df[["Code", "Account Name"]].copy()
            # Calculating net balance for liabilities/equity (Credit - Debit)
            l_show["Balance"] = (
                liab_df["Total - Credit"] - liab_df["Total - Debit"]
            ).apply(format_currency)
            st.dataframe(l_show, use_container_width=True, hide_index=True)

        st.markdown(f"**Net Profit added to Equity:** {format_currency(net_income)}")
        st.markdown(
            f"""
        <div style='background:#155724; color:white; padding:12px 16px; 
                    border-radius:8px; font-weight:700; font-size:16px;'>
          Total Liabilities & Equity: {format_currency(total_liab)}
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    diff = total_assets - total_liab
    if abs(diff) < 1:
        st.success("✅ The balance sheet is balanced")
    else:
        st.warning(
            f"⚠️ Balance Sheet Difference: {format_currency(abs(diff))} — "
            "This may be due to default opening equity balances"
        )
