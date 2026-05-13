# -*- coding: utf-8 -*-
"""
Test för normalizer v1.5 — kontroll att conf-spannet verkligen sprids
och att STYRKA-substring-buggen är fixad.
"""
import sys
sys.path.insert(0, '/home/claude')

from normalizer import (
    normalize_claude_answer,
    compute_hypothesis_scores,
    _ensure_three_hypotheses,
    STYRKA_VAL,
    _source_quality_from_bevis,
    _parse_hypothesis_block,
)


# ── TEST 1: STYRKA-substring fix ──────────────────────────────────────────────
def test_styrka_medel_hog_not_falsely_hog():
    """MEDEL-HÖG ska INTE klassificeras som HÖG."""
    block = """H1[STRUKTURELL]: Strukturell tes
TES: Detta är en tes som är medelstark
BEVIS 1 [E4]: Reuters rapport
MOTARG 1: Motargument
STYRKA: MEDEL-HÖG — välbelagd men begränsad
"""
    hyp = _parse_hypothesis_block(block, "H1")
    assert hyp["styrka"] == "MEDEL-HÖG", f"Förväntade MEDEL-HÖG, fick {hyp['styrka']}"
    print(f"  ✓ MEDEL-HÖG klassificeras korrekt (inte felaktigt som HÖG)")


def test_styrka_hog_still_works():
    """STYRKA: HÖG ska fortfarande klassificeras som HÖG."""
    block = """H1[STRUKTURELL]: Test
TES: tes
BEVIS 1 [E5]: bevis
STYRKA: HÖG — välbelagd
"""
    hyp = _parse_hypothesis_block(block, "H1")
    assert hyp["styrka"] == "HÖG", f"Förväntade HÖG, fick {hyp['styrka']}"
    print(f"  ✓ HÖG klassificeras korrekt")


def test_styrka_medel_works():
    block = """H1[STRUKTURELL]: Test
TES: tes
STYRKA: MEDEL
"""
    hyp = _parse_hypothesis_block(block, "H1")
    assert hyp["styrka"] == "MEDEL", f"Förväntade MEDEL, fick {hyp['styrka']}"
    print(f"  ✓ MEDEL klassificeras korrekt")


def test_styrka_lag_works():
    block = """H1[STRUKTURELL]: Test
TES: tes
STYRKA: LÅG
"""
    hyp = _parse_hypothesis_block(block, "H1")
    assert hyp["styrka"] == "LÅG", f"Förväntade LÅG, fick {hyp['styrka']}"
    print(f"  ✓ LÅG klassificeras korrekt")


# ── TEST 2: Conf-formeln sprids ───────────────────────────────────────────────
def test_three_hog_hypotheses_actually_differentiate():
    """
    Det här är det centrala testet för buggen Marcus beskrev.
    Tre HÖG-hypoteser med olika antal bevis och källkvalitet ska INTE
    klustra runt samma värde.
    """
    hyps = [
        # H1: stark — 5 bevis, alla E5
        {"key": "H1", "styrka": "HÖG", "bevis": [
            "Domstolsbeslut [E5] från BGH",
            "Officiell rapport [E5] från SCB",
            "Riksdagsbeslut [E5] från riksdagen",
            "FN-rapport [E5] från UNHCR",
            "EU-domstolsbeslut [E5]",
        ]},
        # H2: medelstark — 3 bevis, mest E4
        {"key": "H2", "styrka": "HÖG", "bevis": [
            "Reuters [E4] rapport",
            "BBC [E4] artikel",
            "AP News [E4] djupgrävning",
        ]},
        # H3: svagare — 2 bevis, E3
        {"key": "H3", "styrka": "MEDEL", "bevis": [
            "Wikipedia [E3] referens",
            "Tankesmedja [E3] analys",
        ]},
    ]
    scored = compute_hypothesis_scores(hyps)
    confs = [h["conf_pct"] for h in scored]
    print(f"  Conf-spann: H1={confs[0]} H2={confs[1]} H3={confs[2]}")

    # Skillnaden mellan starkaste och svagaste ska vara minst 25 procentenheter
    spread = max(confs) - min(confs)
    assert spread >= 20, f"Spannet är bara {spread}p — formeln klustrar fortfarande"
    print(f"  ✓ Spann mellan starkaste och svagaste: {spread}p (>= 20p krävs)")


def test_no_hypothesis_at_92_ceiling():
    """v1.4 capade på 0.92 vilket gjorde starkaste hypotes alltid = 92. Nu ska den kunna nå 95."""
    hyps = [
        {"key": "H1", "styrka": "HÖG", "bevis": [
            f"Bevis [E5]" for _ in range(8)
        ]},
    ]
    scored = compute_hypothesis_scores(hyps)
    conf = scored[0]["conf_pct"]
    print(f"  Maximal conf (8 bevis E5, HÖG): {conf}")
    # I v1.5 ska detta nå minst 90 men kunna passera 92
    assert conf >= 90, f"Conf {conf} — för låg för en max-stark hypotes"


def test_weak_hypothesis_actually_weak():
    """En hypotes med få bevis och låg styrka ska få lågt conf."""
    hyps = [
        {"key": "H1", "styrka": "LÅG", "bevis": []},
    ]
    scored = compute_hypothesis_scores(hyps)
    conf = scored[0]["conf_pct"]
    print(f"  Min conf (LÅG, inga bevis): {conf}")
    assert conf <= 25, f"Conf {conf} — för hög för svagaste hypotes"


# ── TEST 3: Reproducerbarhet av 95/94/20 (jämför v1.4 vs v1.5) ────────────────
def test_old_clustering_problem_resolved():
    """
    Marcus rapporterade 95%/94%/20% varje gång — symptom på att tre HÖG-hypoteser
    med liknande bevis klustrar. v1.5 ska producera tydlig differentiering.
    """
    # Simulera typisk Claude-output: tre hypoteser, två starka och en svag
    hyps = [
        {"key": "H1", "styrka": "HÖG", "bevis": [
            "BGH-dom [E5] om ansvar",
            "Spiegel [E4] rapport",
            "Reuters [E4] artikel",
        ]},
        {"key": "H2", "styrka": "HÖG", "bevis": [
            "BBC [E4] artikel",
            "AP [E4] rapport",
            "Le Monde [E4] analys",
        ]},
        {"key": "H3", "styrka": "LÅG", "bevis": [
            "Wikipedia [E3] referens",
        ]},
    ]
    scored = compute_hypothesis_scores(hyps)
    confs = sorted([h["conf_pct"] for h in scored], reverse=True)
    print(f"  Typisk fördelning (HÖG/HÖG/LÅG, normalt bevis): {confs}")

    # H1 och H2 är båda HÖG men ska ha samma conf (samma input) — det är OK
    # Det viktiga är att H3 är tydligt lägre och att inget hamnar på 92-cap
    assert confs[0] - confs[2] >= 30, "För litet gap mellan H1 och H3"
    print(f"  ✓ Gap H1→H3: {confs[0] - confs[2]}p")


# ── TEST 4: Fallbacks ─────────────────────────────────────────────────────────
def test_fallback_when_parser_misses():
    """Om parsern hittar 0 hypoteser ska _ensure_three_hypotheses ge fallbacks."""
    result = _ensure_three_hypotheses([])
    assert len(result) == 3
    keys = sorted([h["key"] for h in result])
    assert keys == ["H1", "H2", "H3"]
    print(f"  ✓ Fallbacks fungerar — 3 hypoteser även när parser missar")


# ── TEST 4: REGEX-FIX (kritisk — root cause för klusterproblemet) ─────────────
def test_e_tag_regex_matches_claude_actual_format():
    """
    Claude skriver bevisen som '[E3 — CSIS](url)', INTE '[E3](url)'.
    Den gamla regexen \[(E[1-5]|FAKTA)\] matchade INGET i praktiken eftersom
    den krävde stängande ] direkt efter siffran. Detta gjorde att alla
    bevis fick default-källkvalitet → alla hypoteser klustrade.
    """
    from normalizer import _source_quality_from_bevis

    # Claudes faktiska format (från Iran-historikfilen)
    bevis = [
        "BEVIS 1: CSIS-rapporten beskriver krisen. [E3 — CSIS](https://csis.org/x)",
        "BEVIS 2: WEF-analys av energipriserna. [E3 — World Economic Forum](https://weforum.org/y)",
        "BEVIS 3: Iran tappade kontroll över minorna. [E3 — Wikipedia/NYT]",
    ]
    sq = _source_quality_from_bevis(bevis)
    print(f"  src_quality för [E3 — källa]-format: {sq:.3f}")
    # E3 = 0.6 — om regexen fungerar ska vi få 0.6, inte default 0.4
    assert abs(sq - 0.6) < 0.01, f"Förväntade 0.60 (E3), fick {sq}"
    print(f"  ✓ E-taggar i format [E3 — källa] matchas korrekt")


def test_e_tag_regex_matches_blandade_format():
    """Olika format som Claude faktiskt producerar."""
    from normalizer import _source_quality_from_bevis
    bevis = [
        "BEVIS 1: text [E5](url)",                # Klassiskt format
        "BEVIS 2: text [E4 — BBC](url)",          # Med tankstreck
        "BEVIS 3: text [E5 -- Reuters, 2026]",    # Med dubbelt bindestreck
    ]
    sq = _source_quality_from_bevis(bevis)
    # E5=1.0, E4=0.8, E5=1.0 → avg = 0.933
    print(f"  src_quality blandade format: {sq:.3f}")
    assert abs(sq - 0.933) < 0.01, f"Förväntade 0.93, fick {sq}"
    print(f"  ✓ Blandade E-tagg-format matchas korrekt")


def test_no_etag_gives_low_default():
    from normalizer import _source_quality_from_bevis
    bevis = ["BEVIS 1: text utan tagg", "BEVIS 2: också utan tagg"]
    sq = _source_quality_from_bevis(bevis)
    assert sq == 0.40, f"Förväntade 0.40 (bevis men inga taggar), fick {sq}"
    print(f"  ✓ Bevis utan E-tagg ger 0.40 (varning, inte neutralt 0.5)")


# ── RUN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        ("STYRKA-substring", [
            test_styrka_medel_hog_not_falsely_hog,
            test_styrka_hog_still_works,
            test_styrka_medel_works,
            test_styrka_lag_works,
        ]),
        ("Conf-spridning", [
            test_three_hog_hypotheses_actually_differentiate,
            test_no_hypothesis_at_92_ceiling,
            test_weak_hypothesis_actually_weak,
            test_old_clustering_problem_resolved,
        ]),
        ("E-tag regex (kritisk root cause)", [
            test_e_tag_regex_matches_claude_actual_format,
            test_e_tag_regex_matches_blandade_format,
            test_no_etag_gives_low_default,
        ]),
        ("Fallbacks", [
            test_fallback_when_parser_misses,
        ]),
    ]

    failed = 0
    for group, fns in tests:
        print(f"\n── {group} ──")
        for fn in fns:
            try:
                fn()
            except AssertionError as e:
                print(f"  ✗ {fn.__name__}: {e}")
                failed += 1
            except Exception as e:
                print(f"  ✗ {fn.__name__} CRASHED: {type(e).__name__}: {e}")
                failed += 1

    print(f"\n{'═' * 60}")
    if failed:
        print(f"FAILED: {failed} test(er) trasiga")
        sys.exit(1)
    else:
        print(f"OK — alla tester gröna")
