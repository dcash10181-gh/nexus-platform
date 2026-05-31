# Catalog Integrity & Single Source of Truth

**Status:** Resolved
**Date:** 2026-05-31
**Area:** `api/catalog/seed.py`, `frontend/src/data/catalog.js`, `frontend/src/components/AskNexus.jsx`

## Problem

Three demo-breaking bugs traced to one root cause: the catalog had **no single
source of truth**, and references drifted out of sync after the 55→81 catalog
expansion (commit `9b66aef`).

1. **Frontend ran on 18 hardcoded titles** (`MOCK_CONTENT` in `App.jsx`) while the
   UI claimed "81 titles". Most catalog titles were unmatchable and unlinkable.
2. **Ask Nexus had no title-intent matching.** Voice/text requests for a specific
   title ("watch Aftersun", "play Past Lives") fell through to the mood prompt,
   because the matcher only keyed on genre/mood triggers — title strings lived
   only inside reply text and suggestion arrays.
3. **17 flagship titles were orphaned.** Titles referenced by the mood matcher
   (suggestion IDs) and the Neo4j graph relationship pairs — Severance, Dune,
   Parasite, Succession, The Bear, Blade Runner 2049, The Last of Us, and others
   — did not exist as catalog entries. Suggestion chips dead-linked; graph edges
   pointed at non-existent nodes.

## Resolution

- **Reconciled the seed to 98 titles.** Restored the 17 orphaned titles: 10 were
  recovered from the original `MOCK_CONTENT` flagship set; 7 (House of the Dragon,
  Inception, Past Lives, Slow Horses, Station Eleven, The Menu, True Detective:
  Night Country) were authored with accurate metadata. Verified **zero orphan
  references** across mood matcher and graph pairs.
- **Established a single source of truth.** `api/catalog/seed.py` is canonical.
  `scripts/export_catalog.py` generates `frontend/src/data/catalog.js` from it and
  runs an integrity check (fails if any mood/graph reference is unresolved).
  `App.jsx` imports the generated module — the inline `MOCK_CONTENT` literal is
  gone. The demo renders the full catalog with **no running API/DB dependency**.
- **Added title-intent matching to Ask Nexus** (`findTitleMatch`). Runs *before*
  mood matching: a named title routes straight to the existing open-confirmation
  flow. Punctuation-insensitive on both sides (so "Dune Part Two" matches
  "Dune: Part Two"); longest-match-wins; short titles (≤4 chars, e.g. "Dark")
  require a cue verb to avoid colliding with mood words.

## Guardrails / lessons

- **Never edit `frontend/src/data/catalog.js` by hand.** Change `seed.py`, then run
  `python scripts/export_catalog.py` and commit the regenerated file.
- The export script's integrity check is the canary: if a future catalog edit
  orphans a mood/graph reference, the build step fails loudly instead of shipping
  a silently broken demo.
- Any catalog refactor must update *all three* reference sites together: catalog
  entries, mood matcher suggestion IDs, and graph relationship pairs.

## Follow-ups (not yet done)

- **v2:** Replace the client-side mock mood table with live `/v1/search` calls so
  the 18-bucket hardcoded matcher is retired entirely and the API is the runtime
  source of truth (keep the static export as offline-demo fallback).
- **v2:** Fuzzy title matching (Levenshtein / token overlap) to absorb
  speech-to-text drift ("after sun", "passed lives").
- Remove abandoned Fly.io artifacts (`Dockerfile.fly`, `fly.toml`) — dead weight
  since the Railway migration.
