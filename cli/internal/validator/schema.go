// Package validator provides validation utilities for Agent Cards.
package validator

import (
	"fmt"
	"strings"
	"sync"

	"github.com/a2aproject/a2a/cli/schemas"
	"github.com/santhosh-tekuri/jsonschema/v5"
)

var (
	agentCardSchema *jsonschema.Schema
	schemaOnce      sync.Once
	schemaErr       error
)

// GetAgentCardSchema returns the compiled Agent Card JSON Schema.
func GetAgentCardSchema() (*jsonschema.Schema, error) {
	schemaOnce.Do(func() {
		agentCardSchema, schemaErr = loadSchema()
	})
	return agentCardSchema, schemaErr
}

// loadSchema loads and compiles the Agent Card schema.
func loadSchema() (*jsonschema.Schema, error) {
	if schemas.AgentCardSchema == "" {
		return nil, fmt.Errorf("schema data is empty")
	}

	compiler := jsonschema.NewCompiler()
	compiler.Draft = jsonschema.Draft7

	if err := compiler.AddResource("agentcard.json", strings.NewReader(schemas.AgentCardSchema)); err != nil {
		return nil, fmt.Errorf("failed to add schema resource: %w", err)
	}

	schema, err := compiler.Compile("agentcard.json")
	if err != nil {
		return nil, fmt.Errorf("failed to compile schema: %w", err)
	}

	return schema, nil
}

// LoadSchemaFromBytes compiles a schema from raw bytes.
func LoadSchemaFromBytes(data []byte) (*jsonschema.Schema, error) {
	compiler := jsonschema.NewCompiler()
	compiler.Draft = jsonschema.Draft7

	if err := compiler.AddResource("schema.json", strings.NewReader(string(data))); err != nil {
		return nil, fmt.Errorf("failed to add schema resource: %w", err)
	}

	schema, err := compiler.Compile("schema.json")
	if err != nil {
		return nil, fmt.Errorf("failed to compile schema: %w", err)
	}

	return schema, nil
}
