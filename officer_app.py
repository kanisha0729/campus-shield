"""
Campus Shield - placement officer app (separate from the student app).

Run in a second terminal:
    python -m streamlit run officer_app.py --server.port 8502
Opens at http://localhost:8502

Locked with a PIN. Set it with the environment variable
CAMPUS_SHIELD_OFFICER_PIN; if not set, the demo PIN 1234 is used.
New reports appear automatically, so the officer never needs to refresh
(refreshing the browser would ask for the PIN again).
"""

import os

import streamlit as st

from core import db, ui

st.set_page_config(page_title="Campus Shield · Officer", page_icon="🛡️", layout="centered",
                   initial_sidebar_state="collapsed")
ui.apply_style()
db.init_db()

OFFICER_PIN = os.environ.get("CAMPUS_SHIELD_OFFICER_PIN", "1234")

ui.top_bar("Placement cell")


# ---------- PIN lock ----------

if not st.session_state.get("officer_ok"):
    ui.hero("Placement cell sign-in",
            "Only the placement officer can confirm or clear a reported offer.",
            "Officer access", "officer", "Placement", "Cell", "Only")
    with st.form("login"):
        pin = st.text_input("Officer PIN", type="password")
        ok = st.form_submit_button("Unlock dashboard", type="primary")
    if ok:
        if pin == OFFICER_PIN:
            st.session_state.officer_ok = True
            st.rerun()
        else:
            st.error("That PIN is wrong. Try again.")
    st.stop()


# ---------- Live watcher: new reports arrive without a browser refresh ----------

@st.fragment(run_every=4)
def watch_new_reports() -> None:
    """Every 4 seconds, count cases. If a new one arrived, redraw the dashboard."""
    total = len(db.get_cases())
    before = st.session_state.get("seen_total")
    st.session_state.seen_total = total
    if before is not None and total > before:
        st.toast("New report received.", icon="📥")
        st.rerun(scope="app")


watch_new_reports()


# ---------- Header and summary ----------

ui.hero("Review queue",
        "Check each reported offer. Your decision and remark go straight to the student who reported it.",
        "Placement officer", "officer", "Checked by", "Placement", "Cell")

all_cases = db.get_cases()
count = lambda s: sum(1 for c in all_cases if c["status"] == s)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Awaiting review", count("Pending"))
m2.metric("Confirmed scams", count("Confirmed scam"))
m3.metric("Genuine", count("Genuine"))
m4.metric("Repeat scams caught", sum(1 for c in all_cases if (c["status"] or "").startswith("Matched")))

st.caption("New reports appear here on their own. No need to refresh the page.")

tab_queue, tab_all = st.tabs(["Awaiting review", "All cases"])


# ---------- Review queue: details left, decision right ----------

with tab_queue:
    pending = db.get_cases("Pending")
    if not pending:
        st.info("Nothing to review. New reports will appear here automatically.")

    for c in pending:
        with st.container(border=True):
            ui.case_header(c, extra=f"From {c['reporter'] or 'unknown'}")
            left, right = st.columns([3, 2], gap="large")

            with left:
                ui.quote(c["offer_text"])
                ui.facts(c)
                st.caption(f"Red flags: {c['flags'] or 'none'}")

            with right:
                decision = st.radio("Decision", ["Confirmed scam", "Genuine", "Unverified"],
                                    key=f"dec_{c['case_id']}")
                remark = st.text_area("Remark for the student", key=f"note_{c['case_id']}", height=90,
                                      placeholder="e.g. Company confirmed it never sent this offer")
                if st.button("Send decision", key=f"save_{c['case_id']}", type="primary", width="stretch"):
                    if not remark.strip():
                        st.warning("Add a remark first. The student will read it.")
                    else:
                        db.set_status(c["case_id"], decision, remark)
                        st.toast(f"Decision sent for Case #{c['case_id']}.", icon="✅")
                        st.rerun()


# ---------- All cases ----------

with tab_all:
    if not all_cases:
        st.info("No cases yet.")
    else:
        st.dataframe(
            [{"Case": c["case_id"], "Date": c["created_at"], "Reporter": c["reporter"],
              "Company": c["company_claimed"], "Status": c["status"], "Remark": c["officer_note"]}
             for c in all_cases],
            hide_index=True, width="stretch",
        )


# ---------- Account and demo tools ----------

st.divider()
a, b = st.columns([1, 1])
with a:
    if st.button("Log out"):
        st.session_state.officer_ok = False
        st.rerun()
with b:
    with st.expander("Demo tools"):
        st.caption("Deletes every case. Use only before a demo.")
        if st.button("Reset all demo data"):
            db.reset_demo()
            st.rerun()

ui.footer()