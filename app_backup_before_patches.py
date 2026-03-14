# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN v8.17b — STREAMLIT UI
Designmål:
- Behåll den snygga mörka v8.17-designen
- Förbättra kontrast och läsbarhet
- Visa mer sammanhängande text i korten
- Extrahera och visa klickbara länkar tydligare i varje del
- Röra engine/normalizer så lite som möjligt
"""

import re
from datetime import date as _date
from urllib.parse import quote_plus

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Sanningsmaskinen",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,300;0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@300;400;500;600&family=Libre+Franklin:wght@300;400;600;700&display=swap');

:root{
  --bg:#0a0b0d; --bg1:#0f1115; --bg2:#141821; --bg3:#1b2230;
  --border:#242c3a; --border2:#303a4c;
  --ink:#f2efe8; --ink2:#d7d0c4; --ink3:#b3ad9f; --ink4:#7f8898;
  --grn:#57c78a; --grn-bg:#0a1711; --grn-dim:#1e4a34;
  --amb:#e2b04c; --amb-bg:#171205; --amb-dim:#5e4518;
  --red:#db6b57; --red-bg:#180b0a; --red-dim:#5b2620;
  --blu:#6eb6ff; --blu-bg:#0a1220; --blu-dim:#23486d;
  --mono:'JetBrains Mono',monospace; --serif:'Spectral',serif; --sans:'Libre Franklin',sans-serif;
}

html, body, [class*="css"]{
  background:var(--bg);
  color:var(--ink);
  font-family:var(--sans);
  -webkit-font-smoothing:antialiased;
}
*,
*::before,
*::after{box-sizing:border-box}
.main .block-container{
  max-width:1060px;
  padding:0 1.5rem 5.3rem;
  margin:0 auto;
}
div[data-testid="stAppViewContainer"]{background:var(--bg)}
div[data-testid="stSidebar"]{background:var(--bg1)}
#MainMenu, footer, header {visibility:hidden;}
a{color:#6ca9ef;text-decoration:underline;}
a:hover{color:#9cc7ff}
*{max-width:100%;word-break:normal !important;overflow-wrap:break-word !important;}
pre, code, .analysis-text{white-space:pre-wrap !important;word-break:normal !important;overflow-wrap:anywhere !important;}
div.stMarkdown p{margin:0}
.stCaption{color:var(--ink4)!important}

.topbar{display:flex;align-items:center;justify-content:space-between;padding:1rem 0 .75rem;border-bottom:1px solid var(--border);margin-bottom:1.15rem;}
.topbar-left{display:flex;align-items:baseline;gap:1rem}
.topbar-mark{font-family:var(--mono);font-size:.58rem;font-weight:600;letter-spacing:.35em;color:var(--ink3);text-transform:uppercase;}
.topbar-title{font-family:var(--serif);font-size:1.03rem;font-weight:600;color:var(--ink);}
.topbar-right{font-family:var(--mono);font-size:.58rem;color:var(--ink3);letter-spacing:.08em;}
.topbar-sub{font-family:var(--mono);font-size:.6rem;color:var(--ink3);letter-spacing:.07em;padding:.4rem 0 .9rem;border-bottom:1px solid var(--border);margin-bottom:1rem;line-height:1.7;}

.stTextArea textarea{background:var(--bg2)!important;border:1px solid var(--border2)!important;border-radius:2px!important;color:var(--ink)!important;font-family:var(--serif)!important;font-size:1rem!important;line-height:1.6!important;padding:.78rem 1rem!important;}
.stTextArea textarea:focus{border-color:var(--blu)!important}
.stTextArea textarea::placeholder{color:var(--ink4)!important}
.stButton>button{background:var(--ink)!important;color:var(--bg)!important;border:none!important;border-radius:2px!important;font-family:var(--mono)!important;font-size:.63rem!important;font-weight:600!important;letter-spacing:.15em!important;padding:.5rem 1.2rem!important;text-transform:uppercase!important;transition:opacity .15s!important;}
.stButton>button:hover{opacity:.84!important}
.stButton>button:disabled{opacity:.3!important}

.step-row{display:flex;gap:.3rem;flex-wrap:wrap;margin:.8rem 0 1.15rem}
.step{
  font-family:var(--mono);font-size:.58rem;padding:.18rem .55rem;border:1px solid var(--border);
  color:var(--ink4);letter-spacing:.04em;background:transparent;transition:all .25s ease;
}
.step-done{border-color:var(--grn-dim);color:var(--grn);background:var(--grn-bg)}
.step-active{
  border-color:var(--blu);color:#bfe0ff;background:var(--blu-bg);
  box-shadow:0 0 0 1px rgba(110,182,255,.15) inset, 0 0 14px rgba(110,182,255,.08);
  animation:stepPulse 1.8s ease-in-out infinite;
}
.step-warn{border-color:var(--red-dim);color:var(--red);background:var(--red-bg)}
@keyframes stepPulse{
  0%{opacity:1; box-shadow:0 0 0 1px rgba(110,182,255,.12) inset, 0 0 8px rgba(110,182,255,.04);}
  50%{opacity:.78; box-shadow:0 0 0 1px rgba(110,182,255,.28) inset, 0 0 18px rgba(110,182,255,.12);}
  100%{opacity:1; box-shadow:0 0 0 1px rgba(110,182,255,.12) inset, 0 0 8px rgba(110,182,255,.04);}
}

.zone{border:1px solid var(--border);margin:.45rem 0;overflow:hidden;background:var(--bg1);}
.zone-header{font-family:var(--mono);font-size:.52rem;font-weight:600;letter-spacing:.28em;text-transform:uppercase;padding:.5rem 1rem;background:var(--bg2);border-bottom:1px solid var(--border);color:var(--ink3);display:flex;align-items:center;justify-content:space-between;gap:1rem;}
.zone-body{padding:.92rem 1rem;background:var(--bg1)}
.zone-accent-grn{border-left:3px solid var(--grn)}
.zone-accent-amb{border-left:3px solid var(--amb)}
.zone-accent-red{border-left:3px solid var(--red)}
.zone-accent-blu{border-left:3px solid var(--blu)}

.pill{display:inline-block;font-family:var(--mono);font-size:.56rem;font-weight:600;letter-spacing:.1em;padding:.15rem .6rem;border:1px solid;text-transform:uppercase;white-space:nowrap;}
.pill-grn{color:var(--grn);border-color:var(--grn-dim);background:var(--grn-bg)}
.pill-amb{color:var(--amb);border-color:var(--amb-dim);background:var(--amb-bg)}
.pill-red{color:var(--red);border-color:var(--red-dim);background:var(--red-bg)}
.pill-blu{color:var(--blu);border-color:var(--blu-dim);background:var(--blu-bg)}
.pill-dim{color:var(--ink3);border-color:var(--border);background:var(--bg2)}

.exec-conclusion{font-family:var(--serif);font-size:1.05rem;font-weight:600;color:#b8e8c8;line-height:1.55;padding:.9rem 1.1rem;border-left:4px solid var(--grn);background:var(--grn-bg);}
.exec-label{font-family:var(--mono);font-size:.48rem;letter-spacing:.3em;color:var(--grn);margin-bottom:.3rem;text-transform:uppercase;}
.exec-explanation{font-family:var(--sans);font-size:.83rem;color:var(--ink2);line-height:1.72;padding:.72rem 1.1rem;border-left:2px solid var(--border2);background:var(--bg2);}
.exec-conf{font-family:var(--mono);font-size:.5rem;color:var(--ink4);letter-spacing:.15em;padding:.35rem 1.1rem;background:var(--bg2);border-top:1px solid var(--border);text-align:right;}
.exec-falsif{border-top:1px solid var(--border);padding:.6rem 1rem;background:var(--bg2);display:flex;gap:.8rem;align-items:baseline;}
.exec-falsif-lbl{font-family:var(--mono);font-size:.48rem;letter-spacing:.2em;color:var(--ink4);white-space:nowrap;flex-shrink:0;}
.exec-falsif-txt{font-family:var(--sans);font-size:.78rem;color:#aab7ff;line-height:1.55;}

.hyp-dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1px;background:var(--border);border-top:1px solid var(--border);}
.hyp-card{background:var(--bg1);padding:.85rem 1rem;position:relative;overflow:hidden}
.hyp-card-winner{border-left:3px solid var(--grn)}
.hyp-card-2{border-left:3px solid var(--amb)}
.hyp-card-3{border-left:3px solid var(--ink3)}
.hyp-card-rank{font-family:var(--mono);font-size:.48rem;color:var(--ink4);letter-spacing:.2em;margin-bottom:.2rem;text-transform:uppercase}
.hyp-card-key{font-family:var(--mono);font-size:.72rem;font-weight:700;letter-spacing:.06em;margin-bottom:.08rem}
.hyp-card-lbl{font-family:var(--mono);font-size:.52rem;letter-spacing:.12em;color:var(--ink3);margin-bottom:.4rem}
.hyp-card-title{font-family:var(--serif);font-size:.92rem;font-weight:600;color:var(--ink);line-height:1.45;margin-bottom:.65rem}
.hyp-card-bar-wrap{display:flex;align-items:center;gap:.6rem;margin-bottom:.45rem}
.hyp-card-bar-track{flex:1;height:4px;background:var(--bg3);border-radius:2px;position:relative}
.hyp-card-bar-fill{position:absolute;left:0;top:0;height:100%;border-radius:2px}
.hyp-card-pct{font-family:var(--mono);font-size:.65rem;font-weight:700;min-width:2.5rem;text-align:right}
.hyp-card-meta{font-family:var(--mono);font-size:.5rem;color:var(--ink4);display:flex;gap:.6rem;flex-wrap:wrap}
.hyp-card-tes{font-family:var(--sans);font-size:.78rem;color:var(--ink2);line-height:1.62;margin-top:.5rem;padding-top:.5rem;border-top:1px solid var(--border);}

.nyckelord-strip{display:flex;gap:.4rem;flex-wrap:wrap;padding:.55rem 1rem;background:var(--bg2);border-top:1px solid var(--border)}
.nyckelord-label{font-family:var(--mono);font-size:.48rem;color:var(--ink4);letter-spacing:.2em;align-self:center;white-space:nowrap}
.nyckelord-tag{font-family:var(--mono);font-size:.6rem;color:var(--blu);border:1px solid var(--blu-dim);background:var(--blu-bg);padding:.12rem .5rem;text-decoration:none;letter-spacing:.04em}
.metod-strip{font-family:var(--mono);font-size:.56rem;color:var(--ink4);background:var(--bg2);border-top:1px solid var(--border);padding:.5rem 1rem;line-height:1.7;letter-spacing:.02em}

.rc-table{width:100%;border-collapse:collapse}
.rc-table td{padding:.45rem .65rem;border-bottom:1px solid var(--border);font-family:var(--sans);font-size:.77rem;vertical-align:top}
.rc-table tr:last-child td{border-bottom:none}
.rc-col-label{font-family:var(--mono);font-size:.48rem;color:var(--ink4);letter-spacing:.2em;white-space:nowrap;min-width:60px}
.rc-col-claim{color:var(--ink2);line-height:1.5}
.rc-col-status{white-space:nowrap}
.rc-col-source{color:var(--ink3);font-size:.72rem}
.rc-st-v{color:var(--grn);font-family:var(--mono);font-size:.6rem;font-weight:600}
.rc-st-d{color:var(--amb);font-family:var(--mono);font-size:.6rem;font-weight:600}
.rc-st-u{color:var(--red);font-family:var(--mono);font-size:.6rem;font-weight:600}
.rc-st-n{color:var(--ink3);font-family:var(--mono);font-size:.6rem}

.hyp-detail-label{font-family:var(--mono);font-size:.52rem;letter-spacing:.28em;color:var(--ink4);text-transform:uppercase;padding:1rem 0 .3rem;border-top:1px solid var(--border);margin-top:.8rem;}
.hyp-det-header{padding:.65rem 1rem;border-bottom:1px solid var(--border);background:var(--bg2)}
.hyp-det-key{font-family:var(--mono);font-size:.68rem;font-weight:700;letter-spacing:.06em}
.hyp-det-title{font-family:var(--serif);font-size:.95rem;font-weight:600;color:var(--ink);line-height:1.45}
.hyp-det-scores{display:flex;align-items:center;gap:.8rem;margin-top:.35rem;flex-wrap:wrap}
.hyp-det-bar-track{width:120px;height:4px;background:var(--bg3);border-radius:2px;position:relative}
.hyp-det-bar-fill{position:absolute;left:0;top:0;height:100%;border-radius:2px}
.hyp-det-score{font-family:var(--mono);font-size:.65rem;font-weight:600}
.hyp-det-styrka{font-family:var(--mono);font-size:.52rem;letter-spacing:.1em;color:var(--ink4)}
.hyp-sec-lbl{font-family:var(--mono);font-size:.5rem;letter-spacing:.2em;text-transform:uppercase;color:var(--ink4);margin-bottom:.25rem}
.hyp-sec-empty{font-family:var(--mono);font-size:.62rem;color:var(--ink4);font-style:italic;padding:.2rem .5rem}
.hyp-tes{font-family:var(--sans);font-size:.82rem;color:#9fe2bb;line-height:1.7;padding:.48rem .76rem;border-left:2px solid var(--grn-dim);background:var(--grn-bg)}
.hyp-ev-list{list-style:none;padding:0;margin:0}
.hyp-ev-list li{font-family:var(--sans);font-size:.79rem;color:var(--ink2);line-height:1.62;padding:.34rem .76rem;border-left:2px solid var(--grn-dim);background:var(--grn-bg);margin-bottom:.18rem;display:flex;gap:.45rem;align-items:baseline}
.hyp-ev-list li::before{content:"•";color:var(--grn);flex-shrink:0}
.hyp-mo{font-family:var(--sans);font-size:.79rem;color:#e0b1a7;line-height:1.62;padding:.34rem .76rem;border-left:2px solid var(--red-dim);background:var(--red-bg);margin-bottom:.18rem}
.hyp-fl{font-family:var(--sans);font-size:.79rem;color:#aab7ff;line-height:1.62;padding:.34rem .76rem;border-left:2px solid var(--blu-dim);background:var(--blu-bg)}

.primary-card{border:1px solid var(--border);margin-top:.75rem;background:var(--bg1)}
.primary-head{background:var(--bg2);padding:.55rem 1rem;border-bottom:1px solid var(--border);font-family:var(--mono);font-size:.63rem;color:var(--ink3);letter-spacing:.04em;text-transform:none}
.primary-intro{padding:.95rem 1rem .7rem;background:var(--bg2);border-bottom:1px solid var(--border)}
.primary-intro-k{font-family:var(--mono);font-size:.48rem;letter-spacing:.25em;color:var(--ink4);margin-bottom:.4rem;text-transform:uppercase}
.primary-intro-t{font-family:var(--sans);font-size:.82rem;color:var(--ink2);line-height:1.7}
.analysis-text{font-family:var(--sans);font-size:.82rem;line-height:1.86;color:var(--ink2)}
.analysis-text a{color:#6ca9ef;text-decoration:underline}

.verdict{border:1px solid;padding:.9rem 1rem;margin:.5rem 0;display:flex;align-items:center;gap:1rem}
.verdict-grn{border-color:var(--grn-dim);background:var(--grn-bg)}
.verdict-amb{border-color:var(--amb-dim);background:var(--amb-bg)}
.verdict-red{border-color:var(--red-dim);background:var(--red-bg)}
.verdict-icon{font-family:var(--mono);font-size:1.3rem}
.verdict-label{font-family:var(--mono);font-size:.5rem;letter-spacing:.25em;color:var(--ink4);margin-bottom:.2rem}
.verdict-text{font-family:var(--serif);font-size:.95rem;font-weight:600}
.verdict-grn .verdict-text{color:#80c89a}
.verdict-amb .verdict-text{color:#c09050}
.verdict-red .verdict-text{color:#c07060}

.conflict-line{font-size:.77rem;color:var(--ink2);padding:.2rem 0;border-bottom:1px solid var(--border);line-height:1.58}
.conflict-line:last-child{border-bottom:none}

.layer-card{border:1px solid var(--border);padding:.9rem 1rem;margin-bottom:.4rem;background:var(--bg1)}
.layer-lbl{font-family:var(--mono);font-size:.5rem;color:var(--ink4);letter-spacing:.2em;margin-bottom:.2rem}
.layer-ttl{font-family:var(--serif);font-size:.88rem;color:var(--ink2);font-weight:600;margin-bottom:.6rem;padding-bottom:.35rem;border-bottom:1px solid var(--border)}

.degraded{border:1px solid var(--red-dim);border-left:3px solid var(--red);background:var(--red-bg);padding:.75rem 1rem;margin:.6rem 0;font-family:var(--mono);font-size:.65rem;color:var(--red);line-height:1.7}
.empty-state{margin-top:2rem;padding:2rem;border:1px solid var(--border);background:var(--bg1)}
.empty-kw{font-family:var(--mono);font-size:.52rem;letter-spacing:.3em;color:var(--ink4);margin-bottom:.9rem}
.empty-row{display:flex;gap:1rem;padding:.4rem 0;border-bottom:1px solid var(--border);font-size:.8rem}
.empty-step{font-family:var(--mono);font-size:.6rem;color:var(--ink4);min-width:4.5rem;padding-top:.05rem}
.empty-desc{color:var(--ink3);line-height:1.5}
.empty-footer{font-family:var(--mono);font-size:.58rem;color:var(--ink4);margin-top:.9rem;letter-spacing:.05em}

.link-strip{
  display:flex; gap:.38rem; flex-wrap:wrap; margin-top:.55rem;
}
.link-chip{
  display:inline-block; font-family:var(--mono); font-size:.56rem;
  color:#8cc4ff; border:1px solid var(--blu-dim); background:var(--blu-bg);
  padding:.16rem .48rem; text-decoration:none; letter-spacing:.03em;
}
.link-chip:hover{
  background:#0d1830; color:#b8dcff;
}
.link-strip-dim{
  font-family:var(--mono); font-size:.55rem; color:var(--ink4); margin-top:.45rem;
}

div[data-testid="stExpander"]>div:first-child{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:0!important;font-family:var(--mono)!important;font-size:.63rem!important;color:var(--ink3)!important}
div[data-testid="stExpander"]>div:last-child{background:var(--bg1)!important;border:1px solid var(--border)!important;border-top:none!important;border-radius:0!important}
.stSpinner>div{border-top-color:var(--grn)!important}
</style>
""",
    unsafe_allow_html=True,
)


def _slugify(q: str, n: int = 45) -> str:
    s = q or ""
    for k, v in {"å": "a", "ä": "a", "ö": "o", "Å": "A", "Ä": "A", "Ö": "O"}.items():
        s = s.replace(k, v)
    s = re.sub(r"[^a-zA-Z0-9\s]", "", s).strip().lower()
    s = re.sub(r"\s+", "_", s)
    return s[:n] or "analys"


def _safe(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _autolink_raw_urls(text: str) -> str:
    if not text:
        return ""

    def repl(m):
        url = m.group(0)
        return f"[{url}]({url})"

    return re.sub(r'(?<!\]\()(?<!href=")(https?://[^\s<]+)', repl, text)


def _safe_links(text: str) -> str:
    if not text:
        return ""
    text = _autolink_raw_urls(text)
    links = {}

    def _stash_md(m):
        key = f"\x00L{len(links)}\x00"
        label = _safe(m.group(1))
        url = m.group(2)
        links[key] = f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>'
        return key

    t2 = re.sub(r"\[([^\]]+)\]\((https?://[^\s\)]+)\)", _stash_md, text)
    t2 = _safe(t2)
    for key, html in links.items():
        t2 = t2.replace(key, html)
    t2 = t2.replace("\n", "<br>")
    return t2


def _extract_urls(text: str):
    if not text:
        return []
    urls = re.findall(r'https?://[^\s<\)"]+', text)
    seen = set()
    out = []
    for u in urls:
        u = u.rstrip('.,;]')
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _domain_label(url: str) -> str:
    m = re.search(r'https?://(?:www\.)?([^/\s]+)', url or "")
    return m.group(1) if m else "källa"


def _links_strip_html(urls, max_links=4):
    urls = [u for u in urls if u][:max_links]
    if not urls:
        return '<div class="link-strip-dim">Inga klickbara länkar extraherade i denna del.</div>'
    chips = []
    for u in urls:
        label = _domain_label(u)
        chips.append(f'<a class="link-chip" href="{u}" target="_blank" rel="noopener noreferrer">{_safe(label)}</a>')
    return '<div class="link-strip">' + "".join(chips) + '</div>'


def _collect_links_from_hyp(hyp: dict):
    urls = []
    for part in [hyp.get("tes", ""), hyp.get("falsifiering", "")]:
        urls.extend(_extract_urls(part))
    for lst_name in ["bevis", "motarg"]:
        for item in hyp.get(lst_name, []) or []:
            urls.extend(_extract_urls(item))
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _pill(label: str, cls: str) -> str:
    return f'<span class="pill pill-{cls}">{_safe(label)}</span>'


def _section_zone(title: str, body_html: str, accent: str = "blu", right_html: str = "") -> str:
    return f"""
<div class="zone zone-accent-{accent}">
  <div class="zone-header"><span>{_safe(title)}</span><span>{right_html}</span></div>
  <div class="zone-body">{body_html}</div>
</div>
"""


def step_html(steps):
    h = '<div class="step-row">'
    for label, status in steps:
        cls = {"done": "step-done", "active": "step-active", "warn": "step-warn"}.get(status, "")
        h += f'<span class="step {cls}">{_safe(label)}</span>'
    return h + "</div>"


STYRKA_COLOR = {
    "HÖG": "#57c78a",
    "MEDEL-HÖG": "#8fd45f",
    "MEDEL": "#6eb6ff",
    "LÅG": "#db6b57",
}

REALITY_PILL = {
    "VERIFIED": ("grn", "✓ VERIFIED"),
    "ONGOING": ("blu", "◉ ONGOING"),
    "PARTIAL": ("amb", "◑ PARTIAL"),
    "HYPOTHETICAL": ("dim", "◌ HYPOTHETICAL"),
    "ANALYTICAL": ("blu", "◎ ANALYTICAL"),
    "UNVERIFIED": ("red", "✗ UNVERIFIED"),
    "ERROR": ("red", "✗ ERROR"),
}
STATUS_PILL = {
    "KLAR": ("grn", "✓ KLAR"),
    "REVIDERAD": ("amb", "↻ REVIDERAD"),
    "DEGRADERAD": ("red", "⚠ DEGRADERAD"),
    "RUNNING": ("blu", "◉ RUNNING"),
}


def _build_assessment(ranked):
    if not ranked:
        return "", ""
    winner = ranked[0]
    conclusion = f"Evidensen stödjer starkast {winner.get('key','')} [{winner.get('label','')}]"
    if winner.get("title"):
        conclusion += f" — {winner['title']}"
    conclusion += "."

    parts = []
    tes = winner.get("tes", "")
    if tes:
        short = tes[:260]
        if len(tes) > 260:
            cut = short.rfind(". ")
            if cut > 90:
                short = short[:cut + 1]
            else:
                short = short.rstrip() + "…"
        if short and not short.endswith(".") and not short.endswith("…"):
            short += "."
        parts.append(short)

    if len(ranked) > 1:
        r2 = ranked[1]
        p = f"Sekundär förklaringskraft: {r2.get('key','')} [{r2.get('label','')}]"
        if r2.get("title"):
            p += f" — {r2['title'][:70]}"
        p += f" (conf {r2.get('conf', 0.5):.2f})."
        parts.append(p)

    if len(ranked) > 2:
        r3 = ranked[-1]
        parts.append(f"Svagast: {r3.get('key','')} [{r3.get('label','')}] (conf {r3.get('conf', 0.2):.2f}).")

    return conclusion, " ".join(parts)


def _hyp_dashboard_html(ranked):
    cards = []
    rank_labels = ["#1 STARKAST", "#2", "#3", "#4"]
    card_classes = ["hyp-card-winner", "hyp-card-2", "hyp-card-3"]

    for i, h in enumerate(ranked[:4]):
        key = h.get("key", "")
        lbl = h.get("label", "")
        title = h.get("title", "")
        styrka = (h.get("styrka") or "MEDEL").upper()
        tes = h.get("tes", "")
        bevis = h.get("bevis", []) or []
        motarg = h.get("motarg", []) or []
        pct = int(h.get("conf_pct", int(h.get("conf", 0.5) * 100)))
        color = STYRKA_COLOR.get(styrka, "#6eb6ff")
        cls = card_classes[i] if i < len(card_classes) else ""

        tes_short = ""
        if tes:
            tes_short = tes[:220]
            if len(tes) > 220:
                cut = tes_short.rfind(". ")
                if cut > 80:
                    tes_short = tes_short[:cut + 1]
                else:
                    tes_short = tes_short.rstrip() + "…"

        link_strip = _links_strip_html(_collect_links_from_hyp(h), max_links=3)

        cards.append(f"""
<div class="hyp-card {cls}">
  <div class="hyp-card-rank">{rank_labels[i] if i < len(rank_labels) else f'#{i+1}'}</div>
  <div class="hyp-card-key" style="color:{color}">{_safe(key)}</div>
  <div class="hyp-card-lbl">{_safe(lbl)}</div>
  <div class="hyp-card-title">{_safe(title)}</div>
  <div class="hyp-card-bar-wrap">
    <div class="hyp-card-bar-track"><div class="hyp-card-bar-fill" style="width:{pct}%;background:{color}"></div></div>
    <span class="hyp-card-pct" style="color:{color}">{pct}%</span>
  </div>
  <div class="hyp-card-meta"><span>{_safe(styrka)}</span><span>{len(bevis)} bevis</span><span>{len(motarg)} motarg</span></div>
  {"<div class='hyp-card-tes'>" + _safe(tes_short) + "</div>" if tes_short else ""}
  {link_strip}
</div>
""")
    return '<div class="hyp-dashboard">' + "".join(cards) + "</div>"


def _nyckelord_html(ranked):
    if not ranked:
        return ""
    tags = []
    for h in ranked[:3]:
        term = " ".join((h.get("title") or h.get("label") or h.get("key") or "").split()[:3]).strip()
        if term:
            url = "https://www.google.com/search?q=" + quote_plus(term)
            tags.append(
                f'<a class="nyckelord-tag" href="{url}" target="_blank" rel="noopener noreferrer">{_safe(term)}</a>'
            )
    if not tags:
        return ""
    return '<div class="nyckelord-strip"><span class="nyckelord-label">SÖK VIDARE</span>' + "".join(tags) + "</div>"


def _parse_rc_structured(txt: str):
    items = []
    for block in re.split(r"\n(?=CLAIM\s*\d*:)", txt or "", flags=re.IGNORECASE):
        c_m = re.search(r"CLAIM\s*\d*:\s*(.+?)(?:\n|$)", block, re.IGNORECASE)
        s_m = re.search(r"STATUS\s*:\s*(.+?)(?:\n|$)", block, re.IGNORECASE)
        src_m = re.search(r"(?:SOURCE|KÄLLA)\s*:\s*(.+?)(?:\n|$)", block, re.IGNORECASE)
        if c_m:
            items.append({
                "claim": c_m.group(1).strip(),
                "status": s_m.group(1).strip() if s_m else "",
                "source": src_m.group(1).strip() if src_m else "",
            })
    if items:
        return items[:6]

    for line in (txt or "").split("\n"):
        s = line.strip()
        u = s.upper()
        if not s or len(s) < 12:
            continue
        if any(x in u for x in ["ÖVERGRIPANDE", "OVERALL STATUS", "BESLUT:", "REALITY CHECK", "SAMMANFATTNING"]):
            continue

        st = ""
        if any(x in u for x in ["VERIFIED", "BEKRÄFTAD", "✓", "✔"]):
            st = "VERIFIED"
        elif any(x in u for x in ["DISPUTED", "OMTVISTAD", "DELVIS", "PARTIAL", "OKLART", "◑"]):
            st = "DISPUTED"
        elif any(x in u for x in ["UNVERIFIED", "EJ BEKRÄFTAD", "✗"]):
            st = "UNVERIFIED"

        src = ""
        sm = re.search(r"\(([^)]{5,90})\)\s*$", s)
        if sm:
            src = sm.group(1).strip()

        clean = re.sub(r"^(CLAIM\s*\d*:?\s*|[-•·]\s*)", "", s).strip()
        if len(clean) > 10:
            items.append({"claim": clean[:220], "status": st, "source": src})
        if len(items) >= 6:
            break

    if items:
        return items[:6]

    fallback_lines = [l.strip() for l in (txt or "").split("\n") if l.strip()]
    out = []
    for line in fallback_lines[:6]:
        out.append({"claim": line[:240], "status": "", "source": ""})
    return out or [{"claim": (txt or "")[:300].replace("\n", " "), "status": "", "source": ""}]


def _rc_table_html(items):
    rows = []
    for it in items:
        claim = it.get("claim", "")
        status = (it.get("status", "") or "").upper()
        source = it.get("source", "")

        if "VERIFIED" in status or "BEKRÄFTAD" in status:
            sc, si = "rc-st-v", "✓ VERIFIED"
        elif "DISPUTED" in status or "OMTVISTAD" in status or "PARTIAL" in status:
            sc, si = "rc-st-d", "◑ DISPUTED"
        elif "UNVERIFIED" in status or "EJ BEKRÄFTAD" in status:
            sc, si = "rc-st-u", "✗ UNVERIFIED"
        else:
            sc, si = "rc-st-n", "◎ —"

        src_html = _safe_links(source) if source else '<span style="color:var(--ink4)">—</span>'
        rows.append(
            f'<tr><td class="rc-col-label">CLAIM</td><td class="rc-col-claim">{_safe_links(claim)}</td><td class="rc-col-status"><span class="{sc}">{si}</span></td><td class="rc-col-source">{src_html}</td></tr>'
        )
    return '<table class="rc-table">' + "".join(rows) + "</table>"


def _verdict_from_red_team(red_text: str):
    up = (red_text or "").upper()
    if "KOLLAPSAR" in up:
        return "red", "✗", "KOLLAPSAR — Analysen håller inte"
    if "MODIFIERAS" in up or "IFRÅGASATT" in up or "UTMANAD" in up:
        return "amb", "◑", "MODIFIERAS — Analysen revideras"
    if "HÅLLER" in up:
        return "grn", "✓", "HÅLLER — Analysen bekräftad"
    return None, None, None


def _normalize_text_for_render(text: str) -> str:
    if not text:
        return ""
    try:
        from normalizer import normalize_references
        return normalize_references(text)
    except Exception:
        return text


def _render_primary_analysis_block(ranked, claude_answer):
    intro = """
<div class="primary-card">
  <div class="primary-head">📄 Primäranalys — Claude Opus råtext</div>
  <div class="primary-intro">
    <div class="primary-intro-k">Primäranalys · Claude Opus · steg 1</div>
    <div class="primary-intro-t">Analysen identifierar konkurrerande hypoteser, väger evidens, testar motargument och försöker falsifiera alternativa förklaringar. Här visas både strukturerad hypotesöversikt och den fulla råtexten längre ner.</div>
  </div>
</div>
"""
    st.markdown(intro, unsafe_allow_html=True)

    if ranked:
        for hyp in ranked:
            key = hyp.get("key", "")
            lbl = hyp.get("label", "")
            title = hyp.get("title", "")
            styrka = (hyp.get("styrka") or "MEDEL").upper()
            tes = hyp.get("tes", "")
            bevis = hyp.get("bevis", []) or []
            motarg = hyp.get("motarg", []) or []
            falsif = hyp.get("falsifiering", "")
            conf = hyp.get("conf", 0.5)
            pct = int(hyp.get("conf_pct", int(conf * 100)))
            color = STYRKA_COLOR.get(styrka, "#6eb6ff")

            ev_html = (
                '<ul class="hyp-ev-list">' + "".join(f"<li>{_safe_links(b)}</li>" for b in bevis[:5]) + "</ul>"
            ) if bevis else '<div class="hyp-sec-empty">Ingen evidens identifierad.</div>'
            mo_html = (
                "".join(f'<div class="hyp-mo">{_safe_links(m)}</div>' for m in motarg[:3])
            ) if motarg else '<div class="hyp-sec-empty">Inga motargument identifierade.</div>'
            fl_html = f'<div class="hyp-fl">{_safe_links(falsif)}</div>' if falsif else '<div class="hyp-sec-empty">Inget falsifieringstest identifierat.</div>'
            hyp_links_html = _links_strip_html(_collect_links_from_hyp(hyp), max_links=5)

            st.markdown(f"""
<div class="zone" style="margin-top:0;border-left:3px solid {color}">
  <div class="hyp-det-header">
    <div class="hyp-det-key" style="color:{color}">{_safe(key)}  {_safe(lbl)}</div>
    <div class="hyp-det-title">{_safe(title)}</div>
    <div class="hyp-det-scores">
      <div class="hyp-det-bar-track"><div class="hyp-det-bar-fill" style="width:{pct}%;background:{color}"></div></div>
      <span class="hyp-det-score" style="color:{color}">{conf:.2f} ({pct}%)</span>
      <span class="hyp-det-styrka">{_safe(styrka)}</span>
      <span style="font-family:var(--mono);font-size:.5rem;color:var(--ink4)">{len(bevis)} bevis · {len(motarg)} motarg</span>
    </div>
  </div>
  <div class="zone-body" style="padding:.8rem .9rem">
    <div style="margin-bottom:.7rem"><div class="hyp-sec-lbl">TES</div>{('<div class="hyp-tes">' + _safe_links(tes) + '</div>') if tes else '<div class="hyp-sec-empty">Ingen tes identifierad.</div>'}</div>
    <div style="margin-bottom:.7rem"><div class="hyp-sec-lbl">EVIDENS</div>{ev_html}{hyp_links_html}</div>
    <div style="margin-bottom:.7rem"><div class="hyp-sec-lbl">MOTARGUMENT</div>{mo_html}</div>
    <div><div class="hyp-sec-lbl">FALSIFIERINGSTEST</div>{fl_html}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    with st.expander("Visa full råtext från primäranalysen", expanded=False):
        st.markdown(
            f'<div class="analysis-text">{_safe_links(_normalize_text_for_render(claude_answer))}</div>',
            unsafe_allow_html=True,
        )


for key, val in [
    ("result", None),
    ("running", False),
    ("awaiting_confirm", False),
    ("layers_generated", False),
    ("deep_generated", False),
]:
    if key not in st.session_state:
        st.session_state[key] = val


with st.sidebar:
    st.markdown(
        '<div style="font-family:monospace;font-size:.58rem;letter-spacing:.25em;color:#666;padding:.5rem 0;text-transform:uppercase;">Sparade analyser</div>',
        unsafe_allow_html=True,
    )
    try:
        from history import list_history, load_result, delete_result
        from pdf_export import build_pdf as _pdf_sidebar

        entries = list_history()
        if not entries:
            st.caption("Inga sparade analyser.")

        for e in entries:
            ts = e.get("timestamp", "").replace("_", " ")[:16]
            ico = {
                "VERIFIED": "✅",
                "ANALYTICAL": "🔍",
                "PARTIAL": "⚠️",
                "UNVERIFIED": "❌",
                "HYPOTHETICAL": "💭",
            }.get(e.get("reality"), "📄")

            with st.expander(f"{ico} {ts}"):
                q = e.get("question", "")
                st.caption(q[:50] + "…" if len(q) > 50 else q)
                c1, c2, c3 = st.columns(3)

                with c1:
                    if st.button("Öppna", key=f"o_{e['filename']}"):
                        loaded = load_result(e["filename"])
                        if loaded:
                            st.session_state.result = loaded
                            st.session_state.layers_generated = bool(loaded.get("layers", {}).get("ground"))
                            st.session_state.deep_generated = bool(loaded.get("layers", {}).get("deep1"))
                            st.rerun()

                with c2:
                    try:
                        loaded2 = load_result(e["filename"])
                        if loaded2:
                            pb = _pdf_sidebar(loaded2)
                            slug = _slugify(loaded2.get("question", "analys"))
                            st.download_button(
                                "PDF",
                                pb,
                                file_name=f"sanningsmaskinen_{e['timestamp'][:10]}_{slug}.pdf",
                                mime="application/pdf",
                                key=f"p_{e['filename']}",
                            )
                    except Exception:
                        pass

                with c3:
                    if st.button("🗑", key=f"d_{e['filename']}"):
                        delete_result(e["filename"])
                        st.rerun()
    except Exception:
        st.caption("history.py saknas eller kunde inte laddas.")


today_str = _date.today().strftime("%Y-%m-%d")

st.markdown(
    f"""
<div class="topbar">
  <div class="topbar-left">
    <span class="topbar-mark">◎ Sanningsmaskinen</span>
    <span class="topbar-title">Epistemiskt analysverktyg</span>
  </div>
  <div class="topbar-right">v8.17b · Claude Opus + GPT-4o · {today_str}</div>
</div>
<div class="topbar-sub">
  Analyserar komplexa frågor genom att väga konkurrerande hypoteser, granska evidens och falsifiera svagare förklaringar.
</div>
""",
    unsafe_allow_html=True,
)

question = st.text_area(
    "",
    placeholder="Skriv en fråga — t.ex. Vem sprängde Nord Stream? eller Varför invaderade Ryssland Ukraina 2022?",
    height=84,
    label_visibility="collapsed",
)

c1, c2, _ = st.columns([1.5, 1, 5])
with c1:
    run_btn = st.button("Analysera →", disabled=st.session_state.running)
with c2:
    if st.session_state.result and st.button("Rensa"):
        st.session_state.result = None
        st.session_state.layers_generated = False
        st.session_state.deep_generated = False
        st.rerun()

if run_btn and question.strip():
    st.session_state.running = True
    st.session_state.result = None
    st.session_state.layers_generated = False
    st.session_state.deep_generated = False

    try:
        from engine import (
            event_reality_check,
            ask_claude,
            ask_gpt_critic,
            analyze_conflicts,
            run_red_team,
            auto_rewrite,
            assess_depth_recommendation,
        )

        steps = [
            ("0 Reality", ""),
            ("1 Primär", ""),
            ("2 GPT", ""),
            ("3 Konflikt", ""),
            ("4 Red Team", ""),
            ("5 Rewrite?", ""),
        ]
        ph = st.empty()

        def upd(i, warn=-1):
            arr = []
            for j, (n, _) in enumerate(steps):
                if j < i:
                    arr.append((n, "done"))
                elif j == i:
                    arr.append((n, "active"))
                elif j == warn:
                    arr.append((n, "warn"))
                else:
                    arr.append((n, ""))
            ph.markdown(step_html(arr), unsafe_allow_html=True)

        upd(0)
        with st.spinner("Reality check..."):
            rc = event_reality_check(question.strip())

        upd(1)
        if not rc.get("proceed"):
            st.session_state.awaiting_confirm = True
            st.session_state._rc = rc
            st.session_state._question = question.strip()
            st.session_state.running = False
            ph.empty()
            st.rerun()

        with st.spinner("Primäranalys..."):
            ca = ask_claude(question.strip(), rc)

        upd(2)
        with st.spinner("GPT-4 kritiker..."):
            ga = ask_gpt_critic(question.strip(), ca, rc["status"])

        upd(3)
        with st.spinner("Konfliktanalys..."):
            cf = analyze_conflicts(ca, ga)

        upd(4)
        with st.spinner("Red Team..."):
            rr, should_rewrite = run_red_team(question.strip(), ca, cf)

        red_team_ok = bool(rr and "misslyckades" not in rr.lower() and "api-fel" not in rr.lower() and len(rr) > 100)
        fa = ""
        if should_rewrite and red_team_ok:
            upd(5)
            with st.spinner("Rewrite..."):
                fa = auto_rewrite(question.strip(), ca, rr)

        ph.markdown(step_html([(n, "done") for n, _ in steps]), unsafe_allow_html=True)

        result = {
            "question": question.strip(),
            "reality_check": rc,
            "claude_answer": ca,
            "gpt_answer": ga,
            "conflict_report": cf,
            "red_team_report": rr,
            "red_team_ok": red_team_ok,
            "collapsed": should_rewrite,
            "final_analysis": fa,
            "layers": {},
            "degraded": not red_team_ok,
            "status": "DEGRADERAD" if not red_team_ok else ("REVIDERAD" if fa else "KLAR"),
        }
        result["depth_recommendation"] = assess_depth_recommendation(result)
        st.session_state.result = result

        try:
            from history import save_result
            save_result(result)
        except Exception:
            pass

    except ImportError as e:
        st.error(f"Importfel: {e}")
    except Exception as e:
        st.error(f"Fel: {e}")
    finally:
        st.session_state.running = False
        st.rerun()

if st.session_state.awaiting_confirm:
    rc_tmp = st.session_state.get("_rc", {})
    q_tmp = st.session_state.get("_question", "")

    st.markdown(
        f'<div class="degraded">HÄNDELSEN KAN INTE VERIFIERAS<br>{_safe(rc_tmp.get("text","")[:300])}<br><br>Fortsätta som hypotetiskt scenario?</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1, 4])

    with c1:
        if st.button("Ja, fortsätt"):
            rc_tmp["proceed"] = True
            st.session_state.awaiting_confirm = False
            st.session_state.running = True
            try:
                from engine import (
                    ask_claude,
                    ask_gpt_critic,
                    analyze_conflicts,
                    run_red_team,
                    auto_rewrite,
                    assess_depth_recommendation,
                )

                ca = ask_claude(q_tmp, rc_tmp)
                ga = ask_gpt_critic(q_tmp, ca, rc_tmp["status"])
                cf = analyze_conflicts(ca, ga)
                rr, should_rewrite = run_red_team(q_tmp, ca, cf)
                red_team_ok = bool(rr and "misslyckades" not in rr.lower() and "api-fel" not in rr.lower() and len(rr) > 100)
                fa = auto_rewrite(q_tmp, ca, rr) if should_rewrite and red_team_ok else ""

                result = {
                    "question": q_tmp,
                    "reality_check": rc_tmp,
                    "claude_answer": ca,
                    "gpt_answer": ga,
                    "conflict_report": cf,
                    "red_team_report": rr,
                    "red_team_ok": red_team_ok,
                    "collapsed": should_rewrite,
                    "final_analysis": fa,
                    "layers": {},
                    "degraded": not red_team_ok,
                    "status": "DEGRADERAD" if not red_team_ok else ("REVIDERAD" if fa else "KLAR"),
                }
                result["depth_recommendation"] = assess_depth_recommendation(result)
                st.session_state.result = result
            except Exception as e:
                st.error(f"Fel: {e}")
            finally:
                st.session_state.running = False
                st.rerun()

    with c2:
        if st.button("Avbryt"):
            st.session_state.awaiting_confirm = False
            st.rerun()

if st.session_state.result:
    r = st.session_state.result
    rc = r["reality_check"]
    lyr = r.get("layers", {})

    try:
        from normalizer import normalize_claude_answer, compute_hypothesis_scores, normalize_references

        normalized_claude_text = normalize_references(r.get("claude_answer", ""))
        norm = normalize_claude_answer(normalized_claude_text)
        norm["hypotheses"] = compute_hypothesis_scores(norm.get("hypotheses", []))
        hyps = norm.get("hypotheses", [])
    except Exception as e:
        hyps = []
        st.markdown(
            f'<div class="degraded">NORMALIZER-KUNDE-INTE-PARSA HYPOTESER: {_safe(str(e))}</div>',
            unsafe_allow_html=True,
        )

    rank_order = {"HÖG": 0, "MEDEL-HÖG": 1, "MEDEL": 2, "LÅG": 3}
    ranked = sorted(
        hyps,
        key=lambda h: (
            rank_order.get((h.get("styrka") or "MEDEL").upper(), 99),
            -float(h.get("conf", 0)),
        ),
    )

    rc_status = (rc.get("status", "") or "").upper()
    res_status = (r.get("status", "") or "").upper()

    if r.get("degraded"):
        st.markdown(
            '<div class="degraded">⚠ DEGRADERAD LEVERANS — Red Team körde inte korrekt. Lita inte på slutsatserna utan oberoende verifiering.</div>',
            unsafe_allow_html=True,
        )

    rc_pill_cls, rc_pill_lbl = REALITY_PILL.get(rc_status, ("dim", rc_status))
    st_pill_cls, st_pill_lbl = STATUS_PILL.get(res_status, ("dim", res_status))
    question_body = (
        f'<div style="font-family:var(--serif);font-size:1.12rem;color:var(--ink);line-height:1.5;margin-bottom:.55rem;">{_safe(r["question"])}</div>'
        f'<div style="display:flex;gap:.4rem;flex-wrap:wrap;">{_pill(rc_pill_lbl, rc_pill_cls)}{_pill(st_pill_lbl, st_pill_cls)}</div>'
    )
    st.markdown(_section_zone("FRÅGA", question_body, "blu", today_str), unsafe_allow_html=True)

    if ranked:
        conclusion, explanation = _build_assessment(ranked)
        confs = [float(h.get("conf", 0.5)) for h in ranked]
        avg_conf = sum(confs) / len(confs) if confs else 0.5

        if avg_conf >= 0.70:
            conf_lbl, conf_col = "HÖG", "var(--grn)"
        elif avg_conf >= 0.50:
            conf_lbl, conf_col = "MEDEL–HÖG", "#8fd45f"
        elif avg_conf >= 0.35:
            conf_lbl, conf_col = "MEDEL", "var(--blu)"
        else:
            conf_lbl, conf_col = "LÅG", "var(--red)"

        falsif = ranked[0].get("falsifiering", "")
        falsif_html = (
            f'<div class="exec-falsif"><span class="exec-falsif-lbl">VAD FALSIFIERAR?</span><span class="exec-falsif-txt">{_safe_links(falsif)}</span></div>'
            if falsif else ""
        )
        winner_links = _links_strip_html(_collect_links_from_hyp(ranked[0]), max_links=4)

        exec_html = (
            f'<div class="exec-conclusion"><div class="exec-label">SLUTSATS</div>{_safe(conclusion)}</div>'
            f'<div class="exec-explanation">{_safe(explanation)}</div>'
            f'{winner_links}'
            f'<div class="exec-conf">AGGREGERAD KONFIDENS <span style="color:{conf_col};font-weight:700">{avg_conf:.2f}</span> · {conf_lbl}</div>'
            f'{falsif_html}'
        )

        st.markdown(
            _section_zone(
                "EXECUTIVE SUMMARY",
                exec_html,
                "grn",
                '<span style="font-size:.48rem;letter-spacing:.08em;color:var(--ink4)">ANALYTISK BEDÖMNING · INTE ETT SVAR</span>',
            ),
            unsafe_allow_html=True,
        )

    if ranked:
        hyp_html = (
            _hyp_dashboard_html(ranked)
            + _nyckelord_html(ranked)
            + '<div class="metod-strip">Confidence = evidensstyrka × log(bevisantal+1) × källkvalitet, normaliserat 0–1. E5=officiell · E4=kvalitetsjournalistik · E3=rapport · E2=sekundär · E1=rykten</div>'
        )
        st.markdown(
            _section_zone(
                "HYPOTESER",
                hyp_html,
                "grn",
                '<span style="font-size:.48rem;color:var(--ink4)">EVIDENSSTYRKA · KLICKA FÖR DETALJER NEDAN</span>',
            ),
            unsafe_allow_html=True,
        )

    rc_text = rc.get("text", "") or rc.get("result", "")
    rc_items = _parse_rc_structured(rc_text)
    rc_accent = {
        "VERIFIED": "grn",
        "ONGOING": "blu",
        "PARTIAL": "amb",
        "UNVERIFIED": "red",
        "ANALYTICAL": "blu",
        "HYPOTHETICAL": "dim",
        "ERROR": "red",
    }.get(rc_status, "dim")
    rc_pill_cls, rc_pill_lbl = REALITY_PILL.get(rc_status, ("dim", rc_status))
    st.markdown(
        _section_zone("REALITY CHECK", _rc_table_html(rc_items), rc_accent, _pill(rc_pill_lbl, rc_pill_cls)),
        unsafe_allow_html=True,
    )

    if ranked:
        st.markdown(
            '<div class="hyp-detail-label">Hypotes-detaljer — tes · evidens · motargument · falsifiering</div>',
            unsafe_allow_html=True,
        )
        for hyp in ranked:
            key = hyp.get("key", "")
            lbl = hyp.get("label", "")
            title = hyp.get("title", "")
            styrka = (hyp.get("styrka") or "MEDEL").upper()
            tes = hyp.get("tes", "")
            bevis = hyp.get("bevis", []) or []
            motarg = hyp.get("motarg", []) or []
            falsif = hyp.get("falsifiering", "")
            conf = float(hyp.get("conf", 0.5))
            pct = int(hyp.get("conf_pct", int(conf * 100)))
            color = STYRKA_COLOR.get(styrka, "#6eb6ff")

            ev_html = (
                '<ul class="hyp-ev-list">' + "".join(f"<li>{_safe_links(b)}</li>" for b in bevis[:5]) + "</ul>"
            ) if bevis else '<div class="hyp-sec-empty">Ingen evidens identifierad.</div>'
            mo_html = (
                "".join(f'<div class="hyp-mo">{_safe_links(m)}</div>' for m in motarg[:3])
            ) if motarg else '<div class="hyp-sec-empty">Inga motargument identifierade.</div>'
            fl_html = f'<div class="hyp-fl">{_safe_links(falsif)}</div>' if falsif else '<div class="hyp-sec-empty">Inget falsifieringstest identifierat.</div>'
            hyp_links_html = _links_strip_html(_collect_links_from_hyp(hyp), max_links=5)

            with st.expander(f"{key}  [{lbl}]  {pct}%  —  {title}", expanded=False):
                st.markdown(f"""
<div class="hyp-det-header">
  <div class="hyp-det-key" style="color:{color}">{_safe(key)}  {_safe(lbl)}</div>
  <div class="hyp-det-title">{_safe(title)}</div>
  <div class="hyp-det-scores">
    <div class="hyp-det-bar-track"><div class="hyp-det-bar-fill" style="width:{pct}%;background:{color}"></div></div>
    <span class="hyp-det-score" style="color:{color}">{conf:.2f} ({pct}%)</span>
    <span class="hyp-det-styrka">{_safe(styrka)}</span>
    <span style="font-family:var(--mono);font-size:.5rem;color:var(--ink4)">{len(bevis)} bevis · {len(motarg)} motarg</span>
  </div>
</div>
<div style="padding:.8rem .9rem;background:var(--bg1)">
  <div style="margin-bottom:.7rem"><div class="hyp-sec-lbl">TES</div>{('<div class="hyp-tes">' + _safe_links(tes) + '</div>') if tes else '<div class="hyp-sec-empty">Ingen tes identifierad.</div>'}</div>
  <div style="margin-bottom:.7rem"><div class="hyp-sec-lbl">EVIDENS</div>{ev_html}{hyp_links_html}</div>
  <div style="margin-bottom:.7rem"><div class="hyp-sec-lbl">MOTARGUMENT</div>{mo_html}</div>
  <div><div class="hyp-sec-lbl">FALSIFIERINGSTEST</div>{fl_html}</div>
</div>
""", unsafe_allow_html=True)

    _render_primary_analysis_block(ranked, r.get("claude_answer", ""))

    rr = r.get("red_team_report", "")
    vc, vi, vt = _verdict_from_red_team(rr)
    if vc:
        st.markdown(f"""
<div class="verdict verdict-{vc}">
  <span class="verdict-icon" style="color:var(--{vc})">{vi}</span>
  <div><div class="verdict-label">RED TEAM VERDICT — STEG 4</div><div class="verdict-text">{_safe(vt)}</div></div>
</div>
""", unsafe_allow_html=True)

    cf = _normalize_text_for_render(r.get("conflict_report", ""))
    if cf:
        lines = [l.strip() for l in cf.split("\n") if l.strip()]
        body = "".join(f'<div class="conflict-line">{_safe_links(line)}</div>' for line in lines[:8])
        conflict_urls = _extract_urls(cf)
        body += _links_strip_html(conflict_urls, max_links=5)
        st.markdown(_section_zone("KONFLIKTANALYS — CLAUDE vs GPT", body, "amb"), unsafe_allow_html=True)

    st.markdown('<div style="border-top:1px solid var(--border);margin:1rem 0 .5rem;"></div>', unsafe_allow_html=True)

    if not st.session_state.layers_generated:
        cl1, cl2 = st.columns([1, 3])
        with cl1:
            if st.button("📊 Layer 1–5"):
                with st.spinner("Bygger lagerstruktur..."):
                    from engine import deliver_ground_layers
                    ground = deliver_ground_layers(
                        r["question"],
                        r["claude_answer"],
                        r["gpt_answer"],
                        r["red_team_report"],
                        r["final_analysis"],
                        rc,
                    )
                    r["layers"]["ground"] = ground
                    st.session_state.result = r
                    st.session_state.layers_generated = True
                    st.rerun()
        with cl2:
            st.caption("Destillerar analysen till journalistiskt format.")
    else:
        ground = _normalize_text_for_render(lyr.get("ground", ""))
        secs = re.split(r"(LAYER\s+\d[^:\n]*)", ground)
        titles = {
            "LAYER 1": "Dörren",
            "LAYER 2": "Kartan",
            "LAYER 3": "Tre hypoteser",
            "LAYER 4": "Aktörerna",
            "LAYER 5": "Din makt",
        }

        if len(secs) > 1:
            i = 1
            while i < len(secs):
                h = secs[i].strip()
                c = secs[i + 1].strip() if i + 1 < len(secs) else ""
                k = h[:7].strip()
                st.markdown(
                    f'<div class="layer-card"><div class="layer-lbl">Layer {k[-1]}</div><div class="layer-ttl">{titles.get(k, _safe(h))}</div><div class="analysis-text">{_safe_links(c)}</div></div>',
                    unsafe_allow_html=True,
                )
                i += 2
        elif ground:
            st.markdown(
                f'<div class="layer-card"><div class="analysis-text">{_safe_links(ground)}</div></div>',
                unsafe_allow_html=True,
            )

    if not st.session_state.deep_generated:
        cl1, cl2 = st.columns([1, 3])
        with cl1:
            if st.button("🔬 Fördjupningar"):
                with st.spinner("Genererar fördjupningar..."):
                    from engine import deliver_deep_dives
                    dp = deliver_deep_dives(
                        r["question"],
                        r["claude_answer"],
                        r["gpt_answer"],
                        r["red_team_report"],
                        r["final_analysis"],
                        rc,
                    )
                    r["layers"].update(dp)
                    st.session_state.result = r
                    st.session_state.deep_generated = True
                    st.rerun()
        with cl2:
            st.caption("Historik + detaljerade linser + analytiker-output.")
    else:
        for k, lbl in [
            ("deep1", "🕰 Systemet bakåt i tiden"),
            ("deep2", "🔭 Tre linser i detalj"),
            ("deep3", "📋 Analytiker-output"),
        ]:
            val = _normalize_text_for_render(lyr.get(k, ""))
            with st.expander(lbl, expanded=False):
                st.markdown(f'<div class="analysis-text">{_safe_links(val)}</div>', unsafe_allow_html=True)

    st.markdown('<div style="border-top:1px solid var(--border);margin:1rem 0 .4rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:var(--mono);font-size:.52rem;letter-spacing:.28em;color:var(--ink4);text-transform:uppercase;margin-bottom:.4rem;">Maskinrummet — intern analyskedja</div>',
        unsafe_allow_html=True,
    )

    with st.expander("🔎 Reality Check — fullständig", expanded=False):
        st.markdown(
            f'<div class="analysis-text">{_safe_links(_normalize_text_for_render(rc.get("text","")))}</div>',
            unsafe_allow_html=True,
        )

    with st.expander("⚔️ GPT-4 Kritiker", expanded=False):
        st.markdown(
            f'<div class="analysis-text">{_safe_links(_normalize_text_for_render(r.get("gpt_answer","")))}</div>',
            unsafe_allow_html=True,
        )

    with st.expander("🎯 Red Team — fullständig rapport", expanded=False):
        st.markdown(
            f'<div class="analysis-text">{_safe_links(_normalize_text_for_render(r.get("red_team_report","")))}</div>',
            unsafe_allow_html=True,
        )

    if r.get("final_analysis"):
        revised_text = _normalize_text_for_render(r["final_analysis"])
        with st.expander("✏️ Reviderad analys", expanded=False):
            if revised_text.strip():
                st.markdown(
                    f'<div class="analysis-text">{_safe_links(revised_text)}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="font-family:var(--mono);font-size:.68rem;color:var(--ink4);padding:.6rem;text-align:center;">Ingen reviderad text genererades.</div>',
                    unsafe_allow_html=True,
                )

    st.markdown('<div style="border-top:1px solid var(--border);margin:1.5rem 0 .7rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:var(--mono);font-size:.52rem;letter-spacing:.28em;color:var(--ink4);text-transform:uppercase;margin-bottom:.4rem;">Export</div>',
        unsafe_allow_html=True,
    )

    slug = _slugify(r["question"])

    def _full(res):
        rc_ = res["reality_check"]
        ly = res.get("layers", {})
        parts = [
            f"{'='*70}\nSANNINGSMASKINEN v8.17b\n",
            f"Fråga: {res['question']}\nDatum: {today_str}\n",
            f"Status: {res['status']} | Reality: {rc_['status']}\n{'='*70}\n\n",
            f"REALITY CHECK\n{'-'*40}\n{rc_.get('text','')}\n\n",
            f"PRIMÄRANALYS\n{'-'*40}\n{res.get('claude_answer','')}\n\n",
        ]
        if ly.get("ground"):
            parts.append(f"LAYER 1-5\n{'-'*40}\n{ly['ground']}\n\n")
        for k, t in [("deep1", "FÖRDJUPNING 1"), ("deep2", "FÖRDJUPNING 2"), ("deep3", "FÖRDJUPNING 3")]:
            if ly.get(k):
                parts.append(f"{t}\n{'-'*40}\n{ly[k]}\n\n")
        parts.extend([
            f"GPT-4\n{'-'*40}\n{res.get('gpt_answer','')}\n\n",
            f"RED TEAM\n{'-'*40}\n{res.get('red_team_report','')}\n\n",
        ])
        if res.get("final_analysis"):
            parts.append(f"REVIDERAD\n{'-'*40}\n{res['final_analysis']}\n\n")
        parts.append(f"\n{'='*70}\nSanningen favoriserar ingen sida.")
        return "".join(parts)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.download_button(
            "📄 Hela analysen",
            _full(r).encode(),
            f"sanningsmaskinen_{today_str}_{slug}_full.txt",
            "text/plain",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "📄 Primäranalys",
            (r.get("claude_answer", "") or "").encode(),
            f"sanningsmaskinen_{today_str}_{slug}_analys.txt",
            "text/plain",
            use_container_width=True,
        )
    with c3:
        try:
            from pdf_export import build_pdf as _build_pdf
            st.download_button(
                "📄 PDF",
                _build_pdf(r),
                f"sanningsmaskinen_{today_str}_{slug}.pdf",
                "application/pdf",
                use_container_width=True,
            )
        except Exception:
            pass
    with c4:
        st.download_button(
            "📄 Reality Check",
            (rc.get("text", "") or "").encode(),
            f"sanningsmaskinen_{today_str}_{slug}_reality.txt",
            "text/plain",
            use_container_width=True,
        )

    st.markdown(
        f"""<div style="margin-top:1.5rem;padding-top:.5rem;border-top:1px solid var(--border);display:flex;justify-content:space-between;font-family:var(--mono);font-size:.55rem;color:var(--ink4);gap:1rem;flex-wrap:wrap;"><span>Sanningsmaskinen v8.17b · {today_str}</span><span>{_safe(rc_status)} · {_safe(res_status)}</span><span>Sanningen favoriserar ingen sida.</span></div>""",
        unsafe_allow_html=True,
    )

elif not st.session_state.running and not st.session_state.awaiting_confirm:
    steps_info = [
        ("Steg 0", "Reality Check — VERIFIED / ONGOING / HYPOTHETICAL / ANALYTICAL"),
        ("Steg 1", "Primäranalys — Claude Opus med tre hypoteser, bevis + falsifiering"),
        ("Steg 2", "GPT-4 destruktiv kritik — opponerar, sammanfattar inte"),
        ("Steg 3", "Konfliktanalys — epistemiska meningsskiljaktigheter"),
        ("Steg 4", "Red Team — VERDICT: HÅLLER / MODIFIERAS / KOLLAPSAR"),
        ("Steg 5", "Auto-rewrite om Red Team bedömer KOLLAPSAR eller MODIFIERAS"),
        ("Steg 6", "Layer 1–5 och fördjupningar — on-demand"),
    ]
    rows = "".join(
        f'<div class="empty-row"><span class="empty-step">{_safe(s)}</span><span class="empty-desc">{_safe(d)}</span></div>'
        for s, d in steps_info
    )
    st.markdown(
        f"""<div class="empty-state"><div class="empty-kw">HUR VERKTYGET FUNGERAR</div>{rows}<div class="empty-footer">Exempelfrågor · Vem sprängde Nord Stream? · Varför invaderade Ryssland Ukraina 2022? · Varför invaderade USA Irak 2003?</div></div>""",
        unsafe_allow_html=True,
    )