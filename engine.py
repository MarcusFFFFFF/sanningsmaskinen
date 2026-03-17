# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN v8.18 — ENGINE
Ändringar från v8.15:
  - EPISTEMIC_PRIORITY_INSTRUCTION tillagd i SYSTEM_PROMPT
  - Mönster före enskilda påståenden
  - Dramatik-trigger: söker kontext vid högt laddade påståenden
  - Domslut behandlas som E5, aldrig tonas ned till anklagelse
  - Obekräftade påståenden placeras i mönstrets ram, aldrig isolerade i öppningen
"""

import os
import re
import time
from datetime import date
from anthropic import Anthropic
from openai import OpenAI


anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TODAY = date.today().strftime("%Y-%m-%d")


SOURCE_HIERARCHY = """KÄLLHIERARKI:

E5=Primärkälla direkt (officiellt dokument, lagtext, domstolsbeslut, myndighetsdata):
   SVERIGE:     SCB, Riksdagen (riksdagen.se), Valmyndigheten (val.se), Regeringen,
                Riksrevisionen, Domstolsverket, SKR (kommuner/regioner),
                Polismyndigheten, Åklagarmyndigheten, Brottsförebyggande rådet (BRÅ)
   EU:          EUR-Lex, EU-kommissionen, Europaparlamentet, EU-domstolen
   GLOBALT:     FN, Världsbanken, IMF, WHO, UNHCR, ICC, ICJ, Eurostat, SIPRI,
                Freedom House, Transparency International,
                Congress.gov, C-SPAN, CourtListener/PACER (USA-domstolar)

E4=Tier-1 journalistik — ENDAST gratisfria källor som länk, välj efter geografi:
   GLOBALT:     Reuters, AP, BBC, NYT (gratis art.), WaPo (gratis art.),
                Guardian, Al Jazeera, NPR, ProPublica, GIJN (gijn.org)
   SVERIGE:     SVT Nyheter (svt.se), SR/Ekot (sverigesradio.se), TT (via SVT/SR)
                OBS: DN och SvD har betalvägg — använd bara för analys/citat,
                länka aldrig till dem. Använd SVT/SR för nyhetslänkar.
   NORDEN:      Aftenposten + NTB (NO), Politiken + Ritzau (DK),
                Helsingin Sanomat + STT (FI), RÚV (IS)
   TYSKLAND:    ARD/Tagesschau, Der Spiegel, Zeit Online, FAZ
   FRANKRIKE:   Le Monde, France Info, Le Figaro
   SPANIEN:     El País, La Vanguardia
   ITALIEN:     La Repubblica, Corriere della Sera
   BENELUX:     NRC (NL), De Standaard (BE)
   ÖSTEUROPA:   Gazeta Wyborcza (PL), Index.hu (HU)
   RYSSLAND:    Meduza (exilmedia, Lettland), Moscow Times — RT=[STATSMEDIA]
   TURKIET:     Cumhuriyet, Bianet — TRT=[STATSMEDIA]
   MELLANÖSTERN: Haaretz (IL), Middle East Eye, Al-Monitor
   ASIEN:       South China Morning Post (HK), Caixin (CN-ekonomi),
                NHK World (JP), The Hindu (IN), The Dawn (PK)
   LATINAMERIKA: El Universal (MX), Folha de S.Paulo (BR), La Nación (AR)
   AFRIKA:      Daily Maverick (ZA), The East African (KE), Premium Times (NG)
   AUSTRALIEN:  ABC Australia

E3=Sekundäranalys: Wikipedia (ALLTID E3), think tanks, SOM-institutet,
   Novus/Verian/Sifo/Demoskop (opinionsmätningar — ange uppdragsgivare + datum),
   universitetsrapporter, IFAU, SNS, Riksrevisionsrapporter, DN/SvD opinion/analys
E2=Kommentar, oklar källa, aggregatorsajter, partiegna källor, The Local (expat-media)
E1=Spekulation, sociala medier, RT, statsmedia utan redaktionell frihet

REGLER:
- BETALVÄGG-REGEL: Länka ALDRIG till WSJ, FT, Bloomberg, Politico Premium,
  DN, SvD, The Local eller andra källor bakom betalvägg — användaren kan inte läsa dem.
  Använd alltid en gratis alternativkälla för länken, även om du citerar betalväggsartikeln.
- Wikipedia=E3, aldrig ensam. Para alltid med E4.
- Opinionsmätningar=E3, ange alltid uppdragsgivare och datum.
- Statsmedia (RT, CCTV, TRT, Al Arabiya)=märk [STATSMEDIA].
- Kina: ingen oberoende fastlandskälla — skriv "Ingen oberoende kinesisk källa tillgänglig."
- [IDEOLOGISK KÄLLA] FDD/Heritage/Gatestone/partiegna=märk explicit.
- HÖG=2+ oberoende E4-E5. MEDEL=E3+primärkälla. LÅG=E1-E2.
- Märk alltid: [FAKTA], [INFERENS] eller [DEBATTERAD TOLKNING]."""

THREE_LENSES = """TRE LINSER — IDENTISK STRUKTUR (viktig regel: lika djup för alla tre):

H1[STRUKTURELL]: system, resurser, maktbalans (Waltz/Mearsheimer)
H2[DOMESTIC POLITICS]: inrikespolitik, koalitioner, valintressen (Allison/Putnam)
H3[AKTÖRPSYKOLOGI]: ledarens världsbild, erfarenheter, analogier (Jervis)
Format per hypotes: TES | BEVIS1-3[E-nivå källa URL] | MOTARG1-2 | FALSIFIERINGSTEST | STYRKA[HÖG/MEDEL/LÅG]
RANKING efter att alla tre testats. Avgörande test: vad krävs för att nr2 slår nr1?"""

URL_INSTRUCTION = """
KRITISK LÄNKREGEL — OBLIGATORISK:
För varje BEVIS du anger MÅSTE du inkludera en klickbar länk i exakt detta format:
  [Källnamn](https://exakt-url-till-artikeln.com/artikel)

Exempel RÄTT:
  BEVIS 1: BGH fastslår ukrainskt ansvar. [E5 — BGH](https://www.bundesgerichtshof.de/SharedDocs/Pressemitteilungen/DE/2025/2025312.html)
  BEVIS 2: Der Spiegel namngav Zaluzhnyj. [E4 — Der Spiegel](https://www.spiegel.de/politik/ausland/nord-stream-a-dec2025.html)

Exempel FEL (aldrig göra):
  BEVIS 1: BGH fastslår ukrainskt ansvar. [E5 — primärkälla, BGH]
  BEVIS 2: Der Spiegel namngav Zaluzhnyj. [E4 — Der Spiegel, feb 2026]

Om du inte hittar exakt URL via websökning: skriv [URL ej tillgänglig] — gissa ALDRIG en URL.
Minst 3 av dina bevis totalt MÅSTE ha riktiga https://-länkar.
"""

SOURCE_STRATEGY = """
KÄLLSTRATEGI — ANPASSA EFTER FRÅGANS GEOGRAFI:

GRUNDREGEL: Sök alltid primärkällan direkt — inte Wikipedia eller aggregatorer.
BETALVÄGG-REGEL: Länka ALDRIG till källor bakom betalvägg (DN, SvD, WSJ, FT,
Bloomberg, The Local, Politico Premium). Hitta alltid en gratis länk — SVT/SR för
Sverige, Reuters/AP/BBC för internationellt.

SVENSKA/NORDISKA FRÅGOR:
  Valdata/statistik   → val.se, SCB (E5)
  Lagar/beslut        → riksdagen.se, regeringen.se (E5)
  Brottsutredningar   → polisen.se, aklagare.se, bra.se (E5)
  Statlig granskning  → riksrevisionen.se (E5)
  Kommuner/regioner   → skr.se (E4/E5)
  Nyheter             → svt.se, sverigesradio.se (E4) — sök ALLTID dessa FÖRST
  Opinionsmätningar   → Novus, Verian/SVT, Sifo/Kantar, Demoskop (E3)
  Forskning           → SOM-institutet, IFAU, SNS, svenska universitet (E3)
  Norge               → NTB/Aftenposten (E4), SSB (E5)
  Danmark             → Ritzau/Politiken (E4), Danmarks Statistik (E5)
  Finland             → STT/Helsingin Sanomat (E4), Tilastokeskus (E5)

USA-FRÅGOR:
  Lagstiftning        → Congress.gov, C-SPAN (E5)
  Domstolar           → CourtListener, PACER (E5)
  Nyheter             → Reuters, AP, NPR, Guardian (E4) — gratis och öppna
  Grävjournalistik    → ProPublica, GIJN/gijn.org, ICIJ (E4)

EUROPEISKA FRÅGOR:
  EU-beslut           → EUR-Lex, EU-kommissionen (E5)
  Tyskland            → ARD/Tagesschau, Spiegel (E4)
  Frankrike           → Le Monde, France Info (E4)
  Spanien             → El País (E4)
  Italien             → La Repubblica (E4)
  Ryssland            → Meduza, Moscow Times (E4) — aldrig RT
  Övriga              → landets public service (E4)

ASIEN/GLOBALT:
  Kina                → SCMP, Caixin — flagga avsaknad av oberoende källa
  Japan               → NHK World (E4)
  Indien              → The Hindu (E4)
  Mellanöstern        → Al Jazeera, Haaretz, Middle East Eye (E4)
  Afrika              → Daily Maverick, The East African (E4)
  Latinamerika        → El Universal, Folha de S.Paulo (E4)
  Internationellt     → FN, WHO, Världsbanken, SIPRI, ICC/ICJ (E5)

Motivera alltid källval: [E5 — SCB] / [E4 — SVT Nyheter] / [E3 — Novus/SVT mars 2026]
"""

EPISTEMIC_PRIORITY_INSTRUCTION = """
EPISTEMISK PRIORITERING — OBLIGATORISK:

Verktyget söker kontextuell sanning, inte dramatik.
Briefing svarar på: Vad vet vi?
Analys svarar på: Vad kan detta betyda?
Dessa två får aldrig blandas ihop.

REGEL 1 — MÖNSTER FÖRE ENSKILDA PÅSTÅENDEN
Öppna med det som är bekräftat (E4/E5) och strukturellt relevant.
Det bekräftade mönstret kring en aktör väger tyngre än ett enskilt dramatiskt påstående.
FEL: Öppna med obekräftad anklagelse isolerad.
RÄTT: Öppna med domslut + dokumenterat beteende + strukturellt undanhållande —
      det ger kontext åt allt annat och är journalistiskt starkare.

REGEL 2 — ESKALATION-TRIGGER: SÖK KONTEXT VID BEHOV
När ett påstående är sensationellt, reputationsskadande eller sexuellt/kriminellt laddat:
  1. Gör en extra sökning på aktörens bekräftade mönster INNAN du värderar påståendet
  2. Visa mönstret före påståendet
  3. Fråga: är det enskilda påståendet scoopet, eller är MÖNSTRET scoopet?
Mönstret är nästan alltid starkare — bättre belagt, svårare att avfärda.
Scoopet uppstår när man följer evidensen noggrant, inte när man lyfter det dramatiska.

REGEL 3 — DOMSLUT ÄR E5, ALDRIG ANKLAGELSE
Om en aktör har relevanta domslut — lyft dem explicit med domstol, år och vad domen gällde.
Tona ALDRIG ned ett domslut till "anklagelse" eller "påstående."
EXEMPEL: "X befanns skyldig för sexuellt övergrepp av federal jury 2023 [E5].
Detta är relevant kontext för bedömningen av övriga påståenden om samma aktör."

REGEL 4 — OBEKRÄFTADE PÅSTÅENDEN: RELEVANS ≠ SANNING
KRITISK DISTINKTION: Kontext kan höja analytisk relevans och prioritet — aldrig bevisstatus.
En obekräftad anklagelse förblir obekräftad även om aktören har ett bekräftat mönster.
Märk alltid explicit vad som är domslut, dokumenterat beteende respektive anklagelse.

Obekräftade påståenden får tas upp i ANALYSEN — aldrig i BRIEFINGEN — när:
  — aktören har bekräftat liknande mönster [höjer analytisk relevans, inte sanningsstatus]
  — märkt [ANKLAGELSE — EJ VERIFIERAD]
  — med förklaring: varför nämns detta och vilket bekräftat mönster relaterar det till
  — med explicit notering att kontexten inte förändrar anklagelsens bevisstatus

EXEMPEL RÄTT:
  "Katie Johnson-anklagelsen (1994, tillbakadragen 2016 efter hot) är obekräftad [E2].
  Den nämns här för att: (1) Carroll-domen [E5] bekräftar ett sexualbrottsmönster,
  (2) DOJ undanhåller aktivt Trump-relaterade filer, (3) anklagelsen gäller samma
  tidsperiod som Epstein-relationen. Kontexten höjer analytisk relevans —
  inte anklagelsens bevisstatus. [ANKLAGELSE — EJ VERIFIERAD]"
"""

SYSTEM_PROMPT = (
    f"Du är SANNINGSMASKINEN v8.18. Datum: {TODAY}. "
    "Alien-perspektiv: ingen lojalitet, börja med vad aktören GÖR inte vad den SÄGER. "
    "Websökning tillgänglig — använd max 4 sökningar. "
    "KÄLLCITAT: när du refererar en källa du sökt upp, skriv alltid [Källnamn](URL) "
    "med den faktiska URL:en från sökresultatet. Utan URL: skriv bara källnamn+datum. "
    "SKRIVSÄTT: Skriv som en välutbildad journalist — klara meningar, aktiv röst, "
    "undvik akademisk jargong. Varje påstående ska vara konkret och verifierbart. "
    + SOURCE_HIERARCHY + "\n"
    + THREE_LENSES + "\n"
    + URL_INSTRUCTION + "\n"
    + SOURCE_STRATEGY + "\n"
    + EPISTEMIC_PRIORITY_INSTRUCTION + "\n"
    "Sanningen favoriserar ingen sida."
)

ANALYTICAL_KEYWORDS = [
    "vad förklarar", "varför har", "hur påverkar", "vad är orsaken",
    "hur fungerar", "vad driver", "vilka faktorer", "hur kan vi förstå",
    "vad ligger bakom", "hur hänger", "är det ideologi", "är det geopolitik",
    "relation mellan", "historiskt mönster", "över tid", "sedan länge",
    "struktur", "systemet", "mekanismen bakom",
]

HYPOTHETICAL_KEYWORDS = [
    "tänk om", "vad skulle hända", "hypotetiskt",
    "kontrafaktiskt", "föreställ dig", "antag att",
]


def _classify_question(question: str) -> str:
    """Klassificerar frågan som EVENT / ANALYTICAL / HYPOTHETICAL."""
    q = question.lower().strip()

    if any(kw in q for kw in HYPOTHETICAL_KEYWORDS):
        return "HYPOTHETICAL"

    if q.startswith("om "):
        if any(x in q for x in ["vad skulle", "vad händer om", "hur skulle", "föreställ", "antag"]):
            return "HYPOTHETICAL"

    if any(kw in q for kw in ANALYTICAL_KEYWORDS):
        return "ANALYTICAL"

    return "EVENT"


def safe_encode(text: str) -> str:
    if isinstance(text, bytes):
        return text.decode("utf-8", errors="replace")
    return text


def openai_with_retry(model, max_tokens, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            r = openai_client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
            )
            parts = [
                c.message.content for c in r.choices
                if hasattr(c.message, "content") and c.message.content
            ]
            return safe_encode("\n".join(parts) if parts else "Inget svar.")
        except Exception as e:
            err = str(e).lower()
            if "rate" in err or "timeout" in err or "429" in err:
                time.sleep(2 ** attempt)
                if attempt == max_retries - 1:
                    return "Red Team kunde inte slutföra sin analys efter flera försök. Håll primärhypotesen men med lägre konfidens."
            else:
                return "Red Team API-fel. Primäranalysen gäller men är ogranskat av moteld."
    return "Red Team: okänt fel. Primäranalysen gäller."


def event_reality_check(question: str) -> dict:
    q_type = _classify_question(question)

    if q_type == "ANALYTICAL":
        return {
            "status": "ANALYTICAL",
            "question_type": "ANALYTICAL",
            "text": (
                "[ANALYTISK FRÅGA — inget specifikt event att reality-checka]\n"
                "Frågan analyserar ett strukturellt mönster eller långsiktig relation. "
                "Fortsätter direkt till primäranalys."
            ),
            "proceed": True
        }

    if q_type == "HYPOTHETICAL":
        return {
            "status": "HYPOTHETICAL",
            "question_type": "HYPOTHETICAL",
            "text": (
                "[HYPOTETISK FRÅGA — kontrafaktiskt scenario]\n"
                "Frågan bygger på en påhittad eller kontrafaktisk premiss. "
                "Analys körs men alla slutsatser märks [HYPOTETISKT]."
            ),
            "proceed": True
        }

    prompt = (
        f"Verifiera kärnpåståendena i denna fråga med websökning.\n"
        f"FRÅGA: {question}\n"
        f"Svara EXAKT med dessa rader:\n"
        f"ÖVERGRIPANDE STATUS: VERIFIED\n"
        f"(eller PARTIAL, UNVERIFIED, ONGOING, HYPOTHETICAL)\n"
        f"CLAIM 1: [påstående] | Status: [BEKRÄFTAD/EJ BEKRÄFTAD] | "
        f"Källa: [Namn Datum](URL) [E-nivå]\n"
        f"CLAIM 2: [samma format]\n"
        f"CLAIM 3: [samma format]\n"
        f"BESLUT: FORTSÄTT | Motivering: [en mening]\n\n"
        f"KRITISK URL-REGEL: För varje Källa MÅSTE du ange den exakta direktlänken "
        f"till själva artikeln eller dokumentet — aldrig bara domänen eller en kategorisida.\n"
        f"Om du inte hittar exakt artikel-URL i sökresultatet: skriv [URL ej hittad] — gissa aldrig en URL."
    )
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}]

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=(
                f"Du är ett faktaverifieringssystem. Datum: {TODAY}. Skriv på svenska. "
                f"Första raden MÅSTE vara exakt: "
                f"'ÖVERGRIPANDE STATUS: VERIFIED' (eller PARTIAL/UNVERIFIED/ONGOING/HYPOTHETICAL). "
                f"Använd webbsökning för att hitta de exakta artikel-URL:erna."
            ),
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
        )
        text = "".join(
            b.text for b in response.content
            if hasattr(b, "type") and b.type == "text"
        )
    except Exception as e:
        return {
            "status": "ERROR",
            "question_type": "EVENT",
            "text": f"Reality check kraschade: {e}",
            "proceed": False,
        }

    upper = text.upper()
    status, proceed = "UNVERIFIED", False
    if "STATUS: VERIFIED" in upper or "VERIFIED" in upper[:200]:
        status, proceed = "VERIFIED", True
    elif "STATUS: ONGOING" in upper or "ONGOING" in upper[:200]:
        status, proceed = "ONGOING", True
    elif "STATUS: PARTIAL" in upper or "PARTIAL" in upper[:200]:
        status, proceed = "PARTIAL", True
    elif "STATUS: HYPOTHETICAL" in upper or "HYPOTHETICAL" in upper[:200]:
        status, proceed = "HYPOTHETICAL", True

    if status == "UNVERIFIED" and ("E4" in text or "E5" in text):
        if "EJ BEKRÄFTAD" not in upper and "UNVERIFIED" not in upper[:100]:
            status, proceed = "PARTIAL", True

    return {
        "status": status,
        "question_type": "EVENT",
        "text": text,
        "proceed": proceed,
    }


def ask_claude(question: str, reality_check: dict) -> str:
    q_type = reality_check.get("question_type", "EVENT")
    status = reality_check["status"]

    rc_note = f"\nREALITY CHECK STATUS: {status} | TYP: {q_type}"
    if q_type == "HYPOTHETICAL" or status == "HYPOTHETICAL":
        rc_note += "\n[Kör som HYPOTETISKT — märk alla slutsatser [HYPOTETISKT]]"
    elif status == "ONGOING":
        rc_note += "\n[Pågående händelse — märk tidskänsliga påståenden [PÅGÅENDE]]"
    elif q_type == "ANALYTICAL":
        rc_note += "\n[Strukturell fråga — fokusera på mönster och mekanismer, inte enskild händelse]"

    rc_note += """

JOURNALISTISK STRUKTUR — OBLIGATORISK:
Börja med det bekräftade mönstret — vad aktören GÖR, inte vad de SÄGER.
Börja INTE med biografi, bakgrund eller obekräftade anklagelser isolerade.

Tänk som en erfaren grävjournalist:
- Vad är bekräftat och strukturellt relevant JUST NU?
- Vilket mönster framträder när man ser de bekräftade fakta tillsammans?
- Vad försöker makten dölja — och vad visar deras HANDLINGAR (inte ord)?

KÄLLREGEL — INGA PAYWALLS:
Prioritera alltid: Reuters.com, AP News, BBC, Al Jazeera, The Guardian,
officiella dokument (gov, parliament, un.org, europarl.eu).
"""

    rc_note += (
        "\nKRITISK PÅMINNELSE — OBLIGATORISKA LÄNKAR:\n"
        "Varje BEVIS MÅSTE ha en klickbar länk: [Källnamn](https://url-till-artikeln.com)\n"
        "Använd websökning för att hitta exakta artikel-URLs.\n"
        "Minst 4 bevis totalt MÅSTE ha riktiga https://-länkar.\n"
        "RÄTT: [E4 — Der Spiegel](https://www.spiegel.de/politik/artikel-123.html)\n"
        "FEL:  [E4 — Der Spiegel, feb 2026]"
    )

    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}]
    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": question + rc_note}],
        tools=tools,
    )
    return "".join(
        b.text for b in response.content
        if hasattr(b, "type") and b.type == "text"
    )


def _extract_structured_summary(claude_answer: str) -> str:
    lines = claude_answer.split('\n')
    summary_parts = []

    styrka_lines = [l.strip() for l in lines if 'STYRKA' in l.upper() or 'HÖG' in l or 'MEDEL' in l]
    if styrka_lines:
        summary_parts.append("RANKING:\n" + '\n'.join(styrka_lines[:6]))

    h_sections = []
    current_h = None
    for line in lines:
        if re.match(r'##?\s*H[123]', line) or re.match(r'H[123]\s*[\[—\-]', line):
            current_h = line.strip()
        elif current_h and ('TES:' in line or '**TES' in line):
            h_sections.append(f"{current_h}: {line.strip()[:150]}")
            current_h = None
    if h_sections:
        summary_parts.append("HYPOTESER:\n" + '\n'.join(h_sections))

    falsif = [l.strip() for l in lines if 'FALSIFIERING' in l.upper()]
    if falsif:
        summary_parts.append("FALSIFIERINGSTESTER:\n" + '\n'.join(falsif[:3]))

    for line in lines:
        if any(k in line.upper() for k in ['VINNANDE', 'SLUTSATS', 'PRIMÄR', 'KOMBINAT']):
            summary_parts.append(f"SLUTSATS: {line.strip()[:200]}")
            break

    motarg = [l.strip() for l in lines if 'MOTARG' in l.upper()]
    if motarg:
        summary_parts.append("MOTARGUMENT (urval):\n" + '\n'.join(motarg[:4]))

    structured = '\n\n'.join(summary_parts)

    if len(structured) < 200:
        half = 1000
        structured = (
            claude_answer[:half] +
            "\n[...]\n" +
            claude_answer[-half:]
        )

    return structured[:2000]


def ask_gpt_critic(question: str, claude_answer: str, reality_status: str) -> str:
    structured = _extract_structured_summary(claude_answer)

    prompt = (
        f"Du är en destruktiv kritiker. OPPONERA mot analysen nedan — sammanfatta inte.\n"
        f"Datum: {TODAY} | Status: {reality_status}\n"
        f"FRÅGA: {question}\n"
        f"CLAUDES STRUKTURERADE ANALYS:\n{structured}\n\n"
        f"VIKTIGT: Svara BASERAT PÅ vad som faktiskt står ovan.\n"
        f"Om en hypotes rankas som HÖG — kritisera varför den rankningen kan vara FEL.\n"
        f"Om en hypotes rankas som MEDEL/LÅG — argumentera för att den borde vara högre.\n"
        f"Leverera EXAKT dessa punkter:\n"
        f"FIX1-PREMISS: Accepterades premissen korrekt? [OK / PROBLEM: beskriv]\n"
        f"FIX2-LINSBALANS: Fick H1/H2/H3 identisk struktur och rättvis behandling? "
        f"[OK / PROBLEM: vilken fick för mycket/lite]\n"
        f"FIX3-KÄLLDISCIPLIN: Extraordinära motivpåståenden utan 2×E4-stöd? "
        f"[OK / PROBLEM: konkret exempel från texten ovan]\n"
        f"FIX4-RANKING: Är rankingen (H1/H2/H3 STYRKA) motiverad av bevisen? "
        f"[OK / PROBLEM: citera den rad du ifrågasätter]\n"
        f"SVAGASTE_LED: Det enskilda påstående som om det är fel fäller mest\n"
        f"ALT-H: Den starkaste alternativhypotes som INTE testades i texten ovan\n"
        f"DOM: En skarp mening — håller analysen eller inte, och varför?"
    )
    return openai_with_retry(
        model="gpt-4o-search-preview",
        max_tokens=900,
        messages=[
            {"role": "system", "content": (
                f"Du är en destruktiv kritiker av epistemisk analys. Datum: {TODAY}. "
                f"Var specifik — citera exakt vad du kritiserar. "
                f"Aldrig generell. Om du kritiserar linsbalansen, nämn vilken hypotes som fick fel behandling."
            )},
            {"role": "user", "content": safe_encode(prompt)}
        ]
    )


def analyze_conflicts(claude_answer: str, gpt_answer: str) -> str:
    prompt = (
        f"Identifiera GENUINA meningsskiljaktigheter mellan Claude och GPT-kritikern.\n"
        f"CLAUDES ANALYS (urval):\n{claude_answer[:1500]}\n\n"
        f"GPT-KRITIKERNS SVAR:\n{gpt_answer[:800]}\n\n"
        f"Lista EXAKT tre konflikter:\n"
        f"KONFLIKT 1: [vad de är oense om] | Claude: [position] | GPT: [position] | "
        f"Avgörande: [vad som skulle lösa konflikten]\n"
        f"KONFLIKT 2: [samma format]\n"
        f"KONFLIKT 3: [samma format]\n"
        f"SAMSTÄMMIGHET: [vad de faktiskt är överens om — max 2 meningar]"
    )
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 1}]
    try:
        r = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            system=f"Du är konfliktanalytiker. Datum: {TODAY}. Skriv på svenska. Var specifik.",
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
        )
        return "".join(
            b.text for b in r.content
            if hasattr(b, "type") and b.type == "text"
        )
    except Exception as e:
        return f"[Konfliktanalys misslyckades: {e}]"


def run_red_team(question: str, claude_answer: str, conflict_report: str) -> tuple:
    structured = _extract_structured_summary(claude_answer)

    prompt = (
        f"RED TEAM. Ditt uppdrag: BYGG en fullständig konkurrerande analys som slår ut "
        f"Claude:s vinnande hypotes. Datum: {TODAY}\n"
        f"FRÅGA: {question}\n"
        f"CLAUDE:S ANALYS (strukturerad):\n{structured}\n"
        f"KONFLIKTER: {conflict_report[:400]}\n\n"
        f"STEG 1 — T1-PREMISS: Finns felaktiga eller obekräftade faktapåståenden? "
        f"[Citera exakt, ange varför det är tveksamt]\n"
        f"STEG 2 — KONKURRERANDE MODELL: Bygg en fullständig alternativ förklaring "
        f"som INTE är Claude:s vinnare. Ge den:\n"
        f"  ALT-TES: [en mening — vad är den alternativa huvudförklaringen?]\n"
        f"  ALT-BEVIS1: [starkaste beviset för alternativet]\n"
        f"  ALT-BEVIS2: [näststarkaste]\n"
        f"  ALT-BEVIS3: [tredje]\n"
        f"  VARFÖR CLAUDE HAR FEL: [vad i Claude:s analys ignorerar eller underskattar detta alternativ?]\n"
        f"STEG 3 — T3-KÄLLKRITIK: Vilka av Claude:s bevis är svagast belagda? "
        f"[Specificera E-nivå och varför det inte räcker]\n"
        f"STEG 4 — T4-CLAIM CASCADE: Om svagaste påståendet i Claude:s vinnarhypotes "
        f"visar sig vara fel — vad kollapsar?\n"
        f"VERDICT: [HÅLLER / MODIFIERAS / KOLLAPSAR] + en mening varför\n"
        f"ALTERNATIV RANKING: Om din modell är korrekt, hur borde H1/H2/H3 rankas?"
    )
    result = openai_with_retry(
        model="gpt-4o-search-preview",
        max_tokens=1200,
        messages=[
            {"role": "system", "content": (
                f"Du är Red Team-analytiker. Datum: {TODAY}. "
                f"Ditt jobb är att FALSIFIERA Claude:s slutsats — inte lista generella invändningar. "
                f"Bygg en fullständig konkurrerande modell med konkreta bevis. "
                f"Om du inte kan hitta starka motbevis, säg det — men försök hårt."
            )},
            {"role": "user", "content": safe_encode(prompt)}
        ]
    )
    should_rewrite = any(x in result.upper() for x in ["KOLLAPSAR", "IFRÅGASATT", "UTMANAD", "MODIFIERAS"])
    return result, should_rewrite


def auto_rewrite(question: str, claude_answer: str, red_team_report: str) -> str:
    prompt = (
        f"Red Team: analys behöver revideras. Datum: {TODAY}\n"
        f"FRÅGA: {question}\n"
        f"ORIGINAL:\n{claude_answer[:2000]}\n"
        f"RED TEAM:\n{red_team_report[:800]}\n"
        f"Förbättra: kör tre linser om, degradera svaga påståenden [HYPOTES], "
        f"inkludera ALT-H1/H2/H3. Märk [REVIDERAD VERSION].\n"
        f"VIKTIGT: Behåll alla källänkar från originalet och lägg till nya där möjligt. "
        f"Format: [Källnamn](https://url)"
    )
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}]
    try:
        r = anthropic_client.messages.create(
            model="claude-opus-4-6",
            max_tokens=3000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            tools=tools
        )
        return "".join(
            b.text for b in r.content
            if hasattr(b, "type") and b.type == "text"
        )
    except Exception as e:
        return f"[Auto-rewrite misslyckades: {e}]"


def assess_depth_recommendation(result: dict) -> dict:
    red_team = result.get("red_team_report", "").upper()
    conflict = result.get("conflict_report", "").upper()
    collapsed = result.get("collapsed", False)
    degraded = result.get("degraded", False)
    q_type = result.get("reality_check", {}).get("question_type", "EVENT")
    claude_len = len(result.get("claude_answer", ""))

    if collapsed or degraded:
        return {
            "layers_recommended": True,
            "deep_recommended": True,
            "reason": (
                "🔴 Red Team bedömde KOLLAPSAR/MODIFIERAS — analysen har reviderats. "
                "Layer 1-5 hjälper dig navigera skillnaderna. "
                "Fördjupning 3 visar vad som faktiskt förändrades."
            ),
            "level": "red"
        }

    if "HÖG" in conflict and "KONFLIKT" in conflict:
        return {
            "layers_recommended": True,
            "deep_recommended": True,
            "reason": (
                "🔴 Hög konflikt mellan Claude och GPT-kritikern. "
                "Fördjupning 2 ger dig de tre linserna i detalj "
                "och hjälper dig avgöra vilken hypotes som håller bäst."
            ),
            "level": "red"
        }

    if q_type == "ANALYTICAL":
        return {
            "layers_recommended": True,
            "deep_recommended": False,
            "reason": (
                "🟡 Analytisk strukturfråga med lång tidshorisont. "
                "Layer 1-5 destillerar analysen till journalistiskt format. "
                "Fördjupning 1 (Systemet bakåt i tiden) rekommenderas vid behov."
            ),
            "level": "yellow"
        }

    if claude_len > 3000:
        return {
            "layers_recommended": True,
            "deep_recommended": False,
            "reason": (
                "🟡 Primäranalysen är omfattande. "
                "Layer 1-5 ger dig en navigerbar struktur. "
                "Fördjupningar är tillgängliga vid behov."
            ),
            "level": "yellow"
        }

    return {
        "layers_recommended": False,
        "deep_recommended": False,
        "reason": (
            "🟢 Analysen är kortfattad och entydig. "
            "Råanalysen ovan räcker troligen — Layer 1-5 är tillgänglig vid behov."
        ),
        "level": "green"
    }


def deliver_ground_layers(question, claude_answer, gpt_answer,
                          red_team_report, final_analysis, reality_check) -> str:
    analysis = final_analysis if final_analysis else claude_answer
    status = reality_check["status"]

    banners = {
        "VERIFIED":     "✓ [VERIFIERAD HÄNDELSE]",
        "ONGOING":      "⟳ [PÅGÅENDE HÄNDELSE — fakta uppdateras]",
        "PARTIAL":      "◑ [DELVIS VERIFIERAD]",
        "ANALYTICAL":   "◈ [ANALYTISK FRÅGA — strukturellt mönster]",
        "HYPOTHETICAL": "◇ [HYPOTETISKT SCENARIO]",
    }
    banner = banners.get(status, "○ [EJ VERIFIERAD]")

    prompt = (
        f"Destillera analysen till fem lager. Datum: {TODAY} | {banner}\n"
        f"FRÅGA: {question}\n"
        f"ANALYS:\n{analysis[:2500]}\n"
        f"RED TEAM:\n{red_team_report[:400]}\n\n"
        f"Leverera EXAKT dessa sektioner:\n"
        f"LAYER 1 — DÖRREN\n"
        f"{banner}\n"
        f"[2-3 meningar: kärnan, offentligt narrativ ifrågasatt, frågan ingen ställer]\n"
        f"LAYER 2 — KARTAN\n"
        f"VAD VI VET SÄKERT [FAKTA]\n"
        f"1. [faktum][källa+URL][E-nivå][HÖG]\n"
        f"2. [faktum][källa+URL][E-nivå][HÖG]\n"
        f"3. [faktum][källa+URL][E-nivå][HÖG]\n"
        f"VAD SOM ÄR OSÄKERT [INFERENS/DEBATTERAD TOLKNING]\n"
        f"1. [fråga/inferens][LÅG]\n"
        f"2. [fråga/inferens][LÅG]\n"
        f"FRÅGAN INGEN STÄLLER: [strukturell fråga]\n"
        f"LAYER 3 — TRE HYPOTESER\n"
        f"H1[STRUKTURELL]: [tes] — Styrka:[HÖG/MEDEL/LÅG]\n"
        f"H2[DOMESTIC POLITICS]: [tes] — Styrka:[HÖG/MEDEL/LÅG]\n"
        f"H3[AKTÖRPSYKOLOGI]: [tes] — Styrka:[HÖG/MEDEL/LÅG]\n"
        f"VINNANDE: [vilken+varför] | TEST: [vad krävs för att nr2 slår nr1]\n"
        f"LAYER 4 — AKTÖRERNA\n"
        f"[Per aktör: SÄGER | FRUKTAR | STRUKTURELLT INTRESSE. Max 2 meningar.]\n"
        f"LAYER 5 — DIN MAKT\n"
        f"TRE FRÅGOR TILL VILKEN POLITIKER SOM HELST\n"
        f"1. [avslöjar strukturell förståelse]\n"
        f"2. [avslöjar domestic politics]\n"
        f"3. [avslöjar ärlighet om osäkerhet]\n"
        f"SÅ HÄR KÄNNER DU IGEN MANIPULATION: [2 konkreta mönster]"
    )

    try:
        r = anthropic_client.messages.create(
            model="claude-opus-4-6",
            max_tokens=3000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return "".join(
            b.text for b in r.content
            if hasattr(b, "type") and b.type == "text"
        )
    except Exception as e:
        return f"[Layer 1-5 misslyckades: {e}]"


def _split_deep_sections(combined: str) -> tuple:
    markers = [
        r"FÖRDJUPNING\s*1",
        r"FÖRDJUPNING\s*2",
        r"FÖRDJUPNING\s*3",
    ]
    positions = []
    for marker in markers:
        m = re.search(marker, combined, re.IGNORECASE)
        positions.append(m.start() if m else None)

    if all(p is not None for p in positions):
        p1, p2, p3 = positions
        return combined[p1:p2].strip(), combined[p2:p3].strip(), combined[p3:].strip()

    found = [(i, p) for i, p in enumerate(positions) if p is not None]
    if len(found) >= 2:
        parts = []
        for idx in range(len(found)):
            start = found[idx][1]
            end = found[idx + 1][1] if idx + 1 < len(found) else len(combined)
            parts.append(combined[start:end].strip())
        while len(parts) < 3:
            parts.append(parts[-1])
        return parts[0], parts[1], parts[2]

    n = len(combined)
    third = n // 3
    return combined[:third].strip(), combined[third:2*third].strip(), combined[2*third:].strip()


def deliver_deep_dives(question, claude_answer, gpt_answer,
                       red_team_report, final_analysis, reality_check) -> dict:
    analysis = final_analysis if final_analysis else claude_answer

    prompt = (
        f"Tre fördjupningar. Datum: {TODAY} | FRÅGA: {question}\n"
        f"ANALYS:\n{analysis[:2000]}\n"
        f"GPT:\n{gpt_answer[:600]}\n"
        f"RED TEAM:\n{red_team_report[:400]}\n\n"
        f"FÖRDJUPNING 1 — SYSTEMET BAKÅT I TIDEN\n"
        f"HUR UPPSTOD SYSTEMET? [Max 4 meningar, claim-level med källhänvisning]\n"
        f"PREJUDIKAT: [2-3 historiska paralleller: land/år | narrativ | mekanism | utfall]\n"
        f"SIFFROR: [3 siffror | vad det betyder | E-nivå källa URL]\n"
        f"FÖRDJUPNING 2 — TRE LINSER I DETALJ\n"
        f"H1 STRUKTURELL: kärntesen | 2 bevis[källa] | 1 motargument | falsifieringstest\n"
        f"H2 DOMESTIC: kärntesen | 2 bevis[källa] | 1 motargument | falsifieringstest\n"
        f"H3 PSYKOLOGI: kärntesen | 2 bevis[källa] | 1 motargument | falsifieringstest\n"
        f"KÄLLKVALITETSAUDIT: [E3 märkt som E5? Saknade tier-1? Inferens som fakta?]\n"
        f"FÖRDJUPNING 3 — FULLSTÄNDIG ANALYTIKER-OUTPUT\n"
        f"REALITY: [claim-för-claim: [FAKTA]/[INFERENS]/[DEBATTERAD TOLKNING]]\n"
        f"VINNANDE HYPOTES + MOTIVERING + FALSIFIERINGSTEST\n"
        f"RED TEAM SVAR: [hur analysen svarar på ALT-H1/H2/H3]\n"
        f"VAD FALSIFIERAR VINNANDE? [3 observationer]\n"
        f"KÄLLFÖRTECKNING: [Namn | Datum | E-nivå | URL | Vad den stöder]"
    )

    try:
        r = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        combined = "".join(
            b.text for b in r.content
            if hasattr(b, "type") and b.type == "text"
        )
    except Exception as e:
        combined = f"[Fördjupningar misslyckades: {e}]"

    deep1, deep2, deep3 = _split_deep_sections(combined)
    return {"deep1": deep1, "deep2": deep2, "deep3": deep3}


def run_full_pipeline(question: str, force_proceed: bool = False) -> dict:
    result = {
        "question": question,
        "reality_check": None,
        "claude_answer": "",
        "gpt_answer": "",
        "conflict_report": "",
        "red_team_report": "",
        "red_team_ok": False,
        "collapsed": False,
        "final_analysis": "",
        "layers": {},
        "degraded": False,
        "status": "RUNNING",
        "depth_recommendation": None,
    }

    rc = event_reality_check(question)
    result["reality_check"] = rc

    if not rc["proceed"] and not force_proceed:
        result["status"] = rc["status"]
        return result
    if not rc["proceed"] and force_proceed:
        rc["proceed"] = True

    result["claude_answer"] = ask_claude(question, rc)
    result["gpt_answer"] = ask_gpt_critic(question, result["claude_answer"], rc["status"])
    result["conflict_report"] = analyze_conflicts(result["claude_answer"], result["gpt_answer"])

    red_report, should_rewrite = run_red_team(
        question, result["claude_answer"], result["conflict_report"]
    )
    result["red_team_report"] = red_report
    result["collapsed"] = should_rewrite

    result["red_team_ok"] = bool(
        red_report
        and "misslyckades" not in red_report.lower()
        and "api-fel" not in red_report.lower()
        and len(red_report) > 100
    )
    result["degraded"] = not result["red_team_ok"]

    if should_rewrite and result["red_team_ok"]:
        result["final_analysis"] = auto_rewrite(
            question, result["claude_answer"], red_report
        )

    result["depth_recommendation"] = assess_depth_recommendation(result)

    result["status"] = "DEGRADERAD" if result["degraded"] else (
        "REVIDERAD" if result["final_analysis"] else "KLAR"
    )
    return result
