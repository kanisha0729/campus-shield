from core import db, matching, red_flags


def flags(text, email="", company=""):
    return [f["flag"] for f in red_flags.check_offer(text, email, company)]


def test_fee_demand_flagged():
    assert "Fee demand" in flags("Pay Rs 1,999 registration fee to confirm your seat")


def test_stipend_is_not_a_fee():
    assert "Fee demand" not in flags("You will get a stipend of Rs 15,000 per month")


def test_free_mail_for_company_offer():
    assert "Free-mail sender" in flags("Offer letter attached", "hr.team@gmail.com", "TechNova")


def test_urgency_minutes():
    assert "Urgency words" in flags("Reply within 30 minutes or the offer is cancelled")


def test_match_only_confirmed_cases():
    db.add_case({"offer_text": "x", "phone": "+91 90000 00001", "status": "Pending"})
    assert matching.find_confirmed_match("9000000001", "", "") is None
    cid = db.add_case({"offer_text": "x", "phone": "+91 90000 00001", "status": "Confirmed scam"})
    m = matching.find_confirmed_match("09000000001", "", "")
    assert m["case_id"] == cid and m["matched_on"] == "phone"


def test_upi_match_ignores_case():
    db.add_case({"offer_text": "x", "upi_id": "TechNova.HR@okaxis", "status": "Confirmed scam"})
    assert matching.find_confirmed_match("", "", "technova.hr@okaxis")["matched_on"] == "UPI ID"


def test_students_search_only_confirmed():
    db.add_case({"offer_text": "x", "company_claimed": "Alpha", "status": "Confirmed scam"})
    db.add_case({"offer_text": "x", "company_claimed": "Alpha Pending", "status": "Pending"})
    db.add_case({"offer_text": "x", "company_claimed": "Alpha Genuine", "status": "Genuine"})
    assert [c["company_claimed"] for c in db.search_confirmed("alpha")] == ["Alpha"]


def test_seed_loads_sample_data():
    import seed
    assert seed.seed() == 16
    assert len(db.get_cases("Confirmed scam")) == 4
    assert db.get_case(1)["company_claimed"].startswith("TechNova")
