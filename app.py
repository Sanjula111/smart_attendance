"""
Smart Attendance System - Main Application Entry Point
======================================================
Run with: streamlit run app.py
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Smart Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Global font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    [data-testid="stSidebar"] .stRadio label { color: #e0e0e0 !important; }

    /* Hero banner */
    .hero-banner {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .hero-banner h1 { color: #ffffff; font-size: 2.5rem; font-weight: 700; margin: 0; }
    .hero-banner p  { color: #a0c4ff; font-size: 1.1rem; margin: 0.5rem 0 0; }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #0f3460);
        border: 1px solid #2d6a9f;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-card h2 { color: #4fc3f7; font-size: 2rem; margin: 0; }
    .metric-card p  { color: #b0bec5; margin: 0.3rem 0 0; font-size: 0.9rem; }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #0f3460, #1e3a5f);
        color: white !important;
        padding: 0.75rem 1.25rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.05rem;
        margin: 1.5rem 0 1rem;
        border-left: 4px solid #4fc3f7;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0f3460, #1565c0);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1565c0, #1976d2);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(21,101,192,0.4);
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #2d6a9f;
        border-radius: 12px;
        padding: 1rem;
        background: rgba(15, 52, 96, 0.1);
    }

    /* Success / info boxes */
    .success-box {
        background: linear-gradient(135deg, #1b5e20, #2e7d32);
        border-left: 4px solid #66bb6a;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color: #e8f5e9;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #0d47a1, #1565c0);
        border-left: 4px solid #42a5f5;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color: #e3f2fd;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #e65100, #bf360c);
        border-left: 4px solid #ff7043;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        color: #fbe9e7;
        margin: 1rem 0;
    }

    /* DataFrames */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

    /* Divider */
    hr { border-color: #2d6a9f33; }

    /* Camera widget */
    [data-testid="stCamera"] { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Smart Attendance")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠 Dashboard", "📸 Mark Attendance", "👤 Manage Students", "📊 View Records"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "<small style='color:#607d8b'>Built with OpenCV & face_recognition</small>",
        unsafe_allow_html=True,
    )

# ── Route to page modules ────────────────────────────────────────────────────
if page == "🏠 Dashboard":
    from pages.dashboard import render
    render()
elif page == "📸 Mark Attendance":
    from pages.mark_attendance import render
    render()
elif page == "👤 Manage Students":
    from pages.manage_students import render
    render()
elif page == "📊 View Records":
    from pages.view_records import render
    render()
