#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  NEXUS Platform — Single-Command Installer                       ║
# ║  curl -sSL https://raw.githubusercontent.com/dcash10181-gh/     ║
# ║       nexus-platform/main/install.sh | bash                      ║
# ╚══════════════════════════════════════════════════════════════════╝
set -euo pipefail

CYAN='\033[0;36m'; WHITE='\033[1;37m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

REPO="https://github.com/dcash10181-gh/nexus-platform"
TARGET_DIR="${NEXUS_DIR:-$HOME/nexus-platform}"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${WHITE}  N E X U S  Platform  v1.1              ${CYAN}║${NC}"
echo -e "${CYAN}║${WHITE}  AI-Native Video Orchestration           ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Prerequisites ────────────────────────────────────────────────────
echo -e "${WHITE}Checking prerequisites...${NC}"

check_cmd() {
  if command -v "$1" &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} $1"
  else
    echo -e "  ${RED}✗ $1 not found${NC}"
    case $1 in
      docker) echo -e "    Install Docker Desktop: https://docs.docker.com/get-docker/" ;;
      git)    echo -e "    Install git: https://git-scm.com/downloads" ;;
    esac
    exit 1
  fi
}

check_cmd docker
check_cmd git

# Check Docker is running
if ! docker info &>/dev/null 2>&1; then
  echo -e "${RED}✗ Docker is not running. Start Docker Desktop and try again.${NC}"
  exit 1
fi
echo -e "  ${GREEN}✓${NC} Docker is running"

# ── Clone or update ──────────────────────────────────────────────────
echo ""
if [ -d "$TARGET_DIR/.git" ]; then
  echo -e "${WHITE}Updating existing install at ${TARGET_DIR}...${NC}"
  git -C "$TARGET_DIR" pull --quiet
else
  echo -e "${WHITE}Installing NEXUS to ${TARGET_DIR}...${NC}"
  git clone --depth=1 "$REPO" "$TARGET_DIR"
fi
cd "$TARGET_DIR"

# ── Environment setup ────────────────────────────────────────────────
if [ ! -f .env ]; then
  cp .env.example .env
  echo -e "${GREEN}✓${NC} Created .env with default settings"
fi

# ── Start the stack ──────────────────────────────────────────────────
echo ""
echo -e "${WHITE}Starting NEXUS...${NC}"
echo -e "  Services: API · Vector DB · Knowledge Graph · Frontend"
echo ""

docker compose pull --quiet 2>/dev/null || true
docker compose up -d --build

# ── Wait for API ─────────────────────────────────────────────────────
echo ""
echo -e "${WHITE}Waiting for services to start (this takes ~2 minutes on first run)...${NC}"
printf "  "

MAX_WAIT=180
waited=0
until curl -sf http://localhost:8000/health >/dev/null 2>&1; do
  if [ $waited -ge $MAX_WAIT ]; then
    echo ""
    echo -e "${RED}✗ Timed out. Check logs: docker compose logs api${NC}"
    exit 1
  fi
  printf "."
  sleep 5
  waited=$((waited + 5))
done

echo ""
echo -e "  ${GREEN}✓${NC} API is ready"

# ── Seed catalog ─────────────────────────────────────────────────────
echo -e "${WHITE}Loading content catalog...${NC}"
docker compose run --rm seeder 2>/dev/null && \
  echo -e "  ${GREEN}✓${NC} Catalog loaded" || \
  echo -e "  ${YELLOW}⚠  Catalog seeder skipped (may already be seeded)${NC}"

# ── Done ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  NEXUS is running!                            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${WHITE}Open in browser:${NC}    http://localhost:3000"
echo -e "  ${WHITE}API docs:${NC}           http://localhost:8000/docs"
echo -e "  ${WHITE}Neo4j browser:${NC}      http://localhost:7474"
echo ""
echo -e "  ${CYAN}No API keys required. Runs entirely on your machine.${NC}"
echo ""
echo -e "  ${YELLOW}To stop:${NC}  docker compose down"
echo -e "  ${YELLOW}To start again:${NC}  docker compose up -d"
echo ""

# Open browser if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  sleep 2
  open http://localhost:3000 2>/dev/null || true
fi
