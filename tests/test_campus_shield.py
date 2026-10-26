from core import db, matching, red_flags


def flags(text, email="", company=""):
    return [f["flag"] for f in red_flags.check_offer(text, email, company)]


def test_fee_demand_flagged():
    assert "Fee demand" in flags("Pay Rs 1,999 registration fee to confirm your seat")


def test_stipend_is_not_a_fee():
    assert "Fee demand" not in flags("You will get a stipend of Rs 15,000 per month")


def test_zero_fee_is_not_a_fee():
    assert "Fee demand" not in flags("Registration fee: ₹0; no deposit or payment is required")


def test_deposit_before_word_is_a_fee():
    assert "Fee demand" in flags("Pay a ₹1,500 refundable onboarding deposit within 20 minutes")


def test_amount_before_rs_is_a_fee():
    assert "Fee demand" in flags("Pay 500000 rs to confirm your seat")
    assert "Fee demand" not in flags("We pay 15000 rs stipend monthly")


def test_free_mail_for_company_offer():
    assert "Free-mail sender" in flags("Offer letter attached", "hr.team@gmail.com", "Velorix")


def test_urgency_minutes():
    assert "Urgency words" in flags("Reply within 30 minutes or the offer is cancelled")


def test_match_only_confirmed_cases():
    db.add_case({"offer_text": "x", "phone": "+91 90000 00001", "status": "Pending"})
    assert matching.find_confirmed_match("9000000001", "", "") is None
    cid = db.add_case({"offer_text": "x", "phone": "+91 90000 00001", "status": "Confirmed scam"})
    m = matching.find_confirmed_match("09000000001", "", "")
    assert m["case_id"] == cid and m["matched_on"] == "phone"


def test_upi_match_ignores_case():
    db.add_case({"offer_text": "x", "upi_id": "Velorix.HR@okaxis", "status": "Confirmed scam"})
    assert matching.find_confirmed_match("", "", "velorix.hr@okaxis")["matched_on"] == "UPI ID"


def test_students_search_only_confirmed():
    db.add_case({"offer_text": "x", "company_claimed": "Alpha", "status": "Confirmed scam"})
    db.add_case({"offer_text": "x", "company_claimed": "Alpha Pending", "status": "Pending"})
    db.add_case({"offer_text": "x", "company_claimed": "Alpha Genuine", "status": "Genuine"})
    assert [c["company_claimed"] for c in db.search_confirmed("alpha")] == ["Alpha"]


def test_seed_loads_sample_data():
    import csv
    import seed
    with open(seed.CSV_PATH, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert seed.seed() == len(rows)
    assert db.get_case(1)["company_claimed"] == "Velorix"
    assert db.get_case(1)["status"] == "Confirmed scam"
    allowed = {"Pending", "Confirmed scam", "Genuine", "Unverified"}
    assert {r["status"] for r in rows} <= allowed


def test_genuine_samples_have_no_fee_flag():
    import seed
    seed.seed()
    for c in db.get_cases("Genuine"):
        assert "Fee demand" not in (c["flags"] or "")


def test_demo_reports_all_match_a_confirmed_case():
    import csv
    import os
    import seed
    seed.seed()
    path = os.path.join(os.path.dirname(seed.CSV_PATH), "demo_reports.csv")
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            assert matching.find_confirmed_match(r["phone"], r["sender_email"], r["upi_id"]) is not None