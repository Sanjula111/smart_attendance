"""
utils/face_utils.py
===================
Core face-recognition helpers:
  - encode_faces_from_folder  – build an encoding database from student images
  - recognize_faces           – identify faces in a captured frame
  - draw_face_boxes           – annotate a frame with bounding boxes & labels
"""

import os
import pickle
import numpy as np
import cv2

# face_recognition is the primary library; we wrap import so the app can
# degrade gracefully if the library is missing (show install instructions).
try:
    import face_recognition
    FACE_LIB_AVAILABLE = True
except ImportError:
    FACE_LIB_AVAILABLE = False

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENT_DIR    = os.path.join(BASE_DIR, "data", "student_images")
ENCODINGS_FILE = os.path.join(BASE_DIR, "data", "encodings.pkl")

os.makedirs(STUDENT_DIR, exist_ok=True)


# ────────────────────────────────────────────────────────────────────────────
# Encoding helpers
# ────────────────────────────────────────────────────────────────────────────

def encode_faces_from_folder() -> dict[str, list]:
    """
    Scan every image in STUDENT_DIR, compute face encodings, and persist
    the result as a pickle file for fast lookup on the next run.

    File-naming convention:
        <StudentName>_<anything>.<ext>   →  name = "StudentName"
        <StudentName>.<ext>              →  name = "StudentName"

    Returns
    -------
    dict  {name: [encoding, ...]}
    """
    if not FACE_LIB_AVAILABLE:
        return {}

    encodings_db: dict[str, list] = {}
    supported = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for fname in os.listdir(STUDENT_DIR):
        ext = os.path.splitext(fname)[1].lower()
        if ext not in supported:
            continue

        # Derive the student name from the filename
        stem = os.path.splitext(fname)[0]
        name = stem.split("_")[0].replace("-", " ").title()

        img_path = os.path.join(STUDENT_DIR, fname)
        image    = face_recognition.load_image_file(img_path)
        encs     = face_recognition.face_encodings(image)

        if encs:
            encodings_db.setdefault(name, []).append(encs[0])

    # Persist to disk
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(encodings_db, f)

    return encodings_db


def load_encodings() -> dict[str, list]:
    """Load pre-computed encodings from disk (or rebuild if missing)."""
    if os.path.exists(ENCODINGS_FILE):
        with open(ENCODINGS_FILE, "rb") as f:
            return pickle.load(f)
    return encode_faces_from_folder()


# ────────────────────────────────────────────────────────────────────────────
# Recognition
# ────────────────────────────────────────────────────────────────────────────

def recognize_faces(
    frame_bgr: np.ndarray,
    encodings_db: dict[str, list],
    tolerance: float = 0.5,
) -> list[dict]:
    """
    Identify every face in *frame_bgr*.

    Parameters
    ----------
    frame_bgr   : BGR image (from OpenCV)
    encodings_db: {name: [encoding, ...]} mapping
    tolerance   : lower = stricter matching (default 0.5)

    Returns
    -------
    list of dicts:  [{name, top, right, bottom, left, confidence}, ...]
    """
    if not FACE_LIB_AVAILABLE or not encodings_db:
        return []

    # Resize for speed; recognition still done on original coordinates
    small = cv2.resize(frame_bgr, (0, 0), fx=0.25, fy=0.25)
    rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    locations = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, locations)

    results = []
    all_names = list(encodings_db.keys())
    all_encs  = [enc for encs in encodings_db.values() for enc in encs]
    # Map flat index → name
    flat_names = [
        name
        for name, encs in encodings_db.items()
        for _ in encs
    ]

    for enc, loc in zip(encodings, locations):
        distances = face_recognition.face_distance(all_encs, enc)
        best_idx  = int(np.argmin(distances)) if len(distances) else -1

        if best_idx >= 0 and distances[best_idx] <= tolerance:
            name       = flat_names[best_idx]
            confidence = round((1 - distances[best_idx]) * 100, 1)
        else:
            name       = "Unknown"
            confidence = 0.0

        # Scale coords back to original frame size
        top, right, bottom, left = [v * 4 for v in loc]
        results.append(
            dict(name=name, top=top, right=right, bottom=bottom, left=left, confidence=confidence)
        )

    return results


# ────────────────────────────────────────────────────────────────────────────
# Drawing
# ────────────────────────────────────────────────────────────────────────────

def draw_face_boxes(frame_bgr: np.ndarray, faces: list[dict]) -> np.ndarray:
    """
    Annotate *frame_bgr* in-place with coloured bounding boxes and labels.
    Returns the annotated frame.
    """
    annotated = frame_bgr.copy()

    for face in faces:
        color = (0, 200, 100) if face["name"] != "Unknown" else (0, 80, 220)
        top, right, bottom, left = face["top"], face["right"], face["bottom"], face["left"]

        # Bounding box
        cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)

        # Label background
        label = f"{face['name']} ({face['confidence']}%)" if face["name"] != "Unknown" else "Unknown"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(annotated, (left, bottom - h - 10), (left + w + 6, bottom), color, -1)

        # Label text
        cv2.putText(
            annotated, label,
            (left + 3, bottom - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
            (255, 255, 255), 1,
        )

    return annotated
