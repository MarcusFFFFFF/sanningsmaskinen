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

from dotenv import load_dotenv
load_dotenv(override=True)

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
H2[INRIKESPOLITIK]: inrikespolitik, koalitioner, valintressen (Allison/Putnam)
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
    f"AKTUALITETSPRIORITET: Sök ALLTID efter nyheter från de senaste 24 timmarna (idag: {TODAY}). "
    "Börja med det SENASTE som hänt — inte bakgrundshistorik. "
    "Prioritera Reuters, AP News, Bloomberg, BBC, Al Jazeera som primärkällor. "
    "Källdatum MÅSTE anges i länktexten: [Reuters, 23 mars 2026](url). "
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


def _log_usage(step: str, model: str, response) -> None:
    """
    Logga token-användning från API-svar. Hanterar både Anthropic
    (input_tokens, cache_creation_input_tokens, cache_read_input_tokens,
    output_tokens) och OpenAI (prompt_tokens, completion_tokens, total_tokens).
    Skrivs till stdout med [usage]-prefix så Railway-loggen kan grep:as.
    """
    try:
        u = getattr(response, "usage", None)
        if u is None:
            return
        parts = [f"step={step}", f"model={model}"]
        for attr in (
            "input_tokens", "output_tokens",
            "cache_creation_input_tokens", "cache_read_input_tokens",
            "prompt_tokens", "completion_tokens", "total_tokens",
        ):
            v = getattr(u, attr, None)
            if v is not None:
                parts.append(f"{attr}={v}")
        server_tools = getattr(u, "server_tool_use", None)
        if server_tools:
            web_searches = getattr(server_tools, "web_search_requests", None)
            if web_searches is not None:
                parts.append(f"web_searches={web_searches}")
        print("[usage] " + " ".join(parts), flush=True)
    except Exception as e:
        print(f"[usage] step={step} log_error={type(e).__name__}: {e}", flush=True)


def openai_with_retry(model, max_tokens, messages, max_retries=3, step="openai"):
    for attempt in range(max_retries):
        try:
            r = openai_client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages,
                timeout=60,
            )
            _log_usage(step, model, r)
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
        f"DAGENS DATUM: {TODAY} — sök SENASTE nyheterna, max 24 timmar gamla.\n"
        f"Prioritera: Reuters, AP News, Bloomberg, BBC, Al Jazeera, CNN, NYT, Guardian.\n"
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
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1200,
            system=(
                f"Du är ett faktaverifieringssystem. Datum: {TODAY}. Skriv på svenska. "
                f"VIKTIGT: Sök alltid efter de SENASTE nyheterna från de senaste 24 timmarna. "
                f"Prioritera primärkällor: Reuters, AP, Bloomberg, BBC, Al Jazeera. "
                f"Första raden MÅSTE vara exakt: "
                f"'ÖVERGRIPANDE STATUS: VERIFIED' (eller PARTIAL/UNVERIFIED/ONGOING/HYPOTHETICAL). "
                f"Använd webbsökning för att hitta de exakta artikel-URL:erna."
            ),
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
        )
        _log_usage("reality_check", "claude-sonnet-4-6", response)
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
    # Check UNVERIFIED first — "VERIFIED" is a substring of "UNVERIFIED"
    if "UNVERIFIED" in upper[:300] or "EJ BEKRÄFTAD" in upper[:300] or "EJ VERIFIERBAR" in upper[:300]:
        status, proceed = "UNVERIFIED", False
    elif "STATUS: VERIFIED" in upper or ("VERIFIED" in upper[:200] and "UNVERIFIED" not in upper[:200]):
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


def get_breaking_context(question: str, status: str) -> str:
    """
    För ONGOING/PARTIAL-frågor: sök aktivt efter militära deployeringar,
    deadlines och eskaleringar de senaste 6 timmarna.
    Returnerar en komprimerad kontext-sträng som injiceras i Claude-prompten.
    """
    if status not in ("ONGOING", "PARTIAL"):
        return ""

    # Bygg en riktad sökning baserad på nyckelord i frågan
    search_prompt = (
        f"Fråga: {question}\n"
        f"Datum: {TODAY}\n\n"
        f"Sök efter de SENASTE 6 timmarnas nyheter om denna fråga. "
        f"Fokusera specifikt på:\n"
        f"1. MILITÄRA DEPLOYERINGAR eller truppförflyttningar\n"
        f"2. ULTIMATUM, deadlines eller tidsramar som löper ut\n"
        f"3. ESKALERINGAR de senaste 12 timmarna\n"
        f"4. MARKNADSRÖRELSER (oljepris, börser) som reaktion på händelserna\n\n"
        f"Svar KORT — max 400 ord. Bara bekräftade fakta med källhänvisning. "
        f"Format:\n"
        f"BREAKING [tidpunkt]: [fakta] [Källa](url)\n"
        f"BREAKING [tidpunkt]: [fakta] [Källa](url)\n"
        f"Prioritera Reuters, AP, Bloomberg, BBC."
    )

    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}]
    try:
        r = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            system=(
                f"Du är ett nyhetsspanningssystem. Datum: {TODAY}. "
                f"Sök ALLTID efter nyheter från de senaste 6 timmarna. "
                f"Prioritera Reuters, AP, Bloomberg. Skriv på svenska. "
                f"Var extremt koncis — bara de mest akuta fakta."
            ),
            messages=[{"role": "user", "content": search_prompt}],
            tools=tools,
        )
        _log_usage("breaking_context", "claude-sonnet-4-6", r)
        result = "".join(
            b.text for b in r.content
            if hasattr(b, "type") and b.type == "text"
        ).strip()
        if result and len(result) > 50:
            return (
                f"\n\n⚡ BREAKING CONTEXT — SENASTE 6 TIMMARNA ({TODAY}):\n"
                f"{result}\n"
                f"INSTRUKTION: Integrera dessa breaking-fakta HÖGST UPP i din analys "
                f"under rubriken 'SENASTE TIMMARNAS HÄNDELSER'. "
                f"Nämn specifikt alla militära deployeringar, deadlines och eskaleringar."
            )
    except Exception:
        pass
    return ""


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
        "FEL:  [E4 — Der Spiegel, feb 2026]\n"
        f"\nAKTUALITET — KRITISKT: Datum idag är {TODAY}.\n"
        "Sök ALLTID efter nyheter från de senaste 24 timmarna.\n"
        "Prioritera Reuters, AP News, Bloomberg, BBC, Al Jazeera, CNN framför äldre källor.\n"
        "Om frågan gäller en pågående händelse: börja med det SENASTE som hänt idag.\n"
        "Ange alltid källans publiceringsdatum i länktexten: [E4 — Reuters, 23 mars 2026](url)"
    )

    # Fler sökningar för pågående händelser
    max_search = 8 if status in ("ONGOING", "PARTIAL") else 5
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": max_search}]

    # Hämta breaking context för pågående händelser
    breaking = get_breaking_context(question, status)

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=7000,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": question + rc_note + breaking}],
        tools=tools,
    )
    _log_usage("ask_claude", "claude-opus-4-6", response)
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
        model="gpt-4o",
        max_tokens=900,
        messages=[
            {"role": "system", "content": (
                f"Du är en destruktiv kritiker av epistemisk analys. Datum: {TODAY}. "
                f"Var specifik — citera exakt vad du kritiserar. "
                f"Aldrig generell. Om du kritiserar linsbalansen, nämn vilken hypotes som fick fel behandling."
            )},
            {"role": "user", "content": safe_encode(prompt)}
        ],
        step="gpt_critic",
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
        _log_usage("analyze_conflicts", "claude-sonnet-4-6", r)
        return "".join(
            b.text for b in r.content
            if hasattr(b, "type") and b.type == "text"
        )
    except Exception as e:
        return f"[Konfliktanalys misslyckades: {e}]"


def run_red_team(question: str, claude_answer: str, conflict_report: str) -> tuple:
    structured = _extract_structured_summary(claude_answer)

    # Faktaankare: råa utdrag ur början och slutet av primäranalysen så Red Team
    # ser de aktuella aktörerna och datumen i sin ursprungliga prosa.
    head = claude_answer[:800]
    tail = claude_answer[-800:] if len(claude_answer) > 1600 else ""

    prompt = (
        f"RED TEAM. Datum: {TODAY}\n"
        f"FRÅGA: {question}\n\n"
        f"━━━ FAKTAANKARE — ENDA TILLÅTNA FAKTAKÄLLAN ━━━\n"
        f"PRIMÄRANALYS (öppning):\n{head}\n\n"
        f"PRIMÄRANALYS (slut):\n{tail}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"CLAUDE:S STRUKTURERADE HYPOTESER:\n{structured}\n\n"
        f"GPT-KRITIKERNS KONFLIKTKARTA:\n{conflict_report[:600]}\n\n"
        f"DITT UPPDRAG: Bygg en konkurrerande analys som slår ut Claude:s vinnande hypotes. "
        f"Använd ENDAST aktörsnamn, datum, presidenter och politiska beslut som finns "
        f"i FAKTAANKARET ovan. Hitta ALDRIG på information som inte står där.\n\n"
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
        model="gpt-4o",
        max_tokens=1200,
        messages=[
            {"role": "system", "content": (
                f"Du är Red Team-analytiker. Datum: {TODAY}. "
                f"Ditt jobb är att FALSIFIERA Claude:s slutsats — inte lista generella invändningar. "
                f"Bygg en fullständig konkurrerande modell med konkreta bevis. "
                f"Om du inte kan hitta starka motbevis, säg det — men försök hårt.\n\n"
                f"KRITISK FAKTAREGEL: Använd ALDRIG din egen träningsdata för att verifiera "
                f"fakta om aktuella händelser, presidenter, ledare eller politiska beslut. "
                f"Håll dig STRIKT till de fakta som finns i FAKTAANKARET i user-meddelandet. "
                f"Om primäranalysen säger att Trump är president 2026, så är Trump president — "
                f"din träningsdata är inte aktuell. Skriv på svenska."
            )},
            {"role": "user", "content": safe_encode(prompt)}
        ],
        step="red_team",
    )
    should_rewrite = any(x in result.upper() for x in ["KOLLAPSAR", "IFRÅGASATT", "UTMANAD", "MODIFIERAS"])
    return result, should_rewrite


def auto_rewrite(question: str, claude_answer: str, red_team_report: str) -> str:
    # Web search återinförs ENDAST när Red Team sa KOLLAPSAR — då behöver vi
    # bygga om från grunden med färsk fakta. MODIFIERAS räcker det att
    # omstrukturera utan ny sökning.
    is_collapsed = "KOLLAPSAR" in (red_team_report or "").upper()

    prompt = (
        f"Red Team: analys behöver revideras. Datum: {TODAY}\n"
        f"FRÅGA: {question}\n"
        f"ORIGINAL:\n{claude_answer[:2000]}\n"
        f"RED TEAM:\n{red_team_report[:800]}\n"
        f"Förbättra: kör tre linser om, degradera svaga påståenden [HYPOTES], "
        f"inkludera ALT-H1/H2/H3. Märk [REVIDERAD VERSION].\n"
        + (
            f"KOLLAPSAR — bygg om från grunden. Sök nya källor via web search "
            f"för att uppdatera fakta. Prioritera Reuters, AP, Bloomberg, BBC. "
            f"Format: [Källnamn, {TODAY}](https://url)"
            if is_collapsed else
            f"Behåll alla källänkar från originalet — sök inte nya källor, "
            f"omstrukturera baserat på Red Teams kritik."
        )
        + "\n\nFORMAT — KRITISKT: Börja DIREKT med analysen. "
        + "Skriv ALDRIG om din process, vad du planerar att söka, "
        + "vad du tänker göra eller hur du tolkar uppgiften. "
        + "Bara resultatet — som om du redan är klar med arbetet. "
        + "INGEN meta-text. INGEN inledning som 'Jag börjar med att...' eller "
        + "'Låt mig först söka...'. Hoppa rakt in i [REVIDERAD VERSION]-rubriken."
        + "\n\nKRITISK LÄNKREGEL: VARJE faktapåstående MÅSTE ha en klickbar "
        + "länk i format [Källnamn](https://url). Inga påståenden utan länk "
        + "är tillåtna. Om du inte har en URL, skriv inte påståendet."
    )
    kwargs = {
        "model": "claude-opus-4-6",
        "max_tokens": 3000,
        "system": [{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        "messages": [{"role": "user", "content": prompt}],
    }
    if is_collapsed:
        kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]

    try:
        r = anthropic_client.messages.create(**kwargs)
        _log_usage("auto_rewrite", "claude-opus-4-6", r)
        return "".join(
            b.text for b in r.content
            if hasattr(b, "type") and b.type == "text"
        )
    except Exception as e:
        return f"[Auto-rewrite misslyckades: {e}]"


def generate_article(question: str, final_analysis: str, ranked: list) -> str:
    """
    Generera en journalistisk artikel (300-400 ord) baserad på den reviderade analysen.
    Returnerar en publicerbar text med ingress, brödtext och avslutning.
    """
    if not final_analysis:
        return ""

    # Bygg hypotes-sammanfattning
    hyp_summary = ""
    if ranked:
        hyp_lines = []
        for h in ranked[:3]:
            pct = int(h.get("conf_pct", int(float(h.get("conf", 0.5)) * 100)))
            tes = h.get("tes", "")[:120]
            hyp_lines.append(f"- {h.get('key','')} [{h.get('label','')}] {pct}%: {tes}")
        hyp_summary = "\n".join(hyp_lines)

    prompt = (
        f"Du är en erfaren journalist på en kvalitetstidning. Skriv en journalistisk artikel "
        f"på 300-400 ord baserad på följande analys. Skriv på svenska.\n\n"
        f"FRÅGA SOM ANALYSERATS: {question}\n\n"
        f"ANALYSENS SLUTSATSER (hypoteser rankade efter evidensstyrka):\n{hyp_summary}\n\n"
        f"ANALYSTEXT (använd som faktaunderlag):\n{final_analysis[:2500]}\n\n"
        f"INSTRUKTIONER:\n"
        f"- Börja med en stark nyhetsingress (vad, vem, när, varför det spelar roll)\n"
        f"- Presentera det mest akuta/breaking i andra stycket\n"
        f"- Förklara de konkurrerande förklaringarna kortfattat i brödtexten\n"
        f"- Avsluta med vad som avgör hur situationen utvecklas\n"
        f"- Journalistisk ton: aktiv röst, konkreta fakta, inga akademiska termer\n"
        f"- Märk INTE ut hypoteser som H1/H2/H3 — skriv dem som naturlig analys\n"
        f"- Inkludera inte källhänvisningar i texten\n"
        f"- Skriv INTE rubriker eller mellanrubriker — bara löpande text\n"
        f"- Max 400 ord"
    )

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            system=f"Du är en erfaren grävjournalist. Datum: {TODAY}. Skriv klar, faktabaserad journalistik.",
            messages=[{"role": "user", "content": prompt}],
        )
        _log_usage("generate_article", "claude-sonnet-4-6", response)
        return "".join(
            b.text for b in response.content
            if hasattr(b, "type") and b.type == "text"
        ).strip()
    except Exception as e:
        return f"[Artikelgenerering misslyckades: {e}]"


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
        f"H2[INRIKESPOLITIK]: [tes] — Styrka:[HÖG/MEDEL/LÅG]\n"
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
        f"H2 INRIKESPOLITIK: kärntesen | 2 bevis[källa] | 1 motargument | falsifieringstest\n"
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

    # Generera journalistisk artikel baserad på slutprodukten
    article_source = result["final_analysis"] or result["claude_answer"]
    if article_source and len(article_source) > 200:
        result["article"] = generate_article(
            question,
            article_source,
            result.get("ranked", [])
        )
    else:
        result["article"] = ""

    return result
