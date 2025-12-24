# A2A CLI

Command-line interface for working with the A2A (Agent-to-Agent) Protocol.

## Features

- **Generate**: Create Agent Card templates with customizable parameters
- **Validate**: Validate Agent Cards against the A2A protocol specification
- **Test**: Test connectivity to agent endpoints
- **View**: Display agent capabilities and skills in readable format
- **Simulate**: Simulate client-server interactions with agents

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/a2aproject/a2a.git
cd a2a/cli

# Build
make build

# Install to GOPATH/bin
make install
```

## Quick Start

### Generate an Agent Card

```bash
# Generate with defaults
a2a generate

# Generate with custom settings
a2a generate --name "My Agent" --description "A helpful agent" --version "2.0.0"

# Add skills
a2a generate --skill "translate:Translate:Translate text between languages"

# Output as YAML
a2a generate --format yaml -o agent-card.yaml
```

### Validate an Agent Card

```bash
# Validate a local file
a2a validate agent-card.json

# Strict mode (fail on warnings)
a2a validate --strict agent-card.json

# Output as JSON
a2a validate -o json agent-card.json
```

### Test Agent Connectivity

```bash
# Test a URL
a2a test https://agent.example.com

# Test from Agent Card file
a2a test agent-card.json

# Skip TLS verification (development)
a2a test -k https://localhost:8080
```

### View Agent Capabilities

```bash
# View overview
a2a view agent-card.json

# View detailed skills
a2a view --skills agent-card.json

# View security configuration
a2a view --security agent-card.json

# View from URL
a2a view https://agent.example.com/.well-known/agent-card.json
```

### Simulate Interactions

```bash
# Send a single message
a2a simulate -m "Hello, what can you do?" https://agent.example.com

# Interactive mode
a2a simulate https://agent.example.com

# Stream responses
a2a simulate --stream -m "Tell me a story" https://agent.example.com

# Log session
a2a simulate --log session.json https://agent.example.com
```

## Commands

| Command    | Description                              |
|------------|------------------------------------------|
| `generate` | Generate an Agent Card template          |
| `validate` | Validate an Agent Card file              |
| `test`     | Test connectivity to an agent endpoint   |
| `view`     | View agent capabilities and skills       |
| `simulate` | Simulate client-server interaction       |
| `version`  | Display version information              |

## Global Flags

| Flag          | Description                      |
|---------------|----------------------------------|
| `-o, --output`| Output format: text, json, yaml  |
| `-v, --verbose`| Enable verbose output           |
| `-h, --help`  | Help for any command             |

## Shell Completion

```bash
# Bash
a2a completion bash > /etc/bash_completion.d/a2a

# Zsh
a2a completion zsh > "${fpath[1]}/_a2a"

# Fish
a2a completion fish > ~/.config/fish/completions/a2a.fish
```

```powershell
# PowerShell - Load in current session
a2a completion powershell | Out-String | Invoke-Expression

# PowerShell - Make persistent (add to profile)
a2a completion powershell > a2a.ps1
# Then add `. /path/to/a2a.ps1` to your PowerShell profile
```

## Exit Codes

| Code | Description          |
|------|----------------------|
| 0    | Success              |
| 1    | General error        |
| 2    | Invalid arguments    |
| 3    | File not found       |
| 4    | Validation failed    |
| 5    | Network error        |

## Development

```bash
# Run tests
make test

# Run linter
make lint

# Format code
make fmt

# Cross-compile
make build-all
```

## License

See [LICENSE](../LICENSE) for details.
