# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN v8.19 — STREAMLIT UI
Syfte:
- Behåll den mörka v8.18-designen
- Återställ ren analyskedja mellan engine -> normalizer -> UI
- UI får inte längre påverka scoring eller reality-klassificering
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
  --bg:#0b0b0c; --bg1:#0f0f11; --bg2:#131316; --bg3:#18181c;
  --border:#2b2e36; --border2:#3a3e49;
  --ink:#f0ebe3; --ink2:#d2cbc1; --ink3:#9d968b; --ink4:#6e675d;
  --grn:#3d9970; --grn-bg:#070e0b; --grn-dim:#1a3028;
  --amb:#c0882a; --amb-bg:#100d03; --amb-dim:#2a2010;
  --red:#c0442a; --red-bg:#100706; --red-dim:#2a1410;
  --blu:#4a7fc0; --blu-bg:#060b12; --blu-dim:#101830;
  --mono:'JetBrains Mono',monospace; --serif:'Spectral',serif; --sans:'Libre Franklin',sans-serif;
}
html, body, [class*="css"]{background:var(--bg);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased;}
*,*::before,*::after{box-sizing:border-box}
.main .block-container{max-width:1060px;padding:0 1.5rem 5.3rem;margin:0 auto}
div[data-testid="stAppViewContainer"]{background:var(--bg)}
div[data-testid="stSidebar"]{background:var(--bg1)}
#MainMenu, footer, header {visibility:hidden;}
a,a:visited{color:#6ca9ef!important;text-decoration:underline!important;pointer-events:auto!important;cursor:pointer!important;position:relative;z-index:8}
a:hover{color:#9cc7ff!important}
*{max-width:100%;word-break:normal!important;overflow-wrap:break-word!important;}
pre, code, .analysis-text{white-space:pre-wrap!important;word-break:normal!important;overflow-wrap:anywhere!important;}
.analysis-text a,.rc-col-source a,.nyckelord-tag,a[target="_blank"]{pointer-events:auto!important;cursor:pointer!important;position:relative;z-index:8}
div.stMarkdown p{margin:0}
.stCaption{color:var(--ink4)!important}

.topbar{display:flex;align-items:center;justify-content:space-between;padding:1rem 0 .75rem;border-bottom:1px solid var(--border);margin-bottom:1.15rem;}
.topbar-left{display:flex;align-items:baseline;gap:1rem}
.topbar-mark{font-family:var(--mono);font-size:.58rem;font-weight:600;letter-spacing:.35em;color:var(--ink3);text-transform:uppercase;}
.topbar-title{font-family:var(--serif);font-size:1rem;font-weight:600;color:var(--ink2);}
.topbar-right{font-family:var(--mono);font-size:.58rem;color:var(--ink4);letter-spacing:.08em;}
.topbar-sub{font-family:var(--mono);font-size:.58rem;color:var(--ink4);letter-spacing:.07em;padding:.35rem 0 .85rem;border-bottom:1px solid var(--border);margin-bottom:1rem;}

.stTextArea textarea{background:var(--bg2)!important;border:1px solid var(--border2)!important;border-radius:2px!important;color:var(--ink)!important;font-family:var(--serif)!important;font-size:1rem!important;line-height:1.6!important;padding:.78rem 1rem!important;}
.stTextArea textarea:focus{border-color:var(--blu)!important}
.stTextArea textarea::placeholder{color:var(--ink4)!important}

.stButton>button{background:var(--ink)!important;color:var(--bg)!important;border:none!important;border-radius:2px!important;font-family:var(--mono)!important;font-size:.63rem!important;font-weight:600!important;letter-spacing:.15em!important;padding:.5rem 1.2rem!important;text-transform:uppercase!important;transition:opacity .15s!important;}
.stButton>button:hover{opacity:.84!important}
.stButton>button:disabled{opacity:.3!important}

.step-row{display:flex;gap:.3rem;flex-wrap:wrap;margin:.8rem 0 1.15rem}
.step{font-family:var(--mono);font-size:.58rem;padding:.18rem .55rem;border:1px solid var(--border);color:var(--ink4);letter-spacing:.04em;background:transparent;}
.step-done{border-color:var(--grn-dim);color:var(--grn);background:var(--grn-bg)}
.step-active{border-color:var(--blu);color:var(--blu);background:var(--blu-bg)}
.step-warn{border-color:var(--red-dim);color:var(--red);background:var(--red-bg)}

.zone{border:1px solid var(--border);margin:.45rem 0;overflow:hidden;background:var(--bg1);}
.zone-header{font-family:var(--mono);font-size:.52rem;font-weight:600;letter-spacing:.28em;text-transform:uppercase;padding:.5rem 1rem;background:var(--bg2);border-bottom:1px solid var(--border);color:#bdb5aa;display:flex;align-items:center;justify-content:space-between;gap:1rem;}
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

.exec-conclusion{font-family:var(--serif);font-size:1.12rem;font-weight:600;color:#c7efd8;line-height:1.58;padding:1rem 1.1rem;border-left:4px solid var(--grn);background:var(--grn-bg);}
.exec-label{font-family:var(--mono);font-size:.48rem;letter-spacing:.3em;color:var(--grn);margin-bottom:.32rem;text-transform:uppercase;}
.exec-explanation{font-family:var(--sans);font-size:.9rem;color:var(--ink2);line-height:1.72;padding:.85rem 1.1rem;border-left:2px solid var(--border2);background:var(--bg2);}
.exec-conf{font-family:var(--mono);font-size:.5rem;color:var(--ink4);letter-spacing:.15em;padding:.5rem 1.1rem;background:var(--bg2);border-top:1px solid var(--border);text-align:right;}
.exec-falsif{border-top:1px solid var(--border);padding:.7rem 1rem;background:var(--bg2);display:flex;gap:.8rem;align-items:baseline;}
.exec-falsif-lbl{font-family:var(--mono);font-size:.48rem;letter-spacing:.2em;color:var(--ink4);white-space:nowrap;flex-shrink:0;}
.exec-falsif-txt{font-family:var(--sans);font-size:.78rem;color:#8a8ec9;line-height:1.55;}

.hyp-dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1px;background:var(--border);border-top:1px solid var(--border);}
.hyp-card{background:var(--bg1);padding:.85rem 1rem;position:relative;overflow:hidden}
.hyp-card-winner{border-left:3px solid var(--grn)}
.hyp-card-2{border-left:3px solid var(--amb)}
.hyp-card-3{border-left:3px solid var(--ink3)}
.hyp-card-rank{font-family:var(--mono);font-size:.48rem;color:var(--ink4);letter-spacing:.2em;margin-bottom:.2rem;text-transform:uppercase}
.hyp-card-key{font-family:var(--mono);font-size:.72rem;font-weight:700;letter-spacing:.06em;margin-bottom:.08rem}
.hyp-card-lbl{font-family:var(--mono);font-size:.52rem;letter-spacing:.12em;color:var(--ink3);margin-bottom:.4rem}
.hyp-card-title{font-family:var(--serif);font-size:.88rem;font-weight:600;color:var(--ink2);line-height:1.4;margin-bottom:.65rem}
.hyp-card-bar-wrap{display:flex;align-items:center;gap:.6rem;margin-bottom:.45rem}
.hyp-card-bar-track{flex:1;height:4px;background:var(--bg3);border-radius:2px;position:relative}
.hyp-card-bar-fill{position:absolute;left:0;top:0;height:100%;border-radius:2px}
.hyp-card-pct{font-family:var(--mono);font-size:.65rem;font-weight:700;min-width:2.5rem;text-align:right}
.hyp-card-meta{font-family:var(--mono);font-size:.5rem;color:var(--ink4);display:flex;gap:.6rem;flex-wrap:wrap}
.hyp-card-tes{font-family:var(--sans);font-size:.77rem;color:var(--ink2);line-height:1.58;margin-top:.5rem;padding-top:.5rem;border-top:1px solid var(--border);}

.nyckelord-strip{display:flex;gap:.4rem;flex-wrap:wrap;padding:.55rem 1rem;background:var(--bg2);border-top:1px solid var(--border)}
.nyckelord-label{font-family:var(--mono);font-size:.48rem;color:var(--ink4);letter-spacing:.2em;align-self:center;white-space:nowrap}
.nyckelord-tag{font-family:var(--mono);font-size:.6rem;color:var(--blu);border:1px solid var(--blu-dim);background:var(--blu-bg);padding:.12rem .5rem;text-decoration:none;letter-spacing:.04em}
.metod-strip{font-family:var(--mono);font-size:.56rem;color:var(--ink4);background:var(--bg2);border-top:1px solid var(--border);padding:.5rem 1rem;line-height:1.7;letter-spacing:.02em}

.rc-table{width:100%;border-collapse:collapse}
.rc-table td{padding:.45rem .65rem;border-bottom:1px solid var(--border);font-family:var(--sans);font-size:.77rem;vertical-align:top}
.rc-table tr:last-child td{border-bottom:none}
.rc-col-label{font-family:var(--mono);font-size:.48rem;color:var(--ink4);letter-spacing:.2em;white-space:nowrap;min-width:60px}
.rc-col-claim{color:var(--ink2);line-height:1.55}
.rc-col-status{white-space:nowrap}
.rc-col-source{color:#c8d8ff;font-size:.74rem;line-height:1.6}
.rc-st-v{color:var(--grn);font-family:var(--mono);font-size:.6rem;font-weight:600}
.rc-st-d{color:var(--amb);font-family:var(--mono);font-size:.6rem;font-weight:600}
.rc-st-u{color:var(--red);font-family:var(--mono);font-size:.6rem;font-weight:600}
.rc-st-n{color:var(--ink3);font-family:var(--mono);font-size:.6rem}

.hyp-detail-label{font-family:var(--mono);font-size:.52rem;letter-spacing:.28em;color:var(--ink4);text-transform:uppercase;padding:1rem 0 .3rem;border-top:1px solid var(--border);margin-top:.8rem;}
.hyp-det-header{padding:.65rem 1rem;border-bottom:1px solid var(--border);background:var(--bg2)}
.hyp-det-key{font-family:var(--mono);font-size:.68rem;font-weight:700;letter-spacing:.06em}
.hyp-det-title{font-family:var(--serif);font-size:.92rem;font-weight:600;color:var(--ink2);line-height:1.4}
.hyp-det-scores{display:flex;align-items:center;gap:.8rem;margin-top:.35rem;flex-wrap:wrap}
.hyp-det-bar-track{width:120px;height:4px;background:var(--bg3);border-radius:2px;position:relative}
.hyp-det-bar-fill{position:absolute;left:0;top:0;height:100%;border-radius:2px}
.hyp-det-score{font-family:var(--mono);font-size:.65rem;font-weight:600}
.hyp-det-styrka{font-family:var(--mono);font-size:.52rem;letter-spacing:.1em;color:var(--ink4)}
.hyp-sec-lbl{font-family:var(--mono);font-size:.5rem;letter-spacing:.2em;text-transform:uppercase;color:var(--ink4);margin-bottom:.25rem}
.hyp-sec-empty{font-family:var(--mono);font-size:.62rem;color:var(--ink4);font-style:italic;padding:.2rem .5rem}
.hyp-tes{font-family:var(--sans);font-size:.82rem;color:#8fd0a9;line-height:1.6;padding:.45rem .72rem;border-left:2px solid var(--grn-dim);background:var(--grn-bg)}
.hyp-ev-list{list-style:none;padding:0;margin:0}
.hyp-ev-list li{font-family:var(--sans);font-size:.78rem;color:var(--ink2);line-height:1.55;padding:.3rem .72rem;border-left:2px solid var(--grn-dim);background:var(--grn-bg);margin-bottom:.15rem;display:flex;gap:.4rem;align-items:baseline}
.hyp-ev-list li::before{content:"•";color:var(--grn);flex-shrink:0}
.hyp-mo{font-family:var(--sans);font-size:.78rem;color:#d29a8e;line-height:1.55;padding:.3rem .72rem;border-left:2px solid var(--red-dim);background:var(--red-bg);margin-bottom:.15rem}
.hyp-fl{font-family:var(--sans);font-size:.78rem;color:#8f95d8;line-height:1.55;padding:.32rem .72rem;border-left:2px solid var(--blu-dim);background:var(--blu-bg)}

.primary-card{border:1px solid var(--border);margin-top:.75rem;background:var(--bg1)}
.primary-head{background:var(--bg2);padding:.55rem 1rem;border-bottom:1px solid var(--border);font-family:var(--mono);font-size:.63rem;color:var(--ink2);letter-spacing:.04em;text-transform:none}
.primary-intro{padding:.95rem 1rem .7rem;background:var(--bg2);border-bottom:1px solid var(--border)}
.primary-intro-k{font-family:var(--mono);font-size:.48rem;letter-spacing:.25em;color:var(--ink4);margin-bottom:.4rem;text-transform:uppercase}
.primary-intro-t{font-family:var(--sans);font-size:.84rem;color:var(--ink2);line-height:1.72}
.analysis-text{font-family:var(--sans);font-size:.82rem;line-height:1.82;color:var(--ink2)}
.analysis-text a{color:#6ca9ef;text-decoration:underline}

.verdict{border:1px solid;padding:.9rem 1rem;margin:.5rem 0;display:flex;align-items:center;gap:1rem}
.verdict-grn{border-color:var(--grn-dim);background:var(--grn-bg)}
.verdict-amb{border-color:var(--amb-dim);background:var(--amb-bg)}
.verdict-red{border-color:var(--red-dim);background:var(--red-bg)}
.verdict-icon{font-family:var(--mono);font-size:1.3rem}
.verdict-label{font-family:var(--mono);font-size:.5rem;letter-spacing:.25em;color:var(--ink4);margin-bottom:.2rem}
.verdict-text{font-family:var(--serif);font-size:.95rem;font-weight:600}
.verdict-grn .verdict-text{color:#80c89a}
.verdict-amb .verdict-text{color:#d2b16a}
.verdict-red .verdict-text{color:#d38b7a}

.conflict-line{font-size:.79rem;color:var(--ink2);padding:.28rem 0;border-bottom:1px solid var(--border);line-height:1.55}
.conflict-line:last-child{border-bottom:none}

.layer-card{border:1px solid var(--border);padding:.9rem 1rem;margin-bottom:.4rem;background:var(--bg1)}
.layer-lbl{font-family:var(--mono);font-size:.5rem;color:var(--ink4);letter-spacing:.2em;margin-bottom:.2rem}
.layer-ttl{font-family:var(--serif);font-size:.88rem;color:var(--ink2);font-weight:600;margin-bottom:.6rem;padding-bottom:.35rem;border-bottom:1px solid var(--border)}

.degraded{border:1px solid var(--red-dim);border-left:3px solid var(--red);background:var(--red-bg);padding:.75rem 1rem;margin:.6rem 0;font-family:var(--mono);font-size:.65rem;color:#e29a8f;line-height:1.7}
.empty-state{margin-top:2rem;padding:2rem;border:1px solid var(--border);background:var(--bg1)}
.empty-kw{font-family:var(--mono);font-size:.52rem;letter-spacing:.3em;color:var(--ink4);margin-bottom:.9rem}
.empty-row{display:flex;gap:1rem;padding:.4rem 0;border-bottom:1px solid var(--border);font-size:.8rem}
.empty-step{font-family:var(--mono);font-size:.6rem;color:var(--ink4);min-width:4.5rem;padding-top:.05rem}
.empty-desc{color:var(--ink3);line-height:1.5}
.empty-footer{font-family:var(--mono);font-size:.58rem;color:var(--ink4);margin-top:.9rem;letter-spacing:.05em}

div[data-testid="stExpander"]>div:first-child{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:0!important;font-family:var(--mono)!important;font-size:.63rem!important;color:var(--ink2)!important}
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
    return re.sub(
        r'(?<!\]\()(?<!href=")(https?://[^\s<]+)',
        lambda m: f"[{m.group(0)}]({m.group(0)})",
        text,
    )


def _safe_links(text: str) -> str:
    if not text:
        return ""
    text = _autolink_raw_urls(text)
    links = {}

    def _stash_md(m):
        key = f"\x00L{len(links)}\x00"
        links[key] = f'<a href="{m.group(2)}" target="_blank" rel="noopener noreferrer">{_safe(m.group(1))}</a>'
        return key

    t2 = re.sub(r"\[([^\]]+)\]\((https?://[^\s\)]+)\)", _stash_md, text)
    t2 = _safe(t2)
    for key, html in links.items():
        t2 = t2.replace(key, html)
    return t2.replace("\n", "<br>")


def _looks_hypothetical(question: str) -> bool:
    q = (question or "").lower().strip()
    markers = [
        "tänk om", "vad skulle hända", "hypotetiskt",
        "kontrafaktiskt", "föreställ dig", "antag att"
    ]
    return any(m in q for m in markers) or q.startswith("om ")


def _looks_analytical(question: str) -> bool:
    q = (question or "").lower()
    markers = [
        "vad driver", "vilka är de verkliga strategiska orsakerna", "vad ligger bakom",
        "hur påverkar", "vad förklarar", "relation mellan", "över tid", "mellan 20",
        "historiskt mönster", "strukturell", "geopolit", "jämfört med"
    ]
    return any(m in q for m in markers)


def _effective_reality(question: str, rc: dict) -> dict:
    """
    UI-korrigering endast för visning.
    Får inte användas inne i motorflödet före ask_claude().
    """
    rc = dict(rc or {})
    status = (rc.get("status", "") or "").upper()
    text = rc.get("text", "") or ""
    if status == "HYPOTHETICAL" and _looks_analytical(question) and not _looks_hypothetical(question):
        rc["status"] = "ANALYTICAL"
        prefix = "[UI-KORRIGERING] Reality check klassade frågan som hypotetisk, men frågetypen är analytisk/strukturell. Visas därför som ANALYTICAL i gränssnittet.\n\n"
        if prefix not in text:
            rc["text"] = prefix + text
    return rc


def _strip_meta_lines(text: str) -> str:
    if not text:
        return ""
    lines = []
    seen = set()
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            lines.append("")
            continue
        up = s.upper()
        if any(x in up for x in [
            "LÅT MIG FÖRST SÖKA", "HÄR ÄR MIN ANALYS", "SANNINGSMASKINEN V8.",
            "REALITY CHECK STATUS", "REALITY CHECK:", "PRIMÄRANALYS",
            "CLAUDE OPUS RÅTEXT", "MASKINRUMMET", "INTERNS ANALYSKEDJA"
        ]):
            continue
        if s in seen and len(s) > 40:
            continue
        seen.add(s)
        lines.append(raw)
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _first_complete_sentence(text: str, fallback_chars: int = 220) -> str:
    s = re.sub(r"\s+", " ", (text or "")).strip()
    if not s:
        return ""
    m = re.search(r"^(.{40,}?[\.\!\?])(?:\s|$)", s)
    if m:
        return m.group(1).strip()
    cut = s[:fallback_chars].rsplit(" ", 1)[0].strip()
    return cut + ("…" if cut and not cut.endswith(("…", ".", "!", "?")) else "")


def _normalize_text_for_render(text: str) -> str:
    if not text:
        return ""
    try:
        from normalizer import normalize_references
        return normalize_references(text)
    except Exception:
        return text


def _extract_revised_summary(text: str) -> str:
    t = _strip_meta_lines(_normalize_text_for_render(text))
    if not t:
        return ""
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    body = []
    for ln in lines:
        if ln.startswith("#"):
            continue
        if len(ln) < 20:
            continue
        body.append(ln)
        if len(" ".join(body)) > 260:
            break
    return _first_complete_sentence(" ".join(body), 260)


def _final_summary_from_result(result: dict, ranked: list) -> str:
    revised = _extract_revised_summary(result.get("final_analysis", ""))
    if revised:
        return revised
    if ranked:
        winner = ranked[0]
        tes = _strip_meta_lines(winner.get("tes", ""))
        if tes:
            return _first_complete_sentence(tes, 260)
    raw = _strip_meta_lines(result.get("claude_answer", ""))
    return _first_complete_sentence(raw, 260)


def _dedupe_prefix_blocks(text: str, question: str = "") -> str:
    """
    Endast för rendering/export.
    Använd inte före normalizer/scoring.
    """
    if not text:
        return ""
    t = _strip_meta_lines(text)
    q = (question or "").strip()
    if q:
        t = re.sub(re.escape(q) + r'(\n\s*' + re.escape(q) + r')+', q, t, flags=re.IGNORECASE)
    lines = t.splitlines()
    out = []
    prev = ""
    for ln in lines:
        if ln.strip() and ln.strip() == prev.strip() and len(ln.strip()) > 30:
            continue
        out.append(ln)
        if ln.strip():
            prev = ln
    t = "\n".join(out)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _render_analysis_text(text: str, question: str = "") -> str:
    t = _dedupe_prefix_blocks(_normalize_text_for_render(text), question)
    return f'<div class="analysis-text">{_safe_links(t)}</div>'


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


def _friendly_label(label: str, fallback_title: str = "") -> str:
    mapping = {
        "STRUKTURELL": "Strukturell förklaring",
        "DOMESTIC POLITICS": "Inrikespolitik",
        "AKTÖRPSYKOLOGI": "Aktörspsykologi",
        "STRUKTURELL FÖRKLARING": "Strukturell förklaring",
    }
    key = (label or "").strip().upper()
    return mapping.get(key, label or fallback_title or "Förklaring")


STYRKA_COLOR = {
    "HÖG": "#3d9970",
    "MEDEL-HÖG": "#6daa50",
    "MEDEL": "#4a7fc0",
    "LÅG": "#c0442a",
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
def render_reality_zone(question: str, rc: dict) -> str:
    rc = _effective_reality(question, rc or {})
    status = (rc.get("status") or "").upper()
    text = rc.get("text") or ""
    pill_cls, pill_txt = REALITY_PILL.get(status, ("dim", status or "UNKNOWN"))
    body = _render_analysis_text(text, question)
    return _section_zone(
        "REALITY CHECK",
        body,
        accent="blu",
        right_html=_pill(pill_txt, pill_cls),
    )


def render_hyp_dashboard(ranked: list) -> str:
    if not ranked:
        return ""
    cards = []
    for i, h in enumerate(ranked[:3], start=1):
        key = h.get("key", f"H{i}")
        title = _friendly_label(h.get("label", ""), h.get("title", ""))
        pct = int(round((h.get("probability", 0) or 0) * 100))
        strength = (h.get("styrka") or "").upper()
        color = STYRKA_COLOR.get(strength, "#4a7fc0")
        cls = "hyp-card-winner" if i == 1 else ("hyp-card-2" if i == 2 else "hyp-card-3")

        tes = _strip_meta_lines(h.get("tes", ""))
        tes_html = f'<div class="hyp-card-tes">{_safe_links(tes)}</div>' if tes else ""

        cards.append(f"""
<div class="hyp-card {cls}">
  <div class="hyp-card-rank">RANK {i}</div>
  <div class="hyp-card-key">{_safe(key)}</div>
  <div class="hyp-card-lbl">{_safe(title)}</div>
  <div class="hyp-card-bar-wrap">
    <div class="hyp-card-bar-track">
      <div class="hyp-card-bar-fill" style="width:{pct}%;background:{color};"></div>
    </div>
    <div class="hyp-card-pct">{pct}%</div>
  </div>
  <div class="hyp-card-meta">
    <span>STYRKA: { _safe(strength or "—") }</span>
  </div>
  {tes_html}
</div>
""")
    return '<div class="hyp-dashboard">' + "".join(cards) + "</div>"


def render_exec_zone(summary: str, explanation: str, confidence: str, falsif: str) -> str:
    return _section_zone(
        "SLUTSATS",
        f"""
<div class="exec-label">Executive Summary</div>
<div class="exec-conclusion">{_safe(summary)}</div>
<div class="exec-explanation">{_safe_links(explanation)}</div>
<div class="exec-conf">{_safe(confidence)}</div>
<div class="exec-falsif">
  <div class="exec-falsif-lbl">FALSIFIERBARHET</div>
  <div class="exec-falsif-txt">{_safe_links(falsif)}</div>
</div>
""",
        accent="grn",
    )


def render_primary_analysis(question: str, text: str) -> str:
    clean = _dedupe_prefix_blocks(text, question)
    body = _render_analysis_text(clean, question)
    return _section_zone(
        "PRIMÄR ANALYS",
        body,
        accent="blu",
    )


def render_hyp_detail(ranked: list) -> str:
    if not ranked:
        return ""
    blocks = []
    for i, h in enumerate(ranked, start=1):
        key = h.get("key", f"H{i}")
        title = _friendly_label(h.get("label", ""), h.get("title", ""))
        pct = int(round((h.get("probability", 0) or 0) * 100))
        strength = (h.get("styrka") or "").upper()
        color = STYRKA_COLOR.get(strength, "#4a7fc0")

        tes = _strip_meta_lines(h.get("tes", ""))
        evid = h.get("evidence", []) or []
        mot = h.get("mot", []) or []
        fl = h.get("falsifier", []) or []

        evid_html = "".join(f"<li>{_safe_links(e)}</li>" for e in evid) or '<div class="hyp-sec-empty">—</div>'
        mot_html = "".join(f'<div class="hyp-mo">{_safe_links(m)}</div>' for m in mot) or '<div class="hyp-sec-empty">—</div>'
        fl_html = "".join(f'<div class="hyp-fl">{_safe_links(f)}</div>' for f in fl) or '<div class="hyp-sec-empty">—</div>'

        blocks.append(f"""
<div class="layer-card">
  <div class="hyp-det-header">
    <div class="hyp-det-key">{_safe(key)}</div>
    <div class="hyp-det-title">{_safe(title)}</div>
    <div class="hyp-det-scores">
      <div class="hyp-det-bar-track">
        <div class="hyp-det-bar-fill" style="width:{pct}%;background:{color};"></div>
      </div>
      <div class="hyp-det-score">{pct}%</div>
      <div class="hyp-det-styrka">{_safe(strength)}</div>
    </div>
  </div>

  <div class="hyp-sec-lbl">TES</div>
  <div class="hyp-tes">{_safe_links(tes)}</div>

  <div class="hyp-sec-lbl">EVIDENCE</div>
  <ul class="hyp-ev-list">{evid_html}</ul>

  <div class="hyp-sec-lbl">MOTBEVIS</div>
  {mot_html}

  <div class="hyp-sec-lbl">FALSIFIERBARHET</div>
  {fl_html}
</div>
""")
    return _section_zone(
        "HYPOTESER — DETALJ",
        "".join(blocks),
        accent="amb",
    )


def render_conflicts(conflicts: list) -> str:
    if not conflicts:
        return ""
    rows = "".join(f'<div class="conflict-line">{_safe_links(c)}</div>' for c in conflicts)
    return _section_zone(
        "KONFLIKTER I DATA",
        rows,
        accent="red",
    )
from engine import run_full_pipeline


st.markdown(
"""
<div class="topbar">
  <div class="topbar-left">
    <div class="topbar-mark">SANNINGSMASKINEN</div>
    <div class="topbar-title">Systemisk analysmotor</div>
  </div>
  <div class="topbar-right">v8.19</div>
</div>
<div class="topbar-sub">Systemisk verklighetsanalys • Hypotesranking • Evidensbaserad syntes</div>
""",
unsafe_allow_html=True,
)


question = st.text_area(
    "Fråga",
    height=120,
    placeholder="Skriv en fråga om verkligheten, geopolitik, historia eller ett påstående som ska analyseras…",
)

run = st.button("Analysera")

if "result" not in st.session_state:
    st.session_state.result = None

if run and question.strip():

    steps = [
        ("REALITY CHECK", "active"),
        ("HYPOTESER", ""),
        ("EVIDENS", ""),
        ("SYNTES", ""),
    ]

    step_container = st.empty()
    step_container.markdown(step_html(steps), unsafe_allow_html=True)

    with st.spinner("Analyserar..."):
        result = run_full_pipeline(question)

    st.session_state.result = result

    steps = [
        ("REALITY CHECK", "done"),
        ("HYPOTESER", "done"),
        ("EVIDENS", "done"),
        ("SYNTES", "done"),
    ]

    step_container.markdown(step_html(steps), unsafe_allow_html=True)


result = st.session_state.result

if result:

    rc = result.get("reality_check", {})
    ranked = result.get("ranked_hypotheses", []) or []
    conflicts = result.get("conflicts", []) or []

    summary = _final_summary_from_result(result, ranked)
    explanation = _strip_meta_lines(result.get("final_analysis", ""))
    confidence = result.get("confidence", "Confidence: —")
    falsif = result.get("falsifier", "—")

    st.markdown(
        render_reality_zone(question, rc),
        unsafe_allow_html=True,
    )

    dash = render_hyp_dashboard(ranked)
    if dash:
        st.markdown(dash, unsafe_allow_html=True)

    st.markdown(
        render_exec_zone(summary, explanation, confidence, falsif),
        unsafe_allow_html=True,
    )

    primary = result.get("claude_answer", "")
    if primary:
        st.markdown(
            render_primary_analysis(question, primary),
            unsafe_allow_html=True,
        )

    detail = render_hyp_detail(ranked)
    if detail:
        st.markdown(detail, unsafe_allow_html=True)

    conflict_html = render_conflicts(conflicts)
    if conflict_html:
        st.markdown(conflict_html, unsafe_allow_html=True)


else:

    st.markdown(
"""
<div class="empty-state">
<div class="empty-kw">SYSTEMFLÖDE</div>

<div class="empty-row">
<div class="empty-step">STEP 1</div>
<div class="empty-desc">Reality check – avgör om frågan är verifierbar, analytisk eller hypotetisk</div>
</div>

<div class="empty-row">
<div class="empty-step">STEP 2</div>
<div class="empty-desc">Hypotesgenerering – flera förklaringsmodeller genereras</div>
</div>

<div class="empty-row">
<div class="empty-step">STEP 3</div>
<div class="empty-desc">Evidensanalys – varje hypotes testas mot kända data</div>
</div>

<div class="empty-row">
<div class="empty-step">STEP 4</div>
<div class="empty-desc">Syntes – sannolikhetsranking och slutlig analys</div>
</div>

<div class="empty-footer">
SANNINGSMASKINEN analyserar strukturer, makt, evidens och motbevis.
</div>
</div>
""",
        unsafe_allow_html=True,
    )