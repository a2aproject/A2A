# A2A JSON Artifact

`a2a.json` is a **non-normative build artifact** derived from the canonical proto definition at `specification/grpc/a2a.proto`. It is generated during builds and intentionally **not** committed to source control.

Generation pipeline:

1. `scripts/proto_to_json_schema.sh` converts proto directly to JSON Schema using bufbuild's `protoc-gen-jsonschema` plugin.
2. The resulting `a2a.json` (JSON Schema 2020-12 bundle) is copied to `docs/spec-json/a2a.json` for site publishing.

The build uses `protoc` with `protoc-gen-jsonschema` plugin and `jq` for bundling. Only source (`a2a.proto`) and scripts remain under version control.

The artifact is generated automatically in:

- Local docs builds (`scripts/build_docs.sh`)
- CI workflow (`.github/workflows/generate-a2a-json.yml`) on proto changes

## Do Not Edit

Do **NOT** edit `a2a.json` manually. Update the proto instead. The file is transient and will be regenerated.

## Building the A2A JSON Artifact Locally

To build the `a2a.json` artifact locally, you'll need several dependencies depending on your operating system. This is useful for contributors who want to preview changes before submitting pull requests.

<details>
<summary>macOS/Linux</summary>

### Prerequisites for macOS/Linux

1. **Homebrew (macOS) or apt-get (Debian/Ubuntu)**
   - **macOS**: Install from [brew.sh](https://brew.sh/)
   - **Debian/Ubuntu**: `apt-get` is pre-installed.

2. **Python with pip**

   ```bash
   # Verify installation:
   python3 --version
   pip3 --version
   ```

3. **Core build tools (`protoc`, `go`, `jq`)**
   - **macOS**:

     ```bash
     brew install protobuf go jq
     ```

   - **Debian/Ubuntu**:

     ```bash
     sudo apt-get update && sudo apt-get install -y protobuf-compiler golang jq
     ```

4. **protoc-gen-jsonschema plugin**

   ```bash
   # Install via Go (requires Go to be installed first):
   go install github.com/bufbuild/protoschema-plugins/cmd/protoc-gen-jsonschema@latest
   ```

5. **Clone googleapis repository**

   ```bash
   # Clone to a location like $HOME/googleapis
   git clone https://github.com/googleapis/googleapis.git $HOME/googleapis
   export GOOGLEAPIS_DIR=$HOME/googleapis

   # To persist this, add the export command to your shell profile (e.g., ~/.zshrc or ~/.bashrc)
   echo 'export GOOGLEAPIS_DIR=$HOME/googleapis' >> ~/.bashrc
   ```

6. **Python documentation dependencies**

   ```bash
   # Create and activate virtual environment:
   python3 -m venv .venv-docs
   source .venv-docs/bin/activate

   # Install requirements:
   pip install -r requirements-docs.txt
   ```

#### Building the A2A JSON Artifact on macOS/Linux

Once all prerequisites are installed:

```bash
# Run the build script:
./scripts/build_docs.sh
```

This script handles all necessary steps to generate the `a2a.json` artifact and build the documentation site.
</details>

<details>
<summary>Windows</summary>

#### Windows Prerequisites

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

3. **Go programming language** (for protoc-gen-jsonschema plugin)

   ```powershell
   # Install via WinGet:
   winget install GoLang.Go

   # Or download from https://golang.org/dl/
   # Verify installation:
   go version
   ```

4. **protoc-gen-jsonschema plugin**

   ```powershell
   # Install via Go (requires Go to be installed first):
   go install github.com/bufbuild/protoschema-plugins/cmd/protoc-gen-jsonschema@latest

   # Verify installation (should be in your Go bin directory):
   protoc-gen-jsonschema --version
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

   # To persist this setting, add the following line to your PowerShell profile.
   # You can open your profile for editing by running: notepad $PROFILE
   $env:GOOGLEAPIS_DIR = "C:\path\to\googleapis"
   ```

7. **Python documentation dependencies**

   ```powershell
   # Create and activate virtual environment:
   python -m venv .venv-docs
   .\.venv-docs\Scripts\Activate.ps1

   # Install requirements:
   pip install -r requirements-docs.txt
   ```

#### Building the A2A JSON Artifact on Windows

Once all prerequisites are installed:

```powershell
# Run the build script:
.\scripts\build_docs.ps1

# The documentation will be generated in the ./site directory
# Open site/index.html in your browser to view locally
```

The build script will:

- Generate JSON Schema from Protocol Buffer definitions
- Build the MkDocs site with all content

</details>

#### Troubleshooting

- **protoc errors**: Ensure both `protoc` and the googleapis directory are properly configured
- **jq not found**: Ensure jq is installed and in your `PATH`
- **Python import errors**: Activate the virtual environment and ensure all requirements are installed
- **Missing schemas**: Check that `protoc-gen-jsonschema` is in your `PATH` (run `go env GOPATH` to find Go bin directory)

## Future Work

Planned improvements include:

- Optional OpenAPI v3 conversion and publishing a draft 2020-12 `components.schemas` bundle.
- Automatic alias injection for deprecated names (anyOf wrapper) to ease migrations.
- Validation step ensuring no generated artifacts are reintroduced into git.
