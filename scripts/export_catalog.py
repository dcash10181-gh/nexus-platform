#!/usr/bin/env python3
"""
Export the backend catalog (api/catalog/seed.py) to a static frontend module
(frontend/src/data/catalog.js).

This keeps ONE source of truth: the seed. The frontend imports the generated
module so the demo renders the full catalog with no running API/DB dependency.

Usage:
    python scripts/export_catalog.py

Run this after any change to CATALOG / CATALOG_EXTENDED in seed.py.
The generated file is checked in; regenerate and commit when the seed changes.
"""
from __future__ import annotations
import ast
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(ROOT, "api", "catalog", "seed.py")
OUT = os.path.join(ROOT, "frontend", "src", "data", "catalog.js")


def _extract_list(name: str, text: str) -> str:
    """Return the source slice for `name: list[dict] = [ ... ]`."""
    marker = f"{name}: list[dict] = ["
    start = text.index(marker)
    i = start + len(marker) - 1  # the real opening bracket
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "[":
            depth += 1
        elif text[j] == "]":
            depth -= 1
            if depth == 0:
                return text[i : j + 1]
    raise ValueError(f"Unbalanced brackets while parsing {name}")


def _normalize_dna(dna: dict) -> dict:
    """Convert underscore tokens to spaces for display parity."""
    if not isinstance(dna, dict):
        return dna
    if "thematic_tags" in dna:
        dna["thematic_tags"] = [t.replace("_", " ") for t in dna["thematic_tags"]]
    if dna.get("visual_style"):
        dna["visual_style"] = dna["visual_style"].replace("_", " ")
    if dna.get("audio_mood"):
        dna["audio_mood"] = dna["audio_mood"].replace("_", " ")
    return dna


def main() -> int:
    src = open(SEED, encoding="utf-8").read()
    full = ast.literal_eval(_extract_list("CATALOG", src)) + ast.literal_eval(
        _extract_list("CATALOG_EXTENDED", src)
    )

    seen: dict[str, dict] = {}
    for item in full:
        if item["id"] in seen:
            continue
        item["dna"] = _normalize_dna(item.get("dna") or {})
        seen[item["id"]] = item
    catalog = list(seen.values())

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    body = json.dumps(catalog, ensure_ascii=False, indent=2)
    out = (
        "// AUTO-GENERATED from api/catalog/seed.py — do not edit by hand.\n"
        "// Regenerate via: python scripts/export_catalog.py\n"
        f"const CATALOG = {body};\n\nexport default CATALOG;\n"
    )
    open(OUT, "w", encoding="utf-8").write(out)
    print(f"Exported {len(catalog)} titles -> {os.path.relpath(OUT, ROOT)}")

    # Integrity check: every mood/graph reference must resolve.
    import re

    ids = set(seen)
    pairs = set(re.findall(r'\("([a-z0-9-]+)",\s*"([a-z0-9-]+)"', src))
    graph_ids = {x for p in pairs for x in p}
    js_path = os.path.join(ROOT, "frontend", "src", "components", "AskNexus.jsx")
    mood_ids = set()
    if os.path.exists(js_path):
        mood_ids = set(
            re.findall(r"'([a-z0-9][a-z0-9-]+-\d{4})'", open(js_path).read())
        )
    orphans = sorted((graph_ids | mood_ids) - ids)
    if orphans:
        print("WARNING: orphan references (not in catalog):", orphans, file=sys.stderr)
        return 1
    print("Integrity OK: zero orphan references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
