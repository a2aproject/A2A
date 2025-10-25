#!/bin/bash
set -euo pipefail
# Generate OpenAPI (Swagger v2) using protoc + protoc-gen-openapiv2.
# Requirements: protoc, protoc-gen-openapiv2 on PATH.

# Output (ephemeral): a temporary a2a.swagger.json used only for JSON Schema extraction.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROTO_DIR="$ROOT_DIR/specification/grpc"
OUT_DIR="${OPENAPI_TMP_DIR:-}"
if [ -z "$OUT_DIR" ]; then
  OUT_DIR=$(mktemp -d)
  trap 'rm -rf "$OUT_DIR"' EXIT
fi
PROTO_FILE="$PROTO_DIR/a2a.proto"
GOOGLEAPIS_DIR="${GOOGLEAPIS_DIR:-}"

if ! command -v protoc >/dev/null 2>&1; then
  echo "[generate_openapi] protoc not found on PATH" >&2
  exit 1
fi
if ! command -v protoc-gen-openapiv2 >/dev/null 2>&1; then
  echo "[generate_openapi] protoc-gen-openapiv2 not found on PATH" >&2
  exit 1
fi

# Ensure output dir exists (mktemp already does, but in case OPENAPI_TMP_DIR is provided)
mkdir -p "$OUT_DIR"

# Include googleapis for annotations; attempt common locations.
INCLUDE_FLAGS=("-I""$PROTO_DIR")
# Priority order for googleapis protos providing google/api/*.proto
if [ -n "$GOOGLEAPIS_DIR" ]; then
  INCLUDE_FLAGS+=("-I""$GOOGLEAPIS_DIR")
elif [ -d "$ROOT_DIR/third_party/googleapis" ]; then
  INCLUDE_FLAGS+=("-I""$ROOT_DIR/third_party/googleapis")
elif [ -d "/usr/local/include/google/api" ]; then
  INCLUDE_FLAGS+=("-I""/usr/local/include")
fi

ANNOTATIONS_FOUND=false
for inc in "${INCLUDE_FLAGS[@]}"; do
  # Strip -I prefix
  dir="${inc#-I}"
  if [ -f "$dir/google/api/annotations.proto" ]; then
    ANNOTATIONS_FOUND=true
    break
  fi
done
if [ "$ANNOTATIONS_FOUND" != true ]; then
  echo "[generate_openapi] google/api/annotations.proto not found in include paths (${INCLUDE_FLAGS[*]})." >&2
  echo "[generate_openapi] Set GOOGLEAPIS_DIR env var to your cloned googleapis repo, e.g.:" >&2
  echo "  export GOOGLEAPIS_DIR=~/src/googleapis" >&2
  echo "  git clone https://github.com/googleapis/googleapis.git ~/src/googleapis" >&2
  exit 1
fi

# Generate swagger json.
echo "[generate_openapi] Running protoc to emit swagger..." >&2
protoc "${INCLUDE_FLAGS[@]}" --openapiv2_out "$OUT_DIR" --openapiv2_opt logtostderr=true "$PROTO_FILE"

# Expect output file name (plugin may produce a2a.swagger.json or service-specific name).
SWAGGER_JSON=$(ls "$OUT_DIR"/*.swagger.json 2>/dev/null | head -n1 || true)
if [[ -z "$SWAGGER_JSON" ]]; then
  echo "[generate_openapi] No .swagger.json produced" >&2
  exit 1
fi

echo "[generate_openapi] Generated OpenAPI (ephemeral): $SWAGGER_JSON" >&2

# If caller exported OPENAPI_OUTPUT, copy swagger there (used by build_docs for extraction) without committing.
if [ -n "${OPENAPI_OUTPUT:-}" ]; then
  cp "$SWAGGER_JSON" "$OPENAPI_OUTPUT"
  echo "[generate_openapi] Copied swagger to $OPENAPI_OUTPUT" >&2
fi
