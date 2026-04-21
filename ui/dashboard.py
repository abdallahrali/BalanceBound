"""
Dashboard page UI — Premium financial overview.
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from logic.journal import get_all_entries
from logic.reports import (
    compute_trial_balance,
    count_accounts,
    format_currency,
    get_asset_breakdown,
    get_income_statement_data,
    get_liab_breakdown,
)


def render():
    # ── Page Header ──
    st.markdown(
        """
    <div class="page-header">
      <div>
        <div class="ph-label">Overview</div>
        <h1>Financial Dashboard</h1>
        <p>Real-time snapshot of your company's financial position</p>
      </div>
      <div class="ph-icon">🏠</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    num_of_accounts = count_accounts()
    tb = compute_trial_balance()
    is_data = get_income_statement_data(tb)
    revenues = is_data["total_rev"]
    expenses = is_data["total_exp"]
    net_income = is_data["net_income"]

    asset_root = tb[tb["Code"] == "1"]
    total_assets = (asset_root["Total - Debit"] - asset_root["Total - Credit"]).sum()

    assets = tb[tb["Account Type"] == "Asset"]
    liabilities = tb[tb["Account Type"] == "Liability/Equity"]
    total_journals = len(get_all_entries())

    net_color = "green" if net_income >= 0 else "red"

    # ── Main Financial KPI Cards ──
    st.markdown(
        '<div class="section-header" style="margin-top: 2rem;"><span class="sh-title">Financial Statistics</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="kpi-grid">
      <div class="kpi-card gold">
        <div class="kpi-label">Total Revenues</div>
        <div class="kpi-value">{format_currency(revenues)}</div>
        <div class="kpi-sub">Period earnings</div>
        <div class="kpi-accent"></div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-label">Total Expenses</div>
        <div class="kpi-value">{format_currency(expenses)}</div>
        <div class="kpi-sub">Period spending</div>
        <div class="kpi-accent"></div>
      </div>
      <div class="kpi-card {net_color}">
        <div class="kpi-label">Net Income</div>
        <div class="kpi-value">{format_currency(net_income)}</div>
        <div class="kpi-sub">{"Profit" if net_income >= 0 else "Loss"} for period</div>
        <div class="kpi-accent"></div>
      </div>
      <div class="kpi-card blue">
        <div class="kpi-label">Total Assets</div>
        <div class="kpi-value">{format_currency(total_assets)}</div>
        <div class="kpi-sub">{total_journals} journal entries</div>
        <div class="kpi-accent"></div>
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── Chart of Accounts Structure (NEW SECTION) ──
    st.markdown(
        '<div class="section-header" style="margin-top: 2rem;"><span class="sh-title">Active Accounts Statistics</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    # State initialization for toggle buttons
    if "dashboard_acct_level" not in st.session_state:
        st.session_state.dashboard_acct_level = "Sub-accounts"

    # Button group (acts like a radio button without the radio circle)
    bc1, bc2, bc3, _ = st.columns([1, 1, 1, 4])
    with bc1:
        if st.button(
            "Categories",
            type=(
                "primary"
                if st.session_state.dashboard_acct_level == "Categories"
                else "secondary"
            ),
            use_container_width=True,
        ):
            st.session_state.dashboard_acct_level = "Categories"
            st.rerun()
    with bc2:
        if st.button(
            "Accounts",
            type=(
                "primary"
                if st.session_state.dashboard_acct_level == "Accounts"
                else "secondary"
            ),
            use_container_width=True,
        ):
            st.session_state.dashboard_acct_level = "Accounts"
            st.rerun()
    with bc3:
        if st.button(
            "Sub-accounts",
            type=(
                "primary"
                if st.session_state.dashboard_acct_level == "Sub-accounts"
                else "secondary"
            ),
            use_container_width=True,
        ):
            st.session_state.dashboard_acct_level = "Sub-accounts"
            st.rerun()

    # Calculate account quantities based on selection length
    len_map = {"Categories": 3, "Accounts": 6, "Sub-accounts": 9}
    target_len = len_map[st.session_state.dashboard_acct_level]

    # Filter by code length to match the specific level, then count by their primary root digit
    df_level = num_of_accounts[num_of_accounts["Code"].str.len() == target_len]
    first_digits = df_level["Code"].astype(str).str[0]

    c_assets = sum(first_digits == "1")
    c_liab = sum(first_digits == "2")
    c_rev = sum(first_digits == "3")
    c_exp = sum(first_digits == "4")

    # Render smaller structural KPI Cards
    st.markdown(
        f"""
        <div class="kpi-grid" style="margin-top: 15px; margin-bottom: 2rem;">
          <div class="kpi-card gold" style="padding: 15px;">
            <div class="kpi-label">Assets</div>
            <div class="kpi-value" style="font-size: 1.8rem;">{c_assets}</div>
            <div class="kpi-accent"></div>
          </div>
          <div class="kpi-card blue" style="padding: 15px;">
            <div class="kpi-label">Liab & Equity</div>
            <div class="kpi-value" style="font-size: 1.8rem;">{c_liab}</div>
            <div class="kpi-accent"></div>
          </div>
          <div class="kpi-card green" style="padding: 15px;">
            <div class="kpi-label">Revenues</div>
            <div class="kpi-value" style="font-size: 1.8rem;">{c_rev}</div>
            <div class="kpi-accent"></div>
          </div>
          <div class="kpi-card red" style="padding: 15px;">
            <div class="kpi-label">Expenses</div>
            <div class="kpi-value" style="font-size: 1.8rem;">{c_exp}</div>
            <div class="kpi-accent"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Charts Row ──
    left_col, right_col = st.columns([1, 1])

    PLOT_LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#8A8FA8", size=12),
        margin=dict(l=0, r=0, t=20, b=0),
        height=300,
    )

    with left_col:
        # ── ASSETS BREAKDOWN CHART ──
        st.markdown(
            '<div class="section-header"><span class="sh-title">Asset Breakdown</span>'
            '<div class="sh-divider"></div></div>',
            unsafe_allow_html=True,
        )
        labels, values = get_asset_breakdown(assets)
        if sum(values) > 0:
            fig1 = px.pie(
                values=values,
                names=labels,
                hole=0.55,
                color_discrete_sequence=[
                    "#D4AF37",
                    "#3B82F6",
                    "#22C55E",
                    "#EF4444",
                    "#8B5CF6",
                ],
            )
            fig1.update_traces(
                textfont_size=12,
                marker=dict(line=dict(color="#0D0F14", width=2)),
            )
            fig1.update_layout(
                **PLOT_LAYOUT,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.25,
                    xanchor="center",
                    x=0.5,
                    font=dict(color="#8A8FA8", size=11),
                ),
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.markdown(
                '<div class="alert info"><span class="alert-icon">ℹ️</span>'
                "No asset data available yet. Add journal entries to see the breakdown.</div>",
                unsafe_allow_html=True,
            )

        # ── LIABILITIES BREAKDOWN CHART ──
        st.markdown(
            '<div class="section-header" style="margin-top: 2rem;"><span class="sh-title">Liabilities & Equity Breakdown</span>'
            '<div class="sh-divider"></div></div>',
            unsafe_allow_html=True,
        )

        l_labels, l_values = get_liab_breakdown(liabilities)

        if sum(l_values) > 0:
            fig2 = px.pie(
                values=l_values,
                names=l_labels,
                hole=0.55,
                color_discrete_sequence=[
                    "#F59E0B",  # Amber
                    "#EC4899",  # Pink
                    "#8B5CF6",  # Purple
                    "#06B6D4",  # Cyan
                    "#64748B",  # Slate
                ],
            )
            fig2.update_traces(
                textfont_size=12,
                marker=dict(line=dict(color="#0D0F14", width=2)),
            )
            fig2.update_layout(
                **PLOT_LAYOUT,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.25,
                    xanchor="center",
                    x=0.5,
                    font=dict(color="#8A8FA8", size=11),
                ),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.markdown(
                '<div class="alert info"><span class="alert-icon">ℹ️</span>'
                "No liabilities or equity data available yet. Add journal entries to see the breakdown.</div>",
                unsafe_allow_html=True,
            )

    with right_col:
        st.markdown(
            '<div class="section-header"><span class="sh-title">Recent Journal Entries</span>'
            '<div class="sh-divider"></div></div>',
            unsafe_allow_html=True,
        )
        entries = get_all_entries()
        if not entries:
            st.markdown(
                '<div class="alert info"><span class="alert-icon">ℹ️</span>'
                "No journal entries recorded yet. Navigate to Journal Entries to get started.</div>",
                unsafe_allow_html=True,
            )
        else:
            for entry in entries[-3:][::-1]:
                total = sum(l["dr"] for l in entry["lines"])
                lines_html = "".join(
                    f'<div class="je-line">'
                    f'<span class="je-acct">{l["name"]}</span>'
                    f'<span class="{"je-dr" if l["dr"] > 0 else "je-cr"}">'
                    f'{format_currency(l["dr"] if l["dr"] > 0 else l["cr"])}</span></div>'
                    for l in entry["lines"]
                )
                st.markdown(
                    f"""
                <div class="je-card">
                  <div class="je-header">
                    <span class="je-no">Entry #{entry['journal_no']}</span>
                    <span class="je-date">{entry['date']}</span>
                  </div>
                  <div class="je-desc">{entry.get('explanation', 'No description')}</div>
                  {lines_html}
                  <div class="je-total">
                    Total: <span class="je-total-val">{format_currency(total)}</span>
                  </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # ── Revenue vs Expenses Chart ──
    st.markdown(
        '<div class="section-header" style="margin-top:20px;">'
        '<span class="sh-title">Revenue vs. Expenses</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    fig3 = go.Figure(
        data=[
            go.Bar(
                name="Revenues",
                x=["Revenues"],
                y=[revenues],
                marker_color="#D4AF37",
                marker_line_width=0,
            ),
            go.Bar(
                name="Expenses",
                x=["Expenses"],
                y=[expenses],
                marker_color="#EF4444",
                marker_line_width=0,
            ),
            go.Bar(
                name="Net Income",
                x=["Net Income"],
                y=[max(net_income, 0)],
                marker_color="#22C55E" if net_income >= 0 else "#EF4444",
                marker_line_width=0,
            ),
        ]
    )
    fig3.update_layout(
        title="Revenue vs Expenses Comparison",
        barmode="group",
        height=280,
        font=dict(family="Inter"),
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig3, use_container_width=True)
