# A2A Development Container

This devcontainer provides a fully configured development environment for the A2A project with all required dependencies pre-installed.

## What's Included

### Build Tools

- **protoc** (v28.3) - Protocol Buffers compiler
- **protoc-gen-jsonschema** (bufbuild) - JSON Schema generator for protobuf
- **jq** (latest) - JSON processor
- **googleapis** - Google API proto definitions

### Development Tools

- **Python 3.12** with all documentation dependencies
- **Go** (latest) - for protoc plugin compilation

### VS Code Extensions

- Python language support with Pylance
- Buf for Protocol Buffers
- Code Spell Checker

## Usage

### Opening in VS Code

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open this repository in VS Code
3. When prompted, click "Reopen in Container" (or use Command Palette: "Dev Containers: Reopen in Container")
4. Wait for the container to build and dependencies to install

### Building Documentation

Once inside the container:

```bash
# Build all documentation
./scripts/build_docs.sh

# Convert proto to JSON Schema only
./scripts/proto_to_json_schema.sh specification/json/a2a.json
```

### GitHub Codespaces

This devcontainer configuration also works with GitHub Codespaces:

1. Go to the repository on GitHub
2. Click "Code" → "Codespaces" → "Create codespace on [branch]"
3. Wait for the environment to be provisioned

## Benefits

- **Reproducible builds**: Everyone uses the same tool versions
- **No local setup**: No need to install protoc, jq, etc. on your host machine
- **Quick onboarding**: New contributors can start developing immediately
- **CI/CD alignment**: Same environment as CI can use similar container

## Customization

To modify the environment:

- **Add tools**: Edit `.devcontainer/setup.sh`
- **Change Python/Go versions**: Edit `features` in `devcontainer.json`
- **Add VS Code extensions**: Edit `customizations.vscode.extensions` in `devcontainer.json`

## Troubleshooting

### Container build fails

```bash
# Rebuild without cache
Dev Containers: Rebuild Container (without cache)
```

### Tools not found after setup

```bash
# Re-run setup script manually
bash .devcontainer/setup.sh
```
