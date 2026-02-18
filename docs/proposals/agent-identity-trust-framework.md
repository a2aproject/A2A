# Proposal: Agent Identity Verification and Trust Signals

**Author**: Abdel Fane (OpenA2A, @abdelsfane)
**Date**: 2026-02-17
**Status**: Draft
**Target**: A2A Protocol v1.x

## Problem Statement

The A2A protocol recommends TLS certificate validation (Section 7.2, SHOULD-level requirement) and allows optional JWS signatures on AgentCards (Section 8.4, MAY) for agent identity. These mechanisms verify the *domain* hosting an agent but do not verify the *agent itself*. In multi-agent ecosystems where agents discover each other through registries, well-known URIs, or referrals, this creates fundamental security gaps that are exploitable today.

### Specific Gaps

1. **No verified agent identity.** The `AgentProvider` message contains self-asserted `organization` and `url` fields. Any agent can claim to be published by "Google" or "OpenAI" with no verification. AgentCard signing (Section 8.4) is **MAY** — most deployments will not implement it.

2. **No trust evaluation.** When Agent A discovers Agent B, there is no mechanism for Agent A to evaluate whether Agent B is trustworthy enough for the task at hand. A financial transaction requires higher trust than a weather query, but A2A provides no signals or framework for this distinction.

3. **No trust propagation in delegation chains.** A2A's `referenceTaskIds` field (Section 4.1.4, Message) allows agents to reference related tasks, but provides no authorization boundaries for multi-agent delegation. When Agent B delegates to Agent C, Agent A has no visibility into or control over the delegation chain. There are no authorization boundaries, depth limits, or provenance records.

4. **No AgentCard revocation.** Section 8.4.3 states that "expired or revoked keys MUST NOT be used for verification" but provides no mechanism to check revocation status. Compromised AgentCards persist indefinitely.

5. **No message integrity at the application layer.** Messages between agents have no signing, timestamps, or nonces. Replay attacks work wherever TLS is terminated at a proxy or load balancer.

### Why These Gaps Are Urgent

These are not future threats. Unlike quantum computing (10-15 year horizon), agent impersonation, registry poisoning, and delegation chain attacks are exploitable in any A2A deployment today. As multi-agent systems proliferate in enterprise environments, the absence of identity verification and trust evaluation is the primary barrier to secure adoption.

## Proposed Changes

### 1. Agent Identity Verification Levels

Define three identity verification levels for AgentCard publishers. The level is declared in the AgentCard and can be independently verified by clients.

| Level | Name | Verification | Trust Signal |
| ----- | ---- | ------------ | ------------ |
| 0 | `SELF_ASSERTED` | No verification. Provider fields are self-declared. | Lowest. Suitable for development and testing. |
| 1 | `DOMAIN_VERIFIED` | DNS TXT record confirms the agent is authorized by the domain owner. | Medium. Proves the domain owner endorses this agent. |
| 2 | `ORGANIZATION_VERIFIED` | Third-party attestation from a trust registry or certificate authority verifies the organization. | Highest. Suitable for production deployments handling sensitive data. |

#### AgentCard Extension

Add an `identity` field to AgentCard via the existing `AgentExtension` mechanism:

```json
{
  "capabilities": {
    "extensions": [
      {
        "uri": "https://a2a-protocol.org/extensions/agent-identity",
        "description": "Agent identity verification and trust signals",
        "required": false,
        "params": {
          "version": "1.0.0"
        }
      }
    ]
  }
}
```

Identity metadata is carried in the extension's `params` field within `capabilities.extensions`:

```json
{
  "name": "financial-advisor-agent",
  "provider": {
    "organization": "Example Corp",
    "url": "https://example.com"
  },
  "capabilities": {
    "extensions": [
      {
        "uri": "https://a2a-protocol.org/extensions/agent-identity",
        "description": "Agent identity verification and trust signals",
        "required": false,
        "params": {
          "identityLevel": "DOMAIN_VERIFIED",
          "agentId": "urn:a2a:agent:example.com:financial-advisor:v2",
          "publicKey": {
            "kty": "OKP",
            "crv": "Ed25519",
            "x": "<base64url-encoded public key>",
            "kid": "agent-a1b2c3d4"
          },
          "attestations": [
            {
              "type": "domain",
              "domain": "example.com",
              "verifiedAt": "2026-02-17T00:00:00Z",
              "method": "DNS_TXT"
            }
          ]
        }
      }
    ]
  }
}
```

#### Agent Identifiers

Agents **SHOULD** declare a stable `agentId` using a URN format:

```text
urn:a2a:agent:{domain}:{agent-name}:{version}
```

Examples:

- `urn:a2a:agent:example.com:financial-advisor:v2`
- `urn:a2a:agent:registry.example.org:weather-service:v1`

The `agentId` serves as a persistent identifier across AgentCard updates, key rotations, and deployments. It is bound to the agent's signing key via the AgentCard signature.

#### DNS Verification

For Level 1 (`DOMAIN_VERIFIED`), the domain owner publishes a DNS TXT record:

```text
_a2a-identity.example.com TXT "v=a2a1; agent=financial-advisor; kid=agent-a1b2c3d4; fp=<sha256-fingerprint>"
```

Where:

- `agent`: The agent name portion of the `agentId`
- `kid`: The key identifier from the agent's public key
- `fp`: `base64url(sha256(raw_public_key_bytes))` without padding

Clients verifying domain-level identity **MUST**:

1. Extract the domain from the agent's `provider.url`
2. Query `_a2a-identity.{domain}` TXT record
3. Verify `kid` matches the agent's declared key ID
4. Compute the fingerprint from the agent's public key and verify it matches `fp`

**Security note:** DNS verification is vulnerable to DNS spoofing without DNSSEC. Clients **SHOULD** prefer DNSSEC-validated responses when available.

#### Organization Verification

For Level 2 (`ORGANIZATION_VERIFIED`), a third-party trust registry or certificate authority signs an attestation binding the agent's public key to a verified organization:

```json
{
  "type": "organization",
  "issuer": {
    "name": "A2A Trust Registry",
    "kid": "registry-x1y2z3",
    "url": "https://trust.a2a-registry.org"
  },
  "subject": {
    "organization": "Example Corp",
    "agentId": "urn:a2a:agent:example.com:financial-advisor:v2",
    "kid": "agent-a1b2c3d4"
  },
  "verifiedAt": "2026-02-17T00:00:00Z",
  "expiresAt": "2027-02-17T00:00:00Z",
  "signature": "<base64url-encoded signature by registry key>"
}
```

The attestation is signed over the RFC 8785 canonicalization of the attestation object with the `signature` field excluded.

### 2. Trust Signals

Define standardized trust signals that agents can declare and clients can evaluate. Trust signals are carried in the identity extension `params`:

```json
{
  "trustSignals": {
    "uptime": {
      "value": 0.999,
      "source": "self",
      "measuredAt": "2026-02-17T00:00:00Z"
    },
    "compliance": [
      {
        "standard": "SOC2-Type2",
        "certifiedBy": "Example Auditor",
        "expiresAt": "2027-01-01T00:00:00Z"
      }
    ],
    "securityContact": "security@example.com",
    "incidentResponseSla": "PT4H"
  }
}
```

**Defined trust signal types:**

| Signal | Type | Description |
| ------ | ---- | ----------- |
| `uptime` | `number` (0-1) | Historical availability ratio |
| `compliance` | `array` | Compliance certifications (SOC2, HIPAA, ISO 27001) |
| `securityContact` | `string` | Security incident contact |
| `incidentResponseSla` | `string` (ISO 8601 duration) | Committed incident response time |
| `dataResidency` | `array` of `string` | Geographic regions where data is processed |
| `auditLogAvailable` | `boolean` | Whether the agent provides audit logs |

Trust signals are self-asserted unless accompanied by a third-party attestation. Clients **SHOULD** weight attested signals higher than self-asserted ones.

### 3. Mandatory Signing for Production

Strengthen the AgentCard signing requirements from Section 8.4:

**Current spec language (Section 8.4):**
> "Agent Cards **MAY** be digitally signed..."

**Proposed change:**
> "Agent Cards **MUST** be digitally signed for production deployments accessible over public networks. Agent Cards served only within private networks or during development **MAY** omit signatures."

**Rationale:** Optional signing provides no security guarantee to the ecosystem. If signing is MAY, most implementations will not implement it, and clients cannot rely on its presence. Making signing MUST for production aligns with the spec's existing requirement that "Production deployments MUST use encrypted communication" (Section 7.1).

### 4. AgentCard Revocation

Define a revocation mechanism for compromised AgentCards.

#### Revocation via JWKS Endpoint

Agents that publish a JWKS endpoint (via the `jku` field in the JWS protected header) **MUST** remove revoked keys from the JWKS. Clients **MUST** re-fetch the JWKS before verifying signatures if the cached JWKS is older than the agent's declared `maxKeyAge` (a new optional field):

```json
{
  "uri": "https://a2a-protocol.org/extensions/agent-identity",
  "params": {
    "maxKeyAge": "PT1H"
  }
}
```

#### Revocation via DNS

For `DOMAIN_VERIFIED` agents, the domain owner removes or updates the `_a2a-identity` DNS TXT record. Clients that cache DNS results **SHOULD** respect TTL values.

#### Revocation Notification

Agents **MAY** publish a revocation event at a well-known endpoint:

```text
GET /.well-known/a2a-revocations.json
```

Response:

```json
{
  "revocations": [
    {
      "kid": "agent-old-key",
      "revokedAt": "2026-02-17T00:00:00Z",
      "reason": "KEY_COMPROMISE",
      "replacementKid": "agent-new-key"
    }
  ]
}
```

### 5. Delegation Chain Security

When an agent delegates a task to another agent, the delegation chain **SHOULD** be tracked for provenance and authorization.

#### Delegation Context in Message Metadata

When Agent A sends a task to Agent B, and Agent B delegates to Agent C, Agent B **SHOULD** include delegation context in the message `metadata`:

```json
{
  "metadata": {
    "a2a:delegation": {
      "chain": [
        {
          "agentId": "urn:a2a:agent:client.example.com:orchestrator:v1",
          "kid": "agent-orch-key",
          "delegatedAt": "2026-02-17T00:00:00Z"
        },
        {
          "agentId": "urn:a2a:agent:example.com:financial-advisor:v2",
          "kid": "agent-a1b2c3d4",
          "delegatedAt": "2026-02-17T00:00:01Z"
        }
      ],
      "maxDepth": 3,
      "scopes": ["read:market-data", "execute:analysis"],
      "expiresAt": "2026-02-17T01:00:00Z"
    }
  }
}
```

**Delegation rules:**

- Agents **MUST NOT** delegate beyond the `maxDepth` limit. If no limit is specified, the default is 3.
- Agents **MUST NOT** expand `scopes` — each delegation can only narrow or maintain the scopes granted by the upstream agent.
- Agents **SHOULD** include the full `chain` so downstream agents can verify provenance.
- The `expiresAt` field bounds the time window for the delegation. Agents **MUST** reject expired delegation contexts.

#### Delegation Signing

Each agent in the delegation chain **SHOULD** sign its chain entry, creating a verifiable chain of authorization. Each entry contains a single `signature` field. The signing payload links each hop to the previous one, forming a cryptographic chain.

**Signing payload construction:**

- **First entry (chain originator):** `Sign(JCS({agentId, kid, delegatedAt, scopes, maxDepth, expiresAt}))` using the originator's private key. JCS refers to RFC 8785 JSON Canonicalization Scheme.
- **Subsequent entries:** `Sign(JCS({agentId, kid, delegatedAt, scopes, previousSignature}))` using the delegating agent's private key, where `previousSignature` is the `signature` value from the immediately preceding chain entry.

Including the previous entry's signature in each subsequent signing payload cryptographically binds each hop to the one before it. A verifier can walk the chain from the last entry to the first, confirming that each agent authorized its delegation and acknowledged the chain above it.

```json
{
  "a2a:delegation": {
    "chain": [
      {
        "agentId": "urn:a2a:agent:client.example.com:orchestrator:v1",
        "kid": "agent-orch-key",
        "delegatedAt": "2026-02-17T00:00:00Z",
        "scopes": ["read:market-data", "execute:analysis", "write:report"],
        "signature": "<base64url: Sign_orchestrator(JCS({agentId, kid, delegatedAt, scopes, maxDepth, expiresAt}))>"
      },
      {
        "agentId": "urn:a2a:agent:example.com:financial-advisor:v2",
        "kid": "agent-a1b2c3d4",
        "delegatedAt": "2026-02-17T00:00:01Z",
        "scopes": ["read:market-data", "execute:analysis"],
        "previousSignature": "<copy of chain[0].signature>",
        "signature": "<base64url: Sign_advisor(JCS({agentId, kid, delegatedAt, scopes, previousSignature}))>"
      }
    ],
    "maxDepth": 3,
    "expiresAt": "2026-02-17T01:00:00Z"
  }
}
```

**Verification procedure:**

1. For each entry in the chain (starting from the first):
   - Resolve the agent's public key using the `kid` field
   - Reconstruct the signing payload (first entry uses `{agentId, kid, delegatedAt, scopes, maxDepth, expiresAt}`; subsequent entries use `{agentId, kid, delegatedAt, scopes, previousSignature}`)
   - Verify the `signature` against the reconstructed JCS payload using the agent's public key
2. Verify that each entry's `scopes` is a subset of (or equal to) the previous entry's `scopes`
3. Verify that the chain length does not exceed `maxDepth`

### 6. Message Signing

Add application-layer message integrity to complement TLS transport security.

Messages containing sensitive data or delegation contexts **SHOULD** include a JWS signature in the message `metadata`:

```json
{
  "messageId": "msg-12345",
  "role": "user",
  "parts": [
    { "text": "Analyze the Q4 financial report" }
  ],
  "metadata": {
    "a2a:signature": {
      "protected": "<base64url: {\"alg\":\"EdDSA\",\"kid\":\"agent-a1b2c3d4\"}>",
      "signature": "<base64url-encoded signature over canonicalized message>",
      "timestamp": "2026-02-17T00:00:00Z",
      "nonce": "<base64url-encoded 32-byte random value>"
    }
  }
}
```

**Signature payload:** The signature is computed over the RFC 8785 canonicalization of the message object with the `metadata["a2a:signature"]` field excluded.

**Replay protection:**

- Messages with signatures **MUST** include a `timestamp` and `nonce`.
- Receivers **SHOULD** reject messages with timestamps older than 5 minutes.
- Receivers **SHOULD** reject messages with previously-seen nonces.

**When to sign:**

- Messages containing delegation contexts **MUST** be signed.
- Messages containing financial, health, or personally identifiable data **SHOULD** be signed.
- Messages in development/testing environments **MAY** omit signatures.

## Backward Compatibility

All proposed changes are additive:

- **Identity extension**: Uses the existing `AgentExtension` mechanism. Agents that do not support this extension are unaffected. Clients that do not understand the extension ignore it.
- **Trust signals**: Carried in extension `params`. Non-aware clients ignore them.
- **Mandatory signing**: The specification change from MAY to MUST strengthens the requirement for production deployments over public networks. This is a behavioral change for production agents that previously omitted signatures, but it aligns with the existing MUST for encrypted communication (Section 7.1). Local/development deployments are unaffected.
- **Revocation**: New endpoints (`.well-known/a2a-revocations.json`) are additive. Clients that do not check revocation continue to work.
- **Delegation context**: Carried in message `metadata`, which is an existing extension point. Non-aware agents ignore it.
- **Message signing**: Carried in message `metadata`. Non-aware agents ignore it.

No existing fields are modified. No protobuf schema changes are required.

## Implementation Notes

### Library Support

Agent identity uses Ed25519 for signing. The base AgentCard signing mechanism (Section 8.4) uses ES256/RS256 via JWS; this extension uses Ed25519 for identity-specific signatures (attestations, delegation chains, message signing) due to its compact 64-byte signatures and deterministic signing. All major languages have Ed25519 support:

| Language | Library | Notes |
| -------- | ------- | ----- |
| Go | `crypto/ed25519` (stdlib) | Zero dependencies |
| Python | `cryptography` (PyCA) | Widely used, audited |
| JavaScript/TypeScript | `@noble/ed25519`, Node.js `crypto` | Pure JS or native |
| Java | Bouncy Castle | Enterprise standard; Ed25519 supported since 1.60+ |
| Rust | `ed25519-dalek` | Audited, no-std compatible |

### DNS TXT Record Setup

```bash
# Add agent identity DNS record
# Replace values with your agent's actual kid and fingerprint
_a2a-identity.example.com.  300  IN  TXT  "v=a2a1; agent=financial-advisor; kid=agent-a1b2c3d4; fp=abc123..."
```

### Performance Impact

| Feature | Overhead | Frequency |
| ------- | -------- | --------- |
| Identity metadata in AgentCard | +500-2000 bytes | Once per discovery |
| DNS verification | 1 DNS query (~50ms) | Once per agent, cacheable |
| Message signing | ~0.1ms per message | Per message (opt-in) |
| Delegation chain validation | ~0.1ms per chain entry | Per delegated task |
| Revocation check | 1 HTTP request (~100ms) | Periodic (cacheable via `maxKeyAge`) |

All overheads are negligible relative to the LLM inference latency that dominates agent interactions.

## Security Considerations

### Identity

- **`SELF_ASSERTED` identity (Level 0)** provides no guarantee. Clients **MUST NOT** treat Level 0 agents as verified.
- **`DOMAIN_VERIFIED` (Level 1)** is vulnerable to DNS spoofing without DNSSEC. Clients **SHOULD** combine DNS verification with other signals for high-security tasks.
- **`ORGANIZATION_VERIFIED` (Level 2)** depends on the trustworthiness of the verifying registry. Clients **SHOULD** support multiple registries and cross-reference attestations.

### Trust Signals

- Self-asserted trust signals (uptime, SLA) can be fabricated. Clients **SHOULD** only rely on trust signals that are attested by independent third parties.
- Compliance certifications have expiry dates. Clients **MUST** check `expiresAt` and reject expired certifications.

### Delegation

- Delegation chains create transitive trust. If any agent in the chain is compromised, the entire chain is compromised. The `maxDepth` limit bounds the blast radius.
- Scope narrowing is enforced by convention. A malicious agent can claim narrower scopes while actually performing broader actions. Downstream agents **MUST** independently authorize actions regardless of delegation claims.

### Message Signing

- Message signatures protect against replay and tampering at the application layer. They do NOT replace TLS — both are needed.
- The `nonce` prevents replay attacks but requires receivers to maintain a nonce cache. Receivers **SHOULD** use a time-bounded cache (e.g., reject nonces older than 10 minutes, purge cache entries older than 10 minutes).

### Privacy

- Agent identifiers (`agentId`) are persistent and can be used for tracking. Agents that require anonymity **SHOULD NOT** declare stable identifiers.
- DNS verification reveals the association between a domain and an agent identity.
- Delegation chains reveal the full sequence of agents involved in a task. Agents handling sensitive tasks **SHOULD** consider whether delegation chain metadata should be redacted before forwarding to downstream agents.

## References

- [A2A Protocol Specification v1.0 RC, Section 7: Authentication and Authorization](https://github.com/a2aproject/A2A/blob/main/specification/json/README.md)
- [A2A Protocol Specification v1.0 RC, Section 8.4: Agent Card Signing](https://github.com/a2aproject/A2A/blob/main/specification/json/README.md)
- [A2A Protocol Specification v1.0 RC, Section 13: Security Considerations](https://github.com/a2aproject/A2A/blob/main/specification/json/README.md)
- [RFC 7515: JSON Web Signature (JWS)](https://tools.ietf.org/html/rfc7515)
- [RFC 8785: JSON Canonicalization Scheme (JCS)](https://tools.ietf.org/html/rfc8785)
- [RFC 8615: Well-Known URIs](https://tools.ietf.org/html/rfc8615)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Tomasev, N., Franklin, M., & Osindero, S. "Intelligent AI Delegation." arXiv:2602.11865, February 2026](https://arxiv.org/abs/2602.11865)
