# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN — PDF EXPORT v5.2
"""

import io, re, sys, os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalizer import normalize_result

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.flowables import Flowable

PDF_VERSION = "v8.16"

_SANS = _SANS_B = "Helvetica-Bold"
_BODY = _BODY_B = _BODY_I = "Helvetica"

try:
    pdfmetrics.registerFont(TTFont("SansC",  "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"))
    pdfmetrics.registerFont(TTFont("SansCB", "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Serif",  "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("SerifB", "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("SerifI", "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"))
    _SANS = "SansC"; _SANS_B = "SansCB"
    _BODY = "Serif"; _BODY_B = "SerifB"; _BODY_I = "SerifI"
except:
    _BODY = _BODY_B = _BODY_I = "Helvetica"

C_INK    = colors.HexColor("#0a0a0a")
C_DARK   = colors.HexColor("#1a1a1a")
C_BODY   = colors.HexColor("#222222")
C_MID    = colors.HexColor("#555555")
C_SUBTLE = colors.HexColor("#888888")
C_RULE   = colors.HexColor("#2a2a2a")
C_RULE_L = colors.HexColor("#d0d0d0")
C_WHITE  = colors.HexColor("#ffffff")
C_PAPER  = colors.HexColor("#f4f1e8")

C_RED    = colors.HexColor("#7a1818"); C_RED_BG = colors.HexColor("#fdf0f0"); C_RED_MID = colors.HexColor("#c44040")
C_AMB    = colors.HexColor("#6b4f00"); C_AMB_BG = colors.HexColor("#fdf7e8"); C_AMB_MID = colors.HexColor("#b07a10")
C_GRN    = colors.HexColor("#1a3d28"); C_GRN_BG = colors.HexColor("#f0f7f2"); C_GRN_MID = colors.HexColor("#2d6e46")
C_BLU    = colors.HexColor("#172840"); C_BLU_BG = colors.HexColor("#f0f4fa"); C_BLU_MID = colors.HexColor("#2c5282")

REALITY_COLORS = {
    "VERIFIED":    (colors.HexColor("#0a2a0a"), colors.HexColor("#4caf50"), "✓ VERIFIED"),
    "ONGOING":     (colors.HexColor("#0a1a2a"), colors.HexColor("#5c8fff"), "◉ ONGOING"),
    "PARTIAL":     (colors.HexColor("#2a1a00"), colors.HexColor("#ffa726"), "◑ PARTIAL"),
    "HYPOTHETICAL":(colors.HexColor("#1a1a2a"), colors.HexColor("#9c8fff"), "◌ HYPOTHETICAL"),
    "ANALYTICAL":  (colors.HexColor("#0a1a2a"), colors.HexColor("#5c8fff"), "◎ ANALYTICAL"),
    "UNVERIFIED":  (colors.HexColor("#2a0a0a"), colors.HexColor("#ef5350"), "✗ UNVERIFIED"),
}

PAGE_W, PAGE_H = A4
ML = 18*mm; MR = 18*mm; MT = 14*mm; MB = 24*mm
TW = PAGE_W - ML - MR

SEC_BG = {
    "conclusion": colors.HexColor("#0a0a0a"),
    "reality":    colors.HexColor("#111111"),
    "primary":    colors.HexColor("#0d1a0d"),
    "gpt":        colors.HexColor("#1a0d0d"),
    "conflict":   colors.HexColor("#0d0d1a"),
    "redteam":    colors.HexColor("#1a1200"),
    "revised":    colors.HexColor("#1a0a00"),
    "layers":     colors.HexColor("#0a0a14"),
}

STYRKA_MAP = {
    "HÖG":      (C_GRN, C_GRN_BG, C_GRN_MID, 9),
    "MEDEL-HÖG":(C_AMB, C_AMB_BG, C_AMB_MID, 7),
    "MEDEL":    (C_BLU, C_BLU_BG, C_BLU_MID, 5),
    "LÅG":      (C_RED, C_RED_BG, C_RED_MID, 2),
}

STYRKA_COLOR_HEX = {
    "HÖG":       "#2d6e46",
    "MEDEL-HÖG": "#b07a10",
    "MEDEL":     "#2c5282",
    "LÅG":       "#c44040",
}

def _c(t):
    if not t: return ""
    t = str(t)
    t = re.sub(r'^#{1,6}\s+', '', t, flags=re.MULTILINE)
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'\*(.+?)\*', r'\1', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = t.replace('\x00','').replace('\r','')
    t = t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    return t.strip()

def _truncate_at_sentence(text: str, max_chars: int) -> str:
    if not text or len(text) <= max_chars:
        return text
    chunk = text[:max_chars]
    for sep in ('. ', '! ', '? ', '\n'):
        idx = chunk.rfind(sep)
        if idx > max_chars // 2:
            return chunk[:idx + len(sep)].strip()
    return chunk.strip()

def _p(text, style, fallback=True):
    t = _c(text)
    if not t: return None
    try:
        return Paragraph(t, style)
    except:
        if fallback:
            return Paragraph(t.encode('ascii','replace').decode(), style)
        return None

def _sc(s):
    u = (s or "").upper()
    if any(x in u for x in ["KOLLAPS","IFRÅGASATT","UTMANAD","DEGRADERAD"]): return C_RED, C_RED_BG
    if any(x in u for x in ["REVIDERAD","MODIFIERAS"]): return C_AMB, C_AMB_BG
    if any(x in u for x in ["ONGOING","BEKRÄFTAD","KLAR","ANALYTICAL","VERIFIED"]): return C_GRN, C_GRN_BG
    return C_BLU, C_BLU_BG

def _S():
    return {
        "brand":     ParagraphStyle("brand",    fontName=_SANS_B, fontSize=8,    textColor=C_WHITE,  letterSpacing=5,  leading=11),
        "brand_s":   ParagraphStyle("brand_s",  fontName=_SANS,   fontSize=5.5,  textColor=colors.HexColor("#aaaaaa"), letterSpacing=2),
        "hdr_r":     ParagraphStyle("hdr_r",    fontName=_SANS,   fontSize=5.5,  textColor=colors.HexColor("#bbbbbb"), letterSpacing=1.5, alignment=2),
        "qtitle":    ParagraphStyle("qtitle",   fontName=_BODY_B, fontSize=13,   textColor=C_INK,    leading=19),
        "body":      ParagraphStyle("body",     fontName=_BODY,   fontSize=8.5,  textColor=C_BODY,   leading=14, spaceAfter=4),
        "body_sm":   ParagraphStyle("body_sm",  fontName=_BODY,   fontSize=7.5,  textColor=C_MID,    leading=12, spaceAfter=3),
        "italic":    ParagraphStyle("italic",   fontName=_BODY_I, fontSize=8,    textColor=C_MID,    leading=12, spaceAfter=3),
        "sub":       ParagraphStyle("sub",      fontName=_SANS_B, fontSize=6,    textColor=C_MID,    letterSpacing=2, spaceBefore=5, spaceAfter=1),
        "h_title":   ParagraphStyle("h_title",  fontName=_SANS_B, fontSize=10,   textColor=C_INK,    leading=14, spaceBefore=6, spaceAfter=2),
        "meta":      ParagraphStyle("meta",     fontName=_SANS,   fontSize=6,    textColor=C_SUBTLE, letterSpacing=0.3),
        "tagline":   ParagraphStyle("tagline",  fontName=_BODY_I, fontSize=7.5,  textColor=C_MID,    leading=12),
        "conc_win":  ParagraphStyle("conc_win", fontName=_BODY_B, fontSize=10,   textColor=C_WHITE,  leading=14),
        "conc_body": ParagraphStyle("conc_body",fontName=_BODY,   fontSize=8.5,  textColor=colors.HexColor("#cccccc"), leading=14),
        "conc_label":ParagraphStyle("conc_lbl", fontName=_SANS_B, fontSize=5.5,  textColor=colors.HexColor("#888888"), letterSpacing=3),
        "bar_label": ParagraphStyle("bar_lbl",  fontName=_SANS_B, fontSize=7,    textColor=C_BODY,   leading=10),
        "bar_key":   ParagraphStyle("bar_key",  fontName=_SANS,   fontSize=6.5,  textColor=C_MID,    leading=10),
    }

def _pill(label, tc, bg):
    p = Paragraph(f"<b>{_c(label).upper()}</b>", ParagraphStyle(
        "pill", fontName=_SANS_B, fontSize=5.5, textColor=tc, letterSpacing=2, leading=8))
    t = Table([[p]])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),bg),
        ('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('LINEABOVE',(0,0),(-1,-1),.5,tc),('LINEBELOW',(0,-1),(-1,-1),.5,tc),
        ('LINEBEFORE',(0,0),(0,-1),.5,tc),('LINEAFTER',(-1,0),(-1,-1),.5,tc),
    ]))
    return t

def _section_band(story, label, bg_dark):
    lp = Paragraph(label.upper(), ParagraphStyle(
        "sb", fontName=_SANS_B, fontSize=5.5, textColor=C_WHITE, letterSpacing=3, leading=9))
    band = Table([[lp]], colWidths=[TW])
    band.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),bg_dark),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(Spacer(1, 4*mm))
    story.append(band)
    story.append(Spacer(1, 2.5*mm))

def _left_bar_box(story, items, tc, bg, bar_w=2.5):
    if not items: return
    s = ParagraphStyle("lb", fontName=_BODY, fontSize=8, textColor=C_BODY, leading=13, spaceAfter=3)
    rows = [[_p(it, s)] for it in items if it and it.strip()]
    rows = [[r[0]] for r in rows if r[0]]
    if not rows: return
    t = Table(rows, colWidths=[TW - 12*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),bg),
        ('LINEBEFORE',(0,0),(0,-1),bar_w,tc),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(0,0),6),('BOTTOMPADDING',(0,-1),(-1,-1),6),
        ('TOPPADDING',(0,1),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(0,-2),2.5),
    ]))
    story.append(t)
    story.append(Spacer(1, 1.5*mm))


# ── NEW: Grafisk hypotes-dashboard med canvas-staplar ─────────────────────────

class HypothesisBarChart(Flowable):
    """
    Ritar ett horisontellt stapeldiagram för hypoteser.
    Varje rad: Rank  Key [Label]  Title  ████████░░  73%  STYRKA
    Använder canvas direkt — inga block-chars, inga mystiska boxar.
    """
    ROW_H  = 18 * mm
    BAR_H  = 3.5 * mm
    RANK_W = 8  * mm
    KEY_W  = 30 * mm
    PCT_W  = 12 * mm
    ST_W   = 18 * mm

    def __init__(self, hypotheses, width):
        super().__init__()
        self.hyps   = hypotheses
        self.width  = width
        self.height = len(hypotheses) * (self.ROW_H + 1*mm) + 4*mm

    def draw(self):
        c    = self.canv
        BAR_X = self.RANK_W + self.KEY_W + 2*mm
        BAR_W = self.width - BAR_X - self.PCT_W - self.ST_W - 2*mm

        rank_labels = ["#1", "#2", "#3", "#4", "#5"]
        y = self.height - 3*mm

        for i, h in enumerate(self.hyps):
            key    = h.get("key", "")
            lbl    = h.get("label", "")
            title  = h.get("title", "")[:36]
            styrka = (h.get("styrka") or "MEDEL").upper()
            pct    = h.get("conf_pct", int(h.get("conf", 0.5) * 100))
            hex_c  = STYRKA_COLOR_HEX.get(styrka, "#2c5282")
            color  = colors.HexColor(hex_c)
            tc_rl, bg_rl, _, _ = STYRKA_MAP.get(styrka, STYRKA_MAP["MEDEL"])

            row_top = y
            row_bot = y - self.ROW_H

            # Alternating row background
            bg = colors.HexColor("#f9f7f2") if i % 2 == 0 else colors.HexColor("#f4f1e8")
            c.setFillColor(bg)
            c.rect(0, row_bot, self.width, self.ROW_H, fill=1, stroke=0)

            # Left accent stripe
            accent_w = 3.5 if i == 0 else 2
            c.setFillColor(color)
            c.rect(0, row_bot, accent_w, self.ROW_H, fill=1, stroke=0)

            mid_y = (row_top + row_bot) / 2

            # ── Rank ──────────────────────────────────────────────────────
            r_lbl = rank_labels[i] if i < len(rank_labels) else f"#{i+1}"
            c.setFont(_SANS_B, 6.5)
            c.setFillColor(colors.HexColor("#888888"))
            c.drawCentredString(self.RANK_W / 2 + 1*mm, mid_y + 2.5*mm, r_lbl)

            # ── Key ────────────────────────────────────────────────────────
            c.setFont(_SANS_B, 9)
            c.setFillColor(color)
            c.drawString(self.RANK_W + 1.5*mm, mid_y + 1.5*mm, key)

            # ── Label ──────────────────────────────────────────────────────
            c.setFont(_SANS, 6)
            c.setFillColor(colors.HexColor("#777777"))
            c.drawString(self.RANK_W + 1.5*mm, mid_y - 3*mm, lbl[:18])

            # ── Title ──────────────────────────────────────────────────────
            c.setFont(_BODY, 7.5)
            c.setFillColor(colors.HexColor("#333333"))
            c.drawString(BAR_X, mid_y + 3.5*mm, title)

            # ── Bar track ──────────────────────────────────────────────────
            track_y = mid_y - 1.5*mm
            c.setFillColor(colors.HexColor("#dddddd"))
            c.roundRect(BAR_X, track_y, BAR_W, self.BAR_H, 1.5, fill=1, stroke=0)

            # ── Bar fill ───────────────────────────────────────────────────
            fill_w = max(2*mm, BAR_W * pct / 100)
            c.setFillColor(color)
            c.roundRect(BAR_X, track_y, fill_w, self.BAR_H, 1.5, fill=1, stroke=0)

            # ── Percent ────────────────────────────────────────────────────
            pct_x = BAR_X + BAR_W + 2*mm
            c.setFont(_SANS_B, 9)
            c.setFillColor(color)
            c.drawString(pct_x, mid_y - 0.5*mm, f"{pct}%")

            # ── Styrka ─────────────────────────────────────────────────────
            st_x = pct_x + self.PCT_W
            c.setFont(_SANS_B, 6)
            c.setFillColor(colors.HexColor("#888888"))
            c.drawString(st_x, mid_y - 0.5*mm, styrka)

            # ── Bevis/motarg meta ──────────────────────────────────────────
            bevis_n  = len(h.get("bevis", []))
            motarg_n = len(h.get("motarg", []))
            c.setFont(_SANS, 5.5)
            c.setFillColor(colors.HexColor("#aaaaaa"))
            c.drawString(BAR_X, row_bot + 1.5*mm, f"{bevis_n} bevis  ·  {motarg_n} motarg")

            # ── Row divider ────────────────────────────────────────────────
            c.setStrokeColor(colors.HexColor("#dddddd"))
            c.setLineWidth(0.3)
            c.line(0, row_bot, self.width, row_bot)

            y -= self.ROW_H + 1*mm


def _hypothesis_dashboard(story, s, hypotheses: list):
    """Ny grafisk hypotes-dashboard — ersätter _strength_bar_chart."""
    if not hypotheses:
        return
    story.append(Spacer(1, 3*mm))
    lp = _p("HYPOTES-DASHBOARD — KONFIDENSRANKING", s["sub"])
    if lp:
        story.append(lp)
    story.append(Spacer(1, 2*mm))
    story.append(HypothesisBarChart(hypotheses, TW))
    story.append(Spacer(1, 3*mm))


def _executive_conclusion(story, s, hypotheses: list, sammanfattning: str, status: str):
    if not hypotheses and not sammanfattning:
        return

    rank_order = ["HÖG", "MEDEL-HÖG", "MEDEL", "LÅG"]
    def _rank_key(h):
        st = h.get("styrka","MEDEL")
        try: return rank_order.index(st)
        except: return 99
    ranked = sorted(hypotheses, key=_rank_key)
    winner = ranked[0] if ranked else None

    story.append(Spacer(1, 4*mm))

    header_p = Paragraph(
        "ASSESSMENT — ANALYTISK BEDÖMNING",
        ParagraphStyle("ch", fontName=_SANS_B, fontSize=8, textColor=C_WHITE,
                       letterSpacing=5, leading=11)
    )
    header_box = Table([[header_p]], colWidths=[TW])
    header_box.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), colors.HexColor("#0a0a0a")),
        ('TOPPADDING',   (0,0),(-1,-1), 9),
        ('BOTTOMPADDING',(0,0),(-1,-1), 9),
        ('LEFTPADDING',  (0,0),(-1,-1), 14),
        ('RIGHTPADDING', (0,0),(-1,-1), 14),
        ('LINEABOVE',    (0,0),(-1,0),  2.5, C_GRN_MID),
    ]))
    story.append(header_box)

    if winner:
        key   = winner.get("key", "")
        lbl   = winner.get("label", "")
        title = winner.get("title", "")
        tes   = winner.get("tes", "")

        win_str = f"Evidensen stödjer främst: {key}"
        if lbl:   win_str += f"  [{lbl.upper()}]"
        if title: win_str += f"\n{title}"

        win_p = Paragraph(_c(win_str), ParagraphStyle(
            "cw", fontName=_SANS_B, fontSize=12, textColor=C_WHITE, leading=17))

        inner_rows = [[win_p]]
        if tes:
            tes_p = Paragraph(_c(_truncate_at_sentence(tes, 240)), ParagraphStyle(
                "ct", fontName=_BODY_I, fontSize=8.5, textColor=colors.HexColor("#bbbbbb"),
                leading=14))
            inner_rows.append([tes_p])

        inner = Table(inner_rows, colWidths=[TW - 8*mm])
        inner.setStyle(TableStyle([
            ('TOPPADDING',   (0,0),(-1,-1), 5),
            ('BOTTOMPADDING',(0,0),(-1,-1), 5),
            ('LEFTPADDING',  (0,0),(-1,-1), 0),
            ('RIGHTPADDING', (0,0),(-1,-1), 0),
        ]))

        win_box = Table([[inner]], colWidths=[TW])
        win_box.setStyle(TableStyle([
            ('BACKGROUND',   (0,0),(-1,-1), colors.HexColor("#0f1f0f")),
            ('LINEBEFORE',   (0,0),(0,-1),  5, C_GRN_MID),
            ('TOPPADDING',   (0,0),(-1,-1), 14),
            ('BOTTOMPADDING',(0,0),(-1,-1), 14),
            ('LEFTPADDING',  (0,0),(-1,-1), 16),
            ('RIGHTPADDING', (0,0),(-1,-1), 14),
        ]))
        story.append(win_box)

    # ── Hypotes-dashboard (ny grafisk) ────────────────────────────────────────
    _hypothesis_dashboard(story, s, ranked)

    scores = {"HÖG":3,"MEDEL-HÖG":2,"MEDEL":1,"LÅG":0}
    avg = sum(scores.get(h.get("styrka","MEDEL"),1) for h in hypotheses) / max(len(hypotheses),1)
    if avg >= 2.5:   conf_lbl, conf_tc = "HÖG",      C_GRN
    elif avg >= 1.5: conf_lbl, conf_tc = "MEDEL–HÖG", C_GRN_MID
    elif avg >= 0.8: conf_lbl, conf_tc = "MEDEL",     C_BLU_MID
    else:            conf_lbl, conf_tc = "LÅG",       C_RED

    # Föredra conf_pct från normalizer om tillgängligt
    if hypotheses and hypotheses[0].get("conf_pct") is not None:
        max_pct = max(h.get("conf_pct", 0) for h in hypotheses)
        avg_pct = sum(h.get("conf_pct", 0) for h in hypotheses) // max(len(hypotheses), 1)
        conf_display = f"{avg_pct}%  GENOMSNITT  ·  {conf_lbl}"
    else:
        conf_display = conf_lbl

    conf_label = _p("KONFIDENS", ParagraphStyle("cl", fontName=_SANS_B, fontSize=6,
        textColor=C_SUBTLE, letterSpacing=2, leading=10))
    conf_val   = _p(conf_display, ParagraphStyle("cv", fontName=_SANS_B, fontSize=8,
        textColor=conf_tc, letterSpacing=1.5, leading=10))
    if conf_label and conf_val:
        conf_t = Table([[conf_label, conf_val]], colWidths=[TW*0.25, TW*0.75])
        conf_t.setStyle(TableStyle([
            ('BACKGROUND',   (0,0),(-1,-1), colors.HexColor("#f7f5f0")),
            ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
            ('LEFTPADDING',  (0,0),(-1,-1), 8),
            ('RIGHTPADDING', (0,0),(-1,-1), 8),
            ('TOPPADDING',   (0,0),(-1,-1), 5),
            ('BOTTOMPADDING',(0,0),(-1,-1), 5),
            ('LINEABOVE',    (0,0),(-1,0),  .4, C_RULE_L),
        ]))
        story.append(conf_t)

    falsif = winner.get("falsifiering","") if winner else ""
    if falsif:
        fl_label = _p("VAD SKULLE FALSIFIERA DETTA?", ParagraphStyle("fll", fontName=_SANS_B,
            fontSize=6, textColor=C_SUBTLE, letterSpacing=2, leading=10))
        fl_text  = _p(_truncate_at_sentence(falsif, 200), ParagraphStyle("flt", fontName=_BODY_I,
            fontSize=7.5, textColor=colors.HexColor("#6060a0"), leading=12))
        if fl_label and fl_text:
            fl_t = Table([[fl_label, fl_text]], colWidths=[TW*0.28, TW*0.72])
            fl_t.setStyle(TableStyle([
                ('BACKGROUND',   (0,0),(-1,-1), colors.HexColor("#f0f0f8")),
                ('VALIGN',       (0,0),(-1,-1), 'MIDDLE'),
                ('LEFTPADDING',  (0,0),(-1,-1), 8),
                ('RIGHTPADDING', (0,0),(-1,-1), 8),
                ('TOPPADDING',   (0,0),(-1,-1), 6),
                ('BOTTOMPADDING',(0,0),(-1,-1), 6),
                ('LINEABOVE',    (0,0),(-1,0),  .4, colors.HexColor("#b0b0d0")),
                ('LINEBEFORE',   (0,0),(0,-1),  2, colors.HexColor("#8080c0")),
            ]))
            story.append(fl_t)

    metod_txt = (
        "METOD  Analysen testar konkurrerande hypoteser mot evidens, kritik och "
        "red-team-granskning. Källor graderas E1 (rykten) till E5 (primärkälla). "
        "Analysen syftar inte till att ge ett svar — den falsifierar alternativa förklaringar."
    )
    metod_p = _p(metod_txt, ParagraphStyle(
        "mp", fontName=_SANS, fontSize=6.5, textColor=C_SUBTLE,
        leading=10, spaceAfter=0))
    if metod_p:
        metod_box = Table([[metod_p]], colWidths=[TW])
        metod_box.setStyle(TableStyle([
            ('BACKGROUND',   (0,0),(-1,-1), colors.HexColor("#f0ede6")),
            ('TOPPADDING',   (0,0),(-1,-1), 7),
            ('BOTTOMPADDING',(0,0),(-1,-1), 7),
            ('LEFTPADDING',  (0,0),(-1,-1), 12),
            ('RIGHTPADDING', (0,0),(-1,-1), 12),
            ('LINEABOVE',    (0,0),(-1,0),  .4, C_RULE_L),
        ]))
        story.append(metod_box)

    story.append(Spacer(1, 3*mm))

def _reality_banner(story, s, reality: str, rc_text: str):
    bg, tc, label = REALITY_COLORS.get(
        reality.upper(),
        (colors.HexColor("#1a1a1a"), colors.HexColor("#888888"), reality)
    )

    _section_band(story, "Reality Check — Steg 0 — Claim Verification", SEC_BG["reality"])

    status_p = Paragraph(f"<b>{label}</b>", ParagraphStyle(
        "rs", fontName=_SANS_B, fontSize=9, textColor=tc, letterSpacing=3, leading=13))
    status_box = Table([[status_p]], colWidths=[TW])
    status_box.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), bg),
        ('TOPPADDING',   (0,0),(-1,-1), 8),
        ('BOTTOMPADDING',(0,0),(-1,-1), 8),
        ('LEFTPADDING',  (0,0),(-1,-1), 12),
        ('RIGHTPADDING', (0,0),(-1,-1), 12),
        ('LINEBELOW',    (0,-1),(-1,-1), 1, tc),
    ]))
    story.append(status_box)
    story.append(Spacer(1, 2*mm))

    if rc_text:
        claim_lines = [l.strip() for l in rc_text.split('\n')
                       if l.strip() and 'CLAIM' in l.upper()]
        if claim_lines:
            for cl in claim_lines[:4]:
                if 'BEKRÄFTAD' in cl.upper():   tc_cl = C_GRN
                elif 'EJ BEKRÄFTAD' in cl.upper(): tc_cl = C_RED
                else: tc_cl = C_MID
                pg = _p(cl, ParagraphStyle("rcl", fontName=_BODY, fontSize=7.5,
                                           textColor=tc_cl, leading=12, spaceAfter=2))
                if pg: story.append(pg)
        else:
            _render_raw_compact(story, s, rc_text[:600])

    story.append(Spacer(1, 2*mm))

def _render_hypothesis(story, s, hyp: dict):
    title_str = hyp["key"]
    if hyp.get("label"):  title_str += f" [{hyp['label']}]"
    if hyp.get("title"):  title_str += f" — {hyp['title']}"
    pg = _p(title_str, s["h_title"])
    if pg: story.append(pg)
    story.append(HRFlowable(width="30%", thickness=0.5, color=C_RULE_L))
    story.append(Spacer(1, 1.5*mm))

    if hyp.get("tes"):
        story.append(_p("TES", s["sub"]))
        _left_bar_box(story, [hyp["tes"]], C_GRN, C_GRN_BG)

    if hyp.get("bevis"):
        story.append(_p("BEVIS", s["sub"]))
        _left_bar_box(story, hyp["bevis"], C_GRN, C_GRN_BG)

    if hyp.get("motarg"):
        story.append(_p("MOTARGUMENT", s["sub"]))
        _left_bar_box(story, hyp["motarg"], C_RED, C_RED_BG)

    if hyp.get("falsifiering"):
        story.append(_p("FALSIFIERINGSTEST", s["sub"]))
        _left_bar_box(story, [hyp["falsifiering"]], C_AMB, C_AMB_BG)

    story.append(Spacer(1, 3*mm))

def _render_gpt_structured(story, s, gpt: dict):
    for fix in gpt.get("fixes", []):
        story.append(_p(fix["label"], s["sub"]))
        if fix.get("problem"):
            _left_bar_box(story, [fix["problem"]], C_RED, C_RED_BG)
    if gpt.get("svagaste_led"):
        story.append(_p("SVAGASTE LED", s["sub"]))
        _left_bar_box(story, [gpt["svagaste_led"]], C_AMB, C_AMB_BG)
    if gpt.get("alt_h"):
        story.append(_p("ALTERNATIV HYPOTES", s["sub"]))
        _left_bar_box(story, [gpt["alt_h"]], C_BLU, C_BLU_BG)
    if gpt.get("dom"):
        story.append(_p("DOM", s["sub"]))
        is_neg = any(x in gpt["dom"].upper() for x in ["HÅLLER INTE","KOLLAPSAR","SVAG"])
        tc = C_RED if is_neg else C_GRN
        bg = C_RED_BG if is_neg else C_GRN_BG
        _left_bar_box(story, [gpt["dom"]], tc, bg)

def _render_red_structured(story, s, red: dict):
    if red.get("alt_tes"):
        story.append(_p("ALTERNATIV TES", s["sub"]))
        _left_bar_box(story, [red["alt_tes"]], C_RED, C_RED_BG)
    if red.get("alt_bevis"):
        story.append(_p("ALTERNATIVA BEVIS", s["sub"]))
        _left_bar_box(story, red["alt_bevis"], C_AMB, C_AMB_BG)
    if red.get("varfor_fel"):
        story.append(_p("VARFÖR CLAUDE HAR FEL", s["sub"]))
        _left_bar_box(story, [red["varfor_fel"]], C_RED, C_RED_BG)
    if red.get("verdict"):
        story.append(Spacer(1, 2*mm))
        v = red["verdict"].upper()
        tc = C_RED if "KOLLAPSAR" in v else (C_AMB if "MODIFIERAS" in v else C_GRN)
        bg = C_RED_BG if "KOLLAPSAR" in v else (C_AMB_BG if "MODIFIERAS" in v else C_GRN_BG)
        story.append(_pill(f"VERDICT: {red['verdict'][:60]}", tc, bg))
        story.append(Spacer(1, 2*mm))
    if red.get("alt_ranking"):
        story.append(_p("ALTERNATIV RANKING", s["sub"]))
        _left_bar_box(story, red["alt_ranking"], C_BLU, C_BLU_BG)

def _render_raw_compact(story, s, text: str, max_chars: int = 2000):
    if not text: return
    body_s = s["body_sm"]
    SUBS = ("KONFLIKT","SAMSTÄMMIGHET","OSÄKERHET","FIX","STEG","ALT-","VERDICT",
            "VARFÖR","SVAGASTE","DOM:")
    truncated = _truncate_at_sentence(text, max_chars)
    for para in truncated.split('\n\n'):
        para = para.strip()
        if not para: continue
        up = para.upper()
        style = s["sub"] if any(up.startswith(x) for x in SUBS) else body_s
        pg = _p(para, style)
        if pg: story.append(pg)
        story.append(Spacer(1, 1*mm))

def _header_band(story, s, today, status, reality):
    left = Table([
        [Paragraph("SANNINGSMASKINEN", s["brand"])],
        [Paragraph("EPISTEMISKT ANALYSVERKTYG  ·  KONFIDENTIELLT ARBETSMATERIAL", s["brand_s"])],
    ], colWidths=[TW*0.60])
    right_items = []
    if status:  right_items.append(Paragraph(f"STATUS: {status}", s["hdr_r"]))
    if reality: right_items.append(Paragraph(f"REALITY: {reality}", s["hdr_r"]))
    right_items.append(Paragraph(today, s["hdr_r"]))
    right = Table([[r] for r in right_items], colWidths=[TW*0.40])
    for t in [left, right]:
        t.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),1),('BOTTOMPADDING',(0,0),(-1,-1),1),
                                ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0)]))
    band = Table([[left, right]], colWidths=[TW*0.60, TW*0.40])
    band.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),C_DARK),
        ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
        ('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    story.append(band)

def _question_block(story, s, question, status, reality, today):
    q = _c(question or "")
    if not q: return
    qp = _p(q, s["qtitle"])
    if qp:
        qbox = Table([[qp]], colWidths=[TW])
        qbox.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),C_PAPER),
            ('TOPPADDING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),11),
            ('LEFTPADDING',(0,0),(-1,-1),14),('RIGHTPADDING',(0,0),(-1,-1),12),
            ('LINEBEFORE',(0,0),(0,-1),3.5,C_INK),
        ]))
        story.append(Spacer(1, 5*mm))
        story.append(qbox)
        story.append(Spacer(1, 3*mm))

    pills = []
    if status:
        tc, bg = _sc(status)
        pills.append(_pill(status, tc, bg))
    if reality:
        rc_bg, rc_tc, rc_lbl = REALITY_COLORS.get(reality.upper(),
            (C_BLU, C_BLU_BG, reality))
        pills.append(_pill(rc_lbl, rc_tc, rc_bg))

    meta_p = _p(f"Epistemisk hypotesanalys  ·  Claude Opus + GPT-4  ·  {today}", s["meta"])
    if pills and meta_p:
        pill_w = 32*mm
        cols = [pill_w]*len(pills) + [TW - pill_w*len(pills)]
        rt = Table([pills + [meta_p]], colWidths=cols)
        rt.setStyle(TableStyle([
            ('ALIGN',(0,0),(-1,-1),'LEFT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0),
        ]))
        story.append(rt)
    elif meta_p:
        story.append(meta_p)

    story.append(Spacer(1, 1.5*mm))
    tl = _p("Detta dokument försöker inte ge ett svar. Det falsifierar konkurrerande förklaringar.", s["tagline"])
    if tl: story.append(tl)
    story.append(Spacer(1, 2*mm))
    story.append(HRFlowable(width="100%", thickness=0.6, color=C_RULE))

def build_pdf(result: dict) -> bytes:
    buf   = io.BytesIO()
    today = date.today().strftime("%Y-%m-%d")
    s     = _S()

    norm    = normalize_result(result)
    status  = (result.get("status") or "").upper()
    rc      = result.get("reality_check") or {}
    reality = (rc.get("status") or "").upper()
    layers  = result.get("layers") or {}

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(C_RULE_L)
        canvas.setLineWidth(0.3)
        canvas.line(ML, 14.5*mm, PAGE_W-MR, 14.5*mm)
        canvas.setFont(_SANS, 5.5)
        canvas.setFillColor(C_SUBTLE)
        canvas.drawString(ML, 11.5*mm, f"SANNINGSMASKINEN {PDF_VERSION}  ·  {today}")
        canvas.drawRightString(PAGE_W-MR, 11.5*mm, "Sanningen favoriserar ingen sida.")
        canvas.drawCentredString(PAGE_W/2, 8.5*mm, f"— {doc.page} —")
        canvas.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB)

    story = []
    claude_norm = norm.get("claude", {})
    hypotheses  = claude_norm.get("hypotheses", [])

    _header_band(story, s, today, status, reality)
    _question_block(story, s, result.get("question"), status, reality, today)
    _executive_conclusion(story, s, hypotheses,
                          claude_norm.get("sammanfattning",""), status)

    rc_text = rc.get("text") or rc.get("result") or ""
    _reality_banner(story, s, reality, rc_text)

    _section_band(story, "Primäranalys — Claude Opus — Tre Hypoteser + Falsifiering",
                  SEC_BG["primary"])

    if claude_norm.get("grundfakta"):
        story.append(_p("GRUNDFAKTA", s["sub"]))
        _left_bar_box(story, [claude_norm["grundfakta"]], C_GRN, C_GRN_BG)

    if hypotheses:
        for hyp in hypotheses:
            _render_hypothesis(story, s, hyp)
        _hypothesis_dashboard(story, s, hypotheses)
    else:
        _render_raw_compact(story, s, result.get("claude_answer",""), max_chars=3000)

    if claude_norm.get("ranking"):
        story.append(_p("RANKING", s["sub"]))
        _left_bar_box(story, claude_norm["ranking"], C_INK, C_PAPER, bar_w=3)

    if layers.get("ground"):
        _section_band(story, "Layer 1–5 — Destillerad Journalistisk Analys",
                      SEC_BG["layers"])
        _render_raw_compact(story, s, layers["ground"], max_chars=3000)

    for k, label in [
        ("deep1","Fördjupning 1 — Systemet Bakåt i Tiden"),
        ("deep2","Fördjupning 2 — Tre Linser i Detalj"),
        ("deep3","Fördjupning 3 — Fullständig Analytiker-Output"),
    ]:
        if layers.get(k):
            _section_band(story, label, SEC_BG["layers"])
            _render_raw_compact(story, s, layers[k], max_chars=2000)

    _section_band(story, "GPT-4 Kritiker — Steg 2 — Oberoende Motanalys",
                  SEC_BG["gpt"])
    gpt_norm = norm.get("gpt", {})
    if gpt_norm.get("fixes"):
        _render_gpt_structured(story, s, gpt_norm)
    else:
        _render_raw_compact(story, s, result.get("gpt_answer",""), max_chars=1500)

    _section_band(story, "Konfliktanalys — Steg 3 — Epistemiska Meningsskiljaktigheter",
                  SEC_BG["conflict"])
    _render_raw_compact(story, s, result.get("conflict_report",""), max_chars=1200)

    _section_band(story, "Red Team — Steg 4 — Konkurrerande Modell",
                  SEC_BG["redteam"])
    red_norm = norm.get("red", {})
    if red_norm.get("verdict") or red_norm.get("alt_tes"):
        _render_red_structured(story, s, red_norm)
    else:
        _render_raw_compact(story, s, result.get("red_team_report",""), max_chars=1500)

    final = result.get("final_analysis","")
    if final:
        _section_band(story, "Reviderad Analys — Efter Red Team-Utmaning",
                      SEC_BG["revised"])
        rev_norm = norm.get("claude_revised", {})
        if rev_norm and rev_norm.get("hypotheses"):
            for hyp in rev_norm["hypotheses"]:
                _render_hypothesis(story, s, hyp)
            _hypothesis_dashboard(story, s, rev_norm["hypotheses"])
        else:
            _render_raw_compact(story, s, final, max_chars=2500)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()
