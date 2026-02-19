"""
pages/view_records.py
=====================
Browse, filter, search, and export attendance records.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from utils.attendance_utils import load_attendance, CSV_PATH


def render() -> None:
    st.markdown("""
    <div class="hero-banner">
        <h1>📊 Attendance Records</h1>
        <p>Browse, filter, and export your attendance data</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load all data ─────────────────────────────────────────────────────
    df_all = load_attendance()

    if df_all.empty:
        st.markdown("""
        <div class="info-box">
            📭 No attendance records found yet.
            Go to <b>Mark Attendance</b> to start recording.
        </div>""", unsafe_allow_html=True)
        return

    # ── Filter controls ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔎 Filter Records</div>', unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        all_names = ["All"] + sorted(df_all["Name"].unique().tolist())
        sel_name  = st.selectbox("👤 Student", all_names)

    with fc2:
        min_date = pd.to_datetime(df_all["Date"]).min().date()
        max_date = pd.to_datetime(df_all["Date"]).max().date()
        date_range = st.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    with fc3:
        search_term = st.text_input("🔍 Search name", placeholder="Type to search…")

    # Apply filters
    df = df_all.copy()

    if sel_name != "All":
        df = df[df["Name"] == sel_name]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        df = df[
            (pd.to_datetime(df["Date"]).dt.date >= start) &
            (pd.to_datetime(df["Date"]).dt.date <= end)
        ]

    if search_term:
        df = df[df["Name"].str.contains(search_term, case=False, na=False)]

    # ── Summary metrics ───────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    metrics = [
        (m1, len(df),               "Filtered Records",   "📋"),
        (m2, df["Name"].nunique(),  "Unique Students",    "👥"),
        (m3, df["Date"].nunique(),  "Days in Selection",  "📅"),
    ]
    for col, val, label, icon in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.5rem">{icon}</div>
                <h2>{val}</h2>
                <p>{label}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Table ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📋 Records Table</div>', unsafe_allow_html=True)

    if df.empty:
        st.markdown("""
        <div class="warning-box">⚠️ No records match the selected filters.</div>
        """, unsafe_allow_html=True)
    else:
        # Styled dataframe display
        st.dataframe(
            df.style.apply(
                lambda row: ["background-color: rgba(102,187,106,0.1)"] * len(row)
                if row.get("Status") == "Present" else [""] * len(row),
                axis=1,
            ),
            use_container_width=True,
            hide_index=True,
            height=min(400, 60 + 35 * len(df)),
        )

    # ── Export ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📥 Export Data</div>', unsafe_allow_html=True)

    exp1, exp2 = st.columns(2)

    with exp1:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Filtered CSV",
            data=csv_bytes,
            file_name=f"attendance_export_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with exp2:
        # Full dataset download
        full_csv = df_all.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download All Records",
            data=full_csv,
            file_name=f"attendance_all_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── Attendance by date chart ───────────────────────────────────────────
    if not df.empty and len(df["Date"].unique()) > 1:
        st.markdown('<div class="section-header">📈 Daily Attendance Trend</div>', unsafe_allow_html=True)
        daily = (
            df.groupby("Date")
            .size()
            .reset_index(name="Count")
            .sort_values("Date")
        )
        st.bar_chart(daily.set_index("Date")["Count"], use_container_width=True)

    # ── Danger zone – clear today ─────────────────────────────────────────
    with st.expander("⚠️ Danger Zone"):
        st.warning("This will permanently delete **all** records for today.")
        if st.button("🗑️ Clear Today's Records", type="secondary"):
            today_str = date.today().strftime("%Y-%m-%d")
            df_keep   = df_all[df_all["Date"] != today_str]
            df_keep.to_csv(CSV_PATH, index=False)
            st.success("Today's records have been cleared.")
            st.rerun()
