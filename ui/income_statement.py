# """
# Income Statement page UI — Premium redesign.
# """

# import plotly.graph_objects as go
# import streamlit as st

# from logic.reports import (
#     compute_trial_balance,
#     format_currency,
#     get_income_statement_data,
# )


# def render():
#     st.markdown(
#         """
#     <div class="page-header">
#       <div>
#         <div class="ph-label">Financial Statements</div>
#         <h1>Income Statement</h1>
#         <p>Profitability and performance results for the current period</p>
#       </div>
#       <div class="ph-icon">💹</div>
#     </div>
#     """,
#         unsafe_allow_html=True,
#     )

#     tb = compute_trial_balance()
#     data = get_income_statement_data(tb)
#     rev_df = data["rev_df"]
#     exp_df = data["exp_df"]
#     total_rev = data["total_rev"]
#     total_exp = data["total_exp"]
#     net = data["net_income"]

#     PLOT_LAYOUT = dict(
#         paper_bgcolor="rgba(0,0,0,0)",
#         plot_bgcolor="rgba(0,0,0,0)",
#         font=dict(family="DM Sans", color="#8A8FA8", size=12),
#         margin=dict(l=0, r=0, t=30, b=0),
#     )

#     col_left, col_right = st.columns([1, 1])

#     # ── Revenue ──
#     with col_left:
#         st.markdown(
#             '<div class="section-header"><span class="sh-title">Revenues</span>'
#             '<div class="sh-divider"></div></div>',
#             unsafe_allow_html=True,
#         )
#         if not rev_df.empty:
#             rev_show = rev_df[["Code", "Account Name", "Balance"]].copy()
#             rev_show["Balance"] = rev_show["Balance"].apply(format_currency)
#             st.dataframe(rev_show, use_container_width=True, hide_index=True)
#         else:
#             st.markdown(
#                 '<div class="alert info"><span class="alert-icon">ℹ️</span>No revenue accounts found.</div>',
#                 unsafe_allow_html=True,
#             )
#         st.markdown(
#             f'<div class="total-row"><span class="tr-label">Total Revenues</span>'
#             f'<span class="tr-value">{format_currency(total_rev)}</span></div>',
#             unsafe_allow_html=True,
#         )

#     # ── Expenses ──
#     with col_right:
#         st.markdown(
#             '<div class="section-header"><span class="sh-title">Expenses</span>'
#             '<div class="sh-divider"></div></div>',
#             unsafe_allow_html=True,
#         )
#         if not exp_df.empty:
#             exp_show = exp_df[["Code", "Account Name", "Balance"]].copy()
#             exp_show["Balance"] = exp_show["Balance"].apply(format_currency)
#             st.dataframe(exp_show, use_container_width=True, hide_index=True)
#         else:
#             st.markdown(
#                 '<div class="alert info"><span class="alert-icon">ℹ️</span>No expense accounts found.</div>',
#                 unsafe_allow_html=True,
#             )
#         st.markdown(
#             f'<div class="total-row"><span class="tr-label">Total Expenses</span>'
#             f'<span class="tr-value" style="color: var(--red);">{format_currency(total_exp)}</span></div>',
#             unsafe_allow_html=True,
#         )

#     # ── Net Result ──
#     if net >= 0:
#         st.markdown(
#             f"""
#         <div class="result-box profit">
#           <div class="rb-label">✅ Net Profit for the Period</div>
#           <div class="rb-value">{format_currency(net)}</div>
#           <div class="rb-note">Revenues exceeded expenses — strong performance.</div>
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )
#     else:
#         st.markdown(
#             f"""
#         <div class="result-box loss">
#           <div class="rb-label">❌ Net Loss for the Period</div>
#           <div class="rb-value">{format_currency(abs(net))}</div>
#           <div class="rb-note">Expenses exceeded revenues — review cost structure.</div>
#         </div>
#         """,
#             unsafe_allow_html=True,
#         )

#     # ── Chart ──
#     st.markdown(
#         '<div class="section-header"><span class="sh-title">Visual Breakdown</span>'
#         '<div class="sh-divider"></div></div>',
#         unsafe_allow_html=True,
#     )

#     fig = go.Figure()
#     fig.add_trace(
#         go.Bar(
#             name="Revenues",
#             x=["Revenues"],
#             y=[total_rev],
#             marker_color="#D4AF37",
#             marker_line_width=0,
#             text=[f"{total_rev:,.0f}"],
#             textposition="outside",
#             textfont=dict(color="#D4AF37"),
#         )
#     )
#     fig.add_trace(
#         go.Bar(
#             name="Expenses",
#             x=["Expenses"],
#             y=[total_exp],
#             marker_color="#EF4444",
#             marker_line_width=0,
#             text=[f"{total_exp:,.0f}"],
#             textposition="outside",
#             textfont=dict(color="#EF4444"),
#         )
#     )
#     fig.add_trace(
#         go.Bar(
#             name="Net Profit" if net >= 0 else "Net Loss",
#             x=["Net Result"],
#             y=[abs(net)],
#             marker_color="#22C55E" if net >= 0 else "#F87171",
#             marker_line_width=0,
#             text=[f"{net:,.0f}"],
#             textposition="outside",
#             textfont=dict(color="#22C55E" if net >= 0 else "#F87171"),
#         )
#     )

#     fig.update_layout(
#         **PLOT_LAYOUT,
#         height=380,
#         showlegend=True,
#         legend=dict(
#             orientation="h",
#             yanchor="top",
#             y=1.08,
#             xanchor="right",
#             x=1,
#             font=dict(color="#8A8FA8"),
#         ),
#         barmode="group",
#         yaxis=dict(
#             gridcolor="rgba(255,255,255,0.05)",
#             tickformat=",",
#             tickfont=dict(color="#555B70"),
#         ),
#         xaxis=dict(tickfont=dict(color="#8A8FA8")),
#     )
#     st.plotly_chart(fig, use_container_width=True)


"""
Income Statement page UI — with filters, hierarchical coloring, total cards, and chart.
"""

from datetime import date, datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from logic.reports import (
    compute_trial_balance,
    format_currency,
    get_income_statement_data,
)


def _compute_filtered_tb(date_from, date_to):
    from logic.journal import get_all_entries
    from logic.reports import compute_trial_balance as _base_tb

    if date_from is None and date_to is None:
        return _base_tb()

    all_entries = get_all_entries()
    filtered_entries = []
    for e in all_entries:
        try:
            entry_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
            if date_from and entry_date < date_from:
                continue
            if date_to and entry_date > date_to:
                continue
            filtered_entries.append(e)
        except:
            continue

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
        <h1>💹 Income Statement</h1>
        <p>Profitability and performance results for the current period</p>
      </div>
      <div class="ph-icon">💹</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ─── Filters ─────────────────────────────────────────────────────────────
    f1, f2, f3 = st.columns([2, 1.5, 1.5])
    with f1:
        depth_map = {
            "Main Types": 1,
            "Categories": 3,
            "Accounts": 6,
            "All Sub-accounts": 9,
        }
        sel_depth = st.selectbox(
            "Hierarchy Depth", list(depth_map.keys()), index=3, key="is_depth"
        )
    with f2:
        date_from = st.date_input("From Date", value=None, key="is_from")
    with f3:
        date_to = st.date_input("To Date", value=None, key="is_to")

    # Compute data
    tb = _compute_filtered_tb(date_from, date_to)
    data = get_income_statement_data(tb)

    total_rev = data["total_rev"]
    total_exp = data["total_exp"]
    net = data["net_income"]
    max_len = depth_map[sel_depth]

    # Styling helper
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

    PLOT_LAYOUT = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#8A8FA8", size=12),
        margin=dict(l=0, r=0, t=30, b=0),
    )

    col_left, col_right = st.columns([1, 1])

    # ── Revenue ──
    with col_left:
        st.markdown(
            '<div class="section-header"><span class="sh-title">Revenues</span><div class="sh-divider"></div></div>',
            unsafe_allow_html=True,
        )
        rev_df = data["rev_df"][data["rev_df"]["Code"].str.len() <= max_len].copy()
        if not rev_df.empty:
            rev_df["Balance_Fmt"] = rev_df["Balance"].apply(format_currency)
            st.dataframe(
                rev_df[["Code", "Account Name", "Balance_Fmt", "Level"]].style.apply(
                    _code_style, axis=1
                ),
                column_config={"Balance_Fmt": "Balance", "Level": None},
                use_container_width=True,
                hide_index=True,
            )
        st.markdown(
            f'<div class="total-row"><span class="tr-label">Total Revenues</span>'
            f'<span class="tr-value" style="color: var(--gold);">{format_currency(total_rev)}</span></div>',
            unsafe_allow_html=True,
        )

    # ── Expenses ──
    with col_right:
        st.markdown(
            '<div class="section-header"><span class="sh-title">Expenses</span><div class="sh-divider"></div></div>',
            unsafe_allow_html=True,
        )
        exp_df = data["exp_df"][data["exp_df"]["Code"].str.len() <= max_len].copy()
        if not exp_df.empty:
            exp_df["Balance_Fmt"] = exp_df["Balance"].apply(format_currency)
            st.dataframe(
                exp_df[["Code", "Account Name", "Balance_Fmt", "Level"]].style.apply(
                    _code_style, axis=1
                ),
                column_config={"Balance_Fmt": "Balance", "Level": None},
                use_container_width=True,
                hide_index=True,
            )
        st.markdown(
            f'<div class="total-row"><span class="tr-label">Total Expenses</span>'
            f'<span class="tr-value" style="color: var(--red);">{format_currency(total_exp)}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Net Result Box ──
    if net >= 0:
        st.markdown(
            f'<div class="result-box profit"><div class="rb-label">✅ Net Profit</div><div class="rb-value">{format_currency(net)}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="result-box loss"><div class="rb-label">❌ Net Loss</div><div class="rb-value">{format_currency(abs(net))}</div></div>',
            unsafe_allow_html=True,
        )

    # ── Chart ──
    st.markdown(
        '<div class="section-header"><span class="sh-title">Visual Breakdown</span><div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Revenues",
            x=["Revenues"],
            y=[total_rev],
            marker_color="#D4AF37",
            marker_line_width=0,
            text=[f"{total_rev:,.0f}"],
            textposition="outside",
            textfont=dict(color="#D4AF37"),
        )
    )
    fig.add_trace(
        go.Bar(
            name="Expenses",
            x=["Expenses"],
            y=[total_exp],
            marker_color="#EF4444",
            marker_line_width=0,
            text=[f"{total_exp:,.0f}"],
            textposition="outside",
            textfont=dict(color="#EF4444"),
        )
    )
    fig.add_trace(
        go.Bar(
            name="Net Profit" if net >= 0 else "Net Loss",
            x=["Net Result"],
            y=[abs(net)],
            marker_color="#22C55E" if net >= 0 else "#F87171",
            marker_line_width=0,
            text=[f"{net:,.0f}"],
            textposition="outside",
            textfont=dict(color="#22C55E" if net >= 0 else "#F87171"),
        )
    )

    fig.update_layout(
        **PLOT_LAYOUT,
        height=380,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.08,
            xanchor="right",
            x=1,
            font=dict(color="#8A8FA8"),
        ),
        barmode="group",
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)",
            tickformat=",",
            tickfont=dict(color="#555B70"),
        ),
        xaxis=dict(tickfont=dict(color="#8A8FA8")),
    )
    st.plotly_chart(fig, use_container_width=True)
