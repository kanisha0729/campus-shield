# Campus Shield

**A placement-cell verified scam registry for internship and job offers.**
Hack for Social Cause (VBYLD 2027) · Theme: Digital Safety & Cyber Fraud Awareness · Team KALIBRE (HSC|TN|01014)

College students in Tamil Nadu, especially those looking for a mandatory internship, receive fake internship and job offers over WhatsApp, email and LinkedIn that ask for a fee over UPI. When one student spots a scam, nobody else in the college is warned.

Campus Shield is a web app run by the college placement cell:

1. A student reports a suspicious offer.
2. The app shows transparent red flags (cautions, never a verdict).
3. The placement officer reviews the case and marks it **Confirmed scam**, **Genuine** or **Unverified**.
4. Any later report with the same phone number, email or UPI ID as a confirmed scam warns the student instantly, in English and Tamil, with a link to the case.

One student's verified report protects the whole campus.

---

## Setup

Requirements: Python 3.10 or newer.

```bash
git clone https://github.com/kanisha0729/campus-shield.git
cd campus-shield
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py seed.py                          # loads 16 simulated sample cases
py -m streamlit run app.py          # student page
py -m streamlit run officer_app.py --server.port 8502   # officer page (second terminal)
py -m pytest                        # runs the tests
```

On macOS/Linux use `python3` instead of `py` and `source .venv/bin/activate`.

The student page opens at `http://localhost:8501` and the officer page at `http://localhost:8502`.

All names, phone numbers, emails and UPI IDs in `data/sample_cases.csv` are simulated. No real student or company data is used.

### Environment variables

None are required. The app uses free, local tools only and needs no API keys.

---

## Demo (under one minute)

Open the student page and the officer page side by side. There is no real login in this prototype.

1. **Student A** reports an offer from "TechNova Solutions" that asks for a Rs 2,000 registration fee to UPI ID `technova.hr@okaxis`. Red flags appear: fee demand, free-mail sender, urgency.
2. **Placement officer** opens the review queue and marks the case **Confirmed scam** with a note.
3. **Student B** reports a different-looking offer with the **same UPI ID**.
4. Campus Shield warns Student B immediately in English and Tamil and shows the confirmed case.

---

## How it works

| Step | What happens |
| --- | --- |
| Report | Student enters the offer text, company, sender email, phone and UPI ID. |
| Red-flag check | Rule-based checks with a reason shown for each flag. |
| Match | Phone, email and UPI ID are normalised and compared against **officer-confirmed cases only**. |
| Review | Only the placement officer can mark a case as a scam. |
| Warn | A matching report triggers a warning that names what matched and links to the case. |
| Search | Students can search confirmed scams before replying to an offer. Pending cases are never shown to students. |

Unreviewed reports are never used for matching, so one wrong report cannot warn the whole campus.

---

## Project structure

```
campus-shield/
├── app.py               # student page
├── officer_app.py       # placement officer page
├── seed.py              # loads the sample data
├── core/
│   ├── db.py            # save and read cases (SQLite)
│   ├── ui.py            # shared styling
│   ├── red_flags.py     # rule-based red-flag checks with reasons
│   └── matching.py      # normalise and match against confirmed cases
├── data/sample_cases.csv   # 16 simulated, labelled cases
├── tests/               # 8 tests for red flags, matching, search and seeding
├── docs/
│   └── technical_design.md   # architecture diagram and explanation
├── ai_log.md            # record of AI tool use
├── requirements.txt
└── LICENSE              # MIT
```

---

## Limitations

- **Sample data only.** No real student data is stored.
- **No real login.** The separate student and officer pages are for the demo.
- **Rule-based checks.** Red flags are cautions, not proof. A real offer can trigger a flag, and a scam can avoid all of them.
- **Exact matching.** A scammer who changes phone, email and UPI ID will not match a past case.
- **Single college.** The prototype runs one registry for one placement cell.

## Future work

- Possible-match flags for similar offer wording, sent to the officer for review (never auto-confirmed).
- Reading phone, email and UPI ID from WhatsApp screenshots.
- Colleges across Tamil Nadu sharing confirmed cases in one network.

---

## Use of AI tools

AI assistants (Claude, ChatGPT) were used for idea research, drafting documents, and generating parts of the code, which the team then reviewed, tested and edited. The share of AI-assisted work is stated in our presentation.

## Team

| Member | Role |
| --- | --- |
| Kanisha M (lead) | Core logic: database, red-flag checks, matching |
| B R Devamayookha | Streamlit screens, demo, documentation |
| Harshan S | Sample data, test cases, submission documents |

## License

MIT. See [LICENSE](LICENSE).