#!/bin/bash
# ─────────────────────────────────────────────────────────────
# SANNINGSMASKINEN v4 — Automatisk installation för Mac
# ─────────────────────────────────────────────────────────────

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     SANNINGSMASKINEN v4 — Installation               ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Steg 1: Kontrollera Python
echo "▶ Steg 1/5: Kollar att Python finns installerat..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "⚠️  Python hittades inte."
    echo "   Gå till https://www.python.org/downloads/ och installera Python 3.11+"
    echo "   Kör sedan setup.sh igen."
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo "   ✓ $PYTHON_VERSION hittad"

# Steg 2: Skapa virtuell miljö
echo ""
echo "▶ Steg 2/5: Skapar isolerad Python-miljö..."
python3 -m venv venv
echo "   ✓ Virtuell miljö skapad"

# Steg 3: Aktivera och installera paket
echo ""
echo "▶ Steg 3/5: Installerar nödvändiga paket..."
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet anthropic openai python-dotenv
echo "   ✓ Paket installerade: anthropic, openai, python-dotenv"

# Steg 4: Skapa .env om den inte finns
echo ""
echo "▶ Steg 4/5: Förbereder API-nyckelfilen..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
# ─────────────────────────────────────────────────────────
# SANNINGSMASKINEN — API-NYCKLAR
# Fyll i dina nycklar nedan. Dela ALDRIG den här filen.
# ─────────────────────────────────────────────────────────

ANTHROPIC_API_KEY=din_anthropic_nyckel_här
OPENAI_API_KEY=din_openai_nyckel_här
EOF
    echo "   ✓ .env-fil skapad — du behöver fylla i dina API-nycklar"
else
    echo "   ✓ .env-fil finns redan"
fi

# Steg 5: Skapa startskript
echo ""
echo "▶ Steg 5/5: Skapar startknapp..."
cat > starta.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python3 main.py
EOF
chmod +x starta.sh
echo "   ✓ starta.sh skapad"

# Klar
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     ✓ INSTALLATION KLAR                              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "Nästa steg:"
echo ""
echo "  1. Öppna filen .env i en textredigerare (VS Code eller TextEdit)"
echo "     och ersätt 'din_anthropic_nyckel_här' med din riktiga nyckel"
echo "     och 'din_openai_nyckel_här' med din riktiga nyckel"
echo ""
echo "  2. Starta verktyget genom att skriva:"
echo "     ./starta.sh"
echo ""
echo "  Var hämtar jag API-nycklar?"
echo "  • Anthropic: https://console.anthropic.com → API Keys"
echo "  • OpenAI:    https://platform.openai.com → API Keys"
echo ""
