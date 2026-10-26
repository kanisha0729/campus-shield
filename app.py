"""
Campus Shield - student app.

Run:
    py -m streamlit run app.py
Opens at http://localhost:8501

The placement officer app is a separate program (officer_app.py, port 8502).
Both read the same database file.
"""

import streamlit as st

from core import db, matching, red_flags, ui

st.set_page_config(page_title="Campus Shield", page_icon="🛡️", layout="centered",
                   initial_sidebar_state="collapsed")
ui.apply_style()
db.init_db()

DECIDED = ("Confirmed scam", "Genuine", "Unverified")  # statuses only the officer sets

TAMIL_WARNING = ("எச்சரிக்கை: இந்த வாய்ப்பு உறுதிசெய்யப்பட்ட மோசடியுடன் பொருந்துகிறது. "
                 "எந்தப் பணமும் செலுத்த வேண்டாம். வேலைவாய்ப்பு அலுவலகத்தைத் தொடர்பு கொள்ளவும்.")
# A Tamil-speaking team member must check this text before the demo.


# ---------- Top of page ----------

ui.top_bar("Student portal")
st.caption("⚠️ Demo data — all companies, numbers and verifications are simulated.")

ui.hero(
    "Is this offer real?",
    "Paste any internship or job offer that asks you to pay. "
    "Your placement cell checks it, and every student is warned once a scam is confirmed.",
    "Before you pay anyone",
    "student",
    "Checked by", "Placement", "Cell",
)

ui.steps([
    ("Report the offer", "Paste the message and the sender's details."),
    ("Placement cell checks it", "An officer confirms it is a scam or genuine."),
    ("Every student is warned", "Anyone who gets the same offer is alerted instantly."),
])

all_cases = db.get_cases()
ui.strip([
    (sum(1 for c in all_cases if c["status"] == "Confirmed scam"), "confirmed scams on campus", True),
    (sum(1 for c in all_cases if (c["status"] or "").startswith("Matched")), "repeat scams caught", False),
    (len(all_cases), "offers reported", False),
])


# ---------- Your details (visible, not hidden in a sidebar) ----------

with st.container(border=True):
    ui.label("Your details")
    c1, c2 = st.columns(2)
    name = c1.text_input("Your name", placeholder="Enter your name", key="name")
    reg_no = c2.text_input("Register number", placeholder="Enter your register number", key="reg_no")
    st.caption("Prototype: no real login. Use sample details for the demo.")

has_identity = bool(name.strip() and reg_no.strip())
reporter = f"{name.strip()} ({reg_no.strip()})"


# ---------- Tabs ----------

my_cases = db.get_cases_by_reporter(reporter) if has_identity else []
updated = sum(1 for c in my_cases if c["status"] in DECIDED)
my_label = f"My reports ({updated} updated)" if updated else "My reports"

tab_report, tab_mine, tab_search = st.tabs(["Check an offer", my_label, "Search confirmed scams"])


# ---------- Check an offer ----------

def show_result(r: dict) -> None:
    """One clear verdict card, shown in place of the form."""
    if r["match"]:
        m = r["match"]
        ui.result_card(
            "danger",
            "Stop. This offer matches a confirmed scam.",
            [f"The {m['matched_on']} {m['value']} was already confirmed as a scam by your placement cell "
             f"(Case #{m['case_id']}).",
             f"Officer's remark: \"{m['note']}\"",
             "Do not pay any money or share your documents. Contact the placement cell."],
            case_no=f"Your report is saved as Case #{r['case_id']}, linked to Case #{m['case_id']}.",
            tamil=TAMIL_WARNING,
        )
    elif r["flags"]:
        ui.result_card(
            "caution",
            f"Sent to your placement cell. We found {len(r['flags'])} warning sign"
            f"{'s' if len(r['flags']) != 1 else ''}.",
            ["Do not pay anything until the placement cell replies. These are cautions, not a verdict:"],
            bullets=[f"{f['flag']}: {f['reason']}" for f in r["flags"]],
            case_no=f"Case #{r['case_id']}. The decision will appear in My reports.",
        )
    else:
        ui.result_card(
            "calm",
            "Sent to your placement cell.",
            ["We found no warning signs, but that does not prove the offer is genuine. "
             "Wait for the placement cell before paying anything."],
            case_no=f"Case #{r['case_id']}. The decision will appear in My reports.",
        )


with tab_report:
    result = st.session_state.get("last_result")

    if result:
        show_result(result)
        if st.button("Check another offer", type="primary"):
            st.session_state.pop("last_result", None)
            st.rerun()
    else:
        with st.form("report_form", clear_on_submit=False):
            company = st.text_input("Company the offer claims to be from", placeholder="e.g. Nexovanta Careers")
            offer_text = st.text_area("Offer message", height=140,
                                      placeholder="Paste the WhatsApp message or email here")
            col1, col2, col3 = st.columns(3)
            sender_email = col1.text_input("Sender email")
            phone = col2.text_input("Phone number")
            upi_id = col3.text_input("UPI ID, if they asked for payment")
            submitted = st.form_submit_button("Check this offer", type="primary", width="stretch")

        if submitted:
            if not has_identity:
                st.warning("Enter your name and register number in Your details first.")
            elif not offer_text.strip():
                st.warning("Paste the offer message to check it.")
            else:
                flags = red_flags.check_offer(offer_text, sender_email, company)
                match = matching.find_confirmed_match(phone, sender_email, upi_id)

                case = {
                    "reporter": reporter,
                    "company_claimed": company,
                    "offer_text": offer_text,
                    "sender_email": sender_email,
                    "phone": phone,
                    "upi_id": upi_id,
                    "flags": "; ".join(f["flag"] for f in flags),
                }
                if match:
                    case["status"] = f"Matched #{match['case_id']}"
                    case["matched_case_id"] = match["case_id"]
                case_id = db.add_case(case)

                st.session_state.last_result = {"case_id": case_id, "flags": flags, "match": match}
                st.rerun()


# ---------- My reports: updates arrive on their own ----------

@st.fragment(run_every=4)
def watch_my_updates() -> None:
    """Every 4 seconds, check whether the officer has decided on any of my reports.
    If something changed, redraw the page so the student sees it without refreshing."""
    if not has_identity:
        return
    now = sum(1 for c in db.get_cases_by_reporter(reporter) if c["status"] in DECIDED)
    key = f"seen_updates_{reporter}"
    before = st.session_state.get(key)
    st.session_state[key] = now
    if before is not None and now > before:
        st.toast("The placement cell replied to your report.", icon="📬")
        st.rerun(scope="app")


with tab_mine:
    watch_my_updates()

    if not has_identity:
        st.info("Enter your name and register number in Your details to see your reports.")
    elif not my_cases:
        st.info("No reports yet. Check an offer in the first tab and it will show up here.")
    else:
        st.caption(f"Reports from {reporter}. Decisions appear here automatically.")

    for c in my_cases:
        with st.container(border=True):
            ui.case_header(c)
            ui.quote(c["offer_text"], limit=220)

            status = c["status"]
            if status == "Pending":
                st.caption("Waiting for the placement officer.")
            elif status == "Confirmed scam":
                ui.note(c["officer_note"])
                st.error("Confirmed scam. Do not pay or share your documents.")
            elif status == "Genuine":
                ui.note(c["officer_note"])
                st.success("The placement cell checked this offer and found it genuine.")
            elif status == "Unverified":
                ui.note(c["officer_note"])
                st.info("The placement cell could not verify this offer yet. Do not pay until it is confirmed.")
            elif status.startswith("Matched"):
                st.error(f"Matched confirmed scam Case #{c['matched_case_id']}. Do not pay.")


# ---------- Search confirmed scams ----------

with tab_search:
    query = st.text_input("Search by company, email, phone or UPI ID",
                          placeholder="e.g. Nexovanta or someone@okaxis")
    results = db.search_confirmed(query)
    st.caption("Only offers the placement officer has confirmed as scams are listed.")

    if not results:
        st.info("No confirmed scam matches that. Still unsure? Check the offer in the first tab.")

    for c in results:
        with st.container(border=True):
            ui.case_header(c)
            ui.facts(c)
            ui.note(c["officer_note"])


ui.footer()