# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN v8.15 — STREAMLIT UI
Ändringar från v8.14:
  FIX 1 — Source links: _normalize_urls() bevarar alla URLs, aldrig droppade
  FIX 2 — Confidence scoring: viktad score (styrka×bevisantal×källkvalitet), unik per hypotes
  FIX 3 — Hypothesis bars: H1 STRUKTURELL ███████░░░ 72% med procent
  FIX 4 — Text wrap: word-break:normal, overflow-wrap:break-word, max-width:100%
  FIX 5 — Assessment: SLUTSATS (1 mening) + EXPLANATION (resonemang), ingen duplikering
  FIX 6 — Reality Check: CLAIM / STATUS / SOURCE strukturerat format
  FIX 7 — Hypothesis readability: full titel i rubrik, score+pct i header, 4 sektioner
  BUGFIX — conf_score/conf_pct nyckelnamn konsistenta med normalizer v1.2
"""

import os, re
import streamlit as st
from datetime import date as _date
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Sanningsmaskinen", page_icon="◎", layout="wide",
                   initial_sidebar_state="collapsed")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@300;400;500;600&family=Libre+Franklin:wght@300;400;600;700&display=swap');

:root {
  --bg:       #0b0b0c; --bg1: #0f0f11; --bg2: #131316; --bg3: #18181c;
  --border:   #1f1f24; --border2: #2a2a32;
  --ink:      #e2ddd6; --ink2: #a09a92; --ink3: #5a5650; --ink4: #333038;
  --grn:      #3d9970; --grn-bg: #0a1410; --grn-dim: #1a3028;
  --amb:      #c0882a; --amb-bg: #120e04; --amb-dim: #2a2010;
  --red:      #c0442a; --red-bg: #130808; --red-dim: #2a1410;
  --blu:      #4a7fc0; --blu-bg: #080d14; --blu-dim: #101830;
  --mono: 'JetBrains Mono', monospace;
  --serif: 'Spectral', serif;
  --sans: 'Libre Franklin', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
  font-family: var(--sans); background: var(--bg); color: var(--ink);
  -webkit-font-smoothing: antialiased;
}

.main .block-container { max-width: 1040px; padding: 0 1.5rem 5rem; margin: 0 auto; }

/* FIX 4: Text wrap — prevent vertical text */
* {
  word-break: normal !important;
  overflow-wrap: break-word !important;
  max-width: 100%;
  white-space: normal !important;
}
pre, code, .analysis-text, .mono-block {
  white-space: pre-wrap !important;
  word-break: break-all !important;
}

/* ── Topbar ── */
.topbar {
  display:flex; align-items:center; justify-content:space-between;
  padding:1rem 0 0.8rem; border-bottom:1px solid var(--border); margin-bottom:1.5rem;
}
.topbar-left  { display:flex; align-items:baseline; gap:1rem; }
.topbar-mark  { font-family:var(--mono); font-size:0.6rem; font-weight:600;
                letter-spacing:0.35em; color:var(--ink3); text-transform:uppercase; }
.topbar-title { font-family:var(--serif); font-size:1.05rem; font-weight:600;
                color:var(--ink2); letter-spacing:0.01em; }
.topbar-right { font-family:var(--mono); font-size:0.6rem; color:var(--ink4); letter-spacing:0.1em; }

/* ── Input ── */
.stTextArea textarea {
  background:var(--bg2) !important; border:1px solid var(--border2) !important;
  border-radius:2px !important; color:var(--ink) !important;
  font-family:var(--serif) !important; font-size:1rem !important;
  padding:0.75rem 1rem !important; line-height:1.6 !important;
}
.stTextArea textarea:focus { border-color:var(--blu) !important; }
.stTextArea textarea::placeholder { color:var(--ink4) !important; }

.stButton > button {
  background:var(--ink) !important; color:var(--bg) !important; border:none !important;
  border-radius:2px !important; font-family:var(--mono) !important; font-size:0.65rem !important;
  font-weight:600 !important; letter-spacing:0.15em !important; padding:0.55rem 1.4rem !important;
  text-transform:uppercase !important; transition:opacity 0.15s !important;
}
.stButton > button:hover { opacity:0.85 !important; }
.stButton > button:disabled { opacity:0.3 !important; }

/* ── Progress ── */
.step-row { display:flex; gap:0.35rem; flex-wrap:wrap; margin:1rem 0 1.5rem; }
.step { font-family:var(--mono); font-size:0.6rem; padding:0.2rem 0.6rem;
        border:1px solid var(--border); color:var(--ink4); letter-spacing:0.05em; }
.step-done   { border-color:var(--grn-dim); color:var(--grn); background:var(--grn-bg); }
.step-active { border-color:var(--blu); color:var(--blu); background:var(--blu-bg);
               animation:blink 1.4s ease-in-out infinite; }
.step-warn   { border-color:var(--red-dim); color:var(--red); background:var(--red-bg); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* ── Zone panels ── */
.zone { border:1px solid var(--border); margin-bottom:0.6rem; margin-top:24px; overflow:hidden; }
.zone-header {
  font-family:var(--mono); font-size:0.55rem; font-weight:600; letter-spacing:0.3em;
  text-transform:uppercase; padding:0.55rem 1rem; background:var(--bg2);
  border-bottom:1px solid var(--border); color:var(--ink3);
  display:flex; align-items:center; justify-content:space-between;
}
.zone-header-accent { border-left:3px solid; }
.zone-grn { border-left-color:var(--grn) !important; }
.zone-amb { border-left-color:var(--amb) !important; }
.zone-red { border-left-color:var(--red) !important; }
.zone-blu { border-left-color:var(--blu) !important; }
.zone-body { padding:1rem; background:var(--bg1); }

/* ── Status pills ── */
.pill {
  display:inline-block; font-family:var(--mono); font-size:0.58rem;
  font-weight:600; letter-spacing:0.12em; padding:0.18rem 0.65rem;
  border:1px solid; text-transform:uppercase;
}
.pill-grn { color:var(--grn); border-color:var(--grn-dim); background:var(--grn-bg); }
.pill-amb { color:var(--amb); border-color:var(--amb-dim); background:var(--amb-bg); }
.pill-red { color:var(--red); border-color:var(--red-dim); background:var(--red-bg); }
.pill-blu { color:var(--blu); border-color:var(--blu-dim); background:var(--blu-bg); }
.pill-dim { color:var(--ink3); border-color:var(--border); background:var(--bg2); }

/* ── FIX 5: Assessment — 1 mening + explanation ── */
.assessment-conclusion {
  font-family:var(--serif); font-size:1.08rem; font-weight:600;
  color:#b0e4c0; line-height:1.5; padding:0.8rem 1rem;
  border-left:4px solid var(--grn); background:var(--grn-bg);
  margin-bottom:0.5rem;
}
.assessment-label {
  font-family:var(--mono); font-size:0.5rem; letter-spacing:0.3em;
  color:var(--grn); margin-bottom:0.3rem;
}
.assessment-explanation {
  font-family:var(--sans); font-size:0.82rem; color:var(--ink3);
  line-height:1.7; padding:0.7rem 1rem;
  border-left:2px solid var(--border2); background:var(--bg2);
  margin-bottom:0.6rem;
}
.conf-row {
  display:flex; align-items:center; gap:1.2rem; padding:0.5rem 0.8rem;
  background:var(--bg2); border-top:1px solid var(--border); margin-top:0.4rem;
}
.conf-label { font-family:var(--mono); font-size:0.5rem; color:var(--ink4); letter-spacing:0.2em; }
.conf-val   { font-family:var(--mono); font-size:0.82rem; font-weight:600; }
.conf-lbl   { font-family:var(--mono); font-size:0.55rem; letter-spacing:0.1em; }

/* ── FIX 3: Hypothesis progress bars ── */
.hyp-bar-row {
  display:grid;
  grid-template-columns: 140px 180px 48px 1fr;
  align-items:center;
  gap:0.6rem;
  padding:0.45rem 0.8rem;
  border-bottom:1px solid var(--border);
  font-family:var(--mono);
}
.hyp-bar-row:last-child { border-bottom:none; }
.hyp-bar-key   { font-size:0.65rem; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap !important; }
.hyp-bar-track { position:relative; height:6px; background:var(--bg3); border-radius:2px; }
.hyp-bar-fill  { position:absolute; left:0; top:0; height:100%; border-radius:2px; }
.hyp-bar-pct   { font-size:0.62rem; text-align:right; }
.hyp-bar-lbl   { font-size:0.58rem; color:var(--ink4); overflow:hidden; text-overflow:ellipsis;
                 white-space:nowrap !important; max-width:100%; }

/* ── Ranking table ── */
.rank-table { width:100%; border-collapse:collapse; margin-bottom:0.6rem; }
.rank-table td {
  padding:0.4rem 0.6rem; border-bottom:1px solid var(--border);
  font-family:var(--mono); font-size:0.68rem; vertical-align:middle;
  overflow-wrap:break-word; word-break:normal; max-width:200px;
}
.rank-table tr:last-child td { border-bottom:none; }
.rank-num  { color:var(--ink4); width:1.5rem; }
.rank-key  { font-weight:600; }
.rank-title { color:var(--ink3); padding-left:0.4rem; }
.rank-conf { text-align:right; font-size:0.6rem; color:var(--ink3); }

/* ── Metod strip ── */
.metod-strip {
  font-family:var(--mono); font-size:0.6rem; color:var(--ink4);
  background:var(--bg2); border-top:1px solid var(--border);
  padding:0.55rem 1rem; line-height:1.7; letter-spacing:0.02em;
}

/* ── FIX 6: Reality Check — CLAIM/STATUS/SOURCE ── */
.rc-table { width:100%; border-collapse:collapse; }
.rc-table td {
  padding:0.45rem 0.7rem; border-bottom:1px solid var(--border);
  font-family:var(--sans); font-size:0.78rem; vertical-align:top;
  overflow-wrap:break-word; word-break:normal;
}
.rc-table tr:last-child td { border-bottom:none; }
.rc-col-label { font-family:var(--mono); font-size:0.5rem; color:var(--ink4);
                letter-spacing:0.2em; white-space:nowrap; padding-right:0.8rem; }
.rc-col-claim  { color:var(--ink2); line-height:1.55; }
.rc-col-status { white-space:nowrap; }
.rc-col-source { color:var(--ink3); }
.rc-col-source a { color:#5a9fe0; text-decoration:underline; }
.rc-status-v { color:var(--grn);  font-family:var(--mono); font-size:0.62rem; font-weight:600; }
.rc-status-d { color:var(--amb);  font-family:var(--mono); font-size:0.62rem; font-weight:600; }
.rc-status-u { color:var(--red);  font-family:var(--mono); font-size:0.62rem; font-weight:600; }
.rc-status-n { color:var(--ink3); font-family:var(--mono); font-size:0.62rem; }

/* ── FIX 7: Hypothesis cards — tydliga rubriker ── */
.hyp-card-header {
  padding:0.75rem 1rem; border-bottom:1px solid var(--border);
  background:var(--bg2);
}
.hyp-card-key {
  font-family:var(--mono); font-size:0.7rem; font-weight:700;
  letter-spacing:0.08em; margin-bottom:0.2rem;
}
.hyp-card-title {
  font-family:var(--serif); font-size:0.95rem; font-weight:600;
  color:var(--ink2); line-height:1.4;
  overflow-wrap:break-word; word-break:normal;
}
.hyp-card-score-row {
  display:flex; align-items:center; gap:0.8rem; margin-top:0.4rem;
}
.hyp-card-score { font-family:var(--mono); font-size:0.68rem; font-weight:600; }
.hyp-card-styrka { font-family:var(--mono); font-size:0.55rem; letter-spacing:0.12em; color:var(--ink4); }

.hyp-section       { margin-bottom:0.75rem; }
.hyp-section-label {
  font-family:var(--mono); font-size:0.52rem; letter-spacing:0.2em;
  text-transform:uppercase; color:var(--ink4); margin-bottom:0.3rem;
}
.hyp-section-empty { font-family:var(--mono); font-size:0.65rem; color:var(--ink4);
                     font-style:italic; padding:0.25rem 0.5rem; }
.hyp-tes {
  font-family:var(--sans); font-size:0.82rem; color:#7ab89a; line-height:1.65;
  padding:0.45rem 0.7rem; border-left:2px solid var(--grn-dim); background:var(--grn-bg);
}
.hyp-ev-list { list-style:none; padding:0; margin:0; }
.hyp-ev-list li {
  font-family:var(--sans); font-size:0.78rem; color:var(--ink3); line-height:1.55;
  padding:0.3rem 0.7rem; border-left:2px solid var(--grn-dim); background:var(--grn-bg);
  margin-bottom:0.2rem; display:flex; gap:0.5rem; align-items:baseline;
  overflow-wrap:break-word; word-break:normal;
}
.hyp-ev-list li::before { content:"•"; color:var(--grn); flex-shrink:0; }
.hyp-ev-list a { color:#5a9fe0; text-decoration:underline; font-size:0.72rem; }
.hyp-mo {
  font-family:var(--sans); font-size:0.78rem; color:#9a7060; line-height:1.55;
  padding:0.3rem 0.7rem; border-left:2px solid var(--red-dim); background:var(--red-bg);
  margin-bottom:0.2rem; overflow-wrap:break-word;
}
.hyp-fl {
  font-family:var(--sans); font-size:0.78rem; color:#7070a0; line-height:1.55;
  padding:0.35rem 0.7rem; border-left:2px solid var(--blu-dim); background:var(--blu-bg);
  overflow-wrap:break-word;
}

/* ── Nyckelord ── */
.nyckelord-strip {
  display:flex; gap:0.5rem; flex-wrap:wrap; padding:0.6rem 1rem;
  background:var(--bg2); border-top:1px solid var(--border);
}
.nyckelord-label { font-family:var(--mono); font-size:0.5rem; color:var(--ink4);
                   letter-spacing:0.2em; align-self:center; white-space:nowrap; }
.nyckelord-tag {
  font-family:var(--mono); font-size:0.62rem; color:var(--blu);
  border:1px solid var(--blu-dim); background:var(--blu-bg);
  padding:0.15rem 0.55rem; text-decoration:none; letter-spacing:0.05em;
}
.nyckelord-tag:hover { background:#101830; color:#8ac0f0; }

/* ── Verdict ── */
.verdict {
  border:1px solid; padding:1rem; margin:0.6rem 0;
  display:flex; align-items:center; gap:1rem;
}
.verdict-grn { border-color:var(--grn-dim); background:var(--grn-bg); }
.verdict-amb { border-color:var(--amb-dim); background:var(--amb-bg); }
.verdict-red { border-color:var(--red-dim); background:var(--red-bg); }
.verdict-icon  { font-family:var(--mono); font-size:1.4rem; }
.verdict-label { font-family:var(--mono); font-size:0.55rem; letter-spacing:0.25em;
                 color:var(--ink4); margin-bottom:0.25rem; }
.verdict-text  { font-family:var(--serif); font-size:1rem; font-weight:600; }
.verdict-grn .verdict-text { color:#80c89a; }
.verdict-amb .verdict-text { color:#c09050; }
.verdict-red .verdict-text { color:#c07060; }

/* ── Analysis text ── */
.analysis-text {
  font-family:var(--sans); font-size:0.8rem; line-height:1.8; color:var(--ink3);
  white-space:pre-wrap; overflow-wrap:break-word; word-break:normal;
}
.analysis-text a { color:#5a9fe0; text-decoration:underline; }

/* ── Layer cards ── */
.layer-card { border:1px solid var(--border); padding:1rem; margin-bottom:0.5rem; background:var(--bg1); }
.layer-lbl  { font-family:var(--mono); font-size:0.55rem; color:var(--ink4); letter-spacing:0.2em; margin-bottom:0.25rem; }
.layer-ttl  { font-family:var(--serif); font-size:0.9rem; color:var(--ink2); font-weight:600;
              margin-bottom:0.7rem; padding-bottom:0.4rem; border-bottom:1px solid var(--border); }

/* ── Degraded ── */
.degraded {
  border:1px solid var(--red-dim); border-left:3px solid var(--red);
  background:var(--red-bg); padding:0.8rem 1rem; margin:0.8rem 0;
  font-family:var(--mono); font-size:0.68rem; color:var(--red); line-height:1.7;
}

/* ── Empty state ── */
.empty-state { margin-top:2.5rem; padding:2rem; border:1px solid var(--border); background:var(--bg1); }
.empty-kw    { font-family:var(--mono); font-size:0.55rem; letter-spacing:0.3em; color:var(--ink4); margin-bottom:1rem; }
.empty-row   { display:flex; gap:1rem; padding:0.45rem 0; border-bottom:1px solid var(--border); font-size:0.82rem; }
.empty-step  { font-family:var(--mono); font-size:0.62rem; color:var(--ink4); min-width:4.5rem; padding-top:0.05rem; }
.empty-desc  { color:var(--ink3); line-height:1.55; overflow-wrap:break-word; }
.empty-footer{ font-family:var(--mono); font-size:0.6rem; color:var(--ink4); margin-top:1rem; letter-spacing:0.05em; }

/* ── Expander ── */
div[data-testid="stExpander"] > div:first-child {
  background:var(--bg2) !important; border:1px solid var(--border) !important;
  border-radius:0 !important; font-family:var(--mono) !important;
  font-size:0.65rem !important; color:var(--ink3) !important;
}
div[data-testid="stExpander"] > div:last-child {
  background:var(--bg1) !important; border:1px solid var(--border) !important;
  border-top:none !important; border-radius:0 !important;
}
.stSpinner > div { border-top-color:var(--grn) !important; }
#MainMenu, footer, header { visibility:hidden; }
div.stMarkdown p { margin:0; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────────────

def _slugify(q, n=45):
    for k,v in {'å':'a','ä':'a','ö':'o','Å':'A','Ä':'A','Ö':'O'}.items(): q=q.lower().replace(k,v)
    return re.sub(r'\s+','_',re.sub(r'[^a-z0-9\s]','',q).strip())[:n] or "analys"

def step_html(steps):
    h='<div class="step-row">'
    for n,s in steps:
        c={"done":"step-done","active":"step-active","warn":"step-warn"}.get(s,"step")
        h+=f'<span class="step {c}">{n}</span>'
    return h+'</div>'

def _pill(label, cls):
    return f'<span class="pill pill-{cls}">{label}</span>'

def _safe(t):
    return (t or "").replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def _render_links(text: str) -> str:
    """[text](url) → klickbar HTML-länk."""
    if not text: return ""
    text = re.sub(
        r'\[([^\]]+)\]\((https?://[^\)]+)\)',
        r'<a href="\2" target="_blank" rel="noopener">\1</a>', text
    )
    return text

def _safe_links(t):
    s = (t or "").replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    s = s.replace('&amp;','&')
    return _render_links(s)

# ── FIX 3: Hypothesis bar renderer ───────────────────────────────────────────
STYRKA_COLORS = {
    "HÖG":       "#3d9970",
    "MEDEL-HÖG": "#6daa50",
    "MEDEL":     "#4a7fc0",
    "LÅG":       "#c0442a",
}

def _hyp_bars_html(ranked: list) -> str:
    """
    FIX 3: Renderar progress-bar-tabell:
    H1 STRUKTURELL  ███████░░░  72%  Systemisk maktasymmetri
    """
    rows = ""
    for h in ranked:
        key    = h.get("key","")
        lbl    = h.get("label","") or h.get("styrka","")
        title  = h.get("title","")
        styrka = (h.get("styrka") or "MEDEL").upper()
        pct    = h.get("conf_pct", h.get("conf_score", 0.5) * 100 if "conf_score" in h else 50)
        pct    = int(pct) if isinstance(pct, (int, float)) else 50
        conf   = h.get("conf_score", h.get("conf", 0.50))
        color  = STYRKA_COLORS.get(styrka, "#4a7fc0")

        key_lbl = f"{key} {lbl}" if lbl else key
        # Trunkera title för bar-raden (full titel visas i expander nedan)
        title_short = (title[:55] + "…") if len(title) > 55 else title

        rows += f"""
<div class="hyp-bar-row">
  <span class="hyp-bar-key" style="color:{color}">{_safe(key_lbl)}</span>
  <div class="hyp-bar-track">
    <div class="hyp-bar-fill" style="width:{pct}%;background:{color}"></div>
  </div>
  <span class="hyp-bar-pct" style="color:{color}">{pct}%</span>
  <span class="hyp-bar-lbl">{_safe(title_short)}</span>
</div>"""
    return f'<div style="background:var(--bg2);padding:0.3rem 0;border:1px solid var(--border);margin-bottom:0.6rem;">{rows}</div>'

# ── FIX 5: Assessment builder — 1 mening + explanation ───────────────────────
def _build_assessment(ranked: list) -> tuple:
    """
    Returns (conclusion_sentence: str, explanation_paragraph: str)
    Ingen duplikering — conclusion = 1 mening, explanation = resonemang.
    """
    if not ranked:
        return "", ""
    w = ranked[0]
    w_key, w_lbl, w_title, w_tes = (
        w.get("key",""), w.get("label",""), w.get("title",""), w.get("tes","")
    )
    # Conclusion — 1 mening
    conclusion = f"Evidensen stödjer starkast {w_key}"
    if w_lbl:   conclusion += f" [{w_lbl}]"
    if w_title: conclusion += f" — {w_title}"
    conclusion += "."

    # Explanation — resonemang, inte duplikat av conclusion
    parts = []
    if w_tes:
        tes_short = w_tes[:160].rsplit('. ', 1)[0] if len(w_tes) > 160 else w_tes
        if not tes_short.endswith('.'): tes_short += "."
        parts.append(tes_short)
    if len(ranked) > 1:
        r = ranked[1]
        r_key, r_lbl = r.get("key",""), r.get("label","")
        runner = f"Sekundär förklaringskraft: {r_key}"
        if r_lbl: runner += f" [{r_lbl}]"
        if r.get("title"): runner += f" — {r['title'][:50]}"
        runner += f" (conf {r.get('conf_score', r.get('conf', 0)):.2f})."
        parts.append(runner)
    if len(ranked) > 2:
        weakest = ranked[-1]
        parts.append(f"Svagast stöd: {weakest.get('key','')} [{weakest.get('label','')}] (conf {weakest.get('conf_score', weakest.get('conf', 0)):.2f}).")

    return conclusion, " ".join(parts)

# ── FIX 6: Reality Check parser → CLAIM/STATUS/SOURCE ────────────────────────
def _parse_rc_structured(txt: str) -> list:
    """
    Returnerar lista av dicts: {claim, status, source}
    Försöker extrahera strukturerat; faller tillbaka på rad-parsing.
    """
    items = []

    # Försök 1: explicit CLAIM/STATUS/SOURCE-block
    for block in re.split(r'\n(?=CLAIM\s*\d*:)', txt, flags=re.IGNORECASE):
        c_m = re.search(r'CLAIM\s*\d*:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        s_m = re.search(r'STATUS\s*:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        src_m = re.search(r'SOURCE\s*:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        if c_m:
            items.append({
                "claim":  c_m.group(1).strip(),
                "status": s_m.group(1).strip() if s_m else "",
                "source": src_m.group(1).strip() if src_m else "",
            })
    if items:
        return items[:6]

    # Försök 2: rad-parsing med status-hints
    for line in txt.split('\n'):
        l  = line.strip()
        lu = l.upper()
        if not l or len(l) < 12: continue
        if any(skip in lu for skip in ["ÖVERGRIPANDE","OVERALL STATUS","STATUS:","SAMMANFATTNING","REALITY CHECK","METOD"]): continue

        st = ""
        if any(x in lu for x in ["BEKRÄFTAD","CONFIRMED","VERIFIED","✓","✔"]): st = "VERIFIED"
        elif any(x in lu for x in ["EJ BEKRÄFTAD","OMTVISTAD","DISPUTED","DELVIS","⚠","OKLART"]): st = "DISPUTED"
        elif any(x in lu for x in ["FALSERAT","FALSKT","✗"]): st = "UNVERIFIED"

        # Extrahera eventuell källa i parentesen eller efter dash
        src = ""
        src_m = re.search(r'\(([^)]{5,60})\)\s*$', l)
        if src_m: src = src_m.group(1).strip()

        clean = re.sub(r'^(CLAIM\s*\d*:?\s*|[-•·]\s*)', '', l).strip()
        if len(clean) > 10:
            items.append({"claim": clean[:200], "status": st, "source": src})
        if len(items) >= 6: break

    return items if items else [{"claim": txt[:300].replace('\n',' '), "status":"", "source":""}]


def _rc_table_html(items: list) -> str:
    """FIX 6: Renderar CLAIM/STATUS/SOURCE som en ren tabell."""
    rows = ""
    for it in items:
        claim  = it.get("claim","")
        status = it.get("status","").upper()
        source = it.get("source","")

        if "VERIFIED" in status or "BEKRÄFTAD" in status:
            st_cls, st_ico = "rc-status-v", "✓ VERIFIED"
        elif "DISPUTED" in status or "OMTVISTAD" in status or "PARTIAL" in status:
            st_cls, st_ico = "rc-status-d", "◑ DISPUTED"
        elif "UNVERIFIED" in status or "FALSERAT" in status:
            st_cls, st_ico = "rc-status-u", "✗ UNVERIFIED"
        else:
            st_cls, st_ico = "rc-status-n", "◎ —"

        src_html = _safe_links(source) if source else '<span style="color:var(--ink4)">—</span>'

        rows += f"""
<tr>
  <td class="rc-col-label">CLAIM</td>
  <td class="rc-col-claim">{_safe_links(claim)}</td>
  <td class="rc-col-status"><span class="{st_cls}">{st_ico}</span></td>
  <td class="rc-col-source">{src_html}</td>
</tr>"""

    return f'<table class="rc-table">{rows}</table>'

# ── Nyckelord ─────────────────────────────────────────────────────────────────
def _nyckelord_html(ranked: list) -> str:
    if not ranked: return ""
    tags = []
    for hyp in ranked[:3]:
        title = hyp.get("title","") or hyp.get("label","") or hyp.get("key","")
        term  = " ".join(title.split()[:3])
        if term:
            url = "https://www.google.com/search?q=" + re.sub(r'\s+', '+', term)
            tags.append(f'<a class="nyckelord-tag" href="{url}" target="_blank">{_safe(term)}</a>')
    if not tags: return ""
    return f'<div class="nyckelord-strip"><span class="nyckelord-label">SÖK VIDARE</span>{"".join(tags)}</div>'

REALITY_PILL = {
    "VERIFIED":     ("grn","✓ VERIFIED"),  "ONGOING":      ("blu","◉ ONGOING"),
    "PARTIAL":      ("amb","◑ PARTIAL"),   "HYPOTHETICAL": ("dim","◌ HYPOTHETICAL"),
    "ANALYTICAL":   ("blu","◎ ANALYTICAL"),"UNVERIFIED":   ("red","✗ UNVERIFIED"),
}
STATUS_PILL = {
    "KLAR":      ("grn","✓ KLAR"),
    "REVIDERAD": ("amb","↻ REVIDERAD"),
    "DEGRADERAD":("red","⚠ DEGRADERAD"),
}

# ── Session state ─────────────────────────────────────────────────────────────
for k,v in [("result",None),("running",False),("awaiting_confirm",False),
            ("layers_generated",False),("deep_generated",False),
            ("active_hyp",None),("show_machine",False)]:
    if k not in st.session_state: st.session_state[k]=v

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:monospace;font-size:0.6rem;letter-spacing:0.25em;color:#444;padding:0.5rem 0;text-transform:uppercase;">Sparade analyser</div>', unsafe_allow_html=True)
    try:
        from history import list_history, load_result, delete_result
        from pdf_export import build_pdf as _pdf_sidebar
        entries = list_history()
        if not entries: st.caption("Inga sparade analyser.")
        for e in entries:
            ts  = e['timestamp'].replace('_',' ')[:16]
            ico = {'VERIFIED':'✅','ANALYTICAL':'🔍','PARTIAL':'⚠️','UNVERIFIED':'❌','HYPOTHETICAL':'💭'}.get(e['reality'],'📄')
            with st.expander(f"{ico} {ts}"):
                st.caption(e['question'][:50]+'…' if len(e['question'])>50 else e['question'])
                c1,c2,c3 = st.columns(3)
                with c1:
                    if st.button("Öppna", key=f"o_{e['filename']}"):
                        ld = load_result(e['filename'])
                        if ld:
                            st.session_state.result = ld
                            st.session_state.layers_generated = bool(ld.get('layers',{}).get('ground'))
                            st.session_state.deep_generated   = bool(ld.get('layers',{}).get('deep1'))
                            st.rerun()
                with c2:
                    ld2 = load_result(e['filename'])
                    if ld2:
                        try:
                            pb = _pdf_sidebar(ld2)
                            sl = _slugify(ld2.get('question','analys'))
                            st.download_button("PDF", pb, file_name=f"sanningsmaskinen_{e['timestamp'][:10]}_{sl}.pdf",
                                               mime="application/pdf", key=f"p_{e['filename']}")
                        except: pass
                with c3:
                    if st.button("🗑", key=f"d_{e['filename']}"): delete_result(e['filename']); st.rerun()
    except: st.caption("history.py saknas")

# ── Topbar ────────────────────────────────────────────────────────────────────
today_str = _date.today().strftime("%Y-%m-%d")
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <span class="topbar-mark">◎ Sanningsmaskinen</span>
    <span class="topbar-title">Epistemiskt analysverktyg</span>
  </div>
  <div class="topbar-right">v8.15 · Claude Opus + GPT-4o · {today_str}</div>
</div>
<div style="font-family:var(--mono);font-size:0.6rem;color:var(--ink4);letter-spacing:0.08em;
padding:0.4rem 0 0.9rem;border-bottom:1px solid var(--border);margin-bottom:1rem;">
  Verktyget analyserar komplexa frågor genom konkurrerande hypoteser, evidensgranskning
  och adversariell kritik — det ger inte ett svar, det falsifierar alternativa förklaringar.
</div>
""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
question = st.text_area("", placeholder="Skriv en fråga — t.ex. Vem sprängde Nord Stream? eller Varför invaderade Ryssland Ukraina 2022?",
                        height=80, label_visibility="collapsed")
c1,c2,_ = st.columns([1.5,1,5])
with c1: run_btn = st.button("Analysera →", disabled=st.session_state.running)
with c2:
    if st.session_state.result:
        if st.button("Rensa"):
            for k in ["result","layers_generated","deep_generated","active_hyp","show_machine"]:
                st.session_state[k] = None if k=="result" else False
            st.rerun()

# ── Pipeline ──────────────────────────────────────────────────────────────────
if run_btn and question.strip():
    st.session_state.update({"running":True,"result":None,"layers_generated":False,
                              "deep_generated":False,"active_hyp":None,"show_machine":False})
    try:
        from engine import (event_reality_check, ask_claude, ask_gpt_critic,
                            analyze_conflicts, run_red_team, auto_rewrite,
                            assess_depth_recommendation)
        steps = [("0 Reality",""),("1 Primär",""),("2 GPT",""),("3 Konflikt",""),("4 Red Team",""),("5 Rewrite?","")]
        ph = st.empty()
        def upd(i,w=-1):
            s=[(n,"done") if j<i else (n,"active") if j==i else (n,"warn") if j==w else (n,"") for j,(n,_) in enumerate(steps)]
            ph.markdown(step_html(s), unsafe_allow_html=True)

        upd(0)
        with st.spinner("Reality check..."): rc = event_reality_check(question.strip())
        upd(1)
        if not rc["proceed"]:
            st.session_state.update({"awaiting_confirm":True,"_rc":rc,"_question":question.strip(),"running":False})
            ph.empty(); st.rerun()

        with st.spinner("Primäranalys..."): ca = ask_claude(question.strip(), rc)
        upd(2)
        with st.spinner("GPT-4 kritiker..."): ga = ask_gpt_critic(question.strip(), ca, rc["status"])
        upd(3)
        with st.spinner("Konfliktanalys..."): cf = analyze_conflicts(ca, ga)
        upd(4)
        with st.spinner("Red Team..."): rr, col = run_red_team(question.strip(), ca, cf)
        ro = bool(rr and "misslyckades" not in rr.lower())
        fa = ""
        if col and ro:
            upd(5)
            with st.spinner("Rewrite..."): fa = auto_rewrite(question.strip(), ca, rr)

        ph.markdown(step_html([(n,"done") for n,_ in steps]), unsafe_allow_html=True)
        res = {"question":question.strip(),"reality_check":rc,"claude_answer":ca,
               "gpt_answer":ga,"conflict_report":cf,"red_team_report":rr,
               "red_team_ok":ro,"collapsed":col,"final_analysis":fa,"layers":{},
               "degraded":not ro,"status":"DEGRADERAD" if not ro else ("REVIDERAD" if fa else "KLAR")}
        res["depth_recommendation"] = assess_depth_recommendation(res)
        st.session_state.result = res
        try:
            from history import save_result; save_result(res)
        except: pass
    except ImportError as e: st.error(f"engine.py saknas: {e}")
    except Exception as e:   st.error(f"Fel: {e}")
    finally: st.session_state.running = False; st.rerun()

# ── Confirm hypothetical ──────────────────────────────────────────────────────
if st.session_state.awaiting_confirm:
    rc = st.session_state.get("_rc",{}); q = st.session_state.get("_question","")
    st.markdown(f'<div class="degraded">HÄNDELSEN KAN INTE VERIFIERAS<br>{_safe(rc.get("text","")[:300])}<br><br>Fortsätta som hypotetiskt scenario?</div>', unsafe_allow_html=True)
    c1,c2 = st.columns([1,4])
    with c1:
        if st.button("Ja, fortsätt"):
            rc["proceed"]=True; st.session_state.awaiting_confirm=False; st.session_state.running=True
            try:
                from engine import (ask_claude,ask_gpt_critic,analyze_conflicts,run_red_team,auto_rewrite,assess_depth_recommendation)
                ca=ask_claude(q,rc); ga=ask_gpt_critic(q,ca,rc["status"]); cf=analyze_conflicts(ca,ga)
                rr,col=run_red_team(q,ca,cf); ro=bool(rr and "misslyckades" not in rr.lower())
                fa=auto_rewrite(q,ca,rr) if col and ro else ""
                res={"question":q,"reality_check":rc,"claude_answer":ca,"gpt_answer":ga,
                     "conflict_report":cf,"red_team_report":rr,"red_team_ok":ro,"collapsed":col,
                     "final_analysis":fa,"layers":{},"degraded":not ro,
                     "status":"DEGRADERAD" if not ro else ("REVIDERAD" if fa else "KLAR")}
                res["depth_recommendation"]=assess_depth_recommendation(res)
                st.session_state.result=res
            except Exception as e: st.error(f"Fel: {e}")
            finally: st.session_state.running=False; st.rerun()
    with c2:
        if st.button("Avbryt"): st.session_state.awaiting_confirm=False; st.rerun()

# ── Result view ───────────────────────────────────────────────────────────────
if st.session_state.result:
    r   = st.session_state.result
    rc  = r["reality_check"]
    lyr = r.get("layers",{})

    try:
        from normalizer import normalize_claude_answer, compute_hypothesis_scores
        norm = normalize_claude_answer(r.get("claude_answer",""))
        norm["hypotheses"] = compute_hypothesis_scores(norm["hypotheses"])
        hyps = norm.get("hypotheses",[])
    except: hyps=[]

    rank_order = {"HÖG":0,"MEDEL-HÖG":1,"MEDEL":2,"LÅG":3}
    ranked = sorted(hyps, key=lambda h: (
        rank_order.get(h.get("styrka","MEDEL"), 99),
        -h.get("conf_score", h.get("conf", 0))
    ))

    rc_status  = (rc.get("status","") or "").upper()
    res_status = (r.get("status","") or "").upper()

    if r["degraded"]:
        st.markdown('<div class="degraded">⚠ DEGRADERAD LEVERANS — Red Team körde inte korrekt.</div>', unsafe_allow_html=True)

    # ── ZON 1: FRÅGA ─────────────────────────────────────────────────────────
    rc_pill_cls, rc_pill_lbl = REALITY_PILL.get(rc_status, ("dim", rc_status))
    st_pill_cls, st_pill_lbl = STATUS_PILL.get(res_status, ("dim", res_status))
    st.markdown(f"""
<div class="zone">
  <div class="zone-header zone-header-accent zone-blu">
    <span>FRÅGA</span><span>{today_str}</span>
  </div>
  <div class="q-block" style="padding:1.2rem 1rem;background:var(--bg1)">
    <div style="font-family:var(--serif);font-size:1.15rem;color:var(--ink);line-height:1.5;margin-bottom:0.6rem;">{_safe(r['question'])}</div>
    <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
      {_pill(rc_pill_lbl, rc_pill_cls)}{_pill(st_pill_lbl, st_pill_cls)}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── ZON 2: ASSESSMENT (FIX 5) ────────────────────────────────────────────
    if ranked:
        conclusion, explanation = _build_assessment(ranked)

        # Confidence aggregat
        confs = [h.get("conf_score", h.get("conf", 0.5)) for h in ranked]
        avg_conf = sum(confs) / len(confs) if confs else 0.5
        if avg_conf >= 0.70:   conf_lbl, conf_col = "HÖG",       "var(--grn)"
        elif avg_conf >= 0.50: conf_lbl, conf_col = "MEDEL–HÖG", "#6daa50"
        elif avg_conf >= 0.35: conf_lbl, conf_col = "MEDEL",      "var(--blu)"
        else:                  conf_lbl, conf_col = "LÅG",        "var(--red)"

        # FIX 3: progress bars
        bars_html = _hyp_bars_html(ranked)

        # Ranking-tabell (kompakt, ingen duplikering av bars)
        rank_rows = ""
        for i,h in enumerate(ranked):
            st_v = h.get("styrka","MEDEL")
            col  = STYRKA_COLORS.get(st_v.upper(), "#4a7fc0")
            k=h.get("key",""); lb=h.get("label",""); t=h.get("title","")
            conf = h.get("conf_score", h.get("conf", 0.50))
            rank_rows += f"""
<tr>
  <td class="rank-num">{i+1}.</td>
  <td class="rank-key" style="color:{col}">{k}{' ['+lb+']' if lb else ''}</td>
  <td class="rank-title">{_safe(t[:45])}</td>
  <td class="rank-conf">{conf:.2f}</td>
</tr>"""

        falsif = ranked[0].get("falsifiering","") if ranked else ""
        falsif_html = ""
        if falsif:
            falsif_html = f"""
<div style="border-top:1px solid var(--border);padding:0.7rem 1rem;background:var(--bg2);display:flex;gap:0.8rem;align-items:baseline;">
  <span style="font-family:var(--mono);font-size:0.52rem;letter-spacing:0.2em;color:var(--ink4);white-space:nowrap;">VAD SKULLE FALSIFIERA?</span>
  <span style="font-family:var(--sans);font-size:0.8rem;color:#7070a0;line-height:1.6;">{_safe(falsif)}</span>
</div>"""

        st.markdown(f"""
<div class="zone">
  <div class="zone-header zone-header-accent zone-grn">
    <span>ASSESSMENT</span>
    <span style="font-size:0.5rem;letter-spacing:0.1em">ANALYTISK BEDÖMNING — INTE ETT SVAR</span>
  </div>
  <div class="zone-body">
    <div class="assessment-conclusion">
      <div class="assessment-label">SLUTSATS</div>
      {_safe(conclusion)}
    </div>
    <div class="assessment-explanation">{_safe(explanation)}</div>
    <div class="conf-row">
      <span class="conf-label">AGGREGERAD KONFIDENS</span>
      <span class="conf-val" style="color:{conf_col}">{avg_conf:.2f}</span>
      <span class="conf-lbl" style="color:{conf_col}">{conf_lbl}</span>
    </div>
    {bars_html}
    <table class="rank-table" style="background:var(--bg2)">{rank_rows}</table>
  </div>
  {falsif_html}
  {_nyckelord_html(ranked)}
  <div class="metod-strip">
    METOD — Konkurrerande hypoteser testas mot evidens, GPT-kritik och red-team-granskning.
    Confidence = evidensstyrka × antal bevis × källkvalitet, normaliserat 0–1.
    Analysen falsifierar alternativa förklaringar — den besvarar inte frågan.
  </div>
</div>
""", unsafe_allow_html=True)

    # ── ZON 3: REALITY CHECK (FIX 6) ─────────────────────────────────────────
    rc_text   = rc.get("text","") or rc.get("result","")
    rc_items  = _parse_rc_structured(rc_text)
    rc_accent = {"VERIFIED":"grn","ONGOING":"blu","PARTIAL":"amb",
                 "UNVERIFIED":"red","ANALYTICAL":"blu","HYPOTHETICAL":"dim"}.get(rc_status,"dim")
    st.markdown(f"""
<div class="zone">
  <div class="zone-header zone-header-accent zone-{rc_accent}">
    <span>REALITY CHECK — STEG 0</span>
    <span>{_pill(REALITY_PILL.get(rc_status,("dim",rc_status))[1], REALITY_PILL.get(rc_status,("dim",rc_status))[0])}</span>
  </div>
  <div class="zone-body">{_rc_table_html(rc_items)}</div>
</div>
""", unsafe_allow_html=True)

    # ── ZON 4: HYPOTESER (FIX 7) ─────────────────────────────────────────────
    if hyps:
        st.markdown("""
<div style="font-family:var(--mono);font-size:0.55rem;letter-spacing:0.3em;color:var(--ink4);
text-transform:uppercase;padding:1rem 0 0.4rem;border-top:1px solid var(--border);margin-top:24px;">
HYPOTESER — KLICKA FÖR DETALJER</div>
""", unsafe_allow_html=True)

        for hyp in hyps:
            key    = hyp.get("key","")
            lbl    = hyp.get("label","")
            title  = hyp.get("title","")
            styrka = (hyp.get("styrka") or "MEDEL").upper()
            tes    = hyp.get("tes","")
            bevis  = hyp.get("bevis",[])
            motarg = hyp.get("motarg",[])
            falsif = hyp.get("falsifiering","")
            conf   = hyp.get("conf_score", hyp.get("conf", 0.50))
            pct    = hyp.get("conf_pct", int(conf * 100))
            color  = STYRKA_COLORS.get(styrka, "#4a7fc0")

            # FIX 7: full titel i expander-rubrik, aldrig trunkerad
            exp_label = f"{key}  {('['+lbl+']') if lbl else ''}  ·  {conf:.2f} ({pct}%)  —  {title}"

            ev_html = ""
            if bevis:
                items_html = "".join(f'<li>{_safe_links(b)}</li>' for b in bevis[:5])
                ev_html = f'<ul class="hyp-ev-list">{items_html}</ul>'
            else:
                ev_html = '<div class="hyp-section-empty">Ingen evidens identifierad.</div>'

            mo_html = ""
            if motarg:
                mo_html = "".join(f'<div class="hyp-mo">{_safe_links(m)}</div>' for m in motarg[:3])
            else:
                mo_html = '<div class="hyp-section-empty">Inga motargument identifierade.</div>'

            fl_html = (f'<div class="hyp-fl">{_safe_links(falsif)}</div>'
                       if falsif else '<div class="hyp-section-empty">Inget falsifieringstest identifierat.</div>')

            with st.expander(exp_label, expanded=False):
                # FIX 7: tydlig header med score + explanation
                st.markdown(f"""
<div class="hyp-card-header">
  <div class="hyp-card-key" style="color:{color}">{key} {lbl}</div>
  <div class="hyp-card-title">{_safe(title)}</div>
  <div class="hyp-card-score-row">
    <div class="hyp-bar-track" style="width:160px">
      <div class="hyp-bar-fill" style="width:{pct}%;background:{color}"></div>
    </div>
    <span class="hyp-card-score" style="color:{color}">{conf:.2f} ({pct}%)</span>
    <span class="hyp-card-styrka">{styrka}</span>
    <span style="font-family:var(--mono);font-size:0.52rem;color:var(--ink4)">{len(bevis)} bevis · {len(motarg)} motarg</span>
  </div>
</div>

<div style="padding:0.85rem 0.9rem;background:var(--bg1)">
  <div class="hyp-section">
    <div class="hyp-section-label">TES</div>
    {'<div class="hyp-tes">' + _safe_links(tes) + '</div>' if tes else '<div class="hyp-section-empty">Ingen tes identifierad.</div>'}
  </div>
  <div class="hyp-section">
    <div class="hyp-section-label">EVIDENS</div>
    {ev_html}
  </div>
  <div class="hyp-section">
    <div class="hyp-section-label">MOTARGUMENT</div>
    {mo_html}
  </div>
  <div class="hyp-section">
    <div class="hyp-section-label">FALSIFIERINGSTEST</div>
    {fl_html}
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        with st.expander("📄 Primäranalys", expanded=True):
            st.markdown(f'<div class="analysis-text">{_safe_links(r.get("claude_answer",""))}</div>', unsafe_allow_html=True)

    # ── RED TEAM VERDICT ──────────────────────────────────────────────────────
    rr = r.get("red_team_report","")
    if rr:
        up = rr.upper()
        if "KOLLAPSAR" in up:    vc,vi,vt = "red","✗","KOLLAPSAR — Analysen håller inte"
        elif "MODIFIERAS" in up: vc,vi,vt = "amb","◑","MODIFIERAS — Analysen revideras"
        elif "HÅLLER" in up:     vc,vi,vt = "grn","✓","HÅLLER — Analysen bekräftad"
        else: vc=vi=vt=None
        if vc:
            st.markdown(f"""
<div class="verdict verdict-{vc}" style="margin:0.8rem 0">
  <span class="verdict-icon" style="color:var(--{vc})">{vi}</span>
  <div><div class="verdict-label">RED TEAM VERDICT — STEG 4</div><div class="verdict-text">{vt}</div></div>
</div>""", unsafe_allow_html=True)

    # ── CONFLICT ANALYSIS ─────────────────────────────────────────────────────
    cf = r.get("conflict_report","")
    if cf:
        lines  = [l.strip() for l in cf.split('\n') if l.strip()]
        cl_html = "".join(f'<div style="font-size:0.78rem;color:var(--ink3);padding:0.2rem 0;overflow-wrap:break-word;">{_safe_links(l)}</div>' for l in lines[:6])
        st.markdown(f"""
<div class="zone" style="margin-top:0.6rem">
  <div class="zone-header zone-header-accent zone-amb"><span>KONFLIKTANALYS — CLAUDE vs GPT</span></div>
  <div class="zone-body">{cl_html}</div>
</div>""", unsafe_allow_html=True)

    # ── LAYERS ────────────────────────────────────────────────────────────────
    st.markdown('<div style="border-top:1px solid var(--border);margin:1rem 0 0.6rem;"></div>', unsafe_allow_html=True)
    if not st.session_state.layers_generated:
        cl1,cl2 = st.columns([1,3])
        with cl1:
            if st.button("📊 Layer 1–5"):
                with st.spinner("Bygger lagerstruktur..."):
                    from engine import deliver_ground_layers
                    g = deliver_ground_layers(r["question"],r["claude_answer"],r["gpt_answer"],r["red_team_report"],r["final_analysis"],rc)
                    r["layers"]["ground"]=g; st.session_state.result=r; st.session_state.layers_generated=True; st.rerun()
        with cl2: st.caption("Destillerar analysen till journalistiskt format. ~$0.25")
    else:
        ground = lyr.get("ground","")
        secs   = re.split(r'(LAYER\s+\d[^:\n]*)', ground)
        titles = {"LAYER 1":"Dörren","LAYER 2":"Kartan","LAYER 3":"Tre hypoteser","LAYER 4":"Aktörerna","LAYER 5":"Din makt"}
        if len(secs)>1:
            i=1
            while i<len(secs):
                h=secs[i].strip(); c=secs[i+1].strip() if i+1<len(secs) else ""
                k=h[:7].strip()
                st.markdown(f'<div class="layer-card"><div class="layer-lbl">Layer {k[-1]}</div><div class="layer-ttl">{titles.get(k,h)}</div><div class="analysis-text">{_safe_links(c)}</div></div>', unsafe_allow_html=True)
                i+=2
        else:
            st.markdown(f'<div class="layer-card"><div class="analysis-text">{_safe_links(ground)}</div></div>', unsafe_allow_html=True)

    if not st.session_state.deep_generated:
        cl1,cl2 = st.columns([1,3])
        with cl1:
            if st.button("🔬 Fördjupningar"):
                with st.spinner("Genererar fördjupningar..."):
                    from engine import deliver_deep_dives
                    dp = deliver_deep_dives(r["question"],r["claude_answer"],r["gpt_answer"],r["red_team_report"],r["final_analysis"],rc)
                    r["layers"].update(dp); st.session_state.result=r; st.session_state.deep_generated=True; st.rerun()
        with cl2: st.caption("Historik + detaljerade linser + analytiker-output. ~$0.15")
    else:
        for k,lbl in [("deep1","🕰 Systemet bakåt i tiden"),("deep2","🔭 Tre linser i detalj"),("deep3","📋 Analytiker-output")]:
            with st.expander(lbl):
                st.markdown(f'<div class="analysis-text">{_safe_links(lyr.get(k,""))}</div>', unsafe_allow_html=True)

    # ── MASKINRUMMET ──────────────────────────────────────────────────────────
    st.markdown('<div style="border-top:1px solid var(--border);margin:1rem 0 0.4rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:monospace;font-size:0.55rem;letter-spacing:0.3em;color:#333;text-transform:uppercase;margin-bottom:0.5rem;">Maskinrummet — intern analyskedja</div>', unsafe_allow_html=True)

    with st.expander("🔎 Reality Check — fullständig"):
        st.markdown(f'<div class="analysis-text">{_safe_links(rc.get("text",""))}</div>', unsafe_allow_html=True)
    with st.expander("⚔️ GPT-4 Kritiker"):
        st.markdown(f'<div class="analysis-text">{_safe_links(r.get("gpt_answer",""))}</div>', unsafe_allow_html=True)
    with st.expander("🎯 Red Team — fullständig rapport"):
        st.markdown(f'<div class="analysis-text">{_safe_links(r.get("red_team_report",""))}</div>', unsafe_allow_html=True)

    if r.get("final_analysis"):
        with st.expander("✏️ Reviderad analys"):
            try:
                from normalizer import normalize_references
                revised_text = normalize_references(r["final_analysis"])
            except Exception:
                revised_text = r["final_analysis"]
            if revised_text and revised_text.strip():
                st.markdown(f'<div class="analysis-text">{_safe_links(revised_text)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-family:var(--mono);font-size:0.7rem;color:var(--ink4);padding:0.6rem;text-align:center;">REVIDERAD ANALYS — ingen text genererades.</div>', unsafe_allow_html=True)

    # ── EXPORT ────────────────────────────────────────────────────────────────
    st.markdown('<div style="border-top:1px solid var(--border);margin:1.5rem 0 0.8rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:monospace;font-size:0.55rem;letter-spacing:0.3em;color:#333;text-transform:uppercase;margin-bottom:0.5rem;">Export</div>', unsafe_allow_html=True)

    _slug = _slugify(r['question'])

    def _full(res):
        rc_=res["reality_check"]; ly=res.get("layers",{})
        p=["="*70+"\nSANNINGSMASKINEN v8.15\n",f"Fråga: {res['question']}\nDatum: {today_str}\n",
           f"Status: {res['status']} | Reality: {rc_['status']}\n","="*70+"\n\n",
           "REALITY CHECK\n"+"-"*40+"\n",rc_.get("text","")+"\n\n",
           "PRIMÄRANALYS\n"+"-"*40+"\n",res.get("claude_answer","")+"\n\n"]
        if ly.get("ground"): p+=["LAYER 1-5\n"+"-"*40+"\n",ly["ground"]+"\n\n"]
        for k,t in [("deep1","FÖRDJUPNING 1"),("deep2","FÖRDJUPNING 2"),("deep3","FÖRDJUPNING 3")]:
            if ly.get(k): p+=[f"{t}\n"+"-"*40+"\n",ly[k]+"\n\n"]
        p+=["GPT-4\n"+"-"*40+"\n",res.get("gpt_answer","")+"\n\n",
            "RED TEAM\n"+"-"*40+"\n",res.get("red_team_report","")+"\n\n"]
        if res.get("final_analysis"): p+=["REVIDERAD\n"+"-"*40+"\n",res["final_analysis"]+"\n\n"]
        p+=["\n"+"="*70+"\nSanningen favoriserar ingen sida."]
        return "".join(p)

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.download_button("📄 Hela analysen", _full(r).encode(), f"sanningsmaskinen_{today_str}_{_slug}_full.txt","text/plain",use_container_width=True)
    with c2: st.download_button("📄 Primäranalys",  r.get("claude_answer","").encode(), f"sanningsmaskinen_{today_str}_{_slug}_analys.txt","text/plain",use_container_width=True)
    with c3:
        try:
            from pdf_export import build_pdf as _bp
            st.download_button("📄 PDF", _bp(r), f"sanningsmaskinen_{today_str}_{_slug}.pdf","application/pdf",use_container_width=True)
        except: pass
    with c4:
        st.download_button("📄 Reality Check", rc.get("text","").encode(), f"sanningsmaskinen_{today_str}_{_slug}_reality.txt","text/plain",use_container_width=True)

    st.markdown(f"""
<div style="margin-top:2rem;padding-top:0.6rem;border-top:1px solid var(--border);
display:flex;justify-content:space-between;font-family:monospace;font-size:0.58rem;color:#2a2a32;">
  <span>Sanningsmaskinen v8.15 · {today_str}</span>
  <span>{rc_status} · {res_status}</span>
  <span>Sanningen favoriserar ingen sida.</span>
</div>""", unsafe_allow_html=True)

# ── Empty state ───────────────────────────────────────────────────────────────
elif not st.session_state.running and not st.session_state.awaiting_confirm:
    steps_info = [
        ("Steg 0","Reality Check — VERIFIED / ONGOING / HYPOTHETICAL / ANALYTICAL"),
        ("Steg 1","Primäranalys — Claude Opus med tre hypoteser, bevis + falsifiering"),
        ("Steg 2","GPT-4 destruktiv kritik — opponerar, sammanfattar inte"),
        ("Steg 3","Konfliktanalys — epistemiska meningsskiljaktigheter"),
        ("Steg 4","Red Team — VERDICT: HÅLLER / MODIFIERAS / KOLLAPSAR"),
        ("Steg 5","Auto-rewrite om Red Team bedömer KOLLAPSAR eller MODIFIERAS"),
        ("Steg 6","Layer 1–5 och fördjupningar — on-demand"),
    ]
    rows = "".join(f'<div class="empty-row"><span class="empty-step">{s}</span><span class="empty-desc">{d}</span></div>' for s,d in steps_info)
    st.markdown(f"""
<div class="empty-state">
  <div class="empty-kw">HUR VERKTYGET FUNGERAR</div>
  {rows}
  <div class="empty-footer">
    Exempelfrågor · Vem sprängde Nord Stream? · Varför invaderade Ryssland Ukraina 2022? · Varför invaderade USA Irak 2003?
  </div>
</div>""", unsafe_allow_html=True)