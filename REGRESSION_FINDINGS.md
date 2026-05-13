# Regression-fynd från 10 prod-fixtures

Datum: 13 maj 2026. Körd mot v1.5 av normalizer.

## Det stora fyndet

**8 av 10 prod-analyser hade tomt `ranked` i v1.4** — frontend-fallbacken (85/55/25) var de facto produkten. Det är inte ett ranking-problem. Det är att ranking-systemet inte var aktivt i 80% av användningen.

Orsaken är E-tag-regexen (dokumenterad i CHANGES.md). När parsern inte hittade E-taggar i bevisen failade källkvalitetsberäkningen för många frågor i en kedja som ledde till tomt `ranked`.

v1.5 fixar 7 av 8 av dessa. JFK kvarstår som problemfall (separat orsak — se nedan).

## Fall för fall

| Fråga | v1.4 | v1.5 | Status |
|---|---|---|---|
| Northvolt | tomt | 79/61/58 | ✓ |
| Samerna | tomt | 55/53/52 | ✓ |
| NATO 2024 | tomt | 73/73/55 | ⚠ kluster |
| JFK | tomt | 65/45/25 (fallback) | ✗ parser-fel |
| USA invaderade Iran (hypotetisk) | tomt | 81/81/59 | ⚠ kluster |
| Anthropic (1) | tomt | 85/73/67 | ✓ |
| Anthropic (2) | tomt | 85/83/55 | ✓ |
| Iran-status 23/4 19:11 | 43/43/42 | 85/76/76 | ⚠ kluster |
| Iran-status 23/4 20:24 | 78/78/58 | 87/79/67 | ✓ |
| Nord Stream | 67/58/58 | 69/67/65 | ✓ |

Nettoresultat: 6 av 10 nu fullt differentierade, 3 har kvarvarande kluster, 1 har parser-fel.

## Klusterfallen — vad de visar

NATO och Iran-status (19:11) klustrar för att de **är epistemiskt identiska**:
- Båda HÖG-hypoteser
- Samma antal bevis (3 vs 3)
- Samma antal motargument (2 vs 2)
- Samma källkvalitet (alla E4)

Det är matematiskt omöjligt för formeln att differentiera dem. Det är inte heller fel — två likvärdigt starka hypoteser borde få samma conf.

Iran-invaderade-USA klustrar trots att H3 har 11 bevis vs H1:s 3. Det är en **reell formelsvaghet**: `_evidence_count_factor(n) = min(1.0, 0.40 + 0.25 × log2(n+1))` cap:as på 1.0 redan vid 4 bevis. Fler bevis premieras inte.

## JFK — ett tredje problem

Parsern hittar 0/3 hypoteser. Bara 3 E-taggar i hela råtexten. Reality_check status är PARTIAL (frågan "vem dödad jfk" är delvis verifierad — gärningsmannen är fastslagen men konspirationsteorier finns).

Hypotes: när reality_check signalerar PARTIAL eller UNVERIFIED, ändrar Claude format — den producerar inte tre strukturerade hypoteser med STYRKA-bedömningar, utan en mer fri-form-text. Parsern är inte tränad för det formatet.

Det här är ett separat fix från regex-buggen. Kräver antingen:
- Engine-prompt som tvingar ACH-format även för PARTIAL-frågor
- Parser som hanterar friare format som fallback
- Eller medvetet val: PARTIAL-frågor visar inte H1-H3-kort (matchar DECISION-dokumentet du skrev om Medtänkaren)

## Tre konkreta nästa steg

### A. Frontend-parser ska bort (kritiskt)

`static/index.html` rad 583 har en `parseHypotheses`-funktion som körs om backend skickar tomt `ranked`. Den hårdkodar `conf = 0.85 / 0.55 / 0.25`. Det här har visat **fake-rankings i 8 av 10 prod-körningar.** Ta bort den helt. Om backend skickar tomt ranked, visa felmeddelande eller dölj H-korten — visa inte fake.

Sökning för fixet:
```js
// FORE (rad 599):
const ranked = (r.ranked && r.ranked.length > 0) ? r.ranked : parseHypotheses(r.claude_answer || '');

// EFTER:
const ranked = (r.ranked && r.ranked.length > 0) ? r.ranked : [];
```

Och radera `parseHypotheses`-funktionen helt (rad 571-596). Med v1.5-fixen ska backend nu leverera ranked i ~9 av 10 fall — det är OK att UI:t inte visar H-kort i resten.

### B. Höj evidence_count_factor-taket

Trivial parameter-ändring. Iran-invaderade-USA visar att 11 bevis inte premieras över 3. Föreslagen ändring i normalizer.py:

```python
def _evidence_count_factor(n: int) -> float:
    if n <= 0:
        return 0.30
    # Höj taket: 3 bevis = 0.85, 6 bevis = 0.95, 10+ bevis = 1.0
    return min(1.0, 0.40 + 0.20 * math.log2(n + 1))
```

Inte gör det idag. Lägg det på nästa patchlista.

### C. JFK-fallet kräver promptändring i engine.py

För frågor där reality_check returnerar PARTIAL/UNVERIFIED, säkerställer engine.py inte att Claude håller sig till ACH-formatet. Två lösningar:

1. Skärp prompten i `ask_claude`: "Även för obekräftade/partiella frågor MÅSTE du producera H1/H2/H3 i exakt struktur."
2. Implementera DECISION-dokumentets "Medtänkare"-flöde: PARTIAL-frågor får en chattbubbla istället för H-kort.

Alternativ 2 är epistemiskt ärligare. Men kräver UI-arbete.

## Vad regression-sviten är värd

`regression_test.py` är nu en testbädd som körs mot riktig prod-data. Lägg den i CI:

```
python3 regression_test.py fixtures/ > regression.log
# Kontroll att inga nya kluster eller parser-fel introduceras
grep "kluster\|0/3 hypoteser" regression.log
```

Innan varje deploy: kör mot fixturerna, granska diff mot förra deployen. Det fångar exakt den typ av tysta regression som E-tag-buggen var. Hade vi haft denna i v1.0 hade buggen hittats samma dag.

Lägg också till nya fixtures kontinuerligt — varje gång du hittar ett edge-case (PARTIAL, UNVERIFIED, mycket långa svar, mycket korta svar), spara `history/<den-filen>.json` i `fixtures/`.

---

## Vad jag rekommenderar härnäst

I ordning, med hänsyn till var värdet är högst:

1. **Deploya v9 (de filer vi redan har)** — backup, drop-in, `pip install flask-limiter`, push. Det fixar det största problemet (E-tag-buggen) och säkerheten.
2. **Ta bort frontend-parsern** — en 30-min-ändring. Förhindrar att fake-rankings visas i de få fall backend fortfarande failar.
3. **Lägg regression-sviten i ditt repo + CI** — den är guld värd för fortsatt utveckling.
4. **Spara om en JFK-typ-fråga med v1.5 deployad** — verifiera om regex-fixen ensam löste det eller om problemet är engine.py:s prompt.
5. **JFK-fallet och prompt-skärpning** — efter att vi sett om punkt 4 ändrar bilden.
