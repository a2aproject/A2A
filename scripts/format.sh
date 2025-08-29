#!/bin/bash

set -euo pipefail
# Determine the repository root directory based on the script's location.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." &>/dev/null && pwd)
bash "${SCRIPT_DIR}/sort_spelling.sh"

# Define file and directory paths.
MARKDOWN_DIR="${REPO_ROOT}/docs/"
MARKDOWNLINT_CONFIG="${REPO_ROOT}/.github/linters/.markdownlint.json"

# Install markdownlint-cli if the command doesn't already exist.
if ! command -v markdownlint &>/dev/null; then
  echo "Installing markdownlint-cli..."
  npm install -g markdownlint-cli
fi

# Run markdownlint to format files.
echo "Formatting markdown files..."
# Check for the existence of the directory and config file before running.
[ -d "${MARKDOWN_DIR}" ] || {
  echo "ERROR: Markdown directory not found: ${MARKDOWN_DIR}"
  exit 1
}
[ -f "${MARKDOWNLINT_CONFIG}" ] || {
  echo "ERROR: Markdownlint config not found: ${MARKDOWNLINT_CONFIG}"
  exit 1
}

markdownlint "${MARKDOWN_DIR}" --config "${MARKDOWNLINT_CONFIG}" --fix

echo "Script finished successfully."
