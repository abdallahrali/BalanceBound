"""
Chart of Accounts page UI.
"""

import pandas as pd
import streamlit as st
from logic.accounts import (
    build_accounts_display_df,
    save_accounts_to_csv,
    add_account,
    delete_account,
    get_available_parents,
    get_code_level,
)


def inject_level_colors_css():
    st.markdown(
        """
        <style>
        .level-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 11px;
            color: white;
            text-align: center;
        }
        .level-1 { background-color: #e74c3c; }
        .level-2 { background-color: #e67e22; }
        .level-3 { background-color: #f39c12; }
        .level-4 { background-color: #27ae60; }
        .level-9 { background-color: #3498db; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render():
    inject_level_colors_css()
    
    st.markdown(
        """
    <div class='main-header'>
      <h1>📖 Chart of Accounts</h1>
      <p>Management and structure of the company's financial accounts</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    df = build_accounts_display_df()

    with st.expander("➕ Add New Account"):
        add_form_col1, add_form_col2, add_form_col3 = st.columns([1, 2, 1])
        with add_form_col1:
            new_code = st.text_input("Code", key="new_acc_code", placeholder="e.g. 101005001")
        with add_form_col2:
            new_name = st.text_input("Name", key="new_acc_name", placeholder="Account name")
        with add_form_col3:
            new_level = st.selectbox(
                "Level",
                options=[(1, "Main"), (2, "Group"), (3, "Category"), (4, "Account"), (9, "Sub-account")],
                format_func=lambda x: x[1],
                key="new_acc_level"
            )
        
        parent_options = []
        if new_level[0] > 1:
            parent_options = get_available_parents(new_level[0])
            parent_options = [""] + [f"{code} - {name[:40]}" for code, name in parent_options]
        
        selected_parent = ""
        if new_level[0] > 1:
            selected_parent = st.selectbox(
                "Parent Account",
                options=parent_options,
                key="new_acc_parent",
                help=f"Select parent for {new_level[1]} level"
            )
        
        if st.button("➕ Add Account", key="btn_add_acc"):
            if not new_code or not new_name:
                st.error("⚠️ Code and Name are required")
            else:
                parent_code = ""
                if selected_parent:
                    parent_code = selected_parent.split(" - ")[0]
                success, msg = add_account(new_code, new_name, parent_code)
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    tabs = st.tabs(["🏛️ Assets", "⚖️ Liabilities & Equity", "📉 Expenses", "💰 Revenues"])
    prefixes = ["1", "2", "3", "4"]

    level_labels = {1: "Main", 2: "Group", 3: "Category", 4: "Account", 9: "Sub"}

    for i, tab in enumerate(tabs):
        with tab:
            filtered_df = df[df["Code"].astype(str).str.startswith(prefixes[i])].copy()
            
            header_cols = st.columns([1, 4, 1, 1])
            with header_cols[0]:
                st.markdown("**Code**")
            with header_cols[1]:
                st.markdown("**Account Name**")
            with header_cols[2]:
                st.markdown("**Level**")
            with header_cols[3]:
                st.markdown("")

            for idx, row in filtered_df.iterrows():
                code = str(row["Code"])
                level = get_code_level(code)
                level_label = level_labels.get(level, f"L{level}")
                
                level_class = f"level-{level}"
                
                row_cols = st.columns([1, 4, 1, 1])
                with row_cols[0]:
                    st.code(code, language=None)
                with row_cols[1]:
                    edited_name = st.text_input(
                        f"name_{code}",
                        value=row["Account Name"],
                        key=f"input_{code}",
                        label_visibility="collapsed",
                    )
                    if edited_name != row["Account Name"]:
                        df.loc[df["Code"] == code, "Account Name"] = edited_name
                        save_accounts_to_csv(df)
                        st.rerun()
                with row_cols[2]:
                    st.markdown(f'<span class="{level_class}">{level_label}</span>', unsafe_allow_html=True)
                with row_cols[3]:
                    if st.button("🗑️", key=f"del_{code}", help=f"Delete {row['Account Name']}"):
                        success, msg = delete_account(code, cascade=True)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)