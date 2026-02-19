"""
pages/dashboard.py
==================
Landing dashboard – shows summary metrics and today's attendance table.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from datetime import date

from utils.attendance_utils import get_stats, load_attendance
from utils.face_utils import STUDENT_DIR


def render() -> None:
    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner">
        <h1>🎓 Smart Attendance System</h1>
        <p>AI-powered face recognition · Real-time detection · Automated records</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Metric cards ─────────────────────────────────────────────────────────
    stats = get_stats()
    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (c1, stats["today_count"],      "Today's Attendees",  "📅"),
        (c2, stats["unique_students"],  "Registered Students","👥"),
        (c3, stats["total_records"],    "Total Records",      "📋"),
        (c4, stats["unique_dates"],     "Days Tracked",       "📆"),
    ]
    for col, value, label, icon in cards:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:2rem">{icon}</div>
                <h2>{value}</h2>
                <p>{label}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Today's attendance ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📅 Today\'s Attendance</div>', unsafe_allow_html=True)
    today_str = date.today().strftime("%Y-%m-%d")
    df = load_attendance(filter_date=today_str)

    if df.empty:
        st.markdown("""
        <div class="info-box">
            📭 No attendance recorded yet today. Head to <b>Mark Attendance</b> to get started.
        </div>""", unsafe_allow_html=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Quick-start guide ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🚀 Quick Start Guide</div>', unsafe_allow_html=True)

    steps = [
        ("1️⃣", "Register Students",   "Go to **Manage Students** → upload a clear photo for each student."),
        ("2️⃣", "Build Encodings",     "After uploading, click **Encode Faces** to train the recognition model."),
        ("3️⃣", "Mark Attendance",     "Go to **Mark Attendance** → capture a webcam photo → the system auto-detects faces."),
        ("4️⃣", "View Records",        "Go to **View Records** to filter, search, and export attendance data."),
    ]
    cols = st.columns(4)
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align:left; padding:1.2rem">
                <div style="font-size:1.6rem; margin-bottom:.4rem">{num}</div>
                <div style="color:#4fc3f7; font-weight:600; margin-bottom:.4rem">{title}</div>
                <div style="color:#b0bec5; font-size:.85rem">{desc}</div>
            </div>""", unsafe_allow_html=True)

    # ── Students registered ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">👥 Registered Students</div>', unsafe_allow_html=True)
    images = [
        f for f in os.listdir(STUDENT_DIR)
        if os.path.splitext(f)[1].lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    ]
    if images:
        names = sorted({os.path.splitext(f)[0].split("_")[0].title() for f in images})
        cols  = st.columns(min(len(names), 6))
        for col, name in zip(cols, names):
            with col:
                st.markdown(f"""
                <div class="metric-card" style="padding:.8rem">
                    <div style="font-size:1.6rem">🧑‍🎓</div>
                    <div style="color:#e0e0e0; font-size:.85rem; margin-top:.3rem">{name}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-box">
            ⚠️ No students registered yet. Add student photos in <b>Manage Students</b>.
        </div>""", unsafe_allow_html=True)
