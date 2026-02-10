#!/bin/bash

# Exit on error (-e), undefined variable usage (-u), or failed pipe command (-o pipefail).
set -euo pipefail

# Determine the repository root directory based on the script's location.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
REPO_ROOT=$(cd -- "${SCRIPT_DIR}/.." &>/dev/null && pwd)

# Change to the repository root so that file paths are relative to it.
cd "${REPO_ROOT}"

# Run API Linter locally using Docker.
# This mirrors the configuration used in GitHub Actions.
# Using the image used by the googleapis/api-linter action.
echo "Running API Linter..."
docker run \
  --rm \
  -t \
  -v "${REPO_ROOT}:/workspace" \
  -w /workspace \
  gcr.io/gapic-images/api-linter:latest \
  --proto-path=specification \
  --config-path=specification/.api-linter.yaml \
  specification/*.proto

echo "API Linter finished."