"""
pages/mark_attendance.py
========================
Webcam-based attendance marking page.

Flow:
  1. User clicks 'Take Photo' (st.camera_input).
  2. Photo is sent to face_recognition pipeline.
  3. Detected faces are displayed with bounding boxes.
  4. User clicks 'Mark Attendance' to confirm.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from utils.face_utils import (
    FACE_LIB_AVAILABLE,
    load_encodings,
    recognize_faces,
    draw_face_boxes,
)
from utils.attendance_utils import mark_attendance, get_today_marked


def render() -> None:
    st.markdown("""
    <div class="hero-banner">
        <h1>📸 Mark Attendance</h1>
        <p>Capture your photo – the AI will recognise your face automatically</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Library check ──────────────────────────────────────────────────────
    if not FACE_LIB_AVAILABLE:
        st.error(
            "❌ **face_recognition** library is not installed.\n\n"
            "Install it with:\n```bash\npip install face-recognition\n```\n"
            "You may also need: `brew install cmake` (macOS) or `sudo apt install cmake` (Linux)."
        )
        return

    # ── Load encodings ────────────────────────────────────────────────────
    encodings_db = load_encodings()
    if not encodings_db:
        st.markdown("""
        <div class="warning-box">
            ⚠️ No face encodings found. Please go to <b>Manage Students</b>, upload photos,
            and click <b>Encode Faces</b> first.
        </div>""", unsafe_allow_html=True)
        return

    # ── Sidebar info ──────────────────────────────────────────────────────
    today_marked = get_today_marked()
    with st.sidebar:
        st.markdown("### 📋 Today's Status")
        if today_marked:
            for name in sorted(today_marked):
                st.success(f"✅ {name}")
        else:
            st.info("No one marked yet today")

    # ── Camera section ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📷 Webcam Capture</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
        📌 Click <b>Take Photo</b> below. Make sure your face is clearly visible and well-lit.
    </div>""", unsafe_allow_html=True)

    camera_image = st.camera_input("Take a photo", label_visibility="collapsed")

    if camera_image is None:
        st.markdown("""
        <div style="text-align:center; color:#607d8b; padding:2rem">
            👆 Click the camera button above to capture your photo
        </div>""", unsafe_allow_html=True)
        return

    # ── Process captured image ────────────────────────────────────────────
    st.markdown('<div class="section-header">🔍 Detection Results</div>', unsafe_allow_html=True)

    # Convert Streamlit UploadedFile → numpy BGR array
    pil_img = Image.open(camera_image).convert("RGB")
    frame   = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    with st.spinner("🤖 Analysing faces…"):
        faces = recognize_faces(frame, encodings_db)

    annotated = draw_face_boxes(frame, faces)
    annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

    col_img, col_info = st.columns([3, 2])

    with col_img:
        st.image(annotated_rgb, caption="Detected Faces", use_container_width=True)

    with col_info:
        if not faces:
            st.markdown("""
            <div class="warning-box">
                🚫 No face detected. Please retake the photo with better lighting
                and make sure your face is clearly visible.
            </div>""", unsafe_allow_html=True)
        else:
            for face in faces:
                name = face["name"]
                conf = face["confidence"]

                if name == "Unknown":
                    st.markdown(f"""
                    <div class="warning-box">
                        ❓ <b>Unknown Face</b><br>
                        Confidence: {conf}%<br>
                        This person is not in the student database.
                    </div>""", unsafe_allow_html=True)
                else:
                    already = name in today_marked
                    colour  = "#1b5e20" if not already else "#bf360c"
                    icon    = "✅" if not already else "⚠️"
                    status  = "Ready to mark" if not already else "Already marked today"

                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,{colour},{colour}bb);
                                border-radius:12px; padding:1.2rem; margin-bottom:.8rem;
                                border-left:4px solid {'#66bb6a' if not already else '#ff7043'}">
                        <div style="font-size:1.8rem">{icon}</div>
                        <div style="color:white; font-size:1.2rem; font-weight:700">{name}</div>
                        <div style="color:#e0e0e0; font-size:.85rem">Confidence: {conf}%</div>
                        <div style="color:#bdbdbd; font-size:.8rem; margin-top:.3rem">{status}</div>
                    </div>""", unsafe_allow_html=True)

            # ── Mark attendance button ────────────────────────────────────
            recognised = [f for f in faces if f["name"] != "Unknown"]
            not_yet    = [f for f in recognised if f["name"] not in today_marked]

            if not_yet:
                if st.button("✅ Mark Attendance", type="primary"):
                    for face in not_yet:
                        success, msg = mark_attendance(face["name"])
                        if success:
                            st.balloons()
                            st.success(msg)
                        else:
                            st.warning(msg)
                    st.rerun()
            elif recognised:
                st.markdown("""
                <div class="success-box">
                    🎉 All recognised students are already marked for today!
                </div>""", unsafe_allow_html=True)

    # ── Tips ──────────────────────────────────────────────────────────────
    with st.expander("💡 Tips for better recognition"):
        st.markdown("""
        - **Lighting**: Ensure your face is well-lit from the front.
        - **Distance**: Stay 0.5–1.5 m from the camera.
        - **Angle**: Face the camera directly.
        - **Glasses/mask**: Remove if recognition fails.
        - **Encoding**: If recognition is poor, re-upload a clearer photo and re-encode.
        """)
