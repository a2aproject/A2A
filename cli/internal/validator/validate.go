package validator

import (
	"encoding/json"
	"fmt"
	"regexp"
	"strconv"
	"strings"

	"github.com/a2aproject/a2a/cli/internal/agentcard"
	"github.com/santhosh-tekuri/jsonschema/v5"
	"gopkg.in/yaml.v3"
)

// Validate validates an Agent Card against the JSON Schema.
func Validate(data []byte, format agentcard.FileFormat) (*agentcard.ValidationResult, error) {
	// Convert YAML to JSON if needed
	var jsonData []byte
	var err error

	if format == agentcard.FormatYAML {
		jsonData, err = yamlToJSON(data)
		if err != nil {
			return nil, fmt.Errorf("failed to convert YAML to JSON: %w", err)
		}
	} else {
		jsonData = data
	}

	// Parse JSON for validation
	var v interface{}
	if err := json.Unmarshal(jsonData, &v); err != nil {
		return &agentcard.ValidationResult{
			Valid: false,
			Errors: []agentcard.ValidationError{
				{
					Path:    "$",
					Message: fmt.Sprintf("Invalid JSON: %s", err.Error()),
				},
			},
		}, nil
	}

	// Get compiled schema
	schema, err := GetAgentCardSchema()
	if err != nil {
		return nil, fmt.Errorf("failed to get schema: %w", err)
	}

	// Validate against schema
	if err := schema.Validate(v); err != nil {
		validationErr, ok := err.(*jsonschema.ValidationError)
		if !ok {
			return nil, fmt.Errorf("unexpected validation error type: %w", err)
		}

		errors := extractErrors(validationErr, string(data))
		return &agentcard.ValidationResult{
			Valid:  false,
			Errors: errors,
		}, nil
	}

	// Generate warnings for optional best practices
	warnings := generateWarnings(v)

	return &agentcard.ValidationResult{
		Valid:    true,
		Warnings: warnings,
	}, nil
}

// ValidateFile validates an Agent Card file.
func ValidateFile(path string) (*agentcard.ValidationResult, error) {
	card, err := agentcard.ParseFile(path)
	if err != nil {
		return &agentcard.ValidationResult{
			Valid: false,
			Errors: []agentcard.ValidationError{
				{
					Path:    "$",
					Message: err.Error(),
				},
			},
		}, nil
	}

	// Re-serialize to validate the parsed data
	data, err := card.ToJSON(false)
	if err != nil {
		return nil, fmt.Errorf("failed to serialize card: %w", err)
	}

	return Validate(data, agentcard.FormatJSON)
}

// yamlToJSON converts YAML to JSON.
func yamlToJSON(yamlData []byte) ([]byte, error) {
	var v interface{}
	if err := yaml.Unmarshal(yamlData, &v); err != nil {
		return nil, err
	}

	// Convert map[interface{}]interface{} to map[string]interface{}
	v = convertMapKeys(v)

	return json.Marshal(v)
}

// convertMapKeys converts map[interface{}]interface{} to map[string]interface{}
// This is needed because YAML unmarshals maps with interface{} keys.
func convertMapKeys(v interface{}) interface{} {
	switch x := v.(type) {
	case map[interface{}]interface{}:
		m := make(map[string]interface{})
		for k, val := range x {
			m[fmt.Sprintf("%v", k)] = convertMapKeys(val)
		}
		return m
	case map[string]interface{}:
		m := make(map[string]interface{})
		for k, val := range x {
			m[k] = convertMapKeys(val)
		}
		return m
	case []interface{}:
		for i, val := range x {
			x[i] = convertMapKeys(val)
		}
	}
	return v
}

// extractErrors extracts validation errors from a jsonschema.ValidationError.
func extractErrors(err *jsonschema.ValidationError, sourceData string) []agentcard.ValidationError {
	var errors []agentcard.ValidationError

	for _, cause := range err.Causes {
		errors = append(errors, extractErrors(cause, sourceData)...)
	}

	if len(err.Causes) == 0 {
		path := jsonPointerToPath(err.InstanceLocation)
		line := findLineNumber(sourceData, path)

		errors = append(errors, agentcard.ValidationError{
			Path:    path,
			Message: err.Message,
			Line:    line,
		})
	}

	return errors
}

// jsonPointerToPath converts a JSON pointer to a readable path.
func jsonPointerToPath(pointer string) string {
	if pointer == "" || pointer == "/" {
		return "$"
	}

	// Remove leading slash
	pointer = strings.TrimPrefix(pointer, "/")

	// Split by slash
	parts := strings.Split(pointer, "/")

	// Build path
	var result strings.Builder
	result.WriteString("$")

	for _, part := range parts {
		// Unescape JSON pointer encoding
		part = strings.ReplaceAll(part, "~1", "/")
		part = strings.ReplaceAll(part, "~0", "~")

		// Check if it's an array index
		if _, err := strconv.Atoi(part); err == nil {
			result.WriteString("[")
			result.WriteString(part)
			result.WriteString("]")
		} else {
			result.WriteString(".")
			result.WriteString(part)
		}
	}

	return result.String()
}

// findLineNumber attempts to find the line number for a given path.
func findLineNumber(data string, path string) int {
	// Simple heuristic: search for the last key in the path
	parts := strings.Split(path, ".")
	if len(parts) == 0 {
		return 0
	}

	lastPart := parts[len(parts)-1]
	// Remove array index if present
	if idx := strings.Index(lastPart, "["); idx != -1 {
		lastPart = lastPart[:idx]
	}

	if lastPart == "" || lastPart == "$" {
		return 1
	}

	// Search for the key in the data
	pattern := fmt.Sprintf(`"%s"\s*:`, regexp.QuoteMeta(lastPart))
	re := regexp.MustCompile(pattern)
	loc := re.FindStringIndex(data)

	if loc == nil {
		return 0
	}

	// Count newlines before the match
	return strings.Count(data[:loc[0]], "\n") + 1
}

// generateWarnings generates warnings for optional best practices.
func generateWarnings(v interface{}) []agentcard.ValidationError {
	var warnings []agentcard.ValidationError

	card, ok := v.(map[string]interface{})
	if !ok {
		return warnings
	}

	// Check for missing optional but recommended fields
	if _, ok := card["provider"]; !ok {
		warnings = append(warnings, agentcard.ValidationError{
			Path:    "$.provider",
			Message: "Consider adding provider information for better discoverability",
		})
	}

	if _, ok := card["documentationUrl"]; !ok {
		warnings = append(warnings, agentcard.ValidationError{
			Path:    "$.documentationUrl",
			Message: "Consider adding documentation URL for users",
		})
	}

	if _, ok := card["supportedInterfaces"]; !ok {
		warnings = append(warnings, agentcard.ValidationError{
			Path:    "$.supportedInterfaces",
			Message: "Consider adding supported interfaces for client connectivity",
		})
	}

	// Check skills for missing optional fields
	if skills, ok := card["skills"].([]interface{}); ok {
		for i, skill := range skills {
			if s, ok := skill.(map[string]interface{}); ok {
				if _, ok := s["examples"]; !ok {
					warnings = append(warnings, agentcard.ValidationError{
						Path:    fmt.Sprintf("$.skills[%d].examples", i),
						Message: "Consider adding examples to help users understand the skill",
					})
				}
			}
		}
	}

	return warnings
}
