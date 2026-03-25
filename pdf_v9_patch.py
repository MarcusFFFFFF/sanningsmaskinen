#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Applicerar tre ändringar på app.py för att koppla in pdf_export_v9:

1. Lägger till _build_pdf_v9() hjälpfunktion efter _slugify()
2. Byter ut PDF-knappen i export-sektionen (c3)
3. Lägger till PDF-knapp direkt efter Executive Summary

Kör: python3 pdf_v9_patch.py app.py app_v9.py
"""

import sys

PATCH_1_FIND = '''def _slugify(q, n=45):
    for k,v in {'å':'a','ä':'a','ö':'o','Å':'A','Ä':'A','Ö':'O'}.items():
        q = (q or "").replace(k,v)
    return re.sub(r'\\s+','_', re.sub(r'[^a-zA-Z0-9\\s]','', q).strip().lower())[:n] or "analys"'''

PATCH_1_REPLACE = '''def _slugify(q, n=45):
    for k,v in {'å':'a','ä':'a','ö':'o','Å':'A','Ä':'A','Ö':'O'}.items():
        q = (q or "").replace(k,v)
    return re.sub(r'\\s+','_', re.sub(r'[^a-zA-Z0-9\\s]','', q).strip().lower())[:n] or "analys"


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
            for sent in re.split(r"(?<=[.!?])\\s+", src):
                s = sent.strip()
                s = re.sub(r"\\[FAKTA\\]|\\[INFERENS\\]|\\[PÅGÅENDE\\]|\\*{1,3}", "", s).strip()
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
        for pat in [r"De facto stängt[^.]+\\.", r"Sundet[^.]+stängt[^.]+\\.",
                    r"\\d+%\\s+trafikminskning[^.]+"]:
            m = re.search(pat, txt, re.IGNORECASE)
            if m:
                operativ["nu"] = m.group(0)[:110].strip()
                break
        if not operativ.get("nu"):
            operativ["nu"] = "Pågående situation — se analys."

        # Härnäst
        for pat in [r"\\d+\\s*(?:mars|april|maj)[^.]+deadline[^.]+\\.",
                    r"deadline[^.]+löper[^.]+\\.", r"förhandlings\\w*\\s+\\w+\\s+\\d+"]:
            m = re.search(pat, txt, re.IGNORECASE)
            if m:
                operativ["nasta"] = m.group(0)[:110].strip()
                break
        if not operativ.get("nasta"):
            operativ["nasta"] = "Nästa avgörande moment okänt — följ löpande."

        # Risk
        for pat in [r"(?:HÖG|KRITISK)[^.]*DIA[^.]+\\.",
                    r"DIA[^.]+(?:månader|veckor)[^.]+\\.",
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
        return b""'''


# PATCH 2: PDF-knappen i export-sektionen (c3)
PATCH_2_FIND = '''    with c3:
        try:
            from pdf_export import build_pdf as _bp
            # Säkerställ att ranked finns i result-objektet
            r_for_pdf = dict(r)
            if "ranked" not in r_for_pdf or not r_for_pdf["ranked"]:
                r_for_pdf["ranked"] = ranked
            st.download_button("📄 PDF",_bp(r_for_pdf),f"sanningsmaskinen_{today_str}_{slug}.pdf","application/pdf",use_container_width=True)
        except: pass'''

PATCH_2_REPLACE = '''    with c3:
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
            pass'''


# PATCH 3: PDF-knapp direkt efter Executive Summary-blocket
PATCH_3_FIND = '''    # 3. HYPOTESER
    if ranked:'''

PATCH_3_REPLACE = '''    # PDF-snabbexport — direkt under Executive Summary
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
    if ranked:'''


def apply(src_path: str, dst_path: str):
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    applied = 0
    for i, (find, replace, name) in enumerate([
        (PATCH_1_FIND, PATCH_1_REPLACE, "_build_pdf_v9 funktion"),
        (PATCH_2_FIND, PATCH_2_REPLACE, "PDF-knapp i export"),
        (PATCH_3_FIND, PATCH_3_REPLACE, "PDF-knapp efter exec summary"),
    ], 1):
        if find in content:
            content = content.replace(find, replace)
            print(f"  Patch {i} ({name}): OK")
            applied += 1
        else:
            print(f"  Patch {i} ({name}): HITTADES INTE")

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n{applied}/3 patchar applicerade → {dst_path}")
    return applied


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "app.py"
    dst = sys.argv[2] if len(sys.argv) > 2 else "app_v9.py"
    n = apply(src, dst)
    if n < 3:
        print("\nVARNING: Inte alla patchar applicerades.")
        print("Kontrollera att app.py matchar v8.18-versionen.")
