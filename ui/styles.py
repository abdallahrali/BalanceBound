"""
CSS styling and LTR support.
"""

import streamlit as st


def inject_css():
    """Inject all custom CSS into the Streamlit app."""
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Layout Direction: Left-to-Right */
    .stApp { direction: ltr; }
    .stSidebar { direction: ltr; }
    [data-testid="stSidebar"] { direction: ltr; }

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
        border-radius: 12px;
        margin-bottom: 25px;
        border-left: 5px solid #e94560;
    }
    .main-header h1 { color: white; margin: 0; font-size: 26px; }
    .main-header p { color: #a0a0b0; margin: 5px 0 0 0; font-size: 14px; }

    .stDataFrame { direction: ltr; }
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
        background: var(--secondary-background-color);
        border: 1px solid rgba(150, 150, 150, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        direction: ltr;
        color: var(--text-color);
    }
    .journal-card .je-header {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px dashed rgba(150, 150, 150, 0.4);
        padding-bottom: 8px;
        margin-bottom: 10px;
        font-weight: 600;
        color: var(--text-color);
    }
    .journal-card .je-line {
        display: flex;
        justify-content: space-between;
        font-size: 14px;
        padding: 2px 0;
    }
    .je-line .dr { color: #2ecc71; font-weight: 600; }
    .je-line .cr { color: #e74c3c; font-weight: 600; }
    
    /* Responsive adjustment for metric labels */
    [data-testid="stMetricLabel"] {
        text-align: left;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
