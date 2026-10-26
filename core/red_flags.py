"""Red-flag checks for a reported offer.

Each check returns a flag with a plain reason, or nothing. Flags are cautions,
never a verdict: only the placement officer can mark a case as a scam.
"""
import re
from datetime import datetime

try:
    import whois  # python-whois
except ImportError:  # the app still works without the domain-age check
    whois = None

FREE_MAIL = ("gmail.com", "yahoo.com", "outlook.com", "rediffmail.com", "hotmail.com")

# Money the student is asked to SEND. A stipend or salary must never match.
FEE_PHRASES = ("registration fee", "processing fee", "certificate fee", "verification fee",
               "training fee", "joining fee", "onboarding fee", "onboarding deposit", "processing payment", "security deposit",
               "refundable deposit")
# "Registration fee: Rs 0", "fee: nil", "fee waived" are not fee demands.
NO_FEE_AFTER = re.compile(r"^[\s:\-]*((rs\.?|₹|inr)?\s?0\b|nil\b|none\b|free\b|waived\b|not required\b|not applicable\b)")
# An amount followed closely by fee/deposit/payment: "₹1,500 refundable onboarding deposit".
AMOUNT_THEN_FEE = re.compile(r"(rs\.?|₹|inr)\s?([\d,]+)[^.\n]{0,30}?\b(fee|deposit|payment|charge)s?\b")
FEE_THEN_AMOUNT = re.compile(r"\b(fee|deposit)s?\b\W{0,3}(rs\.?|₹|inr)\s?([\d,]+)")
SEND_MONEY = re.compile(r"\b(pay|send|transfer|deposit)\b([^.\n]{0,30}?)(rs\.?|₹|inr)\s?\d")
UPI_ID = re.compile(r"\b[\w.\-]+@[a-z]+\b(?!\.)")
AMOUNT = re.compile(r"(rs\.?|₹|inr)\s?\d")

URGENCY_WORDS = ("within 24 hours", "immediately", "last date today", "today itself",
                 "limited seats", "limited slots", "final warning", "act fast")
URGENCY_MINUTES = re.compile(r"within \d+\s*(minutes|mins|hours)")

NEW_DOMAIN_DAYS = 180


def _fee_demand(text: str) -> dict | None:
    asks = False
    for p in FEE_PHRASES:
        for m in re.finditer(re.escape(p), text):
            if not NO_FEE_AFTER.match(text[m.end():m.end() + 20]):
                asks = True
    if not asks:
        found = [(m.group(0), m.group(2)) for m in AMOUNT_THEN_FEE.finditer(text)]
        found += [(m.group(0), m.group(3)) for m in FEE_THEN_AMOUNT.finditer(text)]
        for span, amount in found:
            if amount.replace(",", "").strip("0") and "stipend" not in span and "salary" not in span:
                asks = True
                break
    if not asks:
        for m in SEND_MONEY.finditer(text):
            if "stipend" not in m.group(2) and "salary" not in m.group(2):
                asks = True
                break
    if not asks and UPI_ID.search(text) and AMOUNT.search(text):
        asks = True
    if asks:
        return {"flag": "Fee demand",
                "reason": "The offer asks you to send money. Genuine employers do not charge for internships."}
    return None


def _free_mail(domain: str, company_claimed: str) -> dict | None:
    if company_claimed and domain in FREE_MAIL:
        return {"flag": "Free-mail sender",
                "reason": "A company offer was sent from a free email address, not a company domain."}
    return None


def _new_domain(domain: str) -> dict | None:
    """Domain age from WHOIS. Skipped for free mail; any failure means no flag."""
    if not domain or domain in FREE_MAIL or domain.endswith(".example") or whois is None:
        return None
    try:
        created = whois.whois(domain).creation_date
        if isinstance(created, list):
            created = created[0]
        if not created:
            return None
        age = (datetime.now() - created.replace(tzinfo=None)).days
    except Exception:
        return None
    if age < NEW_DOMAIN_DAYS:
        return {"flag": "New domain",
                "reason": f"The sender's email domain was registered only {age} days ago."}
    return None


def _urgency(text: str) -> dict | None:
    if any(w in text for w in URGENCY_WORDS) or URGENCY_MINUTES.search(text):
        return {"flag": "Urgency words", "reason": "The message pressures you to act fast."}
    return None


def check_offer(offer_text: str, sender_email: str, company_claimed: str) -> list[dict]:
    text = (offer_text or "").lower()
    domain = (sender_email or "").strip().lower().rsplit("@", 1)[-1] if "@" in (sender_email or "") else ""
    results = [_fee_demand(text), _free_mail(domain, company_claimed),
               _new_domain(domain), _urgency(text)]
    return [r for r in results if r]
