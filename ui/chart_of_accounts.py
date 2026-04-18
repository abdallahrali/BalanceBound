# BalanceBound (copy 1)/ui/chart_of_accounts.py

import re

import pandas as pd
import streamlit as st

# Attempt to load st_keyup for real-time instant search
try:
    from st_keyup import st_keyup

    HAS_KEYUP = True
except ImportError:
    HAS_KEYUP = False

from logic.accounts import (
    build_accounts_display_df,
    delete_account_cascade,
    generate_next_code,
    get_parent_for_code,
    get_potential_parents,
    save_accounts_to_csv,
)


# --- HELPER: Arabic Normalization ---
def normalize_arabic(text):
    """Normalizes Arabic text for flexible searching (e.g., أ to ا, ى to ي)"""
    if not isinstance(text, str):
        return str(text)
    text = re.sub(r"[أإآ]", "ا", text)
    text = re.sub(r"[ى]", "ي", text)
    text = re.sub(r"[ة]", "ه", text)
    return text


# --- DIALOG: Multi-Delete Confirmation ---
@st.dialog("Confirm Deletion")
def confirm_delete_dialog(deleted_codes_list, full_df):
    # INJECT CSS TO HIDE THE 'X' CLOSE BUTTON
    st.markdown(
        """
        <style>
        div[data-testid="stDialog"] button[aria-label="Close"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        f"Are you sure you want to delete **{len(deleted_codes_list)}** selected account(s)?"
    )

    # Gather all affected accounts (including cascaded children)
    all_affected_codes = set()
    affected_accounts_info = []

    for code in deleted_codes_list:
        mask = full_df["Code"].astype(str).str.startswith(str(code))
        children = full_df[mask]
        for _, row in children.iterrows():
            if row["Code"] not in all_affected_codes:
                all_affected_codes.add(row["Code"])
                affected_accounts_info.append((row["Code"], row["Account Name"]))

    if len(affected_accounts_info) > 0:
        st.error(
            f"⚠️ A total of **{len(affected_accounts_info)}** accounts will be deleted (Cascade Delete):"
        )
        for c, n in affected_accounts_info:
            if c in deleted_codes_list:
                st.write(f"- 🔴 **{c}**: {n} *(Selected)*")
            else:
                st.write(f"- ⭕ **{c}**: {n} *(Child)*")
    else:
        st.error("⚠️ This action cannot be undone.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Delete All", use_container_width=True, type="primary"):
            for code in deleted_codes_list:
                delete_account_cascade(code)

            # Save success message to survive the rerun
            st.session_state["success_toast"] = (
                f"Successfully deleted {len(deleted_codes_list)} accounts and their children."
            )
            st.session_state["editor_key"] += 1
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state["editor_key"] += 1
            st.rerun()


def render():
    # 1. Check for pending toasts before rendering anything else
    if "success_toast" in st.session_state:
        st.toast(st.session_state.pop("success_toast"), icon="✅")

    st.markdown(
        "<div class='main-header'><h1>📖 Chart of Accounts</h1></div>",
        unsafe_allow_html=True,
    )

    # State keys to force widget resets
    if "editor_key" not in st.session_state:
        st.session_state["editor_key"] = 0
    if "add_key" not in st.session_state:
        st.session_state["add_key"] = 0
    if "search_key" not in st.session_state:
        st.session_state["search_key"] = 0

    tab_view, tab_add, tab_delete = st.tabs(
        ["📄 View", "➕ Add Account", "🗑️ Delete Account"]
    )

    df = build_accounts_display_df()

    def get_accounts_to_delete(code):
        mask = df["Code"].astype(str).str.startswith(str(code))
        return df[mask]

    # --- TAB 1: VIEW ---
    with tab_view:
        st.markdown("### 🔍 Search, Filter & Sort")

        col1, col2, col3, col4 = st.columns([2, 1.2, 1.2, 1.2])

        with col1:
            # Tightly packed columns to make the 'X' button sit flush with the input
            s_col, x_col = st.columns([85, 15])
            with s_col:
                if HAS_KEYUP:
                    search_query = st_keyup(
                        "Instant Search",
                        placeholder="Type Code or Name...",
                        key=f"search_{st.session_state['search_key']}",
                    )
                else:
                    search_query = st.text_input(
                        "Search",
                        placeholder="Install st-keyup for instant search",
                        key=f"search_{st.session_state['search_key']}",
                    )
            with x_col:
                st.markdown(
                    "<div style='margin-top: 28px;'></div>", unsafe_allow_html=True
                )
                if st.button(
                    "❌",
                    key="clear_search",
                    help="Clear search",
                    use_container_width=True,
                ):
                    st.session_state["search_key"] += 1
                    st.rerun()

        with col2:
            type_options = df["Type"].unique()
            selected_types = st.multiselect("Filter by Type", options=type_options)

        with col3:
            level_options = df["Level"].unique()
            selected_levels = st.multiselect("Filter by Level", options=level_options)

        with col4:
            sort_by = st.selectbox(
                "🔀 Sort Table By:",
                [
                    "Code (Ascending)",
                    "Code (Descending)",
                    "Account Name (A-Z)",
                    "Account Name (Z-A)",
                ],
            )

        # Apply Filters
        filtered_df = df.copy()

        if search_query:
            norm_query = normalize_arabic(search_query).lower()
            normalized_names = (
                filtered_df["Account Name"].apply(normalize_arabic).str.lower()
            )

            mask = filtered_df["Code"].astype(str).str.contains(
                norm_query, case=False
            ) | normalized_names.str.contains(norm_query, case=False)
            filtered_df = filtered_df[mask]

        if selected_types:
            filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]

        if selected_levels:
            filtered_df = filtered_df[filtered_df["Level"].isin(selected_levels)]

        # Apply Sorting Programmatically
        if sort_by == "Code (Ascending)":
            filtered_df = filtered_df.sort_values("Code", ascending=True)
        elif sort_by == "Code (Descending)":
            filtered_df = filtered_df.sort_values("Code", ascending=False)
        elif sort_by == "Account Name (A-Z)":
            filtered_df = filtered_df.sort_values("Account Name", ascending=True)
        elif sort_by == "Account Name (Z-A)":
            filtered_df = filtered_df.sort_values("Account Name", ascending=False)

        filtered_df = filtered_df.reset_index(drop=True)

        st.info(
            "💡 **Tip:** Edit names directly in the cells. Select rows and press **Delete** to remove them."
        )

        if filtered_df.empty:
            st.warning("No accounts match your search criteria.")
        else:
            level_styles = {
                "Type": "background-color: #0f3460; color: white; font-weight: bold;",
                "Category": "background-color: #16427d; color: #e0e0e0;",
                "Account": "background-color: #2e5a91; color: #d0d0d0;",
                "Sub-account": "background-color: #4a77a8; color: #ffffff;",
            }

            def apply_code_style(row):
                style = level_styles.get(row["Level"], "")
                return [style if col == "Code" else "" for col in row.index]

            styled_df = filtered_df.style.apply(apply_code_style, axis=1)

            edited_df = st.data_editor(
                styled_df,
                column_config={
                    "Code": st.column_config.TextColumn("Code", disabled=True),
                    "Account Name": st.column_config.TextColumn(
                        "Account Name", width="large"
                    ),
                    "Type": st.column_config.TextColumn("Type", disabled=True),
                    "Level": st.column_config.TextColumn("Level", disabled=True),
                },
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic",
                key=f"view_editor_{st.session_state['editor_key']}",
            )

            if len(edited_df) > len(filtered_df):
                st.error(
                    "⚠️ Adding accounts directly from the table is disabled. Please use the '➕ Add Account' tab."
                )
                st.session_state["editor_key"] += 1
                st.rerun()

            elif len(edited_df) < len(filtered_df):
                deleted_codes = list(set(filtered_df["Code"]) - set(edited_df["Code"]))
                if deleted_codes:
                    confirm_delete_dialog(deleted_codes, df)

            elif not edited_df.equals(filtered_df):
                changes_made = False
                for _, row in edited_df.iterrows():
                    code = row["Code"]
                    new_name = row["Account Name"]
                    old_name = filtered_df[filtered_df["Code"] == code][
                        "Account Name"
                    ].values[0]

                    if new_name != old_name:
                        df.loc[df["Code"] == code, "Account Name"] = new_name
                        changes_made = True

                if changes_made:
                    save_accounts_to_csv(df)
                    st.session_state["success_toast"] = (
                        "Account names updated successfully!"
                    )
                    st.session_state["editor_key"] += 1
                    st.rerun()

    # --- TAB 2: ADD ---
    with tab_add:
        st.subheader("Create New Account")

        ak = st.session_state["add_key"]

        mode = st.radio(
            "Input Method",
            ["Guided (Selection)", "Manual (Code)"],
            horizontal=True,
            key=f"add_mode_{ak}",
        )

        new_code = ""
        parent_display = "N/A"

        if mode == "Guided (Selection)":
            col1, col2 = st.columns(2)
            with col1:
                target_level = st.selectbox(
                    "Account Level",
                    ["Category", "Account", "Sub-account"],
                    key=f"add_level_{ak}",
                )

            parents_df = get_potential_parents(target_level)
            parent_options = {
                f"{row['code']} - {row['name']}": row["code"]
                for _, row in parents_df.iterrows()
            }

            with col2:
                selected_parent_label = st.selectbox(
                    "Select Parent",
                    options=list(parent_options.keys()),
                    key=f"add_parent_{ak}",
                )
                parent_code = (
                    parent_options[selected_parent_label] if parent_options else None
                )

            if parent_code:
                new_code = generate_next_code(parent_code, target_level)
                st.info(f"Generated Code: **{new_code}**")

        else:
            manual_code = st.text_input(
                "Enter Account Code",
                placeholder="e.g. 101001005",
                key=f"add_manual_code_{ak}",
            )
            if manual_code:
                c_len = len(manual_code)
                levels_map = {3: "Category", 6: "Account", 9: "Sub-account"}
                inferred_level = levels_map.get(c_len, "Unknown")

                parent_code = get_parent_for_code(manual_code)
                all_codes = df["Code"].tolist()

                if parent_code not in all_codes:
                    parent_display = f"⚠️ PARENT {parent_code} DOES NOT EXIST"
                    st.error(parent_display)
                else:
                    parent_display = parent_code
                    st.success(f"Level: {inferred_level} | Parent: {parent_display}")

                new_code = manual_code

        new_name = st.text_input("Account Name", key=f"add_name_{ak}")
        if st.button("Save Account", type="primary"):
            if not new_name:
                st.error("Please enter an account name.")
            elif "⚠️" in parent_display:
                st.error("Cannot save: Parent does not exist.")
            elif new_code in df["Code"].values:
                st.error("This code already exists.")
            else:
                new_row = pd.DataFrame([{"Code": new_code, "Account Name": new_name}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                save_accounts_to_csv(updated_df)

                # Setup toast for next rerun and clear form
                st.session_state["success_toast"] = (
                    f"Account '{new_name}' ({new_code}) added successfully!"
                )
                st.session_state["editor_key"] += 1
                st.session_state["add_key"] += 1
                st.rerun()

    # --- TAB 3: DELETE ---
    with tab_delete:
        st.subheader("Remove Account")
        st.warning(
            "Deleting a parent account will also delete all its categories and sub-accounts."
        )

        options = {
            f"({row['Code']}) {row['Account Name']}": row["Code"]
            for _, row in df.iterrows()
        }

        to_delete_label = st.selectbox(
            "Select Account to Remove", options=list(options.keys())
        )
        if to_delete_label:
            target_code = options[to_delete_label]

            if st.button("Delete Selected Account", type="secondary"):
                confirm_delete_dialog([target_code], df)
