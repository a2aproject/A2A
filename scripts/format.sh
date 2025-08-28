#!/bin/bash

# Exit immediately if a command fails (-e) or if an undeclared variable is used (-u).
set -eu

bash scripts/sort_spelling.sh

# Define file and directory paths.
MARKDOWN_DIR="docs/"
MARKDOWNLINT_CONFIG=".github/linters/.markdownlint.json"

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
