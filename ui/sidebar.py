"""
Sidebar navigation — button-based, professional dark design.
"""

from datetime import datetime

import streamlit as st

from config import APP_VERSION, PAGES
from logic.journal import get_all_entries

# Map page keys to icons
_ICONS = {
    "dashboard": "󰕮",  # we'll use text fallbacks
    "chart_of_accounts": "",
    "journal_entries": "",
    "trial_balance": "",
    "income_statement": "",
    "balance_sheet": "",
}

_NAV = [
    ("dashboard", "🏠", "Dashboard"),
    ("chart_of_accounts", "📖", "Chart of Accounts"),
    ("journal_entries", "✍️", "Journal Entries"),
    ("trial_balance", "⚖️", "Trial Balance"),
    ("income_statement", "💹", "Income Statement"),
    ("balance_sheet", "🏛️", "Balance Sheet"),
]


def render_sidebar() -> str:
    """Render sidebar and return the selected page key."""

    # ── Initialise active page in session state ──────────────────────────────
    if "active_page" not in st.session_state:
        st.session_state.active_page = "dashboard"

    # ── Logo block ───────────────────────────────────────────────────────────
    st.sidebar.markdown(
        f"""
        <div class="sb-logo">
            <div class="sb-logo-mark">⚖️</div>
            <div class="sb-logo-text">
                <span class="sb-logo-name">BalanceBound</span>
                <span class="sb-logo-ver"></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Section label ─────────────────────────────────────────────────────────
    st.sidebar.markdown(
        "<p class='sb-section-label'>Main Menu</p>",
        unsafe_allow_html=True,
    )

    # ── Nav buttons ───────────────────────────────────────────────────────────
    for key, icon, label in _NAV:
        is_active = st.session_state.active_page == key

        # Use Streamlit's native "primary" type to highlight the active button
        clicked = st.sidebar.button(
            f"{icon}  {label}",
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        )

        if clicked:
            st.session_state.active_page = key
            st.rerun()
    # for key, icon, label in _NAV:
    #     is_active = st.session_state.active_page == key
    #     btn_class = "sb-nav-btn sb-nav-btn--active" if is_active else "sb-nav-btn"

    #     # We wrap each button in a styled div via markdown + use_container_width
    #     st.sidebar.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
    #     clicked = st.sidebar.button(
    #         f"{icon}  {label}",
    #         key=f"nav_{key}",
    #         use_container_width=True,
    #     )
    #     st.sidebar.markdown("</div>", unsafe_allow_html=True)

    #     if clicked:
    #         st.session_state.active_page = key
    #         st.rerun()

    # ── Divider + stats ───────────────────────────────────────────────────────
    # total = len(get_all_entries())
    # now = datetime.now().strftime("%d %b %Y, %H:%M")

    # st.sidebar.markdown(
    #     f"""
    #     <div class="sb-stats">
    #         <div class="sb-stats-row">
    #             <span class="sb-stats-label">Journal Entries</span>
    #             <span class="sb-stats-val">{total}</span>
    #         </div>
    #         <div class="sb-stats-row">
    #             <span class="sb-stats-label">Last Refreshed</span>
    #             <span class="sb-stats-val">{now}</span>
    #         </div>
    #     </div>
    #     """,
    #     unsafe_allow_html=True,
    # )

    return st.session_state.active_page
