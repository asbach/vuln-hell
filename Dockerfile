# =============================================================================
# INTENTIONALLY MISCONFIGURED — for Hadolint / Checkov / Trivy / Snyk testing
# =============================================================================

# hadolint ignore=DL3007 — DL3007: no specific version tag (using floating tag)
FROM python:3.11

# hadolint ignore=DL4000 — DL4000: MAINTAINER is deprecated
MAINTAINER security-test@corp.internal

# A02/A05: Secrets hardcoded in image layers — detected by Trivy secret scanner & Checkov CKV_DOCKER_5
ENV SECRET_KEY=supersecretkey123
ENV ADMIN_PASSWORD=admin123
ENV DATABASE_URL=sqlite:///./vulnerable.db
ENV JWT_SECRET=secret123

# hadolint ignore=DL3008,DL3009,DL3015 — unpinned apt packages, no cleanup, extra packages
RUN apt-get update && apt-get install -y curl wget netcat-traditional

# Copy uv binary from official image (pinned for reproducibility)
COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /usr/local/bin/uv

# hadolint ignore=DL3020 — DL3020: ADD used instead of COPY
ADD pyproject.toml /app/pyproject.toml
ADD . /app

WORKDIR /app

# hadolint ignore=DL3013 — DL3013: uv sync without --frozen (allows version drift)
RUN uv sync

# CKV_DOCKER_2: No HEALTHCHECK instruction (Checkov)
# CKV_DOCKER_3: No USER instruction — runs as root (Checkov)

EXPOSE 8000

# hadolint ignore=DL3025 — DL3025: CMD in shell form instead of JSON array
CMD uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
