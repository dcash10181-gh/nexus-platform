# Environment Setup & Runtime Troubleshooting

> **Read this before running anything in this repo.** Every "it doesn't work on
> my machine" incident in this project's history has had the same root cause: a
> stale or wrong-version language runtime shadowing the correct one on `PATH`.
> CI pins the correct runtimes; your local shell does not unless you set it up.

---

## Required runtimes (non-negotiable)

| Tool   | Required version | Why this exact version |
|--------|------------------|------------------------|
| Python | **3.12** (not 3.13+, not 3.11) | 3.13+ breaks `pydantic-core` via PyO3 ABI incompatibility. The whole API depends on pydantic 2.9.x. |
| Node   | **20** (≥18 minimum) | Vite 5 and Vitest 4 require Node 18+. Anything older (e.g. a stray Node 8) cannot parse ESM `import` and fails on every command. |

These are pinned in the repo:
- `.python-version` (root) → `3.12` — read by `pyenv`.
- `.nvmrc` (root) → `20` — read by `nvm use`.
- `frontend/package.json` `engines` field → enforces Node ≥18 on install.

---

## First-time setup

### 1. Install version managers (once per machine)

Do **not** install language runtimes as raw binaries into `/usr/local/bin`.
That is how this machine accumulated Python 2.7, 3.4, 3.5, 3.14 and a Node 8 all
shadowing each other. Use managers that put a single shimmed version first on
`PATH`:

```bash
# nvm (Node)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
# then restart the shell, or:  export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"

# pyenv (Python) — recommended over Homebrew for version pinning
brew install pyenv
# add to ~/.zshrc or ~/.bash_profile:
#   export PYENV_ROOT="$HOME/.pyenv"
#   command -v pyenv >/dev/null && eval "$(pyenv init -)"
```

### 2. Install the pinned versions

```bash
cd <repo-root>
nvm install            # reads .nvmrc -> installs/uses Node 20
nvm use
pyenv install 3.12     # if not already installed
pyenv local 3.12       # honors .python-version
```

### 3. API (Python) setup

```bash
cd api
python --version                 # MUST read 3.12.x — verify before anything else
python -m venv .venv
source .venv/bin/activate         # prompt should now show (.venv)
which pytest                      # MUST point inside api/.venv — not /usr/local
pip install --upgrade pip
pip install -r requirements.txt
pytest tests/ -v -m "not requires_services"   # expect 55 passed
```

### 4. Frontend (Node) setup

```bash
cd frontend
node --version                    # MUST read v20.x — verify before anything else
npm ci                            # uses package-lock.json; fails loudly on drift
npm test                          # vitest — expect tests passing
npm run build
```

---

## The golden rule

**Before running any toolchain command, verify the runtime:**

```bash
python --version    # expect 3.12.x  (inside api/.venv)
node --version      # expect v20.x
```

If either is wrong, fix the runtime FIRST. Do not debug the application —
the application is almost never the problem. A wrong runtime is.

---

## Troubleshooting: known failure signatures

These have all happened in this project. Match the symptom, apply the fix.

### `Unexpected token import`
- **Cause:** Node < 18 is active (ESM not supported). A stale Node 8 at
  `/usr/local/bin/node` was shadowing the real one.
- **Diagnose:** `node --version` (will show v8/v10/etc.), `which -a node`.
- **Fix:** `nvm use 20` (or `nvm install 20`). Confirm `node --version` ≥ 18.

### `Cannot fetch index base URL https://pypi.python.org/simple/`
- **Cause:** Python 2.7 is active. Its ancient pip can't reach modern PyPI.
- **Diagnose:** `python --version` (shows 2.7.x).
- **Fix:** Activate the 3.12 venv (`source api/.venv/bin/activate`). Use
  `python3`/the venv, never bare `python` (which points at system 2.7).

### `pydantic-core` / PyO3 build failure on install
- **Cause:** Python 3.13+ active. PyO3 ABI mismatch.
- **Diagnose:** `python --version` (shows 3.13.x or 3.14.x).
- **Fix:** Use exactly 3.12. `pyenv local 3.12` then rebuild the venv.

### `numpy` / `torch` import or install errors
- **Cause:** numpy 2.x pulled in; torch 2.2.x is incompatible.
- **Fix:** `requirements.txt` pins `numpy>=1.26,<2.0`. Reinstall in a clean venv.

### `unrecognized arguments: --cov-omit`
- **Cause:** `--cov-omit` is not a real pytest-cov flag. Omit config belongs in
  `.coveragerc`, not the CLI.
- **Fix:** Already fixed — omit list lives in `api/.coveragerc`; CI uses only
  `--cov=. --cov-report=xml`.

### `npm ci` fails with lockfile mismatch
- **Cause:** `package-lock.json` out of sync with `package.json`.
- **Fix:** `cd frontend && npm install`, commit the updated lockfile.

### Homebrew: "homebrew-core is a shallow clone"
- **Cause:** shallow clone can't update.
- **Fix:** `git -C $(brew --repository)/Library/Taps/homebrew/homebrew-core fetch --unshallow`
  (slow, one-time). Note: this machine has BOTH `/usr/local` (Intel) and
  `/opt/homebrew` (Apple Silicon) Homebrews — installs may land in either. Check
  `which -a <tool>` to find where a formula actually installed.

### macOS git version conflict
- **Cause:** macOS ships git 1.7.x; Homebrew git 2.x requires explicit `PATH`
  ordering to win.
- **Fix:** Ensure the Homebrew bin dir precedes `/usr/bin` in `PATH`.

---

## Why this doc exists

Across this project's life, four separate work sessions were derailed by runtime
shadowing: Python 3.13/PyO3, Homebrew git 1.7 vs 2.54, Node 8 vs 20, and Python
2.7/3.14 vs 3.12. Each cost significant time because the *symptom* (a build or
test error) looked like an application bug, while the *cause* was always the
environment. Pinning versions (`.nvmrc`, `.python-version`, `engines`) plus the
"verify the runtime first" rule above eliminates the entire class.
