# Enterprise Implementation of A2A

The Agent2Agent (A2A) protocol is designed with enterprise requirements at its
core. Rather than inventing new, proprietary standards for security and
operations, A2A aims to integrate seamlessly with existing enterprise
infrastructure and widely adopted best practices. This approach allows
organizations to use their existing investments and expertise in security,
monitoring, governance, and identity management.

A key principle of A2A is that agents are typically **opaque** because they don't
share internal memory, tools, or direct resource access with each other. This
opacity naturally aligns with standard client-server security paradigms,
treating remote agents as standard HTTP-based enterprise applications.

## Transport Level Security (TLS)

Ensuring the confidentiality and integrity of data in transit is fundamental for
any enterprise application.

- **HTTPS Mandate**: All A2A communication in production environments must
    occur over `HTTPS`.
- **Modern TLS Standards**: Implementations should use modern TLS versions.
    TLS 1.2 or higher is recommended. Strong, industry-standard cipher suites
    should be used to protect data from eavesdropping and tampering.
- **Server Identity Verification**: A2A clients should verify the A2A server's
    identity by validating its TLS certificate against trusted certificate
    authorities during the TLS handshake. This prevents man-in-the-middle
    attacks.

## Authentication

A2A delegates authentication to standard web mechanisms. It primarily relies on
HTTP headers and established standards like OAuth2 and OpenID Connect.
Authentication requirements are advertised by the A2A server in its Agent Card.

- **No Identity in Payload**: A2A protocol payloads, such as `JSON-RPC`
    messages, don't carry user or client identity information directly. Identity
    is established at the transport/HTTP layer.
- **Agent Card Declaration**: The A2A server's Agent Card describes the
    authentication schemes it supports in its `security` field and aligns with
    those defined in the OpenAPI Specification for authentication.
- **Out-of-Band Credential Acquisition**: The A2A Client obtains the necessary credentials,
    such as OAuth 2.0 tokens or API keys, through processes external to the A2A protocol itself. Examples include OAuth flows or secure key distribution.
- **HTTP Header Transmission**: Credentials **must** be transmitted in standard
    HTTP headers as per the requirements of the chosen authentication scheme.
    Examples include `Authorization: Bearer <TOKEN>` or `API-Key: <KEY_VALUE>`.
- **Server-Side Validation**: The A2A server **must** authenticate every
    incoming request using the credentials provided in the HTTP headers.
    - If authentication fails or credentials are missing, the server **should**
        respond with a standard HTTP status code:
        - `401 Unauthorized`: If the credentials are missing or invalid. This
            response **should** include a `WWW-Authenticate` header to inform
            the client about the supported authentication methods.
        - `403 Forbidden`: If the credentials are valid, but the authenticated
            client does not have permission to perform the requested action.
- **In-Task Authentication (Secondary Credentials)**: If an agent needs
    additional credentials to access a different system or service during a
    task (for example, to use a specific tool on the user's behalf), the A2A server
    indicates to the client that more information is needed. The client
    is then responsible for obtaining these secondary credentials through a
    process outside of the A2A protocol itself (for example, an OAuth flow) and
    providing them back to the A2A server to continue the task.

## Authorization

Once a client is authenticated, the A2A server is responsible for authorizing
the request. Authorization logic is specific to the agent's implementation,
the data it handles, and applicable enterprise policies.

- **Granular Control**: Authorization **should** be applied based on the
    authenticated identity, which could represent an end user, a client
    application, or both.
- **Skill-Based Authorization**: Access can be controlled on a per-skill
    basis, as advertised in the Agent Card. For example, specific OAuth scopes
    **should** grant an authenticated client access to invoke certain skills but
    not others.
- **Data and Action-Level Authorization**: Agents that interact with backend
    systems, databases, or tools **must** enforce appropriate authorization before
    performing sensitive actions or accessing sensitive data through those
    underlying resources. The agent acts as a gatekeeper.
- **Principle of Least Privilege**: Agents **must** grant only the necessary
    permissions required for a client or user to perform their intended
    operations through the A2A interface.

## AgentCard Security Configuration

This section provides practical examples for configuring security schemes in your
Agent Card. The `securitySchemes` field defines available authentication methods,
while the `security` field specifies which schemes are required for accessing
the agent.

The relationship between these fields works as follows:

1. **`securitySchemes`**: A map of named security scheme definitions. Each scheme
   specifies the authentication mechanism type and its configuration.
2. **`security`**: An array that references schemes defined in `securitySchemes`
   and specifies required scopes (if applicable).

For complete field definitions, see the [A2A Protocol Specification](../specification.md#451-securityscheme).

### OpenID Connect (Recommended for Enterprise SSO)

OpenID Connect is the recommended approach for enterprise environments with
existing identity providers. Clients discover authentication endpoints
automatically from the provider's discovery document.

```json
{
  "securitySchemes": {
    "corporate-sso": {
      "openIdConnectSecurityScheme": {
        "description": "Corporate SSO via identity provider",
        "openIdConnectUrl": "https://identity.example.com/.well-known/openid-configuration"
      }
    }
  },
  "security": [
    { "corporate-sso": ["openid", "profile", "email"] }
  ]
}
```

**Field explanations**:

- `openIdConnectUrl` (**required**): URL to the OpenID Connect discovery document.
  This URL **must** use HTTPS and return a valid OIDC configuration.
- `description` (optional): Human-readable description of the security scheme.
- The `security` array references the scheme name (`corporate-sso`) and lists
  required scopes. Common scopes include `openid`, `profile`, and `email`.

See [Section 4.5.5 OpenIdConnectSecurityScheme](../specification.md#455-openidconnectsecurityscheme)
for the complete field specification.

### API Key (Machine-to-Machine Communication)

API keys are the simplest authentication mechanism, suitable for automated
agent-to-agent communication where OAuth flows are impractical.

```json
{
  "securitySchemes": {
    "agent-api-key": {
      "apiKeySecurityScheme": {
        "description": "API key for automated agent access",
        "location": "header",
        "name": "X-Agent-API-Key"
      }
    }
  },
  "security": [
    { "agent-api-key": [] }
  ]
}
```

**Field explanations**:

- `location` (**required**): Where the API key is transmitted. Valid values:
  - `header`: In an HTTP header (recommended)
  - `query`: As a URL query parameter
  - `cookie`: In an HTTP cookie
- `name` (**required**): The name of the header, query parameter, or cookie.
- `description` (optional): Human-readable description.
- The `security` array uses an empty scope array `[]` since API keys don't
  support scopes.

See [Section 4.5.2 APIKeySecurityScheme](../specification.md#452-apikeysecurityscheme)
for the complete field specification.

### OAuth 2.0 Authorization Code Flow

OAuth 2.0 with the authorization code flow is appropriate when user-delegated
access is required. The agent acts on behalf of an authenticated user.

```json
{
  "securitySchemes": {
    "oauth2": {
      "oauth2SecurityScheme": {
        "description": "OAuth 2.0 with authorization code flow",
        "flows": {
          "authorizationCode": {
            "authorizationUrl": "https://auth.example.com/oauth/authorize",
            "tokenUrl": "https://auth.example.com/oauth/token",
            "scopes": {
              "agent:read": "Read agent capabilities and status",
              "agent:execute": "Execute agent skills and tasks"
            }
          }
        }
      }
    }
  },
  "security": [
    { "oauth2": ["agent:read", "agent:execute"] }
  ]
}
```

**Field explanations**:

- `flows` (**required**): Contains the OAuth flow configuration. The A2A
  specification supports:
  - `authorizationCode`: Standard authorization code flow
  - `clientCredentials`: Machine-to-machine without user context
  - `implicit`: Deprecated, not recommended
  - `password`: Resource owner password credentials
- `authorizationUrl` (**required** for authorization code): The OAuth
  authorization endpoint.
- `tokenUrl` (**required**): The OAuth token endpoint.
- `scopes` (**required**): A map of scope names to descriptions documenting
  available permissions.
- The `security` array lists the scopes required to access the agent.

See [Section 4.5.4 OAuth2SecurityScheme](../specification.md#454-oauth2securityscheme)
for the complete field specification.

## AgentCard Signing and Verification

Agent Cards can be digitally signed using JSON Web Signature (JWS) to ensure
authenticity and integrity. Signing is the responsibility of the agent provider,
while verification is performed by clients receiving the Agent Card.

For the complete specification, see [Section 8.4 Agent Card Signing](../specification.md#84-agent-card-signing).

### Why Sign Agent Cards?

In distributed environments where agents from different organizations interact,
signing provides:

- **Authenticity**: Proof that the Agent Card originates from the claimed provider
- **Integrity**: Detection of any tampering after the card was signed
- **Trust**: Clients can verify cards against known public keys

### Signing an Agent Card

The agent provider signs the Agent Card using the following process:

**Step 1: Prepare the Agent Card**

Before signing, prepare the Agent Card content:

1. Remove the `signatures` field if present (to avoid circular dependency)
2. Remove optional fields that have default values (per Protocol Buffer semantics)
3. Keep all required fields, even if they contain default values

**Step 2: Canonicalize using RFC 8785**

Apply JSON Canonicalization Scheme (JCS) as defined in
[RFC 8785](https://tools.ietf.org/html/rfc8785):

- Sort object keys lexicographically
- Normalize number representations
- Remove insignificant whitespace

**Before canonicalization**:

```json
{
  "name": "Example Agent",
  "capabilities": {
    "streaming": false,
    "pushNotifications": true
  },
  "skills": []
}
```

**After canonicalization**:

```json
{"capabilities":{"pushNotifications":true,"streaming":false},"name":"Example Agent","skills":[]}
```

See [Section 8.4.1 Canonicalization Requirements](../specification.md#841-canonicalization-requirements)
for detailed rules.

**Step 3: Create the Protected Header**

Construct a JWS protected header with the required parameters:

```json
{
  "alg": "ES256",
  "typ": "JOSE",
  "kid": "agent-signing-key-2025",
  "jku": "https://agent.example.com/.well-known/jwks.json"
}
```

**Header parameters**:

- `alg` (**required**): Signing algorithm. Recommended: `ES256` (ECDSA with P-256)
- `typ` (recommended): Token type, should be `JOSE`
- `kid` (**required**): Key identifier for the signing key
- `jku` (optional): URL to the JSON Web Key Set containing the public key

**Step 4: Compute the JWS Signature**

Following [RFC 7515](https://tools.ietf.org/html/rfc7515):

1. Base64url-encode the protected header
2. Base64url-encode the canonicalized Agent Card (payload)
3. Construct the signing input: `BASE64URL(header) || '.' || BASE64URL(payload)`
4. Sign with your private key using the algorithm specified in `alg`
5. Base64url-encode the resulting signature bytes

**Step 5: Construct the AgentCardSignature**

Add the signature to the Agent Card's `signatures` array:

```json
{
  "signatures": [
    {
      "protected": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpPU0UiLCJraWQiOiJhZ2VudC1zaWduaW5nLWtleS0yMDI1Iiwiamt1IjoiaHR0cHM6Ly9hZ2VudC5leGFtcGxlLmNvbS8ud2VsbC1rbm93bi9qd2tzLmpzb24ifQ",
      "signature": "MEUCIQDKZokx9..."
    }
  ]
}
```

**AgentCardSignature fields**:

- `protected` (**required**): Base64url-encoded protected header JSON
- `signature` (**required**): Base64url-encoded signature bytes
- `header` (optional): Unprotected header as a JSON object (not base64url-encoded)

See [Section 4.4.7 AgentCardSignature](../specification.md#447-agentcardsignature)
for the complete field specification.

### Publishing Your Public Key (JWKS)

Distribute your public key via a JSON Web Key Set (JWKS) at the URL specified
in the `jku` header parameter:

```json
{
  "keys": [
    {
      "kty": "EC",
      "crv": "P-256",
      "kid": "agent-signing-key-2025",
      "use": "sig",
      "x": "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU",
      "y": "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0"
    }
  ]
}
```

**JWKS best practices**:

- Host at a well-known URL (e.g., `/.well-known/jwks.json`)
- Serve over HTTPS only
- Include `kid` matching the signature's protected header
- Support key rotation by including multiple keys

### Verifying an Agent Card Signature

Clients receiving signed Agent Cards should verify signatures before trusting
the card content.

**Verification Workflow**:

1. **Extract the signature**: Get the first (or a trusted) entry from the
   `signatures` array

2. **Decode the protected header**: Base64url-decode the `protected` field to
   extract `kid` and `jku`

3. **Retrieve the public key**: Fetch the JWKS from `jku` and find the key
   matching `kid`. Use cached keys if the URL is unavailable.

4. **Prepare the Agent Card**: Remove the `signatures` field and apply the same
   canonicalization as the signing process (RFC 8785)

5. **Verify the JWS**: Use a standard JWS library to verify the signature
   against the canonicalized payload

6. **Accept or reject**: If verification succeeds, trust the Agent Card. If it
   fails, reject the card.

See [Section 8.4.3 Signature Verification](../specification.md#843-signature-verification)
for complete verification requirements.

### Error Handling

| Condition | Recommended Action |
|-----------|-------------------|
| No `signatures` field | Treat as unsigned. Policy determines acceptance. |
| `jku` URL unreachable | Fall back to cached keys. Fail if no cached key available. |
| Key `kid` not found | Reject the signature. |
| Key expired or revoked | Reject the signature. |
| Signature invalid | Reject the Agent Card. |
| Multiple signatures | Verify at least one signature from a trusted issuer. |

### Multiple Signatures

Agent Cards **may** contain multiple signatures to support:

- **Key rotation**: Old and new keys sign during transition periods
- **Multiple issuers**: Different organizations vouch for the same agent
- **Algorithm migration**: Signatures with both legacy and modern algorithms

Clients **should** verify at least one signature from a trusted issuer before
accepting the Agent Card.

## Data Privacy and Confidentiality

Protecting sensitive data exchanged between agents is paramount, requiring
strict adherence to privacy regulations and best practices.

- **Sensitivity Awareness**: Implementers must be acutely aware of the
    sensitivity of data exchanged in Message and Artifact parts of A2A
    interactions.
- **Compliance**: Ensure compliance with relevant data privacy regulations
    such as GDPR, CCPA, and HIPAA, based on the domain and data involved.
- **Data Minimization**: Avoid including or requesting unnecessarily sensitive
    information in A2A exchanges.
- **Secure Handling**: Protect data both in transit, using TLS as mandated,
    and at rest if persisted by agents, according to enterprise data security
    policies and regulatory requirements.

## Tracing, Observability, and Monitoring

A2A's reliance on HTTP allows for straightforward integration with standard
enterprise tracing, logging, and monitoring tools, providing critical visibility
into inter-agent workflows.

- **Distributed Tracing**: A2A Clients and Servers **should** participate in
    distributed tracing systems. For example, use OpenTelemetry to propagate
    trace context, including trace IDs and span IDs, through standard HTTP
    headers, such as W3C Trace Context headers. This enables end-to-end
    visibility for debugging and performance analysis.
- **Comprehensive Logging**: Log details on both client and server, including
    taskId, sessionId, correlation IDs, and trace context for troubleshooting
    and auditing.
- **Metrics**: A2A servers should expose key operational metrics, such as
    request rates, error rates, task processing latency, and resource
    utilization, to enable performance monitoring, alerting, and capacity
    planning.
- **Auditing**: Audit significant events, such as task creation, critical
    state changes, and agent actions, especially when involving sensitive data
    or high-impact operations.

## API Management and Governance

For A2A servers exposed externally, across organizational boundaries, or even within
large enterprises, integration with API Management solutions is highly recommended,
as this provides:

- **Centralized Policy Enforcement**: Consistent application of security
    policies such as authentication and authorization, rate limiting, and quotas.
- **Traffic Management**: Load balancing, routing, and mediation.
- **Analytics and Reporting**: Insights into agent usage, performance, and
    trends.
- **Developer Portals**: Facilitate discovery of A2A-enabled agents, provide
documentation such as Agent Cards, and streamline onboarding for client developers.

By adhering to these enterprise-grade practices, A2A implementations can be
deployed securely, reliably, and manageably within complex organizational
environments. This fosters trust and enables scalable inter-agent collaboration.
