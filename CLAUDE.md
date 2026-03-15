# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This is an **intentionally vulnerable** FastAPI application used exclusively for evaluating SAST/DAST/pentest tooling. Every security flaw is deliberate. Do **not** fix vulnerabilities unless explicitly asked — doing so defeats the purpose of the repo.

## Commands

```bash
# Install deps (Python 3.11 required — pinned in .python-version)
uv sync --extra dev

# Run the app locally
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Docker
docker build -t vulnshop .
docker compose up

# Bandit (Python SAST)
uv run bandit -r app/ -c pyproject.toml

# Bandit — high severity only
uv run bandit -r app/ -c pyproject.toml --severity-level high
```

## Architecture

Single-package FastAPI app. Entry point is `app/main.py`, which registers all routers, enables `debug=True`, and adds a wildcard CORS middleware. The SQLite database is initialised on startup via `app/database.py:init_db()` and seeded with default users (`admin/admin`, `alice/password123`).

**Request flow:** browser/API client → `main.py` middleware → router → raw `sqlite3` queries (no ORM) → response.

**Auth model:** JWT signed with the hardcoded secret `secret123` (in `app/security.py`). The token is stored in a non-HttpOnly cookie named `token`. Each route that needs auth calls `get_current_user()` locally — there is no FastAPI dependency that enforces auth globally.

**Router layout:**

| Router | Prefix | Key vulns |
|--------|--------|-----------|
| `routes/auth.py` | `/login`, `/register`, `/api/login` | SQLi in login/register, MD5 passwords, mass assignment on `role`, plaintext password in audit log |
| `routes/users.py` | `/api/users` | IDOR (no ownership checks), full PII returned, mass assignment via `PUT` |
| `routes/products.py` | `/products`, `/api/products` | SQLi in search, stored + reflected XSS via `\|safe` |
| `routes/admin.py` | `/admin` | Broken access control (JWT role claim only), several sub-routes have no auth at all |
| `routes/utils.py` | `/api/utils` | Command injection (`/ping`), SSRF (`/fetch`), path traversal (`/file`), pickle RCE (`/deserialize`), SSTI (`/render`), eval RCE (`/exec`), subprocess shell=True (`/shell`), yaml.unsafe_load (`/parse-yaml`), SSL no-verify (`/fetch-ssl-insecure`), env dump (`/env`) |

## Dependency CVEs (intentional — do not upgrade)

| Package | Version | CVE |
|---------|---------|-----|
| pyjwt | 2.3.0 | CVE-2022-29217 — alg:none confusion |
| requests | 2.27.1 | CVE-2023-32681 — Proxy-Authorization leak |
| Pillow | 9.3.0 | CVE-2023-44271, CVE-2023-50447 |
| cryptography | 38.0.4 | CVE-2023-23931 |
| jinja2 | 3.1.2 | CVE-2024-22195 |
| python-multipart | 0.0.5 | CVE-2024-24762 |

## Dockerfile / docker-compose misconfigs (intentional)

Hadolint: DL3007 (no image tag), DL4000 (MAINTAINER), DL3008 (unpinned apt), DL3020 (ADD vs COPY), DL3025 (shell-form CMD).
Checkov: CKV_DOCKER_2 (no HEALTHCHECK), CKV_DOCKER_3 (root user), privileged mode, secrets in `ENV`.
