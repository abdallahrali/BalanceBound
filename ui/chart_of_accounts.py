"""
Chart of Accounts page UI - Finalized & Clean Version.
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

LEVEL_COLORS = {
    1: "#e74c3c",   # Main - Red
    2: "#e67e22",   # Group - Orange
    3: "#f39c12",   # Category - Yellow/Gold
    4: "#27ae60",   # Account - Green
    9: "#3498db",   # Sub-account - Blue
}

LEVEL_COLORS_LIGHT = {
    1: "#fadbd8",   # Main - Light Red
    2: "#fdebd0",   # Group - Light Orange
    3: "#fcf3cf",   # Category - Light Yellow
    4: "#d5f5e3",   # Account - Light Green
    9: "#d6eaf8",   # Sub-account - Light Blue
}

def inject_level_colors_css():
    st.markdown(
        """
        <style>
        .level-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 12px;
            color: white;
            text-align: center;
            min-width: 80px;
        }
        .level-main { background-color: #e74c3c; }
        .level-group { background-color: #e67e22; }
        .level-category { background-color: #f39c12; }
        .level-account { background-color: #27ae60; }
        .level-sub { background-color: #3498db; }
        
        .row-level-1 { background-color: #fadbd8 !important; }
        .row-level-2 { background-color: #fdebd0 !important; }
        .row-level-3 { background-color: #fcf3cf !important; }
        .row-level-4 { background-color: #d5f5e3 !important; }
        .row-level-9 { background-color: #d6eaf8 !important; }
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

    col1, col2 = st.columns([1, 1])
    with col1:
        st.info("💡 **Tip:** Edit account names directly in the table cells and press **Enter**.")
    with col2:
        with st.expander("➕ Add New Account"):
            add_form_col1, add_form_col2, add_form_col3 = st.columns([1, 2, 1])
            with add_form_col1:
                new_code = st.text_input("Code", key="new_acc_code", placeholder="e.g. 101005")
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
                parent_options = [""] + [f"{code} - {name[:30]}" for code, name in parent_options]
            
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

    for i, tab in enumerate(tabs):
        with tab:
            filtered_df = df[df["Code"].astype(str).str.startswith(prefixes[i])].copy()
            
            cols = st.columns([6, 2, 1, 1])
            with cols[0]:
                st.markdown("**Account Name**")
            with cols[1]:
                st.markdown("**Level**")
            with cols[2]:
                st.markdown("**Delete**")
            with cols[3]:
                st.markdown("**Type**")

            for idx, row in filtered_df.iterrows():
                code = str(row["Code"])
                level = get_code_level(code)
                level_label = row["Level"]
                
                level_class = f"level-{level}"
                if level == 9:
                    level_class = "level-sub"
                
                bg_color = LEVEL_COLORS_LIGHT.get(level, "#f0f0f0")
                
                with st.container():
                    row_cols = st.columns([6, 2, 1, 1])
                    with row_cols[0]:
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
                    with row_cols[1]:
                        st.markdown(f'<span class="level-badge {level_class}">{level_label}</span>', unsafe_allow_html=True)
                    with row_cols[2]:
                        if st.button("🗑️", key=f"del_{code}", help=f"Delete {row['Account Name']} and children"):
                            success, msg = delete_account(code, cascade=True)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    with row_cols[3]:
                        st.write(row["Type"])

    st.markdown("---")
    st.markdown("### 📊 Level Legend")
    legend_cols = st.columns(5)
    legend_items = [
        (1, "Main", "#e74c3c"),
        (2, "Group", "#e67e22"),
        (3, "Category", "#f39c12"),
        (4, "Account", "#27ae60"),
        (9, "Sub-account", "#3498db"),
    ]
    for j, (level, label, color) in enumerate(legend_items):
        with legend_cols[j]:
            st.markdown(
                f'<span style="background-color: {color}; color: white; padding: 5px 12px; border-radius: 15px; font-size: 12px; font-weight: 600;">{label}</span>',
                unsafe_allow_html=True,
            )