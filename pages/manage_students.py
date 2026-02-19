"""
pages/manage_students.py
========================
Upload student photos, view registered students, and trigger face encoding.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
import streamlit as st
from PIL import Image

from utils.face_utils import (
    FACE_LIB_AVAILABLE,
    STUDENT_DIR,
    ENCODINGS_FILE,
    encode_faces_from_folder,
)


SUPPORTED = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _list_students() -> list[dict]:
    """Return a list of {name, filename, path} for every registered image."""
    students = []
    for fname in sorted(os.listdir(STUDENT_DIR)):
        if os.path.splitext(fname)[1].lower() in SUPPORTED:
            stem = os.path.splitext(fname)[0]
            name = stem.split("_")[0].replace("-", " ").title()
            students.append({"name": name, "filename": fname, "path": os.path.join(STUDENT_DIR, fname)})
    return students


def render() -> None:
    st.markdown("""
    <div class="hero-banner">
        <h1>👤 Manage Students</h1>
        <p>Upload student photos and build the face recognition database</p>
    </div>
    """, unsafe_allow_html=True)

    if not FACE_LIB_AVAILABLE:
        st.error("❌ **face_recognition** library not installed. See Mark Attendance page for instructions.")
        return

    # ── Upload section ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📤 Upload Student Photo</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        📌 <b>Naming convention:</b> Name your file as <code>StudentName.jpg</code> or
        <code>StudentName_01.jpg</code>. The part before the first underscore (or the full
        stem) becomes the student's display name.
    </div>""", unsafe_allow_html=True)

    with st.form("upload_form", clear_on_submit=True):
        uploaded = st.file_uploader(
            "Choose student image(s)",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
            accept_multiple_files=True,
        )
        submitted = st.form_submit_button("📥 Save Photos", type="primary")

    if submitted and uploaded:
        saved, skipped = 0, 0
        for file in uploaded:
            dest = os.path.join(STUDENT_DIR, file.name)
            if os.path.exists(dest):
                skipped += 1
                continue
            with open(dest, "wb") as f:
                f.write(file.getbuffer())
            saved += 1

        if saved:
            st.success(f"✅ Saved {saved} photo(s). Click **Encode Faces** below to update the model.")
        if skipped:
            st.warning(f"⚠️ Skipped {skipped} file(s) — already exist. Delete & re-upload to replace.")

    # ── Encode button ─────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🧠 Face Encoding</div>', unsafe_allow_html=True)

    enc_col, status_col = st.columns([1, 3])
    with enc_col:
        encode_btn = st.button("🔄 Encode Faces", type="primary", use_container_width=True)

    if encode_btn:
        students = _list_students()
        if not students:
            st.warning("⚠️ No student images found. Upload at least one photo first.")
        else:
            with st.spinner("🤖 Computing face encodings – this may take a moment…"):
                db = encode_faces_from_folder()
            if db:
                st.success(f"✅ Encoding complete! {len(db)} student(s) encoded successfully.")
            else:
                st.error("❌ No faces found in uploaded images. Ensure photos show a clear face.")

    # Show encoding status
    enc_exists = os.path.exists(ENCODINGS_FILE)
    with status_col:
        if enc_exists:
            mtime = os.path.getmtime(ENCODINGS_FILE)
            import datetime
            ts = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            st.markdown(f"""
            <div class="success-box" style="margin:0">
                ✅ Face encodings are <b>up to date</b> (last built: {ts})
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box" style="margin:0">
                ⚠️ Encodings not built yet. Click <b>Encode Faces</b>.
            </div>""", unsafe_allow_html=True)

    # ── Registered students gallery ───────────────────────────────────────
    st.markdown('<div class="section-header">👥 Registered Students</div>', unsafe_allow_html=True)
    students = _list_students()

    if not students:
        st.markdown("""
        <div class="info-box">
            📭 No students registered yet. Upload photos above to get started.
        </div>""", unsafe_allow_html=True)
        return

    # Gallery – 4 per row
    cols_per_row = 4
    for i in range(0, len(students), cols_per_row):
        row_students = students[i : i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, stu in zip(cols, row_students):
            with col:
                try:
                    img = Image.open(stu["path"])
                    # Crop square thumbnail
                    w, h = img.size
                    side = min(w, h)
                    img  = img.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
                    img  = img.resize((200, 200), Image.LANCZOS)
                    st.image(img, use_container_width=True)
                except Exception:
                    st.image("https://via.placeholder.com/200?text=Error", use_container_width=True)

                st.markdown(f"<div style='text-align:center;color:#4fc3f7;font-weight:600'>{stu['name']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align:center;color:#607d8b;font-size:.75rem'>{stu['filename']}</div>", unsafe_allow_html=True)

                if st.button("🗑️ Delete", key=f"del_{stu['filename']}", use_container_width=True):
                    os.remove(stu["path"])
                    # Invalidate encoding cache so next encode is fresh
                    if os.path.exists(ENCODINGS_FILE):
                        os.remove(ENCODINGS_FILE)
                    st.success(f"Deleted {stu['name']}. Re-encode to update the model.")
                    st.rerun()
