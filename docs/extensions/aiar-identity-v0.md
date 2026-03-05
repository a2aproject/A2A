# Agent Identity and Accountability Reporting (AIAR) Extension — v0

**Extension URI:** `https://github.com/a2aproject/A2A/extensions/aiar.identity/v0`

**Status:** Draft (v0 — MVP)

**Authors:** A2A Community Contributors

---

## Abstract

Discovery is not identity. Runtime authentication is not ownership.

The A2A protocol enables agents to discover one another via Agent Cards and
communicate through well-defined message flows. However, the base protocol does
not provide a mechanism for a client to **verify** that a given Agent Card
or runtime endpoint is bound to a **verifiable issuer identity**.

The Agent Identity and Accountability Reporting (AIAR) extension addresses this
gap by introducing:

1. **Verifiable identity binding** in Agent Cards via JWS signatures tied to a
    declared issuer.
2. **Runtime proof-of-possession** so clients can confirm the agent endpoint
    controls the signing key.
3. **Optional RPC methods** for programmatic retrieval of identity proofs and
    issuer metadata.

This extension is fully opt-in, additive, and backwards-compatible. It does
**not** attempt to solve global governance, reputation, or revocation
infrastructure. Instead, it provides the cryptographic primitives and
metadata structure that higher-level trust frameworks can build upon.

## Motivation

| Scenario | Gap without AIAR |
| :--- | :--- |
| Client discovers an Agent Card at `/.well-known/agent-card.json` | No proof the card was published by the claimed organization |
| Client sends sensitive data to an agent endpoint | No proof the endpoint is operated by the Agent Card's issuer |
| Agent Card is served from a CDN or registry | No tamper-evidence; card could be modified in transit |
| Multiple agents claim to be from "Acme Corp" | No way to distinguish legitimate agents from imposters |

## Terminology

| Term | Definition |
| :--- | :--- |
| **Issuer** | The organization or entity that publishes and vouches for an agent. Identified by a URI (e.g., DID, HTTPS URL). |
| **Subject Agent** | The agent whose identity is being asserted by the issuer. |
| **Agent Card** | The self-describing manifest for an agent, as defined by the A2A specification. |
| **Proof Bundle** | A collection of cryptographic proofs (JWS, timestamps, optional attestations) that bind an agent to its issuer. |
| **Trusted Issuer Set** | A client-defined policy listing issuers the client is willing to trust. This is NOT defined by this extension; it is a client implementation concern. |
| **Key ID (kid)** | A unique identifier for the signing key, as used in JWS headers (RFC 7515). |
| **JCS** | JSON Canonicalization Scheme (RFC 8785), used to produce a deterministic representation of JSON objects for signing. |

## Extension Type

This extension is a combination of:

- **Data-only**: Adds identity metadata to Agent Card `params`.
- **Profile**: Adds structured request/response data in message `metadata`.
- **Method (Extended Skills)**: Defines optional RPC methods (`aiar.*`).

## Activation

### Declaration

Agents that support this extension declare it in their Agent Card under
`capabilities.extensions`:

```json
{
    "uri": "https://github.com/a2aproject/A2A/extensions/aiar.identity/v0",
    "description": "Verifiable agent identity and accountability reporting",
    "required": false,
    "params": {
        "issuer": "https://example.com",
        "kid": "example-key-2025-01",
        "signedFields": "card",
        "jws": {
            "protected": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImV4YW1wbGUta2V5LTIwMjUtMDEifQ",
            "signature": "MEUCIQC...base64url..."
        }
    }
}
```

### Client Opt-In

Clients opt in to this extension by including the extension URI in the
`A2A-Extensions` HTTP header (or gRPC metadata) when making requests:

```http
POST /message:send HTTP/1.1
Host: agent.example.com
Content-Type: application/json
A2A-Extensions: https://github.com/a2aproject/A2A/extensions/aiar.identity/v0
```

### Agent Response

When the extension is successfully activated, the agent includes the extension
URI in the response `A2A-Extensions` header:

```http
HTTP/1.1 200 OK
Content-Type: application/json
A2A-Extensions: https://github.com/a2aproject/A2A/extensions/aiar.identity/v0
```

If the agent does not support this extension, it ignores the activation request
and omits the URI from the response header.

## Agent Card Identity Parameters

When an agent declares support for this extension, the `params` field of the
`AgentExtension` object contains the following fields:

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `issuer` | string | Yes | URI identifying the issuing organization (HTTPS URL or DID). |
| `kid` | string | Yes | Key ID referencing the signing key. The key material SHOULD be resolvable via the issuer's JWKS endpoint (`{issuer}/.well-known/jwks.json`) or DID document. |
| `signedFields` | string | Yes | What is signed. Value MUST be `"card"` (the entire Agent Card minus the AIAR extension's `jws` field). |
| `jws` | object | Yes | JWS JSON Serialization (RFC 7515 §7.2) containing the signature over the canonical Agent Card. See [Signing Target](#signing-target). |
| `jws.protected` | string | Yes | Base64url-encoded protected JWS header. MUST include `alg` and `kid`. |
| `jws.signature` | string | Yes | Base64url-encoded signature value. |
| `jws.header` | object | No | Unprotected JWS header values. |
| `attestations` | array | No | Optional array of third-party attestation objects. See [Attestations](#attestations). |

### Signing Target

The signing target is a **canonical JSON representation** of the Agent Card,
constructed as follows:

1. Start with the complete Agent Card JSON object.
2. Remove the `jws` field from the AIAR extension's `params` object (i.e.,
    remove `capabilities.extensions[aiar].params.jws`). All other fields,
    including `params.issuer`, `params.kid`, and `params.signedFields`,
    remain in the signing input.
3. Apply [RFC 8785 (JCS)](https://www.rfc-editor.org/rfc/rfc8785) canonicalization
    to produce a deterministic UTF-8 byte string.
4. The resulting byte string is the JWS payload. The JWS MAY use either
    attached or detached payload (RFC 7515 Appendix F). If detached, the
    verifier reconstructs the payload using the same canonicalization steps.

**Recommended algorithms** (in order of preference):

- `ES256` (ECDSA using P-256 and SHA-256)
- `EdDSA` (Ed25519)
- `RS256` (RSASSA-PKCS1-v1_5 using SHA-256) — for legacy compatibility only

### Attestations

The optional `attestations` array allows issuers to include third-party
credentials that vouch for the agent's identity. Each attestation object has:

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `type` | string | Yes | Attestation type. Values: `"uri"` (reference) or `"vc"` (embedded Verifiable Credential). |
| `value` | string | Yes | For `"uri"`: a URL to the attestation document. For `"vc"`: an embedded W3C Verifiable Credential (JWT or JSON-LD compact form). |
| `description` | string | No | Human-readable description of the attestation. |

### Verification Steps (Agent Card)

A client verifying an Agent Card's identity binding MUST perform these steps:

1. **Extract** the AIAR extension from `capabilities.extensions[]` by matching
    the extension URI.
2. **Decode** the `jws.protected` header and extract `alg` and `kid`.
3. **Resolve** the signing key using the `kid`:
    - If `issuer` is an HTTPS URL: fetch `{issuer}/.well-known/jwks.json` and
        find the key matching `kid`.
    - If `issuer` is a DID: resolve the DID document and find the
        verification method matching `kid`.
4. **Reconstruct** the signing target by removing `params.jws` from the AIAR
    extension entry and applying JCS canonicalization to the resulting Agent Card.
5. **Verify** the JWS signature using the resolved key and reconstructed payload.
6. **Check issuer trust**: verify that `issuer` is in the client's Trusted
    Issuer Set (a client policy decision).
7. **Optionally validate** any `attestations` entries.

## Message-Level Identity Requests and Proofs

### Request Extension Data

When a client wants to request identity proof at the message level, it includes
an identity request in the `SendMessageRequest.metadata` map, keyed by the
extension URI with a `/request` suffix:

**Metadata key:** `https://github.com/a2aproject/A2A/extensions/aiar.identity/v0/request`

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `minAssurance` | string | Yes | Minimum assurance level required. Values: `"self-signed"`, `"org-signed"`, `"third-party-signed"`. |
| `acceptableIssuers` | array of strings | No | List of issuer URIs the client will accept. If omitted, the client accepts any issuer in its local Trusted Issuer Set. |
| `requireFreshnessSeconds` | integer | No | Maximum age (in seconds) of the proof bundle. If omitted, the client accepts any valid proof. |

**Assurance levels:**

| Level | Meaning |
| :--- | :--- |
| `self-signed` | The agent's key is self-asserted; no organizational binding required. |
| `org-signed` | The signing key is bound to an organizational issuer identity. |
| `third-party-signed` | The identity includes at least one third-party attestation. |

**Example request:**

```http
POST /message:send HTTP/1.1
Host: agent.example.com
Content-Type: application/json
A2A-Extensions: https://github.com/a2aproject/A2A/extensions/aiar.identity/v0

{
    "jsonrpc": "2.0",
    "method": "SendMessage",
    "id": "req-42",
    "params": {
        "message": {
            "messageId": "msg-001",
            "role": "ROLE_USER",
            "parts": [{"text": "Process this invoice."}],
            "extensions": [
                "https://github.com/a2aproject/A2A/extensions/aiar.identity/v0"
            ]
        },
        "metadata": {
            "https://github.com/a2aproject/A2A/extensions/aiar.identity/v0/request": {
                "minAssurance": "org-signed",
                "requireFreshnessSeconds": 300
            }
        }
    }
}
```

### Response Proof Bundle

When the extension is active and the agent supports the requested assurance
level, the agent includes a proof bundle in the response `Task.metadata` (or
`Message.metadata` for direct message responses), keyed by the extension URI
with a `/proof_bundle` suffix:

**Metadata key:** `https://github.com/a2aproject/A2A/extensions/aiar.identity/v0/proof_bundle`

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `cardDigest` | string | Yes | Base64url-encoded SHA-256 hash of the JCS-canonicalized Agent Card (same canonical form used for the Agent Card signature). |
| `issuer` | string | Yes | The issuer URI (must match the Agent Card's AIAR `params.issuer`). |
| `kid` | string | Yes | The key ID used for signing this proof. |
| `proofOfPossession` | object | Yes | A JWS proving the agent currently controls the signing key. See below. |
| `issuedAt` | string | Yes | ISO 8601 timestamp of when this proof was generated. |
| `expiresAt` | string | Yes | ISO 8601 timestamp of when this proof expires. |
| `attestations` | array | No | Optional attestations (same schema as Agent Card attestations). |

#### Proof of Possession

The `proofOfPossession` field is a JWS (compact or JSON serialization) whose
payload is a JSON object containing:

```json
{
    "iss": "https://example.com",
    "sub": "https://agent.example.com/.well-known/agent-card.json",
    "cardDigest": "sha256:base64url-encoded-hash",
    "iat": 1735689600,
    "exp": 1735689900,
    "nonce": "client-provided-or-server-generated"
}
```

| Field | Type | Description |
| :--- | :--- | :--- |
| `iss` | string | The issuer URI. |
| `sub` | string | The Agent Card URL or agent identifier. |
| `cardDigest` | string | SHA-256 digest of the canonical Agent Card, prefixed with `sha256:`. |
| `iat` | integer | Issued-at Unix timestamp. |
| `exp` | integer | Expiration Unix timestamp. |
| `nonce` | string | A nonce for replay prevention. Server-generated if not provided by client. |

**Example response:**

```json
{
    "jsonrpc": "2.0",
    "id": "req-42",
    "result": {
        "id": "task-101",
        "contextId": "ctx-001",
        "status": {
            "state": "TASK_STATE_COMPLETED",
            "message": {
                "messageId": "msg-002",
                "role": "ROLE_AGENT",
                "parts": [{"text": "Invoice processed successfully."}],
                "extensions": [
                    "https://github.com/a2aproject/A2A/extensions/aiar.identity/v0"
                ]
            }
        },
        "metadata": {
            "https://github.com/a2aproject/A2A/extensions/aiar.identity/v0/proof_bundle": {
                "cardDigest": "sha256:abc123def456...",
                "issuer": "https://example.com",
                "kid": "example-key-2025-01",
                "proofOfPossession": {
                    "protected": "eyJhbGciOiJFUzI1NiIsImtpZCI6ImV4YW1wbGUta2V5LTIwMjUtMDEifQ",
                    "payload": "eyJpc3MiOiJodHRwczovL2V4YW1wbGUuY29tIi...",
                    "signature": "MEUCIQD...base64url..."
                },
                "issuedAt": "2025-12-01T00:00:00Z",
                "expiresAt": "2025-12-01T00:05:00Z"
            }
        }
    }
}
```

## Optional RPC Methods

This extension defines the following optional RPC methods. Agents MAY implement
them. Clients MUST handle a "method not found" error gracefully if the agent
does not support them.

These methods follow the JSON-RPC 2.0 calling convention used by A2A.

### `aiar.getProofBundle`

Returns a fresh proof bundle for the agent's identity.

**Request:**

```json
{
    "jsonrpc": "2.0",
    "method": "aiar.getProofBundle",
    "id": "rpc-1",
    "params": {
        "includeAttestations": true
    }
}
```

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `includeAttestations` | boolean | No | If `true`, include attestations in the response. Defaults to `false`. |

**Response:**

```json
{
    "jsonrpc": "2.0",
    "id": "rpc-1",
    "result": {
        "cardDigest": "sha256:abc123def456...",
        "issuer": "https://example.com",
        "kid": "example-key-2025-01",
        "proofOfPossession": {
            "protected": "eyJhbGciOiJFUzI1NiJ9",
            "payload": "eyJpc3MiOi...",
            "signature": "MEUCIQD..."
        },
        "issuedAt": "2025-12-01T00:00:00Z",
        "expiresAt": "2025-12-01T00:05:00Z",
        "attestations": [
            {
                "type": "uri",
                "value": "https://trust-registry.example.org/attestations/acme-corp",
                "description": "Acme Corp verified agent operator"
            }
        ]
    }
}
```

### `aiar.getIssuer`

Returns metadata about the agent's issuer.

**Request:**

```json
{
    "jsonrpc": "2.0",
    "method": "aiar.getIssuer",
    "id": "rpc-2",
    "params": {}
}
```

**Response:**

```json
{
    "jsonrpc": "2.0",
    "id": "rpc-2",
    "result": {
        "issuer": "https://example.com",
        "issuerUrl": "https://example.com/about",
        "policyUrl": "https://example.com/agent-policy",
        "contact": "security@example.com"
    }
}
```

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `issuer` | string | Yes | The issuer URI (same as in Agent Card). |
| `issuerUrl` | string | No | URL with human-readable information about the issuer. |
| `policyUrl` | string | No | URL to the issuer's agent operation policy. |
| `contact` | string | No | Contact information for security or identity inquiries. |

### `aiar.rotateKeys` (Deferred)

Key rotation is an important operational concern but is deferred from the v0
MVP. Future versions of this extension MAY define an `aiar.rotateKeys` method
that allows agents to signal key rotation events to subscribed clients. For v0,
key rotation is handled out-of-band by updating the Agent Card and the issuer's
JWKS endpoint.

## Relationship to Agent Card `signatures` Field

The A2A protocol defines a top-level `signatures` field on the `AgentCard`
message (type `AgentCardSignature`). This field provides a general-purpose
mechanism for JWS signatures over Agent Cards.

The AIAR extension **complements** rather than replaces `signatures`:

- `AgentCard.signatures` provides raw JWS mechanics without identity semantics.
- AIAR adds **issuer binding**, **key resolution conventions**, **runtime
    proof-of-possession**, and **structured attestations**.

Agents MAY use both: `signatures` for transport-level integrity and the AIAR
extension for identity verification. The AIAR extension's `params.jws` follows
the same JWS JSON Serialization format as `AgentCardSignature`.

## Versioning Policy

- The extension URI includes a version segment (`/v0`).
- Non-breaking additions (new optional fields in `params`, new optional RPC
    methods) MAY be made within the same version.
- Breaking changes (removing fields, changing semantics of existing fields,
    changing the signing target) MUST use a new URI (e.g., `.../v1`).
- Agents MUST NOT fall back to a different version if the requested version is
    not supported.

## Security Considerations

### Sybil Resistance

This extension does not provide global Sybil resistance. Any entity can create
a signing key and self-sign an Agent Card. The Trusted Issuer Set is a **client
policy decision** — clients MUST maintain their own list of trusted issuers and
MUST NOT trust an agent solely because it presents a valid AIAR signature.

### Replay Prevention

The proof-of-possession mechanism includes `iat`, `exp`, and `nonce` fields to
mitigate replay attacks. Clients SHOULD:

- Reject proofs where `exp` is in the past.
- Reject proofs where `iat` is too far in the past (per
    `requireFreshnessSeconds`).
- Use unique nonces when possible.

### Key Compromise and Rotation

If a signing key is compromised:

1. The issuer MUST remove the compromised key from their JWKS endpoint (or DID
    document).
2. The issuer MUST update all affected Agent Cards with a new `kid` and
    re-sign.
3. Clients that cache JWKS responses SHOULD implement a maximum cache TTL and
    re-fetch keys periodically.

This extension does not define a real-time revocation mechanism. Implementors
requiring immediate revocation should consider supplementing with short-lived
proof bundles (small `expiresAt` windows) and frequent JWKS polling.

### Phishing and Impersonation

A valid JWS signature alone does not prevent impersonation — the client MUST
also verify that the `issuer` is in its Trusted Issuer Set. A signature from
an untrusted issuer provides integrity but not trustworthiness.

### Privacy

This extension is designed to assert **organizational** identity, not personal
identity. The `issuer` field identifies an organization, not an individual.
Implementations SHOULD NOT include personally identifiable information in
Agent Card `params` or proof bundles. The `contact` field in `aiar.getIssuer`
is intended for organizational security contacts, not personal data.

## Compatibility

- **Backwards-compatible**: Agents that do not support this extension simply
    omit it from their `capabilities.extensions`. Existing clients and agents
    are unaffected.
- **Core schema unchanged**: All AIAR data is placed in existing extension
    points (`AgentExtension.params`, `Message.metadata`, `Task.metadata`).
    No core protobuf messages are modified.
- **Graceful degradation**: If a client requests AIAR but the agent does not
    support it, the agent ignores the `A2A-Extensions` header and proceeds
    normally. The client observes the absence of the extension URI in the
    response header.

## Out of Scope (v0)

The following are explicitly **not** addressed by this MVP:

- Global trust registries or federated identity governance.
- Certificate revocation lists (CRLs) or OCSP-style revocation checking.
- Reputation scoring or behavioral trust metrics.
- End-to-end message encryption (orthogonal concern).
- Agent-to-agent mutual authentication (may be addressed in a future version).
- Automated key rotation notification (`aiar.rotateKeys` is deferred).
