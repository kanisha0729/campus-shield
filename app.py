"""Campus Shield - Streamlit screens (Deva).

Run:  streamlit run app.py
The core/ files are stubs until Kanisha's real versions replace them.
"""
import streamlit as st

from core import db, matching, red_flags

st.set_page_config(page_title="Campus Shield", page_icon="🛡️", layout="centered")
db.init_db()

# ---------- Sidebar: demo role switch ----------
st.sidebar.title("🛡️ Campus Shield")
role = st.sidebar.radio("View as", ["Student", "Placement officer"])
st.sidebar.caption("Demo only: no real login in this prototype. All data is sample data.")


def show_warning(match: dict) -> None:
    case = db.get_case(match["case_id"])
    date = case["created_at"][:10] if case else ""
    st.error(
        f"**Warning: this offer matches a confirmed scam.** "
        f"The {match['matched_on']} **{match['value']}** belongs to Case #{match['case_id']}, "
        f"confirmed as a scam by the placement officer. "
        f"Officer's note: \"{match['note']}\". Do not pay any money. Contact the placement cell."
    )
    # Tamil text: a Tamil-speaking team member must check this before the demo.
    st.error(
        f"**எச்சரிக்கை: இந்த வாய்ப்பு உறுதிசெய்யப்பட்ட மோசடியுடன் பொருந்துகிறது.** "
        f"இது வழக்கு #{match['case_id']}-உடன் தொடர்புடையது. "
        f"எந்தப் பணமும் செலுத்த வேண்டாம். வேலைவாய்ப்பு அலுவலகத்தைத் தொடர்பு கொள்ளவும்."
    )


# ---------- Student view ----------
if role == "Student":
    tab_report, tab_search = st.tabs(["Report a suspicious offer", "Search confirmed scams"])

    with tab_report:
        st.subheader("Report a suspicious offer")
        with st.form("report_form", clear_on_submit=False):
            reporter = st.text_input("Your name (sample)", value="Student A")
            company = st.text_input("Company the offer claims to be from")
            offer_text = st.text_area("Paste the offer message", height=150)
            col1, col2, col3 = st.columns(3)
            sender_email = col1.text_input("Sender email")
            phone = col2.text_input("Phone number")
            upi_id = col3.text_input("UPI ID (if payment asked)")
            submitted = st.form_submit_button("Check & Submit")

        if submitted:
            if not offer_text.strip():
                st.warning("Please paste the offer message.")
            else:
                flags = red_flags.check_offer(offer_text, sender_email, company)
                match = matching.find_confirmed_match(phone, sender_email, upi_id)

                case = {
                    "reporter": reporter, "company_claimed": company, "offer_text": offer_text,
                    "sender_email": sender_email, "phone": phone, "upi_id": upi_id,
                    "flags": "; ".join(f["flag"] for f in flags),
                }
                if match:
                    case["status"] = f"Matched #{match['case_id']}"
                    case["matched_case_id"] = match["case_id"]
                case_id = db.add_case(case)

                if match:
                    show_warning(match)
                if flags:
                    st.markdown("**Red flags found** (cautions, not a verdict):")
                    for f in flags:
                        st.warning(f"**{f['flag']}**: {f['reason']}")
                elif not match:
                    st.info("No red flags found. That does not prove the offer is genuine.")
                st.success(f"Report saved as Case #{case_id}. The placement officer will review it.")

    with tab_search:
        st.subheader("Search confirmed scams")
        st.caption("Only cases the placement officer has confirmed are shown here.")
        q = st.text_input("Search by company, email, phone or UPI ID")
        results = db.search_confirmed(q)
        if not results:
            st.info("No confirmed scams match your search.")
        for c in results:
            with st.container(border=True):
                st.markdown(f"**Case #{c['case_id']}: {c['company_claimed'] or 'Unknown company'}**  ·  {c['created_at'][:10]}")
                st.write(f"Email: {c['sender_email'] or '-'}  ·  Phone: {c['phone'] or '-'}  ·  UPI: {c['upi_id'] or '-'}")
                st.caption(f"Officer's note: {c['officer_note']}")

# ---------- Officer view ----------
else:
    tab_queue, tab_all = st.tabs(["Review queue", "All cases"])

    with tab_queue:
        st.subheader("Review queue")
        pending = db.get_cases("Pending")
        if not pending:
            st.info("No pending reports.")
        for c in pending:
            with st.container(border=True):
                st.markdown(f"**Case #{c['case_id']}: {c['company_claimed'] or 'Unknown company'}**  ·  {c['created_at']}")
                st.text(c["offer_text"])
                st.write(f"Email: {c['sender_email'] or '-'}  ·  Phone: {c['phone'] or '-'}  ·  UPI: {c['upi_id'] or '-'}")
                st.caption(f"Red flags: {c['flags'] or 'none'}")
                decision = st.radio("Decision", ["Confirmed scam", "Genuine", "Unverified"],
                                    key=f"dec_{c['case_id']}", horizontal=True)
                note = st.text_input("Note (shown in warnings if confirmed)", key=f"note_{c['case_id']}")
                if st.button("Save decision", key=f"save_{c['case_id']}"):
                    if decision == "Confirmed scam" and not note.strip():
                        st.warning("Add a note explaining why it is a scam.")
                    else:
                        db.set_status(c["case_id"], decision, note)
                        st.rerun()

    with tab_all:
        st.subheader("All cases")
        cases = db.get_cases()
        if not cases:
            st.info("No cases yet.")
        else:
            st.dataframe(
                [{"Case": c["case_id"], "Date": c["created_at"], "Company": c["company_claimed"],
                  "Status": c["status"], "Note": c["officer_note"]} for c in cases],
                hide_index=True, width="stretch",
            )
