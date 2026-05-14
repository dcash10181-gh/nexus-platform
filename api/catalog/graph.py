"""
Knowledge graph — Neo4j integration.

Models content as a rich entity graph:
  (Content) -[:HAS_GENRE]->  (Genre)
  (Content) -[:FEATURES]->   (Person)   # cast & crew
  (Content) -[:EXPLORES]->   (Theme)
  (Content) -[:SIMILAR_TO]-> (Content)  # LLM-inferred
  (User)    -[:WATCHED]->     (Content) {completed, rating, timestamp}
  (User)    -[:PREFERS]->     (Genre | Theme)

The graph powers:
  - "Because you watched X" explanations
  - Cold-start via theme/director paths (SemanticGNN-style)
  - Social signals when friend-graph is enabled
"""
from __future__ import annotations

import logging
from functools import lru_cache

from neo4j import AsyncGraphDatabase, AsyncDriver

from config import get_settings

log = logging.getLogger(__name__)


class KnowledgeGraph:
    def __init__(self, uri: str, user: str, password: str):
        self._driver: AsyncDriver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self._driver.close()

    # ── Schema bootstrap ─────────────────────────────────────────────────

    async def ensure_schema(self) -> None:
        async with self._driver.session() as s:
            # Constraints
            await s.run("CREATE CONSTRAINT content_id IF NOT EXISTS FOR (c:Content) REQUIRE c.id IS UNIQUE")
            await s.run("CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
            await s.run("CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE")
            await s.run("CREATE CONSTRAINT theme_name IF NOT EXISTS FOR (t:Theme) REQUIRE t.name IS UNIQUE")
            await s.run("CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE")
            # Indexes
            await s.run("CREATE INDEX content_title IF NOT EXISTS FOR (c:Content) ON (c.title)")
            await s.run("CREATE INDEX content_year IF NOT EXISTS FOR (c:Content) ON (c.year)")
        log.info("Neo4j schema ensured")

    # ── Content ingestion ────────────────────────────────────────────────

    async def upsert_content(self, items: list[dict]) -> None:
        async with self._driver.session() as s:
            for item in items:
                await s.run(
                    """
                    MERGE (c:Content {id: $id})
                    SET c.title = $title, c.year = $year, c.kind = $kind,
                        c.rating = $rating, c.poster_url = $poster_url,
                        c.backdrop_url = $backdrop_url, c.synopsis = $synopsis
                    WITH c
                    FOREACH (g IN $genres |
                        MERGE (gn:Genre {name: g})
                        MERGE (c)-[:HAS_GENRE]->(gn)
                    )
                    WITH c
                    FOREACH (t IN $themes |
                        MERGE (th:Theme {name: t})
                        MERGE (c)-[:EXPLORES]->(th)
                    )
                    WITH c
                    FOREACH (p IN $cast |
                        MERGE (pe:Person {name: p})
                        MERGE (c)-[:FEATURES]->(pe)
                    )
                    """,
                    id=item["id"],
                    title=item["title"],
                    year=item.get("year", 0),
                    kind=item.get("kind", "film"),
                    rating=item.get("rating", 0.0),
                    poster_url=item.get("poster_url", ""),
                    backdrop_url=item.get("backdrop_url", ""),
                    synopsis=item.get("synopsis", ""),
                    genres=item.get("genres", []),
                    themes=item.get("dna", {}).get("thematic_tags", []) if item.get("dna") else [],
                    cast=item.get("cast", []),
                )
        log.info("Upserted %d items into knowledge graph", len(items))

    # ── User activity tracking ───────────────────────────────────────────

    async def record_watch(
        self,
        user_id: str,
        content_id: str,
        completed: bool,
        rating: float | None = None,
    ) -> None:
        async with self._driver.session() as s:
            await s.run(
                """
                MERGE (u:User {id: $uid})
                MERGE (c:Content {id: $cid})
                MERGE (u)-[r:WATCHED]->(c)
                SET r.completed = $completed,
                    r.rating = $rating,
                    r.ts = timestamp()
                WITH u, c
                FOREACH (g IN [(c)-[:HAS_GENRE]->(gn) | gn.name] |
                    MERGE (gn:Genre {name: g})
                    MERGE (u)-[p:PREFERS]->(gn)
                    ON CREATE SET p.weight = 1
                    ON MATCH  SET p.weight = p.weight + (CASE WHEN $completed THEN 1 ELSE 0.3 END)
                )
                """,
                uid=user_id,
                cid=content_id,
                completed=completed,
                rating=rating or 0.0,
            )

    # ── Recommendation signals ───────────────────────────────────────────

    async def get_user_genre_weights(self, user_id: str) -> dict[str, float]:
        async with self._driver.session() as s:
            result = await s.run(
                """
                MATCH (u:User {id: $uid})-[p:PREFERS]->(g:Genre)
                RETURN g.name AS genre, p.weight AS weight
                ORDER BY weight DESC LIMIT 20
                """,
                uid=user_id,
            )
            records = await result.data()
            total = sum(r["weight"] for r in records) or 1.0
            return {r["genre"]: r["weight"] / total for r in records}

    async def get_watch_history(self, user_id: str, limit: int = 50) -> list[str]:
        async with self._driver.session() as s:
            result = await s.run(
                """
                MATCH (u:User {id: $uid})-[r:WATCHED]->(c:Content)
                RETURN c.id AS id ORDER BY r.ts DESC LIMIT $limit
                """,
                uid=user_id,
                limit=limit,
            )
            records = await result.data()
            return [r["id"] for r in records]

    async def get_because_you_watched(self, content_id: str, limit: int = 10) -> list[dict]:
        """Shared-genre + shared-theme paths from a seed title."""
        async with self._driver.session() as s:
            result = await s.run(
                """
                MATCH (seed:Content {id: $cid})-[:HAS_GENRE|EXPLORES]->(node)
                      <-[:HAS_GENRE|EXPLORES]-(rec:Content)
                WHERE rec.id <> $cid
                WITH rec, count(node) AS shared
                RETURN rec.id AS id, rec.title AS title, shared
                ORDER BY shared DESC LIMIT $limit
                """,
                cid=content_id,
                limit=limit,
            )
            return await result.data()

    async def get_director_filmography(self, director: str) -> list[dict]:
        async with self._driver.session() as s:
            result = await s.run(
                """
                MATCH (p:Person {name: $director})<-[:FEATURES]-(c:Content)
                RETURN c.id AS id, c.title AS title, c.year AS year
                ORDER BY c.year DESC
                """,
                director=director,
            )
            return await result.data()

    async def create_similarity_edge(self, id_a: str, id_b: str, score: float) -> None:
        async with self._driver.session() as s:
            await s.run(
                """
                MATCH (a:Content {id: $a}), (b:Content {id: $b})
                MERGE (a)-[r:SIMILAR_TO]->(b)
                SET r.score = $score
                """,
                a=id_a,
                b=id_b,
                score=score,
            )

    async def get_content_by_id(self, content_id: str) -> dict | None:
        async with self._driver.session() as s:
            result = await s.run(
                """
                MATCH (c:Content {id: $cid})
                OPTIONAL MATCH (c)-[:HAS_GENRE]->(g:Genre)
                OPTIONAL MATCH (c)-[:FEATURES]->(p:Person)
                OPTIONAL MATCH (c)-[:EXPLORES]->(t:Theme)
                RETURN c,
                       collect(DISTINCT g.name) AS genres,
                       collect(DISTINCT p.name) AS cast,
                       collect(DISTINCT t.name) AS themes
                """,
                cid=content_id,
            )
            record = await result.single()
            if not record:
                return None
            node = dict(record["c"])
            node["genres"] = record["genres"]
            node["cast"] = record["cast"]
            node["themes"] = record["themes"]
            return node

    async def graph_stats(self) -> dict:
        async with self._driver.session() as s:
            result = await s.run(
                """
                MATCH (c:Content) WITH count(c) AS content_count
                MATCH (u:User)    WITH content_count, count(u) AS user_count
                MATCH ()-[r:WATCHED]->() WITH content_count, user_count, count(r) AS watch_count
                RETURN content_count, user_count, watch_count
                """
            )
            record = await result.single()
            if record:
                return dict(record)
            return {"content_count": 0, "user_count": 0, "watch_count": 0}


@lru_cache
def get_graph() -> KnowledgeGraph:
    s = get_settings()
    return KnowledgeGraph(
        uri=s.neo4j_uri,
        user=s.neo4j_user,
        password=s.neo4j_password,
    )
