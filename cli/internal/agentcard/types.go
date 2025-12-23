// Package agentcard provides types and utilities for working with A2A Agent Cards.
package agentcard

import "time"

// AgentCard represents an A2A agent's metadata and capabilities.
// See: https://a2a-protocol.org/latest/specification/#441-agentcard
type AgentCard struct {
	// Required fields
	ProtocolVersion    string            `json:"protocolVersion" yaml:"protocolVersion"`
	Name               string            `json:"name" yaml:"name"`
	Description        string            `json:"description" yaml:"description"`
	Version            string            `json:"version" yaml:"version"`
	Capabilities       AgentCapabilities `json:"capabilities" yaml:"capabilities"`
	DefaultInputModes  []string          `json:"defaultInputModes" yaml:"defaultInputModes"`
	DefaultOutputModes []string          `json:"defaultOutputModes" yaml:"defaultOutputModes"`
	Skills             []AgentSkill      `json:"skills" yaml:"skills"`

	// Optional fields
	SupportedInterfaces       []AgentInterface          `json:"supportedInterfaces,omitempty" yaml:"supportedInterfaces,omitempty"`
	Provider                  *AgentProvider            `json:"provider,omitempty" yaml:"provider,omitempty"`
	DocumentationURL          string                    `json:"documentationUrl,omitempty" yaml:"documentationUrl,omitempty"`
	SecuritySchemes           map[string]SecurityScheme `json:"securitySchemes,omitempty" yaml:"securitySchemes,omitempty"`
	Security                  []Security                `json:"security,omitempty" yaml:"security,omitempty"`
	SupportsExtendedAgentCard bool                      `json:"supportsExtendedAgentCard,omitempty" yaml:"supportsExtendedAgentCard,omitempty"`
	Signatures                []AgentCardSignature      `json:"signatures,omitempty" yaml:"signatures,omitempty"`
	IconURL                   string                    `json:"iconUrl,omitempty" yaml:"iconUrl,omitempty"`
}

// AgentCapabilities defines optional capabilities supported by an agent.
type AgentCapabilities struct {
	Streaming              bool             `json:"streaming,omitempty" yaml:"streaming,omitempty"`
	PushNotifications      bool             `json:"pushNotifications,omitempty" yaml:"pushNotifications,omitempty"`
	StateTransitionHistory bool             `json:"stateTransitionHistory,omitempty" yaml:"stateTransitionHistory,omitempty"`
	Extensions             []AgentExtension `json:"extensions,omitempty" yaml:"extensions,omitempty"`
}

// AgentExtension represents a protocol extension supported by an agent.
type AgentExtension struct {
	URI         string                 `json:"uri" yaml:"uri"`
	Description string                 `json:"description,omitempty" yaml:"description,omitempty"`
	Required    bool                   `json:"required,omitempty" yaml:"required,omitempty"`
	Params      map[string]interface{} `json:"params,omitempty" yaml:"params,omitempty"`
}

// AgentSkill represents a distinct capability that an agent can perform.
type AgentSkill struct {
	// Required fields
	ID          string `json:"id" yaml:"id"`
	Name        string `json:"name" yaml:"name"`
	Description string `json:"description" yaml:"description"`

	// Optional fields
	Tags        []string `json:"tags,omitempty" yaml:"tags,omitempty"`
	InputModes  []string `json:"inputModes,omitempty" yaml:"inputModes,omitempty"`
	OutputModes []string `json:"outputModes,omitempty" yaml:"outputModes,omitempty"`
	Examples    []string `json:"examples,omitempty" yaml:"examples,omitempty"`
}

// AgentInterface represents an endpoint interface for the agent.
type AgentInterface struct {
	URL       string `json:"url" yaml:"url"`
	Transport string `json:"transport,omitempty" yaml:"transport,omitempty"` // "jsonrpc", "grpc", "rest"
}

// AgentProvider represents the service provider of an agent.
type AgentProvider struct {
	URL          string `json:"url" yaml:"url"`
	Organization string `json:"organization" yaml:"organization"`
}

// SecurityScheme defines authentication mechanism.
type SecurityScheme struct {
	Type          string                       `json:"type,omitempty" yaml:"type,omitempty"`
	Description   string                       `json:"description,omitempty" yaml:"description,omitempty"`
	APIKey        *APIKeySecurityScheme        `json:"apiKeySecurityScheme,omitempty" yaml:"apiKeySecurityScheme,omitempty"`
	HTTP          *HTTPAuthSecurityScheme      `json:"httpAuthSecurityScheme,omitempty" yaml:"httpAuthSecurityScheme,omitempty"`
	OAuth2        *OAuth2SecurityScheme        `json:"oauth2SecurityScheme,omitempty" yaml:"oauth2SecurityScheme,omitempty"`
	OpenIDConnect *OpenIDConnectSecurityScheme `json:"openIdConnectSecurityScheme,omitempty" yaml:"openIdConnectSecurityScheme,omitempty"`
	MutualTLS     *MutualTLSSecurityScheme     `json:"mtlsSecurityScheme,omitempty" yaml:"mtlsSecurityScheme,omitempty"`
}

// APIKeySecurityScheme for API key authentication.
type APIKeySecurityScheme struct {
	Description string `json:"description,omitempty" yaml:"description,omitempty"`
	Location    string `json:"location" yaml:"location"` // "query", "header", "cookie"
	Name        string `json:"name" yaml:"name"`
}

// HTTPAuthSecurityScheme for HTTP authentication.
type HTTPAuthSecurityScheme struct {
	Description  string `json:"description,omitempty" yaml:"description,omitempty"`
	Scheme       string `json:"scheme" yaml:"scheme"` // "Bearer", "Basic"
	BearerFormat string `json:"bearerFormat,omitempty" yaml:"bearerFormat,omitempty"`
}

// OAuth2SecurityScheme for OAuth 2.0 authentication.
type OAuth2SecurityScheme struct {
	Description       string      `json:"description,omitempty" yaml:"description,omitempty"`
	Flows             *OAuthFlows `json:"flows" yaml:"flows"`
	OAuth2MetadataURL string      `json:"oauth2MetadataUrl,omitempty" yaml:"oauth2MetadataUrl,omitempty"`
}

// OAuthFlows represents OAuth 2.0 flow configurations.
type OAuthFlows struct {
	Implicit          *OAuthFlow `json:"implicit,omitempty" yaml:"implicit,omitempty"`
	Password          *OAuthFlow `json:"password,omitempty" yaml:"password,omitempty"`
	ClientCredentials *OAuthFlow `json:"clientCredentials,omitempty" yaml:"clientCredentials,omitempty"`
	AuthorizationCode *OAuthFlow `json:"authorizationCode,omitempty" yaml:"authorizationCode,omitempty"`
}

// OAuthFlow represents a single OAuth 2.0 flow configuration.
type OAuthFlow struct {
	AuthorizationURL string            `json:"authorizationUrl,omitempty" yaml:"authorizationUrl,omitempty"`
	TokenURL         string            `json:"tokenUrl,omitempty" yaml:"tokenUrl,omitempty"`
	RefreshURL       string            `json:"refreshUrl,omitempty" yaml:"refreshUrl,omitempty"`
	Scopes           map[string]string `json:"scopes,omitempty" yaml:"scopes,omitempty"`
}

// OpenIDConnectSecurityScheme for OpenID Connect authentication.
type OpenIDConnectSecurityScheme struct {
	Description      string `json:"description,omitempty" yaml:"description,omitempty"`
	OpenIDConnectURL string `json:"openIdConnectUrl" yaml:"openIdConnectUrl"`
}

// MutualTLSSecurityScheme for mutual TLS authentication.
type MutualTLSSecurityScheme struct {
	Description string `json:"description,omitempty" yaml:"description,omitempty"`
}

// Security represents security requirement.
type Security struct {
	Schemes map[string][]string `json:"schemes,omitempty" yaml:"schemes,omitempty"`
}

// AgentCardSignature represents a JWS signature for the Agent Card.
type AgentCardSignature struct {
	Protected string                 `json:"protected" yaml:"protected"`
	Signature string                 `json:"signature" yaml:"signature"`
	Header    map[string]interface{} `json:"header,omitempty" yaml:"header,omitempty"`
}

// ValidationResult represents the outcome of validation.
type ValidationResult struct {
	Valid    bool              `json:"valid"`
	Errors   []ValidationError `json:"errors,omitempty"`
	Warnings []ValidationError `json:"warnings,omitempty"`
}

// ValidationError represents a single validation issue.
type ValidationError struct {
	Path    string `json:"path"`             // JSON path to the error (e.g., "skills[0].id")
	Message string `json:"message"`          // Human-readable error message
	Line    int    `json:"line,omitempty"`   // Line number in source file (if available)
	Column  int    `json:"column,omitempty"` // Column number in source file (if available)
}

// ConnectionTestResult represents the outcome of a connection test.
type ConnectionTestResult struct {
	URL          string        `json:"url"`
	Reachable    bool          `json:"reachable"`
	ResponseTime time.Duration `json:"responseTime"`
	StatusCode   int           `json:"statusCode,omitempty"`
	Error        string        `json:"error,omitempty"`
	TLSValid     bool          `json:"tlsValid,omitempty"`
	TLSExpiry    *time.Time    `json:"tlsExpiry,omitempty"`
	AgentCard    *AgentCard    `json:"agentCard,omitempty"`
}

// SimulationSession maintains state for multi-turn interactions.
type SimulationSession struct {
	ID        string    `json:"id"`
	TaskID    string    `json:"taskId,omitempty"`
	ContextID string    `json:"contextId,omitempty"`
	Messages  []Message `json:"messages"`
	CreatedAt time.Time `json:"createdAt"`
	UpdatedAt time.Time `json:"updatedAt"`
}

// Message represents a single turn in the conversation.
type Message struct {
	Role    string `json:"role"` // "user" or "agent"
	Content string `json:"content"`
	Parts   []Part `json:"parts,omitempty"`
}

// Part represents a section of message content.
type Part struct {
	Text     string                 `json:"text,omitempty"`
	File     *FilePart              `json:"file,omitempty"`
	Data     map[string]interface{} `json:"data,omitempty"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
}

// FilePart represents file content in a message.
type FilePart struct {
	URI       string `json:"uri,omitempty"`
	Bytes     []byte `json:"bytes,omitempty"`
	MediaType string `json:"mediaType,omitempty"`
	Name      string `json:"name,omitempty"`
}
