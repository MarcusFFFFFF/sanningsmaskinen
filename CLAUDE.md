# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Sanningsmaskinen is an epistemic analysis tool (Swedish-language) that runs a multi-stage analysmotor (Claude Opus + GPT) to answer complex questions with explicit source grading (E1–E5), three-lens hypothesis testing, conflict analysis, and Red Team review. The system's core principle: produce the *least wrong* answer, not the most pleasing one. See `sanningsmaskinen_grundprinciper.md` for the governing philosophy — the E1–E5 grading and the structural prompts in `engine.py` are deliberately load-bearing and should not be softened without explicit reason.

## Running the app

There are **two parallel frontends** in this repo, both backed by `engine.py`:

- **Flask + static HTML (production / Railway)** — entry point `server.py`. This is what the `Procfile` runs:
  ```
  gunicorn server:app --timeout 300 --workers 2 --bind 0.0.0.0:$PORT
  ```
  Local: `python3 server.py` (defaults to port 5001). Serves `static/index.html` at `/` and exposes `/analyze-stream` (SSE, GET for Safari/iOS + POST), `/analyze-bg` + `/result/<job_id>` (background jobs in SQLite at `data/jobs.db`), and `/history`.
- **Streamlit (legacy/local)** — `app.py`. Run with `streamlit run app.py` after `source venv/bin/activate`. Note `requirements.txt` still pulls in `streamlit` for this reason.

`main.py` and `starta.sh` are the older CLI from README/INSTALL — kept around but not the current path.

There are no tests, no linter config, and no build step. Dependencies: `pip install -r requirements.txt`. Required env vars in `.env`: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` (see `.env.example`).

## Architecture

The pipeline lives in `engine.py` and is orchestrated by `server.py::_run_pipeline` (and `_stream_response` for SSE). The stages, in order, are:

1. **`event_reality_check(question)`** — classifies the question as `EVENT` / `ANALYTICAL` / `HYPOTHETICAL` and may short-circuit the pipeline (`proceed=False`) for non-events.
2. **`ask_claude(question, rc)`** — primary analysis from Claude Opus (`claude-opus-4-6`) using the big `SYSTEM_PROMPT` assembled from `SOURCE_HIERARCHY` + `THREE_LENSES` + `URL_INSTRUCTION` + `SOURCE_STRATEGY` + `EPISTEMIC_PRIORITY_INSTRUCTION`. Output is expected to contain three hypotheses (H1 structural / H2 domestic / H3 actor-psychology) with TES/BEVIS/MOTARG/STYRKA fields and `[E1]`–`[E5]` source tags.
3. **`ask_gpt_critic`** — destructive critique from GPT.
4. **`analyze_conflicts`** — epistemic conflict map between the two answers.
5. **`run_red_team`** — adversarial review; returns `(report, should_rewrite)`. The pipeline marks itself `degraded` if Red Team failed (short report or contains "misslyckades"/"api-fel").
6. **`auto_rewrite`** — only runs if Red Team said rewrite *and* Red Team itself was healthy.
7. **`normalizer.parse_hypotheses` + `compute_hypothesis_scores`** — parses Claude's structured output into ranked hypothesis dicts (used by the UI and the article generator).
8. **`generate_article`** — produces the final journalist-style writeup from `final_analysis or claude_answer`.
9. **`assess_depth_recommendation`** — suggests whether the user should drill deeper.

Final `status` is one of `KLAR` / `REVIDERAD` / `DEGRADERAD` / (or whatever `reality_check` returned if it short-circuited).

### normalizer.py — fragile ordering

`normalizer.py` parses Claude's free-text output into structured hypotheses and rescales `STYRKA` labels into numeric `conf` scores using `_SOURCE_LABELS` (E1=0.2 … E5=1.0). **Critical ordering bug from v18, documented in `INSTALL.md`:** `normalize_references()` rewrites `[E4]`/`[E5]` tags into Swedish labels and **must not** run before `normalize_claude_answer()` — doing so destroys the evidence tags before the BEVIS parser sees them. If you touch the normalize pipeline, preserve this order.

### History persistence

Completed runs are written to `history/<YYYYMMDD>_<safe_question>.json` by `server.py::_save_history`. The `/history` endpoint lists the most recent 50. The `history/` directory is gitignored.

### Background jobs

`/analyze-bg` spawns a daemon thread that runs `_run_pipeline` and writes status/result to SQLite (`data/jobs.db`, WAL mode). Clients poll `/result/<job_id>`. This exists so users can close the tab without losing the run — keep that property when modifying job code.

## Repo hygiene notes

The working tree has many backup files (`app_backup_*.py`, `app 2.py`, `engine.py.bak87`, `Arkiv*.zip`, etc.) and screenshots from the user's workflow. These are intentional local snapshots — **do not delete them** and do not edit them as if they were the live code. The live files are `app.py`, `engine.py`, `server.py`, `normalizer.py`, `pdf_export.py`, `static/index.html`, `outreach.html`. The gitignore already excludes `*backup*.py`, `*copy*.py`, `*.bak*`, `history/`, `.env`, and `venv/`.

Swedish is the working language for prompts, UI, comments, and commit messages — keep it that way unless asked otherwise.
