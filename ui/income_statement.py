"""
Income Statement page UI.
"""

import plotly.graph_objects as go
import streamlit as st

from logic.reports import (
    compute_trial_balance,
    format_currency,
    get_income_statement_data,
)


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>💹 Income Statement</h1>
      <p>Company performance results for the period</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tb = compute_trial_balance()
    data = get_income_statement_data(tb)
    rev_df = data["rev_df"]
    exp_df = data["exp_df"]
    total_rev = data["total_rev"]
    total_exp = data["total_exp"]
    net = data["net_income"]

    # Revenue section
    st.markdown("### 💰 Revenues")
    if not rev_df.empty:
        # Using English column names from logic/reports.py
        rev_show = rev_df[["Code", "Account Name", "Balance"]].copy()
        rev_show["Balance"] = rev_show["Balance"].apply(format_currency)
        st.dataframe(rev_show, use_container_width=True, hide_index=True)
    st.markdown(f"**Total Revenues: {format_currency(total_rev)}**")

    st.markdown("---")

    # Expense section
    st.markdown("### 📉 Expenses")
    if not exp_df.empty:
        # Using English column names from logic/reports.py
        exp_show = exp_df[["Code", "Account Name", "Balance"]].copy()
        exp_show["Balance"] = exp_show["Balance"].apply(format_currency)
        st.dataframe(exp_show, use_container_width=True, hide_index=True)
    st.markdown(f"**Total Expenses: {format_currency(total_exp)}**")

    st.markdown("---")

    # Net Profit/Loss display
    if net >= 0:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg, #1e7e34, #28a745); 
                    color:white; padding:20px; border-radius:12px; text-align:center;'>
          <div style='font-size:16px;'>✅ Net Profit for the Period</div>
          <div style='font-size:36px; font-weight:700;'>{format_currency(net)}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg, #721c24, #dc3545); 
                    color:white; padding:20px; border-radius:12px; text-align:center;'>
          <div style='font-size:16px;'>❌ Net Loss for the Period</div>
          <div style='font-size:36px; font-weight:700;'>{format_currency(abs(net))}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Waterfall chart
    fig = go.Figure(
        go.Waterfall(
            name="Income Statement",
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["Revenues", "Expenses", "Net Profit"],
            y=[total_rev, -total_exp, 0],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "#28a745"}},
            decreasing={"marker": {"color": "#dc3545"}},
            totals={"marker": {"color": "#0f3460"}},
            texttemplate="%{y:,.0f}",
            textposition="outside",
        )
    )

    fig.update_layout(
        title="Income Statement Breakdown",
        showlegend=False,
        height=400,
        font=dict(family="Inter"),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
