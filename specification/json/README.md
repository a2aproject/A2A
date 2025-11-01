# A2A JSON Artifact

`a2a.json` is a **non-normative build artifact** derived from the canonical proto definition at `specification/grpc/a2a.proto`. It is generated during builds and intentionally **not** committed to source control.

Generation pipeline:

1. `protoc` + `protoc-gen-openapiv2` produce `specification/grpc/openapi/a2a.swagger.json`.
2. `scripts/extract_json_schema.sh` extracts `definitions` into an ephemeral `a2a.json` (draft-07 schema bundle) copied to `docs/spec-json/a2a.json` for site publishing.

Removed artifact: `a2a-openapi-schemas.json` (an intermediate OpenAPI schema expansion) previously committed during early tooling iteration has been deleted to avoid tracking generated content. Only source (`a2a.proto`) and scripts remain under version control.

The artifact is generated automatically in:

- Local docs builds (`scripts/build_docs.sh`)
- CI workflow (`.github/workflows/generate-a2a-json.yml`) on proto changes

## Do Not Edit

Do **NOT** edit `a2a.json` manually. Update the proto instead. The file is transient and will be regenerated.

## Building Documentation on Windows

To build the A2A documentation locally on Windows, you'll need several dependencies. This is useful for contributors who want to preview documentation changes before submitting pull requests.

### Windows Prerequisites

1. **Python with pip** (for MkDocs)
   ```powershell
   # Install Python from python.org or via Microsoft Store
   # Verify installation:
   python --version
   pip --version
   ```

2. **Protocol Buffers compiler (protoc)**
   ```powershell
   # Install via WinGet (recommended):
   winget install Google.Protobuf

   # Verify installation:
   protoc --version
   ```

3. **Go programming language** (for protoc-gen-openapiv2 plugin)
   ```powershell
   # Install via WinGet:
   winget install GoLang.Go

   # Or download from https://golang.org/dl/
   # Verify installation:
   go version
   ```

4. **protoc-gen-openapiv2 plugin**
   ```powershell
   # Install via Go (requires Go to be installed first):
   go install github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-openapiv2@latest

   # Verify installation (should be in your Go bin directory):
   protoc-gen-openapiv2 --version

   # Or download binary from GitHub releases and add to PATH
   ```

5. **jq (JSON processor)**
   ```powershell
   # Install via WinGet:
   winget install jqlang.jq

   # Verify installation:
   jq --version
   ```

6. **Clone googleapis repository**
   ```powershell
   # Clone to any location and set environment variable:
   git clone https://github.com/googleapis/googleapis.git C:\path\to\googleapis
   $env:GOOGLEAPIS_DIR = "C:\path\to\googleapis"

   # Add to your PowerShell profile to persist:
   Add-Content $PROFILE '$env:GOOGLEAPIS_DIR = "C:\path\to\googleapis"'
   ```

7. **Python documentation dependencies**
   ```powershell
   # Create and activate virtual environment:
   python -m venv .venv-docs
   .\.venv-docs\Scripts\Activate.ps1

   # Install requirements:
   pip install -r requirements-docs.txt
   ```

### Building the Documentation

Once all prerequisites are installed:

```powershell
# Run the build script:
.\scripts\build_docs.ps1

# The documentation will be generated in the ./site directory
# Open site/index.html in your browser to view locally
```

The build script will:
- Generate OpenAPI schema from Protocol Buffer definitions
- Extract JSON schemas for documentation
- Build the MkDocs site with all content

### Troubleshooting

- **protoc errors**: Ensure both `protoc` and the googleapis directory are properly configured
- **jq command line too long**: This is automatically handled by using temporary files
- **Python import errors**: Activate the virtual environment and ensure all requirements are installed
- **Missing schemas**: Check that protoc-gen-openapiv2 is in your PATH

## Future Work

Planned improvements include:

- Optional OpenAPI v3 conversion and publishing a draft 2020-12 `components.schemas` bundle.
- Automatic alias injection for deprecated names (anyOf wrapper) to ease migrations.
- Validation step ensuring no generated artifacts are reintroduced into git.
