#!/bin/bash
set -euo pipefail
# Convert proto files to JSON Schema in a single operation.
#
# v2: Added split-output mode — pass a second argument (output directory)
#     to generate individual JSON Schema files for each core A2A type.
#
# Usage:
#   proto_to_json_schema.sh <output.json> [split_dir]
#
#   <output.json>  — bundled schema file (always generated)
#   [split_dir]    — optional directory for per-type JSON Schema files
#
# When split_dir is provided, the script additionally writes one
# {TypeName}.json file per core type under that directory.

OUTPUT=${1:-}
SPLIT_DIR=${2:-}

if [[ -z "$OUTPUT" ]]; then
  echo "Usage: $0 <output.json> [split_dir]" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROTO_DIR="$ROOT_DIR/specification"
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

# Verify protoc-gen-jsonschema is the correct implementation (bufbuild/protoschema-plugins)
PLUGIN_VERSION=$(protoc-gen-jsonschema --version 2>&1 || true)
if [[ ! "$PLUGIN_VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: Incorrect protoc-gen-jsonschema plugin detected." >&2
  echo "Current version output: '$PLUGIN_VERSION'" >&2
  echo "This script requires the plugin from github.com/bufbuild/protoschema-plugins" >&2
  echo "Please install it with:" >&2
  echo "  go install github.com/bufbuild/protoschema-plugins/cmd/protoc-gen-jsonschema@latest" >&2
  exit 1
fi

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

CLEAN_PROTO_FILE="$TEMP_DIR/$(basename "$PROTO_FILE")"
grep -v -e "// --8<--" -e "// protolint:" "$PROTO_FILE" >"$CLEAN_PROTO_FILE"
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

DEF_COUNT=$(jq '.definitions | length' "$OUTPUT")
echo "✓ Generated $OUTPUT with $DEF_COUNT definitions" >&2

# ---------------------------------------------------------------------------
# Step 3: Split — generate per-type JSON Schema files (only when SPLIT_DIR set)
# ---------------------------------------------------------------------------
if [[ -z "$SPLIT_DIR" ]]; then
  exit 0
fi

echo "→ Splitting schemas into $SPLIT_DIR ..." >&2
mkdir -p "$SPLIT_DIR"

# Core types to extract as standalone schemas
CORE_TYPES=(
  AgentCard
  Task
  TaskStatus
  Message
  Artifact
  Part
  TaskStatusUpdateEvent
  TaskArtifactUpdateEvent
  AgentCapabilities
  AgentSkill
  AgentExtension
  AuthenticationInfo
  AgentInterface
  AgentProvider
)

# Build a jq expression that, for each core type, emits a standalone schema.
# Each file gets: $schema, $id, title, type:object, properties (from the def).
# If a type is not found in definitions, it is skipped silently.

for TYPE_NAME in "${CORE_TYPES[@]}"; do
  jq --arg type "$TYPE_NAME" --arg id_base "https://a2a-protocol.org/spec" '
    .definitions[$type] | select(.) | . + {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "$id": "\($id_base)/\($type).json",
      title: $type
    }
  ' "$OUTPUT" > "$SPLIT_DIR/${TYPE_NAME}.json" 2>/dev/null || true

  # Remove empty file if type was not found
  if [[ ! -s "$SPLIT_DIR/${TYPE_NAME}.json" ]]; then
    rm -f "$SPLIT_DIR/${TYPE_NAME}.json"
  fi
done

# Also extract SecurityScheme and its sub-types (any definition containing "Security")
jq --arg id_base "https://a2a-protocol.org/spec" '
  .definitions | keys[] | select(startswith("Security"))
' --raw-output "$OUTPUT" 2>/dev/null | while read -r TYPE_NAME; do
  jq --arg type "$TYPE_NAME" --arg id_base "https://a2a-protocol.org/spec" '
    .definitions[$type] | select(.) | . + {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "$id": "\($id_base)/\($type).json",
      title: $type
    }
  ' "$OUTPUT" > "$SPLIT_DIR/${TYPE_NAME}.json"
done

SPLIT_COUNT=$(find "$SPLIT_DIR" -maxdepth 1 -name '*.json' | wc -l | tr -d ' ')
echo "✓ Generated $SPLIT_COUNT split schema files in $SPLIT_DIR" >&2
