"""Load the simulated sample cases into campus_shield.db.

Run:  py seed.py        (wipes existing cases first, so it is safe to re-run)
All names, numbers and emails in data/sample_cases.csv are made up.
"""
import csv
import os

from core import db, red_flags

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_cases.csv")


def seed() -> int:
    db.init_db()
    db.reset_demo()
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        flags = red_flags.check_offer(r["offer_text"], r["sender_email"], r["company_claimed"])
        r["flags"] = "; ".join(fl["flag"] for fl in flags)
        db.add_case(r)
    return len(rows)


if __name__ == "__main__":
    print(f"Seeded {seed()} sample cases into {db.DB_PATH}")
