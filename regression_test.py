# -*- coding: utf-8 -*-
"""
Regression-svit för Sanningsmaskinen normalizer.
Kör v1.5 mot riktig produktionsdata och flaggar avvikelser.

Användning:
    python3 regression_test.py [path/to/fixtures]
"""
import sys
import json
import os
from pathlib import Path
from collections import Counter

sys.path.insert(0, '/home/claude')
from normalizer import (
    normalize_claude_answer,
    compute_hypothesis_scores,
    _ensure_three_hypotheses,
    _source_quality_from_bevis,
)


def analyze_fixture(filepath):
    """Returnerar dict med analys av en fixture-fil."""
    with open(filepath, 'r', encoding='utf-8') as f:
        d = json.load(f)

    question = d.get('question', '')
    raw_claude = d.get('claude_answer', '') or ''
    status = d.get('status', '')
    rc_status = (d.get('reality_check') or {}).get('status', '')

    # v1.4 — vad som faktiskt visades på UI:t
    old_ranked = d.get('ranked') or []

    # v1.5 — kör om samma råtext genom nya normalizern
    parsed = normalize_claude_answer(raw_claude)['hypotheses']
    new_ranked = _ensure_three_hypotheses(
        sorted(compute_hypothesis_scores(parsed),
               key=lambda h: h.get('conf', 0),
               reverse=True)
    )

    # Källkvalitet per hypotes (visar att E-tag-fixen fungerar)
    src_q = [_source_quality_from_bevis(h.get('bevis', [])) for h in parsed]

    # Räkna E-taggar som hittades i råtexten med nya regexen
    import re
    e_tags = re.findall(r'\[(E[1-5]|FAKTA)\b', raw_claude)
    e_distribution = Counter(e_tags)

    return {
        'file': os.path.basename(filepath),
        'question': question[:75],
        'status': status,
        'rc_status': rc_status,
        'raw_length': len(raw_claude),
        'old_ranked': old_ranked,
        'new_ranked': new_ranked,
        'parsed_count': len(parsed),
        'src_quality': src_q,
        'e_tags_total': len(e_tags),
        'e_distribution': dict(e_distribution),
    }


def flag_issues(a):
    """Returnerar lista med varningar för en analys."""
    issues = []

    if not a['old_ranked']:
        issues.append("v1.4 hade TOMT ranked → frontend-fallback körde då")

    # Kollar v1.5 för kluster (två conf_pct exakt samma)
    new_pcts = [h.get('conf_pct') for h in a['new_ranked']]
    seen = []
    for p in new_pcts:
        if p in seen:
            issues.append(f"v1.5 har fortfarande kluster: två hypoteser conf_pct={p}")
        seen.append(p)

    if a['parsed_count'] < 3:
        issues.append(f"Parsern hittade bara {a['parsed_count']}/3 hypoteser — fallback aktiveras")

    if a['e_tags_total'] == 0:
        issues.append("0 E-taggar i hela råtexten — Claude följde inte E1-E5-formatet")
    elif a['e_tags_total'] < 6:
        issues.append(f"Bara {a['e_tags_total']} E-taggar — Claude underutnyttjar källhierarkin")

    return issues


def format_ranked(ranked):
    """Format: 'H1=87 H2=79 H3=67'"""
    if not ranked:
        return "tomt"
    return " ".join(f"{h.get('key')}={h.get('conf_pct')}"
                    for h in ranked if h.get('conf_pct') is not None)


def main():
    fixtures_dir = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/fixtures'
    files = sorted(Path(fixtures_dir).glob('*.json'))

    print(f"\n═══ Regression mot {len(files)} fixtures (v1.4 → v1.5) ═══\n")

    all_issues = []
    e_tag_counts = []

    for filepath in files:
        a = analyze_fixture(filepath)
        issues = flag_issues(a)
        all_issues.extend([(a['file'], i) for i in issues])
        e_tag_counts.append(a['e_tags_total'])

        # Kort variant av frågan
        q = a['question'][:55] + ('…' if len(a['question']) > 55 else '')

        print(f"  {a['file'][:50]}...")
        print(f"    Fråga:    {q}")
        print(f"    Status:   {a['status']:<12} RC: {a['rc_status']}")
        print(f"    v1.4:     {format_ranked(a['old_ranked'])}")
        print(f"    v1.5:     {format_ranked(a['new_ranked'])}")
        print(f"    E-taggar: {a['e_tags_total']} st  fördelning: {a['e_distribution']}")

        if a['src_quality']:
            sq = "/".join(f"{x:.2f}" for x in a['src_quality'])
            print(f"    src_q:    {sq}")

        if issues:
            for i in issues:
                print(f"    ⚠  {i}")
        print()

    # Sammanfattning
    print("═" * 60)
    print(f"Total: {len(files)} fixtures, {len(all_issues)} flaggade rader")
    print()

    # E-tag-statistik (största fyndet — Claude måste bli bättre på E-taggar)
    avg_etags = sum(e_tag_counts) / len(e_tag_counts) if e_tag_counts else 0
    min_etags = min(e_tag_counts)
    max_etags = max(e_tag_counts)
    print(f"E-taggar per analys: min={min_etags} max={max_etags} snitt={avg_etags:.1f}")
    print(f"  (Optimalt: 9+ per analys = 3 hypoteser × 3 bevis × E-tag)")
    print()

    if all_issues:
        print("ALLA FLAGGNINGAR:")
        for f, i in all_issues:
            print(f"  {f[:45]}: {i}")


if __name__ == "__main__":
    main()
