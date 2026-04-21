"""
Journal Entries page UI — Premium redesign.
"""

import time
from datetime import date

import pandas as pd
import streamlit as st

from logic.accounts import get_account_type_label, get_accounts_dict, get_leaf_accounts
from logic.journal import (
    add_je_line,
    delete_journal_entry,
    get_all_entries,
    remove_je_line,
    save_journal_entry,
    validate_je_lines,
)
from logic.reports import format_currency


@st.dialog("✏️ Edit Journal Entry", width="large")
def edit_journal_entry_dialog(entry_id: int):
    import json
    from datetime import datetime

    from config import SAMPLE_ENTRIES_JSON
    from logic.accounts import (
        get_account_type,
        get_account_type_label,
        get_accounts_dict,
        get_leaf_accounts,
    )

    # Find the specific entry
    entry = next((e for e in st.session_state.entries if e["id"] == entry_id), None)
    if not entry:
        st.error("Entry not found.")
        return

    # Initialize State specifically for this popup dialog
    ekey = f"edit_state_{entry_id}"
    if ekey not in st.session_state:
        ui_lines = []
        for l in entry["lines"]:
            side = "Debit" if float(l.get("dr", 0)) > 0 else "Credit"
            amt = float(l.get("dr", 0)) if side == "Debit" else float(l.get("cr", 0))
            ui_lines.append(
                {
                    "code": l.get("code", ""),
                    "cost_centre": l.get("cost_centre", ""),
                    "numerical": l.get("numerical", 0),
                    "amount": amt,
                    "side": side,
                }
            )

        # Ensure at least 2 lines are always visible
        while len(ui_lines) < 2:
            ui_lines.append(
                {
                    "code": "",
                    "cost_centre": "",
                    "numerical": 0,
                    "amount": 0.0,
                    "side": "Debit",
                }
            )

        st.session_state[ekey] = {
            "date": datetime.strptime(entry["date"], "%Y-%m-%d").date(),
            "explanation": entry.get("explanation", ""),
            "lines": ui_lines,
        }

    state = st.session_state[ekey]

    # --- Header Inputs ---
    c1, c2 = st.columns(2)
    state["date"] = c1.date_input(
        "Transaction Date", value=state["date"], key=f"ed_date_{entry_id}"
    )
    state["explanation"] = c2.text_input(
        "Description", value=state["explanation"], key=f"ed_exp_{entry_id}"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Entry Lines Editor ---
    leaf_accounts = get_leaf_accounts()
    all_options = {f"{code} — {name}": code for code, name in leaf_accounts}
    lines_to_remove = []

    # Get all currently selected codes in the dialog state
    selected_codes = set(
        line.get("code") for line in state["lines"] if line.get("code")
    )

    for i, line in enumerate(state["lines"]):
        cols = st.columns([2.5, 1.5, 1.2, 1.5, 1.2, 0.5])
        viz = "collapsed" if i > 0 else "visible"

        with cols[0]:
            current_code = line.get("code")

            # Filter options just like in the add tab
            row_options = {
                label: code
                for label, code in all_options.items()
                if code not in selected_codes or code == current_code
            }

            options_list = [""] + list(row_options.keys())
            curr_sel = next(
                (k for k, v in row_options.items() if v == current_code), None
            )

            acc_label = st.selectbox(
                "Account",
                options=options_list,
                index=options_list.index(curr_sel) if curr_sel in options_list else 0,
                label_visibility=viz,
                key=f"ed_acc_{entry_id}_{i}",
            )

            selected_code = row_options.get(acc_label, "")

            # Instantly rerun to remove the selected account from other dropdowns
            if state["lines"][i]["code"] != selected_code:
                state["lines"][i]["code"] = selected_code
                st.rerun()

        with cols[1]:
            state["lines"][i]["cost_centre"] = st.text_input(
                "Cost Centre",
                value=line.get("cost_centre", ""),
                label_visibility=viz,
                key=f"ed_cc_{entry_id}_{i}",
            )

        with cols[2]:
            state["lines"][i]["numerical"] = st.text_input(
                "Numerical #",
                value=str(line.get("numerical", 0)),
                label_visibility=viz,
                key=f"ed_num_{entry_id}_{i}",
            )

        with cols[3]:
            state["lines"][i]["amount"] = st.number_input(
                "Amount",
                min_value=0.0,
                value=float(line.get("amount", 0.0)),
                format="%.2f",
                step=100.0,
                label_visibility=viz,
                key=f"ed_amt_{entry_id}_{i}",
            )

        with cols[4]:
            state["lines"][i]["side"] = st.selectbox(
                "Side",
                ["Debit", "Credit"],
                index=0 if line["side"] == "Debit" else 1,
                label_visibility=viz,
                key=f"ed_side_{entry_id}_{i}",
            )

        with cols[5]:
            if i == 0:
                st.markdown(
                    "<div style='margin-top:28px;'></div>", unsafe_allow_html=True
                )
            if st.button("✕", key=f"ed_rm_{entry_id}_{i}") and len(state["lines"]) > 2:
                lines_to_remove.append(i)

    # Handle line additions/removals
    for idx in reversed(lines_to_remove):
        state["lines"].pop(idx)
        st.rerun()

    if st.button("＋ Add Line", key=f"ed_add_{entry_id}"):
        state["lines"].append(
            {
                "code": "",
                "cost_centre": "",
                "numerical": 0,
                "amount": 0.0,
                "side": "Debit",
            }
        )
        st.rerun()

    # --- Validation & Saving ---
    total_dr = sum(l["amount"] for l in state["lines"] if l["side"] == "Debit")
    total_cr = sum(l["amount"] for l in state["lines"] if l["side"] == "Credit")
    diff = abs(total_dr - total_cr)

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Debit", f"{total_dr:,.2f}")
    m2.metric("Total Credit", f"{total_cr:,.2f}")
    m3.metric("Difference", f"{diff:,.2f}")

    has_activity = any((l["amount"] > 0 and l["code"]) for l in state["lines"])
    is_balanced = (diff < 0.01) and has_activity
    all_codes_valid = all(l["code"] for l in state["lines"] if l["amount"] > 0)

    can_save = is_balanced and all_codes_valid

    if not can_save:
        st.warning(
            "⚠️ Entry must be balanced and all lines with amounts must have an account selected."
        )

    if st.button(
        "💾 Save Changes",
        disabled=not can_save,
        type="primary",
        use_container_width=True,
        key=f"ed_save_btn_{entry_id}",
    ):
        acc_dict = get_accounts_dict()
        new_db_lines = []
        for l in state["lines"]:
            if l["code"] and l["amount"] > 0:
                is_dr = l["side"] == "Debit"
                new_db_lines.append(
                    {
                        "code": l["code"],
                        "name": acc_dict.get(l["code"], l["code"]),
                        "account_type": get_account_type_label(l["code"]),
                        "cost_centre": l["cost_centre"],
                        "numerical": (
                            int(l["numerical"])
                            if str(l["numerical"]).replace("-", "").isdigit()
                            else 0
                        ),
                        "dr": l["amount"] if is_dr else 0.0,
                        "cr": 0.0 if is_dr else l["amount"],
                        "type": get_account_type(l["code"]),
                    }
                )

        # Update the main state list
        for i, e in enumerate(st.session_state.entries):
            if e["id"] == entry_id:
                st.session_state.entries[i]["date"] = state["date"].strftime("%Y-%m-%d")
                st.session_state.entries[i]["explanation"] = state["explanation"]
                st.session_state.entries[i]["lines"] = new_db_lines
                break

        # Save to Database (JSON)
        try:
            with open(SAMPLE_ENTRIES_JSON, "w", encoding="utf-8") as f:
                json.dump(st.session_state.entries, f, ensure_ascii=False, indent=2)
            st.toast("✅ Journal entry updated successfully!", icon="📝")
        except Exception as e:
            st.error(f"Failed to update database: {e}")

        del st.session_state[ekey]  # Clear the temporary edit state
        time.sleep(1)
        st.rerun()


def render():
    st.markdown(
        """
    <div class="page-header">
      <div>
        <div class="ph-label">Accounting</div>
        <h1>Journal Entries</h1>
        <p>Record, review, and manage all accounting transactions</p>
      </div>
      <div class="ph-icon">✍️</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tab_view, tab_add = st.tabs(["📋  View Entries", "➕  New Entry"])

    with tab_view:
        _render_view_tab()

    with tab_add:
        _render_add_tab()


# def _render_view_tab():
#     entries = get_all_entries()
#     if not entries:
#         st.markdown(
#             '<div class="alert info"><span class="alert-icon">ℹ️</span>'
#             "No journal entries have been recorded yet. "
#             "Switch to the <strong>New Entry</strong> tab to get started.</div>",
#             unsafe_allow_html=True,
#         )
#         return

#     # Build summary table
#     all_lines = []
#     for i, entry in enumerate(entries):
#         if i > 0:
#             all_lines.append(
#                 {
#                     "Journal No.": "",
#                     "Date": "",
#                     "Explanation": "",
#                     "Cost Centre": "",
#                     "Code": "",
#                     "Account": "",
#                     "Account Type": "",
#                     "Debit": None,
#                     "Credit": None,
#                 }
#             )

#         for line in entry["lines"]:
#             code_str = str(line.get("code", ""))
#             first_digit = code_str[0] if code_str else ""
#             from config import ACCOUNT_TYPE_LABELS, ACCOUNT_TYPE_MAP

#             raw_type = ACCOUNT_TYPE_MAP.get(first_digit, "Other")
#             display_type = ACCOUNT_TYPE_LABELS.get(raw_type, "Other")

#             all_lines.append(
#                 {
#                     "Journal No.": entry["journal_no"],
#                     "Date": entry["date"],
#                     "Explanation": entry.get("explanation", ""),
#                     "Cost Centre": entry.get("cost_centre", ""),
#                     "Code": code_str,
#                     "Account": line.get("name", ""),
#                     "Account Type": display_type,
#                     "Debit": line.get("dr", 0),
#                     "Credit": line.get("cr", 0),
#                 }
#             )

#     if all_lines:
#         df_all = pd.DataFrame(all_lines)
#         st.markdown(
#             '<div class="section-header"><span class="sh-title">All Entries — Summary Table</span>'
#             '<div class="sh-divider"></div></div>',
#             unsafe_allow_html=True,
#         )
#         st.dataframe(df_all, use_container_width=True, hide_index=True)
#         st.markdown("<br>", unsafe_allow_html=True)

#     st.markdown(
#         '<div class="section-header"><span class="sh-title">Entry Details</span>'
#         '<div class="sh-divider"></div></div>',
#         unsafe_allow_html=True,
#     )

#     for entry in reversed(entries):
#         total_dr = sum(l["dr"] for l in entry["lines"])
#         total_cr = sum(l["cr"] for l in entry["lines"])
#         balanced = abs(total_dr - total_cr) < 0.01

#         badge = (
#             '<span class="badge balanced">✓ Balanced</span>'
#             if balanced
#             else '<span class="badge unbalanced">✗ Unbalanced</span>'
#         )
#         header = (
#             f"Entry #{entry['journal_no']}  ·  {entry['date']}  ·  "
#             f"{entry.get('explanation', 'No description')}"
#         )

#         with st.expander(header):
#             col_info1, col_info2 = st.columns(2)
#             col_info1.write(f"**Description:** {entry.get('explanation', '—')}")
#             col_info2.write(f"**Cost Centre:** {entry.get('cost_centre', '—')}")

#             st.markdown(badge, unsafe_allow_html=True)

#             df_lines = pd.DataFrame(entry["lines"])
#             df_display = df_lines.rename(
#                 columns={
#                     "code": "Code",
#                     "name": "Account Name",
#                     "account_type": "Type",
#                     "numerical": "Numerical",
#                     "dr": "Debit",
#                     "cr": "Credit",
#                 }
#             )

#             cols_to_show = ["Code", "Account Name"]
#             if "Type" in df_display.columns:
#                 cols_to_show.append("Type")
#             if "Numerical" in df_display.columns:
#                 cols_to_show.append("Numerical")
#             cols_to_show.extend(["Debit", "Credit"])

#             st.dataframe(
#                 df_display[cols_to_show], use_container_width=True, hide_index=True
#             )

#             c1, c2, c3 = st.columns([2, 2, 1])
#             c1.markdown(f"**Total:** {format_currency(total_dr)}")

#             delete_key = f"delete_confirm_{entry['id']}"

#             if c3.button("🗑️ Delete", key=f"del_{entry['id']}"):
#                 st.session_state[delete_key] = True

#             if st.session_state.get(delete_key, False):
#                 st.markdown(
#                     f'<div class="alert warning"><span class="alert-icon">⚠️</span>'
#                     f'You are about to permanently delete Entry #{entry["journal_no"]}. '
#                     f"This action cannot be undone.</div>",
#                     unsafe_allow_html=True,
#                 )
#                 col_yes, col_no = st.columns(2)
#                 if col_yes.button(
#                     "✓ Confirm Delete", key=f"conf_del_{entry['id']}", type="primary"
#                 ):
#                     delete_journal_entry(entry["id"])
#                     st.session_state[delete_key] = False
#                     st.toast("✅ Journal entry deleted successfully.", icon="🗑️")
#                     st.rerun()
#                 if col_no.button("✕ Cancel", key=f"cancel_del_{entry['id']}"):
#                     st.session_state[delete_key] = False
#                     st.rerun()


def _render_view_tab():
    import re
    from datetime import datetime

    from config import ACCOUNT_TYPE_LABELS, ACCOUNT_TYPE_MAP

    def normalize_arabic(text):
        if not isinstance(text, str):
            return str(text)
        text = re.sub(r"[أإآ]", "ا", text)
        text = re.sub(r"[ى]", "ي", text)
        text = re.sub(r"[ة]", "ه", text)
        return text

    try:
        from st_keyup import st_keyup

        HAS_KEYUP = True
    except ImportError:
        HAS_KEYUP = False

    entries = get_all_entries()
    if not entries:
        st.markdown(
            '<div class="alert info"><span class="alert-icon">ℹ️</span>'
            "No journal entries have been recorded yet. "
            "Switch to the <strong>New Entry</strong> tab to get started.</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Setup State ──
    if "je_search_key" not in st.session_state:
        st.session_state["je_search_key"] = 0

    # ── Filters UI ──
    st.markdown(
        '<div class="section-header"><span class="sh-title">Search & Filter</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    col1, col3, col4, col5 = st.columns([3, 1.2, 1.2, 1.2])

    with col1:
        s_col, x_col = st.columns([85, 15])
        with s_col:
            if HAS_KEYUP:
                search_query = st_keyup(
                    "Search (Code, Name, Desc)",
                    placeholder="Type to search...",
                    key=f"je_search_{st.session_state['je_search_key']}",
                )
            else:
                search_query = st.text_input(
                    "Search (Code, Name, Desc)",
                    placeholder="Type to search...",
                    key=f"je_search_{st.session_state['je_search_key']}",
                )
        with x_col:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            if st.button(
                "✕",
                key="clear_je_search",
                help="Clear search",
                use_container_width=True,
            ):
                st.session_state["je_search_key"] += 1
                st.rerun()

    with col3:
        date_from = st.date_input("From Date", value=None, key="je_date_from")

    with col4:
        date_to = st.date_input("To Date", value=None, key="je_date_to")

    with col5:
        sort_by = st.selectbox(
            "Sort By",
            [
                "Journal No. (Desc)",
                "Journal No. (Asc)",
                "Date (Newest)",
                "Date (Oldest)",
            ],
        )

    # ── Apply Filters ──
    filtered_entries = []
    for e in entries:
        try:
            e_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
        except:
            e_date = None

        if date_from and e_date and e_date < date_from:
            continue
        if date_to and e_date and e_date > date_to:
            continue

        if search_query:
            q = normalize_arabic(search_query).lower()
            match = False
            if (
                q in normalize_arabic(str(e["journal_no"])).lower()
                or q in normalize_arabic(str(e.get("explanation", ""))).lower()
                or q
                in normalize_arabic(
                    str(e.get("cost_centre", ""))
                ).lower()  # Kept for backwards compatibility if old data has it
            ):
                match = True
            else:
                for l in e["lines"]:
                    if (
                        q in normalize_arabic(str(l.get("code", ""))).lower()
                        or q in normalize_arabic(str(l.get("name", ""))).lower()
                        or q
                        in normalize_arabic(
                            str(l.get("cost_centre", ""))
                        ).lower()  # Add CC to line search
                    ):
                        match = True
                        break
            if not match:
                continue

        filtered_entries.append(e)

    # ── Sort ──
    if sort_by == "Date (Newest)":
        filtered_entries.sort(key=lambda x: x["date"], reverse=True)
    elif sort_by == "Date (Oldest)":
        filtered_entries.sort(key=lambda x: x["date"], reverse=False)
    elif sort_by == "Journal No. (Desc)":
        filtered_entries.sort(key=lambda x: x["journal_no"], reverse=True)
    elif sort_by == "Journal No. (Asc)":
        filtered_entries.sort(key=lambda x: x["journal_no"], reverse=False)

    # ── Build Summary Table ──
    all_lines = []
    for i, entry in enumerate(filtered_entries):
        if i > 0:
            all_lines.append(
                {
                    "Journal No.": "",
                    "Date": "",
                    "Explanation": "",
                    "Code": "",
                    "Account": "",
                    "Account Type": "",
                    "Cost Centre": "",  # Moved to the line level
                    "Debit": None,
                    "Credit": None,
                }
            )

        for line in entry["lines"]:
            code_str = str(line.get("code", ""))
            first_digit = code_str[0] if code_str else ""
            raw_type = ACCOUNT_TYPE_MAP.get(first_digit, "Other")
            display_type = ACCOUNT_TYPE_LABELS.get(raw_type, "Other")

            all_lines.append(
                {
                    "Journal No.": entry["journal_no"],
                    "Date": entry["date"],
                    "Explanation": entry.get("explanation", ""),
                    "Code": code_str,
                    "Account": line.get("name", ""),
                    "Account Type": display_type,
                    "Cost Centre": line.get(
                        "cost_centre", ""
                    ),  # Moved to the line level
                    "Debit": line.get("dr", 0),
                    "Credit": line.get("cr", 0),
                }
            )

    if all_lines:
        df_all = pd.DataFrame(all_lines)
        st.markdown(
            '<div class="section-header"><span class="sh-title">Filtered Entries — Summary Table</span>'
            '<div class="sh-divider"></div></div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            df_all,
            column_config={
                "Debit": st.column_config.NumberColumn("Debit", format="%,.2f"),
                "Credit": st.column_config.NumberColumn("Credit", format="%,.2f"),
            },
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="alert warning"><span class="alert-icon">🔍</span>'
            "No entries match your search and filter criteria.</div>",
            unsafe_allow_html=True,
        )

    # ── Expanders (The Cards) ──
    if filtered_entries:
        st.markdown(
            '<div class="section-header"><span class="sh-title">Entry Details</span>'
            '<div class="sh-divider"></div></div>',
            unsafe_allow_html=True,
        )

        for entry in filtered_entries:
            total_dr = sum(l["dr"] for l in entry["lines"])
            total_cr = sum(l["cr"] for l in entry["lines"])
            balanced = abs(total_dr - total_cr) < 0.01

            badge = (
                '<span class="badge balanced">✓ Balanced</span>'
                if balanced
                else '<span class="badge unbalanced">✗ Unbalanced</span>'
            )

            # Simplified Expander Header to just show Journal No and Explanation
            header = f"Entry #{entry['journal_no']}  ·  {entry.get('explanation', 'No description')}"

            with st.expander(header):
                # --- UPDATED CARD INFO HEADER ---
                col_info1, col_info2 = st.columns(2)
                col_info1.write(f"**Description:** {entry.get('explanation', '—')}")
                col_info2.write(
                    f"**Date:** {entry.get('date', '—')}"
                )  # Replaced Cost Centre with Date

                st.markdown(badge, unsafe_allow_html=True)

                df_lines = pd.DataFrame(entry["lines"])
                df_display = df_lines.rename(
                    columns={
                        "code": "Code",
                        "name": "Account Name",
                        "account_type": "Type",
                        "cost_centre": "Cost Centre",  # Added mapping for Cost Centre
                        "numerical": "Numerical",
                        "dr": "Debit",
                        "cr": "Credit",
                    }
                )

                # --- BUILD THE LINE TABLE COLUMNS ---
                cols_to_show = ["Code", "Account Name"]
                if "Type" in df_display.columns:
                    cols_to_show.append("Type")
                if (
                    "Cost Centre" in df_display.columns
                ):  # Added Cost Centre to the line items table
                    cols_to_show.append("Cost Centre")
                if "Numerical" in df_display.columns:
                    cols_to_show.append("Numerical")
                cols_to_show.extend(["Debit", "Credit"])

                st.dataframe(
                    df_display[cols_to_show],
                    column_config={
                        "Debit": st.column_config.NumberColumn("Debit", format="%,.2f"),
                        "Credit": st.column_config.NumberColumn(
                            "Credit", format="%,.2f"
                        ),
                    },
                    use_container_width=True,
                    hide_index=True,
                )

                # --- FOOTER BUTTONS ---
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.markdown(f"**Total:** {format_currency(total_dr)}")

                if c3.button(
                    "✏️ Edit", key=f"edit_btn_{entry['id']}", use_container_width=True
                ):
                    # We assume edit_journal_entry_dialog is defined somewhere else in the file or globally
                    edit_journal_entry_dialog(entry["id"])

                delete_key = f"delete_confirm_{entry['id']}"

                if c4.button(
                    "🗑️ Delete", key=f"del_{entry['id']}", use_container_width=True
                ):
                    st.session_state[delete_key] = True

                if st.session_state.get(delete_key, False):
                    st.markdown(
                        f'<div class="alert warning"><span class="alert-icon">⚠️</span>'
                        f'You are about to permanently delete Entry #{entry["journal_no"]}. '
                        f"This action cannot be undone.</div>",
                        unsafe_allow_html=True,
                    )
                    col_yes, col_no = st.columns(2)
                    if col_yes.button(
                        "✓ Confirm Delete",
                        key=f"conf_del_{entry['id']}",
                        type="primary",
                    ):
                        delete_journal_entry(entry["id"])
                        st.session_state[delete_key] = False
                        st.toast("✅ Journal entry deleted successfully.", icon="🗑️")
                        time.sleep(1.5)
                        st.rerun()
                    if col_no.button("✕ Cancel", key=f"cancel_del_{entry['id']}"):
                        st.session_state[delete_key] = False
                        time.sleep(1.5)
                        st.rerun()


def _render_add_tab():
    st.markdown(
        '<div class="section-header"><span class="sh-title">New Journal Entry</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    # Entry Header
    c1, c2 = st.columns(2)
    entry_date = c1.date_input(
        "Transaction Date",
        value=date.today(),
        key=f"date_{st.session_state.next_journal}",
    )
    explanation = c2.text_input(
        "Description",
        placeholder="e.g., Sales invoice #1042, Rent payment...",
        key=f"exp_{st.session_state.next_journal}",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-header"><span class="sh-title">Entry Lines</span>'
        '<div class="sh-divider"></div></div>',
        unsafe_allow_html=True,
    )

    leaf_accounts = get_leaf_accounts()
    all_options = {f"{code} — {name}": code for code, name in leaf_accounts}
    lines_to_remove = []

    # --- DYNAMIC DROPDOWN: Find all currently selected codes ---
    selected_codes = set(
        line.get("code") for line in st.session_state.je_lines if line.get("code")
    )

    for i, line in enumerate(st.session_state.je_lines):
        cols = st.columns([2.2, 1.1, 1.3, 1.0, 1.8, 1.2, 0.5])
        c_acc, c_type, c_cc, c_num, c_amt, c_side, c_del = cols

        with c_acc:
            current_code = line.get("code")

            # Filter options: exclude if selected elsewhere, keep if unselected or if it's THIS line's current code
            row_options = {
                label: code
                for label, code in all_options.items()
                if code not in selected_codes or code == current_code
            }

            current_selection = None
            if current_code:
                for label, code in row_options.items():
                    if code == current_code:
                        current_selection = label
                        break

            account_label = st.selectbox(
                "Account",
                options=list(row_options.keys()),
                index=(
                    list(row_options.keys()).index(current_selection)
                    if current_selection
                    else None
                ),
                placeholder="Select account...",
                key=f"acc_{i}_{st.session_state.next_journal}",
            )
            selected_code = row_options.get(account_label, "")

            # If the user changed the account, update the state and rerun instantly so it vanishes from other rows
            if st.session_state.je_lines[i].get("code") != selected_code:
                st.session_state.je_lines[i]["code"] = selected_code
                st.session_state.je_lines[i]["_selected_code"] = selected_code
                new_type = (
                    get_account_type_label(selected_code) if selected_code else ""
                )
                st.session_state.je_lines[i]["account_type"] = new_type
                st.session_state[f"type_{i}_{st.session_state.next_journal}"] = new_type
                st.rerun()

        with c_type:
            st.text_input(
                "Type",
                value=line.get("account_type", ""),
                key=f"type_{i}_{st.session_state.next_journal}",
                disabled=True,
            )

        with c_cc:
            st.session_state.je_lines[i]["cost_centre"] = st.text_input(
                "Cost Centre",
                value=line.get("cost_centre", ""),
                key=f"cc_line_{i}_{st.session_state.next_journal}",
                placeholder="Branch/Dept",
            )

        with c_num:
            num_str = st.text_input(
                "Numerical #",
                value=str(line.get("numerical", 0)),
                key=f"num_{i}_{st.session_state.next_journal}",
            )
            try:
                st.session_state.je_lines[i]["numerical"] = int(num_str)
            except ValueError:
                st.session_state.je_lines[i]["numerical"] = 0

        with c_amt:
            st.session_state.je_lines[i]["amount"] = st.number_input(
                "Amount",
                min_value=0.0,
                value=float(line.get("amount", 0.0)),
                format="%.2f",
                step=100.0,
                key=f"amt_{i}_{st.session_state.next_journal}",
            )

        with c_side:
            st.session_state.je_lines[i]["side"] = st.selectbox(
                "Side",
                options=["Debit", "Credit"],
                index=0 if line.get("side") == "Debit" else 1,
                key=f"side_{i}_{st.session_state.next_journal}",
            )

        with c_del:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            if (
                st.button("✕", key=f"rm_{i}_{st.session_state.next_journal}")
                and len(st.session_state.je_lines) > 2
            ):
                lines_to_remove.append(i)

    for idx in reversed(lines_to_remove):
        remove_je_line(idx)
        st.rerun()

    col_add, _ = st.columns([1, 3])
    with col_add:
        if st.button("＋ Add Line"):
            add_je_line()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Validation summary
    total_dr, total_cr, diff, is_balanced = validate_je_lines()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Debit", format_currency(total_dr))
    m2.metric("Total Credit", format_currency(total_cr))
    m3.metric("Difference", format_currency(diff))

    # --- RESTORED ORIGINAL VALIDATION (Removed duplicate warnings) ---
    headers_valid = True
    lines_valid = True
    has_activity = False

    for line in st.session_state.je_lines:
        amt = float(line.get("amount", 0.0))
        code = line.get("code")

        if code or amt > 0:
            if not code:
                lines_valid = False
                break
            if amt > 0:
                has_activity = True

    can_save = is_balanced and headers_valid and lines_valid and has_activity

    if can_save:
        st.markdown(
            '<div class="alert success"><span class="alert-icon">✅</span>'
            "Entry is balanced and ready to save.</div>",
            unsafe_allow_html=True,
        )
    elif not lines_valid:
        st.markdown(
            '<div class="alert warning"><span class="alert-icon">⚠️</span>'
            "Each active line must have an Account selected.</div>",
            unsafe_allow_html=True,
        )
    elif total_dr > 0 or total_cr > 0:
        st.markdown(
            '<div class="alert error"><span class="alert-icon">❌</span>'
            f"Entry is unbalanced — Debits must equal Credits. Current difference: {format_currency(diff)}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="alert info"><span class="alert-icon">ℹ️</span>'
            "Enter amounts in at least two lines to save an entry.</div>",
            unsafe_allow_html=True,
        )

    col_save, _ = st.columns([1, 3])
    with col_save:
        if st.button("💾  Save Journal Entry", disabled=not can_save, type="primary"):
            new_entry = save_journal_entry(entry_date, explanation)
            if new_entry:
                st.toast(
                    f"✅ Entry #{new_entry['journal_no']} saved successfully!", icon="✍️"
                )
                # st.balloons()
                time.sleep(1.5)
                st.rerun()
