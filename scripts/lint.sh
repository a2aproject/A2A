#!/bin/bash

# Exit on error (-e), undefined variable usage (-u), or failed pipe command (-o pipefail).
set -euo pipefail

# Determine the repository root directory based on the script's location.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
REPO_ROOT=$(cd -- "${SCRIPT_DIR}/.." &>/dev/null && pwd)
# Absolute path to the Super Linter configuration file.
SUPER_LINTER_ENV="${REPO_ROOT}/.github/super-linter.env"
# Detect the default branch from the remote repository.
DEFAULT_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)

# Run Super Linter locally using Docker.
# This mirrors the configuration used in GitHub Actions to provide consistent linting behavior.
docker run \
  --rm -t \
  --platform linux/x86_64 \
  -v "${REPO_ROOT}":/tmp/lint \
  -e SHELL=/bin/bash \
  -e DEFAULT_BRANCH="${DEFAULT_BRANCH}" \
  -e RUN_LOCAL=true \
  -e LOG_LEVEL=INFO \
  --env-file "${SUPER_LINTER_ENV}" \
  ghcr.io/super-linter/super-linter:slim-v8
