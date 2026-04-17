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
    get_asset_breakdown,
    get_income_statement_data,
)


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>🏠 Main Dashboard</h1>
      <p>Overview of the company's financial status</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tb = compute_trial_balance()
    is_data = get_income_statement_data(tb)
    revenues = is_data["total_rev"]
    expenses = is_data["total_exp"]
    net_income = is_data["net_income"]

    # Use the English column names established in logic/reports.py
    assets = tb[tb["Account Type"] == "Asset"]
    total_assets = (assets["Total - Debit"] - assets["Total - Credit"]).sum()
    total_journals = len(get_all_entries())

    # ── KPI Cards ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""<div class='metric-card'>
            <div class='value'>{format_currency(revenues)}</div>
            <div class='label'>💰 Total Revenues</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class='metric-card'>
            <div class='value'>{format_currency(expenses)}</div>
            <div class='label'>💸 Total Expenses</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class='metric-card'>
            <div class='value'>{format_currency(net_income)}</div>
            <div class='label'>📈 Net Income</div>
        </div>""",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""<div class='metric-card'>
            <div class='value'>{format_currency(total_assets)}</div>
            <div class='label'>🏦 Total Assets</div>
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Section ──
    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown(
            "<div class='section-title'>📊 Asset Analysis</div>",
            unsafe_allow_html=True,
        )
        labels, values = get_asset_breakdown(assets)
        if sum(values) > 0:
            fig1 = px.pie(
                values=values,
                names=labels,
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig1.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
                ),
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No asset data available for analysis.")

    with right_col:
        st.markdown(
            "<div class='section-title'>📝 Latest Journal Entries</div>",
            unsafe_allow_html=True,
        )
        entries = get_all_entries()
        if not entries:
            st.write("No entries recorded yet.")
        else:
            # Show last 3 entries
            for entry in entries[-3:][::-1]:
                total = sum(l["dr"] for l in entry["lines"])
                lines_html = "".join(
                    f"<div class='je-line'><span>{l['name']}</span>"
                    f"<span class='{'dr' if l['dr']>0 else 'cr'}'>"
                    f"{format_currency(l['dr'] if l['dr']>0 else l['cr'])}</span></div>"
                    for l in entry["lines"]
                )
                st.markdown(
                    f"""
                <div class='journal-card'>
                  <div class='je-header'>
                    Entry No. {entry['journal_no']} — {entry['date']}
                    | {entry.get('explanation', '')}
                  </div>
                  {lines_html}
                  <div style='text-align:right; font-size:12px; color:#888; margin-top:8px;'>
                    Total: {format_currency(total)}
                  </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # ── Bar chart ──
    st.markdown(
        "<div class='section-title'>📈 Revenue vs Expenses Comparison</div>",
        unsafe_allow_html=True,
    )
    fig2 = go.Figure(
        data=[
            go.Bar(
                name="Revenues", x=["Revenues"], y=[revenues], marker_color="#28a745"
            ),
            go.Bar(
                name="Expenses", x=["Expenses"], y=[expenses], marker_color="#dc3545"
            ),
            go.Bar(
                name="Net Income",
                x=["Net Income"],
                y=[max(net_income, 0)],
                marker_color="#0f3460",
            ),
        ]
    )
    fig2.update_layout(
        barmode="group",
        height=280,
        font=dict(family="Inter"),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig2, use_container_width=True)
