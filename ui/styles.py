"""
CSS styling and RTL support.
"""

import streamlit as st


def inject_css():
    """Inject all custom CSS into the Streamlit app."""
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    * { font-family: 'Cairo', sans-serif !important; }

    .stApp { direction: rtl; }
    .stSidebar { direction: rtl; }
    [data-testid="stSidebar"] { direction: rtl; }

    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: white;
        margin-bottom: 10px;
    }
    .metric-card .value { font-size: 28px; font-weight: 700; color: #e94560; }
    .metric-card .label { font-size: 14px; color: #a0a0b0; margin-top: 5px; }

    .main-header {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        padding: 25px 30px;
        border-radius: 15px;
        margin-bottom: 25px;
        border-left: 5px solid #e94560;
    }
    .main-header h1 { color: white; margin: 0; font-size: 26px; }
    .main-header p { color: #a0a0b0; margin: 5px 0 0 0; font-size: 14px; }

    .stDataFrame { direction: rtl; }
    thead th { background-color: #0f3460 !important; color: white !important; }

    .stButton > button {
        background: linear-gradient(135deg, #0f3460, #e94560);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover { opacity: 0.9; transform: scale(1.01); }

    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #0f3460;
        border-bottom: 2px solid #e94560;
        padding-bottom: 8px;
        margin-bottom: 15px;
    }

    .journal-card {
        background: #f8f9ff;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        direction: rtl;
    }
    .journal-card .je-header {
        font-weight: 700; color: #0f3460; font-size: 15px; margin-bottom: 8px;
    }
    .journal-card .je-row {
        display: flex; justify-content: space-between;
        padding: 4px 0; border-bottom: 1px solid #eee;
    }
    .dr-amount { color: #28a745; font-weight: 600; }
    .cr-amount { color: #dc3545; font-weight: 600; }

    .stTextInput input, .stNumberInput input, .stSelectbox select {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
