"""
Journal Entries page UI.
"""

from datetime import date

import pandas as pd
import streamlit as st

from logic.accounts import get_accounts_dict, get_leaf_accounts
from logic.journal import (
    add_je_line,
    delete_journal_entry,
    get_all_entries,
    remove_je_line,
    save_journal_entry,
    validate_je_lines,
)
from logic.reports import format_currency


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>✍️ Journal Entries</h1>
      <p>Record and view accounting journal entries</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    tab_view, tab_add = st.tabs(["📋 View Entries", "➕ Add New Entry"])

    with tab_view:
        _render_view_tab()

    with tab_add:
        _render_add_tab()


def _render_view_tab():
    entries = get_all_entries()
    if not entries:
        st.info("No entries recorded yet.")
        return

    for entry in reversed(entries):
        total_dr = sum(l["dr"] for l in entry["lines"])
        total_cr = sum(l["cr"] for l in entry["lines"])
        balanced = abs(total_dr - total_cr) < 0.01

        header = (
            f"Entry No. {entry['journal_no']} — {entry['date']} — "
            f"{entry.get('explanation', '')}"
        )

        with st.expander(header):
            col_info1, col_info2 = st.columns(2)
            col_info1.write(f"**Explanation:** {entry.get('explanation', '-')}")
            col_info2.write(f"**Cost Centre:** {entry.get('cost_centre', '-')}")

            # Display lines in a table
            df_lines = pd.DataFrame(entry["lines"])
            # Translate internal keys to display names
            df_display = df_lines.rename(
                columns={
                    "code": "Code",
                    "name": "Account Name",
                    "dr": "Debit",
                    "cr": "Credit",
                    "type": "Account Type",
                }
            )
            st.table(df_display[["Code", "Account Name", "Debit", "Credit"]])

            # Footer with totals and delete button
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"**Total:** {format_currency(total_dr)}")

            # Delete functionality
            delete_state_key = f"delete_confirm_{entry['id']}"
            
            if c3.button("🗑️ Delete Entry", key=f"del_{entry['id']}"):
                # Set a flag in session state to remember we are confirming
                st.session_state[delete_state_key] = True

            # Check if we are in the confirmation state
            if st.session_state.get(delete_state_key, False):
                st.warning(f"Are you sure you want to delete entry no. {entry['journal_no']}?")
                
                col_yes, col_no = st.columns(2)
                if col_yes.button("Yes, Delete", key=f"conf_del_{entry['id']}"):
                    delete_journal_entry(entry["id"])
                    st.session_state[delete_state_key] = False # Reset state
                    st.success("Entry deleted successfully.")
                    st.rerun()
                    
                if col_no.button("Cancel", key=f"cancel_del_{entry['id']}"):
                    st.session_state[delete_state_key] = False # Reset state
                    st.rerun()

def _render_add_tab():
    st.markdown(
        "<div class='section-title'>Add New Entry</div>", unsafe_allow_html=True
    )

    # 1. Entry Header Data
    with st.container():
        c1, c2, c3 = st.columns(3)
        entry_date = c1.date_input("Date", value=date.today())
        explanation = c2.text_input("Explanation", placeholder="e.g., Sales invoice...")
        cost_centre = c3.text_input("Cost Centre", placeholder="e.g., Main Branch")

    st.markdown("---")

    # 2. Entry Lines
    st.markdown("**Entry Lines**")
    leaf_accounts = get_leaf_accounts()
    options = {f"{code} - {name}": code for code, name in leaf_accounts}

    lines_to_remove = []

    for i, line in enumerate(st.session_state.je_lines):
        c1, c2, c3, c4 = st.columns([4, 2, 2, 0.5])

        with c1:
            # Finding current index for the selectbox
            current_selection = None
            if line["code"]:
                for label, code in options.items():
                    if code == line["code"]:
                        current_selection = label
                        break

            account_label = st.selectbox(
                "Account",
                options=list(options.keys()),
                index=(
                    list(options.keys()).index(current_selection)
                    if current_selection
                    else None
                ),
                placeholder="Choose account...",
                key=f"acc_{i}",
            )
            st.session_state.je_lines[i]["code"] = options.get(account_label, "")

        with c2:
            dr = st.number_input(
                "Debit",
                min_value=0.0,
                value=float(line["dr"]),
                step=100.0,
                key=f"dr_{i}",
                format="%.2f",
            )
            st.session_state.je_lines[i]["dr"] = dr
        with c3:
            cr = st.number_input(
                "Credit",
                min_value=0.0,
                value=float(line["cr"]),
                step=100.0,
                key=f"cr_{i}",
                format="%.2f",
            )
            st.session_state.je_lines[i]["cr"] = cr
        with c4:
            st.write("")
            if st.button("🗑️", key=f"rm_{i}") and len(st.session_state.je_lines) > 2:
                lines_to_remove.append(i)

    for idx in reversed(lines_to_remove):
        remove_je_line(idx)
        st.rerun()

    col_add, col_save = st.columns([1, 2])
    with col_add:
        if st.button("➕ Add Line"):
            add_je_line()
            st.rerun()

    # Validation display
    total_dr, total_cr, diff, is_balanced = validate_je_lines()

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Debit", format_currency(total_dr))
    col_b.metric("Total Credit", format_currency(total_cr))
    col_c.metric("Difference", format_currency(diff))

    if is_balanced:
        st.success("✅ Balanced — Ready to save")
    elif total_dr > 0 or total_cr > 0:
        st.error("❌ Unbalanced — Debits must equal Credits")
    else:
        st.info("ℹ️ At least two lines with valid data are required")

    # 3. Save Button
    if st.button("Save Entry", disabled=not is_balanced):
        new_entry = save_journal_entry(entry_date, explanation, cost_centre)
        if new_entry:
            st.success(f"Entry No. {new_entry['journal_no']} saved successfully.")
            st.balloons()
            st.rerun()
