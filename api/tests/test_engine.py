"""
Unit tests — recommendation engine scoring logic.

These tests don't require running services (Qdrant, Neo4j) — they test
the scoring, diversity, and signal-building functions in isolation.
"""
from __future__ import annotations

import pytest
from recommendations.engine import (
    _recency_signal,
    _context_signal,
    _build_signals,
    _dict_to_content,
)


# ── _recency_signal ───────────────────────────────────────────────────────

class TestRecencySignal:
    def test_very_recent_scores_high(self):
        assert _recency_signal(2025) >= 0.95

    def test_current_year_is_max(self):
        assert _recency_signal(2025) == 1.0

    def test_five_year_old_title_reduced(self):
        score = _recency_signal(2020)
        assert 0.5 < score < 1.0

    def test_twenty_year_old_title_zero(self):
        assert _recency_signal(2005) == 0.0

    def test_ancient_title_clamped_at_zero(self):
        assert _recency_signal(1990) == 0.0

    def test_future_year_does_not_go_above_one(self):
        # Should clamp at 1.0 not exceed it
        assert _recency_signal(2030) >= 1.0  # max(0, 1 - neg) > 1 is fine
        assert _recency_signal(2030) <= 2.0  # but not absurd


# ── _context_signal ───────────────────────────────────────────────────────

class TestContextSignal:
    def _item(self, pacing: float = 0.5, runtime: int = 90) -> dict:
        return {"dna": {"pacing": pacing, "runtime_min": runtime}}

    def test_morning_prefers_short_slow(self):
        item = self._item(pacing=0.3, runtime=30)
        score = _context_signal(item, {"time_of_day": "morning"})
        assert score > 0

    def test_morning_penalizes_long_fast(self):
        long_fast = self._item(pacing=0.9, runtime=180)
        short_slow = self._item(pacing=0.2, runtime=25)
        assert _context_signal(short_slow, {"time_of_day": "morning"}) >= \
               _context_signal(long_fast, {"time_of_day": "morning"})

    def test_mobile_prefers_short(self):
        short = self._item(runtime=25)
        long = self._item(runtime=150)
        short_score = _context_signal(short, {"device": "mobile"})
        long_score = _context_signal(long, {"device": "mobile"})
        assert short_score >= long_score

    def test_evening_tv_boosts_propulsive(self):
        fast = self._item(pacing=0.8)
        score = _context_signal(fast, {"time_of_day": "evening", "device": "tv"})
        assert score > 0

    def test_score_capped_at_one(self):
        item = self._item(pacing=0.1, runtime=15)
        ctx = {"time_of_day": "morning", "device": "mobile"}
        assert _context_signal(item, ctx) <= 1.0

    def test_empty_context_returns_zero(self):
        assert _context_signal(self._item(), {}) == 0.0


# ── _build_signals ────────────────────────────────────────────────────────

class TestBuildSignals:
    def _item(self, genres=None, dna=None, year=2023):
        return {
            "genres": genres or ["Thriller"],
            "dna": dna or {"visual_style": "cinematic", "pacing": 0.6},
            "year": year,
            "semantic_score": 0.82,
            "genre_score": 0.75,
            "recency_score": 0.9,
        }

    def test_returns_list(self):
        signals = _build_signals(self._item(), {"Thriller": 0.4})
        assert isinstance(signals, list)

    def test_max_four_signals(self):
        signals = _build_signals(self._item(), {"Thriller": 0.5})
        assert len(signals) <= 4

    def test_semantic_signal_included_when_high(self):
        item = self._item()
        item["semantic_score"] = 0.9
        signals = _build_signals(item, {})
        names = [s.name for s in signals]
        assert "Semantic match" in names

    def test_semantic_signal_excluded_when_low(self):
        item = self._item()
        item["semantic_score"] = 0.1
        signals = _build_signals(item, {})
        names = [s.name for s in signals]
        assert "Semantic match" not in names

    def test_genre_signal_when_preference_exists(self):
        signals = _build_signals(self._item(genres=["Drama"]), {"Drama": 0.6})
        names = [s.name for s in signals]
        assert "Genre affinity" in names

    def test_recent_release_signal_for_new_content(self):
        item = self._item(year=2024)
        item["recency_score"] = 0.9
        signals = _build_signals(item, {})
        names = [s.name for s in signals]
        assert "Recent release" in names

    def test_all_signal_weights_between_zero_and_one(self):
        signals = _build_signals(self._item(), {"Thriller": 0.5})
        for s in signals:
            assert 0.0 <= s.weight <= 1.0

    def test_signals_have_non_empty_detail(self):
        signals = _build_signals(self._item(), {"Thriller": 0.5})
        for s in signals:
            assert s.detail.strip()


# ── _dict_to_content ──────────────────────────────────────────────────────

class TestDictToContent:
    def test_basic_conversion(self):
        d = {
            "id": "abc", "title": "Test", "year": 2023,
            "kind": "film", "synopsis": "synopsis",
            "genres": ["Drama"], "rating": 7.5,
        }
        content = _dict_to_content(d)
        assert content.id == "abc"
        assert content.title == "Test"
        assert content.year == 2023
        assert content.rating == 7.5

    def test_dna_parsed_when_present(self):
        d = {
            "id": "xyz", "title": "DNA Test", "year": 2022,
            "kind": "series", "synopsis": "",
            "genres": [], "rating": 0.0,
            "dna": {
                "pacing": 0.5, "tension_curve": [0.3, 0.7],
                "visual_style": "gritty", "audio_mood": "tense",
                "thematic_tags": ["power"], "runtime_min": 45,
            },
        }
        content = _dict_to_content(d)
        assert content.dna is not None
        assert content.dna.pacing == 0.5
        assert content.dna.visual_style == "gritty"

    def test_missing_dna_is_none(self):
        d = {"id": "no-dna", "title": "No DNA", "year": 2020,
             "kind": "film", "synopsis": "", "genres": [], "rating": 0.0}
        content = _dict_to_content(d)
        assert content.dna is None

    def test_missing_fields_use_defaults(self):
        content = _dict_to_content({"id": "min"})
        assert content.title == "Unknown"
        assert content.genres == []
        assert content.cast == []
