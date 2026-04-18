"""
Trial Balance page UI.
"""

import pandas as pd
import streamlit as st

from logic.accounts import get_account_type, get_leaf_accounts
from logic.journal import update_opening_balance
from logic.reports import compute_trial_balance, format_currency


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>⚖️ Trial Balance</h1>
      <p>View hierarchical balances for all accounts across different periods</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 1. --- Update Opening Balances ---
    # We replaced the expander with a clear section header and a subtle side-border.
    # This keeps the section always visible and ensures it blends with the website theme.
    st.markdown(
        """
        <div style='border-left: 5px solid #2563eb; padding-left: 20px; margin-top: 10px; margin-bottom: 20px;'>
            <h3 style='margin: 0;'>⚙️ Update Opening Balances</h3>
            <p style='margin: 0; opacity: 0.8;'>Select an account from the list below to set or modify its starting balance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        leaf_accounts = get_leaf_accounts()
        options = {f"{code} - {name}": code for code, name in leaf_accounts}

        # Adjusted column variable names for clarity (Account, Category, Amount, Side, Button)
        c1, c_cat, c_amt, c_side, c_btn = st.columns([3, 2, 2, 2, 2])

        selected_label = c1.selectbox("Choose Account", list(options.keys()))
        selected_code = options[selected_label]

        # Using non-technical terms like "Category" instead of "Account Type"
        account_category = get_account_type(selected_code)
        c_cat.text_input("Category", value=account_category, disabled=True)

        # Get current balance to populate inputs
        current_ob = st.session_state.opening_balances.get(
            selected_code, {"dr": 0.0, "cr": 0.0}
        )

        # --- EDITED PART START ---
        # Determine the current amount and which side is active
        current_dr = float(current_ob.get("dr", 0.0))
        current_cr = float(current_ob.get("cr", 0.0))
        
        if current_cr > 0:
            current_amount = current_cr
            default_side_idx = 1  # 1 corresponds to "Credit"
        else:
            current_amount = current_dr
            default_side_idx = 0  # 0 corresponds to "Debit"

        # 1. Single Amount field
        amount_input = c_amt.number_input(
            "Amount", min_value=0.0, value=current_amount, step=100.0
        )
        
        # 2. Side dropdown
        side_input = c_side.selectbox(
            "Side", options=["Debit", "Credit"], index=default_side_idx
        )
        # --- EDITED PART END ---

        # Button alignment
        c_btn.write("")
        c_btn.write("")
        if c_btn.button("💾 Save Balance", use_container_width=True, type="primary"):
            
            # --- EDITED PART START ---
            # Translate the Amount and Side back into dr and cr for the update function
            dr_val = amount_input if side_input == "Debit" else 0.0
            cr_val = amount_input if side_input == "Credit" else 0.0
            
            update_opening_balance(selected_code, dr_val, cr_val)
            # --- EDITED PART END ---
            
            st.success("The opening balance has been successfully updated and saved.")
            st.rerun()

    st.markdown("---")

    tb = compute_trial_balance()

    if tb.empty:
        st.info(
            "No data to display. Please add journal entries or opening balances first."
        )
        return

    # --- Summary Performance Metrics ---
    # We only sum Level 1 accounts to avoid double-counting the totals
    level_1_tb = tb[tb["Level"] == 1]

    # Totals for Opening Balances
    total_ob_dr = level_1_tb["Opening Balance - Debit"].sum()
    total_ob_cr = level_1_tb["Opening Balance - Credit"].sum()
    total_ob_net = abs(total_ob_dr - total_ob_cr)

    # Totals for Movements
    total_mv_dr = level_1_tb["Movement - Debit"].sum()
    total_mv_cr = level_1_tb["Movement - Credit"].sum()
    total_mv_net = max(total_mv_dr, total_mv_cr)

    # Grand Totals
    total_tb_dr = level_1_tb["Total - Debit"].sum()
    total_tb_cr = level_1_tb["Total - Credit"].sum()
    total_tb_net = abs(total_tb_dr - total_tb_cr)

    # 2. --- Redesigned KPI Section ---
    # We use a column layout to show the Total and its Debit/Credit components underneath
    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Starting Balances (Net)", format_currency(total_ob_net))
        st.caption(
            f"**Debit:** {format_currency(total_ob_dr)} | **Credit:** {format_currency(total_ob_cr)}"
        )

    with m2:
        st.metric("Total Activity (Net)", format_currency(total_mv_net))
        st.caption(
            f"**Debit:** {format_currency(total_mv_dr)} | **Credit:** {format_currency(total_mv_cr)}"
        )

    with m3:
        st.metric(
            "Net Balance "
            + ("(Debit)" if (total_tb_dr >= total_tb_cr) else "(Credit)"),
            format_currency(total_tb_net),
        )
        st.caption(
            f"**Debit:** {format_currency(total_tb_dr)} | **Credit:** {format_currency(total_tb_cr)}"
        )

    if total_tb_net < 0.01:
        st.success("✅ The system is perfectly balanced.")
    else:
        st.error(
            f"❌ The system is currently out of balance by {format_currency(total_tb_net)}."
        )
    st.markdown("---")

    # 2. --- Collapse/Expand Feature ---
    st.markdown("### 📊 Interactive Trial Balance")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        depth_mapping = {
            "1. Main Types Only": 1,
            "2. Categories": 3,
            "3. Accounts": 6,
            "4. All Subaccounts": 9,
        }
        selected_depth = st.select_slider(
            "🗂️ Collapse / Expand Hierarchy",
            options=list(depth_mapping.keys()),
            value="4. All Subaccounts",
        )
    with col_b:
        st.info(
            "💡 **Tip:** Edit Opening Balances directly in the table below and click Save."
        )

    # Filter the dataframe based on the slider
    max_len = depth_mapping[selected_depth]
    filtered_tb = tb[tb["Code"].str.len() <= max_len].copy()

    # 3. --- Interactive Table & Hierarchical Headers ---
    edited_tb = st.data_editor(
        filtered_tb,
        column_config={
            "Code": st.column_config.TextColumn("Code", disabled=True),
            "Account Name": st.column_config.TextColumn("Account Name", disabled=True),
            "Account Type": st.column_config.TextColumn("Type", disabled=True),
            "Level": None,  # Internal field
            # Editable columns for opening balances
            "Opening Balance - Debit": st.column_config.NumberColumn(
                "Opening Balance ➡️ Debit",
                min_value=0.0,
                format="%.2f",
                help="Editable for detailed accounts",
            ),
            "Opening Balance - Credit": st.column_config.NumberColumn(
                "Opening Balance ➡️ Credit",
                min_value=0.0,
                format="%.2f",
                help="Editable for detailed accounts",
            ),
            # Automatic reporting columns
            "Movement - Debit": st.column_config.NumberColumn(
                "Movement ➡️ Debit", disabled=True, format="%.2f"
            ),
            "Movement - Credit": st.column_config.NumberColumn(
                "Movement ➡️ Credit", disabled=True, format="%.2f"
            ),
            "Total - Debit": st.column_config.NumberColumn(
                "Total ➡️ Debit", disabled=True, format="%.2f"
            ),
            "Total - Credit": st.column_config.NumberColumn(
                "Total ➡️ Credit", disabled=True, format="%.2f"
            ),
            "Balance": st.column_config.NumberColumn(
                "Net Balance", disabled=True, format="%.2f"
            ),
            "Balance Type": st.column_config.TextColumn("Side", disabled=True),
        },
        use_container_width=True,
        hide_index=True,
        key="tb_inline_editor",
    )

    # Logic to save changes made directly in the table
    if st.button("💾 Save Table Modifications", type="primary"):
        has_changes = False

        for _, row in edited_tb.iterrows():
            code = str(row["Code"])

            if len(code) == 9:
                # Logic: If the user deletes a number or leaves it empty, default to 0.0
                raw_dr = row["Opening Balance - Debit"]
                raw_cr = row["Opening Balance - Credit"]

                # Check for empty/missing values (NaN) and replace with 0.0
                new_dr = float(raw_dr) if (pd.notnull(raw_dr) and raw_dr != "") else 0.0
                new_cr = float(raw_cr) if (pd.notnull(raw_cr) and raw_cr != "") else 0.0

                current_ob = st.session_state.opening_balances.get(
                    code, {"dr": 0.0, "cr": 0.0}
                )
                if current_ob["dr"] != new_dr or current_ob["cr"] != new_cr:
                    update_opening_balance(code, new_dr, new_cr)
                    has_changes = True

        if has_changes:
            st.success("Your modifications have been saved and the totals updated.")
            st.rerun()
        else:
            st.info("No changes were detected in the detailed accounts.")
