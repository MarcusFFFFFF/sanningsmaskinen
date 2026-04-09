"""
Sanningsmaskinen — Flask backend
- SSE via EventSource GET (Safari/iOS-kompatibelt)
- Background jobs via threading + SQLite (flikstangningssaker)
- Modell: claude-opus-4-6 (66% billigare an Opus 4)
"""

from flask import Flask, request, jsonify, Response, stream_with_context
import sys, os, json, re, time, sqlite3, threading, uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import (
    event_reality_check, ask_claude, ask_gpt_critic,
    analyze_conflicts, run_red_team, auto_rewrite,
    generate_article, assess_depth_recommendation
)

_BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(_BASE, "static"))

# SQLite for background jobs
DB_PATH = os.environ.get('DB_PATH', os.path.join(_BASE, 'data', 'jobs.db'))


# ── DATABASE ──────────────────────────────────────────────────────────────────

def _get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = _get_db()
    db.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        status TEXT DEFAULT 'pending',
        query TEXT,
        result TEXT,
        error TEXT,
        current_step INTEGER DEFAULT 0,
        created_at REAL,
        completed_at REAL
    )""")
    db.commit()
    db.close()


def _update_job(job_id, **kwargs):
    db = _get_db()
    sets = ', '.join(k + '=?' for k in kwargs)
    vals = list(kwargs.values()) + [job_id]
    db.execute("UPDATE jobs SET " + sets + " WHERE id=?", vals)
    db.commit()
    db.close()


# ── SSE HELPERS ───────────────────────────────────────────────────────────────

def sse(event, data):
    payload = json.dumps(data, ensure_ascii=False)
    return "event: {}\ndata: {}\n\n".format(event, payload)


# ── PIPELINE RUNNER (shared by SSE + background) ──────────────────────────────

def _run_pipeline(question, on_step=None, sid="anon"):
    """
    Kor hela analyspipelinen.
    on_step(step_num) kallas efter varje steg om det ar definierat.
    Returnerar result-dict.
    """
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
        "article": "",
        "ranked": [],
    }

    rc = event_reality_check(question)
    result["reality_check"] = rc
    if on_step: on_step(0)

    if not rc["proceed"]:
        result["status"] = rc["status"]
        return result

    result["claude_answer"] = ask_claude(question, rc)
    if on_step: on_step(1)

    result["gpt_answer"] = ask_gpt_critic(question, result["claude_answer"], rc["status"])
    if on_step: on_step(2)

    # analyze_conflicts och run_red_team är inbördes oberoende — kör parallellt.
    # red_team får tom conflict_report eftersom de delar input (claude_answer + gpt) men inte beror på varandra.
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_conflicts = ex.submit(analyze_conflicts, result["claude_answer"], result["gpt_answer"])
        f_red       = ex.submit(run_red_team, question, result["claude_answer"], "")
        result["conflict_report"] = f_conflicts.result()
        red_report, should_rewrite = f_red.result()
    if on_step: on_step(3)

    result["red_team_report"] = red_report
    result["collapsed"] = should_rewrite
    result["red_team_ok"] = bool(
        red_report
        and "misslyckades" not in red_report.lower()
        and "api-fel" not in red_report.lower()
        and len(red_report) > 100
    )
    result["degraded"] = not result["red_team_ok"]
    if on_step: on_step(4)

    if should_rewrite and result["red_team_ok"]:
        result["final_analysis"] = auto_rewrite(question, result["claude_answer"], red_report)
        if on_step: on_step(5)

    try:
        from normalizer import normalize_claude_answer, compute_hypothesis_scores, _ensure_three_hypotheses
        hyps = normalize_claude_answer(result["claude_answer"])["hypotheses"]
        result["ranked"] = _ensure_three_hypotheses(
            sorted(
                compute_hypothesis_scores(hyps),
                key=lambda h: h.get("conf", 0),
                reverse=True
            )
        )
    except Exception as e:
        import traceback
        print(f"[normalizer error in _run_pipeline] {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        result["ranked"] = []

    article_source = result["final_analysis"] or result["claude_answer"]
    if article_source and len(article_source) > 200:
        try:
            result["article"] = generate_article(question, article_source, result.get("ranked", []))
        except Exception:
            result["article"] = ""

    result["depth_recommendation"] = assess_depth_recommendation(result)
    result["status"] = (
        "DEGRADERAD" if result["degraded"] else
        ("REVIDERAD" if result["final_analysis"] else "KLAR")
    )

    try:
        _save_history(question, result, sid)
    except Exception:
        pass

    return result


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return open(os.path.join(_BASE, 'static', 'index.html'), encoding='utf-8').read()


@app.route("/analyze-stream", methods=["GET"])
def analyze_stream_get():
    """EventSource GET — Safari/iOS-kompatibelt."""
    question = (request.args.get("q") or "").strip()
    sid = re.sub(r"[^a-f0-9\-]", "", (request.args.get("sid") or "anon"))[:36] or "anon"
    if not question:
        def err():
            yield sse("error", {"message": "Ingen fraga angiven"})
        return Response(stream_with_context(err()), mimetype="text/event-stream")
    return _stream_response(question, sid)


@app.route("/analyze-stream", methods=["POST"])
def analyze_stream_post():
    """POST fallback for icke-Safari-klienter."""
    data = request.get_json()
    question = (data.get("question") or "").strip()
    if not question:
        def err():
            yield sse("error", {"message": "Ingen fraga angiven"})
        return Response(stream_with_context(err()), mimetype="text/event-stream")
    return _stream_response(question)


def _stream_response(question, sid="anon"):
    step_labels = [
        "Verifierar frågan...",
        "Claude Opus bygger hypoteser...",
        "GPT-4o kör destruktiv kritik...",
        "Analyserar epistemiska konflikter...",
        "Red Team granskar analysen...",
        "Skriver om analysen baserat på Red Team...",
    ]
    done_labels = [
        [],
        ["Frågan verifierad"],
        ["Frågan verifierad", "Hypoteser byggda"],
        ["Frågan verifierad", "Hypoteser byggda", "Destruktiv kritik klar"],
        ["Frågan verifierad", "Hypoteser byggda", "Destruktiv kritik klar", "Konflikter kartlagda"],
        ["Frågan verifierad", "Hypoteser byggda", "Destruktiv kritik klar", "Konflikter kartlagda", "Red Team klar"],
    ]

    def generate():
        current_step = [0]

        def on_step(step):
            current_step[0] = step
            next_step = step + 1
            if next_step <= 5:
                label = step_labels[next_step] if next_step < len(step_labels) else "Bearbetar..."
                done = done_labels[next_step] if next_step < len(done_labels) else []
                # yield maste ske fran generatorn — anvand en kö
                pass

        try:
            yield sse("progress", {"step": 0, "label": step_labels[0], "done": []})
            rc = event_reality_check(question)

            if not rc["proceed"]:
                result = {"question": question, "reality_check": rc, "status": rc["status"],
                          "claude_answer": "", "gpt_answer": "", "conflict_report": "",
                          "red_team_report": "", "final_analysis": "", "ranked": [], "article": ""}
                yield sse("result", _serialize(result))
                return

            yield sse("progress", {"step": 1, "label": step_labels[1], "done": done_labels[1]})
            claude_answer = ask_claude(question, rc)

            yield sse("progress", {"step": 2, "label": step_labels[2], "done": done_labels[2]})
            gpt_answer = ask_gpt_critic(question, claude_answer, rc["status"])

            # Steg 3 + 4 körs parallellt. Visa båda labels samtidigt så användaren ser att de pågår.
            yield sse("progress", {"step": 3, "label": step_labels[3], "done": done_labels[3]})
            yield sse("progress", {"step": 4, "label": step_labels[4], "done": done_labels[4]})
            with ThreadPoolExecutor(max_workers=2) as ex:
                f_conflicts = ex.submit(analyze_conflicts, claude_answer, gpt_answer)
                f_red       = ex.submit(run_red_team, question, claude_answer, "")
                conflict_report = f_conflicts.result()
                red_report, should_rewrite = f_red.result()

            red_team_ok = bool(
                red_report
                and "misslyckades" not in red_report.lower()
                and "api-fel" not in red_report.lower()
                and len(red_report) > 100
            )

            final_analysis = ""
            if should_rewrite and red_team_ok:
                yield sse("progress", {"step": 5, "label": step_labels[5], "done": done_labels[5]})
                final_analysis = auto_rewrite(question, claude_answer, red_report)

            try:
                from normalizer import normalize_claude_answer, compute_hypothesis_scores, _ensure_three_hypotheses
                hyps = normalize_claude_answer(claude_answer)["hypotheses"]
                ranked = _ensure_three_hypotheses(
                    sorted(compute_hypothesis_scores(hyps), key=lambda h: h.get("conf", 0), reverse=True)
                )
            except Exception as e:
                import traceback
                print(f"[normalizer error in _stream_response] {type(e).__name__}: {e}", flush=True)
                traceback.print_exc()
                ranked = []

            article_source = final_analysis or claude_answer
            article = ""
            if article_source and len(article_source) > 200:
                try:
                    article = generate_article(question, article_source, ranked)
                except Exception:
                    article = ""

            result = {
                "question": question,
                "reality_check": rc,
                "claude_answer": claude_answer,
                "gpt_answer": gpt_answer,
                "conflict_report": conflict_report,
                "red_team_report": red_report,
                "red_team_ok": red_team_ok,
                "collapsed": should_rewrite,
                "final_analysis": final_analysis,
                "degraded": not red_team_ok,
                "ranked": ranked,
                "article": article,
                "status": "DEGRADERAD" if not red_team_ok else ("REVIDERAD" if final_analysis else "KLAR"),
                "depth_recommendation": assess_depth_recommendation({
                    "red_team_ok": red_team_ok,
                    "conflict_report": conflict_report,
                    "claude_answer": claude_answer,
                }),
            }

            try:
                _save_history(question, result, sid)
            except Exception as e:
                print(f"[save_history error] {type(e).__name__}: {e}", flush=True)

            yield sse("result", _serialize(result))

        except Exception as e:
            import traceback
            print(f"[stream_response error] question={question!r} {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
            yield sse("error", {"message": f"{type(e).__name__}: {e}"})

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


# ── BACKGROUND JOBS ───────────────────────────────────────────────────────────

def _run_bg(job_id, question):
    """Kor pipeline i bakgrundstrad, uppdaterar SQLite."""
    def on_step(step):
        _update_job(job_id, current_step=step, status='running')

    try:
        result = _run_pipeline(question, on_step=on_step)
        _update_job(job_id, status='complete', result=json.dumps(_serialize(result), ensure_ascii=False), completed_at=time.time())
    except Exception as e:
        _update_job(job_id, status='failed', error=str(e))


@app.route("/analyze-bg", methods=["POST"])
def analyze_bg():
    """Starta bakgrundsjobb. Returnerar job_id omedelbart."""
    data = request.get_json()
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Ingen fraga"}), 400

    job_id = str(uuid.uuid4())
    db = _get_db()
    db.execute(
        "INSERT INTO jobs (id, status, query, created_at) VALUES (?, 'pending', ?, ?)",
        (job_id, question, time.time())
    )
    db.commit()
    db.close()

    t = threading.Thread(target=_run_bg, args=(job_id, question), daemon=True)
    t.start()

    return jsonify({"job_id": job_id}), 202


@app.route("/result/<job_id>")
def get_result(job_id):
    """Polla status for ett bakgrundsjobb."""
    db = _get_db()
    row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    db.close()
    if not row:
        return jsonify({"status": "not_found"}), 404
    resp = {"status": row["status"], "current_step": row["current_step"]}
    if row["status"] == "complete" and row["result"]:
        resp["result"] = json.loads(row["result"])
    elif row["status"] == "failed":
        resp["error"] = row["error"]
    return jsonify(resp)


# ── HISTORY ───────────────────────────────────────────────────────────────────

HISTORY_PASSWORD = os.environ.get("HISTORY_PASSWORD", "sanningsmaskinen")


def _check_history_pwd():
    return (request.args.get("pwd") or "") == HISTORY_PASSWORD


@app.route("/history", methods=["GET"])
def history():
    admin_pwd = os.environ.get("ADMIN_PASSWORD", "")
    is_admin = admin_pwd and (request.args.get("admin") == admin_pwd)
    if not is_admin and not _check_history_pwd():
        return jsonify({"error": "forbidden"}), 403
    sid = (request.args.get("sid") or "")
    entries = []
    history_dir = os.path.join(_BASE, "history")
    if os.path.isdir(history_dir):
        files = sorted([f for f in os.listdir(history_dir) if f.endswith(".json")], reverse=True)[:50]
        for f in files:
            try:
                with open(os.path.join(history_dir, f)) as fh:
                    data = json.load(fh)
                    entry = {
                        "filename": f,
                        "question": data.get("question", ""),
                        "timestamp": data.get("timestamp", ""),
                        "status": data.get("status", ""),
                        "reality": data.get("reality_check", {}).get("status", ""),
                        "session_id": data.get("session_id", "")
                    }
                    if is_admin or not sid or entry["session_id"] == sid:
                        entries.append(entry)
            except Exception:
                pass
    return jsonify(entries)


@app.route("/history/<path:filename>", methods=["GET"])
def load_history(filename):
    if not _check_history_pwd():
        return jsonify({"error": "forbidden"}), 403
    from urllib.parse import unquote
    filename = unquote(filename)
    history_dir = os.path.join(_BASE, "history")
    path = os.path.join(history_dir, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Hittades inte"}), 404
    with open(path, encoding="utf-8") as f:
        return jsonify(json.load(f))


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _save_history(question, result, session_id="anon"):
    history_dir = os.path.join(_BASE, "history")
    os.makedirs(history_dir, exist_ok=True)
    ts = date.today().strftime("%Y%m%d")
    safe_q = re.sub(r"[^\w\s-]", "", question)[:40].strip().replace(" ", "_")
    filename = ts + "_" + session_id[:8] + "_" + safe_q + ".json"
    result["question"] = question
    result["timestamp"] = ts
    result["session_id"] = session_id
    with open(os.path.join(history_dir, filename), "w", encoding="utf-8") as f:
        json.dump(_serialize(result), f, ensure_ascii=False, indent=2)


def _serialize(obj):
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(i) for i in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


# ── START ─────────────────────────────────────────────────────────────────────

_init_db()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    print("Sanningsmaskinen startar pa http://localhost:{}".format(port))
    app.run(debug=False, host='0.0.0.0', port=port)
