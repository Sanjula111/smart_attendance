"""
utils/attendance_utils.py
=========================
All CSV-based attendance operations:
  - mark_attendance   – write a new record (duplicate-safe)
  - load_attendance   – read records into a DataFrame
  - get_today_marked  – names already recorded today
  - get_stats         – summary metrics for the dashboard
"""

import os
import csv
from datetime import datetime, date

import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR     = os.path.join(BASE_DIR, "data", "attendance")
CSV_PATH     = os.path.join(DATA_DIR, "attendance.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# CSV column headers
COLUMNS = ["Name", "Date", "Time", "Status"]


# ────────────────────────────────────────────────────────────────────────────
# Initialisation
# ────────────────────────────────────────────────────────────────────────────

def _ensure_csv() -> None:
    """Create the CSV with headers if it does not already exist."""
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(COLUMNS)


# ────────────────────────────────────────────────────────────────────────────
# Core operations
# ────────────────────────────────────────────────────────────────────────────

def get_today_marked() -> set[str]:
    """Return the set of names already marked present today."""
    _ensure_csv()
    today = date.today().strftime("%Y-%m-%d")
    marked: set[str] = set()

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Date") == today:
                marked.add(row["Name"])

    return marked


def mark_attendance(name: str) -> tuple[bool, str]:
    """
    Record attendance for *name* (today).

    Returns
    -------
    (True,  success_message)   – if newly recorded
    (False, reason_message)    – if already recorded or name invalid
    """
    _ensure_csv()

    if not name or name.strip().lower() == "unknown":
        return False, "Cannot record attendance for an unrecognised face."

    name = name.strip()
    today     = date.today().strftime("%Y-%m-%d")
    now_time  = datetime.now().strftime("%H:%M:%S")

    # Duplicate guard
    already = get_today_marked()
    if name in already:
        return False, f"⚠️ {name}'s attendance is already recorded for today."

    # Append record
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, today, now_time, "Present"])

    return True, f"✅ Attendance marked for **{name}** at {now_time}."


# ────────────────────────────────────────────────────────────────────────────
# Reporting helpers
# ────────────────────────────────────────────────────────────────────────────

def load_attendance(filter_date: str | None = None) -> pd.DataFrame:
    """
    Load all attendance records into a DataFrame.

    Parameters
    ----------
    filter_date : 'YYYY-MM-DD' string or None (returns all records)
    """
    _ensure_csv()
    df = pd.read_csv(CSV_PATH)

    if df.empty:
        return pd.DataFrame(columns=COLUMNS)

    if filter_date:
        df = df[df["Date"] == filter_date]

    # Nice display ordering
    df = df.sort_values(["Date", "Time"], ascending=[False, False]).reset_index(drop=True)
    return df


def get_stats() -> dict:
    """Return aggregate statistics used by the dashboard."""
    df = load_attendance()
    today_str = date.today().strftime("%Y-%m-%d")

    today_df  = df[df["Date"] == today_str] if not df.empty else pd.DataFrame()
    dates     = df["Date"].nunique() if not df.empty else 0
    students  = df["Name"].nunique() if not df.empty else 0
    today_cnt = len(today_df)
    total     = len(df)

    return {
        "total_records": total,
        "unique_students": students,
        "unique_dates": dates,
        "today_count": today_cnt,
    }
