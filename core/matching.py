"""STUB for Kanisha's matching.py.

Normalises identifiers and matches ONLY against officer-confirmed cases.
"""
import re

from core import db


def normalise_phone(p: str) -> str:
    digits = re.sub(r"\D", "", p or "")
    return digits[-10:] if len(digits) >= 10 else digits


def normalise_text(s: str) -> str:
    return (s or "").strip().lower()


def find_confirmed_match(phone: str, email: str, upi_id: str) -> dict | None:
    p, e, u = normalise_phone(phone), normalise_text(email), normalise_text(upi_id)
    for c in db.get_cases("Confirmed scam"):
        if u and normalise_text(c.get("upi_id")) == u:
            return {"case_id": c["case_id"], "matched_on": "UPI ID", "value": u, "note": c["officer_note"]}
        if p and normalise_phone(c.get("phone")) == p:
            return {"case_id": c["case_id"], "matched_on": "phone", "value": p, "note": c["officer_note"]}
        if e and normalise_text(c.get("sender_email")) == e:
            return {"case_id": c["case_id"], "matched_on": "email", "value": e, "note": c["officer_note"]}
    return None
