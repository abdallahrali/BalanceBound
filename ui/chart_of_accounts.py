"""
Chart of Accounts page UI - Finalized & Clean Version.
"""

import pandas as pd
import streamlit as st
# استيراد الوظائف من ملف الـ logic
from logic.accounts import build_accounts_display_df, save_accounts_to_csv

def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>📖 Chart of Accounts</h1>
      <p>Management and structure of the company's financial accounts</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 1. تحميل البيانات
    df = build_accounts_display_df()

    st.info("💡 **Tip:** Edit account names directly in the table cells and press **Enter**.")

    # 2. التبويبات
    tabs = st.tabs(["🏛️ Assets", "⚖️ Liabilities & Equity", "📉 Expenses", "💰 Revenues"])
    prefixes = ["1", "2", "3", "4"]

    for i, tab in enumerate(tabs):
        with tab:
            filtered_df = df[df["Code"].astype(str).str.startswith(prefixes[i])].copy()
            
            # 3. محرر البيانات
            edited_df = st.data_editor(
                filtered_df,
                column_config={
                    "Code": st.column_config.TextColumn("Code", disabled=True),
                    "Account Name": st.column_config.TextColumn("Account Name", width="large"),
                    "Type": st.column_config.TextColumn("Type", disabled=True),
                    "Level": st.column_config.TextColumn("Level", disabled=True),
                },
                hide_index=True,
                use_container_width=True,
                key=f"editor_tab_{prefixes[i]}"
            )

            # 4. الحفظ عند التغيير
            if not edited_df.equals(filtered_df):
                # تحديث الـ DataFrame الرئيسي بالأسماء الجديدة
                for index, row in edited_df.iterrows():
                    df.loc[df["Code"] == row["Code"], "Account Name"] = row["Account Name"]
                
                # استدعاء وظيفة الحفظ من ملف الـ logic
                save_accounts_to_csv(df)
                
                st.success(f"Changes synced successfully!")
                st.rerun()