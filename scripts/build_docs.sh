#!/bin/bash
set -euo pipefail

# Unified docs build script that ensures the non-normative JSON artifact is
# regenerated (if stale) before invoking MkDocs. Uses pure shell.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SCHEMA_JSON="$ROOT_DIR/specification/json/a2a.json"
PROTO_SRC="$ROOT_DIR/specification/grpc/a2a.proto"
SPEC_SITE_DIR="$ROOT_DIR/docs/spec"
SCHEMA_JSON_SITE_FILE="$SPEC_SITE_DIR/a2a.json"
PROTO_SITE_FILE="$SPEC_SITE_DIR/a2a.proto"
PROTO_TO_SCHEMA_SCRIPT="$ROOT_DIR/scripts/proto_to_json_schema.sh"

regen_needed() {
  if [ ! -f "$SCHEMA_JSON" ]; then return 0; fi

  local proto_mtime
  local schema_mtime
  if [[ "$(uname)" == "Darwin" ]]; then
    proto_mtime=$(stat -f %m "$PROTO_SRC")
    schema_mtime=$(stat -f %m "$SCHEMA_JSON")
  else
    proto_mtime=$(stat -c %Y "$PROTO_SRC")
    schema_mtime=$(stat -c %Y "$SCHEMA_JSON")
  fi
  [ "$proto_mtime" -gt "$schema_mtime" ]
}

echo "[build_docs] Checking schema freshness..." >&2
if regen_needed; then
  echo "[build_docs] Regenerating a2a.json from proto" >&2
  if [ -x "$PROTO_TO_SCHEMA_SCRIPT" ]; then
    bash "$PROTO_TO_SCHEMA_SCRIPT" "$SCHEMA_JSON" || {
      echo "[build_docs] Warning: proto to JSON schema conversion failed" >&2
    }
  else
    echo "[build_docs] proto_to_json_schema.sh missing or not executable; skipping schema generation." >&2
  fi
else
  echo "[build_docs] Schema is up-to-date, skipping regeneration" >&2
fi

# Always ensure spec files are available in docs directory for MkDocs
mkdir -p "$SPEC_SITE_DIR"

if [ -f "$SCHEMA_JSON" ]; then
  cp "$SCHEMA_JSON" "$SCHEMA_JSON_SITE_FILE"
  echo "[build_docs] Published schema to $SCHEMA_JSON_SITE_FILE" >&2
else
  echo "[build_docs] Warning: Schema file not found at $SCHEMA_JSON - MkDocs may fail" >&2
fi

if [ -f "$PROTO_SRC" ]; then
  cp "$PROTO_SRC" "$PROTO_SITE_FILE"
  echo "[build_docs] Published proto to $PROTO_SITE_FILE" >&2
else
  echo "[build_docs] Warning: Proto file not found at $PROTO_SRC" >&2
fi

# Build SDK documentation
echo "[build_docs] Building SDK documentation..." >&2
SDK_DOCS_SCRIPT="$ROOT_DIR/scripts/build_sdk_docs.sh"
if [ -x "$SDK_DOCS_SCRIPT" ]; then
  bash "$SDK_DOCS_SCRIPT" || echo "[build_docs] Warning: SDK docs build failed" >&2
else
  echo "[build_docs] SDK docs script not found or not executable: $SDK_DOCS_SCRIPT" >&2
fi

echo "[build_docs] Building MkDocs site..." >&2
mkdocs build "$@"
echo "[build_docs] Done." >&2
