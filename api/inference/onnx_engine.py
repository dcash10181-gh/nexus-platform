"""
ONNX Inference Engine — on-device / privacy-preserving personalization.

NEXUS's Federated Privacy Mode runs a quantized ONNX model that:
  1. Embeds user preference signals locally (client-side or edge device)
  2. Scores a candidate list without sending raw behavioral data to the server
  3. Merges server-side semantic scores with local preference scores

The flow:
  server: retrieves candidate pool (titles only, no user data sent)
  client: scores candidates against local ONNX preference model
  client: returns ranked list (never sends raw history to server)

This implements a lightweight version of federated recommendations:
  - No raw watch history leaves the device
  - Model weights are updated via differential privacy (planned v1.1)
  - Works offline for cached catalogs
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

log = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).parent / "models" / "nexus_preference_v1.onnx"
SCALER_PATH = Path(__file__).parent / "models" / "scaler_params.npz"

FEATURE_DIM = 8  # [pacing, tension_mean, tension_std, visual_enc, audio_enc, recency, genre_match, completion_rate]


class ONNXPreferenceScorer:
    """
    Scores content candidates using a user's local preference profile.

    The model is a lightweight MLP (3 layers, 64→32→1) trained on
    aggregated behavioral patterns. Quantized INT8 for <2ms per candidate.

    When the ONNX model file is unavailable (first run, development),
    falls back to a rule-based scorer with identical interface.
    """

    def __init__(self):
        self._session = None
        self._fallback = True
        self._load_model()

    def _load_model(self):
        if not MODEL_PATH.exists():
            log.info(
                "ONNX model not found at %s — using rule-based fallback scorer. "
                "Run `python -m inference.train` to generate the model.",
                MODEL_PATH,
            )
            return

        try:
            import onnxruntime as ort  # type: ignore
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 2
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            self._session = ort.InferenceSession(
                str(MODEL_PATH),
                sess_options=opts,
                providers=["CPUExecutionProvider"],
            )
            self._fallback = False
            log.info("ONNX preference model loaded: %s", MODEL_PATH)
        except ImportError:
            log.warning("onnxruntime not installed — pip install onnxruntime for on-device inference")
        except Exception as e:
            log.error("ONNX load error: %s — using fallback", e)

    def score_batch(
        self,
        candidates: list[dict],
        user_profile: dict,
    ) -> list[float]:
        """
        Score a list of content candidates against a user preference profile.

        Args:
            candidates: list of content dicts with 'dna', 'genres', 'year'
            user_profile: {genre_weights, avg_pacing_pref, completion_rate}

        Returns:
            list of float scores (0..1) aligned with candidates
        """
        features = np.array(
            [self._extract_features(c, user_profile) for c in candidates],
            dtype=np.float32,
        )

        if self._session is not None:
            inputs = {self._session.get_inputs()[0].name: features}
            outputs = self._session.run(None, inputs)
            scores = outputs[0].flatten().tolist()
        else:
            scores = self._rule_based_score(features, user_profile)

        return scores

    def _extract_features(self, item: dict, profile: dict) -> list[float]:
        """Extract fixed-dim feature vector from content item + user profile."""
        dna = item.get("dna") or {}
        genres = item.get("genres", [])
        year = item.get("year", 2000)
        genre_weights = profile.get("genre_weights", {})

        pacing = dna.get("pacing", 0.5)
        curve = dna.get("tension_curve", [0.5])
        tension_mean = float(np.mean(curve))
        tension_std = float(np.std(curve)) if len(curve) > 1 else 0.0

        # Encode visual style as numeric (simple hash → 0..1)
        vs = dna.get("visual_style", "")
        visual_enc = (hash(vs) % 100) / 100.0

        # Encode audio mood
        am = dna.get("audio_mood", "")
        audio_enc = (hash(am) % 100) / 100.0

        # Recency
        recency = max(0.0, 1.0 - (2025 - year) / 20.0)

        # Genre match (dot product of item genres with user preferences)
        genre_match = min(1.0, sum(genre_weights.get(g, 0.0) for g in genres))

        # Completion rate alignment
        completion_rate = profile.get("completion_rate", 0.7)

        return [pacing, tension_mean, tension_std, visual_enc, audio_enc,
                recency, genre_match, completion_rate]

    def _rule_based_score(self, features: np.ndarray, profile: dict) -> list[float]:
        """
        Simple rule-based scorer — used when ONNX model is unavailable.
        Weights: genre_match > tension_mean > recency > pacing alignment.
        """
        scores = []
        avg_pacing = profile.get("avg_pacing_pref", 0.5)

        for feat in features:
            pacing, t_mean, t_std, vis, aud, recency, genre_match, comp = feat
            pacing_align = 1.0 - abs(pacing - avg_pacing)
            score = (
                0.40 * genre_match
                + 0.20 * t_mean
                + 0.15 * recency
                + 0.15 * pacing_align
                + 0.10 * comp
            )
            scores.append(float(np.clip(score, 0.0, 1.0)))

        return scores


@lru_cache
def get_onnx_scorer() -> ONNXPreferenceScorer:
    return ONNXPreferenceScorer()


# ── Federated scoring endpoint helper ────────────────────────────────────

async def federated_score(
    candidates: list[dict],
    user_profile: dict,
) -> list[dict]:
    """
    Score candidates using the on-device ONNX model and merge with server scores.

    In production this is called client-side via WASM. On the server it provides
    the same scoring for API clients that opt into the federated mode.
    """
    scorer = get_onnx_scorer()
    local_scores = scorer.score_batch(candidates, user_profile)

    results = []
    for item, local_score in zip(candidates, local_scores):
        server_score = item.get("score", 0.5)
        # Blend: 50% server semantic score, 50% local preference score
        blended = 0.5 * server_score + 0.5 * local_score
        results.append({**item, "score": round(blended, 4), "local_score": round(local_score, 4)})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
