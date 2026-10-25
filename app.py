"""
Campus Shield - Streamlit application.

Run using:
    streamlit run app.py
"""

import streamlit as st

from core import db, matching, red_flags


# ---------- Page setup ----------

st.set_page_config(
    page_title="Campus Shield",
    page_icon="🛡️",
    layout="centered"
)

# Prepare the database
db.init_db()


# ---------- Sidebar ----------

st.sidebar.title("🛡️ Campus Shield")

role = st.sidebar.radio(
    "View as",
    ["Student", "Placement officer"]
)

st.sidebar.caption(
    "Demo only: no real login in this prototype. "
    "All data is sample data."
)


# ---------- Show a confirmed-scam warning ----------

def show_warning(match: dict) -> None:
    """
    Display a warning when a report matches
    an existing confirmed scam.
    """

    st.error(
        f"**Warning: this offer matches a confirmed scam.** "
        f"The {match['matched_on']} "
        f"**{match['value']}** belongs to Case #{match['case_id']}. "
        f"Officer's note: \"{match['note']}\". "
        "Do not pay any money. Contact the placement cell."
    )

    # Tamil warning
    st.error(
        f"**எச்சரிக்கை: இந்த வாய்ப்பு உறுதிசெய்யப்பட்ட "
        f"மோசடியுடன் பொருந்துகிறது.** "
        f"இது வழக்கு #{match['case_id']}-உடன் தொடர்புடையது. "
        "எந்தப் பணமும் செலுத்த வேண்டாம். "
        "வேலைவாய்ப்பு அலுவலகத்தைத் தொடர்பு கொள்ளவும்."
    )


# ==================================================
# STUDENT VIEW
# ==================================================

if role == "Student":

    tab_report, tab_search = st.tabs(
        ["Report a suspicious offer", "Search confirmed scams"]
    )

    # ---------- Report an offer ----------

    with tab_report:

        st.subheader("Report a suspicious offer")

        with st.form("report_form", clear_on_submit=False):

            reporter = st.text_input(
                "Your name (sample)",
                value="Student A"
            )

            company = st.text_input(
                "Company the offer claims to be from"
            )

            offer_text = st.text_area(
                "Paste the offer message",
                height=150
            )

            col1, col2, col3 = st.columns(3)

            sender_email = col1.text_input("Sender email")
            phone = col2.text_input("Phone number")
            upi_id = col3.text_input("UPI ID (if payment requested)")

            submitted = st.form_submit_button("Check & Submit")

        # Process the submitted report
        if submitted:

            if not offer_text.strip():

                st.warning("Please paste the offer message.")

            else:

                # Check for warning signs
                flags = red_flags.check_offer(
                    offer_text,
                    sender_email,
                    company
                )

                # Search for an existing confirmed scam
                match = matching.find_confirmed_match(
                    phone,
                    sender_email,
                    upi_id
                )

                # Prepare the new report
                case = {
                    "reporter": reporter,
                    "company_claimed": company,
                    "offer_text": offer_text,
                    "sender_email": sender_email,
                    "phone": phone,
                    "upi_id": upi_id,
                    "flags": "; ".join(
                        flag["flag"] for flag in flags
                    ),
                }

                # Link the report if a confirmed scam matches
                if match:

                    case["status"] = f"Matched #{match['case_id']}"
                    case["matched_case_id"] = match["case_id"]

                # Save the report
                case_id = db.add_case(case)

                # Display a warning if a confirmed scam matches
                if match:
                    show_warning(match)

                # Display any warning signs
                if flags:

                    st.markdown(
                        "**Red flags found** "
                        "(cautions, not a verdict):"
                    )

                    for flag in flags:
                        st.warning(
                            f"**{flag['flag']}**: {flag['reason']}"
                        )

                elif not match:

                    st.info(
                        "No red flags found. "
                        "That does not prove the offer is genuine."
                    )

                # Show the appropriate success message
                if match:

                    st.success(
                        f"Report saved as Case #{case_id}, "
                        f"linked to confirmed Case #{match['case_id']}."
                    )

                else:

                    st.success(
                        f"Report saved as Case #{case_id}. "
                        "The report is awaiting placement officer review."
                    )

    # ---------- Search confirmed scams ----------

    with tab_search:

        st.subheader("Search confirmed scams")

        st.caption(
            "Only cases confirmed by the placement officer "
            "are shown here."
        )

        query = st.text_input(
            "Search by company, email, phone or UPI ID"
        )

        results = db.search_confirmed(query)

        if not results:

            st.info("No confirmed scams match your search.")

        else:

            for case in results:

                with st.container(border=True):

                    company_name = (
                        case["company_claimed"] or "Unknown company"
                    )

                    st.markdown(
                        f"**Case #{case['case_id']}: {company_name}**"
                        f" · {case['created_at'][:10]}"
                    )

                    st.write(
                        f"Email: {case['sender_email'] or '-'}"
                        f" · Phone: {case['phone'] or '-'}"
                        f" · UPI: {case['upi_id'] or '-'}"
                    )

                    st.caption(
                        f"Officer's note: {case['officer_note']}"
                    )


# ==================================================
# PLACEMENT OFFICER VIEW
# ==================================================

else:

    tab_queue, tab_all = st.tabs(
        ["Review queue", "All cases"]
    )

    # ---------- Review pending reports ----------

    with tab_queue:

        st.subheader("Review queue")

        pending_cases = db.get_cases("Pending")

        if not pending_cases:

            st.info("No pending reports.")

        else:

            for case in pending_cases:

                with st.container(border=True):

                    company_name = (
                        case["company_claimed"] or "Unknown company"
                    )

                    st.markdown(
                        f"**Case #{case['case_id']}: {company_name}**"
                        f" · {case['created_at']}"
                    )

                    st.text(case["offer_text"])

                    st.write(
                        f"Email: {case['sender_email'] or '-'}"
                        f" · Phone: {case['phone'] or '-'}"
                        f" · UPI: {case['upi_id'] or '-'}"
                    )

                    st.caption(
                        f"Red flags: {case['flags'] or 'none'}"
                    )

                    # Officer selects a decision
                    decision = st.radio(
                        "Decision",
                        [
                            "Confirmed scam",
                            "Genuine",
                            "Unverified"
                        ],
                        key=f"decision_{case['case_id']}",
                        horizontal=True
                    )

                    # Officer explains the decision
                    note = st.text_input(
                        "Note (shown in warnings if confirmed)",
                        key=f"note_{case['case_id']}"
                    )

                    # Save the officer's decision
                    if st.button(
                        "Save decision",
                        key=f"save_{case['case_id']}"
                    ):

                        if decision == "Confirmed scam" and not note.strip():

                            st.warning(
                                "Add a note explaining why "
                                "the offer is a scam."
                            )

                        else:

                            db.set_status(
                                case["case_id"],
                                decision,
                                note
                            )

                            st.rerun()

    # ---------- View all reports ----------

    with tab_all:

        st.subheader("All cases")

        cases = db.get_cases()

        if not cases:

            st.info("No cases yet.")

        else:

            case_data = [
                {
                    "Case": case["case_id"],
                    "Date": case["created_at"],
                    "Company": case["company_claimed"],
                    "Status": case["status"],
                    "Note": case["officer_note"]
                }
                for case in cases
            ]

            st.dataframe(
                case_data,
                hide_index=True,
                width="stretch"
            )