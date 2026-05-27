
---

## 10. Docker Compose Startup Issues

### Neo4j fails health check on first boot

**Symptom:**
```
✘ Container nexus-api   Error dependency neo4j failed to start
dependency failed to start: container nexus-neo4j is unhealthy
```

**Root cause:** Neo4j takes 60–90 seconds to initialize on first boot. The default health check start_period was too short.

**Fix — docker-compose.yml:**
```yaml
neo4j:
  healthcheck:
    interval: 15s
    timeout: 10s
    retries: 20
    start_period: 90s

api:
  depends_on:
    neo4j:
      condition: service_started   # not service_healthy
```

### API crashes if Neo4j isn't ready at startup

**Symptom:** `ValueError: Cannot resolve address neo4j:7687` then `Application startup failed. Exiting.`

**Fix — wrap graph init in main.py lifespan:**
```python
try:
    await get_graph().ensure_schema()
    log.info("nexus.graph.ready")
except Exception as e:
    log.warning("nexus.graph.unavailable", error=str(e))
    # Do not raise — API starts without graph
```

### Docker using cached image after code change

**Fix:** Always `--build` when code has changed:
```bash
docker compose down && docker compose up -d --build
```

### Confirmed working startup

```
✔ Container nexus-neo4j     Started     0.3s
✔ Container nexus-qdrant    Healthy     5.8s
✔ Container nexus-api       Healthy    11.3s
✔ Container nexus-frontend  Started    11.3s
✔ Container nexus-seeder    Started    11.3s
```
