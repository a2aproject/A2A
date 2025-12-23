// Package output provides output formatting utilities for the CLI.
package output

import (
	"encoding/json"
	"fmt"
	"io"

	"gopkg.in/yaml.v3"
)

// Format represents an output format.
type Format string

const (
	FormatText Format = "text"
	FormatJSON Format = "json"
	FormatYAML Format = "yaml"
)

// ParseFormat parses a format string into a Format.
func ParseFormat(s string) (Format, error) {
	switch s {
	case "text", "":
		return FormatText, nil
	case "json":
		return FormatJSON, nil
	case "yaml", "yml":
		return FormatYAML, nil
	default:
		return "", fmt.Errorf("unknown format: %s (valid: text, json, yaml)", s)
	}
}

// Formatter is the interface for output formatters.
type Formatter interface {
	Format(w io.Writer, data interface{}) error
}

// TextFormatter formats output as human-readable text.
type TextFormatter struct{}

// Format writes text-formatted output.
func (f *TextFormatter) Format(w io.Writer, data interface{}) error {
	// For text format, we expect the data to implement a Stringer or similar
	// The actual formatting is done by type-specific methods
	switch v := data.(type) {
	case string:
		_, err := fmt.Fprintln(w, v)
		return err
	case fmt.Stringer:
		_, err := fmt.Fprintln(w, v.String())
		return err
	default:
		// Fall back to JSON for complex types
		return (&JSONFormatter{Indent: true}).Format(w, data)
	}
}

// JSONFormatter formats output as JSON.
type JSONFormatter struct {
	Indent bool
}

// Format writes JSON-formatted output.
func (f *JSONFormatter) Format(w io.Writer, data interface{}) error {
	encoder := json.NewEncoder(w)
	if f.Indent {
		encoder.SetIndent("", "  ")
	}
	return encoder.Encode(data)
}

// YAMLFormatter formats output as YAML.
type YAMLFormatter struct{}

// Format writes YAML-formatted output.
func (f *YAMLFormatter) Format(w io.Writer, data interface{}) error {
	encoder := yaml.NewEncoder(w)
	encoder.SetIndent(2)
	defer encoder.Close()
	return encoder.Encode(data)
}

// GetFormatter returns a formatter for the specified format.
func GetFormatter(format Format) Formatter {
	switch format {
	case FormatJSON:
		return &JSONFormatter{Indent: true}
	case FormatYAML:
		return &YAMLFormatter{}
	default:
		return &TextFormatter{}
	}
}

// Write formats and writes data to the writer using the specified format.
func Write(w io.Writer, format Format, data interface{}) error {
	return GetFormatter(format).Format(w, data)
}

// WriteJSON writes JSON-formatted output.
func WriteJSON(w io.Writer, data interface{}, indent bool) error {
	return (&JSONFormatter{Indent: indent}).Format(w, data)
}

// WriteYAML writes YAML-formatted output.
func WriteYAML(w io.Writer, data interface{}) error {
	return (&YAMLFormatter{}).Format(w, data)
}
