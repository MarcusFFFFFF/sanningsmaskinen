# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN v8.1
Systemisk Sanningsanalytiker med korsvalidering Claude + GPT-4

v8.1: FEM EPISTEMISKA SÄKERHETER + BUGFIXAR A-D (v7 + tre ChatGPT-kritikfixar)
  FIX 1 - CLAIM-BASERAD REALITY CHECK (steg 0)
           Varje kernpastående verifieras separat med E-niva + konfidens.
           Inte bara "ar handelsen verklig?" utan "vilka DELAR ar bekraftade?"
  FIX 2 - TRE LINSER MED TVINGAD LINJAL-STRUKTUR
           H1/H2/H3 far identisk mall: tes + 3 bevis + 2 motargument + falsifieringstest.
           Ingen hypotes far mer utrymme an de andra fore ranking.
  FIX 3 - KALLHIERARKI STRIKT + IDEOLOGISK KALLMARKNING
           FDD/Heritage/neokon think tanks: markas som [IDEOLOGISK KALLA - E3].
           Wikipedia = alltid E3. Think tank-rekommendation ≠ policy-bevis.
  FIX 4 - CLAIM-LEVEL TRACKING
           Varje pastående: PASTÅENDE -> BEVIS -> KONFIDENSPOANG.
           Om baspastående ar E2 degraderas beroende pastående automatiskt.
  FIX 5 - RED TEAM SOM BLOCKERANDE STEG
           Om Red Team failar: leveransen markeras DEGRADERAD.
           Systemet fortsatter aldrig tyst som om Red Team körde.
"""

import os
import time
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

import sys
from datetime import date
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client    = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TODAY = date.today().strftime("%Y-%m-%d")

# ===================================================================
# FIX 3 - KALLHIERARKI
# ===================================================================

SOURCE_HIERARCHY = """
KALLHIERARKI - STRIKT, TILLÄMPAS AUTOMATISKT

E5  Primärkälla: officiella dokument, deklassificerat, vittnesmål under ed,
    direktcitat från offentlig handling (lagtext, FN-resolution, presskonferens
    med namngiven tjänsteman + datum)
E4  Tier-1 journalistik: Reuters, AP, AFP, BBC, NYT, WaPo, Guardian,
    Le Monde, Der Spiegel, Al Jazeera English — med namn på reporter + datum
E3  Trovärdig sekundäranalys: Wikipedia (ALLTID E3, aldrig E5),
    think tanks (RAND, ICG, Chatham House), akademiska papers, SVT, SVD, DN
E2  Kommentar, enstaka källa, oklar ursprungskälla, alternativa medier

IDEOLOGISKA KALLOR — MARKERAS SEPARAT (oavsett E-niva):
[IDEOLOGISK KALLA] FDD (Foundation for Defense of Democracies) — neokonservativ,
    pro-Israel, förespråkar regimskifte i Iran. Rekommendationer är policy-advocacy,
    INTE bevis för faktiskt beslutsmotiv. Använd som indikator, aldrig som bevis.
[IDEOLOGISK KALLA] Heritage Foundation — konservativ, USA-exceptionalism.
[IDEOLOGISK KALLA] Gatestone Institute — höger-nationalistisk.
[IDEOLOGISK KALLA] Quincy Institute — antiinterventionistisk bias åt andra hållet.
REGEL: Think tank-rekommendation ≠ policy-bevis. Märk alltid: [REKOMMENDATION, EJ BESLUT]
E1  Spekulation, inferens utan källbelägg

AUTOMATISK DEGRADERING:
- Wikipedia = alltid E3, aldrig högre
- "Multipla källor" utan namn = E2
- Sociala medier = E1
- Om baspåstående är E2 eller lägre, märk beroende slutsatser:
  [DEGRADERAD — beroende av E2-källa]

CLAIM-LEVEL FORMAT (Fix 4):
Påstående [E-nivå] [-> Källnamn, datum] [KONFIDENSPOÄNG: HÖG/MEDEL/LÅG]

KONFIDENSPOÄNG:
HÖG  = E4-E5 + bekräftat av minst 2 oberoende källor
MEDEL = E3-E4 + en primärkälla
LÅG  = E1-E2 eller enstaka E3-källa
"""

# ===================================================================
# FIX 2 - TRE ANALYTISKA LINSER
# ===================================================================

THREE_LENSES = """
TRE ANALYTISKA LINSER - TVINGAD LINJAL-STRUKTUR (v8)

KRITISK REGEL: Alla tre hypoteser MÅSTE ha IDENTISK struktur och LIKA DJUP.
H1 far INTE mer utrymme, fler bevis eller starkare språk än H2 eller H3.
Det är ett metodfel att behandla en hypotes som "favorit" innan alla tre
har testats likvärdigt.

LINS 1 - STRUKTURELL / NEO-REALISTISK (Waltz, Mearsheimer)
Drivkraft: system, resurser, ekonomisk struktur, maktbalans.

LINS 2 - DOMESTIC POLITICS (Allison, Putnam)
Drivkraft: inrikespolitiska behov, koalitionslogik, valintressen,
byråkratiska aktörer som vann det interna argumentet.

LINS 3 - AKTORPSYKOLOGI / LEADER-DRIVEN (Jervis, Khong)
Drivkraft: individuell beslutsfattares världsbild, erfarenheter,
missuppfattningar, analogier.

OBLIGATORISKT FORMAT - IDENTISKT FÖR ALLA TRE:

H1 [STRUKTURELL]:
  TES: [en mening - vad förklarar denna lins?]
  BEVIS 1: [påstående] [E-nivå] [-> källa, datum] [konfidens]
  BEVIS 2: [påstående] [E-nivå] [-> källa, datum] [konfidens]
  BEVIS 3: [påstående] [E-nivå] [-> källa, datum] [konfidens]
  MOTARGUMENT 1: [starkaste invändningen mot H1]
  MOTARGUMENT 2: [näst starkaste invändningen]
  FALSIFIERINGSTEST: [vad måste observeras för att H1 ska förkastas?]
  STYRKA: [HÖG / MEDEL / LÅG] + en menings motivering

H2 [DOMESTIC POLITICS]:
  TES: [en mening]
  BEVIS 1-3: [samma format]
  MOTARGUMENT 1-2: [samma format]
  FALSIFIERINGSTEST: [specifikt]
  STYRKA: [HÖG / MEDEL / LÅG] + motivering

H3 [AKTORPSYKOLOGI]:
  TES: [en mening]
  BEVIS 1-3: [samma format]
  MOTARGUMENT 1-2: [samma format]
  FALSIFIERINGSTEST: [specifikt]
  STYRKA: [HÖG / MEDEL / LÅG] + motivering

RANKING (EFTER att alla tre testats):
  1. [vinnande hypotes] - förklarar mest med minst antaganden
  2. [andra plats] - förklarar [vad]
  3. [tredje plats] - förklarar [vad]
  Avgörande test för rangordningen: [vad krävs för att nr 2 slår nr 1?]

Om alla tre pekar åt samma håll: notera det och förklara varför det stärker.
Om de pekar åt olika håll: presentera spänningen explicit utan att lösa den.
"""

# ===================================================================
# STRUKTURELL PRIORITERINGSALGORITM
# ===================================================================

STRUCTURAL_ALGORITHM = """
STRUKTURELL PRIORITERINGSALGORITM

PRINCIPEN: Aktörers beteende över tid är mer informativt än deras
uttalade motiv vid ett enskilt tillfälle.

STEG 1 - NARRATIVIDENTIFIERING
Märk det offentliga narrativet: [OFFENTLIGT NARRATIV]
Tillhör det ett känt narrativmönster?

KÄNDA NARRATIVMÖNSTER:
  1900-1950  Civilisation/Ordning   Kolonial kontroll
  1950-1990  Kommunism/Frihet       Kalla kriget
  1973-nu    Petrodollar-försvar    Monetär hegemoni
  1990-2001  Humanitär/Demokrati   Post-Sovjet vakuum
  2001-nu    Terror/Kärnvapen       Juridisk handlingsfrihet
Narrativen roterar. Funktionen är konstant.

STEG 2 - FYRA STRUKTURELLA FAKTORER (HÖG/MEDEL/LÅG)
  F1: EKONOMISK AVVIKELSE - hotar dollarsystemet? nationaliserar?
      säljer resurser i konkurrerande valutor?
  F2: STRATEGISK POSITION - kontrollerar kritiska resurser, rutter?
  F3: OPERATIVT FÖNSTER - militärt försvagad? diplomatiskt isolerad?
  F4: SYSTEMSÅRBARHET - agerar från stabil dominans eller hotat
      systembevarandeläge? HÖG = sårbart system.

STEG 3 - PREJUDIKATTEST
Kärnvapen: Nordkorea (F1=LÅG) -> skyddas. Irak 2003 (F1=HÖG) -> invasion.
Humanitärt: Rwanda (F1=LÅG) -> ingen intervention. Libyen (F1=HÖG) -> intervention.

STEG 4 - PRIORITERINGSBESLUT
[Tas EFTER att tre linser testats]
F1+F2+F3 HÖG: strukturellt motiv primärt.
F1+F2+F3 LÅG: offentligt narrativ kan vara primärt.

STEG 5 - SYSTEMSÅRBARHETSKONTEXTEN (om F4=HÖG, obligatorisk)
Aktören agerar från hotat systembevarandeläge. Varje intervention
accelererar försvagningen av systemets legitimitet.
Historisk parallell: brittiska imperiet, Suez 1956.
"""

# ===================================================================
# SYSTEM PROMPT
# ===================================================================

SYSTEM_PROMPT = (
    "Du är SANNINGSMASKINEN v8.1 - ett analytiskt instrument som kartlägger "
    "maktens mekanismer over tid och rum (1400 till nutid).\n\n"
    "ALIEN-PERSPEKTIVET: Ingen nationell lojalitet. Ingen agenda. "
    "Du börjar aldrig med vad aktören säger - du börjar med vad "
    "aktören konsekvent gör.\n\n"
    "DU HAR TILLGÅNG TILL WEBSÖKNING - ANVÄND DEN:\n"
    "- Steg 0: verifiera att händelsen är verklig\n"
    "- Max 5 sökningar per analys\n"
    "- Ange alltid källa + datum\n\n"
    + SOURCE_HIERARCHY + "\n\n"
    + THREE_LENSES + "\n\n"
    + STRUCTURAL_ALGORITHM + "\n\n"
    "MÄNSKLIGA PRINCIPER\n"
    "1. Mänsklig kontinuitet - fokus skiftar naturligt.\n"
    "2. Tyst intelligens - byt läge utan kommentar.\n"
    "3. Pålitlighet - samma modell på alla frågor.\n\n"
    "KRISLAGRET: Flagga omedelbart vid suicidala tankar, självskada, våld.\n"
    "Svenska resurser: BRIS 116 111 | Mind 90101\n\n"
    "TEMPORAL CHECK - OBLIGATORISKT FÖRSTA STEG:\n"
    "Analysperiod | Datum | Status: HISTORISK/PÅGÅENDE/PROGNOS\n\n"
    "STANDARDUTGÅNG:\n"
    "## EVENT REALITY CHECK [FIX 1]\n"
    "## STRUKTURELL FÖRANALYS + TRE LINSER [FIX 2]\n"
    "## QUICK ANSWER\n"
    "## EXECUTIVE SUMMARY\n"
    "## KEY TAKEAWAYS [claim-level format]\n"
    "## BACKDROP DRIVERS\n"
    "## VOTE DRIVERS\n"
    "## MISSING VARIABLES\n"
    "## WHAT WE KNOW [E4-E5, claim-level]\n"
    "## WHAT WE SUSPECT [E1-E3, claim-level]\n"
    "## PROPAGANDAANALYS\n"
    "## RED TEAM SUMMARY\n"
    "## PATCH\n"
    "## SOURCES\n\n"
    "VERKTYGETS LÖFTE: Sanningen favoriserar ingen sida."
)

conversation_history = []


class Colors:
    CLAUDE  = "\033[94m"
    GPT     = "\033[92m"
    HEADER  = "\033[95m"
    WARNING = "\033[93m"
    RED     = "\033[91m"
    RESET   = "\033[0m"
    BOLD    = "\033[1m"


def print_header():
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("                                                              ")
    print("            SANNINGSMASKINEN v8.1                            ")
    print("            Fix 1: Claim-baserad reality check               ")
    print("            Fix 2: Linjal-hypotesstruktur                    ")
    print("            Fix 3: Strikt källhierarki + ideologisk märkning ")
    print("            Fix 4: Claim-level tracking                      ")
    print("            Fix 5: Red Team som blockerande steg             ")
    print("                                                              ")
    print(f"{Colors.RESET}")
    print(f"Kommandon: {Colors.BOLD}quit{Colors.RESET} avslutar | "
          f"{Colors.BOLD}rensa{Colors.RESET} rensar historik")


def safe_encode(text: str) -> str:
    if isinstance(text, bytes):
        return text.decode("utf-8", errors="replace")
    return text.encode("utf-8", errors="replace").decode("utf-8")


# ===================================================================
# FIX 1 - EVENT REALITY CHECK (steg 0)
# ===================================================================

def event_reality_check(question: str) -> dict:
    """
    FIX 1 v8: Claim-baserad verifiering.
    Varje kernpastående verifieras separat med egen E-niva och konfidenspoang.
    """
    prompt = (
        f"UPPGIFT: Claim-baserad faktaverifiering. Sok aktivt med websökning.\n\n"
        f"TIER-1-KALLOR (E4): Reuters, AP, AFP, BBC, NYT, Washington Post, Guardian, "
        f"Al Jazeera English, Le Monde, SVT, SVD, DN, officiella regeringsuttalanden.\n"
        f"Wikipedia = E3. Sociala medier = E1. Bloggar = E2.\n\n"
        f"FRAGA: {question}\n\n"
        f"Steg 1: Identifiera 4-6 kernpastående i fragan.\n"
        f"Steg 2: Verifiera varje pastående separat med websökning.\n"
        f"Steg 3: Satt status och konfidenspoang per pastående.\n\n"
        f"Leverera EXAKT:\n\n"
        f"CLAIM-BASERAD VERIFIERING\n"
        f"=========================\n"
        f"ÖVERGRIPANDE STATUS: [VERIFIED / PARTIAL / UNVERIFIED / ONGOING / HYPOTHETICAL]\n\n"
        f"KERNPASTÅENDE:\n"
        f"CLAIM 1: [pastående]\n"
        f"  Status: [BEKRAFTAD / EJ BEKRAFTAD / OMTVISTAD]\n"
        f"  Kalla: [Kallnamn | Datum] [E-niva]\n"
        f"  Konfidenspoang: [HOG / MEDEL / LAG]\n"
        f"  Notering: [ev. nyans]\n\n"
        f"CLAIM 2: [samma format]\n"
        f"(fortsatt for alla kernpastående)\n\n"
        f"BEKRAFTADE CLAIMS: [antal] av [totalt]\n"
        f"OMTVISTADE CLAIMS: [lista]\n"
        f"EJ VERIFIERA CLAIMS: [lista]\n\n"
        f"BESLUT: [FORTSATT SOM VERKLIGHET / FORTSATT SOM DELVIS VERIFIERAT / MARK SOM HYPOTETISKT]\n"
        f"Motivering: [en mening]"
    )

    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=3000,
        system=(
            f"Du ar ett strikt faktaverifieringssystem. Datum: {TODAY}. "
            "Verifiera varje kernpastående separat med tier-1-kallor. "
            "En claim ar BEKRAFTAD bara om minst tva oberoende tier-1-kallor bekraftar den. "
            "Skriv pa svenska. Engelska kallcitat i citattecken."
        ),
        messages=[{"role": "user", "content": prompt}],
        tools=tools
    )

    text = ""
    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            text += block.text

    upper = text.upper()
    status = "UNVERIFIED"
    proceed = False
    if any(x in upper for x in ["ÖVERGRIPANDE STATUS: VERIFIED", "ÖVERGRIPANDE STATUS: ONGOING",
                                  "VERGRIPANDE STATUS: VERIFIED", "VERGRIPANDE STATUS: ONGOING"]):
        status = "ONGOING"  # FIX B
        proceed = True
    elif any(x in upper for x in ["ÖVERGRIPANDE STATUS: PARTIAL", "VERGRIPANDE STATUS: PARTIAL"]):
        status = "PARTIAL"
        proceed = True
    elif any(x in upper for x in ["ÖVERGRIPANDE STATUS: HYPOTHETICAL", "VERGRIPANDE STATUS: HYPOTHETICAL"]):
        status = "HYPOTHETICAL"
        proceed = False

    return {"status": status, "text": text, "proceed": proceed}
def ask_claude(question: str, reality_check: dict) -> str:
    reality_context = (
        f"\n\nEVENT REALITY CHECK RESULTAT:\n{reality_check['text']}\n"
        f"STATUS: {reality_check['status']}\n"
    )

    if not reality_check["proceed"]:
        reality_context += (
            "\n[OBS: Händelsen OBEKRÄFTAD. Kör som HYPOTETISKT SCENARIO. "
            "Märk alla slutsatser [HYPOTETISKT].]\n"
        )

    full_question = question + reality_context
    conversation_history.append({"role": "user", "content": full_question})

    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}]

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8192,
        system=SYSTEM_PROMPT + f"\nDAGENS DATUM: {TODAY}.",
        messages=conversation_history,
        tools=tools
    )

    answer = ""
    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            answer += block.text

    conversation_history.append({"role": "assistant", "content": answer})
    return answer


# ===================================================================
# STEG 2 - GPT-4 KRITIKER
# ===================================================================

def ask_gpt_critic(question: str, claude_answer: str, reality_status: str) -> str:
    # Truncate to stay under 6000 TPM limit
    max_chars = 4000  # FIX D
    analysis_truncated = claude_answer[:max_chars] + ("…[trunkerad]" if len(claude_answer) > max_chars else "")

    prompt = f"""Du är en kritisk analytiker med websökning.
DATUM: {TODAY} | EVENT STATUS: {reality_status}
FRÅGA: {question}

CLAUDES ANALYS:
{analysis_truncated}

Granska specifikt de fyra fixes:

FIX 1 - PREMISSINTEGRITET:
Accepterade Claude händelsens premiss korrekt?
Vid UNVERIFIED - analyserade Claude ändå som om det vore verkligt?

FIX 2 - LINSBALANS:
Tre hypoteser presenterade med tre linser?
Dominerade strukturell/F1-F4 på bekostnad av domestic politics
och aktörpsykologi? Var alla tre lika djupt utarbetade?

FIX 3 - KÄLLDISCIPLIN:
Wikipedia använt som E5? (ska vara E3)
Blandas tier-1 och tier-2 i samma evidensnivå?

FIX 4 - CLAIM TRACKING:
Byggs slutsatser på svagt belagda påståenden utan degradering?
Följer centrala påståenden formatet:
  påstående [E-nivå] [källa, datum] [KONFIDENSPOÄNG]?

Leverera:
FIX 1-BEDÖMNING: [OK / PROBLEM + vad]
FIX 2-BEDÖMNING: [OK / PROBLEM + vilken lins dominerade]
FIX 3-BEDÖMNING: [OK / PROBLEM + felklassificerade källor]
FIX 4-BEDÖMNING: [OK / PROBLEM + påståenden som saknar tracking]

STRUKTURELL KRITIK: [håller F1-F4? alternativa förklaringar?]
FAKTAKOLL (tre påståenden): [påstående] -> [BEKRÄFTAD/KORRIGERAD/EJ VERIFIERBAR] + källa

ALT-HYPOTESER (Red Team-förberedelse):
ALT-H1 [DOMESTIC POLITICS]: [starkaste domestic politics-förklaring]
ALT-H2 [AKTORPSYKOLOGI]: [starkaste ledarpsykologi-förklaring]
ALT-H3 [GENUINT NARRATIV]: [starkaste försvar av officiellt narrativ]

RISK-MENINGAR:
[RISK 1] "..." -> [HYPOTES] "..." [VERIFY: ...]
[RISK 2] "..." -> [HYPOTES] "..." [VERIFY: ...]
[RISK 3] "..." -> [HYPOTES] "..." [VERIFY: ...]

KRITIKERNS SLUTSATS: [2-3 meningar]"""

    messages = [
        {"role": "system", "content": (
            f"Du är en kritisk analytiker. Datum: {TODAY}. "
            "Du kontrollerar fyra epistemiska säkerheter: "
            "premissintegritet, linsbalans, källdisciplin, claim tracking."
        )},
        {"role": "user", "content": safe_encode(prompt)}
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4o-search-preview",
        max_tokens=2048,
        messages=messages
    )

    parts = []
    for choice in response.choices:
        msg = choice.message
        if hasattr(msg, "content") and msg.content:
            parts.append(msg.content)
    return safe_encode("\n".join(parts) if parts else "Inget svar.")


# ===================================================================
# STEG 3 - KONFLIKTANALYS
# ===================================================================

def analyze_conflicts(claude_answer: str, gpt_answer: str) -> str:
    prompt = f"""Jämför analyserna. Identifiera genuina meningsskiljaktigheter.
Fokusera på: linsbalans, källdisciplin, hypotesval.

CLAUDES ANALYS: {claude_answer}
GPT KRITIK: {gpt_answer}

Format:
KONFLIKTANALYS
==============
KONFLIKT 1: [ämne]
Claude: [position] | GPT: [position]
Orsak: [epistemologisk skillnad] | Avgörande: [vad löser det]

KONFLIKT 2: [ämne]
[samma format]

SAMSTÄMMIGHET
=============
[3-5 punkter - särskilt om linsbalans och källkvalitet]

OSÄKERHETSNIVÅ: [HÖG/MEDEL/LÅG] + motivering"""

    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


# ===================================================================
# STEG 4 - RED TEAM (skärpt: tre linser + claim cascade)
# ===================================================================

def run_red_team(question: str, claude_answer: str, conflict_report: str) -> tuple:
    # Truncate inputs to stay under GPT-4o-search-preview 6000 TPM limit
    # Approximate: 1 token ~ 4 chars. Budget: ~4000 chars for variable inputs.
    max_analysis_chars = 2000
    max_conflict_chars = 800
    analysis_truncated = claude_answer[:max_analysis_chars] + ("…[trunkerad]" if len(claude_answer) > max_analysis_chars else "")
    conflict_truncated = conflict_report[:max_conflict_chars] + ("…[trunkerad]" if len(conflict_report) > max_conflict_chars else "")

    prompt = f"""Du är ett RED TEAM. FÖRSTÖR analysen.
DATUM: {TODAY}
FRÅGA: {question}
ANALYS (utdrag): {analysis_truncated}
KONFLIKTRAPPORT (utdrag): {conflict_truncated}

TEST 1 - PREMISSATTACK (Fix 1)
Är händelsens premiss korrekt? Centrala fakta som kan vara
felaktiga eller obekräftade?

TEST 2 - LINSATTACK (Fix 2)
Presentera starkaste möjliga version av tre alternativa hypoteser:

ALT-H1 [DOMESTIC POLITICS]:
Förklara händelsen UTAN strukturellt/ekonomiskt motiv.
Vad behövde beslutsfattaren hemma? Koalitionslogik?
Byråkratiska aktörer som vann? Konkret bevis.

ALT-H2 [AKTORPSYKOLOGI]:
Förklara händelsen som driven av individuell ledares världsbild.
Vad fruktar ledaren personligen? Historiska analogier?

ALT-H3 [GENUINT NARRATIV]:
Presentera starkaste försvaret av det officiella narrativet.
Kan kärnvapenhotet / terrorhotet faktiskt vara primärt?

TEST 3 - KÄLLKRITIK (Fix 3)
E4-E5-påståenden utan tier-1-belägg?
Wikipedia markerat som E5?

TEST 4 - CLAIM CASCADE (Fix 4)
Svagast belagda baspåstående - vad kollapsar om det är fel?

TEST 5 - MISSING VARIABLES
Teknologi, demografi, klimat, interna maktspel, slumpmässighet.

VERDICT: [HÅLLER / MODIFIERAS / KOLLAPSAR] + kortmotivering"""

    messages = [
        {"role": "system", "content": (
            f"Du är ett Red Team. Datum: {TODAY}. "
            "Försök bevisa att analysen är fel med tre alternativa "
            "hypoteser: domestic politics, aktörpsykologi, genuint narrativ."
        )},
        {"role": "user", "content": safe_encode(prompt)}
    ]

    response = openai_client.chat.completions.create(
        model="gpt-4o-search-preview",
        max_tokens=3000,
        messages=messages
    )

    parts = []
    for choice in response.choices:
        msg = choice.message
        if hasattr(msg, "content") and msg.content:
            parts.append(msg.content)

    report    = safe_encode("\n".join(parts) if parts else "Inget svar.")
    collapsed = "KOLLAPSAR" in report.upper()
    return report, collapsed


# ===================================================================
# STEG 5 - AUTO-REWRITE
# ===================================================================

def auto_rewrite(question: str, claude_answer: str, red_team_report: str) -> str:
    prompt = f"""Red Team bedömde KOLLAPSAR. Skriv om analysen.
DATUM: {TODAY}
FRÅGA: {question}
ORIGINAL: {claude_answer}
RED TEAM: {red_team_report}

Obligatoriska förbättringar:
1. Kör TRE LINSER på nytt - har domestic politics eller psykologi
   starkare förklaringskraft?
2. Degradera svagt belagda påståenden [HYPOTES] + [VERIFY]
3. Inkludera Red Teams tre ALT-hypoteser explicit
4. Wikipedia = E3, aldrig E5
5. Claim-level format på alla centrala påståenden

Märk: [REVIDERAD VERSION - efter Red Team KOLLAPSAR-verdict]"""

    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}]
    response = anthropic_client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8192,
        system=SYSTEM_PROMPT + f"\nDAGENS DATUM: {TODAY}.",
        messages=[{"role": "user", "content": prompt}],
        tools=tools
    )

    answer = ""
    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            answer += block.text
    return answer


# ===================================================================
# STEG 6 - LAGERUPPBYGGD SLUTLEVERANS
# ===================================================================

def deliver_layered_output(
    question, claude_answer, gpt_answer,
    red_team_report, final_analysis, reality_check
) -> dict:
    analysis = final_analysis if final_analysis else claude_answer
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}]

    if reality_check["status"] in ("VERIFIED", "ONGOING"):
        banner = "[VERIFIK AD HANDEL SE - tier-1-kallor bekraftade]"
    else:
        banner = "[OBEKRAFTAD HANDEL SE - analys som hypotetiskt scenario]"

    ground_prompt = f"""Destillera analysen till fem lager.
DATUM: {TODAY} | REALITY: {reality_check['status']} {banner}
FRÅGA: {question}
ANALYS: {analysis}
RED TEAM: {red_team_report}

Layer 1 ordning:
1. {banner} som första rad
2. Vad hände - ren fakta [E-nivå] [-> källa]
3. Offentligt narrativ [OFFENTLIGT NARRATIV] - ifrågasatt med prejudikat
4. Tre hypoteser kort (H1 strukturell, H2 domestic politics, H3 psykologi)
   + vilken vinner och varför
5. Om F4=HÖG: aktören agerar från sårbarhet
6. Frågan ingen ställer

Claim-level format: påstående [E-nivå] [-> Källnamn datum] [KONFIDENSPOÄNG]

Leverera EXAKT:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAYER 1 - DÖRREN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{banner}
[Fakta. Narrativ ifrågasatt. Tre hypoteser kort. Sårbarhet. Frågan ingen ställer.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAYER 2 - KARTAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VAD VI VET SÄKERT
1. [Faktum] [E4] [-> Källa datum] [HÖG]
2. [Faktum] [E4] [-> Källa datum] [HÖG]
3. [Faktum] [E4] [-> Källa datum] [HÖG]

VAD SOM ÄR OSÄKERT
1. [Öppen fråga] [E2] [LÅG]
2. [Öppen fråga] [E2] [LÅG]

FRÅGAN INGEN STÄLLER
[Den strukturella fråga som saknas i nyhetsflödet.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAYER 3 - SYSTEMET OCH MOTSTÅNDET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRE LINSER - KORT
H1 [STRUKTURELL]: [en mening] [styrka]
H2 [DOMESTIC POLITICS]: [en mening] [styrka]
H3 [AKTORPSYKOLOGI]: [en mening] [styrka]
Vinnande hypotes: [vilken + varför i en mening]

VILKET SYSTEM DRIVER DETTA? [Max 5 meningar.]
VARFÖR TAR UTMANARE RISKEN? [Max 4 meningar.]
VAD HÄNDER OM SYSTEMET KOLLAPSAR? [Bästa/värsta. Max 4 meningar.]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAYER 4 - AKTÖRERNA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[För varje aktör: vad de SÄGER [OFFENTLIGT NARRATIV] |
strukturellt intresse | domestic politics-dimension |
aktörpsykologi-dimension | vad de FRUKTAR mest.
Max 6 meningar. Berättelse.]

OANAD KOPPLING [en mening]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAYER 5 - DIN MAKT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRE FRÅGOR ATT STÄLLA VILKEN POLITIKER SOM HELST
1. [Avslöjar strukturell förståelse vs skydd]
2. [Avslöjar domestic politics-intressen]
3. [Avslöjar ärlighet om osäkerheten]

SÅ HÄR KÄNNER DU IGEN MANIPULATION
[2-3 konkreta retoriska mönster med exempel.]

DISKUSSIONSPREMISSER
1. [Strukturell tes] 2. [Domestic politics-tes] 3. [Systemsårbarhet-tes]"""

    deep1_prompt = f"""Fördjupa Layer 3 och 4. System bakåt i tiden.
DATUM: {TODAY} | REALITY: {reality_check['status']}
FRÅGA: {question} | ANALYS: {analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FÖRDJUPNING 1 - SYSTEMET BAKÅT I TIDEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HUR UPPSTOD SYSTEMET?
[Avgörande beslut, datum, vem vann, vem förlorade. Claim-level format. Max 6 meningar.]

PREJUDIKATEN - TRE LINSER PÅ HISTORIKEN
[Minst 3 paralleller. Format:
Land/år -> narrativ [OFFENTLIGT] -> strukturell mekanism ->
domestic politics-drivkraft -> utfall]

VARFÖR NARRATIVEN BYTTES UT
[Historisk rotationstidslinje. Max 5 meningar.]

SYSTEMETS LOGIK I SIFFROR
[4-5 siffror. Format: siffra -> vad det betyder -> [E-nivå] källa]

AKTÖRERNAS HISTORIA [Max 8 meningar.]"""

    deep2_prompt = f"""Tre linser i detalj. Källkvalitetsaudit.
DATUM: {TODAY} | REALITY: {reality_check['status']}
FRÅGA: {question}
CLAUDES ANALYS: {claude_answer}
GPT KRITIK: {gpt_answer}
RED TEAM: {red_team_report}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FÖRDJUPNING 2 - TRE LINSER I DETALJ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

H1 STRUKTURELL [detaljerad]
Kärntesen | 3 bevis med källbelägg | 2 motargument
Konfidenspoäng: [HÖG/MEDEL/LÅG] + motivering

H2 DOMESTIC POLITICS [detaljerad]
Kärntesen: [vad behövde beslutsfattaren hemma?]
3 bevis | 2 motargument | Konfidenspoäng

H3 AKTORPSYKOLOGI [detaljerad]
Kärntesen: [vad driver ledaren personligen?]
3 bevis | 2 motargument | Konfidenspoäng

HYPOTES-RANKING
[Rangordna tre. Motivera. Vad krävs för att nr 2 slår nr 1?]

KÄLLKVALITETSAUDIT
[Wikipedia-som-E5-fel? Saknade tier-1-belägg? Degraderade claim-kedjor?]

PROPAGANDAMÖNSTER [med konkreta exempel.]"""

    deep3_prompt = f"""Fullständig analytiker-output.
DATUM: {TODAY} | REALITY: {reality_check['status']}
FRÅGA: {question}
CLAUDES ANALYS: {claude_answer}
GPT KRITIK: {gpt_answer}
RED TEAM: {red_team_report}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FÖRDJUPNING 3 - FULLSTÄNDIG ANALYTIKER-OUTPUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FIX 1 - EVENT REALITY STATUS
[Tier-1-källor som bekräftade händelsen]

FIX 2 - TRE LINSER, FULLSTÄNDIG KÖRNING
H1 Strukturell: F1-F4 + narrativmönster + prejudikat [3+] + styrka
H2 Domestic politics: inrikespolitiskt behov + koalition + byråkrati + styrka
H3 Aktörpsykologi: världsbild + erfarenheter + analogier + styrka
Vinnande hypotes + motivering + falsifieringstest

FIX 3 - KÄLLKVALITETSAUDIT
[Varje E4-E5: källa + varför tier-1. Felklassificeringar.]

FIX 4 - CLAIM CASCADE-ANALYS
[Tre mest kritiska baspåståenden: E-nivå, källa, konfidenspoäng,
vad kollapsar om påståendet är fel?]

KONFLIKTANALYS CLAUDE VS GPT
[Ämne | Position A | Position B | Epistemologisk orsak | Avgörande]

RED TEAM SAMMANFATTNING
[ALT-H1, ALT-H2, ALT-H3 + hur analysen svarar]

MISSING VARIABLES

SCENARIOANALYS
A - Status quo | B - Eskalation | C - De-eskalation | D - Systemskifte
[D: det scenario som sällan analyseras men är mest strukturellt viktigt]

VAD FALSIFIERAR VINNANDE HYPOTES? [3-5 konkreta observationer]

KÄLLFÖRTECKNING [Namn | Datum | E-nivå | Vad den stöder]"""

    results = {}
    for key, prompt in [
        ("ground", ground_prompt),
        ("deep1",  deep1_prompt),
        ("deep2",  deep2_prompt),
        ("deep3",  deep3_prompt),
    ]:
        try:
            response = anthropic_client.messages.create(
                model="claude-opus-4-6",
                max_tokens=8192,
                system=SYSTEM_PROMPT + f"\nDAGENS DATUM: {TODAY}.",
                messages=[{"role": "user", "content": prompt}],
                tools=tools
            )
            text = ""
            for block in response.content:
                if hasattr(block, "type") and block.type == "text":
                    text += block.text
            results[key] = text
        except Exception as e:
            results[key] = f"[Fel: {e}]"
    return results


# ===================================================================
# UTILITIES + MAIN
# ===================================================================

def print_divider(char="─", width=60):
    print(f"{Colors.HEADER}{char * width}{Colors.RESET}")


def main():
    print_header()

    if not os.getenv("ANTHROPIC_API_KEY"):
        print(f"{Colors.WARNING}ANTHROPIC_API_KEY saknas{Colors.RESET}")
        sys.exit(1)
    if not os.getenv("OPENAI_API_KEY"):
        print(f"{Colors.WARNING}OPENAI_API_KEY saknas{Colors.RESET}")
        sys.exit(1)

    print(f"{Colors.BOLD}✓ API-nycklar laddade{Colors.RESET}")
    print(f"{Colors.BOLD}✓ Datum: {TODAY}{Colors.RESET}")
    print(f"{Colors.BOLD}✓ Fix 1: Claim-baserad reality check aktiv{Colors.RESET}")
    print(f"{Colors.BOLD}✓ Fix 2: Linjal-hypotesstruktur aktiv{Colors.RESET}")
    print(f"{Colors.BOLD}✓ Fix 3: Källhierarki + ideologisk märkning aktiv{Colors.RESET}")
    print(f"{Colors.BOLD}✓ Fix 4: Claim-level tracking aktiv{Colors.RESET}")
    print(f"{Colors.BOLD}✓ Fix 5: Red Team blockerande steg aktivt{Colors.RESET}\n")

    while True:
        try:
            question = input(f"{Colors.BOLD}Din fråga → {Colors.RESET}").strip()

            if not question:
                continue
            if question.lower() in ["quit", "exit", "avsluta"]:
                print("\nSanningsmaskinen stängs av.\n")
                break
            if question.lower() == "rensa":
                conversation_history.clear()
                print(f"{Colors.WARNING}Historik rensad.{Colors.RESET}\n")
                continue

            print(f"\n{Colors.BOLD}Analyserar...{Colors.RESET}\n")

            # STEG 0: Reality check
            print_divider("═")
            print(f"{Colors.WARNING}{Colors.BOLD}STEG 0 — EVENT REALITY CHECK{Colors.RESET}")
            print_divider("═")
            reality_check = {"status": "UNVERIFIED", "text": "", "proceed": True}
            try:
                reality_check = event_reality_check(question)
                print(f"{Colors.WARNING}{reality_check['text']}{Colors.RESET}")

                if not reality_check["proceed"]:
                    print(f"\n{Colors.RED}{Colors.BOLD}"
                          f"⚠ HÄNDELSEN KAN INTE VERIFIERAS{Colors.RESET}")
                    confirm = input(
                        f"{Colors.BOLD}Fortsätt som hypotetiskt scenario? (j/n) → {Colors.RESET}"
                    ).strip().lower()
                    if confirm != "j":
                        print("Analys avbruten.\n")
                        continue
                    reality_check["proceed"] = True
            except Exception as e:
                print(f"{Colors.WARNING}Reality check-fel: {e}{Colors.RESET}")

            # STEG 1: Claude
            print_divider()
            print(f"{Colors.CLAUDE}{Colors.BOLD}"
                  f"STEG 1 — CLAUDE PRIMÄRANALYS{Colors.RESET}")
            print_divider()
            claude_answer = ""
            try:
                claude_answer = ask_claude(question, reality_check)
                print(f"{Colors.CLAUDE}{claude_answer}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.WARNING}Claude-fel: {e}{Colors.RESET}")

            if not claude_answer:
                continue

            # STEG 2: GPT
            print(f"\n{Colors.BOLD}GPT-4 granskar alla fyra fixes...{Colors.RESET}\n")
            print_divider()
            print(f"{Colors.GPT}{Colors.BOLD}STEG 2 — GPT-4 KRITIKER{Colors.RESET}")
            print_divider()
            gpt_answer = ""
            try:
                gpt_answer = ask_gpt_critic(question, claude_answer, reality_check["status"])
                print(f"{Colors.GPT}{gpt_answer}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.WARNING}GPT-4-fel: {e}{Colors.RESET}")

            # STEG 3: Konflikt
            conflict_report = ""
            if claude_answer and gpt_answer:
                print_divider()
                print(f"{Colors.WARNING}{Colors.BOLD}STEG 3 — KONFLIKTANALYS{Colors.RESET}")
                print_divider()
                try:
                    conflict_report = analyze_conflicts(claude_answer, gpt_answer)
                    print(f"{Colors.WARNING}{conflict_report}{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.WARNING}Konfliktanalys-fel: {e}{Colors.RESET}")

            # STEG 4: Red Team — BLOCKERANDE STEG (v8)
            # Om Red Team failar: degraderad leverans, ingen tyst fortsättning.
            print_divider("═")
            print(f"{Colors.RED}{Colors.BOLD}STEG 4 — RED TEAM (blockerande){Colors.RESET}")
            print_divider("═")
            red_team_report = ""
            red_team_ok = False
            collapsed = False
            try:
                red_team_report, collapsed = run_red_team(
                    question, claude_answer, conflict_report
                )
                red_team_ok = bool(red_team_report and red_team_report != "Inget svar.")
                print(f"{Colors.RED}{red_team_report}{Colors.RESET}")
            except Exception as e:
                red_team_report = f"[RED TEAM MISSLYCKADES: {e}]"
                print(f"{Colors.RED}{Colors.BOLD}"
                      f"⚠ RED TEAM MISSLYCKADES: {e}{Colors.RESET}")

            # Varna om Red Team inte körde
            if not red_team_ok:
                print(f"\n{Colors.RED}{Colors.BOLD}"
                      f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                      f"⚠  DEGRADERAD LEVERANS — RED TEAM KÖRDE INTE\n"
                      f"   Slutleveransen saknar moteld. Alla hypoteser är OGranskade.\n"
                      f"   Lita inte på slutsatserna utan oberoende verifiering.\n"
                      f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                      f"{Colors.RESET}\n")

            # STEG 5: Auto-rewrite
            final_analysis = ""
            if collapsed and red_team_ok:
                print(f"\n{Colors.RED}{Colors.BOLD}"
                      f"⚠ KOLLAPSAR — startar auto-rewrite...{Colors.RESET}\n")
                print_divider("═")
                print(f"{Colors.CLAUDE}{Colors.BOLD}STEG 5 — REVIDERAD ANALYS{Colors.RESET}")
                print_divider("═")
                try:
                    final_analysis = auto_rewrite(question, claude_answer, red_team_report)
                    print(f"{Colors.CLAUDE}{final_analysis}{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.WARNING}Auto-rewrite-fel: {e}{Colors.RESET}")

            # STEG 6: Lager
            degraded_label = "" if red_team_ok else " ⚠ DEGRADERAD — RED TEAM EJ KÖRTS"
            print(f"\n{Colors.BOLD}Bygger slutleverans...{Colors.RESET}\n")
            try:
                layers = deliver_layered_output(
                    question, claude_answer, gpt_answer,
                    red_team_report, final_analysis, reality_check
                )
                print_divider("━")
                print(f"{Colors.HEADER}{Colors.BOLD}"
                      f"STEG 6 — SLUTLEVERANS{degraded_label}{Colors.RESET}")
                print_divider("━")

                if not red_team_ok:
                    print(f"{Colors.RED}[OBS: Denna leverans är degraderad — "
                          f"Red Team körde inte. Hypoteserna är ogranskat.]{Colors.RESET}\n")

                print(f"{Colors.HEADER}{layers.get('ground', '')}{Colors.RESET}")

                for label, key, color in [
                    ("FÖRDJUPNING 1 — DEN NYFIKNE MEDBORGAREN", "deep1", Colors.WARNING),
                    ("FÖRDJUPNING 2 — TRE LINSER I DETALJ",    "deep2", Colors.GPT),
                    ("FÖRDJUPNING 3 — ANALYTIKERN",             "deep3", Colors.CLAUDE),
                ]:
                    print(f"\n{Colors.HEADER}{'─' * 60}{Colors.RESET}")
                    print(f"{color}{Colors.BOLD}▶ {label}{Colors.RESET}")
                    print(f"{Colors.HEADER}{'─' * 60}{Colors.RESET}")
                    print(f"{color}{layers.get(key, '')}{Colors.RESET}")

            except Exception as e:
                print(f"{Colors.WARNING}Slutleverans-fel: {e}{Colors.RESET}")

            print_divider()
            if collapsed and red_team_ok:
                s = "REVIDERAD VERSION LEVERERAD"
                rw = "  → Auto-rewrite"
            elif not red_team_ok:
                s = "KLAR (DEGRADERAD)"
                rw = "  ⚠ Red Team misslyckades"
            else:
                s = "KLAR"
                rw = ""
            print(f"{Colors.HEADER}{Colors.BOLD}ANALYS {s}{Colors.RESET}")
            print(f"{Colors.HEADER}Reality check → Claude → GPT → Konflikt → "
                  f"Red Team{rw}  → 5 lager + 3 fördjupningar{Colors.RESET}")
            print_divider()
            print()

        except KeyboardInterrupt:
            print("\nSanningsmaskinen stängs av.\n")
            break
        except Exception as e:
            print(f"{Colors.WARNING}Oväntat fel: {e}{Colors.RESET}\n")


if __name__ == "__main__":
    main()