# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN — PDF EXPORT v9.0
Premium design matching the UI:
  - Dark editorial masthead
  - Light readable body (print-optimised)
  - Briefing layout: syntes → nyckelfakta → hypoteser → evidens → red team
  - Clickable source links
  - Mobile-friendly A4
"""

import io
import re
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalizer import normalize_result

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Flowable

PDF_VERSION = "v9.0"

# ── Fonts ──────────────────────────────────────────────────────────────────────
_SANS = _SANS_B = _SANS_I = "Helvetica"
_SERIF = _SERIF_B = _SERIF_I = "Helvetica"
_MONO = "Courier"

try:
    pdfmetrics.registerFont(TTFont("Sans",   "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("SansB",  "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("SansI",  "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"))
    pdfmetrics.registerFont(TTFont("Serif",  "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("SerifB", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("SerifI", "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"))
    pdfmetrics.registerFont(TTFont("Mono",   "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("MonoB",  "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"))
    _SANS = "Sans"; _SANS_B = "SansB"; _SANS_I = "SansI"
    _SERIF = "Serif"; _SERIF_B = "SerifB"; _SERIF_I = "SerifI"
    _MONO = "Mono"
except Exception:
    pass

# ── Colour palette (matches UI CSS variables) ─────────────────────────────────
# Dark (masthead / section bands)
C_DARK      = colors.HexColor("#0a0b0d")
C_DARK2     = colors.HexColor("#0f1115")
C_DARK3     = colors.HexColor("#141821")

# Light body
C_PAPER     = colors.HexColor("#fafaf8")
C_PAPER2    = colors.HexColor("#f4f2ed")
C_INK       = colors.HexColor("#1a1a1a")
C_INK2      = colors.HexColor("#333333")
C_INK3      = colors.HexColor("#555555")
C_SUBTLE    = colors.HexColor("#888888")
C_RULE      = colors.HexColor("#dddddd")
C_WHITE     = colors.white

# Accent
C_GRN       = colors.HexColor("#57c78a")
C_GRN_DIM   = colors.HexColor("#1e4a34")
C_GRN_BG    = colors.HexColor("#f0f9f4")
C_AMB       = colors.HexColor("#e2b04c")
C_AMB_DIM   = colors.HexColor("#5e4518")
C_AMB_BG    = colors.HexColor("#fdf8ee")
C_RED       = colors.HexColor("#db6b57")
C_RED_DIM   = colors.HexColor("#5b2620")
C_RED_BG    = colors.HexColor("#fdf3f1")
C_BLU       = colors.HexColor("#6eb6ff")
C_BLU_DIM   = colors.HexColor("#23486d")
C_BLU_BG    = colors.HexColor("#f0f6ff")

STYRKA_COLOR = {
    "HÖG":      C_GRN,
    "MEDEL-HÖG": colors.HexColor("#8fd45f"),
    "MEDEL":    C_BLU,
    "LÅG":      C_RED,
}

STYRKA_BG = {
    "HÖG":      C_GRN_BG,
    "MEDEL-HÖG": colors.HexColor("#f4faee"),
    "MEDEL":    C_BLU_BG,
    "LÅG":      C_RED_BG,
}

REALITY_META = {
    "VERIFIED":    (C_GRN,  "✓ VERIFIED"),
    "ONGOING":     (C_BLU,  "◉ ONGOING"),
    "PARTIAL":     (C_AMB,  "◑ PARTIAL"),
    "HYPOTHETICAL":(C_BLU,  "◌ HYPOTHETICAL"),
    "ANALYTICAL":  (C_BLU,  "◎ ANALYTICAL"),
    "UNVERIFIED":  (C_RED,  "✗ UNVERIFIED"),
}

PAGE_W, PAGE_H = A4
ML = 16*mm; MR = 16*mm; MT = 12*mm; MB = 22*mm
TW = PAGE_W - ML - MR


# ── Style factory ──────────────────────────────────────────────────────────────
def _S():
    return {
        # Masthead (dark bg, white text)
        "brand":     ParagraphStyle("brand",    fontName=_SANS_B,  fontSize=7,    textColor=C_WHITE,  letterSpacing=4,  leading=10),
        "brand_sub": ParagraphStyle("brand_sub",fontName=_MONO,    fontSize=5,    textColor=colors.HexColor("#aaaaaa"), letterSpacing=2, leading=8),
        "hdr_r":     ParagraphStyle("hdr_r",    fontName=_MONO,    fontSize=5,    textColor=colors.HexColor("#bbbbbb"), letterSpacing=1, alignment=2, leading=8),

        # Question
        "question":  ParagraphStyle("q",        fontName=_SERIF_B, fontSize=14,   textColor=C_INK,    leading=20, spaceBefore=2, spaceAfter=4),
        "tagline":   ParagraphStyle("tag",       fontName=_SERIF_I, fontSize=8,    textColor=C_INK3,   leading=13),

        # Section labels (mono caps)
        "sec_lbl":   ParagraphStyle("sl",        fontName=_MONO,    fontSize=5.5,  textColor=C_SUBTLE, letterSpacing=3, leading=9, spaceBefore=10, spaceAfter=3),

        # Body text
        "body":      ParagraphStyle("body",      fontName=_SERIF,   fontSize=9,    textColor=C_INK2,   leading=15, spaceAfter=4),
        "body_sm":   ParagraphStyle("body_sm",   fontName=_SANS,    fontSize=8,    textColor=C_INK3,   leading=13, spaceAfter=3),
        "lead":      ParagraphStyle("lead",      fontName=_SERIF,   fontSize=10.5, textColor=C_INK,    leading=17, spaceAfter=6),
        "italic":    ParagraphStyle("italic",    fontName=_SERIF_I, fontSize=8.5,  textColor=C_INK3,   leading=14),

        # Hypothesis
        "hyp_key":   ParagraphStyle("hk",        fontName=_MONO,    fontSize=8,    textColor=C_INK,    letterSpacing=1, leading=11),
        "hyp_title": ParagraphStyle("ht",        fontName=_SERIF_B, fontSize=10,   textColor=C_INK,    leading=15),
        "hyp_lbl":   ParagraphStyle("hl",        fontName=_MONO,    fontSize=5.5,  textColor=C_SUBTLE, letterSpacing=2, leading=8),

        # Evidence etc
        "ev_body":   ParagraphStyle("ev",        fontName=_SANS,    fontSize=8,    textColor=C_INK2,   leading=13),
        "mo_body":   ParagraphStyle("mo",        fontName=_SANS,    fontSize=8,    textColor=colors.HexColor("#7a2a1a"), leading=13),
        "fl_body":   ParagraphStyle("fl",        fontName=_SANS_I,  fontSize=7.5,  textColor=C_BLU_DIM,leading=12),

        # Assessment
        "conc":      ParagraphStyle("conc",      fontName=_SERIF_B, fontSize=11,   textColor=C_INK,    leading=17),
        "conc_exp":  ParagraphStyle("ce",        fontName=_SERIF,   fontSize=8.5,  textColor=C_INK2,   leading=15),

        # Verdict
        "verdict":   ParagraphStyle("verd",      fontName=_SANS_B,  fontSize=9,    textColor=C_INK,    leading=13),

        # Meta / footer
        "meta":      ParagraphStyle("meta",      fontName=_MONO,    fontSize=5.5,  textColor=C_SUBTLE, letterSpacing=0.5, leading=9),
        "link":      ParagraphStyle("link",      fontName=_MONO,    fontSize=6.5,  textColor=C_BLU_DIM,leading=10),
    }


# ── Helpers ────────────────────────────────────────────────────────────────────
def _c(t):
    if not t: return ""
    t = str(t)
    t = re.sub(r'^#{1,6}\s+', '', t, flags=re.MULTILINE)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\*(.+?)\*', r'<i>\1</i>', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = t.replace('\x00','').replace('\r','')
    t = t.replace('&','&amp;').replace('<b>','XBOPEN').replace('</b>','XBCLOSE').replace('<i>','XIOPEN').replace('</i>','XICLOSE')
    t = t.replace('<','&lt;').replace('>','&gt;')
    t = t.replace('XBOPEN','<b>').replace('XBCLOSE','</b>').replace('XIOPEN','<i>').replace('XICLOSE','</i>')
    return t.strip()

def _p(text, style):
    t = _c(text)
    if not t: return None
    try:
        return Paragraph(t, style)
    except Exception:
        return Paragraph(t.encode('ascii','replace').decode(), style)

def _trunc(text, n):
    if not text or len(text) <= n: return text or ""
    chunk = text[:n]
    for sep in ('. ', '! ', '? '):
        idx = chunk.rfind(sep)
        if idx > n // 2: return chunk[:idx+2].strip()
    return chunk.rstrip() + "…"

def _extract_urls(text):
    if not text: return []
    seen = set(); out = []
    for m in re.findall(r'\[[^\]]+\]\((https?://[^\s\)]+)\)', text):
        if m not in seen: seen.add(m); out.append(m)
    for m in re.findall(r'https?://[^\s<\)"]+', text):
        if m not in seen: seen.add(m); out.append(m)
    BAD = {"google.com","google.se","bing.com","yahoo.com","localhost"}
    return [u for u in out if not any(d in u for d in BAD)]

def _domain(url):
    m = re.search(r'https?://(?:www\.)?([^/\s]+)', url or "")
    return m.group(1) if m else url[:30]

def _sc(styrka):
    s = (styrka or "MEDEL").upper()
    return STYRKA_COLOR.get(s, C_BLU), STYRKA_BG.get(s, C_BLU_BG)


# ── Reusable layout blocks ─────────────────────────────────────────────────────

def _dark_band(story, label, sub=""):
    """Full-width dark section header band."""
    lp = Paragraph(
        f'<b>{label.upper()}</b>',
        ParagraphStyle("db", fontName=_MONO, fontSize=5.5, textColor=C_WHITE,
                       letterSpacing=3, leading=9)
    )
    rows = [[lp]]
    if sub:
        sp = Paragraph(sub, ParagraphStyle("ds", fontName=_SANS_I, fontSize=6,
                                            textColor=colors.HexColor("#aaaaaa"), leading=9))
        rows.append([sp])
    band = Table(rows, colWidths=[TW])
    band.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), C_DARK),
        ('TOPPADDING',   (0,0),(-1,-1), 7),
        ('BOTTOMPADDING',(0,0),(-1,-1), 7),
        ('LEFTPADDING',  (0,0),(-1,-1), 10),
        ('RIGHTPADDING', (0,0),(-1,-1), 10),
    ]))
    story.append(Spacer(1, 3*mm))
    story.append(band)
    story.append(Spacer(1, 1.5*mm))


def _left_bar(story, items, tc, bg, bar_w=2.5):
    if not items: return
    s = ParagraphStyle("lb", fontName=_SANS, fontSize=8, textColor=C_INK2,
                        leading=13, spaceAfter=2)
    rows = []
    for it in items:
        if it and it.strip():
            pg = _p(it, s)
            if pg: rows.append([pg])
    if not rows: return
    t = Table(rows, colWidths=[TW - 10*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), bg),
        ('LINEBEFORE',   (0,0),(0,-1),  bar_w, tc),
        ('LEFTPADDING',  (0,0),(-1,-1), 9),
        ('RIGHTPADDING', (0,0),(-1,-1), 8),
        ('TOPPADDING',   (0,0),(0,0),   6),
        ('BOTTOMPADDING',(0,-1),(-1,-1),6),
        ('TOPPADDING',   (0,1),(-1,-1), 3),
        ('BOTTOMPADDING',(0,0),(0,-2),  3),
    ]))
    story.append(t)
    story.append(Spacer(1, 1.5*mm))


def _pill_inline(label, tc, bg):
    p = Paragraph(f'<b>{_c(label).upper()}</b>',
                  ParagraphStyle("pi", fontName=_MONO, fontSize=5.5, textColor=tc,
                                 letterSpacing=2, leading=8))
    t = Table([[p]])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), bg),
        ('TOPPADDING',   (0,0),(-1,-1), 2.5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 2.5),
        ('LEFTPADDING',  (0,0),(-1,-1), 6),
        ('RIGHTPADDING', (0,0),(-1,-1), 6),
        ('LINEABOVE',    (0,0),(-1,-1), .4, tc),
        ('LINEBELOW',    (0,-1),(-1,-1),.4, tc),
        ('LINEBEFORE',   (0,0),(0,-1),  .4, tc),
        ('LINEAFTER',    (-1,0),(-1,-1),.4, tc),
    ]))
    return t


def _source_chips(story, urls, s, label="KÄLLOR"):
    if not urls: return
    lp = _p(label, s["sec_lbl"])
    if lp: story.append(lp)
    chips = []
    for url in urls[:6]:
        dom = _domain(url)
        chips.append(
            f'<link href="{url}"><font color="#2c5282"><u>{dom}</u></font></link>'
        )
    link_text = "  ·  ".join(chips)
    lp2 = Paragraph(link_text, s["link"])
    story.append(lp2)
    story.append(Spacer(1, 2*mm))


# ── Masthead ───────────────────────────────────────────────────────────────────
def _masthead(story, s, today, question, status, reality):
    rc_col, rc_lbl = REALITY_META.get(reality, (C_BLU, reality))

    # Left: brand
    left_rows = [
        [Paragraph("SANNINGSMASKINEN", s["brand"])],
        [Paragraph("EPISTEMISKT ANALYSVERKTYG", s["brand_sub"])],
    ]
    left = Table(left_rows, colWidths=[TW * 0.6])
    left.setStyle(TableStyle([
        ('TOPPADDING',   (0,0),(-1,-1), 1),
        ('BOTTOMPADDING',(0,0),(-1,-1), 1),
        ('LEFTPADDING',  (0,0),(-1,-1), 0),
        ('RIGHTPADDING', (0,0),(-1,-1), 0),
    ]))

    # Right: date + status
    right_rows = [
        [Paragraph(today, s["hdr_r"])],
        [Paragraph(f"STATUS: {status}", s["hdr_r"])],
        [Paragraph(rc_lbl, ParagraphStyle("rr", fontName=_MONO, fontSize=5,
                                           textColor=rc_col, letterSpacing=1,
                                           alignment=2, leading=8))],
    ]
    right = Table(right_rows, colWidths=[TW * 0.4])
    right.setStyle(TableStyle([
        ('TOPPADDING',   (0,0),(-1,-1), 1),
        ('BOTTOMPADDING',(0,0),(-1,-1), 1),
        ('LEFTPADDING',  (0,0),(-1,-1), 0),
        ('RIGHTPADDING', (0,0),(-1,-1), 0),
    ]))

    band = Table([[left, right]], colWidths=[TW * 0.6, TW * 0.4])
    band.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), C_DARK),
        ('TOPPADDING',   (0,0),(-1,-1), 10),
        ('BOTTOMPADDING',(0,0),(-1,-1), 10),
        ('LEFTPADDING',  (0,0),(-1,-1), 12),
        ('RIGHTPADDING', (0,0),(-1,-1), 12),
        ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
    ]))
    story.append(band)

    # Green accent line below masthead
    story.append(HRFlowable(width="100%", thickness=2.5, color=C_GRN, spaceAfter=0))

    # Question block
    story.append(Spacer(1, 5*mm))
    qp = _p(question, s["question"])
    if qp:
        qbox = Table([[qp]], colWidths=[TW])
        qbox.setStyle(TableStyle([
            ('BACKGROUND',  (0,0),(-1,-1), C_PAPER2),
            ('LINEBEFORE',  (0,0),(0,-1),  4, C_INK),
            ('TOPPADDING',  (0,0),(-1,-1), 11),
            ('BOTTOMPADDING',(0,0),(-1,-1),11),
            ('LEFTPADDING', (0,0),(-1,-1), 14),
            ('RIGHTPADDING',(0,0),(-1,-1), 12),
        ]))
        story.append(qbox)

    tl = _p("Detta dokument försöker inte ge ett svar. Det falsifierar konkurrerande förklaringar.", s["tagline"])
    if tl:
        story.append(Spacer(1, 3*mm))
        story.append(tl)
    story.append(Spacer(1, 2*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_RULE))


# ── Assessment block ───────────────────────────────────────────────────────────
def _assessment(story, s, hypotheses, today):
    if not hypotheses: return

    rank_order = {"HÖG": 0, "MEDEL-HÖG": 1, "MEDEL": 2, "LÅG": 3}
    ranked = sorted(hypotheses, key=lambda h: (
        rank_order.get((h.get("styrka") or "MEDEL").upper(), 99),
        -float(h.get("conf", 0.5))
    ))
    winner = ranked[0]

    _dark_band(story, "Assessment — Analytisk bedömning", "Starkast stödd hypotes")

    # Winner conclusion
    key   = winner.get("key", "")
    lbl   = winner.get("label", "")
    title = winner.get("title", "")
    tes   = winner.get("tes", "")

    conc_str = f"Evidensen stödjer starkast {key}"
    if lbl:   conc_str += f" [{lbl}]"
    if title: conc_str += f" — {title}"

    conc_p = _p(conc_str, s["conc"])
    if conc_p:
        cbox = Table([[conc_p]], colWidths=[TW])
        cbox.setStyle(TableStyle([
            ('BACKGROUND',  (0,0),(-1,-1), C_GRN_BG),
            ('LINEBEFORE',  (0,0),(0,-1),  4, C_GRN),
            ('TOPPADDING',  (0,0),(-1,-1), 10),
            ('BOTTOMPADDING',(0,0),(-1,-1),10),
            ('LEFTPADDING', (0,0),(-1,-1), 14),
            ('RIGHTPADDING',(0,0),(-1,-1), 12),
        ]))
        story.append(cbox)

    if tes:
        tes_p = _p(_trunc(tes, 300), s["conc_exp"])
        if tes_p:
            tbox = Table([[tes_p]], colWidths=[TW])
            tbox.setStyle(TableStyle([
                ('BACKGROUND',  (0,0),(-1,-1), C_PAPER),
                ('LINEBEFORE',  (0,0),(0,-1),  2, C_RULE),
                ('TOPPADDING',  (0,0),(-1,-1), 8),
                ('BOTTOMPADDING',(0,0),(-1,-1),8),
                ('LEFTPADDING', (0,0),(-1,-1), 14),
                ('RIGHTPADDING',(0,0),(-1,-1), 12),
            ]))
            story.append(tbox)

    # Hypothesis ranking table
    story.append(Spacer(1, 4*mm))
    lp = _p("HYPOTES-RANKING", s["sec_lbl"])
    if lp: story.append(lp)
    story.append(Spacer(1, 1.5*mm))

    _render_hyp_ranking_table(story, s, ranked)

    # Falsifiering
    falsif = winner.get("falsifiering", "")
    if falsif:
        story.append(Spacer(1, 3*mm))
        fl_label = _p("VAD FALSIFIERAR VINNARHYPOTESEN?", s["sec_lbl"])
        if fl_label: story.append(fl_label)
        _left_bar(story, [_trunc(falsif, 250)], C_BLU, C_BLU_BG)

    # Metod note
    story.append(Spacer(1, 3*mm))
    metod = _p(
        "METOD  Analysen testar konkurrerande hypoteser mot evidens och red-team-granskning. "
        "Källor graderas E1 (rykten) till E5 (primärkälla). "
        "Confidence = evidensstyrka × log(bevisantal+1) × källkvalitet.",
        ParagraphStyle("mt", fontName=_MONO, fontSize=5.5, textColor=C_SUBTLE,
                       leading=9, letterSpacing=0.2)
    )
    if metod:
        mbox = Table([[metod]], colWidths=[TW])
        mbox.setStyle(TableStyle([
            ('BACKGROUND',  (0,0),(-1,-1), C_PAPER2),
            ('LINEABOVE',   (0,0),(-1,0),  .4, C_RULE),
            ('TOPPADDING',  (0,0),(-1,-1), 6),
            ('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LEFTPADDING', (0,0),(-1,-1), 10),
            ('RIGHTPADDING',(0,0),(-1,-1), 10),
        ]))
        story.append(mbox)

    story.append(Spacer(1, 3*mm))


class HypRankingChart(Flowable):
    """
    Canvas-drawn hypothesis ranking — no ASCII, proper bars.
    Each row: rank | key+label | tes (wrapping) | bar+pct
    """
    ROW_H   = 16 * mm
    RANK_W  = 10 * mm
    KEY_W   = 34 * mm
    PCT_W   = 14 * mm
    PAD     = 3 * mm

    HEX = {"HÖG": "#57c78a", "MEDEL-HÖG": "#8fd45f", "MEDEL": "#6eb6ff", "LÅG": "#db6b57"}

    def __init__(self, ranked, width):
        super().__init__()
        self.ranked = ranked[:4]
        self.width  = width
        self.height = len(self.ranked) * (self.ROW_H + 1*mm) + 8*mm

    def draw(self):
        c      = self.canv
        BAR_X  = self.RANK_W + self.KEY_W + self.PAD
        BAR_W  = self.width - BAR_X - self.PCT_W - self.PAD
        RANKS  = ["#1", "#2", "#3", "#4"]
        y      = self.height - 5*mm

        # Header band
        c.setFillColor(colors.HexColor("#141821"))
        c.rect(0, y, self.width, 6*mm, fill=1, stroke=0)
        c.setFont(_MONO, 5.5)
        c.setFillColor(colors.HexColor("#aaaaaa"))
        for label, x in [("RANK", self.RANK_W/2),
                         ("HYPOTES", self.RANK_W + self.KEY_W/2),
                         ("TES", BAR_X + BAR_W*0.3),
                         ("CONF", BAR_X + BAR_W + self.PCT_W/2)]:
            c.drawCentredString(x, y + 2*mm, label)
        y -= 6*mm

        for i, h in enumerate(self.ranked):
            key    = h.get("key", "")
            lbl    = h.get("label", "")
            tes    = h.get("tes", "") or ""
            styrka = (h.get("styrka") or "MEDEL").upper()
            pct    = h.get("conf_pct", int(h.get("conf", 0.5) * 100))
            col    = colors.HexColor(self.HEX.get(styrka, "#6eb6ff"))
            bg     = colors.HexColor("#f0f9f4") if i == 0 else (
                     colors.HexColor("#fafaf8") if i % 2 == 0 else colors.HexColor("#f4f2ed"))

            row_top = y
            row_bot = y - self.ROW_H
            mid_y   = (row_top + row_bot) / 2

            # Row background
            c.setFillColor(bg)
            c.rect(0, row_bot, self.width, self.ROW_H, fill=1, stroke=0)

            # Winner accent stripe
            if i == 0:
                c.setFillColor(col)
                c.rect(0, row_bot, 2.5, self.ROW_H, fill=1, stroke=0)

            # Rank
            c.setFont(_MONO, 7)
            c.setFillColor(colors.HexColor("#888888"))
            c.drawCentredString(self.RANK_W / 2, mid_y - 2, RANKS[i])

            # Key + label
            c.setFont(_MONO, 8)
            c.setFillColor(col)
            c.drawString(self.RANK_W + 2, mid_y + 1*mm, key)
            c.setFont(_SANS, 6)
            c.setFillColor(colors.HexColor("#888888"))
            c.drawString(self.RANK_W + 2, mid_y - 3.5, lbl[:18])

            # Tes — truncate to full sentence within bar area
            tes_clean = re.sub(r'\[.*?\]|\*+', '', tes).strip()
            # Wrap to two lines manually
            words = tes_clean.split()
            line1, line2 = [], []
            curr_w = 0
            max_w  = BAR_W * 0.95  # approx chars
            switched = False
            for word in words:
                if not switched and curr_w + len(word) < 48:
                    line1.append(word)
                    curr_w += len(word) + 1
                else:
                    switched = True
                    line2.append(word)
                    if len(' '.join(line2)) > 48:
                        break
            t1 = ' '.join(line1)
            t2 = ' '.join(line2)[:48]
            if t2 and not t2.endswith('.'): t2 += '…'

            c.setFont(_SERIF, 7)
            c.setFillColor(colors.HexColor("#333333"))
            c.drawString(BAR_X, mid_y + 2*mm, t1[:60])
            if t2:
                c.setFont(_SERIF, 6.5)
                c.setFillColor(colors.HexColor("#666666"))
                c.drawString(BAR_X, mid_y - 1.5, t2[:60])

            # Bar track
            bar_y = row_bot + 3.5
            bar_h = 3
            c.setFillColor(colors.HexColor("#dddddd"))
            c.roundRect(BAR_X, bar_y, BAR_W, bar_h, 1.5, fill=1, stroke=0)

            # Bar fill — proportional to actual pct
            fill_w = max(3, BAR_W * pct / 100)
            c.setFillColor(col)
            c.roundRect(BAR_X, bar_y, fill_w, bar_h, 1.5, fill=1, stroke=0)

            # Pct label
            c.setFont(_MONO, 8)
            c.setFillColor(col)
            c.drawCentredString(BAR_X + BAR_W + self.PCT_W/2, mid_y - 1, f"{pct}%")

            # Row divider
            c.setStrokeColor(colors.HexColor("#dddddd"))
            c.setLineWidth(0.3)
            c.line(0, row_bot, self.width, row_bot)

            y -= self.ROW_H + 1*mm


def _render_hyp_ranking_table(story, s, ranked):
    """Canvas-drawn ranking chart — correct proportional bars."""
    story.append(HypRankingChart(ranked, TW))
    story.append(Spacer(1, 2*mm))


# ── Reality Check section ──────────────────────────────────────────────────────
def _reality_section(story, s, rc):
    status  = (rc.get("status") or "").upper()
    rc_text = rc.get("text") or rc.get("result") or ""

    rc_col, rc_lbl = REALITY_META.get(status, (C_BLU, status))
    _dark_band(story, "Reality Check — Steg 0 — Claim Verification")

    status_p = Paragraph(
        f"<b>{rc_lbl}</b>",
        ParagraphStyle("rcs", fontName=_MONO, fontSize=9, textColor=rc_col,
                       letterSpacing=3, leading=14)
    )
    sbox = Table([[status_p]], colWidths=[TW])
    sbox.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), C_DARK2),
        ('TOPPADDING',   (0,0),(-1,-1), 7),
        ('BOTTOMPADDING',(0,0),(-1,-1), 7),
        ('LEFTPADDING',  (0,0),(-1,-1), 12),
        ('RIGHTPADDING', (0,0),(-1,-1), 12),
        ('LINEBELOW',    (0,-1),(-1,-1), 1.5, rc_col),
    ]))
    story.append(sbox)
    story.append(Spacer(1, 2*mm))

    # Parse CLAIM lines
    claims = []
    for block in re.split(r'\n(?=CLAIM\s*\d*:)', rc_text, flags=re.IGNORECASE):
        cm = re.search(r'CLAIM\s*\d*:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        sm = re.search(r'STATUS\s*:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
        if cm:
            claims.append({
                "claim":  cm.group(1).strip(),
                "status": sm.group(1).strip() if sm else "",
            })

    if claims:
        for it in claims[:5]:
            st = it["status"].upper()
            if "VERIFIED" in st or "BEKRÄFTAD" in st:
                ic, ic_col = "✓", C_GRN
            elif "UNVERIFIED" in st or "EJ" in st:
                ic, ic_col = "✗", C_RED
            else:
                ic, ic_col = "◑", C_AMB
            ic_p = Paragraph(f"<b>{ic}</b>", ParagraphStyle(
                "ric", fontName=_MONO, fontSize=8, textColor=ic_col, leading=12))
            cl_p = Paragraph(_c(it["claim"][:180]), ParagraphStyle(
                "rcl", fontName=_SANS, fontSize=7.5, textColor=C_INK2, leading=12))
            row = Table([[ic_p, cl_p]], colWidths=[8*mm, TW - 8*mm])
            row.setStyle(TableStyle([
                ('VALIGN',       (0,0),(-1,-1), 'TOP'),
                ('TOPPADDING',   (0,0),(-1,-1), 3),
                ('BOTTOMPADDING',(0,0),(-1,-1), 3),
                ('LEFTPADDING',  (0,0),(-1,-1), 6),
                ('LINEBELOW',    (0,-1),(-1,-1), .3, C_RULE),
            ]))
            story.append(row)
    elif rc_text:
        _left_bar(story, [rc_text[:400]], C_BLU, C_BLU_BG)

    story.append(Spacer(1, 3*mm))


# ── Hypothesis detail card ─────────────────────────────────────────────────────
def _hyp_card(story, s, hyp, urls=None):
    key    = hyp.get("key", "")
    lbl    = hyp.get("label", "")
    title  = hyp.get("title", "")
    styrka = (hyp.get("styrka") or "MEDEL").upper()
    tes    = hyp.get("tes", "")
    bevis  = hyp.get("bevis", []) or []
    motarg = hyp.get("motarg", []) or []
    falsif = hyp.get("falsifiering", "")
    pct    = hyp.get("conf_pct", int(hyp.get("conf", 0.5) * 100))

    tc, bg = _sc(styrka)

    # Header row: key + label + pct + styrka
    header_left = Paragraph(
        f'<b>{key}</b>  <font color="#888888">[{lbl}]</font>',
        ParagraphStyle("chl", fontName=_MONO, fontSize=8, textColor=C_INK, leading=12)
    )
    header_right = Paragraph(
        f'<b>{pct}%</b>  {styrka}',
        ParagraphStyle("chr", fontName=_MONO, fontSize=8, textColor=tc,
                       leading=12, alignment=2)
    )
    header = Table([[header_left, header_right]], colWidths=[TW * 0.65, TW * 0.35])
    header.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), C_DARK3),
        ('LINEABOVE',    (0,0),(-1,0),  2, tc),
        ('TOPPADDING',   (0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LEFTPADDING',  (0,0),(-1,-1), 10),
        ('RIGHTPADDING', (0,0),(-1,-1), 10),
        ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
    ]))
    story.append(header)

    # Title
    if title:
        tp = _p(title, s["hyp_title"])
        if tp:
            tbox = Table([[tp]], colWidths=[TW])
            tbox.setStyle(TableStyle([
                ('BACKGROUND',  (0,0),(-1,-1), C_PAPER2),
                ('LEFTPADDING', (0,0),(-1,-1), 10),
                ('RIGHTPADDING',(0,0),(-1,-1), 10),
                ('TOPPADDING',  (0,0),(-1,-1), 7),
                ('BOTTOMPADDING',(0,0),(-1,-1),4),
            ]))
            story.append(tbox)

    # TES
    if tes:
        lp = _p("TES", s["sec_lbl"])
        if lp: story.append(lp)
        _left_bar(story, [_trunc(tes, 300)], C_GRN, C_GRN_BG)

    # BEVIS
    if bevis:
        lp = _p("EVIDENS", s["sec_lbl"])
        if lp: story.append(lp)
        _left_bar(story, [_trunc(b, 200) for b in bevis[:4]], C_GRN, C_GRN_BG)

    # MOTARG
    if motarg:
        lp = _p("MOTARGUMENT", s["sec_lbl"])
        if lp: story.append(lp)
        _left_bar(story, [_trunc(m, 180) for m in motarg[:3]], C_RED, C_RED_BG)

    # FALSIFIERING
    if falsif:
        lp = _p("FALSIFIERINGSTEST", s["sec_lbl"])
        if lp: story.append(lp)
        _left_bar(story, [_trunc(falsif, 200)], C_BLU, C_BLU_BG)

    # Source links
    if urls:
        _source_chips(story, urls[:4], s)

    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=0.4, color=C_RULE))
    story.append(Spacer(1, 1*mm))


# ── Red Team & Conflict ────────────────────────────────────────────────────────
def _red_team_section(story, s, red_text, red_norm):
    _dark_band(story, "Red Team — Steg 4 — Konkurrerande modell")

    verdict = red_norm.get("verdict", "")
    if verdict:
        v = verdict.upper()
        if "KOLLAPSAR" in v:   vc, vb = C_RED,  C_RED_BG
        elif "MODIFIERAS" in v: vc, vb = C_AMB, C_AMB_BG
        else:                   vc, vb = C_GRN,  C_GRN_BG
        vp = _p(f"VERDICT: {verdict[:80]}", ParagraphStyle(
            "vrd", fontName=_MONO, fontSize=8, textColor=vc,
            letterSpacing=1, leading=12))
        if vp:
            vbox = Table([[vp]], colWidths=[TW])
            vbox.setStyle(TableStyle([
                ('BACKGROUND',  (0,0),(-1,-1), vb),
                ('LINEBEFORE',  (0,0),(0,-1),  3, vc),
                ('TOPPADDING',  (0,0),(-1,-1), 8),
                ('BOTTOMPADDING',(0,0),(-1,-1),8),
                ('LEFTPADDING', (0,0),(-1,-1), 12),
                ('RIGHTPADDING',(0,0),(-1,-1), 10),
            ]))
            story.append(vbox)
            story.append(Spacer(1, 2*mm))

    if red_norm.get("alt_tes"):
        lp = _p("ALTERNATIV TES", s["sec_lbl"])
        if lp: story.append(lp)
        _left_bar(story, [_trunc(red_norm["alt_tes"], 280)], C_RED, C_RED_BG)

    if red_norm.get("varfor_fel"):
        lp = _p("VARFÖR CLAUDE HAR FEL", s["sec_lbl"])
        if lp: story.append(lp)
        _left_bar(story, [_trunc(red_norm["varfor_fel"], 280)], C_AMB, C_AMB_BG)

    if not red_norm.get("verdict") and not red_norm.get("alt_tes"):
        _compact_text(story, s, red_text, 600)

    story.append(Spacer(1, 3*mm))


def _conflict_section(story, s, conflict_text):
    if not conflict_text: return
    _dark_band(story, "Konfliktanalys — Steg 3 — Claude vs GPT-4")
    _compact_text(story, s, conflict_text, 800)
    story.append(Spacer(1, 3*mm))


def _compact_text(story, s, text, max_chars=1000):
    if not text: return
    truncated = _trunc(text, max_chars)
    for para in truncated.split('\n\n'):
        para = para.strip()
        if not para: continue
        up = para.upper()
        if any(up.startswith(x) for x in ("KONFLIKT","VERDICT","DOM:","SVAGASTE","FIX")):
            pg = _p(para, s["sec_lbl"])
        else:
            pg = _p(para, s["body_sm"])
        if pg: story.append(pg)
        story.append(Spacer(1, 1*mm))


# ── Revised analysis section ───────────────────────────────────────────────────
def _revised_section(story, s, final_text, rev_norm):
    if not final_text: return
    _dark_band(story, "Reviderad analys — Efter Red Team-utmaning")

    if rev_norm and rev_norm.get("hypotheses"):
        for hyp in rev_norm["hypotheses"]:
            _hyp_card(story, s, hyp)
    else:
        _compact_text(story, s, final_text, 1500)

    story.append(Spacer(1, 3*mm))


class ConfBarsChart(Flowable):
    """Canvas-drawn confidence bars for ANALYSRESULTAT block."""
    ROW_H = 9 * mm
    HEX   = {"HÖG": "#57c78a", "MEDEL-HÖG": "#8fd45f", "MEDEL": "#6eb6ff", "LÅG": "#db6b57"}

    def __init__(self, ranked, width):
        super().__init__()
        self.ranked = ranked[:4]
        self.width  = width
        self.height = len(self.ranked) * self.ROW_H + 2*mm

    def draw(self):
        c      = self.canv
        KEY_W  = 50 * mm
        BAR_X  = KEY_W + 4*mm
        BAR_W  = self.width - BAR_X - 18*mm
        y      = self.height - 1*mm

        for i, h in enumerate(self.ranked):
            hkey  = h.get("key", "")
            hlbl  = h.get("label", "")
            hpct  = h.get("conf_pct", int(h.get("conf", 0.5) * 100))
            hst   = (h.get("styrka") or "MEDEL").upper()
            col   = colors.HexColor(self.HEX.get(hst, "#6eb6ff"))
            bg    = colors.HexColor("#f0f9f4") if i == 0 else (
                    colors.HexColor("#fafaf8") if i % 2 == 0 else colors.HexColor("#f4f2ed"))

            row_bot = y - self.ROW_H
            mid_y   = (y + row_bot) / 2

            c.setFillColor(bg)
            c.rect(0, row_bot, self.width, self.ROW_H, fill=1, stroke=0)

            c.setFont(_MONO, 7.5)
            c.setFillColor(col)
            c.drawString(4, mid_y + 1.5, hkey)
            c.setFont(_SANS, 6)
            c.setFillColor(colors.HexColor("#888888"))
            c.drawString(4, mid_y - 4, f"[{hlbl}]")

            bar_y = mid_y - 1.5
            c.setFillColor(colors.HexColor("#dddddd"))
            c.roundRect(BAR_X, bar_y, BAR_W, 4, 2, fill=1, stroke=0)

            fill_w = max(3, BAR_W * hpct / 100)
            c.setFillColor(col)
            c.roundRect(BAR_X, bar_y, fill_w, 4, 2, fill=1, stroke=0)

            c.setFont(_MONO, 8)
            c.setFillColor(col)
            c.drawString(BAR_X + BAR_W + 4, mid_y - 2, f"{hpct}%")

            c.setStrokeColor(colors.HexColor("#e0e0e0"))
            c.setLineWidth(0.3)
            c.line(0, row_bot, self.width, row_bot)

            y -= self.ROW_H


# ── BLUF — Analysresultat (Bottom Line Up Front) ──────────────────────────────

def _analysresultat(story, s, ranked):
    if not ranked: return

    winner  = ranked[0]
    key     = winner.get("key", "")
    lbl     = winner.get("label", "")
    title   = winner.get("title", "")
    styrka  = (winner.get("styrka") or "MEDEL").upper()
    pct_w   = winner.get("conf_pct", int(winner.get("conf", 0.5) * 100))
    tes     = winner.get("tes", "") or ""
    bevis   = winner.get("bevis", []) or []
    falsif  = winner.get("falsifiering", "") or ""
    tc, _   = _sc(styrka)

    hex_map = {"HÖG": "#57c78a", "MEDEL-HÖG": "#8fd45f", "MEDEL": "#6eb6ff", "LÅG": "#db6b57"}
    bar_hex = hex_map.get(styrka, "#6eb6ff")

    # ── Header band ───────────────────────────────────────────────────────────
    hdr = Table([[Paragraph("ANALYSRESULTAT",
        ParagraphStyle("arh", fontName=_MONO, fontSize=6, textColor=C_WHITE,
                       letterSpacing=4, leading=9))]], colWidths=[TW])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), C_DARK),
        ('LINEABOVE',    (0,0),(-1,0),  3, C_GRN),
        ('TOPPADDING',   (0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LEFTPADDING',  (0,0),(-1,-1), 12),
        ('RIGHTPADDING', (0,0),(-1,-1), 12),
    ]))
    story.append(hdr)

    # ── Winner block: label + title + tes + top bevis ─────────────────────────
    winner_str = f"{key}  [{lbl}]"
    if title: winner_str += f"  —  {title}"

    block_rows = [
        [Paragraph("MEST SANNOLIK FÖRKLARING",
            ParagraphStyle("arl", fontName=_MONO, fontSize=5.5, textColor=C_SUBTLE,
                           letterSpacing=2, leading=8))],
        [Paragraph(f"<b>{_c(winner_str)}</b>",
            ParagraphStyle("arw", fontName=_SERIF_B, fontSize=12, textColor=C_INK,
                           leading=17))],
        [Paragraph(f'<font color="{bar_hex}"><b>{pct_w}%  EVIDENSSTÖD</b></font>',
            ParagraphStyle("arc", fontName=_MONO, fontSize=7.5, textColor=tc, leading=11))],
    ]

    # TES — full sentence, up to 280 chars
    if tes:
        tes_clean = re.sub(r'\[.*?\]|\*+', '', tes).strip()
        tes_trunc = _trunc(tes_clean, 280)
        block_rows.append([Paragraph(_c(tes_trunc),
            ParagraphStyle("art", fontName=_SERIF, fontSize=9, textColor=C_INK2,
                           leading=15, spaceBefore=3))])

    # Top 2 bevis — stripped of markdown/links
    bevis_clean = []
    for b in bevis[:2]:
        bc = re.sub(r'\[.*?\]\(https?://[^\)]+\)', '', b or '')
        bc = re.sub(r'\[E[1-5][^\]]*\]|\[FAKTA\]|\[INFERENS\]|\*+', '', bc).strip()
        bc = _trunc(bc, 160)
        if bc: bevis_clean.append(bc)

    if bevis_clean:
        bevis_rows = []
        for bc in bevis_clean:
            bevis_rows.append([Paragraph(f"· {_c(bc)}",
                ParagraphStyle("arb", fontName=_SANS, fontSize=7.5,
                               textColor=C_INK3, leading=12))])
        bev_t = Table(bevis_rows, colWidths=[TW - 28*mm])
        bev_t.setStyle(TableStyle([
            ('BACKGROUND',   (0,0),(-1,-1), colors.HexColor("#e8f5ee")),
            ('LINEBEFORE',   (0,0),(0,-1),  2, C_GRN),
            ('TOPPADDING',   (0,0),(0,0),   5),
            ('BOTTOMPADDING',(0,-1),(-1,-1),5),
            ('TOPPADDING',   (0,1),(-1,-1), 2),
            ('BOTTOMPADDING',(0,0),(0,-2),  2),
            ('LEFTPADDING',  (0,0),(-1,-1), 8),
            ('RIGHTPADDING', (0,0),(-1,-1), 8),
        ]))
        block_rows.append([bev_t])

    winner_t = Table(block_rows, colWidths=[TW])
    winner_t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), C_GRN_BG),
        ('LINEBEFORE',   (0,0),(0,-1),  4, C_GRN),
        ('TOPPADDING',   (0,0),(0,0),   10),
        ('BOTTOMPADDING',(0,-1),(-1,-1),8),
        ('TOPPADDING',   (0,1),(-1,-1), 2),
        ('BOTTOMPADDING',(0,0),(0,-2),  2),
        ('LEFTPADDING',  (0,0),(-1,-1), 12),
        ('RIGHTPADDING', (0,0),(-1,-1), 10),
    ]))
    story.append(winner_t)

    # ── Confidence bars ───────────────────────────────────────────────────────
    story.append(ConfBarsChart(ranked, TW))

    # ── Falsifiering ──────────────────────────────────────────────────────────
    if falsif:
        f_clean = re.sub(r'\[.*?\]|\*+', '', falsif).strip()
        f_trunc = _trunc(f_clean, 200)
        if f_trunc:
            fl_rows = [
                [Paragraph("VAD FALSIFIERAR SLUTSATSEN?",
                    ParagraphStyle("fll", fontName=_MONO, fontSize=5.5,
                                   textColor=C_SUBTLE, letterSpacing=2, leading=8))],
                [Paragraph(_c(f_trunc),
                    ParagraphStyle("flt", fontName=_SERIF_I, fontSize=8,
                                   textColor=C_BLU_DIM, leading=13))],
            ]
            fl_t = Table(fl_rows, colWidths=[TW])
            fl_t.setStyle(TableStyle([
                ('BACKGROUND',   (0,0),(-1,-1), C_BLU_BG),
                ('LINEBEFORE',   (0,0),(0,-1),  2, C_BLU),
                ('TOPPADDING',   (0,0),(0,0),   6),
                ('BOTTOMPADDING',(0,-1),(-1,-1),6),
                ('TOPPADDING',   (0,1),(-1,-1), 2),
                ('LEFTPADDING',  (0,0),(-1,-1), 10),
                ('RIGHTPADDING', (0,0),(-1,-1), 10),
            ]))
            story.append(fl_t)

    story.append(Spacer(1, 3*mm))


def _full_sentence(text, max_chars=200):
    """Truncate at sentence boundary, never mid-sentence."""
    if not text or len(text) <= max_chars:
        return text
    chunk = text[:max_chars]
    for sep in ('. ', '! ', '? '):
        idx = chunk.rfind(sep)
        if idx > max_chars // 3:
            return chunk[:idx + 1].strip()
    idx = chunk.rfind(' ')
    return (chunk[:idx].strip() + '…') if idx > 0 else chunk


# ── Briefing extractor ────────────────────────────────────────────────────────

def _extract_briefing(raw: str, ranked: list) -> dict:
    """
    Extract briefing elements — two separate passes for nyckelfakta:

    Pass 1: lines with explicit [E4] or [E5] citation — confirmed facts only.
            Allegations/unverified claims excluded even if E-tagged.
    Pass 2: fallback — concrete lines with dates/numbers/events,
            but STILL excluding unverified allegations.

    nyckelord: H1/H2/H3 tes in strict numerical order.
    """
    lines = raw.split('\n') if raw else []

    SKIP = [
        r'^#{1,6}\s', r'^SANNINGSMASKINEN', r'^Datum:', r'^Status:',
        r'^Låt mig', r'^Jag behöver', r'^\*\*⚠', r'^\[PÅGÅENDE\]',
        r'^\*{0,2}(TES|BEVIS|MOTARG|STYRKA|FALSIF|RANKING)',
        r'^DEL \d', r'^---', r'^H[1-4]\s*[\[\(—]',
    ]

    # Signals that a sentence is an unverified claim — exclude from briefing
    ALLEGATION = [
        r'anklag',
        r'påstår att',
        r'hävdar att',
        r'sägs ha',
        r'uppges ha',
        r'enligt uppgift',
        r'overifierbar',
        r'\[E1\]', r'\[E2\]',
    ]

    def _clean(s):
        s = re.sub(r'\[.*?\]\(https?://[^\)]+\)', '', s)
        s = re.sub(r'\[FAKTA\]|\[INFERENS\]|\[DEBATTERAD TOLKNING\]|\[PÅGÅENDE\]|\*{1,3}', '', s)
        s = re.sub(r'\[E[1-5][^\]]*\]', '', s)
        s = re.sub(r'^\*\*([^*]+)\*\*:?\s*', '', s)
        return s.strip()

    def _is_allegation(s):
        return any(re.search(p, s, re.IGNORECASE) for p in ALLEGATION)

    nyckelfakta = []
    seen = set()

    # Pass 1 — E4/E5 confirmed, no allegations
    for line in lines:
        if len(nyckelfakta) >= 3: break
        s = line.strip()
        if not s or len(s) < 40: continue
        if any(re.match(p, s, re.IGNORECASE) for p in SKIP): continue
        # Accept lines with [E4]/[E5] OR lines marked [FAKTA] that have a URL nearby
        has_source = (re.search(r'\[E[45]', s, re.IGNORECASE) or
                      (re.search(r'\[FAKTA\]', s, re.IGNORECASE) and
                       re.search(r'https?://', s)))
        if not has_source: continue
        if _is_allegation(s): continue
        clean = _clean(s)
        if clean and clean not in seen and len(clean) > 40:
            seen.add(clean)
            nyckelfakta.append(_full_sentence(clean, 200))

    # Pass 2 — fallback: concrete verifiable events, no allegations
    if len(nyckelfakta) < 3:
        CONCRETE = [
            r'\d{1,2}\s+\w+\s+20\d{2}',
            r'miljoner|miljarder|\d+\s*sidor|\d+\s*videor',
            r'gripen|greps|åtalad|avgick|dömdes',
            r'röstade\s+\d+[-–]\d+',
            r'publicerades|offentliggjorde|släppte\s+\d',
        ]
        for line in lines:
            if len(nyckelfakta) >= 3: break
            s = line.strip()
            if not s or len(s) < 40: continue
            if any(re.match(p, s, re.IGNORECASE) for p in SKIP): continue
            if _is_allegation(s): continue
            clean = _clean(s)
            if not clean or clean in seen or len(clean) < 40: continue
            if any(re.search(p, clean, re.IGNORECASE) for p in CONCRETE):
                seen.add(clean)
                nyckelfakta.append(_full_sentence(clean, 200))

    # ── Nyckelord: H1/H2/H3 tes in strict order ──────────────────────────────
    hyp_map = {}
    current_h_num = None
    current_h_label = None
    for line in lines:
        s = line.strip()
        hm = re.match(r'#{1,4}\s*H([1-4])\s*[\[\(]([^\]\)]+)[\]\)]\s*[—\-]\s*(.*)', s)
        if not hm:
            hm = re.match(r'H([1-4])\s*[\[\(]([^\]\)]+)[\]\)]\s*[—\-]\s*(.*)', s)
        if hm:
            current_h_num = int(hm.group(1))
            lbl   = hm.group(2).strip()
            title = hm.group(3).strip()
            current_h_label = f"H{current_h_num} [{lbl}]"
            if title: current_h_label += f" — {title[:50]}"
        if current_h_num and current_h_num not in hyp_map:
            tm = re.match(r'^\*{0,2}TES\*{0,2}\s*:?\s*(.+)', s, re.IGNORECASE)
            if tm:
                tes = re.sub(r'\[.*?\]\(https?://[^\)]+\)', '', tm.group(1)).strip()
                tes = re.sub(r'\[FAKTA\]|\[INFERENS\]|\*{1,3}', '', tes).strip()
                if tes:
                    hyp_map[current_h_num] = (current_h_label, _trunc(tes, 140))
                    current_h_num = None

    nyckelord = [hyp_map[k] for k in sorted(hyp_map.keys()) if k <= 3]

    # Fallback to ranked normalizer data
    if not nyckelord and ranked:
        for h in ranked[:3]:
            key = h.get("key",""); lbl = h.get("label",""); tes = h.get("tes","") or ""
            nyckelord.append((f"{key} [{lbl}]", _trunc(tes, 140)))

    return {"nyckelfakta": nyckelfakta, "nyckelord": nyckelord}


def _briefing_page(story, s, raw_claude, ranked):
    """
    Briefing — två delar:
      1. Bekräftade nyckelfakta (E4/E5 filtrerade, inga anklagelser)
      2. Tre konkurrerande förklaringar (H1/H2/H3)
    """
    brief = _extract_briefing(raw_claude, ranked)

    _dark_band(story, "Briefing — Bekräftade fakta & förklaringar",
               "Källfiltrerat E4/E5 · inga obekräftade påståenden")

    # ── Nyckelfakta ───────────────────────────────────────────────────────────
    if brief["nyckelfakta"]:
        lp = _p("DET DU BEHÖVER VETA NU", s["sec_lbl"])
        if lp: story.append(lp)
        fakta_s = ParagraphStyle("nf", fontName=_SANS, fontSize=8.5,
                                  textColor=C_INK, leading=14)
        rows = []
        for fact in brief["nyckelfakta"]:
            fp = _p(f"› {fact}", fakta_s)
            if fp: rows.append([fp])
        if rows:
            t = Table(rows, colWidths=[TW])
            t.setStyle(TableStyle([
                ('BACKGROUND',   (0,0),(-1,-1), C_AMB_BG),
                ('LINEBEFORE',   (0,0),(0,-1),  2.5, C_AMB),
                ('TOPPADDING',   (0,0),(0,0),   8),
                ('BOTTOMPADDING',(0,-1),(-1,-1),8),
                ('TOPPADDING',   (0,1),(-1,-1), 4),
                ('BOTTOMPADDING',(0,0),(0,-2),  4),
                ('LEFTPADDING',  (0,0),(-1,-1), 10),
                ('RIGHTPADDING', (0,0),(-1,-1), 10),
                ('LINEBELOW',    (0,0),(-1,-2), .3, colors.HexColor("#e8d4a0")),
            ]))
            story.append(t)
        story.append(Spacer(1, 3*mm))

    # ── Tre förklaringar ──────────────────────────────────────────────────────
    if brief["nyckelord"]:
        lp = _p("TRE KONKURRERANDE FÖRKLARINGAR", s["sec_lbl"])
        if lp: story.append(lp)

        H_COLORS = [C_GRN, C_AMB, C_SUBTLE]
        CARD_BG   = [C_GRN_BG, C_AMB_BG, C_PAPER2]

        for i, (h_label, tes) in enumerate(brief["nyckelord"][:3]):
            tc = H_COLORS[i]
            bg = CARD_BG[i]

            m = re.match(r'(H\d\s*\[[^\]]+\])\s*[—\-]?\s*(.*)', h_label)
            key_str   = m.group(1).strip() if m else h_label[:20]
            title_str = m.group(2).strip() if m else ""

            card_rows = []

            key_p = _p(key_str, ParagraphStyle(
                f"hkp{i}", fontName=_MONO, fontSize=7, textColor=tc,
                leading=10, letterSpacing=0.5))
            if key_p: card_rows.append([key_p])

            if title_str:
                tp = _p(title_str, ParagraphStyle(
                    f"htp{i}", fontName=_SERIF_B, fontSize=9,
                    textColor=C_INK, leading=13))
                if tp: card_rows.append([tp])

            # TES — always full sentence, generous length
            tes_display = tes if title_str else ""
            if not tes_display and not title_str:
                tes_display = tes
            if tes_display:
                # Ensure full sentence
                tes_full = _full_sentence(tes_display, 260)
                tesp = _p(tes_full, ParagraphStyle(
                    f"tesp{i}", fontName=_SANS, fontSize=8.5,
                    textColor=C_INK2, leading=14))
                if tesp: card_rows.append([tesp])

            if not card_rows: continue

            card = Table(card_rows, colWidths=[TW])
            card.setStyle(TableStyle([
                ('BACKGROUND',   (0,0),(-1,-1), bg),
                ('LINEABOVE',    (0,0),(-1,0),  1.5, tc),
                ('LINEBEFORE',   (0,0),(0,-1),  2.5, tc),
                ('TOPPADDING',   (0,0),(-1,-1), 7),
                ('BOTTOMPADDING',(0,0),(-1,-1), 7),
                ('LEFTPADDING',  (0,0),(-1,-1), 11),
                ('RIGHTPADDING', (0,0),(-1,-1), 10),
            ]))
            story.append(card)
            story.append(Spacer(1, 1.5*mm))

    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_RULE))
    story.append(Spacer(1, 2*mm))


# ── Page footer callback ───────────────────────────────────────────────────────
def _make_footer(today, status, reality):
    def _footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(C_RULE)
        canvas.setLineWidth(0.3)
        canvas.line(ML, 14*mm, PAGE_W - MR, 14*mm)
        canvas.setFont(_MONO, 5.5)
        canvas.setFillColor(C_SUBTLE)
        canvas.drawString(ML, 11*mm, f"SANNINGSMASKINEN {PDF_VERSION}  ·  {today}  ·  {status}  ·  {reality}")
        canvas.drawRightString(PAGE_W - MR, 11*mm, "Sanningen favoriserar ingen sida.")
        canvas.drawCentredString(PAGE_W / 2, 8*mm, f"— {doc.page} —")
        canvas.restoreState()
    return _footer


# ── Main build function ────────────────────────────────────────────────────────
def build_pdf(result: dict) -> bytes:
    buf   = io.BytesIO()
    today = date.today().strftime("%Y-%m-%d")
    s     = _S()

    norm   = normalize_result(result)
    status = (result.get("status") or "KLAR").upper()
    rc     = result.get("reality_check") or {}
    reality = (rc.get("status") or "").upper()
    layers  = result.get("layers") or {}

    claude_norm = norm.get("claude", {})
    hypotheses  = claude_norm.get("hypotheses", [])

    # Sort by styrka + conf
    rank_order = {"HÖG": 0, "MEDEL-HÖG": 1, "MEDEL": 2, "LÅG": 3}
    ranked = sorted(hypotheses, key=lambda h: (
        rank_order.get((h.get("styrka") or "MEDEL").upper(), 99),
        -float(h.get("conf", 0.5))
    ))

    # Build URL pool from raw text
    raw_claude = result.get("claude_answer", "") or ""

    def _url_pool(raw):
        BAD = {"google.com","google.se","bing.com","yahoo.com","localhost"}
        pool = {"global": []}
        all_u = _extract_urls(raw)
        pool["global"] = [u for u in dict.fromkeys(all_u) if not any(d in u for d in BAD)]
        hp = re.compile(r'(?:^|\n)\s*(?:#{1,4}\s*)?(H[1-4])\s*[\[\(—\-:\s]', re.IGNORECASE)
        matches = list(hp.finditer('\n' + raw))
        for idx, m in enumerate(matches):
            key   = m.group(1).upper()
            start = m.start()
            end   = matches[idx+1].start() if idx+1 < len(matches) else len('\n' + raw)
            block = ('\n' + raw)[start:end]
            real  = [u for u in dict.fromkeys(_extract_urls(block)) if not any(d in u for d in BAD)]
            if real: pool[key] = real
        return pool

    url_pool = _url_pool(raw_claude)

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT, bottomMargin=MB,
        title=f"Sanningsmaskinen — {result.get('question','')[:60]}",
        author="Sanningsmaskinen",
    )

    footer = _make_footer(today, status, reality)
    story  = []

    # ── 1. Masthead + question ─────────────────────────────────────────────────
    _masthead(story, s, today, result.get("question",""), status, reality)
    story.append(Spacer(1, 3*mm))

    # ── 2. BLUF — Analysresultat (slutsatsen först) ───────────────────────────
    _analysresultat(story, s, ranked)

    # ── 3. Briefing — motivering till slutsatsen ──────────────────────────────
    _briefing_page(story, s, raw_claude, ranked)

    # ── 4. Assessment — ranking + falsifiering ────────────────────────────────
    _assessment(story, s, ranked, today)

    # ── 4. Reality Check ───────────────────────────────────────────────────────
    _reality_section(story, s, rc)

    # ── 5. Hypothesis details ──────────────────────────────────────────────────
    _dark_band(story, "Hypoteser — Primäranalys — Tre linser",
               "Claude Opus · Evidensskala E1–E5")

    if ranked:
        for hyp in ranked:
            hyp_urls = url_pool.get(hyp.get("key","").upper(), []) or url_pool.get("global", [])
            _hyp_card(story, s, hyp, urls=hyp_urls[:3])
    else:
        _compact_text(story, s, raw_claude, 2000)

    # ── 6. GPT Critic ─────────────────────────────────────────────────────────
    gpt_text = result.get("gpt_answer", "") or ""
    if gpt_text:
        _dark_band(story, "GPT-4 Kritiker — Steg 2 — Oberoende motanalys")
        gpt_norm = norm.get("gpt", {})
        if gpt_norm.get("dom"):
            lp = _p("DOM", s["sec_lbl"])
            if lp: story.append(lp)
            dom_tc = C_RED if any(x in gpt_norm["dom"].upper() for x in ["HÅLLER INTE","SVAG","KOLLAPSAR"]) else C_GRN
            dom_bg = C_RED_BG if dom_tc == C_RED else C_GRN_BG
            _left_bar(story, [_trunc(gpt_norm["dom"], 250)], dom_tc, dom_bg)
        if gpt_norm.get("svagaste_led"):
            lp = _p("SVAGASTE LED", s["sec_lbl"])
            if lp: story.append(lp)
            _left_bar(story, [_trunc(gpt_norm["svagaste_led"], 200)], C_AMB, C_AMB_BG)
        if not gpt_norm.get("dom"):
            _compact_text(story, s, gpt_text, 700)
        story.append(Spacer(1, 3*mm))

    # ── 7. Conflict ───────────────────────────────────────────────────────────
    _conflict_section(story, s, result.get("conflict_report", ""))

    # ── 8. Red Team ───────────────────────────────────────────────────────────
    red_text = result.get("red_team_report", "") or ""
    red_norm = norm.get("red", {})
    if red_text:
        _red_team_section(story, s, red_text, red_norm)

    # ── 9. Revised analysis ───────────────────────────────────────────────────
    final = result.get("final_analysis", "") or ""
    if final:
        rev_norm = norm.get("claude_revised", {})
        _revised_section(story, s, final, rev_norm)

    # ── 10. Source index ───────────────────────────────────────────────────────
    all_urls = url_pool.get("global", [])
    if all_urls:
        _dark_band(story, "Källförteckning")
        lp = _p("Alla URLs identifierade i analysen — klickbara i PDF-läsare", s["sec_lbl"])
        if lp: story.append(lp)
        story.append(Spacer(1, 1.5*mm))
        for i, url in enumerate(all_urls[:12], 1):
            dom = _domain(url)
            up = _p(
                f'{i}.  <link href="{url}"><font color="#2c5282"><u>{dom}</u></font></link>  '
                f'<font color="#888888">{url[:70]}</font>',
                ParagraphStyle("src", fontName=_MONO, fontSize=6, textColor=C_INK3,
                               leading=10, spaceAfter=2)
            )
            if up: story.append(up)
        story.append(Spacer(1, 3*mm))

    # ── 10. Footer note ───────────────────────────────────────────────────────
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_RULE))
    story.append(Spacer(1, 2*mm))
    end_p = _p(
        f"Sanningsmaskinen {PDF_VERSION}  ·  {today}  ·  "
        "Verktyget försöker inte ge ett svar — det falsifierar konkurrerande förklaringar.  ·  "
        "Sanningen favoriserar ingen sida.",
        ParagraphStyle("end", fontName=_MONO, fontSize=5.5, textColor=C_SUBTLE,
                       leading=9, alignment=1)
    )
    if end_p: story.append(end_p)

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()