---
name: Required GitHub secrets and variables
description: Secrets that must be configured in GitHub repository settings for the pipeline to work
type: project
---

The following secrets must be added under Settings → Secrets and variables → Actions:

| Secret name | Required? | Used by | Notes |
|---|---|---|---|
| `CODACY_PROJECT_TOKEN` | Recommended | `ci.yml` (test job) | Codacy project token for coverage upload. If absent, the step `continue-on-error: true` protects the job. |
| `SEMGREP_APP_TOKEN` | Optional | `security.yml` (semgrep job) | Needed to push results to Semgrep Cloud (app.semgrep.dev). Pipeline works without it but findings won't appear in Semgrep dashboard. |
| `GITHUB_TOKEN` | Automatic | All workflows | Provided automatically; used for SARIF upload, artifact upload, Gitleaks. No configuration needed. |

**Why:** Pipeline was designed to degrade gracefully — `CODACY_PROJECT_TOKEN` and `SEMGREP_APP_TOKEN` use `continue-on-error: true` so their absence doesn't break builds.
**How to apply:** When a user reports a failing Codacy or Semgrep step, check if the secret is configured before investigating the workflow YAML.
