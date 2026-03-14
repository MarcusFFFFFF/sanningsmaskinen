# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN — NORMALIZER v1.3
Förbättringar:
- Bevarar URL:er
- Robustare hypotesparser
- Mer stabil confidence-scoring
- Vid identiska råvärden används kontrollerad tie-break istället för identiska procentsatser
"""

import math
import re

_SOURCE_LABELS = {
    "FAKTA": ("Faktapåstående", 0.5),
    "E1": ("Ryktesspridning", 0.2),
    "E2": ("Sekundäranalys", 0.4),
    "E3": ("Trovärdig rapport", 0.6),
    "E4": ("Kvalitetsjournalistik", 0.8),
    "E5": ("Officiell källa", 1.0),
}

STYRKA_VAL = {
    "HÖG": 0.90,
    "MEDEL-HÖG": 0.70,
    "MEDEL": 0.50,
    "LÅG": 0.25,
}


def _preserve_urls(text: str) -> str:
    def _wrap(m):
        url = m.group(0)
        domain = re.search(r'https?://(?:www\.)?([^/\s\)\]]+)', url)
        label = domain.group(1) if domain else url[:40]
        return f'[{label}]({url})'
    return re.sub(r'(?<!\]\()https?://[^\s\)\]<"]+', _wrap, text or "")


def _clean_line(line: str) -> str:
    line = _preserve_urls(line or "")
    line = re.sub(r'^#{1,6}\s+', '', line)
    line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
    line = re.sub(r'\*(.+?)\*', r'\1', line)
    return line.strip()


def normalize_references(text: str) -> str:
    if not text:
        return text
    text = _preserve_urls(text)

    def _replace(m):
        tag = m.group(1).upper()
        entry = _SOURCE_LABELS.get(tag)
        if entry:
            label, _ = entry
            return f'[{label}]'
        return m.group(0)

    return re.sub(r'\[([A-ZÅÄÖ0-9]+)\](?!\()', _replace, text)


def _source_quality_from_bevis(bevis_list: list) -> float:
    weights = []
    for b in bevis_list:
        for tag in re.findall(r'\[(E[1-5]|FAKTA)\]', b or "", re.IGNORECASE):
            entry = _SOURCE_LABELS.get(tag.upper())
            if entry:
                weights.append(entry[1])
    return sum(weights) / len(weights) if weights else 0.5


def _evidence_count_factor(n: int) -> float:
    if n <= 0:
        return 0.30
    return min(1.0, 0.40 + 0.25 * math.log2(n + 1))


def compute_hypothesis_scores(hypotheses: list) -> list:
    if not hypotheses:
        return hypotheses

    scored = []
    for idx, h in enumerate(hypotheses):
        styrka = (h.get("styrka") or "MEDEL").upper()
        ev_strength = STYRKA_VAL.get(styrka, 0.50)
        bevis = h.get("bevis", []) or []
        ev_count_f = _evidence_count_factor(len(bevis))
        src_quality = _source_quality_from_bevis(bevis)
        raw = ev_strength * ev_count_f * src_quality

        # liten stabil tie-break så att helt lika råvärden inte blir identiska i UI
        raw += (len(bevis) * 0.003) + ((3 - min(idx, 3)) * 0.001)

        scored.append({**h, "conf_raw": raw})

    max_raw = max(s["conf_raw"] for s in scored) or 1.0
    min_raw = min(s["conf_raw"] for s in scored)
    span = max_raw - min_raw

    if span < 1e-9:
        defaults = [0.68, 0.52, 0.36, 0.24]
        out = []
        for i, s in enumerate(scored):
            conf = defaults[i] if i < len(defaults) else max(0.20, defaults[-1] - 0.04 * (i - len(defaults) + 1))
            ss = dict(s)
            ss["conf"] = round(conf, 2)
            ss["conf_pct"] = int(conf * 100)
            out.append(ss)
        return out

    out = []
    for s in scored:
        norm = 0.20 + 0.75 * (s["conf_raw"] - min_raw) / span
        ss = dict(s)
        ss["conf"] = round(norm, 2)
        ss["conf_pct"] = int(norm * 100)
        out.append(ss)

    return out


def normalize_claude_answer(text: str) -> dict:
    result = {
        "grundfakta": "",
        "hypotheses": [],
        "ranking": [],
        "sammanfattning": "",
        "raw": text,
    }
    if not text:
        return result

    lines = text.split('\n')

    gf_lines = []
    in_gf = False
    for line in lines:
        up = line.strip().upper()
        if any(x in up for x in ["GRUNDFAKTA", "VERIFIERADE GRUNDFAKTA", "BAKGRUND", "FAKTABAS"]):
            in_gf = True
            continue
        if in_gf:
            if re.match(r'H[1-4]\s*[\[\(—\-:]', line.strip()):
                break
            if up.startswith("##") and any(x in up for x in ["H1", "H2", "H3"]):
                break
            gf_lines.append(_clean_line(line))
    result["grundfakta"] = '\n'.join(gf_lines).strip()

    h_pattern = re.compile(r'(?:^|\n)\s*(?:#+\s*)?(H[1-4])\s*[\[\(—\-:\s]', re.IGNORECASE)
    h_matches = list(h_pattern.finditer('\n' + text))
    for idx, match in enumerate(h_matches):
        h_key = match.group(1).upper()
        start = match.start()
        end = h_matches[idx + 1].start() if idx + 1 < len(h_matches) else len('\n' + text)
        block = ('\n' + text)[start:end]
        result["hypotheses"].append(_parse_hypothesis_block(block, h_key))

    ranking_lines = []
    in_ranking = False
    for line in lines:
        up = line.strip().upper()
        if any(x in up for x in ["RANKING", "SLUTSATS", "VINNANDE", "SAMMANFATTANDE"]):
            in_ranking = True
            continue
        if in_ranking:
            s = line.strip()
            if not s:
                continue
            if re.match(r'^#{1,3}\s', s) and not any(x in s.upper() for x in ["H1", "H2", "H3"]):
                break
            if any(x in s.upper() for x in ["GPT", "KRITIKER", "KONFLIKT", "RED TEAM"]):
                break
            ranking_lines.append(_clean_line(s))
            if len(ranking_lines) > 12:
                break
    result["ranking"] = [r for r in ranking_lines if r]

    for i, line in enumerate(lines):
        if any(x in line.upper() for x in ["SAMMANFATTANDE", "AVGÖRANDE INSIKT", "BRUTALA INSIKT"]):
            result["sammanfattning"] = '\n'.join(_clean_line(l) for l in lines[i:i + 8] if l.strip())
            break

    return result


def _parse_hypothesis_block(block: str, h_key: str) -> dict:
    hyp = {
        "key": h_key,
        "label": "",
        "title": "",
        "tes": "",
        "bevis": [],
        "motarg": [],
        "falsifiering": "",
        "styrka": "",
        "styrka_motivering": "",
    }

    lines = block.split('\n')
    first_line = ""
    first_line_idx = 0
    for idx, l in enumerate(lines):
        if l.strip():
            first_line = l.strip()
            first_line_idx = idx
            break

    label_match = re.search(r'\[([A-ZÅÄÖ\s]+)\]', first_line)
    if label_match:
        hyp["label"] = label_match.group(1).strip()

    dash_match = re.search(r'[—\-]\s*(.+)$', first_line)
    if dash_match:
        hyp["title"] = dash_match.group(1).strip()
    elif label_match:
        hyp["title"] = first_line[label_match.end():].strip().lstrip('—- ')

    current_section = None
    buf = []

    def flush_buf(section, current_buf):
        text = ' '.join(_preserve_urls(l.strip()) for l in current_buf if l.strip())
        if not text:
            return
        if section == "tes":
            hyp["tes"] = text
        elif section == "bevis":
            hyp["bevis"].append(text)
        elif section == "motarg":
            hyp["motarg"].append(text)
        elif section == "falsif":
            hyp["falsifiering"] = text

    for line in lines[first_line_idx + 1:]:
        s = line.strip()
        up = s.upper()

        if not s:
            flush_buf(current_section, buf)
            buf = []
            continue

        if up.startswith("STYRKA"):
            flush_buf(current_section, buf)
            buf = []
            for key in ["HÖG", "MEDEL-HÖG", "MEDEL", "LÅG"]:
                if key in up:
                    hyp["styrka"] = key
                    rest = s[s.upper().find(key) + len(key):].strip(" :—-()")
                    hyp["styrka_motivering"] = _clean_line(rest)
                    break
            current_section = None
            continue

        if up.startswith("TES:") or up.startswith("**TES") or up == "TES":
            flush_buf(current_section, buf)
            buf = []
            current_section = "tes"
            rest = re.sub(r'^\*?\*?TES:?\*?\*?\s*', '', s, flags=re.IGNORECASE).strip()
            if rest:
                buf.append(rest)
            continue

        if (re.match(r'\*?\*?BEVIS\s*\d*\s*[\[\(:*]', up) or
            re.match(r'\*?\*?BEVIS:?\*?\*?$', up) or
            (current_section == "bevis" and re.match(r'\d+[\.\)]\s+', s))):
            flush_buf(current_section, buf)
            buf = []
            current_section = "bevis"
            rest = re.sub(r'^\*?\*?BEVIS\s*\d*\s*(\[[^\]]*\])?\s*:?\*?\*?\s*', '', s, flags=re.IGNORECASE).strip()
            rest = re.sub(r'^\d+[\.\)]\s+', '', rest).strip()
            if rest:
                buf.append(rest)
            continue

        if current_section == "bevis" and re.match(r'\d+[\.\)]\s+', s):
            flush_buf(current_section, buf)
            buf = []
            rest = re.sub(r'^\d+[\.\)]\s+', '', s).strip()
            if rest:
                buf.append(rest)
            continue

        if (re.match(r'\*?\*?MOTARG(?:UMENT)?\s*\d*\s*:?\*?\*?', up) or
            (up.startswith("MOTARG") and not up.startswith("MOTARGUMENT:"))):
            flush_buf(current_section, buf)
            buf = []
            current_section = "motarg"
            rest = re.sub(r'^\*?\*?MOTARG(?:UMENT)?\s*\d*\s*:?\*?\*?\s*', '', s, flags=re.IGNORECASE).strip()
            if rest:
                buf.append(rest)
            continue

        if current_section == "motarg" and re.match(r'\d+[\.\)]\s+', s):
            flush_buf(current_section, buf)
            buf = []
            rest = re.sub(r'^\d+[\.\)]\s+', '', s).strip()
            if rest:
                buf.append(rest)
            continue

        if "FALSIFIERING" in up:
            flush_buf(current_section, buf)
            buf = []
            current_section = "falsif"
            rest = re.sub(r'^\*?\*?FALSIFIERINGS(?:TEST)?:?\*?\*?\s*', '', s, flags=re.IGNORECASE).strip()
            if rest:
                buf.append(rest)
            continue

        if re.match(r'H[1-4]\s*[\[\(—\-:]', s):
            break

        buf.append(s)

    flush_buf(current_section, buf)

    if not hyp["styrka"]:
        hyp["styrka"] = "MEDEL"

    return hyp


def normalize_gpt_answer(text: str) -> dict:
    result = {"fixes": [], "svagaste_led": "", "alt_h": "", "dom": "", "raw": text}
    for m in re.compile(r'(FIX\d[^:]*:)\s*(.+?)(?=FIX\d|SVAGASTE|ALT-H|DOM:|$)', re.DOTALL | re.IGNORECASE).finditer(text or ""):
        content = m.group(2).strip()
        problem_match = re.search(r'PROBLEM:\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        problem = problem_match.group(1).strip() if problem_match else content[:200]
        result["fixes"].append({"label": m.group(1).strip(), "problem": _clean_line(problem)})
    for field, pattern in [
        ("svagaste_led", r'SVAGASTE_?LED:\s*(.+?)(?=ALT-H|DOM:|$)'),
        ("alt_h", r'ALT-H:\s*(.+?)(?=DOM:|SVAGASTE|$)'),
        ("dom", r'DOM:\s*(.+?)(?=$|\n\n)'),
    ]:
        m = re.search(pattern, text or "", re.DOTALL | re.IGNORECASE)
        if m:
            result[field] = _clean_line(m.group(1).strip()[:400])
    return result


def normalize_red_team(text: str) -> dict:
    result = {"alt_tes": "", "alt_bevis": [], "varfor_fel": "", "verdict": "", "alt_ranking": [], "raw": text}
    for field, pattern in [
        ("alt_tes", r'ALT-TES:\s*(.+?)(?=ALT-BEVIS|VARFÖR|VERDICT|$)'),
        ("varfor_fel", r'VARFÖR CLAUDE HAR FEL:\s*(.+?)(?=STEG|VERDICT|ALT-RANKING|$)'),
        ("verdict", r'VERDICT:\s*(.+?)(?=ALTERNATIV|ALT-RANKING|$|\n\n)'),
    ]:
        m = re.search(pattern, text or "", re.DOTALL | re.IGNORECASE)
        if m:
            result[field] = _clean_line(m.group(1).strip()[:500])

    for m in re.finditer(r'ALT-BEVIS\d+:\s*(.+?)(?=ALT-BEVIS\d|VARFÖR|STEG\s*3|$)', text or "", re.DOTALL | re.IGNORECASE):
        result["alt_bevis"].append(_clean_line(m.group(1).strip()[:300]))

    rank_section = re.search(r'ALTERNATIV RANKING:\s*(.+?)(?=$|\Z)', text or "", re.DOTALL | re.IGNORECASE)
    if rank_section:
        for line in rank_section.group(1).split('\n'):
            s = line.strip()
            if s and re.match(r'^\d+[\.\)]', s):
                result["alt_ranking"].append(_clean_line(s))

    return result


def normalize_result(result: dict) -> dict:
    claude_norm = normalize_claude_answer(result.get("claude_answer", ""))
    claude_norm["hypotheses"] = compute_hypothesis_scores(claude_norm["hypotheses"])

    normalized = {
        "claude": claude_norm,
        "gpt": normalize_gpt_answer(result.get("gpt_answer", "")),
        "red": normalize_red_team(result.get("red_team_report", "")),
    }

    if result.get("final_analysis"):
        revised_raw = result["final_analysis"]
        revised_norm = normalize_claude_answer(revised_raw)
        revised_norm["hypotheses"] = compute_hypothesis_scores(revised_norm["hypotheses"])
        normalized["claude_revised"] = revised_norm
        normalized["revised_text"] = normalize_references(revised_raw)

    return normalized