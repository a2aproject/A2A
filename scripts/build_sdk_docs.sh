#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
PACKAGE_NAME="a2a"          # The name of the package to import
PYPI_PACKAGE_NAME="a2a-sdk" # The name on PyPI
DOCS_SOURCE_DIR="docs/sdk/python"
DOCS_BUILD_DIR="${DOCS_SOURCE_DIR}/_build"
VENV_DIR=".doc-venv"

echo "--- Setting up documentation build environment ---"

# Create a clean virtual environment
if [ -d "$VENV_DIR" ]; then
  rm -rf "$VENV_DIR"
fi
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "--- Installing package and dependencies ---"

# Upgrade pip and install documentation requirements
pip install -U pip
pip install -r "requirements-docs.txt"

# Install the package itself
pip install "${PYPI_PACKAGE_NAME}"

echo "--- Finding installed package path ---"

# Find the installation path of the package
PACKAGE_PATH=$(python -c "import ${PACKAGE_NAME}, os; print(os.path.dirname(${PACKAGE_NAME}.__file__))")
echo "Found '${PACKAGE_NAME}' at: ${PACKAGE_PATH}"

echo "--- Generating API documentation source files (.rst) ---"

# Run sphinx-apidoc on the installed package directory
# -f: force overwrite of existing files
# -e: put each module on its own page
sphinx-apidoc -f -e -o "${DOCS_SOURCE_DIR}" "${PACKAGE_PATH}"

echo "--- Building HTML documentation ---"

# Build the HTML documentation
sphinx-build -b html "${DOCS_SOURCE_DIR}" "${DOCS_BUILD_DIR}/html"

echo "--- Copying SDK docs to MkDocs integration path ---"

# Copy SDK docs to where MkDocs expects them (docs/sdk/python/api/)
SDK_API_DIR="${DOCS_SOURCE_DIR}/api"
if [ -d "${DOCS_BUILD_DIR}/html" ]; then
  rm -rf "${SDK_API_DIR}"
  cp -r "${DOCS_BUILD_DIR}/html" "${SDK_API_DIR}"
  echo "SDK docs copied to: ${SDK_API_DIR}"
else
  echo "Warning: SDK docs build directory not found at ${DOCS_BUILD_DIR}/html"
fi

# Deactivate the virtual environment
deactivate

echo ""
echo "✅ Documentation build complete!"
echo "View the docs by opening: ${SDK_API_DIR}/index.html"
