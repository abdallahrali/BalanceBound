# """
# Balance Sheet page UI — Premium redesign.
# """

# import plotly.graph_objects as go
# import streamlit as st

# from logic.reports import (
#     compute_trial_balance,
#     format_currency,
#     get_asset_breakdown,
#     get_balance_sheet_data,
# )


# def render():
#     st.markdown(
#         """
#     <div class="page-header">
#       <div>
#         <div class="ph-label">Financial Statements</div>
#         <h1>Balance Sheet</h1>
#         <p>Snapshot of the company's financial position — assets, liabilities, and equity</p>
#       </div>
#       <div class="ph-icon">🏛️</div>
#     </div>
#     """,
#         unsafe_allow_html=True,
#     )

#     tb = compute_trial_balance()
#     data = get_balance_sheet_data(tb)
#     assets_df = data["assets_df"]
#     liab_df = data["liab_df"]
#     net_income = data["net_income"]
#     total_assets = data["total_assets"]
#     total_liab = data["total_liab"]

#     col1, col2 = st.columns(2)

#     with col1:
#         st.markdown(
#             '<div class="section-header"><span class="sh-title">Assets</span>'
#             '<div class="sh-divider"></div></div>',
#             unsafe_allow_html=True,
#         )
#         if not assets_df.empty:
#             a_show = assets_df[["Code", "Account Name"]].copy()
#             a_show["Balance"] = (
#                 assets_df["Total - Debit"] - assets_df["Total - Credit"]
#             ).apply(format_currency)
#             st.dataframe(a_show, use_container_width=True, hide_index=True)
#         else:
#             st.markdown(
#                 '<div class="alert info"><span class="alert-icon">ℹ️</span>No asset accounts to display.</div>',
#                 unsafe_allow_html=True,
#             )
#         st.markdown(
#             f'<div class="total-row"><span class="tr-label">Total Assets</span>'
#             f'<span class="tr-value">{format_currency(total_assets)}</span></div>',
#             unsafe_allow_html=True,
#         )

#     with col2:
#         st.markdown(
#             '<div class="section-header"><span class="sh-title">Liabilities & Equity</span>'
#             '<div class="sh-divider"></div></div>',
#             unsafe_allow_html=True,
#         )
#         if not liab_df.empty:
#             l_show = liab_df[["Code", "Account Name"]].copy()
#             l_show["Balance"] = (
#                 liab_df["Total - Credit"] - liab_df["Total - Debit"]
#             ).apply(format_currency)
#             st.dataframe(l_show, use_container_width=True, hide_index=True)
#         else:
#             st.markdown(
#                 '<div class="alert info"><span class="alert-icon">ℹ️</span>No liability/equity accounts to display.</div>',
#                 unsafe_allow_html=True,
#             )

#         st.markdown(
#             f'<div style="font-size:12px; color: var(--text-muted); margin: 8px 0 4px;">'
#             f'Net profit added to equity: <strong style="color:var(--green);">'
#             f"{format_currency(net_income)}</strong></div>",
#             unsafe_allow_html=True,
#         )
#         st.markdown(
#             f'<div class="total-row"><span class="tr-label">Total Liabilities & Equity</span>'
#             f'<span class="tr-value">{format_currency(total_liab)}</span></div>',
#             unsafe_allow_html=True,
#         )

#     st.markdown("<br>", unsafe_allow_html=True)

#     diff = total_assets - total_liab
#     if abs(diff) < 1:
#         st.markdown(
#             '<div class="alert success"><span class="alert-icon">✅</span>'
#             "The balance sheet is perfectly balanced — Total Assets equal Total Liabilities & Equity.</div>",
#             unsafe_allow_html=True,
#         )
#     else:
#         st.markdown(
#             f'<div class="alert warning"><span class="alert-icon">⚠️</span>'
#             f"Balance sheet difference: <strong>{format_currency(abs(diff))}</strong> — "
#             f"This may be due to unset opening equity balances.</div>",
#             unsafe_allow_html=True,
#         )

#     # ── Waterfall Chart ──
#     st.markdown(
#         '<div class="section-header" style="margin-top:8px;"><span class="sh-title">Position Overview</span>'
#         '<div class="sh-divider"></div></div>',
#         unsafe_allow_html=True,
#     )

#     fig = go.Figure(
#         go.Bar(
#             x=["Total Assets", "Total Liabilities & Equity"],
#             y=[total_assets, total_liab],
#             marker_color=["#D4AF37", "#3B82F6"],
#             marker_line_width=0,
#             text=[format_currency(total_assets), format_currency(total_liab)],
#             textposition="outside",
#             textfont=dict(color="#8A8FA8", size=12),
#         )
#     )

#     fig.update_layout(
#         paper_bgcolor="rgba(0,0,0,0)",
#         plot_bgcolor="rgba(0,0,0,0)",
#         font=dict(family="DM Sans", color="#8A8FA8", size=12),
#         margin=dict(l=0, r=0, t=30, b=0),
#         height=320,
#         showlegend=False,
#         yaxis=dict(
#             gridcolor="rgba(255,255,255,0.05)",
#             tickformat=",",
#             tickfont=dict(color="#555B70"),
#         ),
#         xaxis=dict(tickfont=dict(color="#8A8FA8", size=13)),
#     )
#     st.plotly_chart(fig, use_container_width=True)


"""
Balance Sheet page UI — with filters, hierarchical coloring, accounting equation, and chart.
"""

from datetime import date, datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from logic.reports import compute_trial_balance, format_currency, get_balance_sheet_data


def _compute_filtered_tb(date_from: date | None, date_to: date | None) -> pd.DataFrame:
    """Helper to compute TB within a date range (Opening balances always included)."""
    from logic.journal import get_all_entries
    from logic.reports import compute_trial_balance as _base_tb

    if date_from is None and date_to is None:
        return _base_tb()

    all_entries = get_all_entries()
    filtered_entries = []
    for e in all_entries:
        try:
            entry_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
        except:
            continue
        if date_from and entry_date < date_from:
            continue
        if date_to and entry_date > date_to:
            continue
        filtered_entries.append(e)

    movements = {}
    for entry in filtered_entries:
        for line in entry.get("lines", []):
            code = str(line.get("code", ""))
            if not code:
                continue
            if code not in movements:
                movements[code] = {"dr": 0.0, "cr": 0.0}
            movements[code]["dr"] += float(line.get("dr", 0))
            movements[code]["cr"] += float(line.get("cr", 0))

    base = _base_tb()
    if base.empty:
        return base

    def _get_mv(code, side):
        return sum(m[side] for c, m in movements.items() if c.startswith(code))

    base = base.copy()
    base["Movement - Debit"] = base["Code"].apply(lambda c: _get_mv(c, "dr"))
    base["Movement - Credit"] = base["Code"].apply(lambda c: _get_mv(c, "cr"))
    base["Total - Debit"] = base["Opening Balance - Debit"] + base["Movement - Debit"]
    base["Total - Credit"] = (
        base["Opening Balance - Credit"] + base["Movement - Credit"]
    )
    base["Balance"] = abs(base["Total - Debit"] - base["Total - Credit"])
    return base


def render():
    st.markdown(
        """
    <div class='page-header'>
      <div>
        <div class="ph-label">Reports</div>
        <h1>🏛️ Balance Sheet</h1>
        <p>Statement of the company's financial position</p>
      </div>
      <div class="ph-icon">🏛️</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ─── Filters ─────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header"><span class="sh-title">Filters</span><div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )
    f1, f2, f3 = st.columns([2, 1.5, 1.5])

    with f1:
        depth_map = {
            "Main Types": 1,
            "Categories": 3,
            "Accounts": 6,
            "All Sub-accounts": 9,
        }
        sel_depth = st.selectbox(
            "Hierarchy Depth", list(depth_map.keys()), index=3, key="bs_depth"
        )
    with f2:
        date_from = st.date_input("From Date", value=None, key="bs_from")
    with f3:
        date_to = st.date_input("To Date", value=None, key="bs_to")

    # Compute & Data Extraction
    tb = _compute_filtered_tb(date_from, date_to)
    data = get_balance_sheet_data(tb)

    max_len = depth_map[sel_depth]

    # ─── Styling Helper ──────────────────────────────────────────────────────
    level_styles = {
        1: "background-color: rgba(212,175,55,0.18); color:#D4AF37; font-weight:bold;",
        3: "background-color: rgba(212,175,55,0.09); color:#F0D060;",
        6: "background-color: rgba(59,130,246,0.09); color:#93C5FD;",
        9: "background-color: rgba(255,255,255,0.03); color:#E2E8F0;",
    }
    # level_styles = {
    #     # Uses the gold variable defined in styles.py
    #     "Type": "background-color: var(--gold-bg); color: var(--gold); font-weight: bold;",
    #     "Category": "background-color: var(--gold-bg); opacity: 0.8; color: var(--gold-lt);",
    #     # Uses the blue variable defined in styles.py
    #     "Account": "background-color: var(--blue-bg); color: var(--blue);",
    #     # 'Sub-account' now uses the general text color so it stays visible in both modes
    #     "Sub-account": "background-color: transparent; color: var(--text);",
    # }

    def _code_style(row):
        s = level_styles.get(row["Level"], "")
        return [s if col == "Code" else "" for col in row.index]

    col1, col2 = st.columns(2)

    # ─── Assets Side ───
    with col1:
        st.markdown("### 🏦 Assets")
        assets_df = data["assets_df"][
            data["assets_df"]["Code"].str.len() <= max_len
        ].copy()
        if not assets_df.empty:
            assets_df["Balance"] = (
                assets_df["Total - Debit"] - assets_df["Total - Credit"]
            ).apply(format_currency)
            styled_assets = assets_df[
                ["Code", "Account Name", "Balance", "Level"]
            ].style.apply(_code_style, axis=1)
            st.dataframe(
                styled_assets,
                column_config={"Level": None},
                use_container_width=True,
                hide_index=True,
            )

        st.markdown(
            f"<div class='total-row'><span class='tr-label'>Total Assets</span>"
            f"<span class='tr-value'>{format_currency(data['total_assets'])}</span></div>",
            unsafe_allow_html=True,
        )

    # ─── Liabilities & Equity Side ───
    with col2:
        st.markdown("### ⚖️ Liabilities & Equity")
        liab_df = data["liab_df"][data["liab_df"]["Code"].str.len() <= max_len].copy()
        if not liab_df.empty:
            liab_df["Balance"] = (
                liab_df["Total - Credit"] - liab_df["Total - Debit"]
            ).apply(format_currency)
            styled_liab = liab_df[
                ["Code", "Account Name", "Balance", "Level"]
            ].style.apply(_code_style, axis=1)
            st.dataframe(
                styled_liab,
                column_config={"Level": None},
                use_container_width=True,
                hide_index=True,
            )

        # Better Net Profit UI
        st.markdown(
            f'<div class="total-row" style="background:rgba(59,130,246,0.05); border-color:rgba(59,130,246,0.2); padding: 8px 15px; margin-bottom: 5px;">'
            f'<span class="tr-label" style="font-weight:normal; font-size:12px; color:#93C5FD;">↳ Net Profit for Period (Added to Equity)</span>'
            f'<span class="tr-value" style="color:#93C5FD; font-size:14px;">{format_currency(data["net_income"])}</span></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div class='total-row' >"
            f"<span class='tr-label'>Total Liab & Equity</span>"
            f"<span class='tr-value' >{format_currency(data['total_liab'])}</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ─── Accounting Equation Breakdown ───
    diff = data["total_assets"] - data["total_liab"]

    st.markdown(
        '<div class="section-header"><span class="sh-title">Accounting Equation</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    equation_html = f"""
    <div style="background: var(--bg-el); border: 1px solid var(--border); border-radius: var(--r); padding: 20px; margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-around; align-items: center; text-align: center; margin-bottom: 15px;">
            <div>
                <div style="color: var(--text-3); font-size: 16px; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;">Assets</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 24px; color: var(--gold);">{format_currency(data['total_assets'])}</div>
            </div>
            <div style="font-size: 24px; color: var(--text-3);">=</div>
            <div>
                <div style="color: var(--text-3); font-size: 16px; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;">Liabilities + Equity</div>
                <div style="font-family: 'DM Serif Display', serif; font-size: 24px; color: #3B82F6;">{format_currency(data['total_liab'])}</div>
            </div>
        </div>
        <div style="text-align: center; font-size: 12.5px; color: var(--text-2); border-top: 1px dashed var(--border); padding-top: 12px;">
            <strong>Note on Calculation:</strong> Total Liabilities & Equity includes your base liability/equity accounts 
            plus the <strong>{format_currency(data["net_income"])}</strong> Net Profit generated during this period.
        </div>
    </div>
    """
    st.markdown(equation_html, unsafe_allow_html=True)

    if abs(diff) < 1:
        st.success("✅ The balance sheet is perfectly balanced.")
    else:
        st.warning(
            f"⚠️ Balance Sheet Difference: {format_currency(abs(diff))} — Review opening balances and ensuring all sub-accounts are mapped correctly."
        )

    # ─── Position Overview Chart (Restored) ───
    st.markdown(
        '<div class="section-header" style="margin-top:20px;"><span class="sh-title">Position Overview</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    fig = go.Figure(
        go.Bar(
            x=["Total Assets", "Total Liabilities & Equity"],
            y=[data["total_assets"], data["total_liab"]],
            marker_color=["#D4AF37", "#3B82F6"],
            marker_line_width=0,
            text=[
                format_currency(data["total_assets"]),
                format_currency(data["total_liab"]),
            ],
            textposition="outside",
            textfont=dict(color="#8A8FA8", size=12),
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#8A8FA8", size=12),
        margin=dict(l=0, r=0, t=30, b=0),
        height=320,
        showlegend=False,
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            tickformat=",",
            tickfont=dict(color="#555B70"),
        ),
        xaxis=dict(tickfont=dict(color="#8A8FA8")),
    )
    st.plotly_chart(fig, use_container_width=True)
