#!/bin/bash
set -e

# This script concatenates all documentation and specification files
# into a single file for LLM consumption.

# --- Configuration ---
OUTPUT_FILE="docs/llms-full.txt"
DOCS_DIR="docs"
SPEC_DIR="specification"

echo "--- Generating consolidated LLM file: ${OUTPUT_FILE} ---"

# Clear the output file to start fresh
true >"${OUTPUT_FILE}"

# --- Helper function to append file content with a header ---
append_file() {
  local file_path="$1"
  if [ -f "$file_path" ]; then
    echo "Appending: $file_path"
    {
      echo "--- START OF FILE ${file_path} ---"
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

# --- Process Documentation Files ---
# Find all markdown and rst files in the docs directory, sort them for consistent output,
# and append each one.
find "${DOCS_DIR}" -type f \( -name "*.md" -o -name "*.rst" \) | sort | while read -r doc_file; do
  append_file "$doc_file"
done

# --- Process Specification Files ---
append_file "${SPEC_DIR}/grpc/a2a.proto"
append_file "${SPEC_DIR}/json/a2a.json"

echo "✅ Consolidated LLM file generated successfully at ${OUTPUT_FILE}"
