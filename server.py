"""
Sanningsmaskinen — Flask backend
Ersätter app.py (Streamlit) med en riktig webbserver.
Engine.py rörs inte.
"""

from flask import Flask, request, jsonify, send_from_directory
import sys
import os
import json
import re
from datetime import date

# Se till att engine hittas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import run_full_pipeline

import os as _os
_BASE = _os.path.dirname(_os.path.abspath(__file__))
app = Flask(__name__, static_folder=_os.path.join(_BASE, "static"))


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return open(os.path.join(_BASE, 'static', 'index.html')).read()


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Ingen fråga angiven"}), 400

    try:
        result = run_full_pipeline(question)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Normalisera ranked från normalizer
    try:
        from normalizer import parse_hypotheses, compute_hypothesis_scores
        claude_answer = result.get("claude_answer", "")
        hypotheses = parse_hypotheses(claude_answer)
        ranked = sorted(
            compute_hypothesis_scores(hypotheses),
            key=lambda h: h.get("conf", 0),
            reverse=True
        )
        result["ranked"] = ranked
    except Exception:
        result["ranked"] = []

    # Spara i history
    try:
        _save_history(question, result)
    except Exception:
        pass

    return jsonify(_serialize(result))


@app.route("/history", methods=["GET"])
def history():
    entries = []
    history_dir = os.path.join(_BASE, "history")
    if os.path.isdir(history_dir):
        files = sorted(
            [f for f in os.listdir(history_dir) if f.endswith(".json")],
            reverse=True
        )[:50]
        for f in files:
            try:
                with open(os.path.join(history_dir, f)) as fh:
                    data = json.load(fh)
                    entries.append({
                        "filename": f,
                        "question": data.get("question", ""),
                        "timestamp": data.get("timestamp", ""),
                        "status": data.get("status", ""),
                        "reality": data.get("reality_check", {}).get("status", "")
                    })
            except Exception:
                pass
    return jsonify(entries)


@app.route("/history/<path:filename>", methods=["GET"])
def load_history(filename):
    from urllib.parse import unquote
    filename = unquote(filename)
    history_dir = os.path.join(_BASE, "history")
    path = os.path.join(history_dir, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Hittades inte"}), 404
    with open(path, encoding="utf-8") as f:
        return jsonify(json.load(f))


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _save_history(question, result):
    history_dir = os.path.join(os.path.dirname(__file__), "history")
    os.makedirs(history_dir, exist_ok=True)
    ts = date.today().strftime("%Y%m%d")
    safe_q = re.sub(r"[^\w\s-]", "", question)[:40].strip().replace(" ", "_")
    filename = ts + "_" + safe_q + ".json"
    result["question"] = question
    result["timestamp"] = ts
    with open(os.path.join(history_dir, filename), "w") as f:
        json.dump(_serialize(result), f, ensure_ascii=False, indent=2)


def _serialize(obj):
    """Gör result JSON-serialiserbart."""
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(i) for i in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


# ── START ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Sanningsmaskinen startar på http://localhost:5000")
    app.run(debug=True, port=5001)
