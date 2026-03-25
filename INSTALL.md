# Sanningsmaskinen — Patch v18

## Vad som fixades

Rotkorsansen var att `normalize_references()` kördes FÖRE `normalize_claude_answer()` i app.py.
Det ersatte [E4]/[E5]-taggar med svenska labels INNAN parsern hann läsa dem,
vilket gjorde att BEVIS-parsern inte hittade evidens-taggarna och returnerade tomma listor.

## Installation

### 1. Ersätt normalizer.py
Kopiera `normalizer.py` till ~/Desktop/sanningsmaskinen/

### 2. Ersätt pdf_export.py
Kopiera `pdf_export.py` till ~/Desktop/sanningsmaskinen/

### 3. Patcha app.py
Kör:
  python3 app_normalizer_patch.py app.py app.py

Eller ändra manuellt i app.py — sök efter:
  norm = normalize_claude_answer(normalize_references(raw_claude))

Ändra till:
  norm = normalize_claude_answer(raw_claude)

### 4. Starta om
  pkill -9 -f streamlit && cd ~/Desktop/sanningsmaskinen && source venv/bin/activate && streamlit run app.py
