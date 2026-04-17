"""
Dashboard page UI.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from logic.journal import get_all_entries
from logic.reports import (
    compute_trial_balance,
    format_currency,
    get_income_statement_data,
)


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>🏠 لوحة التحكم الرئيسية</h1>
      <p>نظرة عامة على الوضع المالي للشركة</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tb = compute_trial_balance()
    is_data = get_income_statement_data(tb)
    revenues = is_data["total_rev"]
    expenses = is_data["total_exp"]
    net_income = is_data["net_income"]

    assets = tb[tb["نوع الحساب"] == "Asset"]
    total_assets = (
        assets["ميزان المجاميع - مدين"] - assets["ميزان المجاميع - دائن"]
    ).sum()
    total_journals = len(get_all_entries())

    # ── KPI Cards ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""<div class='metric-card'>
            <div class='value'>{format_currency(revenues)}</div>
            <div class='label'>💰 إجمالي الإيرادات</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class='metric-card'>
            <div class='value'>{format_currency(expenses)}</div>
            <div class='label'>📉 إجمالي المصروفات</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        color = "#28a745" if net_income >= 0 else "#dc3545"
        label = "📈 صافي الربح" if net_income >= 0 else "📉 صافي الخسارة"
        st.markdown(
            f"""<div class='metric-card'>
            <div class='value' style='color:{color};'>{format_currency(abs(net_income))}</div>
            <div class='label'>{label}</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""<div class='metric-card'>
            <div class='value'>{total_journals}</div>
            <div class='label'>📝 إجمالي القيود</div>
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Two-column layout ──
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            "<div class='section-title'>📊 توزيع المصروفات</div>",
            unsafe_allow_html=True,
        )
        exp_df = tb[tb["نوع الحساب"] == "Expense"][["اسم الحساب", "الرصيد"]].copy()
        exp_df = exp_df[exp_df["الرصيد"] > 0].sort_values("الرصيد", ascending=False)
        if not exp_df.empty:
            fig = px.pie(
                exp_df,
                values="الرصيد",
                names="اسم الحساب",
                color_discrete_sequence=px.colors.sequential.RdBu,
                hole=0.4,
            )
            fig.update_layout(
                showlegend=True,
                height=350,
                legend=dict(font=dict(family="Cairo")),
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد مصروفات مسجلة حتى الآن.")

    with col_right:
        st.markdown(
            "<div class='section-title'>📋 آخر القيود اليومية</div>",
            unsafe_allow_html=True,
        )
        entries = get_all_entries()
        for entry in reversed(entries[-5:]):
            total = sum(l["dr"] for l in entry["lines"])
            lines_html = "".join(
                f"<div class='je-row'>"
                f"<span>{l['name']}</span>"
                f"<span class='dr-amount'>{format_currency(l['dr'])} م</span>"
                f"<span class='cr-amount'>{format_currency(l['cr'])} د</span>"
                f"</div>"
                for l in entry["lines"]
            )
            st.markdown(
                f"""
            <div class='journal-card'>
              <div class='je-header'>
                قيد رقم {entry['journal_no']} — {entry['date']}
                | {entry.get('explanation', '')}
              </div>
              {lines_html}
              <div style='text-align:left; font-size:12px; color:#888; margin-top:8px;'>
                الإجمالي: {format_currency(total)}
              </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # ── Bar chart ──
    st.markdown(
        "<div class='section-title'>📈 مقارنة الإيرادات والمصروفات</div>",
        unsafe_allow_html=True,
    )
    fig2 = go.Figure(
        data=[
            go.Bar(
                name="الإيرادات", x=["الإيرادات"], y=[revenues], marker_color="#28a745"
            ),
            go.Bar(
                name="المصروفات", x=["المصروفات"], y=[expenses], marker_color="#dc3545"
            ),
            go.Bar(
                name="صافي الربح",
                x=["صافي الربح"],
                y=[max(net_income, 0)],
                marker_color="#0f3460",
            ),
        ]
    )
    fig2.update_layout(
        barmode="group",
        height=280,
        font=dict(family="Cairo"),
        margin=dict(t=20, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)
