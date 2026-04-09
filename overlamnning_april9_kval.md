# Överlämning — 9 april 2026, kvällen

Sessionsöverlämning efter en lång arbetsdag med Sanningsmaskinen. Allt commit:at och pushat till `main`. Working tree clean. Railway-deploy live på `eb0fe42` (eller senare om något pushats efter denna fil).

---

## Nuläge

**Plattform:** Flask + gunicorn på Railway (`sanningsmaskinen-production.up.railway.app`). 2 sync workers, `--timeout 600` (höjt från 300 idag).

**Frontend:** `static/index.html` enfilig vanilla JS + CSS. EventSource-baserad SSE för analys. Sidebar-historik med lösenordsskydd.

**Backend:** `server.py` (Flask) + `engine.py` (LLM-pipeline) + `normalizer.py` (parsing).

**Modeller efter dagens fixar:**
- `claude-opus-4-6` — `ask_claude`, `auto_rewrite`
- `claude-sonnet-4-6` — `event_reality_check`, `get_breaking_context`, `analyze_conflicts`, `generate_article` (flyttades från opus idag)
- `gpt-4o` — `ask_gpt_critic`, `run_red_team` (var gpt-4o-search-preview, hängde silent)

**Streamlit-versionen** (`app.py`) är pensionerad — visar nu en gul redirect-banner till Railway-deployen (commit `31f713f`). Behåller filen för att inte bryta gamla bokmärken/historik.

**Procfile:**
```
web: gunicorn server:app --timeout 600 --workers 2 --bind 0.0.0.0:$PORT
```

---

## Alla fixar idag — i commit-ordning

| Commit | Vad | Kategori |
|---|---|---|
| `63b24bc` | Wrappa `generate_article` i try/except, fallback till tom sträng | bug |
| `ebb0e04` | `renderRedTeamDetail` + regex-fel i `renderConflictReport` (multi-line regex literals var ogiltig JS) | bug |
| `31f713f` | Redirect-banner i Streamlit `app.py` | UX |
| `a4b8486` | Utökad `.gitignore` (data/, *.zip, screenshots, finder-duplikat, UPDATE UI/) | hygien |
| `eb673d5` | `CLAUDE.md` med arkitektur- och pipeline-guide | docs |
| `bb81999` | "Ej kontaktad"-status + affärsplan-sektion i `outreach.html` | feat |
| `1fbc161` | Migrera Anthropic SDK från `beta.messages.create` → stable `messages.create`, förenkla `get_breaking_context`, behåll UNVERIFIED-substring-guard | refactor |
| `327c340` | Ny startsida: hero "Tre förklaringar. En sanning.", exempelfrågor, fyra badges | feat |
| `0fe8951` | Tajta hero så startsidan ryms utan scroll på iPhone 390×700 | UX |
| `e73dd9b` | **Kritisk:** `gpt-4o-search-preview` → `gpt-4o` + `timeout=60` i `openai_with_retry`. Search-preview-modellen hängde silent på riktig Claude-input | bug |
| `cb87342` | H-kort `exp-evidence` line-clamp på hela ord (ersätter rå `slice(0,180)`) | UX |
| `3037bbf` | Stilren fallback i `renderConflictReport` vid engine-felmeddelanden | UX |
| `829034c` | Lösenordsskydd på `/history`-endpoints (env-var `HISTORY_PASSWORD`, default `sanningsmaskinen`) | feat |
| `3a99915` | Klickbara källchips i breaking, vad-vet-vi och gold-blocket. `extractVadVetVi`/`extractGoldBody` filtrerade tidigare bort BEVIS-rader | bug |
| `43d21c0` | Åäö i SSE-progress-labels och historik-knapp flyttad in i topbar | UX |
| `e32e176` | Ignorera `sanningsmaskinen_fix4_preview.html` | hygien |
| `09ebbe1` | **Kritisk:** H-kort tomma sedan första Flask-deployen — `parse_hypotheses` har aldrig funnits i `normalizer.py`. Fix: använd `normalize_claude_answer(text)["hypotheses"]` + `_ensure_three_hypotheses` | bug |
| `0bbe99f` | Logga outer-except + save_history-fel i `_stream_response` | obs |
| `17c3b52` | Anthropic prompt caching på `SYSTEM_PROMPT` (3587 tok cached) | perf |
| `78a1abc` | Ta bort web search i `auto_rewrite` — ask_claude har redan sökt | perf |
| `6a2fdaf` | Parallellisera `analyze_conflicts ‖ run_red_team` med ThreadPoolExecutor | perf |
| `a5d8629` | Gunicorn timeout 300 → 600 (säkerhetsnät) | ops |
| `eb0fe42` | `generate_article` opus → sonnet | perf |

**23 commits totalt.** Stora teman:
1. **Två kritiska tysta buggar:** `parse_hypotheses` ImportError (H-korten var tomma i 100% av analyserna sedan första deployen), `gpt-4o-search-preview` hängde tyst på riktiga inputs och triggade gunicorn worker timeout.
2. **Performance/kostnad:** prompt caching, parallellisering, modellnedflyttning, web search-cap.
3. **UX-fixar:** linkify chips, line-clamp, hero-design, åäö, lösenordsskydd.

---

## Kvarstående buggar och tekniska skulder

### Hög prioritet

- **`/analyze-bg` används inte alls.** Bakgrundsjobs-systemet är fullt byggt i `server.py:316–352` med SQLite, daemon-trådar och `/result/<job_id>`-polling. Frontend använder bara SSE. Att migrera till `/analyze-bg` skulle eliminera hela timeout-klassen av buggar permanent. **Kräver ~30 rader frontend-kod.**

- **Pipeline-tider 200–240s mot 600s gunicorn-gränsen.** Med dagens optimeringar är typisk analystid ~210s (mätt). Marginalen mot timeouten är 390s, vilket är OK för normalfall men inte hållbart för pathologiska queries. Lösning: migrera till `/analyze-bg`.

- **`ask_claude` är den dominerande kostnaden** (~150–180s av 210s, ~$0.24/anrop). Inte rörd idag. Nästa lever: sänk `max_uses` 7 → 5 för EVENT-frågor (sparar 20–50s), eller använd `extended_thinking` istället för upprepade web searches.

### Medel prioritet

- **Två deklarationer av `esc()`** i `static/index.html` (rad 873 + 878). Den andra shadowar den första via JS function hoisting. Funkar i praktiken (linkify-logiken körs) men förvirrande och felkänsligt vid framtida edits.

- **Frontend har dubbla error-handlers** på EventSource: `addEventListener('error', ...)` + `es.onerror = ...`. Båda triggas på samma fel och skriver över `result.innerHTML` — kan ge race där "Analysfel" visas istället för "Anslutningen bröts".

- **Inga payload-baserade integrationstest** för engine.py. Allt testat via lokala Python-snippets eller live mot produktion. Sårbart för regressioner.

- **`auto_rewrite` returnerar `[Auto-rewrite misslyckades: {e}]`** i frontend om Anthropic-anropet kraschar. Texten landar direkt i analysens reviderade version och blir användarsynlig.

### Låg prioritet

- **`favicon.ico` saknas** → `GET /favicon.ico 404` på varje sidladdning. Lägg till en 16×16 PNG eller `<link rel="icon" href="data:,">`.

- **~30 oanvända helpers i `app.py`** (Pylance-varningar): `_slugify`, `_build_pdf_v9`, `_is_english`, `_links_strip_html`, etc. Pensionerade tillsammans med Streamlit-vyn men ligger kvar.

- **Backup-filer** (`app_backup_*.py`, `app v8.17_backup.py`, `engine.py.bak87`, `normalizer_backup_*.py`, `pdf_export_backup_*.py`, etc) i repo-roten — gitignored men tar plats. Kan flyttas till en `archive/`-mapp eller raderas.

- **`outreach 2.html`, `app 2.py`** etc — Finder-duplikat. Gitignorerade, kan raderas.

### Säkerhet

- **OpenAI-nyckelrotation:** den nyckel som leakade i sessionskontexten tidigare (prefix `sk-proj-l7lf8ov5`) verifierades vara INTE den som sitter i lokal `.env` (där sitter `sk-proj-LVKw2d9K`). Du sa att Railway också har nya nyckeln. Verifiera att den **gamla nyckeln är revoked** på platform.openai.com → API Keys, annars är den fortfarande aktiv för vem som helst som sett sessionsloggarna.

- **`HISTORY_PASSWORD`** är hårdkodad default `sanningsmaskinen` i `server.py`. Sätt en starkare via Railway env-var i produktion. Pwd skickas dessutom som query-string vilket loggas av Railway/proxies — för seriöst skydd bör det migrera till `Authorization`-header med `secrets.compare_digest`.

---

## Kostnader per analys

Mätningarna nedan är gjorda med exakt tiktoken-räkning (cl100k_base) av varje prompt och är baserade på dessa antagande priser (verifiera mot din OpenAI/Anthropic-faktura — ±10–15% felmarginal):

- claude-opus-4-6: $5/MTok in, $25/MTok out
- claude-sonnet-4-6: $3/MTok in, $15/MTok out
- gpt-4o: $2.50/MTok in, $10/MTok out
- Anthropic web search: ~$0.01/sökning + ~1500 tok/sökning injection

| Steg | Modell | In tok | Out tok | $/anrop |
|---|---|---:|---:|---:|
| 1. event_reality_check | sonnet | 7 930 | 800 | $0.086 |
| 2a. get_breaking_context (ONGOING/PARTIAL) | sonnet | 6 281 | 500 | $0.066 |
| 2b. ask_claude | opus | 14 605 | 4 000 | $0.243 |
| 3. ask_gpt_critic | gpt-4o | 1 080 | 700 | $0.010 |
| 4. analyze_conflicts | sonnet | 2 391 | 700 | $0.028 |
| 5. run_red_team | gpt-4o | 1 254 | 1 000 | $0.013 |
| 6. auto_rewrite (utan web search efter idag) | opus | ~5 000 | 2 000 | ~$0.075 |
| 7. generate_article (sonnet efter idag) | sonnet | 1 326 | 600 | $0.013 |

**Worst case (allt triggat) idag:** ~$0.51 per analys
**Worst case före dagens perf-fixar:** ~$0.63 per analys
**Övre uppskattning inkl. web search injection-variance:** **~$0.70 per analys**

**Kostnadsdrivare:**
- `ask_claude` (39% av total) — Claude Opus + 5–8 web searches
- `auto_rewrite` (15%, när triggad) — andra Opus-passet
- Övriga steg är försumbara (<3% var)

**Daglig kostnad vid 100 analyser/dag:** ~$50–70/dag, ~$1500–2100/månad.

---

## Nästa steg

### Vad jag rekommenderar i ordning

1. **Migrera frontend till `/analyze-bg`.** Eliminerar timeout-klassen permanent, oberoende av hur långsam pipelinen blir. ~30 rader frontend-arbete: byt ut EventSource mot fetch + setInterval-polling, behåll progress-events via job_id i SQLite. **Egen fokuserad session värd att göra.**

2. **Verifiera att prompt caching faktiskt träffar.** Anthropic returnerar `cache_read_input_tokens` i response. Lägg till loggning i `ask_claude`/`auto_rewrite` som printar dessa siffror så vi vet att vi får 90% rabatt på system-prompten i andra anropet. Trivial change, hög insiktsvärde.

3. **Komprimera `SYSTEM_PROMPT`** från 3587 → ~1800 tokens. `SOURCE_STRATEGY` upprepar mycket av `SOURCE_HIERARCHY`. `EPISTEMIC_PRIORITY_INSTRUCTION` har dubblerade exempel. Sparar ~$0.018/analys efter caching och minskar latency på första (uncached) anropet.

4. **Cap web search i `ask_claude` 7 → 5** för EVENT-frågor. Sparar 20–50s + $0.029/analys. Risk: mindre källtäckning på komplexa frågor.

5. **Lägg till favicon** för att döda 404:orna. Micro-fix.

6. **Cleanup `app.py`** — radera oanvända helpers. Eller radera hela filen om Streamlit-versionen är permanent pensionerad.

7. **Ta bort den dubbla `esc()`-deklarationen** i `static/index.html`. Behåll bara linkify-versionen.

### Vad jag INTE rekommenderar än

- **Bumpa upp ask_claude max_tokens.** 7000 är redan högt. Snittutskrift är ~4000 tok.
- **Byta till async Flask/FastAPI.** För stort refactor utan tydlig vinst — `/analyze-bg` löser samma problem.
- **Komprimera prompt-templates i steg 3-5.** Sparar marginalt eftersom dessa redan är korta.

---

## Outreach-status

Outreach-CRM:t lever i `outreach.html` (statisk fil, ingen backend). Status idag efter `bb81999`:

- Ny status `Ej kontaktad` tillagd som filterbar option och CSS-badge (`badge-ejkontaktad`, grå).
- Affärsplan-sektion publicerad inline i CRM:t med rubriken "Affärsplan — Sanningsmaskinen (uppdaterad 27 mars 2026)". Innehåller övergripande mål, prissättningsantagande (ARPA 3000 kr/mån, konvertering cold→demo 8–12%, demo→betalande 15–20%) och tidiga kunder.

Den faktiska kontakt-listan, status-fördelningen och vilka leads som är öppna ligger inline i `outreach.html` JS-data. Kontrollera filen direkt eller öppna sidan i browsern för aktuellt tillstånd.

**Vad som saknas i outreach-flödet:**
- Ingen backend — alla ändringar måste editas direkt i HTML och commit:as.
- Ingen email-integration, ingen automatiserad uppföljning.
- Ingen koppling mellan outreach och Sanningsmaskinen själv (skulle kunna logga vilka prospects som testat tjänsten).

---

## Snabbreferens — viktiga filer

| Fil | Syfte |
|---|---|
| `server.py` | Flask backend, SSE-pipeline, history-endpoints, `/analyze-bg`-stubbar |
| `engine.py` | LLM-pipeline, alla API-anrop, SYSTEM_PROMPT |
| `normalizer.py` | Parsa Claude-output till strukturerade hypoteser, scoring |
| `static/index.html` | Hela frontend i en fil — CSS, markup, JS, render-funktioner |
| `outreach.html` | Statisk CRM för outreach-flöde |
| `Procfile` | Railway gunicorn-startup, timeout 600s |
| `CLAUDE.md` | Arkitekturguide skapad idag — läs först om du är ny |
| `requirements.txt` | Python deps, includes streamlit för bakåtkompat |

**Live-URL:** `https://sanningsmaskinen-production.up.railway.app`
**Repo:** `https://github.com/MarcusFFFFFF/sanningsmaskinen`
**Railway-projekt:** `focused-fascination`, service `sanningsmaskinen`, environment `production`

---

*Sessionen avslutad 2026-04-09 sen kväll. Working tree clean, alla 23 commits pushade till `main`.*
