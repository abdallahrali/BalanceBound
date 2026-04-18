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

    # ===================== Revenue Section =====================
    st.markdown("### 💰 Revenues")
    if not rev_df.empty:
        rev_show = rev_df[["Code", "Account Name", "Balance"]].copy()

        # ✅ تنسيق الصفوف: الحسابات الأب بخط Bold والـ Leaf عادي
        rev_codes = rev_df["Code"].tolist()
        rev_show["_is_leaf"] = rev_df["Code"].apply(
            lambda c: not any(
                other != c and other.startswith(c) for other in rev_codes
            )
        )

        rev_show["Balance"] = rev_show["Balance"].apply(format_currency)
        # عرض الجدول بدون عمود _is_leaf
        st.dataframe(
            rev_show[["Code", "Account Name", "Balance"]],
            use_container_width=True,
            hide_index=True,
        )
    st.markdown(f"**Total Revenues: {format_currency(total_rev)}**")

    st.markdown("---")

    # ===================== Expense Section =====================
    st.markdown("### 📉 Expenses")
    if not exp_df.empty:
        exp_show = exp_df[["Code", "Account Name", "Balance"]].copy()
        exp_show["Balance"] = exp_show["Balance"].apply(format_currency)
        st.dataframe(
            exp_show[["Code", "Account Name", "Balance"]],
            use_container_width=True,
            hide_index=True,
        )
    st.markdown(f"**Total Expenses: {format_currency(total_exp)}**")

    st.markdown("---")

    # ===================== Net Profit / Loss =====================
    if net >= 0:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg, #1e7e34, #28a745); 
                    color:white; padding:20px; border-radius:12px; text-align:center;
                    margin-bottom: 20px;'>
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
                    color:white; padding:20px; border-radius:12px; text-align:center;
                    margin-bottom: 20px;'>
          <div style='font-size:16px;'>❌ Net Loss for the Period</div>
          <div style='font-size:36px; font-weight:700;'>{format_currency(abs(net))}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ===================== Bar Chart (بدل Waterfall) =====================
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="Revenues",
        x=["Revenues"],
        y=[total_rev],
        marker_color="#28a745",
        text=[f"{total_rev:,.0f}"],
        textposition="outside",
    ))

    fig.add_trace(go.Bar(
        name="Expenses",
        x=["Expenses"],
        y=[total_exp],
        marker_color="#dc3545",
        text=[f"{total_exp:,.0f}"],
        textposition="outside",
    ))

    fig.add_trace(go.Bar(
        name="Net Profit" if net >= 0 else "Net Loss",
        x=["Net Profit/Loss"],
        y=[abs(net)],
        marker_color="#0f3460" if net >= 0 else "#ff6b6b",
        text=[f"{net:,.0f}"],
        textposition="outside",
    ))

    fig.update_layout(
        title="Income Statement Breakdown",
        showlegend=True,
        height=450,
        font=dict(family="Inter"),
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis=dict(title="Amount", tickformat=","),
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)