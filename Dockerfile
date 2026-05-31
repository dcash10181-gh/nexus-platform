# NEXUS single-service deploy (Railway): build the frontend, then serve it
# from the FastAPI app alongside the API. One container, one public URL.
#
# Stage 1 — build the React frontend
FROM node:20-slim AS frontend
WORKDIR /fe
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
# Baked in at build time so the SPA can authenticate to the chat endpoint.
ARG VITE_NEXUS_DEMO_KEY
ENV VITE_NEXUS_DEMO_KEY=$VITE_NEXUS_DEMO_KEY
RUN npm run build

# Stage 2 — Python API image that also serves the built SPA
FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
 && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model so the first request is fast
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY api/ .
COPY --from=frontend /fe/dist /app/static

ENV SERVE_FRONTEND=true
ENV FRONTEND_DIST=/app/static
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
