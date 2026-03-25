#!/usr/bin/env python3
"""
Patch för app.py:
Ändrar normalize_claude_answer(normalize_references(raw_claude))
till normalize_claude_answer(raw_claude)
så att E-taggar finns kvar när parsern körs.
normalize_references körs sedan separat för UI-rendering.
"""
import sys

def apply(src, dst):
    with open(src, 'r', encoding='utf-8') as f:
        code = f.read()

    # Den kritiska raden i app.py
    OLD = "norm = normalize_claude_answer(normalize_references(raw_claude))"
    NEW = "norm = normalize_claude_answer(raw_claude)  # OBS: normalize_references körs EJ här — parsern behöver råa E-taggar"

    if OLD in code:
        code = code.replace(OLD, NEW)
        print("Patch 1 OK: normalize_references borttagen ur normalizer-kedjan")
    else:
        print("Patch 1: raden hittades inte — kontrollera manuellt")

    with open(dst, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"Skriven: {dst}")

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'app.py'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'app_patched.py'
    apply(src, dst)
