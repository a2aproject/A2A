#!/bin/bash
set -e

# This script concatenates all documentation and specification files
# into a single file for LLM consumption.

# --- Configuration ---
OUTPUT_FILE="docs/llms-full.txt"
DOCS_DIR="docs"
SPEC_DIR="specification"
SDK_DOCS_SCRIPT="scripts/build_sdk_docs.sh"
PROJECT_NAME="A2A (Agent2Agent) Protocol"

echo "--- Generating consolidated LLM file: ${OUTPUT_FILE} ---"

# --- Generate Python SDK Text Documentation ---
if [ -f "$SDK_DOCS_SCRIPT" ]; then
  echo "Generating Python SDK documentation..."
  bash "$SDK_DOCS_SCRIPT"
else
  echo "Warning: SDK docs script not found at $SDK_DOCS_SCRIPT"
fi

# Clear the output file and add introduction
cat <<EOF >"${OUTPUT_FILE}"
# ${PROJECT_NAME} - Full Documentation

This file is a consolidated version of all documentation, specifications, and API references
for the ${PROJECT_NAME} project, optimized for LLM consumption.

EOF

# Include llms.txt as the core summary if it exists
if [ -f "${DOCS_DIR}/llms.txt" ]; then
  echo "Including summary from ${DOCS_DIR}/llms.txt"
  {
    echo "## Project Summary"
    echo
    cat "${DOCS_DIR}/llms.txt"
    echo
    echo "---"
    echo
  } >>"${OUTPUT_FILE}"
fi

# --- Helper function to append file content with XML-style tags ---
append_file() {
  local file_path="$1"
  local display_path="${2:-$file_path}"
  if [ -f "$file_path" ]; then
    echo "Appending: $file_path"
    {
      echo "<file path=\"${display_path}\">"
      cat "$file_path"
      echo "</file>"
      echo
    } >>"${OUTPUT_FILE}"
  else
    echo "Warning: File not found, skipping: $file_path" >&2
  fi
}

# --- Build File List ---
echo "## File Index" >>"${OUTPUT_FILE}"
echo >>"${OUTPUT_FILE}"

# Collect all files we intend to include
FILES_TO_INCLUDE=()
FILES_TO_INCLUDE+=("README.md")

# Doc files
while IFS= read -r doc_file; do
  FILES_TO_INCLUDE+=("$doc_file")
done < <(find "${DOCS_DIR}" -type f \( -name "*.md" -o -name "*.rst" \) \
  -not -path "docs/sdk/python/*" \
  -not -path "docs/README.md" \
  -not -path "docs/sdk/python.md" \
  -not -path "docs/llms-full.txt" | sort)

# SDK text files
SDK_TEXT_DIR="docs/sdk/python/_build/text"
if [ -d "$SDK_TEXT_DIR" ]; then
  while IFS= read -r sdk_file; do
    FILES_TO_INCLUDE+=("$sdk_file")
  done < <(find "$SDK_TEXT_DIR" -type f -name "*.txt" | sort)
fi

# Specification
if [ -f "${SPEC_DIR}/a2a.proto" ]; then
  FILES_TO_INCLUDE+=("${SPEC_DIR}/a2a.proto")
fi

# Write the index to the output file
for f in "${FILES_TO_INCLUDE[@]}"; do
  display_name="$f"
  # Clean up display name for SDK files
  if [[ "$f" == "$SDK_TEXT_DIR"* ]]; then
    display_name="sdk/python/${f#"$SDK_TEXT_DIR"/}"
  fi
  echo "- ${display_name}" >>"${OUTPUT_FILE}"
done

{
  echo
  echo "---"
  echo
} >>"${OUTPUT_FILE}"

# --- Append file contents ---
for f in "${FILES_TO_INCLUDE[@]}"; do
  display_name="$f"
  if [[ "$f" == "$SDK_TEXT_DIR"* ]]; then
    display_name="sdk/python/${f#"$SDK_TEXT_DIR"/}"
  fi
  append_file "$f" "$display_name"
done

echo "✅ Consolidated LLM file generated successfully at ${OUTPUT_FILE}"
