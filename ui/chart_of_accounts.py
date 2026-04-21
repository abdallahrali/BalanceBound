# BalanceBound_new/ui/chart_of_accounts.py

import re

import pandas as pd
import streamlit as st

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


def normalize_arabic(text):
    if not isinstance(text, str):
        return str(text)
    text = re.sub(r"[أإآ]", "ا", text)
    text = re.sub(r"[ى]", "ي", text)
    text = re.sub(r"[ة]", "ه", text)
    return text


@st.dialog("Confirm Account Deletion")
def confirm_delete_dialog(deleted_codes_list, full_df):
    st.markdown(
        """
        <style>
        div[data-testid="stDialog"] button[aria-label="Close"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="alert warning"><span class="alert-icon">⚠️</span>'
        f"You are about to delete <strong>{len(deleted_codes_list)}</strong> account(s). "
        f"This will cascade to all child accounts and cannot be undone.</div>",
        unsafe_allow_html=True,
    )

    all_affected_codes = set()
    affected_accounts_info = []

    for code in deleted_codes_list:
        mask = full_df["Code"].astype(str).str.startswith(str(code))
        children = full_df[mask]
        for _, row in children.iterrows():
            if row["Code"] not in all_affected_codes:
                all_affected_codes.add(row["Code"])
                affected_accounts_info.append((row["Code"], row["Account Name"]))

    if affected_accounts_info:
        st.markdown(
            f'<div class="alert error"><span class="alert-icon">❌</span>'
            f"<strong>{len(affected_accounts_info)}</strong> total accounts will be permanently deleted:</div>",
            unsafe_allow_html=True,
        )
        for c, n in affected_accounts_info:
            marker = "🔴 **Selected**" if c in deleted_codes_list else "⭕ Child"
            st.write(f"- {marker} · `{c}` — {n}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Delete All", use_container_width=True, type="primary"):
            for code in deleted_codes_list:
                delete_account_cascade(code)
            st.session_state["success_toast"] = (
                f"Successfully deleted {len(deleted_codes_list)} account(s) and their children."
            )
            st.session_state["editor_key"] += 1
            st.rerun()
    with col2:
        if st.button("✕ Cancel", use_container_width=True):
            st.session_state["editor_key"] += 1
            st.rerun()


def render():
    if "success_toast" in st.session_state:
        st.toast(st.session_state.pop("success_toast"), icon="✅")

    st.markdown(
        """
    <div class="page-header">
      <div>
        <div class="ph-label">Configuration</div>
        <h1>Chart of Accounts</h1>
        <p>Manage the hierarchical structure of all financial accounts</p>
      </div>
      <div class="ph-icon">📖</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    if "editor_key" not in st.session_state:
        st.session_state["editor_key"] = 0
    if "add_key" not in st.session_state:
        st.session_state["add_key"] = 0
    if "search_key" not in st.session_state:
        st.session_state["search_key"] = 0

    tab_view, tab_add, tab_delete = st.tabs(
        ["📄  View Accounts", "➕  Add Account", "🗑️  Delete Account"]
    )

    df = build_accounts_display_df()

    # ── TAB 1: VIEW ──
    # with tab_view:
    #     st.markdown(
    #         '<div class="section-header"><span class="sh-title">Search & Filter</span>'
    #         '<div class="sh-divider"></div></div>',
    #         unsafe_allow_html=True,
    #     )

    #     col1, col2, col3, col4 = st.columns([2, 1.2, 1.2, 1.2])

    #     with col1:
    #         s_col, x_col = st.columns([85, 15])
    #         with s_col:
    #             if HAS_KEYUP:
    #                 search_query = st_keyup(
    #                     "Search by Code or Name",
    #                     placeholder="Type to search instantly...",
    #                     key=f"search_{st.session_state['search_key']}",
    #                 )
    #             else:
    #                 search_query = st.text_input(
    #                     "Search by Code or Name",
    #                     placeholder="Type code or account name...",
    #                     key=f"search_{st.session_state['search_key']}",
    #                 )
    #         with x_col:
    #             st.markdown(
    #                 "<div style='margin-top:28px;'></div>", unsafe_allow_html=True
    #             )
    #             if st.button(
    #                 "✕",
    #                 key="clear_search",
    #                 help="Clear search",
    #                 use_container_width=True,
    #             ):
    #                 st.session_state["search_key"] += 1
    #                 st.rerun()

    #     with col2:
    #         type_options = df["Type"].unique()
    #         selected_types = st.multiselect("Filter by Type", options=type_options)

    #     with col3:
    #         level_options = df["Level"].unique()
    #         selected_levels = st.multiselect("Filter by Level", options=level_options)

    #     with col4:
    #         sort_by = st.selectbox(
    #             "Sort By",
    #             ["Code (Ascending)", "Code (Descending)", "Name (A–Z)", "Name (Z–A)"],
    #         )

    #     filtered_df = df.copy()

    #     if search_query:
    #         norm_query = normalize_arabic(search_query).lower()
    #         normalized_names = (
    #             filtered_df["Account Name"].apply(normalize_arabic).str.lower()
    #         )
    #         mask = filtered_df["Code"].astype(str).str.contains(
    #             norm_query, case=False
    #         ) | normalized_names.str.contains(norm_query, case=False)
    #         filtered_df = filtered_df[mask]

    #     if selected_types:
    #         filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]
    #     if selected_levels:
    #         filtered_df = filtered_df[filtered_df["Level"].isin(selected_levels)]

    #     sort_map = {
    #         "Code (Ascending)": ("Code", True),
    #         "Code (Descending)": ("Code", False),
    #         "Name (A–Z)": ("Account Name", True),
    #         "Name (Z–A)": ("Account Name", False),
    #     }
    #     col_s, asc_s = sort_map[sort_by]
    #     filtered_df = filtered_df.sort_values(col_s, ascending=asc_s).reset_index(
    #         drop=True
    #     )

    #     st.markdown(
    #         '<div class="alert info"><span class="alert-icon">💡</span>'
    #         "You can edit account names directly in the table cells. "
    #         "Select rows and press <strong>Delete</strong> to remove accounts (cascades to children).</div>",
    #         unsafe_allow_html=True,
    #     )

    #     if filtered_df.empty:
    #         st.markdown(
    #             '<div class="alert warning"><span class="alert-icon">🔍</span>'
    #             "No accounts match your search criteria. Try a different query or clear filters.</div>",
    #             unsafe_allow_html=True,
    #         )
    #     else:
    #         level_styles = {
    #             "Type": "background-color: rgba(212,175,55,0.2); color: #D4AF37; font-weight: bold;",
    #             "Category": "background-color: rgba(212,175,55,0.1); color: #F0D060;",
    #             "Account": "background-color: rgba(59,130,246,0.1); color: #93C5FD;",
    #             "Sub-account": "background-color: rgba(255,255,255,0.04); color: #E2E8F0;",
    #         }

    #         def apply_code_style(row):
    #             style = level_styles.get(row["Level"], "")
    #             return [style if col == "Code" else "" for col in row.index]

    #         styled_df = filtered_df.style.apply(apply_code_style, axis=1)

    #         edited_df = st.data_editor(
    #             styled_df,
    #             column_config={
    #                 "Code": st.column_config.TextColumn("Code", disabled=True),
    #                 "Account Name": st.column_config.TextColumn(
    #                     "Account Name", width="large"
    #                 ),
    #                 "Type": st.column_config.TextColumn("Type", disabled=True),
    #                 "Level": st.column_config.TextColumn("Level", disabled=True),
    #             },
    #             hide_index=True,
    #             use_container_width=True,
    #             num_rows="dynamic",
    #             key=f"view_editor_{st.session_state['editor_key']}",
    #         )

    #         if len(edited_df) > len(filtered_df):
    #             st.markdown(
    #                 '<div class="alert error"><span class="alert-icon">🚫</span>'
    #                 "Adding accounts directly in the table is disabled. "
    #                 "Please use the <strong>Add Account</strong> tab instead.</div>",
    #                 unsafe_allow_html=True,
    #             )
    #             st.session_state["editor_key"] += 1
    #             st.rerun()
    #         elif len(edited_df) < len(filtered_df):
    #             deleted_codes = list(set(filtered_df["Code"]) - set(edited_df["Code"]))
    #             if deleted_codes:
    #                 confirm_delete_dialog(deleted_codes, df)
    #         elif not edited_df.equals(filtered_df):
    #             changes_made = False
    #             for _, row in edited_df.iterrows():
    #                 code = row["Code"]
    #                 new_name = row["Account Name"]
    #                 old_name = filtered_df[filtered_df["Code"] == code][
    #                     "Account Name"
    #                 ].values[0]
    #                 if new_name != old_name:
    #                     df.loc[df["Code"] == code, "Account Name"] = new_name
    #                     changes_made = True
    #             if changes_made:
    #                 save_accounts_to_csv(df)
    #                 st.session_state["success_toast"] = (
    #                     "Account names updated successfully!"
    #                 )
    #                 st.session_state["editor_key"] += 1
    #                 st.rerun()

    # ── TAB 1: VIEW ──
    with tab_view:
        st.markdown(
            '<div class="section-header"><span class="sh-title">Search & Filter</span>'
            '<div class="sh-divider"></div></div>',
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns([2, 1.2, 1.2, 1.2])

        with col1:
            s_col, x_col = st.columns([85, 15])
            with s_col:
                if HAS_KEYUP:
                    search_query = st_keyup(
                        "Search by Code or Name",
                        placeholder="Type to search instantly...",
                        key=f"search_{st.session_state['search_key']}",
                    )
                else:
                    search_query = st.text_input(
                        "Search by Code or Name",
                        placeholder="Type code or account name...",
                        key=f"search_{st.session_state['search_key']}",
                    )
            with x_col:
                st.markdown(
                    "<div style='margin-top:28px;'></div>", unsafe_allow_html=True
                )
                if st.button(
                    "✕",
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
                "Sort By",
                ["Code (Ascending)", "Code (Descending)", "Name (A–Z)", "Name (Z–A)"],
            )

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

        sort_map = {
            "Code (Ascending)": ("Code", True),
            "Code (Descending)": ("Code", False),
            "Name (A–Z)": ("Account Name", True),
            "Name (Z–A)": ("Account Name", False),
        }
        col_s, asc_s = sort_map[sort_by]
        filtered_df = filtered_df.sort_values(col_s, ascending=asc_s).reset_index(
            drop=True
        )

        st.markdown(
            '<div class="alert info"><span class="alert-icon">💡</span>'
            "You can edit account names directly in the table cells. "
            "Select rows and press <strong>Delete</strong> to remove accounts (cascades to children).</div>",
            unsafe_allow_html=True,
        )

        if filtered_df.empty:
            st.markdown(
                '<div class="alert warning"><span class="alert-icon">🔍</span>'
                "No accounts match your search criteria. Try a different query or clear filters.</div>",
                unsafe_allow_html=True,
            )
        else:
            level_styles = {
                "Type": "background-color: rgba(212,175,55,0.2); color: #D4AF37; font-weight: bold;",
                "Category": "background-color: rgba(212,175,55,0.1); color: #F0D060;",
                "Account": "background-color: rgba(59,130,246,0.1); color: #93C5FD;",
                "Sub-account": "background-color: rgba(255,255,255,0.04); color: #E2E8F0;",
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
                key=f"view_editor_{st.session_state['editor_key']}",
            )

            if len(edited_df) > len(filtered_df):
                st.markdown(
                    '<div class="alert error"><span class="alert-icon">🚫</span>'
                    "Adding accounts directly in the table is disabled. "
                    "Please use the <strong>Add Account</strong> tab instead.</div>",
                    unsafe_allow_html=True,
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
    # ── TAB 2: ADD ──
    with tab_add:
        st.markdown(
            '<div class="section-header"><span class="sh-title">Create New Account</span>'
            '<div class="sh-divider"></div></div>',
            unsafe_allow_html=True,
        )

        ak = st.session_state["add_key"]
        mode = st.radio(
            "Input Method",
            ["Guided (Selection)", "Manual (Code Entry)"],
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
                f"{row['code']} — {row['name']}": row["code"]
                for _, row in parents_df.iterrows()
            }

            with col2:
                selected_parent_label = st.selectbox(
                    "Parent Account",
                    options=list(parent_options.keys()),
                    key=f"add_parent_{ak}",
                )
                parent_code = (
                    parent_options[selected_parent_label] if parent_options else None
                )

            if parent_code:
                new_code = generate_next_code(parent_code, target_level)
                st.markdown(
                    f'<div class="alert info"><span class="alert-icon">🔢</span>'
                    f"Auto-generated account code: <strong>{new_code}</strong></div>",
                    unsafe_allow_html=True,
                )

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
                    parent_display = f"⚠️ Parent {parent_code} does not exist"
                    st.markdown(
                        f'<div class="alert error"><span class="alert-icon">❌</span>'
                        f"Parent account <strong>{parent_code}</strong> does not exist. "
                        f"Please create it first.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    parent_display = parent_code
                    st.markdown(
                        f'<div class="alert success"><span class="alert-icon">✅</span>'
                        f"Level: <strong>{inferred_level}</strong> · "
                        f"Parent: <strong>{parent_display}</strong></div>",
                        unsafe_allow_html=True,
                    )
                new_code = manual_code

        new_name = st.text_input(
            "Account Name",
            placeholder="e.g. Cash and Cash Equivalents",
            key=f"add_name_{ak}",
        )

        col_save, _ = st.columns([1, 3])
        with col_save:
            if st.button("➕ Create Account", type="primary"):
                if not new_name:
                    st.markdown(
                        '<div class="alert error"><span class="alert-icon">❌</span>'
                        "Account name is required.</div>",
                        unsafe_allow_html=True,
                    )
                elif "⚠️" in parent_display:
                    st.markdown(
                        '<div class="alert error"><span class="alert-icon">❌</span>'
                        "Cannot save: the parent account does not exist.</div>",
                        unsafe_allow_html=True,
                    )
                elif new_code in df["Code"].values:
                    st.markdown(
                        '<div class="alert error"><span class="alert-icon">❌</span>'
                        f"Account code <strong>{new_code}</strong> already exists.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    new_row = pd.DataFrame(
                        [{"Code": new_code, "Account Name": new_name}]
                    )
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    save_accounts_to_csv(updated_df)
                    st.session_state["success_toast"] = (
                        f"Account '{new_name}' ({new_code}) created successfully!"
                    )
                    st.session_state["editor_key"] += 1
                    st.session_state["add_key"] += 1
                    st.rerun()

    # ── TAB 3: DELETE ──
    with tab_delete:
        st.markdown(
            '<div class="section-header"><span class="sh-title">Remove Account</span>'
            '<div class="sh-divider"></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="alert warning"><span class="alert-icon">⚠️</span>'
            "Deleting a parent account will <strong>cascade</strong> and permanently remove "
            "all of its child categories, accounts, and sub-accounts. This cannot be undone.</div>",
            unsafe_allow_html=True,
        )

        # Filter out 1-digit 'Type' accounts from the deletion list
        options = {
            f"({row['Code']}) {row['Account Name']}": row["Code"]
            for _, row in df.iterrows()
            if len(str(row["Code"])) > 1
        }

        if not options:
            st.info("No accounts available to delete.")
        else:
            to_delete_label = st.selectbox(
                "Select Account to Remove",
                options=list(options.keys()),
                key="delete_account_selectbox",
            )
            if to_delete_label:
                target_code = options[to_delete_label]
                col_del, _ = st.columns([1, 3])
                with col_del:
                    if st.button("🗑️ Delete Account", type="primary"):
                        confirm_delete_dialog([target_code], df)
