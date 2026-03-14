#!/bin/bash
# patch_engine.sh — applicera v8.7-ändringar på engine.py
# Kör: bash ~/Downloads/patch_engine.sh

ENGINE=~/Desktop/sanningsmaskinen/engine.py

echo "=== Sanningsmaskinen Engine Patch v8.7 ==="
echo "Patchar: $ENGINE"

# Säkerhetskopia
cp "$ENGINE" "${ENGINE}.bak87"
echo "✓ Backup: engine.py.bak87"

# 1. Red Team VERDICT-språk
sed -i '' 's/HÅLLER \/ MODIFIERAS \/ KOLLAPSAR/HÅLLER \/ UTMANAD \/ IFRÅGASATT/g' "$ENGINE"
echo "✓ VERDICT-språk uppdaterat (KOLLAPSAR → IFRÅGASATT)"

# 2. Return-check
sed -i '' 's/"KOLLAPSAR" in result.upper()/"IFRÅGASATT" in result.upper() or "UTMANAD" in result.upper()/g' "$ENGINE"
echo "✓ Return-logik uppdaterad"

# 3. auto_rewrite-prompt
sed -i '' 's/Red Team: KOLLAPSAR. Skriv om./Red Team ifrågasätter primärhypotesen. Skriv om./g' "$ENGINE"
echo "✓ auto_rewrite-prompt uppdaterad"

# 4. Klistra in generate_executive_summary före assess_depth_recommendation
# Hitta radnumret för def assess_depth_recommendation
LINE=$(grep -n "def assess_depth_recommendation" "$ENGINE" | cut -d: -f1)
echo "✓ Hittade assess_depth_recommendation på rad $LINE"

# Skapa summary-funktionen som tempfil
cat > /tmp/summary_func.py << 'FUNCEOF'

def generate_executive_summary(result: dict) -> str:
    """Executive Summary — Sonnet, ~$0.05/analys"""
    rc      = result.get("reality_check") or {}
    status  = result.get("status", "")
    q       = result.get("question", "")
    claude_short = (result.get("claude_answer") or "")[:1500]
    red_short    = (result.get("red_team_report") or "")[:600]
    final_short  = (result.get("final_analysis") or "")[:800]
    prompt = f"""Du är en analytisk redaktör. Skriv Executive Summary för journalister.

FRÅGA: {q}
REALITY STATUS: {rc.get('status', '')}
ANALYS-STATUS: {status}
CLAUDE (utdrag): {claude_short}
RED TEAM (utdrag): {red_short}
{"REVIDERAD (utdrag): " + final_short if final_short else ""}

Format — skriv EXAKT detta, inget annat:

SANNINGSMASKINEN — EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FRÅGA
{q}

REALITY CHECK
[En mening: bekräftat vs omtvistat]

TRE KONKURRERANDE FÖRKLARINGAR

H1 — [Hypotesnamn]: [En mening + STARK/MEDEL/SVAG]
H2 — [Hypotesnamn]: [En mening + STARK/MEDEL/SVAG]
H3 — [Hypotesnamn]: [En mening + STARK/MEDEL/SVAG]

MEST KONSISTENT MED EVIDENSEN
→ Primär: [en mening]
→ Sekundär: [en mening]
→ Kontext: [en mening]

EPISTEMISK OSÄKERHET
[En mening om vad som inte kan avgöras]

RED TEAM-UTMANING
[En mening om den alternativa modellen]

JOURNALISTISK REKOMMENDATION
[En mening: vad bör följas upp?]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sanningsmaskinen analyserar — den dömer inte.

Använd ALDRIG "HÖG säkerhet". Använd: "mest konsistent med evidensen", "plausibel", "omtvistad"."""

    resp = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text.strip()

FUNCEOF

# Infoga funktionen före assess_depth_recommendation
sed -i '' "${LINE}r /tmp/summary_func.py" "$ENGINE"
echo "✓ generate_executive_summary() infogad på rad $LINE"

# 5. Lägg till anrop i run_full_pipeline — efter red_team_ok-blocket
sed -i '' 's/result\["depth_recommendation"\] = assess_depth_recommendation(result)/result["executive_summary"] = generate_executive_summary(result)\n    result["depth_recommendation"] = assess_depth_recommendation(result)/' "$ENGINE"
echo "✓ executive_summary anrop tillagt i pipeline"

echo ""
echo "=== Patch klar! ==="
echo "Verifiera: grep -n 'executive_summary\|IFRÅGASATT\|generate_executive' ~/Desktop/sanningsmaskinen/engine.py"
