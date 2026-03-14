# SANNINGSMASKINEN

Sanningsmaskinen är ett AI-drivet analysverktyg som granskar påståenden genom flera lager av resonemang.

Systemet använder flera AI-motorer (Claude och GPT) i en strukturerad process för att:

- analysera hypoteser
- hitta motsägelser
- utsätta resonemang för kritisk granskning
- identifiera svagheter och bias
- producera en reviderad slutsats

Målet är att skapa mer transparent och robust informationsanalys.

---# SANNINGSMASKINEN v4
## Steg-för-steg guide — så enkel som möjligt

---

## VAD DU BEHÖVER INNAN DU BÖRJAR

Två API-nycklar (som lösenord till AI-motorerna):
- En från **Anthropic** (Claude): https://console.anthropic.com → logga in → "API Keys" → "Create Key"
- En från **OpenAI** (GPT-4): https://platform.openai.com → logga in → "API Keys" → "Create new secret key"

Kopiera båda och spara dem temporärt i en textnota. Du behöver dem i steg 3.

---

## INSTALLATION — 4 STEG

### Steg 1: Flytta mappen till rätt plats

Flytta mappen `sanningsmaskinen` till din hemkatalog.
Det enklaste är att dra den till `Dokument` eller direkt till skrivbordet.

---

### Steg 2: Öppna Terminal och gå till mappen

Öppna **Terminal** (finns i Program → Verktygsprogram, eller sök "Terminal").

Skriv sedan detta och tryck Enter:
```
cd ~/Desktop/sanningsmaskinen
```

*(Om du lade mappen i Dokument istället: `cd ~/Documents/sanningsmaskinen`)*

Du vet att det fungerade när terminalen visar mappnamnet i prompten.

---

### Steg 3: Kör installationsskriptet

Skriv detta och tryck Enter:
```
chmod +x setup.sh && ./setup.sh
```

Det här kommandot:
- Kontrollerar att Python finns på din dator
- Installerar alla nödvändiga delar automatiskt
- Skapar en fil som heter `.env` där dina API-nycklar ska in

Vänta tills det är klart (tar 1-2 minuter).

---

### Steg 4: Lägg in dina API-nycklar

Öppna filen `.env` i VS Code (eller TextEdit).

Den ser ut så här:
```
ANTHROPIC_API_KEY=din_anthropic_nyckel_här
OPENAI_API_KEY=din_openai_nyckel_här
```

Ersätt `din_anthropic_nyckel_här` med din Anthropic-nyckel.
Ersätt `din_openai_nyckel_här` med din OpenAI-nyckel.

Spara filen.

**Viktigt:** Dela aldrig `.env`-filen med någon. Den innehåller dina nycklar.

---

## STARTA VERKTYGET

Varje gång du vill använda Sanningsmaskinen:

1. Öppna Terminal
2. Skriv: `cd ~/Desktop/sanningsmaskinen` (eller var du lade mappen)
3. Skriv: `./starta.sh`

Verktyget startar och du ser:
```
╔══════════════════════════════════════════════════════╗
║           SANNINGSMASKINEN v4.0                      ║
╚══════════════════════════════════════════════════════╝

Din fråga →
```

Skriv din fråga och tryck Enter. Båda AI-motorerna svarar efter varandra.

---

## KOMMANDON INNE I VERKTYGET

| Kommando | Vad det gör |
|----------|-------------|
| *(skriv din fråga)* | Kör analysen |
| `rensa` | Rensar konversationshistoriken |
| `quit` | Stänger verktyget |

---

## FELSÖKNING

**"command not found: python3"**
→ Installera Python från https://www.python.org/downloads/

**"Invalid API key"**
→ Kontrollera att du kopierade hela nyckeln i .env utan mellanslag

**"ModuleNotFoundError"**
→ Kör `source venv/bin/activate` och sedan `pip install anthropic openai python-dotenv`

---

## FILSTRUKTUR

```
sanningsmaskinen/
├── main.py          ← Själva verktyget
├── setup.sh         ← Installationsskript (kör en gång)
├── starta.sh        ← Startknapp (kör varje gång)
├── .env             ← Dina API-nycklar (dela aldrig)
├── venv/            ← Python-miljö (rör inte)
└── README.md        ← Den här filen
```

---

*SANNINGSMASKINEN v4 — Mars 2026*
