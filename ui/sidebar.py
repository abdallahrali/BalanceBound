"""
Sidebar navigation component.
"""

from datetime import datetime

import streamlit as st

from config import APP_VERSION, PAGES
from logic.journal import get_all_entries


def render_sidebar() -> str:
    """
    Render the sidebar and return the selected page key.
    """
    st.sidebar.markdown(
        f"""
    <div style='text-align:center; padding: 15px 0;'>
      <div style='font-size:40px;'>📊</div>
      <div style='font-size:18px; font-weight:700; color:#0f3460;'>نظام المحاسبة</div>
      <div style='font-size:11px; color:#888;'>Accounting System v{APP_VERSION}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("---")

    selected_label = st.sidebar.radio(
        "", list(PAGES.keys()), label_visibility="collapsed"
    )
    page = PAGES[selected_label]

    st.sidebar.markdown("---")

    total = len(get_all_entries())
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.sidebar.markdown(
        f"""
    <div style='text-align:center; font-size:12px; color:#888;'>
      إجمالي القيود: <b>{total}</b><br>
      آخر تحديث: {now}
    </div>
    """,
        unsafe_allow_html=True,
    )

    return page
