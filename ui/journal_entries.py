"""
Journal Entries page UI.
"""

from datetime import date

import pandas as pd
import streamlit as st

from logic.accounts import get_accounts_dict, get_leaf_accounts, get_account_type_label
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

    # Build summary table from all entries
    all_lines = []
    for i, entry in enumerate(entries):
        # Add an empty "spacer" row between different journal entries
        if i > 0:
            all_lines.append({
                "Journal No.": "", "Date": "", "Explanation": "", 
                "Cost Centre": "", "Code": "", "Account": "", 
                "Account Type": "", "Debit": None, "Credit": None
            })
            
        for line in entry["lines"]:
            # Automatically determine the Account Type based on the first digit of the code
            code_str = str(line.get("code", ""))
            first_digit = code_str[0] if code_str else ""
            
            # Map the prefix to the readable label (defaulting to "Other")
            # Based on config.ACCOUNT_TYPE_MAP and config.ACCOUNT_TYPE_LABELS
            from config import ACCOUNT_TYPE_MAP, ACCOUNT_TYPE_LABELS
            raw_type = ACCOUNT_TYPE_MAP.get(first_digit, "Other")
            display_type = ACCOUNT_TYPE_LABELS.get(raw_type, "Other")

            all_lines.append({
                "Journal No.": entry["journal_no"],
                "Date": entry["date"],
                "Explanation": entry.get("explanation", ""),
                "Cost Centre": entry.get("cost_centre", ""),
                "Code": code_str,
                "Account": line.get("name", ""),
                "Account Type": display_type, # Automatically assigned here
                "Debit": line.get("dr", 0),
                "Credit": line.get("cr", 0),
            })
    
    if all_lines:
        df_all = pd.DataFrame(all_lines)
        st.markdown("### 📊 All Journal Entries")
        st.dataframe(df_all, use_container_width=True, hide_index=True)
        st.markdown("---")

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
                    "account_type": "Entered Type", # The new field
                    "numerical": "Numerical",       # The new field
                    "dr": "Debit",
                    "cr": "Credit",
                }
            )
            
            # Select columns to display safely (checks if old entries don't have the new keys yet)
            cols_to_show = ["Code", "Account Name"]
            if "Entered Type" in df_display.columns: cols_to_show.append("Entered Type")
            if "Numerical" in df_display.columns: cols_to_show.append("Numerical")
            cols_to_show.extend(["Debit", "Credit"])
            
            st.table(df_display[cols_to_show])

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
        c1, c2 = st.columns(2)
        entry_date = c1.date_input("Date", value=date.today(), key=f"date_{st.session_state.next_journal}")
        explanation = c2.text_input("Explanation", placeholder="e.g., Sales invoice...", key=f"exp_{st.session_state.next_journal}")

    st.markdown("---")

    # 2. Entry Lines
    st.markdown("**Entry Lines**")
    leaf_accounts = get_leaf_accounts()
    options = {f"{code} - {name}": code for code, name in leaf_accounts}

    lines_to_remove = []

    for i, line in enumerate(st.session_state.je_lines):
        # Column layout: [Account, Type, Cost Centre, Numerical, Amount, Side, Delete]
        cols = st.columns([2.2, 1.1, 1.3, 1.0, 1.8, 1.2, 0.5])
        c_acc, c_type, c_cc, c_num, c_amt, c_side, c_del = cols

        with c_acc:
            current_selection = None
            if line.get("code"):
                for label, code in options.items():
                    if code == line["code"]:
                        current_selection = label
                        break

            account_label = st.selectbox(
                "Account",
                options=list(options.keys()),
                index=(list(options.keys()).index(current_selection) if current_selection else None),
                placeholder="Choose account...",
                key=f"acc_{i}_{st.session_state.next_journal}",
            )
            selected_code = options.get(account_label, "")
            
            # Check if the account actually changed during this rerun
            if st.session_state.je_lines[i].get("code") != selected_code:
                st.session_state.je_lines[i]["code"] = selected_code
                st.session_state.je_lines[i]["_selected_code"] = selected_code
                
                # Fetch new account type
                new_type = get_account_type_label(selected_code) if selected_code else ""
                st.session_state.je_lines[i]["account_type"] = new_type
                
                # FORCE update the text_input's session_state key so it refreshes instantly
                type_widget_key = f"type_{i}_{st.session_state.next_journal}"
                st.session_state[type_widget_key] = new_type

        with c_type:
            st.text_input("Type", value=line.get("account_type", ""), key=f"type_{i}_{st.session_state.next_journal}", disabled=True)

        with c_cc:
            st.session_state.je_lines[i]["cost_centre"] = st.text_input(
                "Cost Centre", 
                value=line.get("cost_centre", ""), 
                key=f"cc_line_{i}_{st.session_state.next_journal}",
                placeholder="Branch/Dept"
            )

        with c_num:
            num_str = st.text_input("Numerical", value=str(line.get("numerical", 0)), key=f"num_{i}_{st.session_state.next_journal}")
            try:
                st.session_state.je_lines[i]["numerical"] = int(num_str)
            except ValueError:
                st.session_state.je_lines[i]["numerical"] = 0

        with c_amt:
            # Single Amount field
            st.session_state.je_lines[i]["amount"] = st.number_input(
                "Amount",
                min_value=0.0,
                value=float(line.get("amount", 0.0)),
                format="%.2f",
                key=f"amt_{i}_{st.session_state.next_journal}"
            )

        with c_side:
            # Side selector (Debit or Credit)
            st.session_state.je_lines[i]["side"] = st.selectbox(
                "Side",
                options=["Debit", "Credit"],
                index=0 if line.get("side") == "Debit" else 1,
                key=f"side_{i}_{st.session_state.next_journal}"
            )

        with c_del:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"rm_{i}_{st.session_state.next_journal}") and len(st.session_state.je_lines) > 2:
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

    # --- NEW: Required Fields Validation ---
    headers_valid = bool(explanation.strip())
    
    lines_valid = True
    for line in st.session_state.je_lines:
        # Check if line has data
        if line.get("code") or line.get("dr", 0) > 0 or line.get("cr", 0) > 0:
            # If line is used, Account and Cost Centre must be filled
            if not line.get("code") or not line.get("cost_centre", "").strip():
                lines_valid = False
                break

    can_save = is_balanced and headers_valid and lines_valid

    if can_save:
        st.success("✅ Balanced and all required fields filled — Ready to save")
    elif not headers_valid:
        st.warning("⚠️ Missing Info: Please fill out the Explanation.")
    elif not lines_valid:
        st.warning("⚠️ Missing Info: Every active line needs an Account and a Cost Centre.")
    elif total_dr > 0 or total_cr > 0:
        st.error("❌ Unbalanced — Debits must equal Credits")
    else:
        st.info("ℹ️ At least two lines with valid data are required")

# 3. Save Button
    if st.button("Save Entry", disabled=not can_save):
        # Remove cost_centre from this call
        new_entry = save_journal_entry(entry_date, explanation) 
        if new_entry:
            st.success(f"Entry No. {new_entry['journal_no']} saved successfully.")
            st.balloons()
            st.rerun()