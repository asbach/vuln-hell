---
name: Intentional security findings catalogue
description: Master list of expected/intentional findings from each scanner — used to distinguish true positives from tool noise
type: project
---

## Bandit expected findings (all intentional)
- B301/B403 — pickle.loads() in utils.py
- B302/B324 — hashlib.md5() in security.py, database.py
- B307     — eval() in utils.py
- B501     — requests.get(verify=False) in utils.py
- B506     — yaml.load(Loader=yaml.Loader) in utils.py
- B602     — subprocess.Popen(shell=True) in utils.py
- B605     — os.popen() in utils.py
- B701     — Jinja2 Template() without autoescape in utils.py
- B104     — bind-all 0.0.0.0 in CMD

## pip-audit / SCA expected CVEs (do NOT upgrade these packages)
- pyjwt 2.3.0        → CVE-2022-29217 (alg:none confusion)
- requests 2.27.1    → CVE-2023-32681 (Proxy-Authorization leak)
- Pillow 9.3.0       → CVE-2023-44271, CVE-2023-50447
- cryptography 38.0.4 → CVE-2023-23931
- jinja2 3.1.2       → CVE-2024-22195
- python-multipart 0.0.5 → CVE-2024-24762

## Hadolint expected violations
- DL3007 — floating `python:3.11` tag (no hash pin)
- DL4000 — deprecated MAINTAINER instruction
- DL3008 — unpinned apt packages (curl wget netcat-traditional)
- DL3020 — ADD used instead of COPY
- DL3025 — CMD in shell form instead of JSON array
- DL3013 — uv sync without --frozen

## Checkov expected failures
- CKV_DOCKER_2 — no HEALTHCHECK instruction
- CKV_DOCKER_3 — no USER instruction (runs as root)
- CKV2_DC_1   — no resource limits in docker-compose.yml
- CKV2_DC_2   — privileged: true in docker-compose.yml
- CKV_SECRET_* — ENV secrets in Dockerfile + docker-compose.yml

## Gitleaks / secret scanning expected findings
- SECRET_KEY=supersecretkey123 (Dockerfile, docker-compose.yml)
- ADMIN_PASSWORD=admin123 (Dockerfile, docker-compose.yml)
- JWT_SECRET=secret123 (Dockerfile, docker-compose.yml, security.py)
- api_key values: sk-prod-HARDCODED1234567890, sk-user-abcdef1234567890 (database.py)
- SSN: 123-45-6789, 987-65-4321 (database.py)
- Credit card numbers: 4111111111111111, 5500005555555559 (database.py)

## Trivy image secrets expected
All of the above ENV values baked into image layers.

## ZAP DAST expected findings (when running against live app)
- SQL Injection: /login, /register, /api/products?search=
- XSS (reflected + stored): /products, search endpoint
- Command injection: /api/utils/ping
- SSRF: /api/utils/fetch, /api/utils/fetch-ssl-insecure
- Path traversal: /api/utils/file
- Open redirect: /api/utils/redirect
- SSTI: /api/utils/render
- Env dump: /api/utils/env
- CORS: wildcard allow-origin with allow-credentials
- Missing security headers: CSP, X-Frame-Options, X-Content-Type-Options
- Debug mode / stack traces in 500 responses
