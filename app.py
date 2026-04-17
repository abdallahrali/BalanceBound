"""
Arabic Accounting System — Main Streamlit Entry Point
نظام المحاسبة — نقطة الدخول الرئيسية
"""

import streamlit as st

from config import APP_ICON, APP_TITLE
from logic.journal import init_session_state
from ui.sidebar import render_sidebar
from ui.styles import inject_css

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Inject CSS ──────────────────────────────────────────────────────────────
inject_css()

# ─── Initialize State ────────────────────────────────────────────────────────
init_session_state()

# ─── Sidebar Navigation ──────────────────────────────────────────────────────
page = render_sidebar()

# ─── Page Router ──────────────────────────────────────────────────────────────
if page == "dashboard":
    from ui.dashboard import render

    render()

elif page == "chart_of_accounts":
    from ui.chart_of_accounts import render

    render()

elif page == "journal_entries":
    from ui.journal_entries import render

    render()

elif page == "trial_balance":
    from ui.trial_balance import render

    render()

elif page == "income_statement":
    from ui.income_statement import render

    render()

elif page == "balance_sheet":
    from ui.balance_sheet import render

    render()

else:
    st.error(f"الصفحة غير موجودة: {page}")
