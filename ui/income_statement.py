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
      <h1>💹 قائمة الدخل</h1>
      <p>Income Statement — نتائج الأعمال للفترة</p>
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
    st.markdown("### 💰 الإيرادات")
    if not rev_df.empty:
        rev_show = rev_df[["الكود", "اسم الحساب", "الرصيد"]].copy()
        rev_show["الرصيد"] = rev_show["الرصيد"].apply(format_currency)
        st.dataframe(rev_show, use_container_width=True, hide_index=True)
    st.markdown(f"**إجمالي الإيرادات: {format_currency(total_rev)}**")

    st.markdown("---")

    # Expense section
    st.markdown("### 📉 المصروفات")
    if not exp_df.empty:
        exp_show = exp_df[["الكود", "اسم الحساب", "الرصيد"]].copy()
        exp_show["الرصيد"] = exp_show["الرصيد"].apply(format_currency)
        st.dataframe(exp_show, use_container_width=True, hide_index=True)
    st.markdown(f"**إجمالي المصروفات: {format_currency(total_exp)}**")

    st.markdown("---")

    # Net result banner
    if net >= 0:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg,#155724,#28a745);
                    color:white; padding:20px; border-radius:12px; text-align:center;'>
          <div style='font-size:16px;'>✅ صافي الربح للفترة</div>
          <div style='font-size:36px; font-weight:700;'>{format_currency(net)}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
        <div style='background: linear-gradient(135deg,#721c24,#dc3545);
                    color:white; padding:20px; border-radius:12px; text-align:center;'>
          <div style='font-size:16px;'>❌ صافي الخسارة للفترة</div>
          <div style='font-size:36px; font-weight:700;'>{format_currency(abs(net))}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Waterfall chart
    fig = go.Figure(
        go.Waterfall(
            name="قائمة الدخل",
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["الإيرادات", "المصروفات", "صافي الربح"],
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
        title="",
        height=350,
        font=dict(family="Cairo"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
