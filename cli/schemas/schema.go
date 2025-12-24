// Package schemas provides embedded JSON schemas for the A2A CLI.
package schemas

import (
	_ "embed"
)

// AgentCardSchema contains the embedded Agent Card JSON Schema.
//
//go:embed agentcard.json
var AgentCardSchema string
