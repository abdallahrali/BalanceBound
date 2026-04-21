"""
Trial Balance page UI — with account-type filter and date-range filter.
"""

import time
from datetime import date, datetime

import pandas as pd
import streamlit as st

from logic.accounts import get_account_type, get_leaf_accounts
from logic.journal import get_all_entries, update_opening_balance
from logic.reports import compute_trial_balance, format_currency

# ─── helpers ──────────────────────────────────────────────────────────────────


def _compute_filtered_trial_balance(
    date_from: date | None, date_to: date | None
) -> pd.DataFrame:
    """
    Re-run compute_trial_balance but restrict journal movements to the
    chosen date window.  Opening balances are always fully included.
    """
    from config import ACCOUNT_TYPE_MAP, CODE_LEVEL_LABELS
    from logic.accounts import build_accounts_display_df
    from logic.reports import compute_trial_balance as _base_tb

    # If no date filter, just use the normal function
    if date_from is None and date_to is None:
        return _base_tb()

    # ── Filter entries by date ─────────────────────────────────────────────
    all_entries = get_all_entries()
    filtered_entries = []
    for e in all_entries:
        try:
            entry_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
        except Exception:
            continue
        if date_from and entry_date < date_from:
            continue
        if date_to and entry_date > date_to:
            continue
        filtered_entries.append(e)

    # Build movement totals from filtered entries only
    movements: dict[str, dict] = {}  # code -> {dr, cr}
    for entry in filtered_entries:
        for line in entry.get("lines", []):
            code = str(line.get("code", ""))
            if not code:
                continue
            if code not in movements:
                movements[code] = {"dr": 0.0, "cr": 0.0}
            movements[code]["dr"] += float(line.get("dr", 0))
            movements[code]["cr"] += float(line.get("cr", 0))

    # Delegate to the base function's structure but swap movement data
    base = _base_tb()
    if base.empty:
        return base

    # Patch movement columns on the base dataframe
    def _get_movement(code, side):
        # Sum leaf movements up to this code prefix
        total = 0.0
        for c, m in movements.items():
            if c.startswith(code) or code == c:
                total += m[side]
        return total

    base = base.copy()
    base["Movement - Debit"] = base["Code"].apply(lambda c: _get_movement(c, "dr"))
    base["Movement - Credit"] = base["Code"].apply(lambda c: _get_movement(c, "cr"))
    base["Total - Debit"] = base["Opening Balance - Debit"] + base["Movement - Debit"]
    base["Total - Credit"] = (
        base["Opening Balance - Credit"] + base["Movement - Credit"]
    )
    base["Balance"] = abs(base["Total - Debit"] - base["Total - Credit"])
    base["Balance Type"] = base.apply(
        lambda r: (
            "Debit"
            if r["Total - Debit"] > r["Total - Credit"]
            else ("Credit" if r["Total - Credit"] > r["Total - Debit"] else "Balanced")
        ),
        axis=1,
    )
    return base


# ─── main render ──────────────────────────────────────────────────────────────


def render():
    st.markdown(
        """
    <div class="page-header">
      <div>
        <div class="ph-label">Reports</div>
        <h1>Trial Balance</h1>
        <p>Hierarchical account balances — filter by type, date range, and hierarchy depth</p>
      </div>
      <div class="ph-icon">⚖️</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — Opening Balance Editor
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown(
        '<div class="section-header"><span class="sh-title">Set Opening Balances</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="alert info"><span class="alert-icon">ℹ️</span>'
        "Select any asset or liability/equity account to set or update its opening balance. "
        "Revenue and expense accounts are excluded — they do not carry opening balances.</div>",
        unsafe_allow_html=True,
    )

    leaf_accounts = get_leaf_accounts()
    ob_options: dict[str, str] = {}
    for code, name in leaf_accounts:
        cat = get_account_type(code) or ""
        if "revenue" not in cat.lower() and "expense" not in cat.lower():
            ob_options[f"{code} — {name}"] = code

    c1, c_cat, c_amt, c_side, c_btn = st.columns([3, 2, 2, 2, 2])

    sel_label = c1.selectbox("Select Account", list(ob_options.keys()), key="ob_acct")
    sel_code = ob_options.get(sel_label, "")
    acct_cat = get_account_type(sel_code)
    c_cat.text_input("Account Type", value=acct_cat, disabled=True)

    cur_ob = st.session_state.opening_balances.get(sel_code, {"dr": 0.0, "cr": 0.0})
    cur_dr = float(cur_ob.get("dr", 0.0))
    cur_cr = float(cur_ob.get("cr", 0.0))
    cur_amt = cur_cr if cur_cr > 0 else cur_dr
    def_idx = 1 if cur_cr > 0 else 0

    amt_in = c_amt.number_input(
        "Amount", min_value=0.0, value=cur_amt, step=100.0, key="ob_amt"
    )
    side_in = c_side.selectbox(
        "Side", ["Debit", "Credit"], index=def_idx, key="ob_side"
    )

    c_btn.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    if c_btn.button(
        "💾 Save Balance", use_container_width=True, type="primary", key="ob_save"
    ):
        dr_v = amt_in if side_in == "Debit" else 0.0
        cr_v = amt_in if side_in == "Credit" else 0.0
        update_opening_balance(sel_code, dr_v, cr_v)
        st.toast("✅ Opening balance updated successfully.", icon="💾")
        time.sleep(1.5)
        st.rerun()

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — Filters
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown(
        '<div class="section-header"><span class="sh-title">Filters</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    f1, f2, f3, f4 = st.columns([1.6, 1.6, 1.4, 1.4])

    # ── Account-type filter ────────────────────────────────────────────────
    with f1:
        type_options = ["All Types", "Asset", "Liability/Equity", "Revenue", "Expense"]
        selected_type = st.selectbox("Account Type", type_options, key="tb_type_filter")

    # ── Hierarchy depth ────────────────────────────────────────────────────
    with f2:
        depth_map = {
            "Main Types Only": 1,
            "Categories": 3,
            "Accounts": 6,
            "All Sub-accounts": 9,
        }
        selected_depth = st.selectbox(
            "Hierarchy Depth",
            list(depth_map.keys()),
            index=3,
            key="tb_depth",
        )

    # ── Date range ─────────────────────────────────────────────────────────
    # Determine min/max dates from existing entries
    all_entries = get_all_entries()
    entry_dates = []
    for e in all_entries:
        try:
            entry_dates.append(datetime.strptime(e["date"], "%Y-%m-%d").date())
        except Exception:
            pass

    min_date = min(entry_dates) if entry_dates else date(2020, 1, 1)
    max_date = max(entry_dates) if entry_dates else date.today()

    # with f3:
    #     date_from = st.date_input(
    #         "From Date",
    #         value=None,
    #         min_value=date(2000, 1, 1),
    #         max_value=max_date,
    #         key="tb_date_from",
    #         help="Leave blank to include all periods from the start",
    #     )

    # with f4:
    #     date_to = st.date_input(
    #         "To Date",
    #         value=None,
    #         min_value=date(2000, 1, 1),
    #         max_value=date.today(),
    #         key="tb_date_to",
    #         help="Leave blank to include all periods to today",
    #     )

    with f3:
        date_from = st.date_input(
            "From Date",
            value=None,
            key="tb_date_from",
            help="Leave blank to include all periods from the start",
        )

    with f4:
        date_to = st.date_input(
            "To Date",
            value=None,
            key="tb_date_to",
            help="Leave blank to include all periods to today",
        )

    # Show active filter summary
    filter_parts = []
    if selected_type != "All Types":
        filter_parts.append(f"Type: <strong>{selected_type}</strong>")
    if date_from:
        filter_parts.append(f"From: <strong>{date_from.strftime('%d %b %Y')}</strong>")
    if date_to:
        filter_parts.append(f"To: <strong>{date_to.strftime('%d %b %Y')}</strong>")

    if filter_parts:
        st.markdown(
            '<div class="alert info"><span class="alert-icon">🔍</span>'
            f'Active filters — {" &nbsp;·&nbsp; ".join(filter_parts)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — Compute & display
    # ══════════════════════════════════════════════════════════════════════════
    # tb = _compute_filtered_trial_balance(
    #     date_from if date_from else None,
    #     date_to if date_to else None,
    # )

    # if tb.empty:
    #     st.markdown(
    #         '<div class="alert info"><span class="alert-icon">ℹ️</span>'
    #         "No data to display. Add journal entries or set opening balances first.</div>",
    #         unsafe_allow_html=True,
    #     )
    #     return

    # # ── Apply account-type filter ──────────────────────────────────────────
    # if selected_type != "All Types":
    #     tb = tb[tb["Account Type"].str.contains(selected_type, case=False, na=False)]

    # # ── Apply depth filter ─────────────────────────────────────────────────
    # max_len = depth_map[selected_depth]
    # filtered_tb = tb[tb["Code"].str.len() <= max_len].copy()

    # # ── Hide inactive accounts ─────────────────────────────────────────────
    # # Only keep accounts that have at least some opening balance OR some movement
    # active_mask = (
    #     (filtered_tb["Opening Balance - Debit"] != 0)
    #     | (filtered_tb["Opening Balance - Credit"] != 0)
    #     | (filtered_tb["Movement - Debit"] != 0)
    #     | (filtered_tb["Movement - Credit"] != 0)
    # )
    # filtered_tb = filtered_tb[active_mask]

    # # ── Summary KPIs ───────────────────────────────────────────────────────
    # level_1_tb = tb[tb["Level"] == 1]
    # total_dr = level_1_tb["Total - Debit"].sum()
    # total_cr = level_1_tb["Total - Credit"].sum()
    # total_net = abs(total_dr - total_cr)

    # m1, m2, m3 = st.columns(3)
    # m1.metric("Total Debit", format_currency(total_dr))
    # m2.metric("Total Credit", format_currency(total_cr))
    # side_label = (
    #     "Balanced"
    #     if total_net < 0.01
    #     else ("Debit" if total_dr > total_cr else "Credit")
    # )
    # m3.metric(f"Net Balance ({side_label})", format_currency(total_net))

    # if total_net < 0.01:
    #     st.markdown(
    #         '<div class="alert success"><span class="alert-icon">✅</span>'
    #         "The system is perfectly balanced — all debits equal all credits.</div>",
    #         unsafe_allow_html=True,
    #     )
    # else:
    #     st.markdown(
    #         f'<div class="alert error"><span class="alert-icon">❌</span>'
    #         f"Out of balance by <strong>{format_currency(total_net)}</strong>. "
    #         f"Please review your journal entries.</div>",
    #         unsafe_allow_html=True,
    #     )

    # st.markdown("---")

    # ── Table ──────────────────────────────────────────────────────────────
    # st.markdown(
    #     '<div class="section-header"><span class="sh-title">Trial Balance Table</span>'
    #     '<div class="sh-divider"></div></div>',
    #     unsafe_allow_html=True,
    # )

    # if filtered_tb.empty:
    #     st.markdown(
    #         '<div class="alert warning"><span class="alert-icon">🔍</span>'
    #         "No accounts match the selected filters.</div>",
    #         unsafe_allow_html=True,
    #     )
    #     return

    # level_styles = {
    #     1: "background-color: rgba(212,175,55,0.18); color:#D4AF37; font-weight:bold;",
    #     3: "background-color: rgba(212,175,55,0.09); color:#F0D060;",
    #     6: "background-color: rgba(59,130,246,0.09); color:#93C5FD;",
    #     9: "background-color: rgba(255,255,255,0.03); color:#E2E8F0;",
    # }

    # def _row_style(row):
    #     s = level_styles.get(row["Level"], "")
    #     return [s if col == "Code" else "" for col in row.index]

    # styled_tb = filtered_tb.style.apply(_row_style, axis=1)

    # edited_tb = st.data_editor(
    #     styled_tb,
    #     column_config={
    #         "Code": st.column_config.TextColumn("Code", disabled=True),
    #         "Account Name": st.column_config.TextColumn("Account Name", disabled=True),
    #         "Account Type": st.column_config.TextColumn("Type", disabled=True),
    #         "Level": None,
    #         "Opening Balance - Debit": st.column_config.NumberColumn(
    #             "Opening — Dr", min_value=0.0, format="%.2f"
    #         ),
    #         "Opening Balance - Credit": st.column_config.NumberColumn(
    #             "Opening — Cr", min_value=0.0, format="%.2f"
    #         ),
    #         "Movement - Debit": st.column_config.NumberColumn(
    #             "Movement — Dr", disabled=True, format="%.2f"
    #         ),
    #         "Movement - Credit": st.column_config.NumberColumn(
    #             "Movement — Cr", disabled=True, format="%.2f"
    #         ),
    #         "Total - Debit": st.column_config.NumberColumn(
    #             "Total — Dr", disabled=True, format="%.2f"
    #         ),
    #         "Total - Credit": st.column_config.NumberColumn(
    #             "Total — Cr", disabled=True, format="%.2f"
    #         ),
    #         "Balance": st.column_config.NumberColumn(
    #             "Net Balance", disabled=True, format="%.2f"
    #         ),
    #         "Balance Type": st.column_config.TextColumn("Side", disabled=True),
    #     },
    #     use_container_width=True,
    #     hide_index=True,
    #     key="tb_editor",
    # )

    # col_save, _ = st.columns([1, 3])
    # with col_save:
    #     if st.button(
    #         "💾 Save Opening Balance Changes", type="primary", key="tb_save_btn"
    #     ):
    #         changed = False
    #         for _, row in edited_tb.iterrows():
    #             code = str(row["Code"])
    #             if len(code) == 9:
    #                 raw_dr = row["Opening Balance - Debit"]
    #                 raw_cr = row["Opening Balance - Credit"]
    #                 new_dr = (
    #                     float(raw_dr) if pd.notnull(raw_dr) and raw_dr != "" else 0.0
    #                 )
    #                 new_cr = (
    #                     float(raw_cr) if pd.notnull(raw_cr) and raw_cr != "" else 0.0
    #                 )
    #                 cur = st.session_state.opening_balances.get(
    #                     code, {"dr": 0.0, "cr": 0.0}
    #                 )
    #                 if cur["dr"] != new_dr or cur["cr"] != new_cr:
    #                     update_opening_balance(code, new_dr, new_cr)
    #                     changed = True

    #         if changed:
    #             st.toast("✅ Opening balances saved successfully.", icon="💾")
    #             st.rerun()
    #         else:
    #             st.toast("ℹ️ No changes detected.", icon="ℹ️")
    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — Compute & display
    # ══════════════════════════════════════════════════════════════════════════
    tb = _compute_filtered_trial_balance(
        date_from if date_from else None,
        date_to if date_to else None,
    )

    if tb.empty:
        st.markdown(
            '<div class="alert info"><span class="alert-icon">ℹ️</span>'
            "No data to display. Add journal entries or set opening balances first.</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Apply account-type filter ──────────────────────────────────────────
    if selected_type != "All Types":
        tb = tb[tb["Account Type"].str.contains(selected_type, case=False, na=False)]

    # ── Apply depth filter ─────────────────────────────────────────────────
    max_len = depth_map[selected_depth]
    filtered_tb = tb[tb["Code"].str.len() <= max_len].copy()

    # ── Hide inactive accounts ─────────────────────────────────────────────
    active_mask = (
        (filtered_tb["Opening Balance - Debit"] != 0)
        | (filtered_tb["Opening Balance - Credit"] != 0)
        | (filtered_tb["Movement - Debit"] != 0)
        | (filtered_tb["Movement - Credit"] != 0)
    )
    filtered_tb = filtered_tb[active_mask]

    # ── Summary KPIs ───────────────────────────────────────────────────────
    level_1_tb = tb[tb["Level"] == 1]
    total_dr = level_1_tb["Total - Debit"].sum()
    total_cr = level_1_tb["Total - Credit"].sum()
    total_net = abs(total_dr - total_cr)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Debit", format_currency(total_dr))
    m2.metric("Total Credit", format_currency(total_cr))
    side_label = (
        "Balanced"
        if total_net < 0.01
        else ("Debit" if total_dr > total_cr else "Credit")
    )
    m3.metric(f"Net Balance ({side_label})", format_currency(total_net))

    if total_net < 0.01:
        st.markdown(
            '<div class="alert success"><span class="alert-icon">✅</span>'
            "The system is perfectly balanced — all debits equal all credits.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="alert error"><span class="alert-icon">❌</span>'
            f"Out of balance by <strong>{format_currency(total_net)}</strong>. "
            f"Please review your journal entries.</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Table ──────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header"><span class="sh-title">Trial Balance Table</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    if filtered_tb.empty:
        st.markdown(
            '<div class="alert warning"><span class="alert-icon">🔍</span>'
            "No accounts match the selected filters.</div>",
            unsafe_allow_html=True,
        )
        return

    # --- CALCULATE TOTALS (Not appended to the main table) ---
    min_level_len = filtered_tb["Code"].str.len().min()
    top_level_rows = filtered_tb[filtered_tb["Code"].str.len() == min_level_len]

    tot_ob_dr = top_level_rows["Opening Balance - Debit"].sum()
    tot_ob_cr = top_level_rows["Opening Balance - Credit"].sum()
    tot_mv_dr = top_level_rows["Movement - Debit"].sum()
    tot_mv_cr = top_level_rows["Movement - Credit"].sum()
    tot_dr = top_level_rows["Total - Debit"].sum()
    tot_cr = top_level_rows["Total - Credit"].sum()
    net_bal = abs(tot_dr - tot_cr)

    # 1. Main Table Styling & Rendering
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

    def _main_row_style(row):
        s = level_styles.get(row["Level"], "")
        return [s if col == "Code" else "" for col in row.index]

    styled_tb = filtered_tb.style.apply(_main_row_style, axis=1)

    # Shared Column Config to maintain width alignment between the two tables
    shared_col_config = {
        "Code": st.column_config.TextColumn("Code", disabled=True),
        "Account Name": st.column_config.TextColumn("Account Name", disabled=True),
        "Account Type": st.column_config.TextColumn("Type", disabled=True),
        "Level": None,
        "Opening Balance - Debit": st.column_config.NumberColumn(
            "Opening — Dr", min_value=0.0, format="%,f"
        ),
        "Opening Balance - Credit": st.column_config.NumberColumn(
            "Opening — Cr", min_value=0.0, format="%,f"
        ),
        "Movement - Debit": st.column_config.NumberColumn(
            "Movement — Dr", disabled=True, format="%,f"
        ),
        "Movement - Credit": st.column_config.NumberColumn(
            "Movement — Cr", disabled=True, format="%,f"
        ),
        "Total - Debit": st.column_config.NumberColumn(
            "Total — Dr", disabled=True, format="%,f"
        ),
        "Total - Credit": st.column_config.NumberColumn(
            "Total — Cr", disabled=True, format="%,f"
        ),
        "Balance": st.column_config.NumberColumn(
            "Net Balance", disabled=True, format="%,f"
        ),
        "Balance Type": st.column_config.TextColumn("Side", disabled=True),
    }

    # Render the main scrollable editor
    edited_tb = st.data_editor(
        styled_tb,
        column_config=shared_col_config,
        use_container_width=True,
        hide_index=True,
        key="tb_editor",
    )

    # 2. Separate Pinned Totals Row
    total_row = pd.DataFrame(
        [
            {
                "Code": "TOTAL",
                "Account Name": "Grand Totals",
                "Account Type": "",
                "Level": "Total",
                "Opening Balance - Debit": tot_ob_dr,
                "Opening Balance - Credit": tot_ob_cr,
                "Movement - Debit": tot_mv_dr,
                "Movement - Credit": tot_mv_cr,
                "Total - Debit": tot_dr,
                "Total - Credit": tot_cr,
                "Balance": net_bal,
                "Balance Type": "",
            }
        ]
    )

    def _total_row_style(row):
        s = "background-color: rgba(34,197,94,0.15); color:#22C55E; font-weight:bold;"
        number_cols = [
            "Opening Balance - Debit",
            "Opening Balance - Credit",
            "Movement - Debit",
            "Movement - Credit",
            "Total - Debit",
            "Total - Credit",
            "Balance",
        ]
        # Only color the numerical cells as requested
        return [s if col in number_cols else "" for col in row.index]

    styled_total = total_row.style.apply(_total_row_style, axis=1)

    # Render the totals directly underneath as a locked row
    st.dataframe(
        styled_total,
        column_config=shared_col_config,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Save Button ──
    col_save, _ = st.columns([1, 3])
    with col_save:
        if st.button(
            "💾 Save Opening Balance Changes", type="primary", key="tb_save_btn"
        ):
            changed = False
            for _, row in edited_tb.iterrows():
                code = str(row["Code"])
                if len(code) == 9:  # Ensure we only save sub-accounts
                    raw_dr = row["Opening Balance - Debit"]
                    raw_cr = row["Opening Balance - Credit"]
                    new_dr = (
                        float(raw_dr) if pd.notnull(raw_dr) and raw_dr != "" else 0.0
                    )
                    new_cr = (
                        float(raw_cr) if pd.notnull(raw_cr) and raw_cr != "" else 0.0
                    )
                    cur = st.session_state.opening_balances.get(
                        code, {"dr": 0.0, "cr": 0.0}
                    )
                    if cur["dr"] != new_dr or cur["cr"] != new_cr:
                        update_opening_balance(code, new_dr, new_cr)
                        changed = True

            if changed:
                st.toast("✅ Opening balances saved successfully.", icon="💾")
                time.sleep(1)
                st.rerun()
            else:
                st.toast("ℹ️ No changes detected.", icon="ℹ️")
