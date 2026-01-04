#!/bin/bash

set -euo pipefail

# Determine the repository root directory based on the script's location.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." &>/dev/null && pwd)

ALLOW_FILE="${REPO_ROOT}/.github/actions/spelling/allow.txt"

echo "Sorting spelling allow list..."
[ -f "${ALLOW_FILE}" ] || {
  echo "ERROR: Allow list not found: ${ALLOW_FILE}"
  exit 1
}
LC_ALL=C sort -u -o "${ALLOW_FILE}" "${ALLOW_FILE}"
