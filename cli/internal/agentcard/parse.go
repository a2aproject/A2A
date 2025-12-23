package agentcard

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"gopkg.in/yaml.v3"
)

// FileFormat represents the format of an Agent Card file.
type FileFormat string

const (
	FormatJSON    FileFormat = "json"
	FormatYAML    FileFormat = "yaml"
	FormatUnknown FileFormat = "unknown"
)

// ParseOptions configures parsing behavior.
type ParseOptions struct {
	Timeout   time.Duration
	Insecure  bool
	UserAgent string
}

// DefaultParseOptions returns default parsing options.
func DefaultParseOptions() ParseOptions {
	return ParseOptions{
		Timeout:   30 * time.Second,
		Insecure:  false,
		UserAgent: "a2a-cli/1.0",
	}
}

// ParseFile parses an Agent Card from a file.
func ParseFile(path string) (*AgentCard, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read file: %w", err)
	}

	format := DetectFormat(path, data)
	return Parse(data, format)
}

// ParseURL fetches and parses an Agent Card from a URL.
func ParseURL(url string, opts ParseOptions) (*AgentCard, error) {
	client := &http.Client{
		Timeout: opts.Timeout,
	}

	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("User-Agent", opts.UserAgent)
	req.Header.Set("Accept", "application/json, application/yaml, text/yaml")

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch URL: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	// Detect format from content-type header or data
	format := detectFormatFromContentType(resp.Header.Get("Content-Type"))
	if format == FormatUnknown {
		format = DetectFormatFromContent(data)
	}

	return Parse(data, format)
}

// Parse parses Agent Card data in the specified format.
func Parse(data []byte, format FileFormat) (*AgentCard, error) {
	var card AgentCard

	switch format {
	case FormatJSON:
		if err := json.Unmarshal(data, &card); err != nil {
			return nil, fmt.Errorf("failed to parse JSON: %w", err)
		}
	case FormatYAML:
		if err := yaml.Unmarshal(data, &card); err != nil {
			return nil, fmt.Errorf("failed to parse YAML: %w", err)
		}
	default:
		// Try JSON first, then YAML
		if err := json.Unmarshal(data, &card); err != nil {
			if err := yaml.Unmarshal(data, &card); err != nil {
				return nil, fmt.Errorf("failed to parse as JSON or YAML")
			}
		}
	}

	return &card, nil
}

// ParseJSON parses Agent Card data as JSON.
func ParseJSON(data []byte) (*AgentCard, error) {
	return Parse(data, FormatJSON)
}

// ParseYAML parses Agent Card data as YAML.
func ParseYAML(data []byte) (*AgentCard, error) {
	return Parse(data, FormatYAML)
}

// DetectFormat determines the file format from path and content.
func DetectFormat(path string, data []byte) FileFormat {
	// First try by extension
	ext := strings.ToLower(filepath.Ext(path))
	switch ext {
	case ".json":
		return FormatJSON
	case ".yaml", ".yml":
		return FormatYAML
	}

	// Fall back to content detection
	return DetectFormatFromContent(data)
}

// DetectFormatFromContent attempts to detect format by examining content.
func DetectFormatFromContent(data []byte) FileFormat {
	// Trim whitespace
	trimmed := strings.TrimSpace(string(data))
	if len(trimmed) == 0 {
		return FormatUnknown
	}

	// JSON starts with { or [
	if trimmed[0] == '{' || trimmed[0] == '[' {
		return FormatJSON
	}

	// Assume YAML otherwise
	return FormatYAML
}

// detectFormatFromContentType determines format from HTTP Content-Type header.
func detectFormatFromContentType(contentType string) FileFormat {
	ct := strings.ToLower(contentType)
	if strings.Contains(ct, "json") {
		return FormatJSON
	}
	if strings.Contains(ct, "yaml") || strings.Contains(ct, "yml") {
		return FormatYAML
	}
	return FormatUnknown
}

// IsURL checks if the input is a URL.
func IsURL(input string) bool {
	return strings.HasPrefix(input, "http://") || strings.HasPrefix(input, "https://")
}

// ParseFileOrURL parses an Agent Card from either a file path or URL.
func ParseFileOrURL(input string, opts ParseOptions) (*AgentCard, error) {
	if IsURL(input) {
		return ParseURL(input, opts)
	}
	return ParseFile(input)
}

// ToJSON serializes an Agent Card to JSON.
func (c *AgentCard) ToJSON(indent bool) ([]byte, error) {
	if indent {
		return json.MarshalIndent(c, "", "  ")
	}
	return json.Marshal(c)
}

// ToYAML serializes an Agent Card to YAML.
func (c *AgentCard) ToYAML() ([]byte, error) {
	return yaml.Marshal(c)
}
