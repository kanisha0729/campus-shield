"""STUB for Kanisha's red_flags.py.

Simple keyword rules so the screens have something to show. The domain-age
(WHOIS) check is not in the stub; Kanisha adds it.
"""
import re

FREE_MAIL = ("gmail.com", "yahoo.com", "outlook.com", "rediffmail.com", "hotmail.com")
FEE_WORDS = ("registration fee", "processing fee", "certificate fee", "security deposit",
             "deposit", "pay rs", "pay ₹", "verification fee", "training fee")
URGENCY_WORDS = ("within 24 hours", "immediately", "last date today", "limited seats", "urgent")


def check_offer(offer_text: str, sender_email: str, company_claimed: str) -> list[dict]:
    text = (offer_text or "").lower()
    email = (sender_email or "").strip().lower()
    flags = []

    if any(w in text for w in FEE_WORDS) or re.search(r"\b[\w.\-]+@ok\w+\b", text):
        flags.append({"flag": "Fee demand",
                      "reason": "The offer asks you to pay. Genuine employers do not charge for internships."})

    if company_claimed and email.endswith(FREE_MAIL):
        flags.append({"flag": "Free-mail sender",
                      "reason": "A company offer was sent from a free email address, not a company domain."})

    if any(w in text for w in URGENCY_WORDS):
        flags.append({"flag": "Urgency words",
                      "reason": "The message pressures you to act fast."})

    return flags
