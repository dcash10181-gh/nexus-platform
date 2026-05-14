#!/usr/bin/env bash
# ╔═══════════════════════════════════════════════════════════════╗
# ║  NEXUS Platform — Single-Command Installer                    ║
# ║  curl -sSL https://get.nexus.ai | bash                        ║
# ╚═══════════════════════════════════════════════════════════════╝
set -euo pipefail

CYAN='\033[0;36m'; WHITE='\033[1;37m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

REPO="https://github.com/duanecash/nexus-platform"

echo ""
echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${WHITE}  N E X U S  Platform  v1.0.0          ${CYAN}║${NC}"
echo -e "${CYAN}║${WHITE}  AI-Native Video Orchestration         ${CYAN}║${NC}"
echo -e "${CYAN}║  Architect: Duane Cash                 ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

check_cmd() {
  if ! command -v "$1" &>/dev/null; then
    echo -e "${RED}✗ $1 not found. Please install $1 and retry.${NC}"; exit 1
  fi
  echo -e "${GREEN}✓ $1${NC}"
}

check_cmd docker; check_cmd git; check_cmd curl

TARGET_DIR="${NEXUS_DIR:-$HOME/nexus-platform}"
if [ -d "$TARGET_DIR/.git" ]; then
  echo -e "${YELLOW}» Updating existing install at ${TARGET_DIR}...${NC}"
  git -C "$TARGET_DIR" pull --quiet
else
  echo -e "${WHITE}» Cloning NEXUS to ${TARGET_DIR}...${NC}"
  git clone --depth=1 "$REPO" "$TARGET_DIR"
fi
cd "$TARGET_DIR"

[ -f .env ] || cp .env.example .env

echo -e "${WHITE}» Building and starting NEXUS stack...${NC}"
docker compose build --quiet
docker compose up -d --remove-orphans

echo -e "${WHITE}» Waiting for API...${NC}"
MAX_WAIT=120; waited=0
until curl -sf http://localhost:8000/health >/dev/null 2>&1; do
  [ $waited -ge $MAX_WAIT ] && { echo -e "${RED}✗ Timeout${NC}"; exit 1; }
  printf "."; sleep 3; waited=$((waited+3))
done
echo ""

docker compose run --rm seeder 2>/dev/null || true

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  NEXUS is live!                           ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo -e "  ${WHITE}Frontend:${NC}  http://localhost:3000"
echo -e "  ${WHITE}API Docs:${NC}  http://localhost:8000/docs"
echo ""
