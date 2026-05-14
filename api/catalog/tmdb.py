"""
TMDB (The Movie Database) client — fetch real metadata and poster artwork
for the content catalog.

Requires: TMDB_API_KEY in .env (free at developers.themoviedb.org)

Used by the seeder to enrich catalog entries with:
  - Official poster and backdrop images
  - Cast lists from credits endpoint
  - Real synopsis and genre data
  - Runtime and release year

Falls back to stub data when the API key is absent (demo/trial mode).
"""
from __future__ import annotations

import asyncio
import logging
from functools import lru_cache

import httpx

log = logging.getLogger(__name__)

TMDB_BASE    = "https://api.themoviedb.org/3"
TMDB_IMG_500 = "https://image.tmdb.org/t/p/w500"
TMDB_IMG_ORI = "https://image.tmdb.org/t/p/original"


class TMDBClient:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._http = httpx.AsyncClient(
            base_url=TMDB_BASE,
            params={"api_key": api_key},
            timeout=10.0,
        )

    async def close(self):
        await self._http.aclose()

    # ── Search ────────────────────────────────────────────────────────────

    async def search_movie(self, title: str, year: int | None = None) -> dict | None:
        params = {"query": title, "language": "en-US", "page": 1}
        if year:
            params["primary_release_year"] = year
        r = await self._http.get("/search/movie", params=params)
        r.raise_for_status()
        results = r.json().get("results", [])
        return results[0] if results else None

    async def search_tv(self, title: str, year: int | None = None) -> dict | None:
        params = {"query": title, "language": "en-US", "page": 1}
        if year:
            params["first_air_date_year"] = year
        r = await self._http.get("/search/tv", params=params)
        r.raise_for_status()
        results = r.json().get("results", [])
        return results[0] if results else None

    # ── Details ───────────────────────────────────────────────────────────

    async def get_movie_details(self, tmdb_id: int) -> dict:
        r = await self._http.get(f"/movie/{tmdb_id}", params={"append_to_response": "credits"})
        r.raise_for_status()
        return r.json()

    async def get_tv_details(self, tmdb_id: int) -> dict:
        r = await self._http.get(f"/tv/{tmdb_id}", params={"append_to_response": "credits,external_ids"})
        r.raise_for_status()
        return r.json()

    # ── Enrichment ────────────────────────────────────────────────────────

    async def enrich_catalog_item(self, item: dict) -> dict:
        """
        Fetch real TMDB data for a catalog item and merge it in.
        Returns the enriched item; falls back silently if TMDB call fails.
        """
        title = item["title"]
        year = item.get("year")
        kind = item.get("kind", "film")

        try:
            if kind in ("film",):
                result = await self.search_movie(title, year)
                if result:
                    tmdb_id = result["id"]
                    details = await self.get_movie_details(tmdb_id)
                    return _merge_movie(item, details)

            else:  # series / limited / live
                result = await self.search_tv(title, year)
                if result:
                    tmdb_id = result["id"]
                    details = await self.get_tv_details(tmdb_id)
                    return _merge_tv(item, details)

        except Exception as e:
            log.warning("TMDB enrichment failed for '%s': %s", title, e)

        return item  # Return original on failure

    async def enrich_catalog(self, items: list[dict], concurrency: int = 5) -> list[dict]:
        """Enrich a list of catalog items with limited concurrency."""
        sem = asyncio.Semaphore(concurrency)

        async def _enrich(item: dict) -> dict:
            async with sem:
                return await self.enrich_catalog_item(item)

        results = await asyncio.gather(*[_enrich(i) for i in items])
        log.info("TMDB enrichment complete: %d/%d items updated", len(results), len(items))
        return list(results)


# ── Merge helpers ─────────────────────────────────────────────────────────

GENRE_MAP = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Sci-Fi", 10770: "TV Movie",
    53: "Thriller", 10752: "War", 37: "Western",
    # TV
    10759: "Action", 10762: "Kids", 10763: "News",
    10764: "Reality", 10765: "Sci-Fi", 10766: "Soap",
    10767: "Talk", 10768: "War",
}


def _poster_url(path: str | None) -> str:
    return f"{TMDB_IMG_500}{path}" if path else ""


def _backdrop_url(path: str | None) -> str:
    return f"{TMDB_IMG_ORI}{path}" if path else ""


def _top_cast(credits: dict, n: int = 5) -> list[str]:
    cast = credits.get("cast", [])
    return [c["name"] for c in cast[:n] if c.get("name")]


def _director(credits: dict) -> str | None:
    crew = credits.get("crew", [])
    directors = [c["name"] for c in crew if c.get("job") == "Director"]
    return directors[0] if directors else None


def _merge_movie(item: dict, details: dict) -> dict:
    enriched = dict(item)
    genres = [GENRE_MAP.get(g["id"], g["name"]) for g in details.get("genres", [])]
    credits = details.get("credits", {})
    enriched.update({
        "synopsis":     details.get("overview") or item.get("synopsis", ""),
        "genres":       genres or item.get("genres", []),
        "cast":         _top_cast(credits) or item.get("cast", []),
        "director":     _director(credits) or item.get("director"),
        "rating":       round(details.get("vote_average", item.get("rating", 0.0)), 1),
        "poster_url":   _poster_url(details.get("poster_path")) or item.get("poster_url", ""),
        "backdrop_url": _backdrop_url(details.get("backdrop_path")) or item.get("backdrop_url", ""),
        "year":         int(details.get("release_date", "")[:4] or item.get("year", 0)),
        "tmdb_id":      details.get("id"),
    })
    if item.get("dna"):
        enriched["dna"] = dict(item["dna"])
        enriched["dna"]["runtime_min"] = details.get("runtime") or item["dna"].get("runtime_min", 90)
    return enriched


def _merge_tv(item: dict, details: dict) -> dict:
    enriched = dict(item)
    genres = [GENRE_MAP.get(g["id"], g["name"]) for g in details.get("genres", [])]
    credits = details.get("credits", {})
    enriched.update({
        "synopsis":     details.get("overview") or item.get("synopsis", ""),
        "genres":       genres or item.get("genres", []),
        "cast":         _top_cast(credits) or item.get("cast", []),
        "rating":       round(details.get("vote_average", item.get("rating", 0.0)), 1),
        "poster_url":   _poster_url(details.get("poster_path")) or item.get("poster_url", ""),
        "backdrop_url": _backdrop_url(details.get("backdrop_path")) or item.get("backdrop_url", ""),
        "year":         int((details.get("first_air_date") or "")[:4] or item.get("year", 0)),
        "tmdb_id":      details.get("id"),
    })
    if item.get("dna"):
        ep_runtime = details.get("episode_run_time", [])
        enriched["dna"] = dict(item["dna"])
        if ep_runtime:
            enriched["dna"]["runtime_min"] = ep_runtime[0]
    return enriched


# ── Factory ───────────────────────────────────────────────────────────────

@lru_cache
def get_tmdb_client() -> TMDBClient | None:
    """Returns a TMDBClient if TMDB_API_KEY is set, else None."""
    from config import get_settings
    key = getattr(get_settings(), "tmdb_api_key", "")
    if not key:
        log.info("TMDB_API_KEY not set — catalog will use embedded metadata only")
        return None
    return TMDBClient(key)
