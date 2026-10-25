"""Shared look for both apps: fonts, colours, top bar, header with the
verification stamp, steps, result cards, status badges and case cards.

Only fixed text and html-escaped values go into HTML, never raw user input.
"""
import html

import streamlit as st

INK = "#1E1B4B"       # deep indigo
PAGE = "#ECEEFB"      # periwinkle page
MARIGOLD = "#E8A317"  # caution accent
SCAM = "#B42318"
GENUINE = "#127A4B"
SLATE = "#5B6178"

TEAM = "Team KALIBRE · Sona College of Technology, Salem"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Hind+Madurai:wght@400;500;600&display=swap');

html, body, .stApp, [data-testid="stMarkdownContainer"], input, textarea, button, label {{
  font-family: 'Hind Madurai', system-ui, sans-serif;
}}
h1, h2, h3, .cs-display {{ font-family: 'Bricolage Grotesque', 'Hind Madurai', sans-serif; }}

#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stSidebarCollapsedControl"] {{ display: none; }}
header[data-testid="stHeader"] {{ background: transparent; height: 0; }}

.stApp {{
  background:
    radial-gradient(1200px 500px at 85% -10%, rgba(232,163,23,.18), transparent 60%),
    radial-gradient(900px 500px at -10% 10%, rgba(99,102,241,.16), transparent 60%),
    {PAGE};
}}
.block-container {{ padding-top: 1.2rem; padding-bottom: 3rem; max-width: 960px; }}

/* ---------- Top bar ---------- */
.cs-top {{
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 4px 2px 14px; flex-wrap: wrap;
}}
.cs-brand {{ display: flex; align-items: center; gap: 10px; color: {INK}; }}
.cs-logo {{
  width: 34px; height: 34px; border-radius: 10px; background: {INK};
  display: grid; place-items: center; color: {MARIGOLD}; font-size: 18px;
}}
.cs-brand b {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.2rem; font-weight: 800; }}
.cs-brand span {{ color: {SLATE}; font-size: .9rem; margin-left: 4px; }}
.cs-team {{ color: {SLATE}; font-size: .85rem; }}

/* ---------- Header ---------- */
.cs-hero {{
  position: relative; overflow: hidden; border-radius: 22px;
  padding: 30px 32px; margin-bottom: 14px; color: #fff;
  display: grid; grid-template-columns: 1fr auto; gap: 24px; align-items: center;
}}
.cs-hero.student {{ background: {INK}; }}
.cs-hero.officer {{ background: #2A2560; }}
.cs-hero::after {{
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background-image: repeating-linear-gradient(135deg, rgba(255,255,255,.035) 0 2px, transparent 2px 14px);
}}
.cs-hero h1 {{
  color: #fff; font-size: 2.35rem; line-height: 1.05; margin: 0 0 10px; padding: 0;
  font-weight: 800; letter-spacing: -.02em;
}}
.cs-hero p {{ color: rgba(255,255,255,.82); margin: 0; font-size: 1.02rem; max-width: 50ch; }}
.cs-who {{ color: {MARIGOLD}; font-weight: 600; font-size: .95rem; margin-bottom: 6px; }}

/* the stamp: the one bold element */
.cs-stamp {{
  width: 140px; height: 140px; border-radius: 50%;
  border: 3px solid {MARIGOLD}; color: {MARIGOLD};
  display: flex; align-items: center; justify-content: center; text-align: center;
  transform: rotate(-12deg); position: relative; z-index: 1;
  box-shadow: inset 0 0 0 6px {INK}, inset 0 0 0 8px rgba(232,163,23,.7);
  font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: .68rem; line-height: 1.2; letter-spacing: .1em; text-transform: uppercase;
}}
.cs-stamp b {{ display: block; font-size: .98rem; letter-spacing: .03em; margin: 3px 0; }}
@media (max-width: 640px) {{
  .cs-hero {{ grid-template-columns: 1fr; padding: 24px; }}
  .cs-stamp {{ width: 112px; height: 112px; font-size: .56rem; }}
  .cs-stamp b {{ font-size: .8rem; }}
  .cs-hero h1 {{ font-size: 1.8rem; }}
}}

/* ---------- How it works ---------- */
.cs-steps {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 0 0 14px; }}
.cs-step {{
  background: #fff; border: 1px solid #DCDFF2; border-radius: 14px; padding: 12px 14px;
  display: flex; gap: 10px; align-items: flex-start;
}}
.cs-step i {{
  font-style: normal; flex: 0 0 26px; height: 26px; border-radius: 50%;
  background: {PAGE}; color: {INK}; display: grid; place-items: center;
  font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: .85rem;
}}
.cs-step b {{ display: block; color: {INK}; font-size: .95rem; line-height: 1.3; }}
.cs-step span {{ color: {SLATE}; font-size: .84rem; line-height: 1.35; }}
@media (max-width: 640px) {{ .cs-steps {{ grid-template-columns: 1fr; }} }}

/* ---------- Live numbers ---------- */
.cs-strip {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 16px; }}
.cs-chip {{
  background: #fff; border: 1px solid #DCDFF2; border-radius: 999px;
  padding: 6px 14px; font-size: .92rem; color: {INK};
}}
.cs-chip b {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.05rem; margin-right: 4px; }}
.cs-chip.alert b {{ color: {SCAM}; }}

/* ---------- Section label ---------- */
.cs-label {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; color: {INK};
  font-size: 1.05rem; margin: 4px 0 2px; }}

/* ---------- Tabs as pills ---------- */
.stTabs [role="tablist"] {{
  gap: 6px; background: #fff; padding: 6px; border-radius: 14px;
  border: 1px solid #DCDFF2; width: fit-content; max-width: 100%;
}}
.stTabs [role="tab"] {{ border-radius: 10px; padding: 8px 16px; height: auto; margin: 0; }}
.stTabs [role="tab"] p {{ color: {SLATE}; font-weight: 600; }}
.stTabs [role="tab"][aria-selected="true"] {{ background: {INK} !important; }}
.stTabs [role="tab"][aria-selected="true"] p {{ color: #fff; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}

/* ---------- Surfaces ---------- */
[data-testid="stForm"] {{
  background: #fff; border: 1px solid #DCDFF2; border-radius: 18px; padding: 22px 22px 18px;
}}
[data-testid="stVerticalBlockBorderWrapper"] {{ background: #fff; border-radius: 16px; }}

.stTextInput input, .stTextArea textarea {{
  border: 1.5px solid #CDD1EA !important; border-radius: 10px !important;
  background: #F7F8FE !important; color: {INK} !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
  border-color: {INK} !important; background: #fff !important;
}}

.stButton button, [data-testid="stFormSubmitButton"] button {{ border-radius: 10px; font-weight: 600; }}
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"],
.stButton button[kind="primary"] {{ background: {MARIGOLD}; color: {INK}; border: none; }}
[data-testid="stFormSubmitButton"] button[kind="primaryFormSubmit"]:hover,
.stButton button[kind="primary"]:hover {{ background: #D4920C; color: {INK}; }}
button:focus-visible {{ outline: 3px solid {MARIGOLD} !important; outline-offset: 2px; }}

/* ---------- Result card (after checking an offer) ---------- */
.cs-result {{ border-radius: 18px; padding: 22px 24px; margin: 6px 0 12px; border: 1px solid; }}
.cs-result h2 {{ font-size: 1.5rem; margin: 0 0 6px; padding: 0; line-height: 1.15; }}
.cs-result p {{ margin: 0 0 8px; font-size: 1rem; }}
.cs-result .cs-case-no {{ font-size: .88rem; opacity: .85; }}
.cs-result.danger {{ background: #FDECEA; border-color: #F4B7B1; color: #5C120C; }}
.cs-result.danger h2 {{ color: {SCAM}; }}
.cs-result.caution {{ background: #FFF6E0; border-color: #F2D28B; color: #4A3300; }}
.cs-result.caution h2 {{ color: #8A5A00; }}
.cs-result.calm {{ background: #fff; border-color: #DCDFF2; color: {INK}; }}
.cs-result.calm h2 {{ color: {INK}; }}
.cs-result ul {{ margin: 6px 0 8px; padding-left: 20px; }}
.cs-result li {{ margin-bottom: 4px; }}
.cs-result .ta {{ border-top: 1px solid rgba(0,0,0,.08); padding-top: 8px; margin-top: 8px; font-size: .95rem; }}

/* ---------- Status ---------- */
.cs-badge {{
  display: inline-block; padding: 3px 11px; border-radius: 999px;
  font-size: .8rem; font-weight: 600; line-height: 1.5; vertical-align: middle;
}}
.cs-pending    {{ background: #FDF1D6; color: #8A5A00; }}
.cs-scam       {{ background: #FDE3E1; color: {SCAM}; }}
.cs-genuine    {{ background: #DDF3E8; color: {GENUINE}; }}
.cs-unverified {{ background: #E6E8F2; color: {SLATE}; }}
.cs-matched    {{ background: {SCAM}; color: #fff; }}

.cs-case {{ border-left: 5px solid #CDD1EA; padding-left: 14px; }}
.cs-case.pending {{ border-color: {MARIGOLD}; }}
.cs-case.scam, .cs-case.matched {{ border-color: {SCAM}; }}
.cs-case.genuine {{ border-color: {GENUINE}; }}
.cs-title {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.08rem; color: {INK}; }}
.cs-meta {{ color: {SLATE}; font-size: .86rem; margin-top: 2px; }}
.cs-note {{
  background: #F2F3FC; border-radius: 10px; padding: 10px 14px; margin-top: 8px;
  font-size: .95rem; color: {INK};
}}
.cs-note small {{ display: block; color: {SLATE}; font-size: .8rem; margin-bottom: 2px; }}
.cs-quote {{
  background: #F7F8FE; border-radius: 10px; padding: 10px 14px; color: {INK};
  font-size: .95rem; white-space: pre-wrap; margin: 8px 0;
}}
.cs-facts {{ color: {INK}; font-size: .92rem; line-height: 1.7; }}
.cs-facts span {{ color: {SLATE}; }}

div[data-testid="stMetric"] {{
  background: #fff; border: 1px solid #DCDFF2; border-radius: 16px; padding: 14px 18px;
}}
div[data-testid="stMetricValue"] {{ font-family: 'Bricolage Grotesque', sans-serif; color: {INK}; }}

.cs-foot {{ text-align: center; color: {SLATE}; font-size: .82rem; margin-top: 28px; }}

@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; animation: none !important; }} }}
</style>
"""

e = html.escape


def apply_style() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def top_bar(portal: str) -> None:
    st.markdown(
        f'<div class="cs-top"><div class="cs-brand"><div class="cs-logo">🛡</div>'
        f"<b>Campus Shield</b><span>{e(portal)}</span></div>"
        f'<div class="cs-team">{e(TEAM)}</div></div>',
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, who: str, kind: str,
         stamp_top: str, stamp_mid: str, stamp_bottom: str) -> None:
    st.markdown(
        f'<div class="cs-hero {kind}"><div><div class="cs-who">{e(who)}</div>'
        f"<h1>{e(title)}</h1><p>{e(subtitle)}</p></div>"
        f'<div class="cs-stamp" aria-hidden="true"><div>{e(stamp_top)}<b>{e(stamp_mid)}</b>{e(stamp_bottom)}</div></div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def steps(items: list[tuple[str, str]]) -> None:
    """A real sequence, so numbered: (title, line)."""
    cells = "".join(
        f'<div class="cs-step"><i>{i}</i><div><b>{e(t)}</b><span>{e(d)}</span></div></div>'
        for i, (t, d) in enumerate(items, start=1)
    )
    st.markdown(f'<div class="cs-steps">{cells}</div>', unsafe_allow_html=True)


def strip(items: list[tuple[int, str, bool]]) -> None:
    chips = "".join(
        f'<span class="cs-chip{" alert" if alert else ""}"><b>{int(n)}</b>{e(label)}</span>'
        for n, label, alert in items
    )
    st.markdown(f'<div class="cs-strip">{chips}</div>', unsafe_allow_html=True)


def label(text: str) -> None:
    st.markdown(f'<div class="cs-label">{e(text)}</div>', unsafe_allow_html=True)


def result_card(kind: str, title: str, lines: list[str], bullets: list[str] | None = None,
                case_no: str = "", tamil: str = "") -> None:
    """kind: danger | caution | calm. All text is escaped here."""
    body = "".join(f"<p>{e(x)}</p>" for x in lines)
    if bullets:
        body += "<ul>" + "".join(f"<li>{e(b)}</li>" for b in bullets) + "</ul>"
    if case_no:
        body += f'<div class="cs-case-no">{e(case_no)}</div>'
    if tamil:
        body += f'<div class="ta">{e(tamil)}</div>'
    st.markdown(f'<div class="cs-result {kind}"><h2>{e(title)}</h2>{body}</div>', unsafe_allow_html=True)


def _status_key(status: str) -> str:
    s = status or "Pending"
    if s.startswith("Matched"):
        return "matched"
    return {"Pending": "pending", "Confirmed scam": "scam", "Genuine": "genuine"}.get(s, "unverified")


def badge(status: str) -> str:
    key = _status_key(status)
    text = {"pending": "Awaiting review", "scam": "Confirmed scam", "genuine": "Genuine",
            "unverified": "Unverified", "matched": "Matches a confirmed scam"}[key]
    return f'<span class="cs-badge cs-{key}">{text}</span>'


def case_header(case: dict, extra: str = "") -> None:
    company = e(case.get("company_claimed") or "Unknown company")
    date = e((case.get("created_at") or "")[:16])
    meta = f"Case #{case['case_id']}, reported {date}"
    if extra:
        meta += f". {e(extra)}"
    st.markdown(
        f'<div class="cs-case {_status_key(case.get("status"))}">'
        f'<div class="cs-title">{company} &nbsp;{badge(case.get("status"))}</div>'
        f'<div class="cs-meta">{meta}</div></div>',
        unsafe_allow_html=True,
    )


def quote(text: str, limit: int | None = None) -> None:
    t = text or ""
    if limit and len(t) > limit:
        t = t[:limit] + "…"
    st.markdown(f'<div class="cs-quote">{e(t)}</div>', unsafe_allow_html=True)


def facts(case: dict) -> None:
    st.markdown(
        f'<div class="cs-facts"><span>Email</span> {e(case.get("sender_email") or "-")}<br>'
        f'<span>Phone</span> {e(case.get("phone") or "-")}<br>'
        f'<span>UPI ID</span> {e(case.get("upi_id") or "-")}</div>',
        unsafe_allow_html=True,
    )


def note(text: str, title: str = "Placement officer's remark") -> None:
    if text:
        st.markdown(f'<div class="cs-note"><small>{e(title)}</small>{e(text)}</div>', unsafe_allow_html=True)


def footer() -> None:
    st.markdown(
        '<div class="cs-foot">Built by Team KALIBRE: Kanisha M, B R Devamayookha, Harshan S. '
        "Prototype for Hack for Social Cause, VBYLD 2027. All data shown is sample data.</div>",
        unsafe_allow_html=True,
    )