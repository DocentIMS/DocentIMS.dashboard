#!/bin/bash
# SessionStart hook: install Python linters so they are ready to run in
# Claude Code on the web sessions. The DocentIMS.dashboard package is a Plone
# add-on; its unit tests need a full zc.buildout Plone instance (too heavy for
# a session hook), so this hook provisions the lightweight lint toolchain that
# the project's CI uses (black / isort / flake8).
set -euo pipefail

# Only run in the remote (Claude Code on the web) environment.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

# Create a dedicated virtualenv for the lint tools (idempotent; cached after
# the first run). 'venv/' is already in .gitignore.
if [ ! -x venv/bin/python ]; then
  python3 -m venv venv
fi

# Pin versions to match the project's CI (see constraints_plone60.txt).
venv/bin/pip install --quiet --upgrade pip
venv/bin/pip install --quiet "black==22.8.0" "isort>=5" "flake8>=5.0.4" "flake8-html>=0.4.2"

# Expose the lint tools on PATH for the rest of the session.
echo "export PATH=\"$CLAUDE_PROJECT_DIR/venv/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
