#!/bin/bash
set -euo pipefail

echo "==> Setting up A2A development environment..."

# Install system dependencies
echo "→ Installing system packages..."
sudo apt-get update
sudo apt-get install -y \
  curl \
  git \
  jq \
  unzip

# Install Protocol Buffers compiler
echo "→ Installing protoc..."
PROTOC_VERSION="28.3"
PROTOC_ZIP="protoc-${PROTOC_VERSION}-linux-x86_64.zip"
curl -fsSL -o /tmp/protoc.zip "https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOC_VERSION}/${PROTOC_ZIP}"
sudo unzip -q /tmp/protoc.zip -d /usr/local
rm /tmp/protoc.zip

# Install protoc-gen-jsonschema (bufbuild)
echo "→ Installing protoc-gen-jsonschema..."
go install github.com/bufbuild/protoschema-plugins/cmd/protoc-gen-jsonschema@latest
go_bin_path="$(go env GOPATH)/bin/protoc-gen-jsonschema"
if [ -f "$go_bin_path" ]; then
  sudo cp "$go_bin_path" /usr/local/bin/
fi

# Install buf CLI
echo "→ Installing buf..."
go install github.com/bufbuild/buf/cmd/buf@latest
go_bin_path="$(go env GOPATH)/bin/buf"
if [ -f "$go_bin_path" ]; then
  sudo cp "$go_bin_path" /usr/local/bin/
fi

# Install googleapis proto files to third_party
echo "→ Installing googleapis..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
GOOGLEAPIS_DIR="$WORKSPACE_DIR/third_party/googleapis"
if [ ! -d "$GOOGLEAPIS_DIR" ]; then
  mkdir -p "$WORKSPACE_DIR/third_party"
  cd "$WORKSPACE_DIR/third_party"
  git clone --depth 1 https://github.com/googleapis/googleapis.git
  cd "$WORKSPACE_DIR"
fi

# Install Python dependencies for documentation
echo "→ Installing Python packages..."
pip install --no-cache-dir -r requirements-docs.txt

# Verify installations
echo ""
echo "==> Verifying installations..."
echo "protoc: $(protoc --version)"
echo "protoc-gen-jsonschema: $(which protoc-gen-jsonschema)"
echo "buf: $(buf --version 2>/dev/null || echo 'not found')"
echo "jq: $(jq --version)"
echo "python: $(python --version)"
echo "go: $(go version)"

echo ""
echo "✓ Development environment ready!"
echo ""
echo "To build documentation:"
echo "  ./scripts/build_docs.sh"
echo ""
echo "To convert proto to JSON Schema:"
echo "  ./scripts/proto_to_json_schema.sh specification/json/a2a.json"
