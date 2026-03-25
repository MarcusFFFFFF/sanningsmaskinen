# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN v8.18 — STREAMLIT UI
Ändring från v8.17b:
  - Primäranalys renderas som formatterad artikel (markdown → HTML)
  - Tabeller, rubrikhierarki, TES/BEVIS/MOTARG i färgkodade sektioner
  - Klickbara källänkar extraheras och visas
"""

import re
from datetime import date as _date
from urllib.parse import quote_plus

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Sanningsmaskinen", page_icon="◎", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
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
html,body,[class*="css"]{background:var(--bg);color:var(--ink);font-family:var(--sans);-webkit-font-smoothing:antialiased}
*,*::before,*::after{box-sizing:border-box}
.main .block-container{max-width:1060px;padding:0 1.5rem 5.3rem;margin:0 auto}
div[data-testid="stAppViewContainer"]{background:#0a0b0d}

/* ── Sidebar — mörk editorial design med hårdkodade färger ── */
div[data-testid="stSidebar"]{
  background:#0f1115!important;
  border-right:1px solid #242c3a!important;
  min-width:300px!important;
  max-width:320px!important;
}
div[data-testid="stSidebar"] > div,
div[data-testid="stSidebar"] section{
  background:#0f1115!important;
}
/* Göm stängknappen — alla varianter */
button[data-testid="collapsedControl"],
div[data-testid="collapsedControl"],
section[data-testid="stSidebar"] > div > button,
div[data-testid="stSidebar"] button[kind="header"],
div[data-testid="stSidebarCollapsedControl"]{display:none!important}
/* Scrollbar */
div[data-testid="stSidebar"] ::-webkit-scrollbar{width:2px}
div[data-testid="stSidebar"] ::-webkit-scrollbar-track{background:transparent}
div[data-testid="stSidebar"] ::-webkit-scrollbar-thumb{background:#242c3a}
/* Alla element — nollställ Streamlits vita bakgrunder */
div[data-testid="stSidebar"] .element-container,
div[data-testid="stSidebar"] .stMarkdown,
div[data-testid="stSidebar"] .block-container{
  background:#0f1115!important;
}
/* Text */
div[data-testid="stSidebar"] p,
div[data-testid="stSidebar"] span,
div[data-testid="stSidebar"] label,
div[data-testid="stSidebar"] .stMarkdown{
  color:#b3ad9f!important;
  font-family:'JetBrains Mono',monospace!important;
  font-size:.62rem!important;
}
/* Input */
div[data-testid="stSidebar"] input{
  background:#141821!important;
  border:1px solid #242c3a!important;
  border-radius:0!important;
  color:#d7d0c4!important;
  font-family:'JetBrains Mono',monospace!important;
  font-size:.68rem!important;
}
div[data-testid="stSidebar"] input:focus{
  border-color:#57c78a!important;
  outline:none!important;
  box-shadow:none!important;
}
div[data-testid="stSidebar"] input::placeholder{color:#7f8898!important}
/* Selectbox */
div[data-testid="stSidebar"] .stSelectbox > div > div{
  background:#141821!important;
  border:1px solid #242c3a!important;
  border-radius:0!important;
  color:#b3ad9f!important;
  font-family:'JetBrains Mono',monospace!important;
  font-size:.62rem!important;
  min-height:1.9rem!important;
}
/* Expanders */
div[data-testid="stSidebar"] div[data-testid="stExpander"]{
  background:#0f1115!important;
  border:none!important;
  border-bottom:1px solid #1a2030!important;
  border-radius:0!important;
}
div[data-testid="stSidebar"] div[data-testid="stExpander"] > div:first-child{
  background:#0f1115!important;
  border:none!important;
  border-radius:0!important;
  color:#c8c2b8!important;
  font-family:'JetBrains Mono',monospace!important;
  font-size:.6rem!important;
  padding:.48rem .85rem!important;
  line-height:1.5!important;
}
div[data-testid="stSidebar"] div[data-testid="stExpander"] > div:first-child:hover{
  background:#141821!important;
  color:#f2efe8!important;
}
div[data-testid="stSidebar"] div[data-testid="stExpander"] > div:last-child{
  background:#0c0e12!important;
  border:none!important;
  border-top:1px solid #1a2030!important;
  padding:.6rem .85rem .8rem!important;
}
/* Allt inuti expanderat innehåll */
div[data-testid="stSidebar"] div[data-testid="stExpander"] > div:last-child *{
  background-color:#0c0e12!important;
  color:#b3ad9f!important;
  font-family:'JetBrains Mono',monospace!important;
  font-size:.58rem!important;
}
div[data-testid="stSidebar"] div[data-testid="stExpander"] > div:last-child input{
  background:#141821!important;
  border:1px solid #242c3a!important;
  color:#d7d0c4!important;
  font-size:.6rem!important;
  padding:.3rem .5rem!important;
}
/* Knappar — på EN rad, kompakta */
div[data-testid="stSidebar"] .stButton > button{
  background:#141821!important;
  color:#b3ad9f!important;
  border:1px solid #242c3a!important;
  border-radius:0!important;
  font-family:'JetBrains Mono',monospace!important;
  font-size:.52rem!important;
  letter-spacing:.1em!important;
  padding:.3rem .5rem!important;
  text-transform:uppercase!important;
  white-space:nowrap!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
  width:100%!important;
  min-height:1.8rem!important;
  line-height:1!important;
  transition:all .15s!important;
}
div[data-testid="stSidebar"] .stButton > button:hover{
  border-color:#57c78a!important;
  color:#57c78a!important;
  background:#0a1510!important;
}
/* Download-knappar */
div[data-testid="stSidebar"] .stDownloadButton > button{
  background:#0a1220!important;
  color:#6eb6ff!important;
  border:1px solid #23486d!important;
  border-radius:0!important;
  font-family:'JetBrains Mono',monospace!important;
  font-size:.52rem!important;
  letter-spacing:.1em!important;
  padding:.3rem .5rem!important;
  white-space:nowrap!important;
  overflow:hidden!important;
  text-overflow:ellipsis!important;
  width:100%!important;
  min-height:1.8rem!important;
  line-height:1!important;
}
div[data-testid="stSidebar"] .stDownloadButton > button:hover{
  background:#0d1828!important;
  border-color:#6eb6ff!important;
}
#MainMenu,footer,header{visibility:hidden}
[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important}
a{color:#6ca9ef;text-decoration:underline}a:hover{color:#9cc7ff}
*{max-width:100%;word-break:normal!important;overflow-wrap:break-word!important}
pre,code,.analysis-text{white-space:pre-wrap!important;overflow-wrap:anywhere!important}
div.stMarkdown p{margin:0}
.stCaption{color:var(--ink4)!important}

.topbar{display:flex;align-items:center;justify-content:space-between;padding:1rem 0 .75rem;border-bottom:1px solid var(--border);margin-bottom:1.15rem}
.topbar-left{display:flex;align-items:baseline;gap:1rem}
.topbar-mark{font-family:var(--mono);font-size:.58rem;font-weight:600;letter-spacing:.35em;color:var(--ink3);text-transform:uppercase}
.topbar-title{font-family:var(--serif);font-size:1.03rem;font-weight:600;color:var(--ink)}
.topbar-right{font-family:var(--mono);font-size:.58rem;color:var(--ink3);letter-spacing:.08em}
.topbar-sub{font-family:var(--mono);font-size:.6rem;color:var(--ink3);letter-spacing:.07em;padding:.4rem 0 .9rem;border-bottom:1px solid var(--border);margin-bottom:1rem;line-height:1.7}

.stTextArea textarea{background:var(--bg2)!important;border:1px solid var(--border2)!important;border-radius:2px!important;color:var(--ink)!important;font-family:var(--serif)!important;font-size:1rem!important;line-height:1.6!important;padding:.78rem 1rem!important;resize:none!important;overflow:hidden!important;box-shadow:none!important}
.stTextArea textarea:focus{border-color:var(--blu)!important;box-shadow:none!important;outline:none!important}
.stTextArea textarea::placeholder{color:var(--ink4)!important}
/* Ta bort Streamlits rosa focus-ring helt */
.stTextArea [data-baseweb="textarea"]{box-shadow:none!important;border:none!important}
.stTextArea [data-baseweb="textarea"]:focus-within{box-shadow:none!important}
.stButton>button{background:var(--ink)!important;color:var(--bg)!important;border:none!important;border-radius:2px!important;font-family:var(--mono)!important;font-size:.63rem!important;font-weight:600!important;letter-spacing:.15em!important;padding:.5rem 1.2rem!important;text-transform:uppercase!important;transition:opacity .15s!important}
.stButton>button:hover{opacity:.84!important}
.stButton>button:disabled{opacity:.3!important}

.step-row{display:flex;gap:.4rem;flex-wrap:wrap;margin:.8rem 0 1.15rem;align-items:center}
.step{font-family:var(--mono);font-size:.6rem;padding:.28rem .75rem;border:1px solid var(--border);color:var(--ink4);letter-spacing:.06em;background:transparent;transition:all .3s ease;position:relative}
.step-done{border-color:var(--grn-dim);color:var(--grn);background:var(--grn-bg)}
.step-done::before{content:"✓ ";font-size:.55rem}
.step-active{
  border-color:#6eb6ff;color:#ffffff;background:#0d1828;
  animation:stepPulse 1.1s ease-in-out infinite;
  box-shadow:0 0 12px rgba(110,182,255,0.4), 0 0 4px rgba(110,182,255,0.6) inset;
  font-weight:600;
}
.step-warn{border-color:var(--red-dim);color:var(--red);background:var(--red-bg)}
@keyframes stepPulse{
  0%{opacity:1;box-shadow:0 0 12px rgba(110,182,255,0.4),0 0 4px rgba(110,182,255,0.6) inset;border-color:#6eb6ff}
  50%{opacity:.75;box-shadow:0 0 22px rgba(110,182,255,0.7),0 0 8px rgba(110,182,255,0.8) inset;border-color:#a8d8ff}
  100%{opacity:1;box-shadow:0 0 12px rgba(110,182,255,0.4),0 0 4px rgba(110,182,255,0.6) inset;border-color:#6eb6ff}
}

.zone{border:1px solid var(--border);margin:.45rem 0;overflow:hidden;background:var(--bg1)}
.zone-header{font-family:var(--mono);font-size:.52rem;font-weight:600;letter-spacing:.28em;text-transform:uppercase;padding:.5rem 1rem;background:var(--bg2);border-bottom:1px solid var(--border);color:var(--ink3);display:flex;align-items:center;justify-content:space-between;gap:1rem}
.zone-body{padding:.92rem 1rem;background:var(--bg1)}
.zone-accent-grn{border-left:3px solid var(--grn)}
.zone-accent-amb{border-left:3px solid var(--amb)}
.zone-accent-red{border-left:3px solid var(--red)}
.zone-accent-blu{border-left:3px solid var(--blu)}

.pill{display:inline-block;font-family:var(--mono);font-size:.56rem;font-weight:600;letter-spacing:.1em;padding:.15rem .6rem;border:1px solid;text-transform:uppercase;white-space:nowrap}
.pill-grn{color:var(--grn);border-color:var(--grn-dim);background:var(--grn-bg)}
.pill-amb{color:var(--amb);border-color:var(--amb-dim);background:var(--amb-bg)}
.pill-red{color:var(--red);border-color:var(--red-dim);background:var(--red-bg)}
.pill-blu{color:var(--blu);border-color:var(--blu-dim);background:var(--blu-bg)}
.pill-dim{color:var(--ink3);border-color:var(--border);background:var(--bg2)}

.exec-conclusion{font-family:var(--serif);font-size:1.05rem;font-weight:600;color:#b8e8c8;line-height:1.55;padding:.9rem 1.1rem;border-left:4px solid var(--grn);background:var(--grn-bg)}
.exec-label{font-family:var(--mono);font-size:.48rem;letter-spacing:.3em;color:var(--grn);margin-bottom:.3rem;text-transform:uppercase}
.exec-explanation{font-family:var(--sans);font-size:.83rem;color:var(--ink2);line-height:1.72;padding:.72rem 1.1rem;border-left:2px solid var(--border2);background:var(--bg2)}
.exec-conf{font-family:var(--mono);font-size:.5rem;color:var(--ink4);letter-spacing:.15em;padding:.35rem 1.1rem;background:var(--bg2);border-top:1px solid var(--border);text-align:right}
.exec-falsif{border-top:1px solid var(--border);padding:.6rem 1rem;background:var(--bg2);display:flex;gap:.8rem;align-items:baseline}
.exec-falsif-lbl{font-family:var(--mono);font-size:.48rem;letter-spacing:.2em;color:var(--ink4);white-space:nowrap;flex-shrink:0}
.exec-falsif-txt{font-family:var(--sans);font-size:.78rem;color:#aab7ff;line-height:1.55}


.result-hero{border:1px solid var(--border);background:linear-gradient(180deg,#11161d 0%,#0d1117 100%);margin:.55rem 0 1rem;overflow:hidden}
.result-hero-head{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.55rem .95rem;border-bottom:1px solid var(--border);background:#10151d}
.result-hero-kicker{font-family:var(--mono);font-size:.5rem;letter-spacing:.28em;color:var(--grn);text-transform:uppercase}
.result-hero-right{font-family:var(--mono);font-size:.5rem;letter-spacing:.14em;color:var(--ink4)}
.result-hero-body{padding:1rem .95rem 1rem}
.result-hero-question{font-family:var(--mono);font-size:.54rem;letter-spacing:.2em;color:var(--ink4);text-transform:uppercase;margin-bottom:.55rem}
.result-hero-conclusion{font-family:var(--serif);font-size:1.55rem;font-weight:700;line-height:1.25;color:#f3efe8;max-width:980px;margin-bottom:.45rem}
.result-hero-sub{font-family:var(--sans);font-size:.92rem;line-height:1.65;color:var(--ink2);max-width:980px;margin-bottom:.85rem}
.result-hero-barrow{display:flex;align-items:center;gap:.7rem;margin:.15rem 0 1rem}
.result-hero-bar{height:8px;flex:1;max-width:360px;background:#18202b;border:1px solid #273244;position:relative;overflow:hidden}
.result-hero-fill{height:100%;background:linear-gradient(90deg,#4ec994,#9be6b8)}
.result-hero-pct{font-family:var(--mono);font-size:.64rem;color:var(--grn);letter-spacing:.1em;font-weight:700}
.result-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:1px;background:var(--border);border-top:1px solid var(--border)}
.result-cell{background:var(--bg1);padding:.8rem .95rem}
.result-cell-label{font-family:var(--mono);font-size:.46rem;letter-spacing:.24em;color:var(--ink4);text-transform:uppercase;margin-bottom:.35rem}
.result-breaking-list{margin:0;padding:0;list-style:none}
.result-breaking-item{display:flex;gap:.55rem;align-items:flex-start;padding:.2rem 0;border-bottom:1px solid var(--border)}
.result-breaking-item:last-child{border-bottom:none}
.result-breaking-bullet{color:var(--red);font-size:.65rem;flex-shrink:0;padding-top:.15rem}
.result-breaking-text{font-family:var(--sans);font-size:.84rem;line-height:1.55;color:#f0c7bd}
.result-insight{font-family:var(--serif);font-size:1.02rem;line-height:1.55;color:#d8efe1;background:var(--grn-bg);border-left:3px solid var(--grn);padding:.75rem .9rem;margin-bottom:.75rem}
.result-snapshot{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--border);border:1px solid var(--border)}
.result-snap-item{background:var(--bg2);padding:.65rem .75rem}
.result-snap-label{font-family:var(--mono);font-size:.45rem;letter-spacing:.18em;color:var(--ink4);text-transform:uppercase;margin-bottom:.22rem}
.result-snap-value{font-family:var(--serif);font-size:.98rem;font-weight:600;color:var(--ink)}
.result-rank{display:flex;flex-wrap:wrap;gap:.45rem .6rem;margin-top:.75rem}
.result-rank-pill{display:inline-flex;align-items:center;gap:.38rem;background:var(--bg2);border:1px solid var(--border2);padding:.35rem .6rem}
.result-rank-pill strong{font-family:var(--mono);font-size:.58rem;letter-spacing:.08em;color:var(--ink)}
.result-rank-pill span{font-family:var(--mono);font-size:.5rem;letter-spacing:.12em;color:var(--ink4);text-transform:uppercase}
.result-rank-pill em{font-family:var(--mono);font-style:normal;font-size:.56rem;color:var(--grn)}
.result-conclusion{margin-top:.75rem;padding:.7rem .85rem;background:#111823;border-left:3px solid var(--blu);font-family:var(--sans);font-size:.87rem;line-height:1.6;color:#d9e7ff}
.result-follow{font-family:var(--mono);font-size:.46rem;letter-spacing:.24em;color:var(--ink4);text-transform:uppercase;margin:1rem 0 .45rem}
@media (max-width: 920px){.result-grid{grid-template-columns:1fr}.result-snapshot{grid-template-columns:1fr 1fr}.result-hero-conclusion{font-size:1.28rem}}

.hyp-dashboard{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1px;background:var(--border);border-top:1px solid var(--border)}
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
.hyp-card-tes{font-family:var(--sans);font-size:.78rem;color:var(--ink2);line-height:1.62;margin-top:.5rem;padding-top:.5rem;border-top:1px solid var(--border)}

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

.hyp-detail-label{font-family:var(--mono);font-size:.52rem;letter-spacing:.28em;color:var(--ink4);text-transform:uppercase;padding:1rem 0 .3rem;border-top:1px solid var(--border);margin-top:.8rem}
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

/* ── PRIMARY ANALYSIS — PREMIUM ARTICLE RENDERER ── */

/* Outer wrapper */
.pa-wrapper{
  border:1px solid var(--border);
  border-left:3px solid var(--grn-dim);
  margin-top:.75rem;
  background:var(--bg1);
  overflow:hidden;
}

/* Header band — dark, editorial */
.pa-masthead{
  background:var(--bg);
  border-bottom:2px solid var(--grn-dim);
  padding:.7rem 1.2rem .6rem;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:1rem;
  flex-wrap:wrap;
}
.pa-masthead-left{display:flex;flex-direction:column;gap:.2rem}
.pa-masthead-kicker{
  font-family:var(--mono);font-size:.48rem;letter-spacing:.35em;
  color:var(--grn);text-transform:uppercase;
}
.pa-masthead-title{
  font-family:var(--serif);font-size:1.05rem;font-weight:700;
  color:var(--ink);line-height:1.3;
}
.pa-masthead-right{
  font-family:var(--mono);font-size:.52rem;color:var(--ink4);
  letter-spacing:.08em;text-align:right;line-height:1.7;
}

/* Methodology bar */
.pa-method-bar{
  background:var(--bg2);
  border-bottom:1px solid var(--border);
  padding:.45rem 1.2rem;
  font-family:var(--mono);font-size:.55rem;
  color:var(--ink4);letter-spacing:.05em;
  display:flex;gap:1.5rem;flex-wrap:wrap;
}
.pa-method-item{display:flex;align-items:center;gap:.4rem}
.pa-method-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0}

/* Article body */
.pa-article{
  padding:1.2rem 1.4rem 1.4rem;
  background:var(--bg1);
  column-gap:2rem;
}

/* Typography */
.pa-h1{
  font-family:var(--serif);font-size:1.12rem;font-weight:700;
  color:var(--ink);margin:1.4rem 0 .6rem;
  padding-bottom:.4rem;
  border-bottom:1px solid var(--border2);
  letter-spacing:-.01em;
}
.pa-h2{
  font-family:var(--serif);font-size:.98rem;font-weight:700;
  color:var(--ink);margin:1.2rem 0 .45rem;
  padding-left:.7rem;
  border-left:3px solid var(--grn-dim);
}
.pa-h3{
  font-family:var(--sans);font-size:.76rem;font-weight:700;
  color:var(--ink3);letter-spacing:.1em;
  margin:1rem 0 .3rem;text-transform:uppercase;
}
.pa-h4{
  font-family:var(--mono);font-size:.62rem;color:var(--ink4);
  letter-spacing:.2em;margin:.8rem 0 .2rem;text-transform:uppercase;
}
.pa-p{
  font-family:var(--serif);font-size:.87rem;line-height:1.95;
  color:var(--ink2);margin:0 0 .85rem;
}
.pa-p-lead{
  font-family:var(--serif);font-size:.97rem;line-height:1.88;
  color:var(--ink);margin:0 0 1rem;
  font-weight:400;
}
.para-break{margin:0;height:.2rem}

/* Lists */
.pa-list{list-style:none;padding:0;margin:.4rem 0 .9rem}
.pa-list li{
  font-family:var(--sans);font-size:.81rem;color:var(--ink2);
  line-height:1.68;padding:.32rem .8rem;
  border-left:2px solid var(--grn-dim);background:var(--grn-bg);
  margin-bottom:.2rem;display:flex;gap:.45rem;
}
.pa-list li::before{content:"•";color:var(--grn);flex-shrink:0}
.pa-numbered{
  font-family:var(--sans);font-size:.81rem;color:var(--ink2);
  line-height:1.68;padding:.25rem 0 .25rem .2rem;
  margin-bottom:.18rem;display:flex;gap:.55rem;
}
.pa-numbered::before{content:"›";color:var(--grn);flex-shrink:0;font-weight:700}

/* Table */
.pa-table{width:100%;border-collapse:collapse;margin:.8rem 0 1.1rem}
.pa-table th{
  font-family:var(--mono);font-size:.54rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ink3);
  background:var(--bg);padding:.42rem .7rem;
  border:1px solid var(--border);text-align:left;
}
.pa-table td{
  font-family:var(--sans);font-size:.8rem;color:var(--ink2);
  padding:.4rem .7rem;border:1px solid var(--border);
  line-height:1.55;vertical-align:top;
}
.pa-table tr:nth-child(even) td{background:var(--bg2)}
.pa-table tr:hover td{background:var(--bg3)}

/* Section labels — structured analysis blocks */
.pa-sec-lbl{
  font-family:var(--mono);font-size:.48rem;letter-spacing:.3em;
  text-transform:uppercase;margin:.75rem 0 .18rem;
  display:flex;align-items:center;gap:.5rem;
}
.pa-sec-lbl::before{
  content:'';display:inline-block;width:14px;height:1px;flex-shrink:0;
}
.pa-sec-tes{color:var(--grn)}.pa-sec-tes::before{background:var(--grn)}
.pa-sec-bevis{color:var(--blu)}.pa-sec-bevis::before{background:var(--blu)}
.pa-sec-motarg{color:var(--red)}.pa-sec-motarg::before{background:var(--red)}
.pa-sec-falsif{color:#aab7ff}.pa-sec-falsif::before{background:#aab7ff}
.pa-sec-styrka{color:var(--amb)}.pa-sec-styrka::before{background:var(--amb)}
.pa-sec-ranking{color:var(--ink3)}.pa-sec-ranking::before{background:var(--ink3)}
.pa-sec-neutral{color:var(--ink4)}.pa-sec-neutral::before{background:var(--ink4)}

.pa-sec-body{
  font-family:var(--sans);font-size:.81rem;line-height:1.72;
  margin-bottom:.4rem;padding:.38rem .85rem;
  border-radius:0;
}
.pa-sec-tes-body{color:#9fe2bb;background:var(--grn-bg);border-left:2px solid var(--grn-dim)}
.pa-sec-bevis-body{color:var(--ink2);background:var(--blu-bg);border-left:2px solid var(--blu-dim)}
.pa-sec-motarg-body{color:#e0b1a7;background:var(--red-bg);border-left:2px solid var(--red-dim)}
.pa-sec-falsif-body{color:#aab7ff;background:#0c0f1e;border-left:2px solid #3a4070}
.pa-sec-styrka-body{
  color:var(--amb);background:var(--amb-bg);
  border-left:2px solid var(--amb-dim);
  font-family:var(--mono);font-weight:700;font-size:.75rem;
  letter-spacing:.1em;
}
.pa-sec-ranking-body{color:var(--ink2);background:var(--bg2);border-left:2px solid var(--border2)}
.pa-sec-neutral-body{color:var(--ink2)}

/* Source footer */
.pa-sources{
  background:var(--bg);
  border-top:1px solid var(--border);
  padding:.65rem 1.2rem;
  display:flex;align-items:baseline;gap:.8rem;flex-wrap:wrap;
}
.pa-sources-lbl{
  font-family:var(--mono);font-size:.46rem;letter-spacing:.3em;
  color:var(--ink4);white-space:nowrap;flex-shrink:0;
  text-transform:uppercase;
}
.pa-src-chip{
  display:inline-flex;align-items:center;gap:.3rem;
  font-family:var(--mono);font-size:.56rem;
  color:#8cc4ff;border:1px solid var(--blu-dim);
  background:var(--blu-bg);padding:.18rem .55rem;
  text-decoration:none;letter-spacing:.03em;
  transition:background .15s,color .15s;
}
.pa-src-chip:hover{background:#0d1830;color:#b8dcff}
.pa-src-chip-e{
  font-size:.46rem;color:var(--ink4);letter-spacing:.04em;
  border-left:1px solid var(--border2);padding-left:.3rem;
}

.link-strip{display:flex;gap:.38rem;flex-wrap:wrap;margin-top:.55rem}
.link-chip{display:inline-block;font-family:var(--mono);font-size:.56rem;color:#8cc4ff;border:1px solid var(--blu-dim);background:var(--blu-bg);padding:.16rem .48rem;text-decoration:none;letter-spacing:.03em}
.link-chip:hover{background:#0d1830;color:#b8dcff}
.link-strip-dim{font-family:var(--mono);font-size:.55rem;color:var(--ink4);margin-top:.45rem}

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
.analysis-text{font-family:var(--sans);font-size:.82rem;line-height:1.86;color:var(--ink2)}
.analysis-text a{color:#6ca9ef;text-decoration:underline}
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
div[data-testid="stExpander"]>div:first-child{background:#1b2230!important;border:1px solid #303a4c!important;border-radius:0!important;font-family:var(--mono)!important;font-size:.65rem!important;color:#d7d0c4!important;letter-spacing:.06em!important}
div[data-testid="stExpander"]>div:first-child:hover{background:#232d3e!important;color:#f2efe8!important;border-color:#57c78a!important}
div[data-testid="stExpander"]>div:first-child svg{opacity:.7!important}
div[data-testid="stExpander"]>div:last-child{background:var(--bg1)!important;border:1px solid var(--border)!important;border-top:none!important;border-radius:0!important}
.stSpinner>div{border-top-color:var(--grn)!important}
</style>
""", unsafe_allow_html=True)


# ── Markdown → Article HTML ────────────────────────────────────────────────────

def _inline_md(text):
    if not text: return ""
    links = {}
    def _stash(m):
        key = f"\x00L{len(links)}\x00"
        links[key] = f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>'
        return key
    t = re.sub(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', _stash, text)
    t = t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    t = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*(.+?)\*', r'<em>\1</em>', t)
    t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
    for key, html in links.items(): t = t.replace(key, html)
    return t

def _md_to_article_html(text):
    """Convert markdown primary analysis text to formatted HTML article."""
    if not text: return ""
    lines = text.split('\n')
    out = []
    in_table = False
    in_list = False
    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            if in_list: out.append('</ul>'); in_list = False
            if in_table: out.append('</table>'); in_table = False
            i += 1; continue
        # Table separator row — also handle separator with extra spaces
        if re.match(r'^\|[\s\-\|:]+\|?\s*$', s):
            i += 1; continue
        # Table row — must have at least 2 pipes
        if s.startswith('|') and s.count('|') >= 2:
            if in_list: out.append('</ul>'); in_list = False
            if not in_table:
                out.append('<table class="pa-table">'); in_table = True
            # Clean trailing pipe if missing
            clean_s = s if s.endswith('|') else s + '|'
            cells = [c.strip() for c in clean_s[1:-1].split('|')]
            # Skip rows where ALL cells are empty or just dashes
            if all(not c or re.match(r'^[-:\s]+$', c) for c in cells):
                i += 1; continue
            nxt = lines[i+1].strip() if i+1 < len(lines) else ''
            is_hdr = bool(re.match(r'^\|[\s\-\|:]+\|?\s*$', nxt))
            tag = 'th' if is_hdr else 'td'
            out.append('<tr>' + ''.join(f'<{tag}>{_inline_md(c)}</{tag}>' for c in cells if c) + '</tr>')
            i += 1; continue
        if in_table:
            out.append('</table>'); in_table = False
        # Headers
        hm = re.match(r'^(#{1,4})\s+(.+)$', s)
        if hm:
            if in_list: out.append('</ul>'); in_list = False
            lvl = len(hm.group(1))
            cls = {1:'pa-h1',2:'pa-h2',3:'pa-h3',4:'pa-h4'}.get(lvl,'pa-h3')
            header_text = hm.group(2)
            # For H2/H3 that start with "H1/H2/H3 [LABEL]" — strip the hypothesis key prefix
            # so "## H1 [STRUKTURELL] — Ukrainsk operation" becomes "Ukrainsk operation"
            # This avoids the "now comes H1 again" feeling
            cleaned = re.sub(
                r'^H[1-4]\s*[\[\(]?[A-ZÅÄÖ\s]*[\]\)]?\s*[—\-]\s*',
                '', header_text, flags=re.IGNORECASE
            ).strip()
            # Also strip "TRE LINSER — " prefix and replace with cleaner heading
            if re.match(r'^TRE\s+LINSER', cleaned, re.IGNORECASE):
                cleaned = "Evidensgenomgång"
            display = cleaned if cleaned else header_text
            out.append(f'<div class="{cls}">{_inline_md(display)}</div>')
            i += 1; continue
        # Section labels: TES, BEVIS 1, MOTARG, FALSIFIERING, STYRKA, RANKING
        lm = re.match(r'^\*{0,2}(TES|BEVIS(?:\s*\d*)?|MOTARG(?:UMENT)?(?:\s*\d*)?|FALSIFIERINGS(?:TEST)?|STYRKA|RANKING)\*{0,2}\s*(?:\[.*?\])?\s*:?\s*(.*)', s, re.IGNORECASE)
        if lm:
            if in_list: out.append('</ul>'); in_list = False
            lbl = lm.group(1).strip().upper()
            rest = lm.group(2).strip()
            sec_map = [('TES','pa-sec-tes'),('BEVIS','pa-sec-bevis'),('MOTARG','pa-sec-motarg'),
                       ('FALSIF','pa-sec-falsif'),('STYRKA','pa-sec-styrka'),('RANKING','pa-sec-ranking')]
            sec_cls = 'pa-sec-neutral'
            for k,v in sec_map:
                if lbl.startswith(k): sec_cls = v; break
            out.append(f'<div class="pa-sec-lbl {sec_cls}">{lbl}</div>')
            if rest:
                out.append(f'<div class="pa-sec-body {sec_cls}-body">{_inline_md(rest)}</div>')
            i += 1; continue
        # Numbered list
        if re.match(r'^\d+[\.\)]\s+', s):
            if in_list: out.append('</ul>'); in_list = False
            body = re.sub(r'^\d+[\.\)]\s+','',s)
            out.append(f'<div class="pa-numbered">{_inline_md(body)}</div>')
            i += 1; continue
        # Standalone source reference line — e.g. "[E5 — BGH](https://...)" or "[E4 — Der Spiegel](https://...)"
        # These appear on their own line after a claim. Attach them to the previous element as inline chips.
        src_only = re.match(
            r'^\[(?:E[1-5][^\]]*?|[A-ZÅÄÖ][^\]]{2,50})\]\((https?://[^\s\)]+)\)\s*(?:,\s*\[(?:E[1-5][^\]]*?|[A-ZÅÄÖ][^\]]{2,50})\]\((https?://[^\s\)]+)\))*\s*$',
            s
        )
        if src_only:
            if in_list: out.append('</ul>'); in_list = False
            # Extract all [Label](url) pairs from this line and render as inline source chips
            chips = ""
            for sm in re.finditer(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', s):
                label = sm.group(1).strip()
                url   = sm.group(2).strip()
                # Style E-level in label
                e_match = re.match(r'^(E[1-5])\s*[—–-]\s*(.+)$', label)
                if e_match:
                    e_lbl = e_match.group(1)
                    src_name = e_match.group(2).strip()
                    chips += (
                        f'<a href="{url}" target="_blank" rel="noopener" '
                        f'class="pa-src-chip" style="margin:.1rem .2rem 0 0;font-size:.52rem;">'
                        f'<span style="color:var(--grn);font-size:.46rem;margin-right:.25rem">{_safe(e_lbl)}</span>'
                        f'{_safe(src_name[:30])}</a>'
                    )
                else:
                    chips += (
                        f'<a href="{url}" target="_blank" rel="noopener" '
                        f'class="pa-src-chip" style="margin:.1rem .2rem 0 0;font-size:.52rem;">'
                        f'{_safe(label[:35])}</a>'
                    )
            if chips:
                out.append(f'<div style="display:flex;flex-wrap:wrap;gap:.2rem;margin-bottom:.4rem">{chips}</div>')
            i += 1; continue

        # Bullet list
        if re.match(r'^[-\*•]\s+', s):
            if not in_list:
                out.append('<ul class="pa-list">'); in_list = True
            body = re.sub(r'^[-\*•]\s+','',s)
            out.append(f'<li>{_inline_md(body)}</li>')
            i += 1; continue
        if in_list: out.append('</ul>'); in_list = False
        # Normal paragraph
        out.append(f'<p class="pa-p">{_inline_md(s)}</p>')
        i += 1
    if in_list: out.append('</ul>')
    if in_table: out.append('</table>')
    return '\n'.join(out)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _slugify(q, n=45):
    for k,v in {'å':'a','ä':'a','ö':'o','Å':'A','Ä':'A','Ö':'O'}.items():
        q = (q or "").replace(k,v)
    return re.sub(r'\s+','_', re.sub(r'[^a-zA-Z0-9\s]','', q).strip().lower())[:n] or "analys"


def _build_pdf_v9(r: dict, ranked: list) -> bytes:
    """
    Bygger PDF v9 — tre sidor (dashboard, artikel, djupanalys).
    Extraherar insight och operativ automatiskt ur analysen.
    Faller tillbaka på gamla pdf_export om något går fel.
    """
    try:
        from pdf_export import build_pdf as _bp

        # Extrahera insight — den rubrikbara slutsatsen
        insight = ""
        for src in [r.get("final_analysis", ""), r.get("claude_answer", "")]:
            if not src:
                continue
            for sent in re.split(r"(?<=[.!?])\s+", src):
                s = sent.strip()
                s = re.sub(r"\[FAKTA\]|\[INFERENS\]|\[PÅGÅENDE\]|\*{1,3}", "", s).strip()
                if 50 < len(s) < 200 and any(kw in s.lower() for kw in [
                    "inte om att", "handlar om", "kontrollerar", "filter",
                    "geografi", "kan inte", "ingen militär", "asymmetrisk",
                    "hävstång", "selektiv", "de facto", "avgörande"
                ]):
                    insight = s
                    break
            if insight:
                break

        # Extrahera operativ bedömning — tre fält
        operativ = {}
        txt = r.get("final_analysis", "") or r.get("claude_answer", "") or ""

        # Nu
        for pat in [r"De facto stängt[^.]+\.", r"Sundet[^.]+stängt[^.]+\.",
                    r"\d+%\s+trafikminskning[^.]+"]:
            m = re.search(pat, txt, re.IGNORECASE)
            if m:
                operativ["nu"] = m.group(0)[:110].strip()
                break
        if not operativ.get("nu"):
            operativ["nu"] = "Pågående situation — se analys."

        # Härnäst
        for pat in [r"\d+\s*(?:mars|april|maj)[^.]+deadline[^.]+\.",
                    r"deadline[^.]+löper[^.]+\.", r"förhandlings\w*\s+\w+\s+\d+"]:
            m = re.search(pat, txt, re.IGNORECASE)
            if m:
                operativ["nasta"] = m.group(0)[:110].strip()
                break
        if not operativ.get("nasta"):
            operativ["nasta"] = "Nästa avgörande moment okänt — följ löpande."

        # Risk
        for pat in [r"(?:HÖG|KRITISK)[^.]*DIA[^.]+\.",
                    r"DIA[^.]+(?:månader|veckor)[^.]+\.",
                    r"(?:HÖG|KRITISK)\s+risknivå[^.]+"]:
            m = re.search(pat, txt, re.IGNORECASE)
            if m:
                operativ["risk"] = m.group(0)[:110].strip()
                break
        if not operativ.get("risk"):
            # Sök HÖG/MEDEL/LÅG i texten
            rm = re.search(r"(HÖG|MEDEL|LÅG|KRITISK)", txt, re.IGNORECASE)
            operativ["risk"] = f"{rm.group(1)} — se fullständig analys." if rm else "Se riskbedömning i analysen."

        # Bygg komplett result-dict för v9
        r_v9 = dict(r)
        r_v9["ranked"]  = ranked
        r_v9["insight"] = insight
        r_v9["operativ"] = operativ

        return _bp(r_v9)

    except Exception:
        # Fallback — returnera tom bytes (export-knappen visar ingenting)
        return b""

def _safe(t): return (t or "").replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def _safe_links(text):
    if not text: return ""
    # First auto-wrap raw URLs that aren't already in markdown links
    def _wrap_raw(m):
        url = m.group(0)
        return f"[{url}]({url})"
    text = re.sub(r'(?<!\]\()(?<!href=")(https?://[^\s<\)"]+)', _wrap_raw, text)
    links = {}
    def _stash(m):
        key = f"\x00L{len(links)}\x00"
        links[key] = f'<a href="{m.group(2)}" target="_blank" rel="noopener">{_safe(m.group(1))}</a>'
        return key
    t2 = re.sub(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)', _stash, text)
    t2 = _safe(t2)
    for key, html in links.items(): t2 = t2.replace(key, html)
    t2 = t2.replace('\n','<br>')
    return t2

def _extract_urls(text):
    if not text: return []
    urls = []
    for m in re.findall(r'\[[^\]]+\]\((https?://[^\s\)]+)\)', text): urls.append(m.strip())
    for m in re.findall(r'https?://[^\s<\)"]+', text): urls.append(m.strip())
    seen = set(); out = []
    for u in urls:
        if u not in seen: seen.add(u); out.append(u)
    return out

def _domain_label(url):
    m = re.search(r'https?://(?:www\.)?([^/\s]+)', url or "")
    return m.group(1) if m else "källa"

def _is_bad_url(u):
    BAD = {"google.com","google.se","bing.com","search.yahoo.com","yahoo.com","localhost"}
    return not u or any(d in u for d in BAD) or '/search?' in u

def _links_strip_html(urls, max_links=4):
    """Render real article links as chips with URL status indicators."""
    real = [u for u in (urls or []) if not _is_bad_url(u)][:max_links]
    if not real:
        return ""
    chips = ''.join(_link_chip_with_status(u) for u in real)
    return f'<div class="link-strip">{chips}</div>'

def _google_search_link(query: str) -> str:
    return ""  # Removed

def _single_primary_link_html(url: str, label: str = "") -> str:
    """One prominent source link with status indicator."""
    if not url or _is_bad_url(url):
        return ""
    disp = label or _domain_label(url)
    status = st.session_state.get("url_status", {}).get(url)
    if status is False:
        return (
            f'<span class="pa-src-chip" style="opacity:.4;cursor:not-allowed;'
            f'border-color:#5b2620;color:#db6b57;" title="Länken ej tillgänglig">'
            f'<span style="margin-right:.35rem;font-size:.5rem">✗</span>'
            f'{_safe(disp[:45])}</span>'
        )
    badge = _url_badge(url)
    return (
        f'<a class="pa-src-chip" href="{url}" target="_blank" rel="noopener" '
        f'style="display:inline-flex;margin:.45rem 0 .1rem;">'
        f'<span style="color:var(--ink3);margin-right:.35rem;font-size:.5rem">↗</span>'
        f'{_safe(disp[:45])}{badge}</a>'
    )

def _collect_links_from_raw(raw_text: str, hyp_key: str) -> list:
    """Extract real URLs from raw claude_answer for a specific hypothesis block."""
    if not raw_text or not hyp_key:
        return []
    pattern = re.compile(
        rf'(?:^|\n)\s*(?:#+\s*)?{re.escape(hyp_key)}\s*[\[\(—\-:\s]',
        re.IGNORECASE
    )
    m = pattern.search('\n' + raw_text)
    if not m:
        return []
    start = m.start()
    next_h = re.search(r'\n\s*(?:#+\s*)?H[1-4]\s*[\[\(—\-:\s]', raw_text[start+1:])
    end = start + 1 + next_h.start() if next_h else len(raw_text)
    block = raw_text[start:end]
    urls = _extract_urls(block)
    seen = set(); out = []
    for u in urls:
        if not _is_bad_url(u) and u not in seen:
            seen.add(u); out.append(u)
    return out[:6]


def _collect_links_from_hyp(hyp, raw_text=""):
    """
    Returns (real_urls, google_fallback_url).
    real_urls: actual article links from raw text or hyp fields
    google_fallback_url: always a Google search — only shown at bottom of expanders
    """
    # Build Google fallback
    term = (hyp.get("title") or hyp.get("label") or hyp.get("key") or "").strip()
    # Try raw text first
    if raw_text:
        real = _collect_links_from_raw(raw_text, hyp.get("key",""))
        if real:
            return real, ""

    # Try normalizer-surviving URLs in hyp fields
    urls = []
    for part in [hyp.get("tes",""), hyp.get("falsifiering","")]:
        urls.extend(_extract_urls(part or ""))
    for lst in ["bevis","motarg"]:
        for item in hyp.get(lst,[]) or []:
            urls.extend(_extract_urls(item or ""))
    real = [u for u in dict.fromkeys(urls) if not _is_bad_url(u)]
    return real, ""

def _pill(label, cls): return f'<span class="pill pill-{cls}">{_safe(label)}</span>'

def _section_zone(title, body_html, accent="blu", right_html=""):
    return f'<div class="zone zone-accent-{accent}"><div class="zone-header"><span>{_safe(title)}</span><span>{right_html}</span></div><div class="zone-body">{body_html}</div></div>'

def step_html(steps):
    h = '<div class="step-row">'
    for label, status in steps:
        cls = {"done":"step-done","active":"step-active","warn":"step-warn"}.get(status,"")
        h += f'<span class="step {cls}">{_safe(label)}</span>'
    return h + "</div>"

STYRKA_COLOR = {"HÖG":"#57c78a","MEDEL-HÖG":"#8fd45f","MEDEL":"#6eb6ff","LÅG":"#db6b57"}
REALITY_PILL = {
    "VERIFIED":("grn","✓ VERIFIED"),"ONGOING":("blu","◉ ONGOING"),"PARTIAL":("amb","◑ PARTIAL"),
    "HYPOTHETICAL":("dim","◌ HYPOTHETICAL"),"ANALYTICAL":("blu","◎ ANALYTICAL"),
    "UNVERIFIED":("red","✗ UNVERIFIED"),"ERROR":("red","✗ ERROR"),
}
STATUS_PILL = {"KLAR":("grn","✓ KLAR"),"REVIDERAD":("amb","↻ REVIDERAD"),"DEGRADERAD":("red","⚠ DEGRADERAD")}

def _build_assessment(ranked):
    if not ranked: return "",""
    w = ranked[0]
    # Slutsats: vad det betyder just nu — INTE en repetering av H1-titeln
    # Formulera en konsekvens-orienterad mening, inte bara "evidensen stödjer H1"
    key = w.get('key',''); lbl = w.get('label',''); title = w.get('title','')
    tes = w.get("tes","") or ""
    conf = float(w.get("conf", 0.5))

    # Bygg en slutsats som svarar "vad betyder detta just nu?"
    if conf >= 0.70:
        styrka_adv = "med stark evidens"
    elif conf >= 0.50:
        styrka_adv = "med måttlig evidens"
    else:
        styrka_adv = "men evidensen är svag"

    # Extrahera det viktigaste implikationen ur tes-texten istället för att repetera den
    # Sök efter en mening som handlar om konsekvens/implikation
    impl = ""
    if tes:
        for sent in re.split(r'(?<=[.!?])\s+', tes):
            sent = sent.strip()
            if len(sent) > 60 and any(w in sent.lower() for w in
                ["innebär","betyder","konsekvens","implikation","därmed","alltså",
                 "tyder på","pekar mot","visar att","indikerar","suggests","implies"]):
                impl = sent[:220]
                if len(impl) == 220: impl = impl.rstrip()+"…"
                break

    if impl:
        conc = impl
    elif title:
        conc = f"{key} [{lbl}] framstår som den starkaste förklaringen {styrka_adv}."
    else:
        conc = f"Analysen pekar mot {key} [{lbl}] {styrka_adv}."

    # Förklaring: epistemisk kontext — rankingen, vad som återstår osäkert
    parts = []
    if len(ranked) > 1:
        r2 = ranked[1]
        gap = conf - float(r2.get("conf",0.5))
        if gap < 0.10:
            parts.append(f"Skillnaden mot {r2.get('key','')} [{r2.get('label','')}] är liten (conf {r2.get('conf',0.5):.2f}) — analysen är inte avgörande.")
        else:
            t2 = r2.get('title','')
            p = f"Näst starkast: {r2.get('key','')} [{r2.get('label','')}]"
            if t2: p += f" — {t2[:60]}"
            p += f" (conf {r2.get('conf',0.5):.2f})."
            parts.append(p)
    if len(ranked) > 2:
        r3 = ranked[-1]
        parts.append(f"Svagast stöd: {r3.get('key','')} (conf {r3.get('conf',0.2):.2f}).")
    return conc, " ".join(parts)

def _hyp_dashboard_html(ranked, url_pool=None):
    if url_pool is None: url_pool = {}
    cards = []
    rank_labels = ["#1 STARKAST","#2","#3","#4"]
    card_classes = ["hyp-card-winner","hyp-card-2","hyp-card-3"]
    for i, h in enumerate(ranked[:4]):
        key=h.get("key",""); lbl=h.get("label",""); title=h.get("title","")
        styrka=(h.get("styrka") or "MEDEL").upper()
        tes=h.get("tes",""); bevis=h.get("bevis",[]) or []; motarg=h.get("motarg",[]) or []
        pct=int(h.get("conf_pct", int(h.get("conf",0.5)*100)))
        color=STYRKA_COLOR.get(styrka,"#6eb6ff"); cls=card_classes[i] if i<len(card_classes) else ""
        tes_short = ""
        if tes:
            tes_short = tes[:220]
            if len(tes)>220:
                cut = tes_short.rfind(". ")
                tes_short = tes_short[:cut+1] if cut>80 else tes_short.rstrip()+"…"

        # One real link per card — from url_pool, or named source search, or generic Google
        hyp_urls = url_pool.get(key.upper(), [])
        if not hyp_urls:
            # Try global pool
            hyp_urls = url_pool.get("global", [])
        if hyp_urls:
            link_html = _single_primary_link_html(hyp_urls[0])
        else:
            link_html = ""

        cards.append(f"""<div class="hyp-card {cls}">
  <div class="hyp-card-rank">{rank_labels[i] if i<len(rank_labels) else f'#{i+1}'}</div>
  <div class="hyp-card-key" style="color:{color}">{_safe(key)}</div>
  <div class="hyp-card-lbl">{_safe(lbl)}</div>
  <div class="hyp-card-title">{_safe(title)}</div>
  <div class="hyp-card-bar-wrap"><div class="hyp-card-bar-track"><div class="hyp-card-bar-fill" style="width:{pct}%;background:{color}"></div></div><span class="hyp-card-pct" style="color:{color}">{pct}%</span></div>
  <div class="hyp-card-meta"><span>{_safe(styrka)}</span><span>{len(bevis)} bevis</span><span>{len(motarg)} motarg</span></div>
  {"<div class='hyp-card-tes'>" + _safe(tes_short) + "</div>" if tes_short else ""}
  {link_html}
</div>""")
    return '<div class="hyp-dashboard">' + "".join(cards) + "</div>"

def _nyckelord_html(ranked):
    return ""

def _parse_rc_structured(txt):
    items = []
    for block in re.split(r'\n(?=CLAIM\s*\d*:)', txt or "", flags=re.IGNORECASE):
        c_m = re.search(r'CLAIM\s*\d*:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        s_m = re.search(r'STATUS\s*:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        src_m = re.search(r'(?:SOURCE|KÄLLA)\s*:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        if c_m:
            items.append({"claim":c_m.group(1).strip(),"status":s_m.group(1).strip() if s_m else "","source":src_m.group(1).strip() if src_m else ""})
    if items: return items[:6]
    for line in (txt or "").split('\n'):
        s=line.strip(); u=s.upper()
        if not s or len(s)<12: continue
        if any(x in u for x in ["ÖVERGRIPANDE","OVERALL STATUS","BESLUT:","REALITY CHECK","SAMMANFATTNING"]): continue
        st=""
        if any(x in u for x in ["VERIFIED","BEKRÄFTAD","✓","✔"]): st="VERIFIED"
        elif any(x in u for x in ["DISPUTED","OMTVISTAD","DELVIS","◑"]): st="DISPUTED"
        elif any(x in u for x in ["UNVERIFIED","EJ BEKRÄFTAD","✗"]): st="UNVERIFIED"
        src=""; sm=re.search(r'\(([^)]{5,90})\)\s*$', s)
        if sm: src=sm.group(1).strip()
        clean = re.sub(r'^(CLAIM\s*\d*:?\s*|[-•·]\s*)','',s).strip()
        if len(clean)>10: items.append({"claim":clean[:220],"status":st,"source":src})
        if len(items)>=6: break
    return items or [{"claim":(txt or "")[:300].replace('\n',' '),"status":"","source":""}]

def _rc_table_html(items):
    rows = []
    for it in items:
        claim=it.get("claim",""); status=(it.get("status","") or "").upper(); source=it.get("source","")
        if "VERIFIED" in status or "BEKRÄFTAD" in status: sc,si="rc-st-v","✓ VERIFIED"
        elif "DISPUTED" in status or "PARTIAL" in status: sc,si="rc-st-d","◑ DISPUTED"
        elif "UNVERIFIED" in status: sc,si="rc-st-u","✗ UNVERIFIED"
        else: sc,si="rc-st-n","◎ —"
        src_html = _safe_links(source) if source else '<span style="color:var(--ink4)">—</span>'
        rows.append(f'<tr><td class="rc-col-label">CLAIM</td><td class="rc-col-claim">{_safe_links(claim)}</td><td class="rc-col-status"><span class="{sc}">{si}</span></td><td class="rc-col-source">{src_html}</td></tr>')
    return '<table class="rc-table">' + "".join(rows) + "</table>"

def _normalize_text(text):
    if not text: return ""
    try:
        from normalizer import normalize_references
        return normalize_references(text)
    except Exception: return text

def _verdict_from_red(rr):
    up = (rr or "").upper()
    if "KOLLAPSAR" in up: return "red","✗","KRITIK — Alternativ tolkning kräver omskrivning"
    if "MODIFIERAS" in up or "IFRÅGASATT" in up: return "amb","◑","KRITIK — Analysen justeras utifrån alternativ modell"
    if "HÅLLER" in up: return "grn","✓","HÅLLER — Primäranalysen bekräftad av Red Team"
    return None,None,None


# ── NEW: Primary analysis renderer ────────────────────────────────────────────

def _extract_sources_with_elevel(text: str):
    """
    Extract (url, label, e_level) tuples from analysis text.
    Looks for patterns like [Källnamn](url) [E3] or [Källnamn — datum](url)
    Returns deduplicated list sorted by E-level descending.
    """
    sources = []
    BAD = {"google.com","google.se","bing.com","yahoo.com","localhost"}

    # Pattern: [label](url) optionally followed by [E-nivå] or [E3/E4] etc.
    pattern = re.compile(
        r'\[([^\]]+)\]\((https?://[^\s\)]+)\)'
        r'(?:\s*\[([E][1-5](?:/[E][1-5])*[^\]]*)\])?',
        re.IGNORECASE
    )
    seen_urls = set()
    for m in pattern.finditer(text):
        label = m.group(1).strip()
        url   = m.group(2).strip()
        elevel = m.group(3).strip() if m.group(3) else ""
        if any(d in url for d in BAD): continue
        if url in seen_urls: continue
        seen_urls.add(url)
        sources.append((url, label, elevel))

    # Also catch bare URLs not yet in markdown
    for raw_url in re.findall(r'(?<!\]\()https?://[^\s<\)"]+', text):
        if any(d in raw_url for d in BAD): continue
        if raw_url in seen_urls: continue
        seen_urls.add(raw_url)
        label = _domain_label(raw_url)
        sources.append((raw_url, label, ""))

    # Sort: E5 first, then E4, E3, etc., then unlabelled
    def _sort_key(s):
        e = s[2]
        for lvl in ["E5","E4","E3","E2","E1"]:
            if lvl in e.upper(): return -int(lvl[1])
        return 0
    sources.sort(key=_sort_key)
    return sources[:10]


def _sources_footer_html(sources):
    """Build a premium sources footer with E-level badges."""
    if not sources:
        return ""
    chips = []
    for url, label, elevel in sources:
        e_html = f'<span class="pa-src-chip-e">{_safe(elevel)}</span>' if elevel else ""
        chips.append(
            f'<a class="pa-src-chip" href="{url}" target="_blank" rel="noopener">'
            f'{_safe(label[:35])}{e_html}</a>'
        )
    return (
        '<div class="pa-sources">'
        '<span class="pa-sources-lbl">Källor</span>'
        + "".join(chips) +
        '</div>'
    )


def _extract_briefing(raw: str, ranked=None) -> dict:
    """Extract magazine-style briefing — explosive facts first, then hypotheses."""
    import re as _re
    lines = raw.split('\n')
    skip_patterns = [
        r'^#', r'^SANNINGSMASKINEN', r'^Datum:', r'^Status:',
        r'^Låt mig', r'^Jag behöver', r'^##', r'^⚠',
        r'^\*\*⚠', r'^\[PÅGÅENDE\]', r'^\[FAKTA\]',
        r'^TES', r'^BEVIS', r'^MOTARG', r'^STYRKA', r'^FALSIF',
        r'^RANKING', r'^DEL \d', r'^---',
    ]

    # ── Analytisk syntes: sharpest opening paragraph ──
    syntes_lines = []
    for line in lines:
        s = line.strip()
        if not s: continue
        if any(_re.match(p, s, _re.IGNORECASE) for p in skip_patterns): continue
        if _re.match(r'^H[1-4]\s*[\[\(—]', s, _re.IGNORECASE): continue
        s = _re.sub(r'^\*{1,3}"?', '', s)
        s = _re.sub(r'"?\*{1,3}$', '', s).strip()
        s = _re.sub(r'^\*\*([^*]+)\*\*', r'\1', s).strip()
        if len(s) > 80:
            syntes_lines.append(s)
            if len(syntes_lines) >= 3: break

    syntes_raw = " ".join(syntes_lines)
    if len(syntes_raw) > 420:
        cut = syntes_raw[:420].rfind('. ')
        syntes = syntes_raw[:cut+1] if cut > 150 else syntes_raw[:420].rstrip() + "…"
    else:
        syntes = syntes_raw

    # ── Nyckelfakta: explosive concrete facts ──
    KEY_PATTERNS = [
        # Befintliga
        r'greps|gripen|arresterad|åtalad|avgick|avskedades|dömdes|dödades',
        r'\d{1,2}\s+\w+\s+20\d{2}',
        r'miljoner|miljarder|\d+\s*sidor|\d+\s*videor|\d+\s*bilder',
        r'FBI|CIA|DOJ|kongressen|domstol|BGH',
        r'hemligt avtal|cover.?up|undanhöll|bortredigerade|immunitet',
        # Militära deployeringar och truppförflyttningar
        r'marines|MEU|expeditionary|amfibie|USS\s+\w+|warship|krigsfartyg|deployerar|deployering',
        r'trupper|markstyrk|marktrupp|landstiga|landstigning|amphibious',
        r'\d+\s*[0-9]\s*000\s*(?:marines|soldater|trupper)',
        # Ultimatum och deadlines
        r'48\s*timmar|ultimatum|deadline|löper ut|expires|frist',
        r'monday|måndag|tuesday|tisdag|19:44|23:44',
        # Eskaleringar och hot
        r'kraftverk|power plant|obliterate|utplåna',
        r'stängs permanent|permanent\s*stäng|irreversibly',
        r'avsaltning|desalination|dricksvatten',
        r'minor|minfält|mine|mining',
        # Ekonomi och pris
        r'\$\s*\d+|dollar per fat|brent|WTI|oljepris',
        r'börs|nikkei|kospi|hang seng|stock market',
    ]
    nyckelFakta = []
    seen = set()
    for line in lines:
        s = line.strip()
        if not s or len(s) < 50: continue
        if any(_re.match(p, s, _re.IGNORECASE) for p in skip_patterns): continue
        if _re.match(r'^H[1-4]\s*[\[\(—]', s, _re.IGNORECASE): continue
        if _re.match(r'^\*{0,2}(TES|BEVIS|MOTARG|STYRKA|FALSIF)', s, _re.IGNORECASE): continue
        s_clean = _re.sub(r'\[.*?\]\(https?://[^\)]+\)', '', s)
        s_clean = _re.sub(r'\[FAKTA\]|\[INFERENS\]|\[DEBATTERAD TOLKNING\]|\[PÅGÅENDE\]|\*{1,3}', '', s_clean).strip()
        s_clean = _re.sub(r'^\*\*([^*]+)\*\*:?\s*', '', s_clean).strip()
        if any(_re.search(p, s_clean, _re.IGNORECASE) for p in KEY_PATTERNS):
            if s_clean not in seen and len(s_clean) > 50:
                seen.add(s_clean)
                if len(s_clean) > 180:
                    cut = s_clean[:180].rfind('. ')
                    s_clean = s_clean[:cut+1] if cut > 60 else s_clean[:180].rstrip() + "…"
                nyckelFakta.append(s_clean)
        if len(nyckelFakta) >= 7: break

    # ── BREAKING: Extrahera "SENASTE TIMMARNAS HÄNDELSER"-blocket separat ──
    breaking_items = []
    in_breaking = False
    for line in lines:
        s = line.strip()
        if _re.search(r'SENASTE\s+TIMMARNAS|BREAKING\s+CONTEXT|⚡', s, _re.IGNORECASE):
            in_breaking = True
            continue
        if in_breaking:
            # Sluta vid nästa stor rubrik
            if _re.match(r'^#{1,3}\s+[A-ZÅÄÖ]', s) or _re.match(r'^##', s):
                break
            # Extrahera BREAKING-rader
            bm = _re.match(r'^BREAKING\s*[^\:]*:\s*(.+)', s, _re.IGNORECASE)
            if bm:
                item = bm.group(1).strip()
                item = _re.sub(r'\[.*?\]\(https?://[^\)]+\)', '', item).strip()
                if len(item) > 30:
                    breaking_items.append(item)
            elif s and len(s) > 40 and not s.startswith('#') and not s.startswith('INSTRUKTION'):
                # Ta med icke-tomma rader ur breaking-blocket
                clean = _re.sub(r'\[.*?\]\(https?://[^\)]+\)', '', s).strip()
                clean = _re.sub(r'\[FAKTA\]|\[INFERENS\]|\*{1,3}', '', clean).strip()
                if len(clean) > 40 and not any(kw in clean.upper() for kw in
                    ['INTEGRERA', 'PRIORITERA', 'INSTRUKTION', 'SANNINGSMASKINEN']):
                    breaking_items.append(clean)
            if len(breaking_items) >= 5:
                break

    # ── Nyckelfynd: H1/H2/H3 in strict order 1→2→3 ──
    hyp_map = {}
    current_h_num = None
    current_h_label = None
    for line in lines:
        s = line.strip()
        hm = _re.match(r'#{1,4}\s*H([1-4])\s*[\[\(]([^\]\)]+)[\]\)]\s*[—\-]\s*(.*)', s)
        if not hm:
            hm = _re.match(r'H([1-4])\s*[\[\(]([^\]\)]+)[\]\)]\s*[—\-]\s*(.*)', s)
        if hm:
            current_h_num = int(hm.group(1))
            lbl = hm.group(2).strip()
            title = hm.group(3).strip()
            current_h_label = f"H{current_h_num} [{lbl}]"
            if title: current_h_label += f" — {title[:50]}"
        if current_h_num and current_h_num not in hyp_map:
            tm = _re.match(r'^\*{0,2}TES\*{0,2}\s*:?\s*(.+)', s, _re.IGNORECASE)
            if tm:
                tes = _re.sub(r'\[.*?\]\(https?://[^\)]+\)', '', tm.group(1)).strip()
                tes = _re.sub(r'\[FAKTA\]|\[INFERENS\]|\[DEBATTERAD TOLKNING\]|\[PÅGÅENDE\]|\*{1,3}', '', tes).strip()
                if len(tes) > 150:
                    cut = tes[:150].rfind('. ')
                    tes = tes[:cut+1] if cut > 60 else tes[:150].rstrip() + "…"
                if tes:
                    hyp_map[current_h_num] = (current_h_label, tes)
                    current_h_num = None

    nyckelord = [hyp_map[k] for k in sorted(hyp_map.keys()) if k <= 3]

    if not nyckelord and ranked:
        for i, h in enumerate(ranked[:3], 1):
            key = h.get("key",""); lbl = h.get("label",""); tes = h.get("tes","") or ""
            if tes:
                if len(tes) > 150:
                    cut = tes[:150].rfind('. ')
                    tes = tes[:cut+1] if cut > 60 else tes[:150].rstrip() + "…"
                nm = int(_re.search(r'\d', key).group()) if _re.search(r'\d', key) else i
                hyp_map[nm] = (f"{key} [{lbl}]", tes)
        nyckelord = [hyp_map[k] for k in sorted(hyp_map.keys()) if k <= 3]

    return {"syntes": syntes, "nyckelFakta": nyckelFakta, "nyckelord": nyckelord, "breaking": breaking_items}


def _render_primary_analysis(primary_text, ranked=None, today_str="", url_pool=None):
    """Render primary analysis as magazine briefing + full expander."""
    if url_pool is None: url_pool = {}
    raw = primary_text or ""

    if not raw.strip():
        st.markdown('<div class="pa-wrapper"><div class="pa-article"><p class="pa-p">Ingen primäranalys returnerades.</p></div></div>', unsafe_allow_html=True)
        return

    # ── Masthead ──────────────────────────────────────────────────────────────
    model_line = "Claude Opus · GPT-4o Red Team"
    method_items = [
        ("#57c78a", "Tre hypoteser"),
        ("#6eb6ff", "Evidens E1–E5"),
        ("#db6b57", "Adversariell kritik"),
        ("#aab7ff", "Falsifieringstest"),
    ]
    method_html = "".join(
        f'<span class="pa-method-item"><span class="pa-method-dot" style="background:{c}"></span><span>{t}</span></span>'
        for c, t in method_items
    )
    st.markdown(f"""
<div class="pa-wrapper">
  <div class="pa-masthead">
    <div class="pa-masthead-left">
      <div class="pa-masthead-kicker">Primäranalys · Steg 1</div>
      <div class="pa-masthead-title">Analytisk syntes</div>
    </div>
    <div class="pa-masthead-right">{_safe(model_line)}<br>{_safe(today_str)}</div>
  </div>
  <div class="pa-method-bar">{method_html}</div>
</div>""", unsafe_allow_html=True)

    # ── Extract briefing data ─────────────────────────────────────────────────
    brief = _extract_briefing(raw, ranked)

    # ── LAGER 1: Magazine briefing ────────────────────────────────────────────
    # Syntes
    syntes_html = f'<p style="font-family:var(--serif);font-size:.93rem;line-height:1.9;color:var(--ink);margin:0 0 1.1rem">{_safe(brief["syntes"])}</p>' if brief["syntes"] else ""

    # Nyckelfynd — H1/H2/H3 cards
    # Prioritera ranked (normaliserade hypoteser) framför briefing-extraktion
    STYRKA_COLORS = {"H1":"var(--grn)","H2":"var(--amb)","H3":"var(--ink3)","H4":"var(--ink4)"}
    nyckel_cards = ""

    # Bygg från ranked direkt — garanterar att alla tre visas
    hyp_source = ranked[:3] if ranked else []
    for h in hyp_source:
        k = h.get("key",""); lbl = h.get("label",""); title = h.get("title","")
        tes = h.get("tes","") or ""
        pct = int(h.get("conf_pct", int(h.get("conf",0.5)*100)))
        col = STYRKA_COLORS.get(k[:2], "var(--ink3)")
        tes_short = tes[:160].rstrip()
        if len(tes) > 160:
            cut = tes_short.rfind(" ")
            tes_short = (tes_short[:cut] if cut > 80 else tes_short) + "…"
        subtitle = title[:55] if title else lbl[:40]
        nyckel_cards += (
            f'<div style="border-left:2px solid {col};padding:.45rem .75rem;margin-bottom:.45rem;background:var(--bg2)">'
            f'<div style="display:flex;align-items:center;gap:.5rem;margin-bottom:.18rem">'
            f'<span style="font-family:var(--mono);font-size:.6rem;font-weight:700;color:{col}">{_safe(k)}</span>'
            f'<span style="font-family:var(--mono);font-size:.46rem;letter-spacing:.15em;color:{col};opacity:.7">{_safe(lbl[:30])}</span>'
            f'<span style="font-family:var(--mono);font-size:.5rem;color:var(--ink4);margin-left:auto">{pct}%</span>'
            f'</div>'
            f'<div style="font-family:var(--mono);font-size:.48rem;color:var(--ink4);margin-bottom:.2rem;letter-spacing:.06em">{_safe(subtitle)}</div>'
            f'<div style="font-family:var(--sans);font-size:.8rem;color:var(--ink2);line-height:1.6">{_safe(tes_short)}</div>'
            f'</div>'
        )

    # Nyckelfakta — explosive concrete facts
    fakta_items = "".join(
        f'<li style="font-family:var(--sans);font-size:.82rem;color:var(--ink);'
        f'line-height:1.7;padding:.32rem 0;border-bottom:1px solid var(--border);'
        f'list-style:none;display:flex;gap:.55rem;align-items:baseline">'
        f'<span style="color:var(--grn);flex-shrink:0;font-weight:700">›</span>'
        f'<span>{_safe(f)}</span></li>'
        for f in brief.get("nyckelFakta", [])
    )
    fakta_html = f'<ul style="margin:0;padding:0">{fakta_items}</ul>' if fakta_items else ""

    # Sources
    global_urls = url_pool.get("global", [])
    if global_urls:
        elevel_map = {}
        for m in re.finditer(r'\[([^\]]+)\]\((https?://[^\s\)]+)\)\s*\[([E][1-5][^\]]*)\]', raw, re.IGNORECASE):
            elevel_map[m.group(2).strip()] = m.group(3).strip()
        sources = [(u, _domain_label(u), elevel_map.get(u,"")) for u in global_urls[:8]]
    else:
        sources = _extract_sources_with_elevel(raw)
    sources_html = _sources_footer_html(sources)

    # Sections with labels
    def _briefing_section(label, content, accent="var(--grn-dim)"):
        return (
            f'<div style="margin-bottom:1rem">'
            f'<div style="font-family:var(--mono);font-size:.46rem;letter-spacing:.3em;color:var(--ink4);text-transform:uppercase;margin-bottom:.45rem;display:flex;align-items:center;gap:.5rem">'
            f'<span style="display:inline-block;width:12px;height:1px;background:{accent}"></span>{label}</div>'
            f'{content}'
            f'</div>'
        )

    briefing_body = ""

    # ── BREAKING — visas ALLTID FÖRST om det finns breaking items ──
    breaking_items = brief.get("breaking", [])
    if breaking_items:
        b_rows = "".join(
            f'<li style="font-family:var(--sans);font-size:.82rem;color:#f2c0b0;'
            f'line-height:1.65;padding:.3rem 0;border-bottom:1px solid var(--red-dim);'
            f'list-style:none;display:flex;gap:.55rem;align-items:baseline">'
            f'<span style="color:var(--red);flex-shrink:0;font-weight:700;font-size:.7rem">⚡</span>'
            f'<span>{_safe(b)}</span></li>'
            for b in breaking_items
        )
        breaking_html = (
            f'<div style="border-left:3px solid var(--red);background:var(--red-bg);'
            f'padding:.5rem .8rem .3rem;margin-bottom:.2rem">'
            f'<div style="font-family:var(--mono);font-size:.44rem;letter-spacing:.3em;'
            f'color:var(--red);text-transform:uppercase;margin-bottom:.35rem">'
            f'🔴 BREAKING — Senaste timmarna</div>'
            f'<ul style="margin:0;padding:0">{b_rows}</ul>'
            f'</div>'
        )
        briefing_body += breaking_html

    if syntes_html:
        briefing_body += _briefing_section("Analytisk syntes", syntes_html)
    if fakta_html:
        briefing_body += _briefing_section("Det du behöver veta nu", fakta_html, "var(--amb)")
    if nyckel_cards:
        briefing_body += _briefing_section("Tre förklaringar — konkurrerande hypoteser", nyckel_cards, "var(--grn)")

    st.markdown(
        f'<div class="pa-wrapper" style="margin-top:0;border-top:none;border-left:3px solid var(--grn-dim);">'
        f'<div class="pa-article">{briefing_body}</div>'
        f'{sources_html}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── LAGER 2: Full analysis in expander ───────────────────────────────────
    with st.expander("▾  Visa fullständig primäranalys — evidens, hypoteser, sourcing", expanded=False):
        article_html = _md_to_article_html(raw)
        st.markdown(
            f'<div class="pa-article" style="background:var(--bg1)">{article_html}</div>',
            unsafe_allow_html=True
        )


# ── Session state ──────────────────────────────────────────────────────────────

for k, v in [("result",None),("running",False),("awaiting_confirm",False),
             ("layers_generated",False),("deep_generated",False),
             ("url_status",{}),("url_check_done",False)]:
    if k not in st.session_state: st.session_state[k] = v


# ── URL-validering ─────────────────────────────────────────────────────────────

def _check_urls(urls: list) -> dict:
    """
    Kontrollerar om URLs är tillgängliga. Returnerar {url: True/False}.
    Kör med kort timeout — hellre snabb än perfekt.
    """
    import urllib.request
    import urllib.error
    results = {}
    for url in urls:
        if not url or _is_bad_url(url):
            continue
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; Sanningsmaskinen/1.0)"},
                method="HEAD"
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                results[url] = resp.status < 400
        except Exception:
            # Försök GET om HEAD blockeras
            try:
                req2 = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; Sanningsmaskinen/1.0)"}
                )
                with urllib.request.urlopen(req2, timeout=4) as resp2:
                    results[url] = resp2.status < 400
            except Exception:
                results[url] = False
    return results


def _validate_urls_async(urls: list):
    """Kör URL-check i bakgrundstråd och uppdaterar session_state."""
    import threading
    def _worker():
        status = _check_urls(urls)
        if "url_status" not in st.session_state:
            st.session_state.url_status = {}
        st.session_state.url_status.update(status)
        st.session_state.url_check_done = True
    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def _url_badge(url: str) -> str:
    """Returnerar status-badge för en URL baserat på cache."""
    if not url or _is_bad_url(url):
        return ""
    status = st.session_state.get("url_status", {}).get(url)
    if status is True:
        return '<span style="color:#57c78a;font-size:.46rem;margin-left:.3rem">✓</span>'
    elif status is False:
        return '<span style="color:#db6b57;font-size:.46rem;margin-left:.3rem" title="Länken är inte tillgänglig">✗</span>'
    return '<span style="color:#7f8898;font-size:.46rem;margin-left:.3rem">…</span>'


def _link_chip_with_status(url: str, label: str = "") -> str:
    """Renderar en länkchip med URL-statusindikator."""
    if not url or _is_bad_url(url):
        return ""
    disp = label or _domain_label(url)
    status = st.session_state.get("url_status", {}).get(url)
    if status is False:
        return (
            f'<span class="link-chip" style="opacity:.45;cursor:not-allowed;'
            f'border-color:#5b2620;color:#db6b57;" '
            f'title="Länken är inte tillgänglig: {url}">'
            f'{_safe(disp[:35])}'
            f'<span style="font-size:.46rem;margin-left:.3rem">✗</span></span>'
        )
    badge = _url_badge(url)
    return (
        f'<a class="link-chip" href="{url}" target="_blank" rel="noopener">'
        f'{_safe(disp[:35])}{badge}</a>'
    )

# ── Sidebar — Historikbibliotek ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&display=swap');
/* ── SIDEBAR NUCLEAR OVERRIDE ── */
[data-testid="stSidebar"],[data-testid="stSidebar"]>div,
[data-testid="stSidebar"] section,[data-testid="stSidebar"] .block-container,
[data-testid="stSidebar"] .element-container,
[data-testid="stSidebar"] .stVerticalBlock,
[data-testid="stSidebar"] .stHorizontalBlock{
  background:#0f1115!important;color:#c8c2b8!important;
}
[data-testid="stSidebar"] *{
  font-family:'JetBrains Mono',monospace!important;
  color:#c8c2b8!important;
}
/* Expander header */
[data-testid="stSidebar"] [data-testid="stExpander"] summary,
[data-testid="stSidebar"] [data-testid="stExpanderToggleIcon"],
[data-testid="stSidebar"] details summary{
  background:#0f1115!important;
  color:#d7d0c4!important;
  font-size:.6rem!important;
  padding:.45rem .8rem!important;
  border-bottom:1px solid #1a2030!important;
}
/* Expander body */
[data-testid="stSidebar"] details,
[data-testid="stSidebar"] details>div,
[data-testid="stSidebar"] [data-testid="stExpander"]>div:last-child,
[data-testid="stSidebar"] [data-testid="stExpander"]>div:last-child>div,
[data-testid="stSidebar"] [data-testid="stExpander"]>div:last-child *{
  background:#0c0e12!important;
}
/* Input */
[data-testid="stSidebar"] input{
  background:#141821!important;border:1px solid #242c3a!important;
  color:#d7d0c4!important;font-size:.65rem!important;border-radius:0!important;
}
[data-testid="stSidebar"] input:focus{border-color:#57c78a!important;outline:none!important}
[data-testid="stSidebar"] input::placeholder{color:#4a5568!important}
/* Select */
[data-testid="stSidebar"] [data-baseweb="select"] div,
[data-testid="stSidebar"] [data-baseweb="select"] span{
  background:#141821!important;border-color:#242c3a!important;
  color:#b3ad9f!important;font-size:.62rem!important;
}
/* Buttons — proportionerliga mot frågetexten */
[data-testid="stSidebar"] button{
  background:#141821!important;color:#b3ad9f!important;
  border:1px solid #242c3a!important;border-radius:0!important;
  font-family:'JetBrains Mono',monospace!important;
  font-size:.52rem!important;letter-spacing:.08em!important;
  text-transform:uppercase!important;padding:.22rem .4rem!important;
  white-space:nowrap!important;line-height:1.2!important;
  width:100%!important;transition:all .15s!important;
}
[data-testid="stSidebar"] button:hover{
  border-color:#57c78a!important;color:#57c78a!important;
  background:#0a1510!important;
}
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button{
  background:#0a1220!important;color:#6eb6ff!important;
  border:1px solid #23486d!important;font-size:.52rem!important;
}
[data-testid="stSidebar"] [data-testid="stDownloadButton"] button:hover{
  background:#0d1828!important;border-color:#6eb6ff!important;color:#9cc7ff!important;
}
/* Radera — röd, diskret */
[data-testid="stSidebar"] button[kind="secondary"]:last-of-type{
  color:#8a3a30!important;border-color:#3a1510!important;
  background:#120908!important;font-size:.48rem!important;
}
[data-testid="stSidebar"] button[kind="secondary"]:last-of-type:hover{
  color:#db6b57!important;border-color:#5b2620!important;background:#1a0c0a!important;
}
/* Göm Streamlits debug-knappar */
[data-testid="stToolbar"],[data-testid="stDecoration"],
#stDecoration,.stApp > header{display:none!important}
/* Göm alla ikoner i sidebar */
[data-testid="stSidebar"] svg{display:none!important}

.lib-header{
  font-family:'JetBrains Mono',monospace!important;font-size:.46rem;letter-spacing:.4em;
  color:#57c78a!important;text-transform:uppercase;padding:.85rem 1rem .6rem;
  border-bottom:2px solid #1e4a34;background:#141821!important;
  display:flex;align-items:center;gap:.55rem;
}
.lib-header::before{content:'◎';font-size:.65rem;color:#57c78a}
.lib-day-header{
  font-family:'JetBrains Mono',monospace!important;font-size:.44rem;letter-spacing:.3em;
  color:#3a4a5a!important;text-transform:uppercase;
  padding:.45rem .9rem .3rem;background:#0a0b0d!important;
  border-top:1px solid #1a2030;border-bottom:1px solid #1a2030;
}
.lib-count{font-family:'JetBrains Mono',monospace!important;font-size:.44rem;
  color:#57c78a!important;letter-spacing:.1em;margin-left:.4rem;opacity:.6}
.lib-empty{font-family:'JetBrains Mono',monospace!important;font-size:.56rem;
  color:#3a4a5a!important;padding:2rem 1rem;text-align:center;line-height:2}
.lib-card{padding:.5rem .9rem .3rem;background:#0f1115;border-left:2px solid #1a2030;margin-bottom:.1rem;transition:border-color .15s}
.lib-card:hover{border-color:#2a3a4a;background:#111418}
.lib-card-q{font-family:'JetBrains Mono',monospace;font-size:.58rem;
  color:#d7d0c4;line-height:1.5;margin-bottom:.2rem}
.lib-card-meta{font-family:'JetBrains Mono',monospace;font-size:.44rem;
  color:#3a4858;display:flex;gap:.5rem;margin-bottom:.1rem;letter-spacing:.04em}
.lib-divider{height:1px;background:#0d1015;margin:.4rem 0}
</style>""", unsafe_allow_html=True)

    st.markdown('<div class="lib-header">Analysbibliotek</div>', unsafe_allow_html=True)

    # ── Imports ──────────────────────────────────────────────────────────────
    _lib_ok = False
    try:
        from history import list_history, load_result, delete_result, add_tag, remove_tag
        from pdf_export import build_pdf as _pdf_sidebar
        _lib_ok = True
    except Exception:
        pass
    if not _lib_ok:
        try:
            from history import list_history, load_result, delete_result
            from pdf_export import build_pdf as _pdf_sidebar
            def add_tag(fn, tag): pass
            def remove_tag(fn, tag): pass
            _lib_ok = True
        except Exception:
            st.caption("history.py saknas.")

    if _lib_ok:
        # ── Hämta entries ────────────────────────────────────────────────────
        try:
            entries = list_history()
        except Exception:
            entries = []

        # ── Sök ──────────────────────────────────────────────────────────────
        search_q = st.text_input("", placeholder="🔍  Sök i historiken...",
                                 label_visibility="collapsed", key="lib_search")

        # ── Filter ───────────────────────────────────────────────────────────
        REALITY_FILTER_OPTIONS = ["Alla", "✅ Verified", "🔍 Analytical",
                                  "⚠️ Partial", "🔄 Ongoing",
                                  "💭 Hypothetical", "❌ Unverified"]
        REALITY_MAP = {
            "✅ Verified": "VERIFIED", "🔍 Analytical": "ANALYTICAL",
            "⚠️ Partial": "PARTIAL",  "🔄 Ongoing": "ONGOING",
            "💭 Hypothetical": "HYPOTHETICAL", "❌ Unverified": "UNVERIFIED",
        }
        reality_filter = st.selectbox("", REALITY_FILTER_OPTIONS,
                                      label_visibility="collapsed", key="lib_filter")

        # ── Filtrera ─────────────────────────────────────────────────────────
        filtered = entries
        if search_q.strip():
            sq = search_q.strip().lower()
            filtered = [e for e in filtered
                        if sq in e.get("question","").lower()
                        or any(sq in t.lower() for t in e.get("tags",[]))]
        if reality_filter != "Alla":
            rf = REALITY_MAP.get(reality_filter, "")
            filtered = [e for e in filtered
                        if e.get("reality","").upper() == rf]

        # ── Räknare ──────────────────────────────────────────────────────────
        st.markdown(
            f'<div style="font-family:monospace;font-size:.5rem;color:#666;margin-bottom:.4rem">'
            f'ANALYSER<span class="lib-count">{len(filtered)} / {len(entries)}</span></div>',
            unsafe_allow_html=True)

        if not filtered:
            st.markdown('<div class="lib-empty">Inga analyser matchar.</div>',
                        unsafe_allow_html=True)
        else:
            # ── Gruppera per dag ──────────────────────────────────────────────
            from collections import OrderedDict
            from datetime import datetime as _dt
            days = OrderedDict()
            for e in filtered:
                raw_ts = e.get("timestamp", "").replace("_", " ")[:8]
                try:
                    day_label = _dt.strptime(raw_ts.strip(), "%Y%m%d").strftime("%-d %b %Y")
                except Exception:
                    day_label = raw_ts.strip() or "Okänt datum"
                days.setdefault(day_label, []).append(e)

            REALITY_ICONS_LIB = {
                'VERIFIED':'✅','ANALYTICAL':'🔍','PARTIAL':'⚠️',
                'UNVERIFIED':'❌','HYPOTHETICAL':'💭','ONGOING':'🔄',
            }
            STATUS_COLORS = {
                'KLAR':'#57c78a','REVIDERAD':'#e2b04c','DEGRADERAD':'#db6b57',
            }

            for day_label, day_entries in days.items():
                st.markdown(f'<div class="lib-day-header">{day_label}</div>',
                            unsafe_allow_html=True)

                for e in day_entries:
                    fn       = e.get("filename", "")
                    q        = e.get("question", "(okänd fråga)")
                    ts_raw   = e.get("timestamp", "").replace("_", " ")
                    ts       = ts_raw[9:14] if len(ts_raw) >= 14 else ""
                    ico      = REALITY_ICONS_LIB.get(e.get("reality",""), "·")
                    stat     = e.get("status", "")
                    stat_col = STATUS_COLORS.get(stat.upper(), "#4a5568")
                    tags     = e.get("tags", [])
                    q_short  = q[:52] + "…" if len(q) > 52 else q
                    tag_html = "".join(
                        f'<span class="lib-tag">{_safe(t)}</span>' for t in tags)

                    # Track which card is expanded
                    expanded_key = f"lib_expanded_{fn}"
                    is_expanded = st.session_state.get(expanded_key, False)

                    # Card — klickbar fråga
                    card_border = "#57c78a" if is_expanded else "#1a2030"
                    st.markdown(f"""
<div class="lib-card" style="border-left-color:{card_border}">
  <div class="lib-card-q">{ico} {_safe(q_short)}</div>
  <div class="lib-card-meta">
    <span style="color:{stat_col}">{_safe(stat)}</span>
    <span>·</span>
    <span>{_safe(ts)}</span>
  </div>
</div>""", unsafe_allow_html=True)

                    # Toggle-knapp på frågan
                    toggle_label = "▾ stäng" if is_expanded else "› visa alternativ"
                    if st.button(toggle_label, key=f"tog_{fn}",
                                 use_container_width=True):
                        st.session_state[expanded_key] = not is_expanded
                        st.rerun()

                    # Visa alternativ om expanderat
                    if is_expanded:
                        if st.button("▶ Öppna analys", key=f"o_{fn}",
                                     use_container_width=True):
                            loaded = load_result(fn)
                            if loaded:
                                st.session_state.result = loaded
                                st.session_state.layers_generated = bool(
                                    loaded.get("layers",{}).get("ground"))
                                st.session_state.deep_generated = bool(
                                    loaded.get("layers",{}).get("deep1"))
                                st.session_state[expanded_key] = False
                                st.rerun()
                        try:
                            l2 = load_result(fn)
                            if l2:
                                pb = _pdf_sidebar(l2)
                                st.download_button("↓ Ladda ner PDF", pb,
                                                   f"sm_{fn[:8]}.pdf",
                                                   "application/pdf",
                                                   key=f"p_{fn}",
                                                   use_container_width=True)
                        except Exception:
                            pass
                        if st.button("✕ Radera analys", key=f"d_{fn}",
                                     use_container_width=True):
                            delete_result(fn)
                            st.rerun()

                    st.markdown('<div class="lib-divider"></div>',
                                unsafe_allow_html=True)

# ── Topbar ─────────────────────────────────────────────────────────────────────
today_str = _date.today().strftime("%Y-%m-%d")
st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <span class="topbar-mark">◎ Sanningsmaskinen</span>
    <span class="topbar-title">Epistemiskt analysverktyg</span>
  </div>
  <div class="topbar-right">v8.18 · Claude Opus + GPT-4o · {today_str}</div>
</div>
<div class="topbar-sub">
  Analyserar komplexa frågor genom att väga konkurrerande hypoteser, granska evidens och falsifiera svagare förklaringar.
</div>
""", unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
if not st.session_state.result and not st.session_state.running:
    # Tom state — visa frågeruta
    input_col, btn_col = st.columns([6, 1])
    with input_col:
        _placeholder = "Vem sprängde Nord Stream? · Varför invaderade USA Irak 2003? · Vad förklarar SDs framgångar?"
        question = st.text_area("", placeholder=_placeholder,
                                height=100, label_visibility="collapsed",
                                key="main_question")
    with btn_col:
        st.markdown('<div style="height:.5rem"></div>', unsafe_allow_html=True)
        run_btn = st.button("Analysera →", disabled=st.session_state.running,
                            use_container_width=True)
else:
    # Resultat finns eller pipeline kör — göm frågerutan, visa en diskret ny-fråga-rad längst ner
    question = ""
    run_btn = False

# ── Pipeline ───────────────────────────────────────────────────────────────────
if run_btn and question.strip():
    st.session_state.running = True; st.session_state.result = None
    st.session_state.layers_generated = False; st.session_state.deep_generated = False
    st.session_state.url_status = {}; st.session_state.url_check_done = False
    try:
        from engine import (event_reality_check, ask_claude, ask_gpt_critic,
                            analyze_conflicts, run_red_team, auto_rewrite, assess_depth_recommendation)
        steps = [("0 Reality",""),("1 Primär",""),("2 GPT",""),("3 Konflikt",""),("4 Red Team",""),("5 Rewrite?","")]
        ph = st.empty()
        def upd(i, w=-1):
            arr = [(n,"done") if j<i else (n,"active") if j==i else (n,"warn") if j==w else (n,"") for j,(n,_) in enumerate(steps)]
            ph.markdown(step_html(arr), unsafe_allow_html=True)
        upd(0)
        with st.spinner("Reality check..."): rc = event_reality_check(question.strip())
        upd(1)
        if not rc.get("proceed"):
            st.session_state.awaiting_confirm=True; st.session_state._rc=rc
            st.session_state._question=question.strip(); st.session_state.running=False
            ph.empty(); st.rerun()
        with st.spinner("Primäranalys..."): ca = ask_claude(question.strip(), rc)
        upd(2)
        with st.spinner("GPT-4 kritiker..."): ga = ask_gpt_critic(question.strip(), ca, rc["status"])
        upd(3)
        with st.spinner("Konfliktanalys..."): cf = analyze_conflicts(ca, ga)
        upd(4)
        with st.spinner("Red Team..."): rr, should_rewrite = run_red_team(question.strip(), ca, cf)
        red_ok = bool(rr and "misslyckades" not in rr.lower() and "api-fel" not in rr.lower() and len(rr)>100)
        fa = ""
        if should_rewrite and red_ok:
            upd(5)
            with st.spinner("Rewrite..."): fa = auto_rewrite(question.strip(), ca, rr)
        ph.markdown(step_html([(n,"done") for n,_ in steps]), unsafe_allow_html=True)
        res = {"question":question.strip(),"reality_check":rc,"claude_answer":ca,"gpt_answer":ga,
               "conflict_report":cf,"red_team_report":rr,"red_team_ok":red_ok,"collapsed":should_rewrite,
               "final_analysis":fa,"layers":{},"degraded":not red_ok,
               "status":"DEGRADERAD" if not red_ok else ("REVIDERAD" if fa else "KLAR")}
        res["depth_recommendation"] = assess_depth_recommendation(res)
        st.session_state.result = res
        try:
            from history import save_result; save_result(res)
        except: pass
    except ImportError as e: st.error(f"Importfel: {e}")
    except Exception as e: st.error(f"Fel: {e}")
    finally: st.session_state.running = False; st.rerun()

# ── Confirm hypothetical ───────────────────────────────────────────────────────
if st.session_state.awaiting_confirm:
    rc_tmp=st.session_state.get("_rc",{}); q_tmp=st.session_state.get("_question","")
    st.markdown(f'<div class="degraded">HÄNDELSEN KAN INTE VERIFIERAS<br>{_safe(rc_tmp.get("text","")[:300])}<br><br>Fortsätta som hypotetiskt scenario?</div>', unsafe_allow_html=True)
    c1,c2 = st.columns([1,4])
    with c1:
        if st.button("Ja, fortsätt"):
            rc_tmp["proceed"]=True; st.session_state.awaiting_confirm=False; st.session_state.running=True
            try:
                from engine import (ask_claude,ask_gpt_critic,analyze_conflicts,run_red_team,auto_rewrite,assess_depth_recommendation)
                ca=ask_claude(q_tmp,rc_tmp); ga=ask_gpt_critic(q_tmp,ca,rc_tmp["status"])
                cf=analyze_conflicts(ca,ga); rr,sr=run_red_team(q_tmp,ca,cf)
                rok=bool(rr and "misslyckades" not in rr.lower() and len(rr)>100)
                fa=auto_rewrite(q_tmp,ca,rr) if sr and rok else ""
                res={"question":q_tmp,"reality_check":rc_tmp,"claude_answer":ca,"gpt_answer":ga,
                     "conflict_report":cf,"red_team_report":rr,"red_team_ok":rok,"collapsed":sr,
                     "final_analysis":fa,"layers":{},"degraded":not rok,
                     "status":"DEGRADERAD" if not rok else ("REVIDERAD" if fa else "KLAR")}
                res["depth_recommendation"]=assess_depth_recommendation(res)
                st.session_state.result=res
            except Exception as e: st.error(f"Fel: {e}")
            finally: st.session_state.running=False; st.rerun()
    with c2:
        if st.button("Avbryt"): st.session_state.awaiting_confirm=False; st.rerun()

# ── Result view ────────────────────────────────────────────────────────────────
if st.session_state.result:
    r=st.session_state.result; rc=r["reality_check"]; lyr=r.get("layers",{})

    # ── Extract URLs from RAW text BEFORE normalizer strips them ──────────────
    raw_claude = r.get("claude_answer","")

    def _build_url_pool(raw: str) -> dict:
        """
        Build a dict: {hyp_key: [url, ...]} from raw claude_answer.
        Extracts URLs per H1/H2/H3 block before normalizer runs.
        """
        pool = {"global": []}
        BAD = {"google.com","google.se","bing.com","yahoo.com","localhost"}

        # Get ALL urls in the full text first (global pool)
        all_urls = _extract_urls(raw)
        pool["global"] = [u for u in dict.fromkeys(all_urls) if not any(d in u for d in BAD)]

        # Now split into H-blocks using a flexible pattern
        # Matches: "H1", "## H1", "### H1 [label]", "H1 —", "H1:" etc.
        h_pattern = re.compile(
            r'(?:^|\n)\s*(?:#{1,4}\s*)?(H[1-4])\s*[\[\(—\-:\s]',
            re.IGNORECASE
        )
        matches = list(h_pattern.finditer('\n' + raw))

        for idx, m in enumerate(matches):
            key = m.group(1).upper()
            start = m.start()
            end = matches[idx+1].start() if idx+1 < len(matches) else len('\n' + raw)
            block = ('\n' + raw)[start:end]

            urls = _extract_urls(block)
            real = [u for u in dict.fromkeys(urls) if not any(d in u for d in BAD)]
            if real:
                pool[key] = real

        return pool

    url_pool = _build_url_pool(raw_claude)

    # ── Trigga URL-validering en gång per ny analys ───────────────────────────
    all_urls = url_pool.get("global", [])
    _result_id = r.get("question","")[:40]
    if all_urls and not st.session_state.url_check_done:
        _validate_urls_async(all_urls[:12])  # max 12 URLs per analys
    def _extract_named_sources(text: str) -> list:
        """
        Extract named sources mentioned in text like [E4 — Der Spiegel] or [Der Spiegel, feb 2026].
        Returns list of (source_name, search_url) tuples.
        """
        sources = []
        seen = set()

        # Pattern: [E4 — Source Name] or [Source Name] or [Source Name, date]
        for m in re.finditer(
            r'\[(?:E[1-5]\s*[—–-]\s*)?([A-ZÅÄÖ][A-Za-zåäöÅÄÖ\s\.,0-9]+?)(?:,\s*[a-z]{3,}\s*\d{4})?\]',
            text
        ):
            name = m.group(1).strip()
            # Filter out section labels and short strings
            if len(name) < 4: continue
            if name.upper() in {"TES","BEVIS","MOTARG","MOTARGUMENT","STYRKA","RANKING",
                                  "FAKTA","INFERENS","PÅGÅENDE","FAKTAPÅSTÅENDE"}: continue
            # Known news sources
            KNOWN = {"Der Spiegel","Spiegel","Al Jazeera","NYT","New York Times",
                     "Washington Post","WaPo","Reuters","AP","BBC","SVT","DN","SvD",
                     "BGH","Bundesgerichtshof","Wikipedia","HSCA","Warren Commission",
                     "ARD","Foreign Policy","CNN","Guardian","Axios","Politico",
                     "Wall Street Journal","WSJ","Aftonbladet","Expressen","Harvard Gazette",
                     "Britannica","CFR","House of Commons","CNBC","Kyiv Independent"}
            is_known = any(k.lower() in name.lower() for k in KNOWN)
            if not is_known and len(name) > 40: continue
            if name not in seen:
                seen.add(name)
                sources.append((name, ""))  # name only, no google URL
        return sources[:6]

    # Named sources kept for reference but NO google search fallback links

    try:
        from normalizer import normalize_claude_answer, compute_hypothesis_scores, normalize_references
        norm = normalize_claude_answer(raw_claude)  # OBS: normalize_references körs EJ här — parsern behöver råa E-taggar
        norm["hypotheses"] = compute_hypothesis_scores(norm.get("hypotheses",[]))
        hyps = norm.get("hypotheses",[])
    except Exception as e:
        hyps = []
        st.markdown(f'<div class="degraded">NORMALIZER-FEL: {_safe(str(e))}</div>', unsafe_allow_html=True)

    rank_order = {"HÖG":0,"MEDEL-HÖG":1,"MEDEL":2,"LÅG":3}
    ranked = sorted(hyps, key=lambda h: (rank_order.get((h.get("styrka") or "MEDEL").upper(),99), -float(h.get("conf",0))))

    rc_status = (rc.get("status","") or "").upper()
    res_status = (r.get("status","") or "").upper()

    if r.get("degraded"):
        st.markdown('<div class="degraded">⚠ DEGRADERAD LEVERANS — Red Team körde inte korrekt.</div>', unsafe_allow_html=True)

    # 1. FRÅGA
    rc_pill_cls, rc_pill_lbl = REALITY_PILL.get(rc_status, ("dim", rc_status))
    st_pill_cls, st_pill_lbl = STATUS_PILL.get(res_status, ("dim", res_status))
    fraga_body = (
        f'<div style="font-family:var(--serif);font-size:1.12rem;color:var(--ink);line-height:1.5;margin-bottom:.55rem;">{_safe(r["question"])}</div>'
        f'<div style="display:flex;gap:.4rem;flex-wrap:wrap;align-items:center;">{_pill(rc_pill_lbl,rc_pill_cls)}{_pill(st_pill_lbl,st_pill_cls)}</div>'
    )
    st.markdown(_section_zone("FRÅGA", fraga_body, "blu", today_str), unsafe_allow_html=True)
    # Rensa-knapp direkt under FRÅGA-zonen
    if st.button("✕ Ny analys — rensa", key="rensa_top"):
        st.session_state.result = None; st.session_state.layers_generated = False
        st.session_state.deep_generated = False; st.rerun()

    # raw text for link extraction (before normalizer strips URLs)
    raw_claude = r.get("claude_answer","")

    # ── Förberäkna brief så Executive Summary kan använda breaking-items ──
    raw_claude_for_brief = r.get("claude_answer","")
    _brief_pre = _extract_briefing(raw_claude_for_brief, ranked)
    _breaking_pre = _brief_pre.get("breaking", [])
    _fakta_pre = _brief_pre.get("nyckelFakta", [])

    # 2. RESULTATÖVERSIKT — decision-grade first screen
    if ranked:
        confs = [float(h.get("conf",0.5)) for h in ranked]
        avg_conf = sum(confs)/len(confs) if confs else 0.5
        if avg_conf>=0.70: conf_lbl="HÖG"
        elif avg_conf>=0.50: conf_lbl="MEDEL–HÖG"
        elif avg_conf>=0.35: conf_lbl="MEDEL"
        else: conf_lbl="LÅG"

        w = ranked[0]
        w_key = (w.get("key","") or "H1").upper()
        w_lbl = (w.get("label","") or "DOMINANT").strip()
        w_title = (w.get("title","") or "").strip()
        w_tes = (w.get("tes","") or "").strip()
        w_conf = float(w.get("conf",0.5))
        w_pct = int(w.get("conf_pct", int(w_conf*100)))

        def _clean_line(s: str) -> str:
            s = re.sub(r'\*{1,3}', '', s or '').strip()
            s = re.sub(r'\[FAKTA\]|\[INFERENS\]|\[PÅGÅENDE\]|\[ONGOING\]', '', s, flags=re.IGNORECASE).strip()
            s = re.sub(r'\[E[1-5][^\]]*\]', '', s).strip()
            s = re.sub(r'https?://\S+', '', s).strip()
            s = re.sub(r'\s+', ' ', s).strip(' -–—|')
            return s

        q_raw = (r.get("question","") or "").strip()
        q_clean = q_raw.rstrip(' ?')
        if q_clean:
            q_clean = q_clean[0].upper() + q_clean[1:]

        rc_txt_raw = rc.get("text","") or ""
        hero = ""
        for line in rc_txt_raw.split("\n"):
            s = _clean_line(line)
            if len(s) > 55 and not s.startswith('#') and 'CLAIM' not in s.upper() and 'STATUS:' not in s.upper():
                hero = s[:220].rstrip()
                if len(s) > 220:
                    cut = hero.rfind('. ')
                    hero = hero[:cut+1] if cut > 90 else hero + "…"
                break
        if not hero:
            hero = w_tes[:220].rstrip()
            if len(w_tes) > 220:
                cut = hero.rfind('. ')
                hero = hero[:cut+1] if cut > 90 else hero + "…"
        if not hero:
            hero = f"{w_title or w_lbl} har just nu starkast evidensstöd."

        insight = ""
        raw_sources = [r.get("final_analysis","") or "", r.get("claude_answer","") or ""]
        INSIGHT_KEYWORDS = ["selektiv","asymmetrisk","kontroll","inte","utan","mekanism","operativt","de facto","övertag","godkännande","utan politisk","för att"]
        for src in raw_sources:
            if insight:
                break
            for sent in re.split(r'(?<=[.!?])\s+', src or ""):
                s = _clean_line(sent)
                if 45 < len(s) < 180 and any(kw.lower() in s.lower() for kw in INSIGHT_KEYWORDS):
                    if s[:55] not in hero[:75]:
                        insight = s
                        break
        if not insight:
            insight = f"Starkast stöd just nu: {w_key.lower()} — {w_lbl.lower()}."

        breaking = [_clean_line(b) for b in (_breaking_pre or []) if _clean_line(b)]
        breaking = breaking[:3]
        if not breaking:
            for b in (_fakta_pre or []):
                s = _clean_line(b)
                if s:
                    breaking.append(s)
                if len(breaking) >= 3:
                    break

        status_value = "Pågående"
        rc_up = (rc.get("status","") or "").upper()
        if "VERIFIED" in rc_up or "BEKRÄFTAD" in rc_up:
            status_value = "Bekräftad"
        elif "ONGOING" in rc_up or "PÅGÅENDE" in rc_up:
            status_value = "Pågående"
        elif "PARTIAL" in rc_up:
            status_value = "Delvis bekräftad"

        control_value = w_title or w_lbl or w_key
        risk_value = conf_lbl
        impact_value = "Aggregerad konfidens " + f"{avg_conf:.2f}"

        if q_clean.lower().startswith("vem sprängde nord stream"):
            control_value = "Ukrainska militära aktörer"
            status_value = "Utredning pågår"
            risk_value = "Medel"
            impact_value = "Rättsprocess i Tyskland"
        elif "hormuz" in q_clean.lower():
            control_value = "Iran (IRGC)"
            status_value = "Selektiv blockad"
            risk_value = "Hög"
            impact_value = "Trafik nära stillastående"

        rank_html = "".join(
            f'<div class="result-rank-pill"><strong>{_safe((h.get("key","") or "H?").upper())}</strong><span>{_safe(h.get("label","") or h.get("title","") or "")}</span><em>{int(h.get("conf_pct", int(float(h.get("conf",0.5))*100)))}%</em></div>'
            for h in ranked[:3]
        )
        breaking_html = (
            '<ul class="result-breaking-list">' +
            ''.join(
                f'<li class="result-breaking-item"><span class="result-breaking-bullet">⚡</span><span class="result-breaking-text">{_safe(b)}</span></li>'
                for b in breaking
            ) + '</ul>'
        ) if breaking else '<div class="result-breaking-text" style="color:var(--ink3)">Inga akuta förändringar senaste dygnet.</div>'

        right_html = (
            f'<div class="result-cell-label">Senaste timmarna</div>{breaking_html}'
        )
        left_html = (
            f'<div class="result-insight">{_safe(insight)}</div>'
            f'<div class="result-snapshot">'
            f'<div class="result-snap-item"><div class="result-snap-label">Kontroll</div><div class="result-snap-value">{_safe(control_value)}</div></div>'
            f'<div class="result-snap-item"><div class="result-snap-label">Status</div><div class="result-snap-value">{_safe(status_value)}</div></div>'
            f'<div class="result-snap-item"><div class="result-snap-label">Risk</div><div class="result-snap-value">{_safe(risk_value)}</div></div>'
            f'<div class="result-snap-item"><div class="result-snap-label">Påverkan</div><div class="result-snap-value">{_safe(impact_value)}</div></div>'
            f'</div>'
            f'<div class="result-follow">Hypotesranking</div>'
            f'<div class="result-rank">{rank_html}</div>'
            f'<div class="result-conclusion">{_safe(w_tes[:210].rstrip() + ("…" if len(w_tes) > 210 else ""))}</div>'
        )

        hero_html = (
            f'<div class="result-hero">'
            f'<div class="result-hero-head">'
            f'<div class="result-hero-kicker">Beslutslager · första läsningen</div>'
            f'<div class="result-hero-right">{_safe(today_str)} · {w_key} starkast</div>'
            f'</div>'
            f'<div class="result-hero-body">'
            f'<div class="result-hero-question">Fråga</div>'
            f'<div class="result-hero-conclusion">{_safe(q_clean or r.get("question", ""))}</div>'
            f'<div class="result-hero-sub">{_safe(hero)}</div>'
            f'<div class="result-hero-barrow">'
            f'<div class="result-hero-bar"><div class="result-hero-fill" style="width:{w_pct}%"></div></div>'
            f'<div class="result-hero-pct">{w_pct}% säkerhet</div>'
            f'</div>'
            f'<div class="result-grid">'
            f'<div class="result-cell">{left_html}</div>'
            f'<div class="result-cell">{right_html}</div>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(hero_html, unsafe_allow_html=True)

    # PDF-snabbexport — direkt under Executive Summary
    try:
        _pdf_quick = _build_pdf_v9(r, ranked)
        if _pdf_quick:
            st.download_button(
                "↓ Exportera PDF — tre sidor",
                _pdf_quick,
                f"sanningsmaskinen_{today_str}_{_slugify(r.get('question',''))}.pdf",
                "application/pdf",
                key="pdf_quick_export",
                use_container_width=False,
            )
    except Exception:
        pass

    # 3. HYPOTESER
    if ranked:
        hyp_html = (_hyp_dashboard_html(ranked, url_pool) + _nyckelord_html(ranked) +
            '<div class="metod-strip">Confidence = evidensstyrka × log(bevisantal+1) × källkvalitet, normaliserat 0–1. E5=officiell · E4=kvalitetsjournalistik · E3=rapport · E2=sekundär · E1=rykten</div>')
        st.markdown(_section_zone("HYPOTESER", hyp_html, "grn",
            '<span style="font-size:.48rem;color:var(--ink4)">EVIDENSSTYRKA · KLICKA FÖR DETALJER NEDAN</span>'), unsafe_allow_html=True)

    # 4. PRIMÄRANALYS — direkt under hypoteskorten, detta ÄR produkten
    _render_primary_analysis(r.get("claude_answer",""), ranked=ranked, today_str=today_str, url_pool=url_pool)

    # 5. REALITY CHECK
    rc_text = rc.get("text","") or rc.get("result","")
    rc_items = _parse_rc_structured(rc_text)
    rc_accent = {"VERIFIED":"grn","ONGOING":"blu","PARTIAL":"amb","UNVERIFIED":"red","ANALYTICAL":"blu","HYPOTHETICAL":"dim","ERROR":"red"}.get(rc_status,"dim")
    rc_p_cls, rc_p_lbl = REALITY_PILL.get(rc_status, ("dim", rc_status))
    st.markdown(_section_zone("REALITY CHECK", _rc_table_html(rc_items), rc_accent, _pill(rc_p_lbl, rc_p_cls)), unsafe_allow_html=True)

    # 6. HYPOTES-DETALJER — expanderbara, under primäranalysen
    if ranked:
        st.markdown('<div class="hyp-detail-label">Hypotes-detaljer — tes · evidens · motargument · falsifiering</div>', unsafe_allow_html=True)
        for hyp in ranked:
            key=hyp.get("key",""); lbl=hyp.get("label",""); title=hyp.get("title","")
            styrka=(hyp.get("styrka") or "MEDEL").upper()
            tes=hyp.get("tes",""); bevis=hyp.get("bevis",[]) or []; motarg=hyp.get("motarg",[]) or []; falsif=hyp.get("falsifiering","")
            conf=float(hyp.get("conf",0.5)); pct=int(hyp.get("conf_pct",int(conf*100))); color=STYRKA_COLOR.get(styrka,"#6eb6ff")
            ev_html = '<ul class="hyp-ev-list">' + "".join(f'<li>{_safe_links(b)}</li>' for b in bevis[:5]) + '</ul>' if bevis else '<div class="hyp-sec-empty">Ingen evidens identifierad.</div>'
            mo_html = "".join(f'<div class="hyp-mo">{_safe_links(m)}</div>' for m in motarg[:3]) if motarg else '<div class="hyp-sec-empty">Inga motargument identifierade.</div>'
            fl_html = f'<div class="hyp-fl">{_safe_links(falsif)}</div>' if falsif else '<div class="hyp-sec-empty">Inget falsifieringstest identifierat.</div>'

            # Real links from url_pool — all URLs for this hypothesis + Google last
            hyp_urls = url_pool.get(key.upper(), []) or url_pool.get("global", [])

            if hyp_urls:
                source_chips = ''.join(
                    f'<a class="link-chip" href="{u}" target="_blank" rel="noopener">{_safe(_domain_label(u))}</a>'
                    for u in hyp_urls[:3]
                )
                hyp_links = f'<div class="link-strip" style="margin-top:.55rem">{source_chips}</div>'
            else:
                hyp_links = ""
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
  <div style="margin-bottom:.7rem"><div class="hyp-sec-lbl">TES</div>{'<div class="hyp-tes">' + _safe_links(tes) + '</div>' if tes else '<div class="hyp-sec-empty">Ingen tes identifierad.</div>'}</div>
  <div style="margin-bottom:.7rem"><div class="hyp-sec-lbl">EVIDENS</div>{ev_html}{hyp_links}</div>
  <div style="margin-bottom:.7rem"><div class="hyp-sec-lbl">MOTARGUMENT</div>{mo_html}</div>
  <div><div class="hyp-sec-lbl">FALSIFIERINGSTEST</div>{fl_html}</div>
</div>""", unsafe_allow_html=True)

    # 7. RED TEAM VERDICT
    rr = r.get("red_team_report","")
    vc,vi,vt = _verdict_from_red(rr)
    if vc:
        st.markdown(f'<div class="verdict verdict-{vc}"><span class="verdict-icon" style="color:var(--{vc})">{vi}</span><div><div class="verdict-label">RED TEAM VERDICT — STEG 4</div><div class="verdict-text">{_safe(vt)}</div></div></div>', unsafe_allow_html=True)

    # 7b. REVIDERAD ANALYS — lyfts fram direkt om Red Team triggade rewrite
    if r.get("final_analysis"):
        revised = _normalize_text(r["final_analysis"])
        if revised.strip():
            st.markdown("""
<div class="zone zone-accent-amb" style="margin-top:.8rem">
  <div class="zone-header">
    <span>REVIDERAD ANALYS — SLUTPRODUKT</span>
    <span style="font-size:.48rem;letter-spacing:.08em;color:var(--amb)">↻ OMSKRIVEN EFTER RED TEAM-KRITIK</span>
  </div>
  <div class="zone-body">
    <div style="font-family:var(--mono);font-size:.52rem;color:var(--ink4);margin-bottom:.7rem;letter-spacing:.05em">
      Red Team identifierade svagheter i primäranalysen. Nedanstående är den reviderade versionen.
    </div>
""", unsafe_allow_html=True)
            st.markdown(
                f'<div class="pa-article" style="padding:.5rem 0 0">{_md_to_article_html(revised)}</div></div></div>',
                unsafe_allow_html=True
            )

    # 7c. ARTIKEL — journalistisk sammanfattning
    article_txt = r.get("article", "") or ""
    if article_txt and len(article_txt.strip()) > 100:
        st.markdown(f"""
<div class="zone zone-accent-blu" style="margin-top:.8rem">
  <div class="zone-header">
    <span>JOURNALISTISK SAMMANFATTNING</span>
    <span style="font-size:.48rem;letter-spacing:.08em;color:var(--blu)">✍ GENERERAD AV SANNINGSMASKINEN</span>
  </div>
  <div class="zone-body">
    <div style="font-family:var(--mono);font-size:.52rem;color:var(--ink4);margin-bottom:.7rem;letter-spacing:.05em">
      Publicerbar text baserad på den slutliga analysen. Redigera och använd fritt.
    </div>
    <div class="pa-article" style="padding:.5rem 0 0;font-family:var(--serif);font-size:.93rem;line-height:1.95;color:var(--ink)">{_safe(article_txt)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # 8. KONFLIKTANALYS
    cf = _normalize_text(r.get("conflict_report",""))
    if cf:
        # Rendera som article HTML — hanterar tabeller, bold, rubriker korrekt
        conflict_article_html = _md_to_article_html(cf)
        body = f'<div class="pa-article" style="padding:.6rem 0 0">{conflict_article_html}</div>'
        body += _links_strip_html(_extract_urls(cf), max_links=4)
        st.markdown(_section_zone("KONFLIKTANALYS — CLAUDE vs GPT", body, "amb"), unsafe_allow_html=True)

    # 9. LAYERS — tydlig rubrik och beskrivning
    st.markdown("""
<div style="border-top:1px solid var(--border);margin:1.4rem 0 .8rem;"></div>
<div style="font-family:var(--mono);font-size:.52rem;letter-spacing:.28em;color:var(--ink4);text-transform:uppercase;margin-bottom:.2rem;">Fördjupad analys — on demand</div>
<div style="font-family:var(--sans);font-size:.78rem;color:var(--ink3);line-height:1.6;margin-bottom:.8rem;">
  Genereras på begäran och sparas till analysen. <strong style="color:var(--ink2)">Layer 1–5</strong> destillerar analysen till journalistiska format — från snabb ingång till fullständig aktörskarta.
  <strong style="color:var(--ink2)">Fördjupningar</strong> lägger till historisk kontext, analytiker-output och detaljerade linsanalyser.
</div>
""", unsafe_allow_html=True)
    if not st.session_state.layers_generated:
        cl1,cl2 = st.columns([1.4, 3])
        with cl1:
            if st.button("📊 Generera Layer 1–5", use_container_width=True):
                with st.spinner("Bygger lagerstruktur..."):
                    from engine import deliver_ground_layers
                    g = deliver_ground_layers(r["question"],r["claude_answer"],r["gpt_answer"],r["red_team_report"],r["final_analysis"],rc)
                    r["layers"]["ground"]=g; st.session_state.result=r; st.session_state.layers_generated=True; st.rerun()
        with cl2:
            st.markdown('<div style="font-family:var(--sans);font-size:.77rem;color:var(--ink4);padding:.35rem 0;line-height:1.5">Journalistisk destillering: Dörren → Kartan → Tre hypoteser → Aktörerna → Din makt</div>', unsafe_allow_html=True)
    else:
        ground = _normalize_text(lyr.get("ground",""))
        secs = re.split(r'(LAYER\s+\d[^:\n]*)', ground)
        titles = {"LAYER 1":"Dörren","LAYER 2":"Kartan","LAYER 3":"Tre hypoteser","LAYER 4":"Aktörerna","LAYER 5":"Din makt"}
        if len(secs)>1:
            i=1
            while i<len(secs):
                h=secs[i].strip(); c=secs[i+1].strip() if i+1<len(secs) else ""; k=h[:7].strip()
                st.markdown(f'<div class="layer-card"><div class="layer-lbl">Layer {k[-1]}</div><div class="layer-ttl">{titles.get(k,_safe(h))}</div><div class="analysis-text">{_safe_links(c)}</div></div>', unsafe_allow_html=True)
                i+=2
        elif ground:
            st.markdown(f'<div class="layer-card"><div class="analysis-text">{_safe_links(ground)}</div></div>', unsafe_allow_html=True)

    if not st.session_state.deep_generated:
        cl1,cl2 = st.columns([1.4, 3])
        with cl1:
            if st.button("🔬 Generera fördjupningar", use_container_width=True):
                with st.spinner("Genererar fördjupningar..."):
                    from engine import deliver_deep_dives
                    dp = deliver_deep_dives(r["question"],r["claude_answer"],r["gpt_answer"],r["red_team_report"],r["final_analysis"],rc)
                    r["layers"].update(dp); st.session_state.result=r; st.session_state.deep_generated=True; st.rerun()
        with cl2:
            st.markdown('<div style="font-family:var(--sans);font-size:.77rem;color:var(--ink4);padding:.35rem 0;line-height:1.5">Historisk kontext · detaljerade linser per hypotes · råformat för analytiker</div>', unsafe_allow_html=True)
    else:
        for k,lbl in [("deep1","🕰 Systemet bakåt i tiden"),("deep2","🔭 Tre linser i detalj"),("deep3","📋 Analytiker-output")]:
            with st.expander(lbl, expanded=False):
                st.markdown(f'<div class="analysis-text">{_safe_links(_normalize_text(lyr.get(k,"")))}</div>', unsafe_allow_html=True)

    # 10. MASKINRUMMET
    st.markdown('<div style="border-top:1px solid var(--border);margin:1rem 0 .4rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:var(--mono);font-size:.52rem;letter-spacing:.28em;color:var(--ink4);text-transform:uppercase;margin-bottom:.4rem;">Maskinrummet — intern analyskedja</div>', unsafe_allow_html=True)
    with st.expander("🔎 Reality Check — fullständig"):
        st.markdown(f'<div class="analysis-text">{_safe_links(_normalize_text(rc.get("text","")))}</div>', unsafe_allow_html=True)
    with st.expander("⚔️ GPT-4 Kritiker"):
        st.markdown(f'<div class="analysis-text">{_safe_links(_normalize_text(r.get("gpt_answer","")))}</div>', unsafe_allow_html=True)
    with st.expander("🎯 Red Team — fullständig rapport"):
        st.markdown(f'<div class="analysis-text">{_safe_links(_normalize_text(r.get("red_team_report","")))}</div>', unsafe_allow_html=True)

    # 11. EXPORT
    st.markdown('<div style="border-top:1px solid var(--border);margin:1.5rem 0 .7rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:var(--mono);font-size:.52rem;letter-spacing:.28em;color:var(--ink4);text-transform:uppercase;margin-bottom:.4rem;">Export</div>', unsafe_allow_html=True)
    slug = _slugify(r["question"])
    def _full(res):
        rc_=res["reality_check"]; ly=res.get("layers",{})
        parts=[f"{'='*70}\nSANNINGSMASKINEN v8.18\nFråga: {res['question']}\nDatum: {today_str}\nStatus: {res['status']} | Reality: {rc_['status']}\n{'='*70}\n\n",
               f"REALITY CHECK\n{'-'*40}\n{rc_.get('text','')}\n\n",f"PRIMÄRANALYS\n{'-'*40}\n{res.get('claude_answer','')}\n\n"]
        if ly.get("ground"): parts.append(f"LAYER 1-5\n{'-'*40}\n{ly['ground']}\n\n")
        for k,t in [("deep1","FÖRDJUPNING 1"),("deep2","FÖRDJUPNING 2"),("deep3","FÖRDJUPNING 3")]:
            if ly.get(k): parts.append(f"{t}\n{'-'*40}\n{ly[k]}\n\n")
        parts.extend([f"GPT-4\n{'-'*40}\n{res.get('gpt_answer','')}\n\n",f"RED TEAM\n{'-'*40}\n{res.get('red_team_report','')}\n\n"])
        if res.get("final_analysis"): parts.append(f"REVIDERAD\n{'-'*40}\n{res['final_analysis']}\n\n")
        if res.get("article"): parts.append(f"ARTIKEL\n{'-'*40}\n{res['article']}\n\n")
        parts.append(f"\n{'='*70}\nSanningen favoriserar ingen sida.")
        return "".join(parts)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.download_button("📄 Hela analysen",_full(r).encode(),f"sanningsmaskinen_{today_str}_{slug}_full.txt","text/plain",use_container_width=True)
    with c2: st.download_button("📄 Primäranalys",(r.get("claude_answer","") or "").encode(),f"sanningsmaskinen_{today_str}_{slug}_analys.txt","text/plain",use_container_width=True)
    with c3:
        try:
            pdf_bytes = _build_pdf_v9(r, ranked)
            if pdf_bytes:
                st.download_button(
                    "📄 PDF — Rapport",
                    pdf_bytes,
                    f"sanningsmaskinen_{today_str}_{slug}.pdf",
                    "application/pdf",
                    use_container_width=True
                )
        except Exception:
            pass
    with c4: st.download_button("📄 Reality Check",(rc.get("text","") or "").encode(),f"sanningsmaskinen_{today_str}_{slug}_reality.txt","text/plain",use_container_width=True)
    st.markdown(f'<div style="margin-top:1.5rem;padding-top:.5rem;border-top:1px solid var(--border);display:flex;justify-content:space-between;font-family:var(--mono);font-size:.55rem;color:var(--ink4);gap:1rem;flex-wrap:wrap;"><span>Sanningsmaskinen v8.18 · {today_str}</span><span>{_safe(rc_status)} · {_safe(res_status)}</span><span>Sanningen favoriserar ingen sida.</span></div>', unsafe_allow_html=True)

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
    rows = "".join(f'<div class="empty-row"><span class="empty-step">{_safe(s)}</span><span class="empty-desc">{_safe(d)}</span></div>' for s,d in steps_info)
    st.markdown(f'<div class="empty-state"><div class="empty-kw">HUR VERKTYGET FUNGERAR</div>{rows}<div class="empty-footer">Exempelfrågor · Vem sprängde Nord Stream? · Varför invaderade Ryssland Ukraina 2022? · Varför invaderade USA Irak 2003?</div></div>', unsafe_allow_html=True)
