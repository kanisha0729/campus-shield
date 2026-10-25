"""Case storage in a local SQLite file (campus_shield.db).

Same function names as agreed with the team. Every browser window reads
the same file, so a student window and an officer window see each other's
changes. Kanisha can extend or replace this file; the function names and
return shapes must stay the same.
"""
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "campus_shield.db")

COLUMNS = ("case_id", "created_at", "reporter", "company_claimed", "offer_text",
           "sender_email", "phone", "upi_id", "flags", "status",
           "officer_note", "matched_case_id")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                reporter TEXT,
                company_claimed TEXT,
                offer_text TEXT NOT NULL,
                sender_email TEXT,
                phone TEXT,
                upi_id TEXT,
                flags TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                officer_note TEXT DEFAULT '',
                matched_case_id INTEGER
            )
        """)


def add_case(case: dict) -> int:
    row = {k: case.get(k) for k in COLUMNS if k != "case_id"}
    row["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    row["status"] = case.get("status") or "Pending"
    row["officer_note"] = case.get("officer_note") or ""
    cols = ", ".join(row)
    marks = ", ".join("?" for _ in row)
    with _connect() as conn:
        cur = conn.execute(f"INSERT INTO cases ({cols}) VALUES ({marks})", tuple(row.values()))
        return cur.lastrowid


def get_cases(status: str | None = None) -> list[dict]:
    with _connect() as conn:
        if status is None:
            rows = conn.execute("SELECT * FROM cases ORDER BY case_id").fetchall()
        else:
            rows = conn.execute("SELECT * FROM cases WHERE status = ? ORDER BY case_id", (status,)).fetchall()
    return [dict(r) for r in rows]


def get_case(case_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
    return dict(row) if row else None


def set_status(case_id: int, status: str, note: str) -> None:
    with _connect() as conn:
        conn.execute("UPDATE cases SET status = ?, officer_note = ? WHERE case_id = ?",
                     (status, note, case_id))


def get_cases_by_reporter(reporter: str) -> list[dict]:
    """A student's own reports, newest first (for the My reports tab)."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM cases WHERE lower(trim(reporter)) = lower(trim(?)) ORDER BY case_id DESC",
            (reporter,),
        ).fetchall()
    return [dict(r) for r in rows]


def search_confirmed(query: str) -> list[dict]:
    """Students only ever see Confirmed scam cases."""
    q = (query or "").strip().lower()
    out = []
    for c in get_cases("Confirmed scam"):
        fields = [c.get("company_claimed"), c.get("sender_email"), c.get("phone"), c.get("upi_id")]
        if not q or any(q in (f or "").lower() for f in fields):
            out.append(c)
    return out


def reset_demo() -> None:
    """Delete all cases (used by the officer page's demo reset button)."""
    with _connect() as conn:
        conn.execute("DELETE FROM cases")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'cases'")
