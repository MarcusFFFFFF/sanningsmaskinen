# Sanningsmaskinen — Patch v9 (13 maj 2026)

Tre saker patchade: ranking-formel, säkerhet, loggning.

---

## Ranking — den faktiska root cause

Efter att ha kört dina tre history-filer genom v1.5 (Anthropic, Iran/USA, Nord Stream) visade det sig att den största buggen INTE var formeln. Det var en regex.

### Den dolda buggen: E-taggar har aldrig matchats

`_source_quality_from_bevis` använde regexen `\[(E[1-5]|FAKTA)\]` — den krävde stängande `]` direkt efter siffran. Men Claude skriver bevisen som `[E3 — CSIS](url)`, INTE `[E3](url)`.

Verifierat i Iran-historikfilen: **0 av alla bevis i hela analysen matchade den gamla regexen.** Alla fick default-källkvalitet (0.5 i v1.4). Konsekvensen var att hela E1–E5-hierarkin — kärnan i Sanningsmaskinens metodologi — har varit dekorativ. Den påverkade conf-värdena med exakt 0 procent.

Detta är root cause för klusterproblemet: tre hypoteser med samma STYRKA + samma antal bevis + samma default-källkvalitet ⇒ identiska conf-värden. "78/78/58" och "67/58/58" är symptomatiskt för detta.

Fix: `\[(E[1-5]|FAKTA)\b` — `\b` (word boundary) matchar både `[E3]` och `[E3 — CSIS]`.

### Resultat på din verkliga data

| Fråga | v1.4 (deployad) | v1.5 (denna patch) |
|---|---|---|
| Anthropic | `tomt → frontend-fallback 85/55/25` | `85 / 83 / 55` |
| Iran/USA | `78 / 78 / 58` | `87 / 79 / 67` |
| Nord Stream | `67 / 58 / 58` | `69 / 67 / 65` |

Iran-frågans källkvalitet per hypotes efter fixen:
- H1 (STRUKTURELL): src=0.60 — svagare källor
- H2 (INRIKESPOLITIK): src=0.87 — starkare källor
- H3 (AKTÖRSPSYKOLOGI): src=0.80

E1–E5-graderingen fungerar för första gången i produktion.

### Övriga ranking-fix (sekundära men reella)

1. **STYRKA-substring**: `"HÖG" in "MEDEL-HÖG"` är `True` — MEDEL-HÖG felklassificerades som HÖG i båda parsningsstegen (rad 263, 343 i v1.4). Fix: testa längsta nyckel först.

2. **Conf-formeln omviktad**: STYRKA-vikt sänkt (0.50→0.45), bevisräkning höjd (0.20→0.25). STYRKA_VAL sänkt (HÖG 0.90→0.85). Clamp breddat 0.10–0.95 (var 0.15–0.92). Ger plats för differentiering.

3. **Källkvalitets-default**: 0.5 → 0.40 (bevis utan E-tagg, varning) eller 0.25 (inga bevis alls). Var symmetriskt neutralt vilket gjorde att hypoteser utan källor inte straffades.

### Diagnostiklogg

`normalize_result` skriver nu `[normalizer]`-rader till stdout vid varje run så ranking-pipelinen är inspekterbar utan att gräva i kod:

```
[normalizer] parsed_hypotheses=3/3 raw_len=12188
[normalizer]   H1 styrka=HÖG bevis_n=3 motarg_n=2
[normalizer]   H2 styrka=HÖG bevis_n=3 motarg_n=2
[normalizer]   H3 styrka=MEDEL bevis_n=3 motarg_n=2
[normalizer] ranked=[('H1', 'HÖG', 87, False), ('H2', 'HÖG', 79, False), ('H3', 'MEDEL', 67, False)]
```

---

## Säkerhet

### Path traversal på `/history/<filename>` (server.py rad 419 v1.4)

Gammal kod:
```python
filename = unquote(filename)
path = os.path.join(_BASE, "history", filename)
```

Ingen sanering — `filename = "../../.env"` resolveras till projektroot. Fix: kopierar valideringen från `/pdf`-endpointen.

### `HISTORY_PASSWORD` default `"sanningsmaskinen"` i klartext

Gammalt: `os.environ.get("HISTORY_PASSWORD", "sanningsmaskinen")`. Om miljövariabeln inte sätts var hela arkivet öppet med trivialt lösenord.

Nytt: ingen default. Om `HISTORY_PASSWORD` inte är satt genereras `secrets.token_urlsafe(24)` per server-start och loggas. Sätt variabeln i Railway env-vars, annars roterar lösenordet vid varje deploy.

### Lösenord via Authorization-header istället för URL-parameter

`?pwd=...` i URL loggas i Railway-access-logs och i webbläsarens history. Bakåtkompat behålls (loggar varning), men nya integrationer ska använda `Authorization: Bearer <pwd>` eller `X-Auth-Token: <pwd>`.

Frontend-uppdatering krävs för att helt eliminera URL-parametern. Just nu funkar gamla `?pwd=`-anrop men loggar varning.

### Rate limiting

`/analyze-stream` (GET + POST) och `/analyze-bg` har nu `10 per minute; 50 per hour` per IP. Default-limit `200 per hour; 30 per minute` för övriga endpoints.

Kräver `pip install flask-limiter`. Om paketet saknas startar servern fortfarande med varning + obegränsade endpoints (utvecklingsläge).

---

## Brister (loggning)

Tre tysta `except Exception:`-block byttes till loggande varianter:
- `_run_pipeline` article generation (rad 180)
- `_stream_response` article generation (rad 313)
- `admin_page` normalizer-anrop (rad 555)

Nu skrivs `[generate_article error]` resp. `[normalizer error]` till stdout med exception-typ och meddelande. Tidigare swäljdes fel tyst → buggar var osynliga.

---

## Test-suite

`test_normalizer.py` täcker:
- STYRKA-substring (4 tester: HÖG, MEDEL-HÖG, MEDEL, LÅG)
- Conf-spridning (4 tester: differentiering, max-tak, min-svag, typisk fördelning)
- **E-tag regex (3 tester) — kritisk regression-skydd för den dolda buggen**
- Fallback-mekanismen

Kör: `python3 test_normalizer.py`. Lägg i CI när du har CI.

---

## Deploy

```bash
# 1. Backup
cd ~/Desktop/sanningsmaskinen
cp normalizer.py normalizer.py.bak_pre_v9
cp server.py server.py.bak_pre_v9

# 2. Drop in nya filer
cp ~/Downloads/normalizer.py .
cp ~/Downloads/server.py .

# 3. Installera flask-limiter (om inte redan)
source venv/bin/activate
pip install flask-limiter

# 4. Lägg till HISTORY_PASSWORD i Railway env-vars
#    (annars genereras tillfälligt lösenord per deploy)

# 5. Kör test
python3 test_normalizer.py

# 6. Lokalt test innan deploy
python3 server.py  # port 5001
# Öppna http://localhost:5001 och kör en fråga.
# Titta i terminalen efter [normalizer]-rader — verifiera att
# parsed_hypotheses=3/3 och att conf-värdena differentieras.

# 7. git push railway main
```

---

## Vad detta säger om produkten

Den dolda regex-buggen betyder att E1–E5-hierarkin har varit reklam, inte funktion, sedan v1.0. Conf-värdena har de facto beräknats som `0.50 × STYRKA + 0.20 × bevisräkning + 0.30 × konstant 0.5` — inte med någon hänsyn till källkvalitet.

Det är samtidigt en lättnad — det betyder att fixen är trivial (en regex-ändring), och att hela värdet av källhierarki-prompten i engine.py nu faktiskt börjar realiseras i scoring.

Det är också ett starkt argument för fler tester. En enda testfall mot riktig Claude-output hade fångat detta direkt. Innan du tar in pilotkunder rekommenderar jag att vi skriver 10-20 fixture-tester av samma slag — pin riktiga claude_answer-strängar och verifiera förväntade ranked-värden. Skicka mig 5 fler history-filer så bygger jag en regression-svit av dem.

---

## Vad som INTE är fixat (nästa steg)

### Frontend
`static/index.html` rad 583 har en parallell `parseHypotheses`-funktion som körs som fallback om `r.ranked` är tom. Den hårdkodar `conf = 0.85 / 0.55 / 0.25`. Anthropic-frågan i din historik visade detta i praktiken — backend gav tomt, frontend visade 85/55/25.

Med v1.5-fixen i backend ska detta inte hända lika ofta, men fallbacken är fortfarande olämplig. Rekommendation: ta bort frontend-parsern helt. Om backend misslyckas, visa felmeddelande istället för fake-konfidens.

`?pwd=`-skickande från history/pdf-knapparna i frontend ska uppdateras till header-based auth.

### Prompt injection
Inget skydd än. Skriv ett test-script med 10 adversariella inputs och kör som regression innan FOI/MSB.

### LLM-router
Single point of failure × 2 (Anthropic + OpenAI). Lägg in LiteLLM med fallback.

### Engine-tester
Pipelinen har inga tester. Fixera 10 Claude/GPT-svar som mocks och kör pipeline mot dem.

