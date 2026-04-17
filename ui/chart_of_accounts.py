"""
Chart of Accounts page UI.
"""

import streamlit as st

from logic.accounts import build_accounts_display_df


def render():
    st.markdown(
        """
    <div class='main-header'>
      <h1>📖 دليل الحسابات</h1>
      <p>Chart of Accounts — الدليل الكامل لجميع الحسابات</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "🔍 بحث عن حساب (بالاسم أو الكود)", placeholder="ابحث هنا..."
    )

    df = build_accounts_display_df()

    if search:
        mask = df["اسم الحساب"].str.contains(search, na=False) | df["الكود"].astype(
            str
        ).str.contains(search)
        df = df[mask]

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🏦 الأصول",
            "⚖️ الإلتزامات وحقوق الملكية",
            "📉 المصروفات",
            "💰 الإيرادات",
        ]
    )

    type_labels = ["أصول", "التزامات وحقوق ملكية", "مصروفات", "إيرادات"]
    tabs = [tab1, tab2, tab3, tab4]

    for tab, type_label in zip(tabs, type_labels):
        with tab:
            subset = df[df["النوع"] == type_label][["الكود", "اسم الحساب", "المستوى"]]
            st.dataframe(subset, use_container_width=True, hide_index=True, height=500)
