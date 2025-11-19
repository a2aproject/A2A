#!/bin/bash
set -euo pipefail
# Convert proto files to JSON Schema in a single operation.
# Usage: proto_to_json_schema.sh <output_json_schema>

OUTPUT=${1:-}
if [[ -z "$OUTPUT" ]]; then
  echo "Usage: $0 <output.json>" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROTO_DIR="$ROOT_DIR/specification/grpc"
PROTO_FILE="$PROTO_DIR/a2a.proto"
GOOGLEAPIS_DIR="${GOOGLEAPIS_DIR:-}"

check_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: $1 not found on PATH" >&2
    exit 1
  fi
}

# Check dependencies
check_command "protoc"
check_command "protoc-gen-jsonschema"
check_command "jq"

# Create temporary directory for intermediate files
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Setup include paths for googleapis
INCLUDE_FLAGS=("-I$PROTO_DIR")
if [ -n "$GOOGLEAPIS_DIR" ]; then
  INCLUDE_FLAGS+=("-I$GOOGLEAPIS_DIR")
elif [ -d "$ROOT_DIR/third_party/googleapis" ]; then
  INCLUDE_FLAGS+=("-I$ROOT_DIR/third_party/googleapis")
elif [ -d "/usr/local/include/google/api" ]; then
  INCLUDE_FLAGS+=("-I/usr/local/include")
fi

# Verify googleapis annotations are available
ANNOTATIONS_FOUND=false
for inc in "${INCLUDE_FLAGS[@]}"; do
  dir="${inc#-I}"
  if [ -f "$dir/google/api/annotations.proto" ]; then
    ANNOTATIONS_FOUND=true
    break
  fi
done
if [ "$ANNOTATIONS_FOUND" != true ]; then
  echo "Error: google/api/annotations.proto not found in include paths" >&2
  echo "Set GOOGLEAPIS_DIR env var or ensure third_party/googleapis exists" >&2
  exit 1
fi

# Step 0: Pre-process proto
echo "→ Cleaning proto comments..." >&2

# Define path for the cleaned proto in the temp directory
CLEAN_PROTO_FILE="$TEMP_DIR/$(basename "$PROTO_FILE")"

# Use sed to remove lines containing specific patterns:
# 1. matches "// --8<--"
# 2. matches "// protolint:"
sed -e '/\/\/ --8<--/d' \
  -e '/\/\/ protolint:/d' \
  "$PROTO_FILE" >"$CLEAN_PROTO_FILE"

# Add the temp dir to the include path so protoc finds the clean file context
# We prepend it so it takes precedence over the original file
INCLUDE_FLAGS=("-I$TEMP_DIR" "${INCLUDE_FLAGS[@]}")

# Step 1: Generate individual JSON Schema files with JSON field names (camelCase)
echo "→ Generating JSON Schema from proto..." >&2
if ! protoc "${INCLUDE_FLAGS[@]}" \
  --jsonschema_out="$TEMP_DIR" \
  --jsonschema_opt=target=json \
  "$CLEAN_PROTO_FILE" 2>&1; then
  echo "Error: protoc generation failed" >&2
  exit 1
fi

# Step 2: Bundle all schemas into a single file with cleaned names
echo "→ Creating JSON Schema bundle..." >&2

# Check if any JSON files were generated
JSON_FILES=("$TEMP_DIR"/*.json)
if [ ! -f "${JSON_FILES[0]}" ]; then
  echo "Error: No JSON schema files generated" >&2
  exit 1
fi

jq -s '
  (if .[0]."$schema" then .[0]."$schema" else "http://json-schema.org/draft-07/schema#" end) as $schema |
  (reduce .[] as $item ({};
    if $item.title then
      . + {($item.title): ($item | del(."$id"))}
    else
      .
    end
  )) as $defs |
  {
    "$schema": $schema,
    title: "A2A Protocol Schemas",
    description: "Non-normative JSON Schema bundle extracted from proto definitions.",
    version: "v1",
    definitions: $defs
  }
' "$TEMP_DIR"/*.json >"$OUTPUT"

# Count definitions
DEF_COUNT=$(jq '.definitions | length' "$OUTPUT")
echo "✓ Generated $OUTPUT with $DEF_COUNT definitions" >&2
