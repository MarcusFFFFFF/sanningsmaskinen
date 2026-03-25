# -*- coding: utf-8 -*-
"""
SANNINGSMASKINEN — Historikmodul
Sparar varje analys som JSON i ~/sanningsmaskinen/history/
Läses av app.py för att visa och ladda ner gamla analyser.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

# Historik-mapp — relativt till engine.py/app.py
HISTORY_DIR = Path(__file__).parent / 'history'


def _ensure_dir():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _slug(question: str) -> str:
    """Skapar ett filnamn-säkert ID från frågan."""
    q = question.lower()[:50]
    q = re.sub(r'[^a-zåäö0-9 ]', '', q)
    q = re.sub(r'\s+', '_', q.strip())
    return q[:40]


def save_result(result: dict) -> str:
    """
    Sparar ett pipeline-result till history/.
    Returnerar filnamnet (utan path).
    """
    _ensure_dir()
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    slug     = _slug(result.get('question', 'okand'))
    filename = f"{ts}_{slug}.json"
    path     = HISTORY_DIR / filename

    # Gör result JSON-serialiserbart
    serializable = {}
    for k, v in result.items():
        if isinstance(v, dict):
            serializable[k] = v
        elif isinstance(v, (str, bool, int, float, list)) or v is None:
            serializable[k] = v
        else:
            serializable[k] = str(v)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

    return filename


def list_history():
    """
    Returnerar lista med metadata om sparade analyser, nyast först.
    Varje post: {filename, timestamp, question, status, reality}
    """
    _ensure_dir()
    entries = []
    for p in sorted(HISTORY_DIR.glob('*.json'), reverse=True):
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            rc = data.get('reality_check') or {}
            entries.append({
                'filename':  p.name,
                'timestamp': p.name[:15].replace('_', ' '),
                'question':  data.get('question', '(okänd fråga)'),
                'status':    data.get('status', ''),
                'reality':   rc.get('status', ''),
                'has_layers': bool(data.get('layers', {}).get('ground')),
                'has_deep':   bool(data.get('layers', {}).get('deep1')),
                'tags':      data.get('tags', []),
            })
        except Exception:
            continue
    return entries


def load_result(filename: str):
    """Laddar ett sparat result från history/."""
    _ensure_dir()
    path = HISTORY_DIR / filename
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def delete_result(filename: str) -> bool:
    """Raderar en sparad analys."""
    path = HISTORY_DIR / filename
    if path.exists():
        path.unlink()
        return True
    return False


def add_tag(filename: str, tag: str) -> bool:
    """Lägger till en tagg på en sparad analys."""
    path = HISTORY_DIR / filename
    if not path.exists(): return False
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        tags = data.get('tags', [])
        tag = tag.strip()[:30]
        if tag and tag not in tags:
            tags.append(tag)
            data['tags'] = tags
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def remove_tag(filename: str, tag: str) -> bool:
    """Tar bort en tagg från en sparad analys."""
    path = HISTORY_DIR / filename
    if not path.exists(): return False
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        tags = data.get('tags', [])
        data['tags'] = [t for t in tags if t != tag]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
    """Bygger en ren txt-export av ett result."""
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    rc    = result.get('reality_check') or {}
    lyr   = result.get('layers') or {}

    parts = [
        '=' * 70 + '\n',
        'SANNINGSMASKINEN v8.5\n',
        f"Fråga: {result.get('question', '')}\n",
        f"Datum: {today}\n",
        f"Status: {result.get('status', '')} | Reality: {rc.get('status', '')}\n",
        '=' * 70 + '\n\n',
        'REALITY CHECK\n' + '-' * 40 + '\n',
        rc.get('text', '') + '\n\n',
        'PRIMÄRANALYS\n' + '-' * 40 + '\n',
        result.get('claude_answer', '') + '\n\n',
    ]
    if lyr.get('ground'):
        parts += ['LAYER 1-5\n' + '-' * 40 + '\n', lyr['ground'] + '\n\n']
    if lyr.get('deep1'):
        parts += [
            'FÖRDJUPNING 1\n' + '-' * 40 + '\n', lyr['deep1'] + '\n\n',
            'FÖRDJUPNING 2\n' + '-' * 40 + '\n', lyr['deep2'] + '\n\n',
            'FÖRDJUPNING 3\n' + '-' * 40 + '\n', lyr['deep3'] + '\n\n',
        ]
    parts += [
        'GPT-4 KRITIKER\n' + '-' * 40 + '\n',
        result.get('gpt_answer', '') + '\n\n',
        'KONFLIKTANALYS\n' + '-' * 40 + '\n',
        result.get('conflict_report', '') + '\n\n',
        'RED TEAM\n' + '-' * 40 + '\n',
        result.get('red_team_report', '') + '\n\n',
    ]
    if result.get('final_analysis'):
        parts += ['REVIDERAD ANALYS\n' + '-' * 40 + '\n',
                  result['final_analysis'] + '\n\n']
    parts += ['\n' + '=' * 70 + '\n',
              'Sanningen favoriserar ingen sida. — Sanningsmaskinen v8.5']
    return ''.join(parts)
