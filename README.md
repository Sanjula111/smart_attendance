# 🎓 Smart Attendance System

An AI-powered attendance management system built with **Python**, **OpenCV**,
**face_recognition**, and **Streamlit**. It detects students via webcam, marks
attendance automatically, and stores records in a CSV file — all through a
modern, dark-themed web UI.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 Face Recognition | Real-time detection using `dlib` HOG + deep metric learning |
| 📸 Webcam Capture | One-click photo capture via Streamlit's camera input |
| 🔐 Duplicate Guard | Prevents re-marking the same student on the same day |
| 📋 CSV Storage | Human-readable attendance log, compatible with Excel |
| 📊 Dashboard | Live metrics and today's attendance at a glance |
| 🔎 Filter & Export | Date range / name filters + CSV export |
| 🎨 Modern UI | Dark gradient theme, animated cards, success balloons |

---

## 🗂️ Project Structure

```
smart_attendance/
├── app.py                      # Streamlit entry point & routing
├── requirements.txt
├── README.md
├── pages/
│   ├── dashboard.py            # Landing page with metrics
│   ├── mark_attendance.py      # Webcam capture + recognition
│   ├── manage_students.py      # Upload photos & encode faces
│   └── view_records.py         # Browse, filter, export records
├── utils/
│   ├── face_utils.py           # Face encoding & recognition helpers
│   └── attendance_utils.py     # CSV read/write helpers
└── data/
    ├── student_images/         # ← Put student photos here
    ├── attendance/
    │   └── attendance.csv      # Auto-created on first run
    └── encodings.pkl           # Auto-created after encoding
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9+  
- `cmake` (needed to build `dlib`)

```bash
# macOS
brew install cmake

# Ubuntu / Debian
sudo apt-get install cmake build-essential
```

### 2. Install dependencies

```bash
cd smart_attendance
pip install -r requirements.txt
```

> **Note:** `face-recognition` installs `dlib`, which compiles C++ code.  
> This can take **5–15 minutes** on the first install.

### 3. Run the app

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

---

## 📖 Usage Guide

### Step 1 – Register Students

1. Go to **👤 Manage Students**.
2. Upload a clear, front-facing photo for each student.
3. Name files like `Alice.jpg`, `Bob_01.jpg`, `Charlie_Smith.png`.
4. Click **🔄 Encode Faces** to build the recognition model.

### Step 2 – Mark Attendance

1. Go to **📸 Mark Attendance**.
2. Click the camera button to take a photo.
3. The system will detect and name faces automatically.
4. Click **✅ Mark Attendance** to confirm.

### Step 3 – View Records

1. Go to **📊 View Records**.
2. Filter by student name, date range, or search term.
3. Download CSV for spreadsheet analysis.

---

## ⚙️ Configuration

| Parameter | File | Default | Description |
|---|---|---|---|
| `tolerance` | `face_utils.py` | `0.5` | Matching strictness (lower = stricter) |
| `model` | `face_utils.py` | `"hog"` | `"hog"` (fast) or `"cnn"` (accurate, GPU) |
| Scale factor | `face_utils.py` | `0.25` | Frame resize for speed |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `face_recognition` install fails | Ensure `cmake` and C++ build tools are installed |
| Face not detected | Improve lighting; ensure face is fully visible |
| Wrong name detected | Lower `tolerance` (e.g. `0.45`); use a clearer photo |
| Camera not working | Allow browser camera permission; try a different browser |

---

## 📄 CSV Format

```
Name,Date,Time,Status
Alice,2024-03-15,09:02:34,Present
Bob,2024-03-15,09:04:11,Present
```

---

## 🛡️ Privacy Note

All face encodings are stored **locally** (`data/encodings.pkl`).  
No data is sent to any external server.

---

## 📜 License

MIT — free to use and modify.
