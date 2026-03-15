---
name: Pipeline overview
description: Overview of the DevSecOps GitHub Actions pipeline built for the VulnShop intentionally-vulnerable FastAPI app
type: project
---

Four workflow files live in `.github/workflows/`:

- `ci.yml` — lint (Ruff), pytest+coverage, Docker smoke-build. Pushes coverage to Codacy via `codacy/codacy-coverage-reporter-action`.
- `security.yml` — parallel SAST/SCA/container/SBOM/secrets jobs: Bandit, Semgrep, pip-audit, Hadolint, Trivy, Checkov, Gitleaks, Syft. All use `continue-on-error: true` and upload SARIF.
- `dast.yml` — Docker Compose brings the app up; OWASP ZAP runs baseline (PRs) or full active scan (schedule). Python script converts ZAP JSON to SARIF for Security tab upload.
- (Dependabot already configured in `.github/dependabot.yml` for uv ecosystem.)

Supporting configs:
- `.github/semgrep.yml` — layered community rulesets + 10 custom rules for app-specific patterns
- `.github/zap-rules.tsv` — ZAP rule thresholds (all MEDIUM or lower, none suppressed)
- `.github/actions/setup-python-uv/action.yml` — composite action for Python/uv setup boilerplate

**Why:** Platform is intentionally vulnerable for tooling evaluation. All scan jobs must surface findings — never fix or suppress them.
**How to apply:** When adding new jobs, always set `continue-on-error: true` on scan steps and upload SARIF. Never suppress findings.
