# NEXUS — Persistent Demo Deployment Runbook

**Target:** Hostinger KVM 1 VPS (1 vCPU, 4 GB RAM, 50 GB NVMe) running Ubuntu 24.04 + Docker
**Goal:** A always-on, HTTPS, password-gated demo URL you can send a CTO after a warm meeting
**LLM:** Mock provider (zero cost, deterministic, no API keys)

Legend: commands marked **[MAC]** run in your local terminal; **[VPS]** run on the server over SSH. Everything else is context.

---

## 0. What you need before starting

- A Hostinger account with a **KVM 1 VPS** (or KVM 2 if you bought headroom)
- A domain or subdomain you can edit DNS for (e.g. `demo.yourdomain.com`). HTTPS will not work on a bare IP — Let's Encrypt won't issue certs for raw IPs. If you don't have a domain, see Appendix B.
- Your SSH public key (check with `[MAC] cat ~/.ssh/id_ed25519.pub` — if it errors, run `ssh-keygen -t ed25519` first)

---

## 1. Provision the VPS

In the Hostinger hPanel VPS purchase/setup flow:

1. Plan: **KVM 1**.
2. Location: the data center **closest to your prospects** (latency is visible when a CTO clicks around live).
3. OS / template: choose **Ubuntu 24.04 with Docker** (Hostinger offers a Docker template — pick it so Docker + Compose are preinstalled). If only plain Ubuntu 24.04 is available, that's fine — Section 3 installs Docker.
4. Authentication: **add your SSH public key** during setup rather than a root password. More secure and you skip password prompts.
5. Finish setup and note the server's **public IP**.

---

## 2. First login and basic hardening

```bash
# [MAC] connect as root (Hostinger gives you root on a VPS)
ssh root@YOUR_SERVER_IP
```

Create a non-root user so you're not operating as root day-to-day:

```bash
# [VPS]
adduser nexus               # set a password when prompted
usermod -aG sudo nexus
rsync --archive --chown=nexus:nexus ~/.ssh /home/nexus   # copy your SSH key to the new user
```

Reconnect as the new user and confirm sudo works:

```bash
# [MAC]
ssh nexus@YOUR_SERVER_IP
# [VPS]
sudo whoami        # should print: root
```

Update the system:

```bash
# [VPS]
sudo apt update && sudo apt upgrade -y
```

---

## 3. Confirm (or install) Docker

```bash
# [VPS]
docker --version && docker compose version
```

If both print versions, skip ahead. If `docker` is missing:

```bash
# [VPS] install Docker Engine + Compose plugin
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker            # apply the group now without logging out
docker run --rm hello-world   # verify
```

---

## 4. Get the NEXUS code onto the server

The repo is public, so a plain clone works:

```bash
# [VPS]
cd ~
git clone https://github.com/dcash10181-gh/nexus-platform.git
cd nexus-platform
```

---

## 5. Configure for a production demo

### 5a. Environment file

```bash
# [VPS]
cp .env.example .env
nano .env
```

Confirm these values (defaults should already be right):

```
LLM_PROVIDER=mock
DEMO_MODE=true
```

Leave all API-key fields blank — the mock provider needs none. Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### 5b. Bind internal ports to localhost only — CRITICAL

By default Docker publishes ports on `0.0.0.0` (all interfaces) **and bypasses the `ufw` firewall** via its own iptables rules. If you skip this step, Neo4j, Qdrant, and the raw API are reachable from the public internet regardless of your firewall. Fix it by binding every published port to `127.0.0.1` so only the local reverse proxy can reach them.

```bash
# [VPS]
nano docker-compose.yml
```

For each service that publishes a port, prefix the host side with `127.0.0.1:`. Examples — match whatever ports your file actually uses:

```yaml
    ports:
      - "127.0.0.1:3000:3000"     # frontend
      - "127.0.0.1:8000:8000"     # api
      - "127.0.0.1:6333:6333"     # qdrant
      - "127.0.0.1:7474:7474"     # neo4j browser
      - "127.0.0.1:7687:7687"     # neo4j bolt
```

This still works for local development too (localhost is 127.0.0.1), so it's safe to keep.

### 5c. Production override (memory caps + auto-restart)

On a 4 GB box, Neo4j must be told to stay small or it will trigger the kernel's out-of-memory killer mid-demo. Create an override file that the base compose doesn't touch:

```bash
# [VPS]
nano docker-compose.prod.yml
```

Paste this. **Match the service names to your `docker-compose.yml`** (likely `neo4j`, `qdrant`, `api`, `frontend`, `seeder` — verify with `docker compose config --services`):

```yaml
services:
  neo4j:
    restart: unless-stopped
    environment:
      - NEO4J_server_memory_heap_initial__size=512m
      - NEO4J_server_memory_heap_max__size=512m
      - NEO4J_server_memory_pagecache_size=512m
    deploy:
      resources:
        limits:
          memory: 1500m

  qdrant:
    restart: unless-stopped

  api:
    restart: unless-stopped

  frontend:
    restart: unless-stopped
```

(The double underscores in the Neo4j vars are intentional — Neo4j maps `_` in a setting name to `__` in the env var.)

---

## 6. Add swap (out-of-memory insurance)

Cheap protection so a memory spike pages to disk instead of killing a container:

```bash
# [VPS]
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab   # persists across reboots
free -h                                                       # confirm 2.0Gi swap
```

---

## 7. Bring up the stack

Always pass **both** compose files so the production overrides apply:

```bash
# [VPS]
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Verify the port bindings are localhost-only before going further:

```bash
# [VPS]
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
# In the PORTS column you should see 127.0.0.1:xxxx -> xxxx, NOT 0.0.0.0:xxxx
```

Watch the containers come healthy (Neo4j needs ~90 seconds — this is normal):

```bash
# [VPS]
watch docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
# Ctrl+C once neo4j and api show healthy
```

---

## 8. Seed the catalog

Neo4j must be fully up first (see the 90s note above), or the seeder fails with `Cannot resolve address neo4j`.

```bash
# [VPS]
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm seeder
# Expect: "Seeded 81 vectors" (and graph seeding if Neo4j is ready)
```

If it errors on Neo4j DNS, wait 60 seconds and rerun the same command. If you want titles searchable immediately regardless of Neo4j, the vector-only fallback from your knowledge base also works here.

---

## 9. Put it behind your domain with HTTPS (Caddy)

### 9a. Point DNS at the server

In your domain registrar's DNS settings, add an **A record**:

```
Host: demo      (gives you demo.yourdomain.com)
Type: A
Value: YOUR_SERVER_IP
TTL: default
```

Wait for it to propagate (usually minutes, up to ~30). Confirm:

```bash
# [MAC]
dig +short demo.yourdomain.com    # should return YOUR_SERVER_IP
```

Do not proceed to cert issuance until this resolves, or Let's Encrypt will fail.

### 9b. Install Caddy (automatic HTTPS)

```bash
# [VPS]
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install -y caddy
```

### 9c. Configure the reverse proxy

```bash
# [VPS]
sudo nano /etc/caddy/Caddyfile
```

Replace the contents with (swap in your real subdomain). This routes API calls to the backend and everything else to the frontend; Caddy fetches and renews the TLS cert automatically:

```
demo.yourdomain.com {
    handle /api/* {
        reverse_proxy 127.0.0.1:8000
    }
    handle {
        reverse_proxy 127.0.0.1:3000
    }
}
```

> Port check: confirm your frontend really is on 3000 and API on 8000 with `docker compose ... ps`. If they differ, edit the two port numbers above to match.

Reload Caddy:

```bash
# [VPS]
sudo systemctl reload caddy
sudo systemctl status caddy --no-pager   # should be active (running)
```

---

## 10. Lock down the firewall

Only SSH and web ports are public. The internal services are already localhost-bound (Section 5b), so this closes everything else:

```bash
# [VPS]
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
sudo ufw status            # verify only 22/80/443 are allowed
```

---

## 11. Gate the demo with a password (recommended)

A private demo link should not be publicly crawlable. Add HTTP basic auth at the Caddy layer — one shared credential you hand to the prospect.

Generate a password hash:

```bash
# [VPS]
caddy hash-password --plaintext 'CHOOSE_A_STRONG_PASSWORD'
# copy the long $2a$... hash it prints
```

Edit the Caddyfile to add a `basic_auth` block (newer Caddy uses `basic_auth`; if it rejects that on reload, use `basicauth`):

```
demo.yourdomain.com {
    basic_auth {
        ceo PASTE_THE_HASH_HERE
    }
    handle /api/* {
        reverse_proxy 127.0.0.1:8000
    }
    handle {
        reverse_proxy 127.0.0.1:3000
    }
}
```

```bash
# [VPS]
sudo systemctl reload caddy
```

Now you hand the CTO: the URL, the username `ceo`, and the password you chose. Looks intentional and keeps the demo private.

---

## 12. Verify the demo

```bash
# [MAC] from your laptop, not the server
curl -I https://demo.yourdomain.com        # expect HTTP/2 200 (or 401 if password-gated — that's correct)
```

Then in a browser:

1. Visit `https://demo.yourdomain.com` — padlock should show valid HTTPS.
2. Enter the credential if you set one.
3. Confirm the home page loads with hero + content rows.
4. Open **Ask Nexus**, type "intense crime drama" — confirm a real recommendation (not the Severance fallback) and the yes/no confirmation flow.
5. Click through nav: Series, Films, Browse, Impact — all populate.

---

## 13. Pre-demo checklist (run before every CTO session)

```bash
# [VPS] fresh, healthy state
cd ~/nexus-platform
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart
sleep 90
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps   # all healthy?
free -h                                                              # memory not exhausted?
```

Then do the browser walk-through from Section 12 yourself, end to end, so the first person to hit a cold start is you and not the prospect.

---

## 14. Day-to-day operations

```bash
# [VPS] — all run from ~/nexus-platform

# Tail logs
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Restart everything
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart

# Deploy code updates after you push to GitHub
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm seeder

# Stop the stack (keeps data)
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
```

Tip: create an alias so you stop typing both files every time:

```bash
# [VPS]
echo "alias dc='docker compose -f ~/nexus-platform/docker-compose.yml -f ~/nexus-platform/docker-compose.prod.yml'" >> ~/.bashrc
source ~/.bashrc
# then just: dc ps   /   dc logs -f   /   dc restart
```

---

## 15. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Seeder: `Cannot resolve address neo4j` | Neo4j not finished starting | Wait 60–90s, rerun the seeder command |
| A container keeps restarting; `free -h` shows no free memory | Out-of-memory kill | Confirm the prod override applied (`dc config \| grep -A3 memory`); confirm swap is on; Neo4j heap should be capped at 512m |
| Browser can't reach the site | DNS not propagated, or firewall/Caddy | `dig +short demo.yourdomain.com` returns the IP? `sudo systemctl status caddy`? `sudo ufw status`? |
| HTTPS cert won't issue | DNS wasn't pointing at the box when Caddy tried | Confirm the A record resolves, then `sudo systemctl reload caddy` and check `journalctl -u caddy -n 50` |
| Ask Nexus only returns Severance | Old frontend build cached | Hard-refresh; confirm the latest `AskNexus.jsx` was deployed and the image rebuilt |
| Ports show `0.0.0.0` in `dc ps` | Section 5b not applied | Re-edit `docker-compose.yml` to prefix `127.0.0.1:`, then `dc up -d` |
| Neo4j browser/Bolt reachable from internet | Same as above | Localhost-bind the 7474/7687 ports; they should never be public |

---

## 16. Cost control

- The demo is meant to stay up, so leave it running while a deal is active.
- Watch the renewal: the ~$5/mo intro rate renews higher (~$19.49/mo). Set a calendar reminder before renewal to decide keep-vs-cancel.
- To pause spend entirely between deals, stop the VPS from the Hostinger panel (you lose the running instance; redeploy from this runbook in ~20 minutes when needed). Cheaper to just leave a $5–19/mo box up if your pipeline is active.

---

## Appendix A — Updating the demo after code changes

Your normal loop once this is live:

```
[MAC]  edit code → git commit → git push
[VPS]  cd ~/nexus-platform → git pull → dc up -d --build → dc run --rm seeder
```

## Appendix B — No domain yet

If you don't own a domain, a cheap option is a registrar like Cloudflare or Namecheap (~$10/yr for a `.com`, less for others). You only need one subdomain. Until then you *can* demo over `http://YOUR_SERVER_IP:3000` by temporarily allowing that port in `ufw` and not localhost-binding the frontend — but this has no HTTPS, no password gate, and looks unprofessional, so use it only for your own testing, never for a CTO.

---

*Keep this file in `docs/knowledge-base/`. It is operational, not prospect-facing — do not include it in any materials sent to a customer.*
