#!/bin/bash
set -e

# This script concatenates all documentation and specification files
# into a single file for LLM consumption.

# --- Configuration ---
OUTPUT_FILE="docs/llms-full.txt"
DOCS_DIR="docs"
SPEC_DIR="specification"
SDK_DOCS_SCRIPT="scripts/build_sdk_docs.sh"

echo "--- Generating consolidated LLM file: ${OUTPUT_FILE} ---"

# Clear the output file to start fresh
true >"${OUTPUT_FILE}"

# --- Helper function to append file content with a header ---
append_file() {
  local file_path="$1"
  local display_path="${2:-$file_path}"
  if [ -f "$file_path" ]; then
    echo "Appending: $file_path"
    {
      echo "--- START OF FILE ${display_path} ---"
      echo
      cat "$file_path"
      echo
      echo "================================================="
      echo
    } >>"${OUTPUT_FILE}"
  else
    echo "Warning: File not found, skipping: $file_path" >&2
  fi
}

# --- Generate Python SDK Text Documentation ---
if [ -f "$SDK_DOCS_SCRIPT" ]; then
  echo "Generating Python SDK documentation..."
  bash "$SDK_DOCS_SCRIPT"
else
  echo "Warning: SDK docs script not found at $SDK_DOCS_SCRIPT"
fi

# --- Process README ---
append_file "README.md"

# --- Process Documentation Files ---
# Find all markdown and rst files in the docs directory, sort them for consistent output,
# and append each one. Exclude Python SDK source files (rst) because we include generated text.
find "${DOCS_DIR}" -type f \( -name "*.md" -o -name "*.rst" \) \
  -not -path "docs/sdk/python/*" | sort | while read -r doc_file; do
  append_file "$doc_file"
done

# --- Process Python SDK Text Files ---
# Include the generated text documentation for the Python SDK.
# The build_sdk_docs.sh script generates text files in docs/sdk/python/_build/text
SDK_TEXT_DIR="docs/sdk/python/_build/text"
if [ -d "$SDK_TEXT_DIR" ]; then
  find "$SDK_TEXT_DIR" -type f -name "*.txt" | sort | while read -r doc_file; do
    relative_path="${doc_file#$SDK_TEXT_DIR/}"
    append_file "$doc_file" "sdk/python/$relative_path"
  done
else
  echo "Warning: SDK text docs directory not found at $SDK_TEXT_DIR"
fi

# --- Process Specification Files ---
append_file "${SPEC_DIR}/a2a.proto"

echo "✅ Consolidated LLM file generated successfully at ${OUTPUT_FILE}"
