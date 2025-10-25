#!/bin/bash
set -euo pipefail
# Extract pure JSON Schema components from an OpenAPI (v2 or v3) document.
# Usage: extract_json_schema.sh <openapi_file> <output_schema_file>
# Retains components.schemas (v3) or definitions (v2) and writes a JSON Schema bundle
# with top-level $schema and $id hints.

INPUT=${1:-}
OUTPUT=${2:-}
if [[ -z "$INPUT" || -z "$OUTPUT" ]]; then
  echo "Usage: $0 <openapi.(json|yaml)> <output.json>" >&2
  exit 1
fi
if [[ ! -f "$INPUT" ]]; then
  echo "Input file not found: $INPUT" >&2
  exit 1
fi

# Decide parser based on extension; use yq for yaml, jq for json. Require them.
EXT="${INPUT##*.}"
TMP_JSON=$(mktemp)
trap 'rm -f "$TMP_JSON"' EXIT

if [[ "$EXT" == "yaml" || "$EXT" == "yml" ]]; then
  if ! command -v yq >/dev/null 2>&1; then
    echo "yq is required to process YAML OpenAPI documents." >&2
    exit 1
  fi
  yq -o=json '.' "$INPUT" > "$TMP_JSON"
else
  cp "$INPUT" "$TMP_JSON"
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required to extract schemas." >&2
  exit 1
fi

# Try v3 (components.schemas) then fallback to v2 (definitions). Capture as structured JSON for pretty output.
SCHEMA_CONTENT=$(jq 'if .components and .components.schemas then .components.schemas elif .definitions then .definitions else {} end' "$TMP_JSON")

if [[ -z "$SCHEMA_CONTENT" || "$SCHEMA_CONTENT" == "null" ]]; then
  echo "[extract_json_schema] Warning: No schemas found in OpenAPI document." >&2
  SCHEMA_CONTENT="{}"
fi

# Construct final JSON using jq to avoid escaping issues and ensure pretty output.
jq -n --argjson defs "$SCHEMA_CONTENT" '{
  "$schema": "http://json-schema.org/draft-07/schema#",
  title: "A2A Protocol Schemas",
  description: "Non-normative JSON Schema bundle extracted from generated OpenAPI document (proto-derived).",
  version: "v1",
  definitions: $defs
}' | jq . > "$OUTPUT"

echo "[extract_json_schema] Wrote schemas to $OUTPUT" >&2
