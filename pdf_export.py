# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN — PDF Export v15.0
UI-matchad design: samma färgpalett, typografi och känsla som Streamlit-gränssnittet.
Spectral (serif) + JetBrains Mono — söks på Mac och Linux automatiskt.
"""
import re, io, os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Font loader — söker Mac → Linux → fallback ────────────────────────────────
def _find_font(candidates):
    """Hitta första existerande fontfil ur lista av sökvägar."""
    home = os.path.expanduser("~")
    for p in candidates:
        full = p.replace("~", home)
        if os.path.exists(full): return full
    return None

# Spectral — exakt samma serif som UI (Google Fonts → ofta i ~/Library/Fonts)
_SPECTRAL_R = _find_font([
    "~/Library/Fonts/Spectral-Regular.ttf",
    "~/Library/Fonts/Spectral/Spectral-Regular.ttf",
    "/Library/Fonts/Spectral-Regular.ttf",
    "/usr/share/fonts/truetype/spectral/Spectral-Regular.ttf",
    # Fallback: DejaVu Serif (liknande känsla)
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
])
_SPECTRAL_B = _find_font([
    "~/Library/Fonts/Spectral-Bold.ttf",
    "~/Library/Fonts/Spectral/Spectral-Bold.ttf",
    "/Library/Fonts/Spectral-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
])
_SPECTRAL_I = _find_font([
    "~/Library/Fonts/Spectral-Italic.ttf",
    "~/Library/Fonts/Spectral/Spectral-Italic.ttf",
    "/Library/Fonts/Spectral-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
])

# JetBrains Mono — exakt samma mono som UI
_JBM_R = _find_font([
    "~/Library/Fonts/JetBrainsMono-Regular.ttf",
    "~/Library/Fonts/JetBrainsMono/JetBrainsMono-Regular.ttf",
    "~/Library/Fonts/JetBrainsMono[wght].ttf",
    "/Library/Fonts/JetBrainsMono-Regular.ttf",
    "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf",
    # Fallback: DejaVu Sans Mono (närmaste match)
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
])
_JBM_B = _find_font([
    "~/Library/Fonts/JetBrainsMono-Bold.ttf",
    "~/Library/Fonts/JetBrainsMono/JetBrainsMono-Bold.ttf",
    "/Library/Fonts/JetBrainsMono-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
])

# Registrera fonter
def _reg(name, path, fallback=None):
    try:
        if path:
            pdfmetrics.registerFont(TTFont(name, path)); return True
    except Exception: pass
    if fallback:
        try:
            pdfmetrics.registerFont(TTFont(name, fallback)); return True
        except Exception: pass
    return False

_has_serif = _reg("SERIF",  _SPECTRAL_R) and _reg("SERIFB", _SPECTRAL_B) and _reg("SERIFI", _SPECTRAL_I)
_has_mono  = _reg("MONO_R", _JBM_R)      and _reg("MONO_B", _JBM_B)

# Typsnittsvariabler — matchar UI:ts var(--serif) / var(--mono)
SERIF  = "SERIF"  if _has_serif else "Times-Roman"
SERIFB = "SERIFB" if _has_serif else "Times-Bold"
SERIFI = "SERIFI" if _has_serif else "Times-Italic"
MONO   = "MONO_R" if _has_mono  else "Courier"
MONOB  = "MONO_B" if _has_mono  else "Courier-Bold"

# Sans-serif för brödtext (UI: Libre Franklin → närmaste: DejaVu Sans / Helvetica)
_SANS_R = _find_font([
    "~/Library/Fonts/LibreFranklin-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
])
_SANS_B = _find_font([
    "~/Library/Fonts/LibreFranklin-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
])
_has_sans = _reg("SANS_R", _SANS_R) and _reg("SANS_B", _SANS_B)
BODY  = "SANS_R" if _has_sans else "Helvetica"
BOLD  = "SANS_B" if _has_sans else "Helvetica-Bold"
ITAL  = SERIFI   # Kursiv = serif italic = som UI

# ── Färgpalett — EXAKT matchad mot UI CSS-variabler ───────────────────────────
# UI: --bg:#0a0b0d  --bg1:#0f1115  --bg2:#141821  --bg3:#1b2230
BG    = colors.HexColor("#0a0b0d")   # --bg
BG2   = colors.HexColor("#0f1115")   # --bg1
BG3   = colors.HexColor("#141821")   # --bg2
BG4   = colors.HexColor("#1b2230")   # --bg3
# UI: --border:#242c3a  --border2:#303a4c
RULE  = colors.HexColor("#242c3a")   # --border
RULE2 = colors.HexColor("#303a4c")   # --border2
# UI: --ink:#f2efe8  --ink2:#d7d0c4  --ink3:#b3ad9f  --ink4:#7f8898
INK   = colors.HexColor("#f2efe8")   # --ink
INK2  = colors.HexColor("#d7d0c4")   # --ink2
INK3  = colors.HexColor("#b3ad9f")   # --ink3
INK4  = colors.HexColor("#7f8898")   # --ink4
# UI: --grn:#57c78a  --grn-bg:#0a1711  --grn-dim:#1e4a34
GRN   = colors.HexColor("#57c78a")   # --grn
GDIM  = colors.HexColor("#1e4a34")   # --grn-dim
GBKG  = colors.HexColor("#0a1711")   # --grn-bg
# UI: --amb:#e2b04c  --amb-bg:#171205  --amb-dim:#5e4518
AMB   = colors.HexColor("#e2b04c")   # --amb
ADIM  = colors.HexColor("#5e4518")   # --amb-dim
ABKG  = colors.HexColor("#171205")   # --amb-bg
# UI: --red:#db6b57  --red-bg:#180b0a  --red-dim:#5b2620
RED   = colors.HexColor("#db6b57")   # --red
RDIM  = colors.HexColor("#5b2620")   # --red-dim
RBKG  = colors.HexColor("#180b0a")   # --red-bg
# UI: --blu:#6eb6ff  --blu-bg:#0a1220  --blu-dim:#23486d
BLU   = colors.HexColor("#6eb6ff")   # --blu
BDIM  = colors.HexColor("#23486d")   # --blu-dim
BBKG  = colors.HexColor("#0a1220")   # --blu-bg
# Admin/PDF gold — matchar admin-vyns rubrikfärg
GOLD  = colors.HexColor("#c8a96e")   # --gold (PDF + admin headings)

W, H     = A4
ML       = 48
MR       = W - 48
TW       = MR - ML
SEC_GAP  = 30
EL_GAP   = 13
PAD      = 14
FLOOR_P1 = 50
FLOOR_P2 = 50
FLOOR_P3 = 50


# ═══════════════════════════════════════════════════════════════════════════════
# CONTENT EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

_NOISE = re.compile(
    r"^(?:"
    # AI/process language
    r"I'?ll search|let me search|I will search|searching for|"
    r"jag börjar|jag söker|låt mig söka|jag ska|"
    r"denna analys|this analysis|denna rapport|"
    # Engine headers
    r"SANNINGSMASKINEN\s+v\d|Datum:\s+20\d\d|"
    r"STATUS:\s+(?:PÅGÅENDE|KLAR|REVIDERAD|ONGOING)|"
    r"KONFIDENSGRAD:|REVIDERAD VERSION|LÄGESRAPPORT|"
    r"DAG\s+\d+\s*\||IRAN HAR DE FACTO KONTROLL\s*\.?\s*$|"
    r"INSTRUKTION:|INTEGRERA DESSA|BREAKING\s*—\s*SENASTE|"
    # Pågående/tidskänslig markers
    r"\[PÅGÅENDE|PÅGÅENDE\s*—|tidskänslig|ny deadline|"
    # Claude/system references
    r"claude|claude:s|gpt|analysmotor|pipeline|"
    r"primäranalysen håller inte|analysen håller inte|"
    # Internal verdict phrasing
    r"claude:s analys|min analys|vår analys"
    r")",
    re.IGNORECASE
)

def _clean(txt):
    if not txt: return ""
    t = str(txt)
    t = re.sub(r'\[([^\]]+)\]\(https?://[^\)]+\)', r'\1', t)
    t = re.sub(r'https?://\S+', '', t)
    t = re.sub(r'\*{1,3}', '', t)
    t = re.sub(r'^#{1,6}\s*', '', t, flags=re.MULTILINE)
    # Remove bracketed engine tags
    t = re.sub(r'\[(?:FAKTA|INFERENS|DEBATTERAD TOLKNING|PÅGÅENDE[^\]]*|HYPOTETISKT|REVIDERAD VERSION)\]',
               '', t, flags=re.I)
    t = re.sub(r'[⚡🚨🔴📊🔍🧠⚠️🏆💥🟢🔵◈◉◇▸›•·■●◎⟳◷▲]', '', t)
    # Remove engine status lines embedded in text
    t = re.sub(r'#\s*[A-ZÅÄÖ\s]+—\s*LÄGESRAPPORT[^\n]*', '', t)
    t = re.sub(r'STATUS:\s*[A-ZÅÄÖ\s—]+\n', '', t, flags=re.I)
    return t.strip()

def _ok_line(s):
    s = s.strip()
    return (bool(s) and len(s) > 10
            and not _NOISE.match(s)
            and not (s.startswith('|') and s.count('|') >= 2))

def _trunc(txt, n):
    """Trunkera vid sista hela meningen inom n+30 tecken. Aldrig '…'."""
    t = _clean(txt)
    if not t: return ""
    if len(t) <= n: return t
    # Hitta SISTA meningsgränsen inom n+30 (lite slack för att fånga hel mening)
    extended = t[:n + 30]
    last_end = -1
    for m in re.finditer(r'[.!?](?:\s|$)', extended):
        if m.end() <= n + 30:
            last_end = m.end()
    if last_end > n * 0.5:
        return t[:last_end].rstrip()
    # Ingen meningsgräns inom rimlig räckvidd — ta sista hela ordet och avsluta med punkt
    cut = t[:n]
    sp = cut.rfind(' ')
    base = (t[:sp] if sp > 0 else cut).rstrip().rstrip('.,;:—-')
    return base + '.'

def _sentences(text, min_l=35, max_l=260):
    for s in re.split(r'(?<=[.!?])\s+', _clean(text)):
        s = s.strip()
        if min_l <= len(s) <= max_l and _ok_line(s):
            yield s

def _first_sent(text, min_l=35, max_l=260):
    return next(_sentences(text, min_l, max_l), "")

# ── HERO: answers the question directly — concrete real-world status ──────────
def _get_hero(r):
    if r.get("_hero_override"):
        return _trunc(r["_hero_override"], 380)

    STATUS_WORDS = re.compile(
        r'(?:är|blockerad|stängt|öppet|kontrollerar|pågår|bekräftad|'
        r'genomförde|utförde|sprängde|ockuperar|invaderade|styr|håller)',
        re.IGNORECASE
    )
    AVOID = re.compile(
        r'^(?:frågan är|det är oklart|osäkerheten|ingen har bevisat|'
        r'vi vet inte|fullständig tillskrivning|trots|dock|men |'
        r'although|however|the question|no one|'
        # Process-text
        r'jag börjar|jag söker|jag ska|låt mig|let me|i will search|searching|'
        r'denna analys|this analysis|nord stream-sabotaget —|sanningsmaskinen v|'
        r'senaste händelser|briefing|vad vi vet|lägesrapport|datum:)',
        re.IGNORECASE
    )

    def _collect(src, max_chars=380):
        """Hämta upp till 2-3 meningar från src som passar AVOID/STATUS."""
        out, total = [], 0
        for s in _sentences(src or "", 35, 220):
            if AVOID.match(s):
                continue
            out.append(s)
            total += len(s) + 1
            if total >= max_chars or len(out) >= 3:
                break
        return " ".join(out).strip()

    # Try article first — first status-affirming sentence + 1-2 follow-up sentences
    art = r.get("article","")
    if art:
        # Hitta första status-meningen och följ med 1-2 till
        sents = list(_sentences(art, 35, 220))
        for i, s in enumerate(sents):
            if not AVOID.match(s) and STATUS_WORDS.search(s):
                chosen = [s]
                for nxt in sents[i+1:i+3]:
                    if not AVOID.match(nxt):
                        chosen.append(nxt)
                return _trunc(" ".join(chosen), 380)

    # Try H1 tes (ranked[0] = starkaste)
    ranked = r.get("ranked") or []
    if ranked:
        tes = _clean(ranked[0].get("tes",""))
        s = _collect(tes, 380)
        if s:
            return _trunc(s, 380)

    # Fallback: collect 2-3 clean sentences
    for src in [art, r.get("insight",""), r.get("final_analysis","")]:
        s = _collect(src, 380)
        if s:
            return _trunc(s, 380)
    return ""

# ── KEY INSIGHT: mechanism — HOW the situation works ─────────────────────────
def _get_key_insight(r, hero=""):
    if r.get("_insight_override"):
        return _trunc(r["_insight_override"], 300)
    # TES från starkaste hypotesen — första 1-2 meningarna
    ranked = r.get("ranked") or []
    if ranked:
        tes = _clean(ranked[0].get("tes", ""))
        sentences = list(_sentences(tes, 20, 220))
        if sentences:
            joined = " ".join(sentences[:2])
            return _trunc(joined, 300)
    return ""
# ── BREAKING ─────────────────────────────────────────────────────────────────
def _get_breaking(r):
    # 1) Hämta från legacy strukturerat fält om det finns (gamla historikfiler)
    items = r.get("breaking_items") or []
    if items:
        return [_trunc(_clean(i), 180) for i in items[:4]]
    # 2) Föredra article (journalistisk sammanfattning) — första 2-3 starka meningarna
    art = r.get("article", "") or ""
    if art and len(art.strip()) > 100:
        result, seen = [], set()
        for s in _sentences(art, 40, 220):
            key = s[:50]
            if key in seen:
                continue
            seen.add(key)
            result.append(_trunc(s, 180))
            if len(result) >= 4:
                break
        if result:
            return result[:4]
    # 3) Fallback: sök i råtext efter BREAKING-format
    txt = (r.get("claude_answer") or "") + "\n" + (r.get("final_analysis") or "")
    result, seen = [], set()
    DATE_LINE = re.compile(r'^[-*]?\s*\d{1,2}\s+\w+\s+202[56][:\s]', re.IGNORECASE)
    for line in txt.split("\n"):
        s = line.strip()
        m = re.match(r'^BREAKING\s*\[[^\]]*\]\s*[:\-—]\s*(.+)', s, re.I)
        if m:
            item = _trunc(_clean(re.sub(r'\[.*?\]\(.*?\)', '', m.group(1))), 180)
            if len(item) > 30 and item not in seen:
                seen.add(item); result.append(item)
        elif DATE_LINE.match(s):
            item = _trunc(_clean(re.sub(r'^[-*]\s*', '', s)), 180)
            if len(item) > 30 and item not in seen:
                seen.add(item); result.append(item)
        if len(result) >= 4:
            break
    return result[:4]
# ── NARRATIVE PARAGRAPHS — strict noise filtering ────────────────────────────
def _get_paras(r, max_p=5):
    # Extra patterns that must never appear in narrative
    PARA_SKIP = re.compile(
        r'^(?:#{1,4}|BREAKING|SENASTE|TES\s*:|BEVIS|MOTARG|STYRKA|FALSIF|'
        r'\|---|H[1-4]\s*[\[\(]|STATUS:\s*[A-ZÅÄÖ]|DAG\s+\d+|'
        r'SELEKTIV\s+BLOCKAD|INTE\s+FULLSTÄNDIG|LÄGESRAPPORT)',
        re.I
    )
    def _para_ok(p):
        p = p.strip()
        return (len(p) > 55 and _ok_line(p)
                and not PARA_SKIP.match(p)
                and not re.match(r'^jag\s', p, re.I)
                and not re.match(r'^låt\s+mig\s', p, re.I))

    art = r.get("article","")
    if art and len(art.strip()) > 80:
        out = []
        for p in re.split(r'\n{2,}', _clean(art)):
            p2 = p.strip()
            if _para_ok(p2):
                out.append(_trunc(p2, 380))
        if len(out) >= 2: return out[:max_p]

    src  = r.get("final_analysis","") or r.get("claude_answer","")
    out, tot = [], 0
    for p in re.split(r'\n{2,}', src or ""):
        p2 = _clean(p).strip()
        if not _para_ok(p2): continue
        out.append(_trunc(p2, 340))
        tot += len(p2)
        if tot > 1000 or len(out) >= max_p: break
    return out

# ── SCENARIOS: 3 concrete real-world outcomes ────────────────────────────────
def _get_scenarios(r):
    ranked = r.get("ranked") or []

    out = []
    for i, h in enumerate(ranked[:3]):
        lbl = _trunc(_clean(h.get("label", f"Utfall {i+1}")), 40)
        if not lbl:
            lbl = f"Utfall {i+1}"
        # Föredra title + första meningen av tes för fyllig scenariobeskrivning
        title = _clean(h.get("title", ""))
        tes_first = _first_sent(_clean(h.get("tes", "")), 30, 200)
        if title and tes_first and title.lower() not in tes_first.lower():
            desc = f"{title}. {tes_first}"
        elif tes_first:
            desc = tes_first
        elif title:
            desc = title
        else:
            desc = "Se djupanalys för detaljer."
        desc = _trunc(desc, 220)
        if not _ok_line(desc):
            desc = "Se djupanalys för detaljer."
        out.append((lbl, desc))

    while len(out) < 3:
        out.append((f"Utfall {len(out)+1}", "Se djupanalys för detaljer."))
    return out[:3]

# ── VERDICT — clean external language, zero internal references ───────────────
def _get_verdict(r):
    txt = r.get("red_team_report","") or ""
    m   = re.search(r'VERDICT[:\s]+([^\n]+)', txt, re.I)
    if not m: return ""
    raw = re.sub(r'\*+','', m.group(1)).strip()
    orig_upper = raw.upper()

    # Strip internal verdict word completely
    raw = re.sub(r'^(?:KOLLAPSAR|MODIFIERAS|HÅLLER|JUSTERAS)[^—.]*[—.]?\s*', '', raw, flags=re.I).strip()
    # Remove any remaining internal/AI references
    raw = re.sub(r'claude[:\s\'s]*analys[^\.\,]*[\.\,]?', '', raw, flags=re.I).strip()
    raw = re.sub(r'analysen håller inte[^\.\,]*[\.\,]?', '', raw, flags=re.I).strip()
    raw = re.sub(r'primäranalysen håller inte[^\.\,]*[\.\,]?', '', raw, flags=re.I).strip()

    # External prefix based on verdict type
    if "KOLLAPSAR" in orig_upper:
        prefix = "Alternativ tolkning är välgrundad och bör beaktas."
    elif "MODIFIERAS" in orig_upper:
        prefix = "Primäranalysen håller med reservation."
    else:
        prefix = "Bedömningen är välgrundad."

    raw = raw.strip().lstrip('—').strip()
    if raw and len(raw) > 15 and not _NOISE.match(raw):
        raw = raw[0].upper() + raw[1:]
        return _trunc(f"{prefix} {raw}", 320)
    return prefix

def _get_facts(r):
    txt  = (r.get("final_analysis","") or "") + "\n" + (r.get("claude_answer","") or "")
    FACT = [r'\d+\s*(?:%|procent|dollar|fat|miljoner|miljarder|dagar|månader)',
            r'(?:stängt|blockad|passage|ultimatum|deadline|transitering|explosion|arrest)',
            r'(?:trupper|fartyg|missil|attack|dömd|gripen)',
            r'(?:IRGC|BGH|DIA|IMF|NATO|FN\b|ICC|FBI|CIA)']
    items, seen = [], set()
    for line in txt.split('\n'):
        s = _clean(line).strip()
        if len(s) < 38 or len(s) > 170: continue
        if not _ok_line(s): continue
        if re.match(r'^(?:#{1,4}|TES|BEVIS|MOTARG|STYRKA|FALSIF|H[1-4]\s*[\[\(])', s, re.I): continue
        key = s[:42]
        if key in seen: continue
        if any(re.search(p, s, re.I) for p in FACT):
            seen.add(key); items.append(_trunc(s, 135))
        if len(items) >= 4: break
    return items

def _get_urls(r):
    txt = (r.get("claude_answer","") or "") + "\n" + (r.get("final_analysis","") or "")
    seen, out = set(), []
    BAD = {'google.com','google.se','bing.com','yahoo.com'}
    for u in re.findall(r'https?://[^\s\)\]"\'<]+', txt):
        u = u.rstrip('.,;):')
        d = re.sub(r'https?://(www\.)?','',u).split('/')[0]
        if d not in seen and not any(b in d for b in BAD):
            seen.add(d); out.append(d)
    return out[:5]

def _ccol(pct):
    if pct >= 65: return GRN
    if pct >= 40: return AMB
    return RED

def _cdim(pct):
    if pct >= 65: return GDIM
    if pct >= 40: return ADIM
    return RDIM


# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class Doc:
    def __init__(self, buf):
        self.cv = canvas.Canvas(buf, pagesize=A4)
        self.cv.setTitle("Sanningsmaskinen — Intelligence Brief")
        self._pg = 0

    def _f(self, f, sz):   self.cv.setFont(f, sz)
    def _fc(self, c):      self.cv.setFillColor(c)
    def _sc(self, c, lw):  self.cv.setStrokeColor(c); self.cv.setLineWidth(lw)
    def _sw(self, s, f, sz): return self.cv.stringWidth(str(s), f, sz)

    def T(self, x, y, s, sz, col, f=BODY, a='l'):
        self._f(f, sz); self._fc(col)
        {'r': self.cv.drawRightString,
         'c': self.cv.drawCentredString}.get(a, self.cv.drawString)(x, y, str(s))

    def W(self, x, y, txt, sz, col, f=BODY, mw=None, lh=None, floor=50, mx=99):
        """Strict wrap. Never below floor. Never beyond mx lines."""
        if not txt: return y
        if mw is None: mw = MR - x
        if lh is None: lh = round(sz * 1.45)
        self._f(f, sz); self._fc(col)
        words = str(txt).split(); line = ""; n = 0
        for w in words:
            test = (line + " " + w).strip()
            if self._sw(test, f, sz) > mw:
                if n >= mx or y < floor: return y
                if line: self.cv.drawString(x, y, line)
                y -= lh; n += 1; line = w
            else:
                line = test
        if line and n < mx and y >= floor:
            self.cv.drawString(x, y, line); y -= lh
        return y

    def HL(self, y, x1=None, x2=None, col=RULE, lw=0.4):
        self._sc(col, lw); self.cv.line(x1 or ML, y, x2 or MR, y)

    def RECT(self, x, y, w, h, fc, sc=None, lw=0.4):
        self._fc(fc)
        if sc: self._sc(sc, lw); self.cv.rect(x, y, w, h, fill=1, stroke=1)
        else:  self.cv.rect(x, y, w, h, fill=1, stroke=0)

    def LBAR(self, x, y1, y2, col, lw=3.5):
        self._sc(col, lw); self.cv.line(x, y1, x, y2)

    def DOT(self, x, y, r=2, col=INK3):
        self._fc(col); self.cv.circle(x, y, r, fill=1, stroke=0)

    def LINK(self, x, y, w, h, url, label, sz=7, col=None):
        """Klickbar länk — understruken text + invisible linkRect."""
        if not url or not label: return
        fc = col or BLU
        self._f(MONO, sz); self._fc(fc)
        self.cv.drawString(x, y, label)
        sw = self._sw(label, MONO, sz)
        # Understrykning
        self._sc(fc, 0.4); self.cv.line(x, y-1, x+sw, y-1)
        # Klickbar yta
        self.cv.linkURL(str(url), (x, y-2, x+sw+2, y+sz+1), relative=0)

    def NP(self):
        if self._pg > 0: self._foot(); self.cv.showPage()
        self._pg += 1
        self.RECT(0, 0, W, H, BG)

    def _foot(self):
        today = date.today().strftime("%Y-%m-%d")
        self.HL(28, lw=0.3, col=RULE)
        self.T(ML, 17, f"Sanningsmaskinen · Intelligence Brief · {today}", 7, INK3, MONO)
        self.T(MR, 17, str(self._pg), 7, INK3, MONOB, 'r')

    def save(self): self._foot(); self.cv.save()

    def masthead(self, label, today, status=""):
        # Topbar — exakt som UI:ts topbar-mark + topbar-title
        self.T(ML,      H-22, "SANNINGSMASKINEN", 7.5, GOLD, MONOB)
        self.T(ML+118,  H-22, "Intelligence Brief", 7.5, INK3, MONO)
        self.T(MR,      H-22, today, 7.5, INK4, MONO, 'r')
        # Guldfärgad accentlinje — precis som admin-vyns rubrikfärg
        self.HL(H-29, lw=1.2, col=GOLD)
        # Sub-label (sidnamn) och status — som UI:ts topbar-sub
        self.T(ML, H-40, label, 6.5, INK4, MONO)
        if status:
            ed = {"VERIFIED":"● VERIFIED","ONGOING":"⟳ PÅGÅENDE","PARTIAL":"◑ DELVIS",
                  "ANALYTICAL":"○ ANALYTISK","HYPOTHETICAL":"○ HYPOTETISK",
                  "REVIDERAD":"~ REVIDERAD","KLAR":"+ KLAR"}.get(status.upper(), status)
            self.T(MR, H-40, ed, 6.5, INK3, MONOB, 'r')
        return H - 58

    def section_label(self, y, label, col=INK4):
        # Använder BODY (DejaVu Sans) — stöder svenska tecken till skillnad från Courier
        self.T(ML, y, label, 6.5, col, BOLD)
        return y - 11

    def divider(self, y, gap_above=6, gap_below=SEC_GAP):
        y -= gap_above
        self.HL(y, lw=0.35, col=RULE2)
        return y - gap_below


def _get_full_urls(r):
    """Returnerar lista av (domain_label, full_url) par."""
    txt = (r.get("claude_answer","") or "") + "\n" + (r.get("final_analysis","") or "")
    seen, out = set(), []
    BAD = {"google.com","google.se","bing.com","yahoo.com"}
    for u in re.findall(r'https?://[^\s\)\]\'"<]+', txt):
        u = u.rstrip(".,;):")
        d = re.sub(r'https?://(www\.)?','',u).split("/")[0]
        if d not in seen and not any(b in d for b in BAD) and len(d) > 4:
            seen.add(d)
            out.append((d, u))
    return out[:6]

def _draw_link_bar(doc, r):
    """Klickbara källchips i PDF-footern."""
    pairs = _get_full_urls(r)
    if not pairs: return
    doc.HL(48, lw=0.3, col=RULE2)
    doc.T(ML, 37, "KÄLLOR", 6, GOLD, MONOB)
    x = ML + 44
    for domain, url in pairs[:6]:
        label = domain[:22]
        sw = doc._sw(label, MONO, 6.5)
        if x + sw > MR - 4: break
        doc.LINK(x, 37, sw, 9, url, label, sz=6.5, col=BLU)
        x += sw + 10
        # Separator dot
        if x < MR - 20:
            doc._fc(INK4)
            doc.cv.circle(x-5, 39, 1, fill=1, stroke=0)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DECISION PAGE
# ═══════════════════════════════════════════════════════════════════════════════

def build_p1(doc, r):
    doc.NP()
    today  = date.today().strftime("%Y-%m-%d")
    rc_st  = (r.get("reality_check") or {}).get("status","")
    doc_st = r.get("status","")
    ranked = r.get("ranked") or []
    FL     = FLOOR_P1

    y = doc.masthead("BESLUTSSIDA · 1 / 3", today, doc_st or rc_st)

    # ── QUESTION — stor serif rubrik som UI:ts fraga-box ─────────────────────
    q = _trunc(r.get("question",""), 92)
    doc.T(ML, y, f"FRÅGA · {today}", 6.5, GOLD, MONO)
    y -= 14
    y = doc.W(ML, y, q, 22, INK, SERIFB, mw=TW, lh=28, floor=FL, mx=2)
    y -= EL_GAP
    doc.HL(y, lw=0.5, col=RULE2)
    y -= SEC_GAP

    # ── BREAKING ──────────────────────────────────────────────────────────────
    brk = _get_breaking(r)
    if brk and y > FL + 65:
        y = doc.section_label(y, "BREAKING · SENASTE TIMMARNA", RED)
        for item in brk:
            if y < FL + 28: break
            doc.DOT(ML+4, y+3.5, 2.2, RED)
            y = doc.W(ML+13, y, item, 9, INK2, SERIF,
                      mw=TW-15, lh=13.5, floor=FL, mx=3)
            y -= 5
        y = doc.divider(y, gap_above=8, gap_below=SEC_GAP)

    # ── HERO ASSESSMENT — utökad, 3-5 rader ──────────────────────────────────
    hero = _get_hero(r)
    if hero and y > FL + 70:
        bh = 100
        doc.RECT(ML, y-bh, TW, bh, GBKG)
        doc.LBAR(ML, y-bh, y+2, GOLD, 4)
        doc.T(ML+PAD, y-13, "ANALYTISK BEDÖMNING", 6.5, GOLD, BOLD)
        doc.W(ML+PAD, y-28, hero, 10, INK, SERIFB,
              mw=TW-PAD*2, lh=14, floor=y-bh+8, mx=5)
        y -= bh + 18

    # ── KEY INSIGHT — utökad, 2 meningar ─────────────────────────────────────
    insight = _get_key_insight(r, hero)
    if insight and y > FL + 40:
        ih = 48
        doc.LBAR(ML+2, y-ih+4, y+4, AMB, 2.5)
        doc.T(ML+12, y-9, "NYCKELINSIKT", 6.5, AMB, BOLD)
        doc.W(ML+12, y-22, insight, 9, AMB, SERIFI,
              mw=TW-14, lh=13, floor=y-ih+6, mx=3)
        y -= ih + 2
        y = doc.divider(y, gap_above=4, gap_below=18)

    # ── HYPOTES-RANKING — med tes-text under varje rad ───────────────────────
    if ranked and y > FL + 130:
        y = doc.section_label(y, "HYPOTES-RANKING", GOLD)
        BAR_W = TW * 0.36
        HCOLS_R = [GRN, AMB, RED]
        HDIMS_R = [GBKG, ABKG, RBKG]
        for i, h in enumerate(ranked[:3]):
            if y < FL + 50: break
            col  = HCOLS_R[i] if i < 3 else INK3
            dim  = HDIMS_R[i] if i < 3 else BG2
            pct  = int(h.get("conf_pct", int(h.get("conf",0.5)*100)))
            key  = h.get("key","")
            lbl  = h.get("label","")
            titl = _trunc(h.get("title",""), 80)
            tes_sent = _first_sent(_clean(h.get("tes","")), 30, 240)
            tes_short = _trunc(tes_sent, 200) if tes_sent else ""

            # Header-rad (key, label, title, bar, %)
            head_h = 26
            if i == 0:
                doc.RECT(ML, y-head_h+2, TW, head_h, dim)
                doc.LBAR(ML, y-head_h+2, y+4, col, 4)
                doc.T(ML+12, y-9, "#1", 7, col, MONOB)
            else:
                doc.T(ML+4, y-9, f"#{i+1}", 6.5, INK4, MONO)
            doc.T(ML+28, y-9, key, 9.5, col, MONOB)
            doc.T(ML+58, y-9, lbl, 7, col, MONO)
            doc.T(ML+58, y-19, titl, 8, INK2, SERIFB)
            # Bar
            bx = MR - BAR_W - 36
            doc.RECT(bx, y-13, BAR_W, 4, RULE2)
            doc.RECT(bx, y-13, max(4, BAR_W*pct/100), 4, col)
            doc.T(MR, y-10, f"{pct}%", 10.5 if i==0 else 9, col, MONOB, 'r')
            y -= head_h + 2

            # TES-text på egen rad UNDER header-raden
            if tes_short:
                tes_floor = y - 32
                y = doc.W(ML+28, y, tes_short, 7.5, INK3, SERIFI,
                          mw=TW-32, lh=10.5, floor=tes_floor, mx=2)
                y -= 6
            y -= 6
        y -= 4
        y = doc.divider(y, gap_above=6, gap_below=SEC_GAP)

    # ── SLUTSATS — multimening "Vad säga på mötet" ──────────────────────────
    concl_override = r.get("_conclusion_override","")
    concl = ""
    if concl_override:
        concl = _trunc(concl_override, 500)
    elif ranked:
        w = ranked[0]
        wpct  = int(w.get("conf_pct", int(w.get("conf",0.5)*100)))
        wkey  = w.get("key","")
        wlbl  = w.get("label","")
        wtes  = _first_sent(_clean(w.get("tes","")), 30, 280)
        wfals = _first_sent(_clean(w.get("falsifiering","")), 25, 220)
        wbevs = w.get("bevis") or []
        wbev_first = ""
        for b in wbevs:
            cand = _first_sent(_clean(str(b)), 30, 220)
            if cand:
                wbev_first = cand
                break
        parts = []
        if wtes:
            parts.append(f"{wkey} ({wlbl}, {wpct}%): {wtes}")
        if wbev_first:
            parts.append(f"Starkast stöd: {wbev_first}")
        if wfals:
            parts.append(f"Faller om: {wfals}")
        concl = _trunc(" ".join(parts), 600) if parts else ""
    if not concl:
        concl = _get_verdict(r) or "Se djupanalys för fullständig slutsats."
    if concl and y > FL + 40:
        doc.T(ML, y, "VAD SKA DU SÄGA PÅ MÖTET?", 6.5, GOLD, BOLD)
        y -= 11
        doc.W(ML, y, concl, 9.5, INK, SERIFB, mw=TW, lh=14, floor=FL, mx=8)

    _draw_link_bar(doc, r)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — NARRATIVE
# ═══════════════════════════════════════════════════════════════════════════════

def build_p2(doc, r):
    doc.NP()
    today = date.today().strftime("%Y-%m-%d")
    paras = _get_paras(r, max_p=5)
    scens = _get_scenarios(r)
    FL    = FLOOR_P2

    y = doc.masthead("NARRATIV · 2 / 3", today)

    doc.T(ML, y, "BAKGRUND & KONTEXT", 6.5, GOLD, BOLD)
    doc.HL(y-9, lw=0.6, col=GOLD)
    y -= 22

    # Headline — stor serif som UI:ts exec-slutsats
    q = _trunc(r.get("question",""), 76)
    y = doc.W(ML, y, q, 20, INK, SERIFB, mw=TW, lh=26, floor=FL, mx=2)
    y -= SEC_GAP

    # Intro — serif bold ingress som DN-artikel
    if paras and y > FL + 60:
        y = doc.W(ML, y, paras[0], 11, INK, SERIFB,
                  mw=TW, lh=17, floor=FL, mx=3)
        y -= EL_GAP + 4

    # Brödtext — serif regular som UI:ts pa-p
    for para in paras[1:4]:
        if y < FL + 75: break
        y = doc.W(ML, y, para, 10, INK2, SERIF,
                  mw=TW, lh=15, floor=FL+55, mx=4)
        y -= EL_GAP

    # Pullquote — som UI:ts exec-nyckel med amber vänsterlinje
    quote_override = r.get("_quote_override","")
    if y > FL + 60:
        if quote_override and _ok_line(quote_override):
            quote = _trunc(quote_override, 140)
        else:
            hero_key = _get_hero(r)[:50].lower()
            quote    = ""
            for p in paras[1:]:
                s = _first_sent(p, 40, 140)
                if s and s.lower()[:40] not in hero_key:
                    quote = s; break
        if quote and _ok_line(quote):
            y -= 10
            q_floor = max(FL, y-60)
            doc.RECT(ML, q_floor, TW, y+6-q_floor, ABKG)   # --amb-bg bakgrund
            doc.LBAR(ML+2, q_floor, y+6, AMB, 3)
            y = doc.W(ML+16, y, f'"{quote}"', 10.5, AMB, SERIFI,
                      mw=TW-20, lh=16, floor=q_floor, mx=3)
            y -= SEC_GAP

    # Scenarios — möjliga utfall med hypotetikels färger
    if scens and y > FL + 52:
        doc.HL(y, lw=0.4, col=RULE2); y -= SEC_GAP - 4
        y = doc.section_label(y, "MÖJLIGA UTFALL", GOLD)
        SCOL = [GRN, AMB, RED]
        for i, (lbl, desc) in enumerate(scens):
            if y < FL + 18: break
            col = SCOL[i % 3]
            doc.DOT(ML+4, y+3.5, 2.5, col)
            doc.T(ML+14, y, lbl, 8.5, col, BOLD)
            y -= 14
            y = doc.W(ML+14, y, desc, 9, INK2, SERIF,
                      mw=TW-16, lh=13, floor=FL, mx=4)
            y -= 12

    _draw_link_bar(doc, r)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — DEEP ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def build_p3(doc, r):
    doc.NP()
    ranked = r.get("ranked") or []
    today  = date.today().strftime("%Y-%m-%d")
    FL     = FLOOR_P3
    HCOLS  = [GRN, AMB, RED]

    y = doc.masthead("DJUPANALYS · 3 / 3", today)

    doc.T(ML, y, "HYPOTESANALYS", 6.5, GOLD, BOLD)
    doc.HL(y-9, lw=0.6, col=GOLD)
    y -= 22

    # ── H1 / H2 / H3 ─────────────────────────────────────────────────────────
    HDIM = [GBKG, ABKG, RBKG]   # --grn-bg, --amb-bg, --red-bg
    HBAR = [GDIM, ADIM, RDIM]   # --grn-dim, --amb-dim, --red-dim
    for i, h in enumerate(ranked[:3]):
        if y < FL + 105: break
        col  = HCOLS[i] if i < 3 else INK3
        dim  = HDIM[i]  if i < 3 else BG2
        bar  = HBAR[i]  if i < 3 else RULE2
        key  = h.get("key","")
        lbl  = h.get("label","")
        titl = _trunc(h.get("title", h.get("tes","")), 120)
        tes  = _trunc(h.get("tes",""), 400)
        bevs = [_trunc(_clean(b), 220) for b in (h.get("bevis") or [])[:3]
                if b and _ok_line(_clean(str(b)))]
        mot_raw = h.get("motarg") or []
        if isinstance(mot_raw, list):
            mot_raw = mot_raw[0] if mot_raw else ""
        mot  = _trunc(_clean(str(mot_raw)), 220)
        fals_raw = _clean(h.get("falsifiering",""))
        fals_raw = re.sub(r'\[PÅGÅENDE[^\]]*\]', '', fals_raw, flags=re.I).strip()
        fals_raw = re.sub(r'PÅGÅENDE\s*—[^\n]+', '', fals_raw, flags=re.I).strip()
        fals = _trunc(fals_raw, 180) if _ok_line(fals_raw) else ""
        pct  = int(h.get("conf_pct", int(h.get("conf",0.5)*100)))

        if not tes:   tes  = titl or "Hypotesen saknar specificerad tes."
        if not bevs:  bevs = ["Evidens ej specificerad i källmaterial."]
        if not mot:   mot  = "Inga identifierade motargument."
        if not fals:
            tes_raw = (h.get("tes","") or "").strip()
            if tes_raw:
                tes_short = tes_raw[:55].rstrip()
                if len(tes_raw) > 55:
                    tes_short = tes_short.rsplit(" ", 1)[0]
                fals = f"Om '{tes_short}...' falsifieras med primärkällebevis (E1/E2)."
            # else: fals stays empty — no placeholder shown

        # ── Header ────────────────────────────────────────────────────────────
        doc.RECT(ML, y-20, TW, 22, dim)
        doc.LBAR(ML, y-20, y+2, col, 4)
        doc.T(ML+12, y-10, key,  9, col, MONOB)
        doc.T(ML+38, y-10, lbl,  7, col, MONO)
        BAR_W = TW * 0.26
        bx = MR - BAR_W - 40
        doc.RECT(bx, y-7, BAR_W, 3, bar)
        doc.RECT(bx, y-7, max(3, BAR_W*pct/100), 3, col)
        doc.T(MR, y-10, f"{pct}%", 9, col, MONOB, 'r')
        y -= 26

        # ── Titel — serif ──────────────────────────────────────────────────────
        y = doc.W(ML, y, titl, 11, INK, SERIFB,
                  mw=TW*0.86, lh=15, floor=FL, mx=1)
        y -= 8

        # ── TES ───────────────────────────────────────────────────────────────
        doc.T(ML, y, "TES", 5.5, col, BOLD)
        y -= 10
        y = doc.W(ML+6, y, tes, 8.5, INK, SERIF,
                  mw=TW-8, lh=12, floor=FL, mx=2)
        y -= 8

        # ── BEVIS ─────────────────────────────────────────────────────────────
        if bevs and y > FL + 28:
            doc.T(ML, y, "BEVIS", 5.5, GRN, BOLD)
            y -= 10
            for b in bevs[:2]:   # max 2 bevis per hypotes för att spara plats
                if not b or y < FL + 10: break
                doc.DOT(ML+4, y+2.5, 1.8, GRN)
                y = doc.W(ML+12, y, b, 8, INK2, SERIF,
                          mw=TW-14, lh=11.5, floor=FL, mx=2)
                y -= 3
            y -= 4

        # ── MOTARGUMENT ───────────────────────────────────────────────────────
        if mot and y > FL + 22:
            doc.T(ML, y, "MOTARGUMENT", 5.5, AMB, BOLD)
            y -= 10
            y = doc.W(ML+6, y, mot, 8, AMB, SERIFI,
                      mw=TW-8, lh=11.5, floor=FL, mx=2)
            y -= 8

        # ── FALSIFIERAS OM ────────────────────────────────────────────────────
        if fals and fals != "---" and y > FL + 16:
            doc.T(ML, y, "FALSIFIERAS OM", 5.5, INK4, BOLD)
            y -= 10
            y = doc.W(ML+6, y, fals, 7.5, INK3, SERIFI,
                      mw=TW-8, lh=11, floor=FL, mx=1)
            y -= 4

        # ── Separator ────────────────────────────────────────────────────────
        y -= 8
        if i < 2:
            doc.HL(y, lw=0.5, col=RULE2)
            y -= 16

    # ── METODRUTA — förklarar verktygets epistemiska process ────────────────
    if y > FL + 80:
        doc.HL(y, lw=0.4, col=RULE2); y -= 14
        y = doc.section_label(y, "SÅ HÄR FUNGERAR ANALYSEN", GOLD)
        METHOD_LINES = [
            ("H1/H2/H3", "Tre konkurrerande hypoteser testas mot evidens — ingen ges företräde från början."),
            ("Red Team", "GPT-4o attackerar analysen, söker felaktiga premisser och alternativa förklaringar som primäranalysen missat."),
            ("VERDICT", "HÅLLER = primärtesen stod emot kritiken.  MODIFIERAS = justeringar gjorda.  KOLLAPSAR = omskriven."),
            ("Källor", "E5=primärkälla/officiell  E4=kvalitetsmedia  E3=sekundär  E2=rapport  E1=Wikipedia/aggregat."),
        ]
        for lbl, desc in METHOD_LINES:
            if y < FL + 14: break
            doc.T(ML, y, lbl, 7, GOLD, BOLD)
            doc.W(ML+60, y, desc, 7.5, INK2, SERIF, mw=TW-62, lh=11, floor=FL, mx=2)
            y -= 14

    # ── CRITIQUE ──────────────────────────────────────────────────────────────
    verdict = _get_verdict(r)
    if verdict and y > FL + 50:
        doc.HL(y-4, lw=0.4, col=RULE); y -= SEC_GAP
        y = doc.section_label(y, "KRITIK · ALTERNATIV TOLKNING", AMB)
        doc.LBAR(ML+2, y-50, y+2, AMB, 2)
        y = doc.W(ML+10, y, verdict, 9.5, INK2, SERIFI,
                  mw=TW-12, lh=14, floor=FL, mx=4)

    # ── FINAL ASSESSMENT ──────────────────────────────────────────────────────
    hero = _get_hero(r)
    if hero and y > FL + 50:
        doc.HL(y-6, lw=0.4, col=RULE); y -= SEC_GAP
        y = doc.section_label(y, "ANALYTISK SLUTBEDÖMNING", GOLD)
        doc.W(ML, y, hero, 10, INK, SERIFB,
              mw=TW, lh=15, floor=FL, mx=5)


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def build_pdf(result: dict) -> bytes:
    buf = io.BytesIO()
    try:
        r = result or {}
        d = Doc(buf)
        build_p1(d, r)
        build_p2(d, r)
        build_p3(d, r)
        d.save()
    except Exception as e:
        buf = io.BytesIO()
        c2  = canvas.Canvas(buf, pagesize=A4)
        c2.setFillColor(BG); c2.rect(0,0,W,H,fill=1,stroke=0)
        c2.setFillColor(RED); c2.setFont(BOLD,11)
        c2.drawString(48, H-60, "PDF-export misslyckades")
        c2.setFillColor(INK); c2.setFont(BODY,8)
        c2.drawString(48, H-80, str(e)[:100])
        c2.save()
    return buf.getvalue()
