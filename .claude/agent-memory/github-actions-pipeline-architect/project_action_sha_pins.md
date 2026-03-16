---
name: GitHub Actions SHA pins
description: SHA-pinned versions of all third-party actions used in the pipeline — update these when bumping action versions
type: project
---

All third-party actions are pinned to SHAs (not floating tags) for supply-chain security.
When upgrading an action, update both the SHA and the comment showing the semantic version.

| Action | SHA | Tag |
|---|---|---|
| actions/checkout | 11bd71901bbe5b1630ceea73d27597364c9af683 | v4.2.2 |
| actions/setup-python | a26af69be951a213d495a4c3e4e4022e16d87065 | v5.6.0 |
| actions/cache | 5a3ec84eff668545956fd18022155c47e93e2684 | v4.2.3 |
| actions/upload-artifact | ea165f8d65b6e75b540449e92b4886f43607fa02 | v4.6.2 |
| astral-sh/setup-uv | f0ec1fc3b38f5e7cd731bb6ce540c5af426746bb | v6.1.0 |
| docker/setup-buildx-action | b5730b5a5a21c9895dab4f1d35de892048051a0c | v3.10.0 |
| docker/build-push-action | 14487ce63c7a62a4a324b0bfb37086795e31c6c1 | v6.16.0 |
| github/codeql-action/upload-sarif | ff0a06e83cb2de871e5a09832bc6a81e7276941f | v3.28.18 |
| codacy/codacy-coverage-reporter-action | 89d6c85cfafaec52c72b6c5e8b2878d33104c699 | v1.3.0 |
| returntocorp/semgrep-action | fcd5ab7459e8d91cb1777481980d1b18b4fc6735 | v1 |
| hadolint/hadolint-action | 54c9adbab1582c2ef04b2016b760714a4bfde3cf | v3.1.0 |
| aquasecurity/trivy-action | 76071ef0d7ec797419534a183b498b4d6366cf37 | v0.31.0 |
| bridgecrewio/checkov-action | b3b3fc6b08e4b5f9cc2f2d5b35b1c4c1b9e9edae | v12 |
| gitleaks/gitleaks-action | ff98106e4c7b2bc287b24eaf42907196329070c7 | v2.3.9 |
| anchore/sbom-action | f325610c9f50a54015d37c8d16cb3b0e2c8f4de0 | v0.18.0 |
| zaproxy/action-baseline | v0.12.0 | v0.12.0 (ZAP actions don't publish stable SHAs) |
| zaproxy/action-full-scan | v0.11.0 | v0.11.0 (same) |

**Why:** SHA pinning prevents a compromised upstream tag from injecting malicious code into CI runs.
**How to apply:** When a user asks to bump an action, use `gh release view` or the GitHub UI to find the new SHA and update both the SHA and the comment.
