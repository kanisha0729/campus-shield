"""STUB for Kanisha's db.py.

Same function names and return shapes as agreed. Data lives in memory
(st.session_state), so it resets when the app restarts. Kanisha's real
version replaces this file and stores cases in SQLite.
"""
from datetime import datetime

import streamlit as st


def _store():
    if "cases" not in st.session_state:
        st.session_state.cases = []
    return st.session_state.cases


def init_db():
    _store()


def add_case(case: dict) -> int:
    cases = _store()
    case_id = len(cases) + 1
    row = dict(case)
    row["case_id"] = case_id
    row["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    row.setdefault("status", "Pending")
    row.setdefault("officer_note", "")
    row.setdefault("matched_case_id", None)
    cases.append(row)
    return case_id


def get_cases(status: str | None = None) -> list[dict]:
    cases = _store()
    if status is None:
        return list(cases)
    return [c for c in cases if c["status"] == status]


def get_case(case_id: int) -> dict | None:
    for c in _store():
        if c["case_id"] == case_id:
            return c
    return None


def set_status(case_id: int, status: str, note: str) -> None:
    c = get_case(case_id)
    if c:
        c["status"] = status
        c["officer_note"] = note


def search_confirmed(query: str) -> list[dict]:
    """Students only ever see Confirmed scam cases."""
    q = query.strip().lower()
    out = []
    for c in get_cases("Confirmed scam"):
        fields = [c.get("company_claimed", ""), c.get("sender_email", ""),
                  c.get("phone", ""), c.get("upi_id", "")]
        if not q or any(q in (f or "").lower() for f in fields):
            out.append(c)
    return out
