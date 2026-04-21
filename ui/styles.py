"""
CSS styling — Premium dark financial theme with gold accents.
"""

import streamlit as st


def inject_css():
    st.markdown(
        """
    <style>
    /* ═══════════════════════════════════════════════════════════
       FONTS
    ═══════════════════════════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Serif+Display&display=swap');

    /* ═══════════════════════════════════════════════════════════
       DESIGN TOKENS
    ═══════════════════════════════════════════════════════════ */
    :root {
        --bg:          #0D0F14;
        --bg-card:     #13161E;
        --bg-el:       #1A1D27;
        --bg-sub:      #1E2130;
        --border:      rgba(255,255,255,0.07);
        --border-gold: rgba(212,175,55,0.35);
        --gold:        #D4AF37;
        --gold-lt:     #F0D060;
        --gold-bg:     rgba(212,175,55,0.10);
        --text:        #F0F0F5;
        --text-2:      #8A8FA8;
        --text-3:      #555B70;
        --green:       #22C55E;
        --green-bg:    rgba(34,197,94,0.10);
        --red:         #EF4444;
        --red-bg:      rgba(239,68,68,0.10);
        --blue:        #3B82F6;
        --blue-bg:     rgba(59,130,246,0.10);
        --r:           12px;
        --r-sm:        8px;
    }

    /* ═══════════════════════════════════════════════════════════
       GLOBAL
    ═══════════════════════════════════════════════════════════ */
    .stApp {
        background: var(--bg) !important;
        font-family: sans-serif, 'DM Sans' !important;
        color: var(--text) !important;
    }
    * { box-sizing: border-box; }

    /* ═══════════════════════════════════════════════════════════
       SIDEBAR SHELL
    ═══════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 0 !important;
    }
    /* Remove default Streamlit sidebar padding so we control everything */
    [data-testid="stSidebar"] .block-container {
        padding: 0 !important;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 0 !important;
    }

    /* ── Logo ─────────────────────────────────────────────────── */
    .sb-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 22px 20px 18px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 6px;
    }
    .sb-logo-mark {
        width: 42px; height: 42px;
        background: linear-gradient(135deg, #D4AF37 0%, #7A5C10 100%);
        border-radius: 11px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
        box-shadow: 0 4px 16px rgba(212,175,55,0.25);
    }
    .sb-logo-text { display: flex; flex-direction: column; line-height: 1.3; }
    .sb-logo-name {
        font-family: serif, 'DM Serif Display';
        font-size: 17px;
        color: var(--text);
        letter-spacing: 0.3px;
    }
    .sb-logo-ver {
        font-size: 10px;
        color: var(--text-3);
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }

    /* ── Section label ───────────────────────────────────────── */
    p.sb-section-label {
        font-size: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 1.4px !important;
        text-transform: uppercase !important;
        color: var(--text-3) !important;
        padding: 10px 20px 4px !important;
        margin: 0 !important;
    }

    /* ── Nav button wrapper states ───────────────────────────── */
    div.sb-nav-btn       { padding: 2px 10px; }
    div.sb-nav-btn--active { padding: 2px 10px; }

    /* Base button inside sidebar — strip Streamlit defaults */
    div.sb-nav-btn > div[data-testid="stButton"] > button,
    div.sb-nav-btn--active > div[data-testid="stButton"] > button {
        width: 100% !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: var(--r-sm) !important;
        color: var(--text-2) !important;
        font-family: sans-serif, 'DM Sans' !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 10px 14px !important;
        transition: background 0.15s, color 0.15s, border-color 0.15s !important;
        box-shadow: none !important;
        letter-spacing: 0.1px !important;
        justify-content: flex-start !important;
    }

    /* Hover — inactive */
    div.sb-nav-btn > div[data-testid="stButton"] > button:hover {
        background: var(--bg-sub) !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }

    /* Active state */
    div.sb-nav-btn--active > div[data-testid="stButton"] > button {
        background: var(--gold-bg) !important;
        border-color: var(--border-gold) !important;
        color: var(--gold) !important;
        font-weight: 600 !important;
    }
    div.sb-nav-btn--active > div[data-testid="stButton"] > button:hover {
        background: var(--gold-bg) !important;
        color: var(--gold) !important;
    }

    /* ── Stats block ──────────────────────────────────────────── */
    .sb-stats {
        margin: 14px 10px 10px;
        padding: 13px 15px;
        background: var(--bg-sub);
        border: 1px solid var(--border);
        border-radius: var(--r-sm);
    }
    .sb-stats-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11.5px;
        margin-bottom: 7px;
    }
    .sb-stats-row:last-child { margin-bottom: 0; }
    .sb-stats-label { color: var(--text-3); }
    .sb-stats-val   { color: var(--text-2); font-weight: 600; }

    /* ═══════════════════════════════════════════════════════════
       PAGE HEADER
    ═══════════════════════════════════════════════════════════ */
    .page-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        padding: 26px 30px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        margin-bottom: 26px;
        position: relative;
        overflow: hidden;
    }
    .page-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, var(--gold), transparent 70%);
    }
    .page-header .ph-label {
        font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
        text-transform: uppercase; color: var(--gold); margin-bottom: 5px;
    }
    .page-header h1 {
        font-family: serif, 'DM Serif Display';
        font-size: 28px; font-weight: 400;
        color: var(--text); margin: 0 0 5px; line-height: 1.2;
    }
    .page-header p { color: var(--text-2); margin: 0; font-size: 13.5px; }
    .page-header .ph-icon { font-size: 40px; opacity: 0.12; }

    /* ═══════════════════════════════════════════════════════════
       KPI CARDS
    ═══════════════════════════════════════════════════════════ */
    /* ═══════════════════════════════════════════════════════════
       KPI CARDS
    ═══════════════════════════════════════════════════════════ */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr); /* Default 4 columns for desktop */
        gap: 14px;
        margin-bottom: 26px;
    }

    /* --- MOBILE RESPONSIVENESS --- */
    @media (max-width: 768px) {
        .kpi-grid {
            /* Switch to 2 columns on mobile (2 above 2) */
            grid-template-columns: repeat(2, 1fr) !important; 
            gap: 10px !important;
        }

        .kpi-card {
            padding: 15px 12px !important;
        }

        /* Scale down font sizes so they don't overflow on small screens */
        .kpi-card .kpi-value {
            font-size: 1.4rem !important; 
        }
        
        .kpi-card .kpi-label {
            font-size: 9px !important;
            letter-spacing: 0.5px !important;
        }
    }
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--r);
        padding: 18px 20px;
        position: relative; overflow: hidden;
    }
    .kpi-card .kpi-label {
        font-size: 10px; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; color: var(--text-3); margin-bottom: 9px;
    }
    .kpi-card .kpi-value {
        font-family: serif, 'DM Serif Display';
        font-size: 24px; line-height: 1; margin-bottom: 6px;
    }
    .kpi-card .kpi-sub { font-size: 11.5px; color: var(--text-3); }
    .kpi-card .kpi-accent {
        position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    }
    .kpi-card.gold  .kpi-value { color: var(--gold); }
    .kpi-card.gold  .kpi-accent { background: var(--gold); }
    .kpi-card.green .kpi-value { color: var(--green); }
    .kpi-card.green .kpi-accent { background: var(--green); }
    .kpi-card.red   .kpi-value { color: var(--red); }
    .kpi-card.red   .kpi-accent { background: var(--red); }
    .kpi-card.blue  .kpi-value { color: var(--blue); }
    .kpi-card.blue  .kpi-accent { background: var(--blue); }

    /* ═══════════════════════════════════════════════════════════
       SECTION HEADERS
    ═══════════════════════════════════════════════════════════ */
    .section-header {
        display: flex; align-items: center; gap: 10px;
        margin-bottom: 14px; margin-top: 4px;
    }
    .section-header .sh-title {
        font-family: serif, 'DM Serif Display';
        font-size: 17px; color: var(--text); white-space: nowrap;
    }
    .section-header .sh-divider { flex: 1; height: 1px; background: var(--border); }

    /* ═══════════════════════════════════════════════════════════
       JOURNAL ENTRY CARDS
    ═══════════════════════════════════════════════════════════ */
    .je-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--r);
        padding: 16px 18px; margin-bottom: 10px;
        transition: border-color 0.2s;
    }
    .je-card:hover { border-color: rgba(212,175,55,0.22); }
    .je-card .je-header {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid var(--border);
    }
    .je-card .je-no {
        font-family: serif, 'DM Serif Display'; font-size: 14px; color: var(--gold);
    }
    .je-card .je-date {
        font-size: 11px; color: var(--text-3);
        background: var(--bg-sub); padding: 3px 9px; border-radius: 20px;
    }
    .je-card .je-desc { font-size: 12.5px; color: var(--text-2); margin-bottom: 10px; }
    .je-card .je-line {
        display: flex; justify-content: space-between; align-items: center;
        font-size: 12.5px; padding: 5px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    .je-card .je-line:last-of-type { border-bottom: none; }
    .je-acct  { color: var(--text-2); }
    .je-dr    { color: var(--green); font-weight: 600; }
    .je-cr    { color: var(--red);   font-weight: 600; }
    .je-card .je-total {
        display: flex; justify-content: flex-end;
        margin-top: 10px; padding-top: 9px;
        border-top: 1px solid var(--border);
        font-size: 12px; color: var(--text-3);
    }
    .je-card .je-total-val { color: var(--text); font-weight: 600; margin-left: 5px; }

    /* ═══════════════════════════════════════════════════════════
       ALERT BOXES
    ═══════════════════════════════════════════════════════════ */
    .alert {
        display: flex; align-items: flex-start; gap: 11px;
        padding: 12px 15px; border-radius: var(--r-sm);
        margin-bottom: 13px; font-size: 13px; line-height: 1.5;
    }
    .alert.success { background: var(--green-bg); border: 1px solid rgba(34,197,94,0.2);  color: #86EFAC; }
    .alert.error   { background: var(--red-bg);   border: 1px solid rgba(239,68,68,0.2);  color: #FCA5A5; }
    .alert.warning { background: rgba(251,191,36,0.09); border: 1px solid rgba(251,191,36,0.2); color: #FCD34D; }
    .alert.info    { background: var(--blue-bg);  border: 1px solid rgba(59,130,246,0.2); color: #93C5FD; }
    .alert .alert-icon { font-size: 15px; flex-shrink: 0; margin-top: 1px; }

    /* ═══════════════════════════════════════════════════════════
       FINANCIAL RESULT BOX
    ═══════════════════════════════════════════════════════════ */
    .result-box {
        padding: 22px 26px; border-radius: var(--r);
        text-align: center; margin: 22px 0;
    }
    .result-box.profit {
        background: linear-gradient(135deg,rgba(34,197,94,.07),rgba(34,197,94,.02));
        border: 1px solid rgba(34,197,94,.2);
    }
    .result-box.loss {
        background: linear-gradient(135deg,rgba(239,68,68,.07),rgba(239,68,68,.02));
        border: 1px solid rgba(239,68,68,.2);
    }
    .result-box .rb-label {
        font-size: 12px; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; margin-bottom: 7px;
    }
    .result-box.profit .rb-label { color: var(--green); }
    .result-box.loss   .rb-label { color: var(--red); }
    .result-box .rb-value {
        font-family: serif, 'DM Serif Display';
        font-size: 40px; color: var(--text); line-height: 1;
    }
    .result-box .rb-note { font-size: 11.5px; color: var(--text-3); margin-top: 7px; }

    /* ═══════════════════════════════════════════════════════════
       TOTAL ROW
    ═══════════════════════════════════════════════════════════ */
    .total-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 15px;
        background: var(--bg-el);
        border: 1px solid var(--border);
        border-radius: var(--r-sm);
        margin-top: 10px; font-weight: 600;
    }
    .total-row .tr-label { color: var(--text-2); font-size: 13.5px; }
    .total-row .tr-value {
        font-family: serif, 'DM Serif Display';
        font-size: 19px; color: var(--gold);
    }

    /* ═══════════════════════════════════════════════════════════
       BADGES
    ═══════════════════════════════════════════════════════════ */
    .badge {
        display: inline-flex; align-items: center; gap: 5px;
        padding: 3px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 700;
        letter-spacing: 0.5px; text-transform: uppercase;
    }
    .badge.balanced   { background: var(--green-bg); color: var(--green); border: 1px solid rgba(34,197,94,.2); }
    .badge.unbalanced { background: var(--red-bg);   color: var(--red);   border: 1px solid rgba(239,68,68,.2); }

    /* ═══════════════════════════════════════════════════════════
       STREAMLIT COMPONENT OVERRIDES
    ═══════════════════════════════════════════════════════════ */
    /* Sidebar Navigation Buttons padding */
    [data-testid="stSidebar"] .stButton {
        padding: 0 16px !important;
        margin-bottom: 2px !important;
    }

    /* Generic buttons (non-sidebar) */
    .stButton > button {
        background: var(--bg-el) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r-sm) !important;
        font-family: sans-serif, 'DM Sans' !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        transition: all 0.16s !important;
        box-shadow: none !important;
    }
    .stButton > button:hover {
        border-color: var(--border-gold) !important;
        color: var(--gold) !important;
        background: var(--gold-bg) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#D4AF37,#8B6914) !important;
        color: #0D0F14 !important;
        border: none !important;
        font-weight: 700 !important;
    }
    .stButton > button[kind="primary"]:hover {
        opacity: 0.9 !important;
        color: #0D0F14 !important;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input,
    .stDateInput input, .stTextArea textarea {
        background: var(--bg-el) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: var(--r-sm) !important;
        font-family: sans-serif, 'DM Sans' !important;
        font-size: 13px !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--border-gold) !important;
        box-shadow: 0 0 0 2px var(--gold-bg) !important;
    }
    .stSelectbox > div > div {
        background: var(--bg-el) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: var(--r-sm) !important;
        font-family: sans-serif, 'DM Sans' !important;
        font-size: 13px !important;
    }

    /* Labels */
    .stSelectbox label, .stTextInput label, .stNumberInput label,
    .stDateInput label, .stTextArea label, .stMultiSelect label,
    .stSlider label, .stSelectSlider label {
        color: var(--text-2) !important;
        font-size: 11.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.4px !important;
        text-transform: uppercase !important;
        font-family: sans-serif, 'DM Sans' !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid var(--border) !important;
        gap: 2px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-3) !important;
        font-family: sans-serif, 'DM Sans' !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 9px 16px !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.15s !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--gold) !important;
        border-bottom-color: var(--gold) !important;
    }

    /* Metrics */
    [data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r) !important;
        padding: 16px !important;
    }
    [data-testid="stMetricValue"] {
        font-family: serif, 'DM Serif Display' !important;
        font-size: 24px !important;
        color: var(--text) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 10.5px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        color: var(--text-3) !important;
    }

    /* DataFrames */
    .stDataFrame { border-radius: var(--r) !important; overflow: hidden; }
    [data-testid="stDataFrameResizable"] { border-radius: var(--r) !important; }

    /* Expanders */
    [data-testid="stExpander"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--r) !important;
    }
    [data-testid="stExpander"] summary {
        color: var(--text-2) !important;
        font-family: sans-serif, 'DM Sans' !important;
        font-size: 13px !important;
    }
    [data-testid="stExpander"] summary:hover { color: var(--gold) !important; }

    /* Native alerts */
    [data-testid="stAlert"] {
        border-radius: var(--r-sm) !important;
        font-family: sans-serif, 'DM Sans' !important;
        font-size: 13px !important;
    }

    /* Toast */
    [data-testid="stToast"] {
        background: var(--bg-el) !important;
        border: 1px solid var(--border-gold) !important;
        border-radius: var(--r) !important;
        color: var(--text) !important;
        font-family: sans-serif, 'DM Sans' !important;
    }

    /* Dialog */
    [data-testid="stDialog"] > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-gold) !important;
        border-radius: 16px !important;
    }

    /* Multiselect tags */
    .stMultiSelect [data-baseweb="tag"] {
        background: var(--gold-bg) !important;
        border: 1px solid var(--border-gold) !important;
        color: var(--gold) !important;
        border-radius: 6px !important;
    }

    /* Radio */
    .stRadio label { color: var(--text-2) !important; font-size: 13px !important; }

    /* Dividers */
    hr { border-color: var(--border) !important; margin: 18px 0 !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

    /* Hide Streamlit chrome */
    #MainMenu, footer { visibility: hidden; }
    
    </style>
    """,
        unsafe_allow_html=True,
    )
