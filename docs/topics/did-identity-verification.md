# A2A Identity Extension: DID-Based Agent Verification via AIP

**Status**: Draft  
**Date**: 2026-02-23  
**Author**: The Nexus Guard  
**Companion to**: [abdelsfane's Agent Identity and Trust Framework](https://github.com/a2aproject/A2A/pull/1496)

## Abstract

This document specifies how A2A agents can use Decentralized Identifiers (DIDs) and cryptographic vouch chains for identity verification, complementing the extension-based framework proposed in PR #1496. While that proposal defines three verification levels using DNS and organizational attestation, this extension provides the cryptographic identity layer (Option 2 in the design rationale) using infrastructure that exists today: the Agent Identity Protocol (AIP).

## Motivation

PR #1496's design rationale correctly identifies that DID-based identity (Option 2) offers stronger guarantees than extension-based self-assertion (Option 1), but was set aside because "DID infrastructure does not yet exist for agents." AIP provides exactly this infrastructure:

- **DID generation**: Ed25519 keypairs with `did:aip:` method
- **Trust registry**: Transitive vouch chains with scoped trust levels  
- **Verification service**: Live API at `https://aip-service.fly.dev`
- **Client library**: `pip install aip-identity` (Python, 288 tests)
- **MCP integration**: `pip install aip-mcp-server` (8 tools)

This extension can coexist with abdelsfane's Level 0/1/2 model — it provides a concrete implementation path for Level 2 (organization-verified) and beyond.

## Specification

### AgentCard Extension

Agents advertise their AIP identity via the standard `extensions` field in their AgentCard:

```json
{
  "name": "my-agent",
  "url": "https://example.com/.well-known/agent.json",
  "extensions": [
    {
      "uri": "https://aip-service.fly.dev/extensions/identity/v1",
      "required": false,
      "metadata": {
        "did": "did:aip:abc123...",
        "verification_endpoint": "https://aip-service.fly.dev/verify",
        "trust_score_endpoint": "https://aip-service.fly.dev/trust-score",
        "capabilities": ["sign", "verify", "vouch", "message"]
      }
    }
  ]
}
```

### Identity Verification Flow

When Agent A discovers Agent B's AgentCard:

1. **Extract DID**: Read `extensions[].metadata.did` where `uri` matches the AIP extension URI.
2. **Verify identity**: `GET /verify/{did}` — confirms the DID is registered and returns the agent's public key and metadata.
3. **Check trust**: `GET /trust-score/{did_a}/{did_b}` — returns a trust score (0.0–1.0) based on vouch chain analysis.
4. **Establish threshold**: Agent A decides minimum trust score for the operation type (e.g., 0.3 for read-only, 0.7 for write operations).

```python
from aip_identity.client import AIPClient

client = AIPClient()

# Verify the remote agent
remote_agent = client.verify("did:aip:remote_agent_did")
if not remote_agent:
    raise IdentityError("Agent identity not found")

# Check trust relationship
trust = client.trust_score(my_did, remote_agent.did)
if trust.score < 0.5:
    raise TrustError(f"Insufficient trust: {trust.score}")
```

### Message Signing

All A2A messages between AIP-enabled agents SHOULD be signed:

```json
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{"text": "Analyze this dataset"}],
      "metadata": {
        "aip_signature": {
          "did": "did:aip:sender_did",
          "signature": "<base64-encoded-ed25519-signature>",
          "timestamp": 1771891000,
          "nonce": "unique-nonce-value"
        }
      }
    }
  }
}
```

The signature covers `method + params.message.parts + timestamp + nonce` to prevent replay attacks.

### Vouch Chains for Delegation

When Agent A delegates to Agent B, which sub-delegates to Agent C:

1. Agent A vouches for Agent B (scoped to specific capabilities)
2. Agent B vouches for Agent C (scope must be equal or narrower)
3. Agent C's trust score from Agent A's perspective is computed transitively

This maps directly to abdelsfane's delegation chain proposal but with cryptographic enforcement rather than self-asserted metadata.

```python
# Agent A vouches for Agent B with scoped trust
client.vouch(
    voucher_did=agent_a_did,
    subject_did=agent_b_did,
    scope=["data-analysis", "read-only"],
    trust_level=0.8
)

# Transitive trust: A→B→C
trust_a_to_c = client.trust_score(agent_a_did, agent_c_did)
# Returns weighted transitive score: 0.8 * 0.7 = 0.56
```

### Revocation

AIP provides real-time revocation via the service API:

- `DELETE /vouch/{vouch_id}` — revoke a specific vouch
- Revocation is immediate — subsequent trust score queries reflect the change
- No CRL distribution delay (unlike X.509)

## Compatibility with PR #1496

| PR #1496 Concept | AIP Implementation |
|---|---|
| Level 0 (Self-Asserted) | DID registration (automatic) |
| Level 1 (Domain-Verified) | DID + domain linking via `.well-known/aip-identity.json` |
| Level 2 (Organization-Verified) | Vouch from known organization's DID |
| Trust Signals | Vouch chains with scoped trust levels |
| AgentCard Signing | Ed25519 signatures on AgentCard JSON |
| Delegation Chains | Transitive vouch chains with scope narrowing |
| Revocation | Real-time API-based revocation |

## Security Considerations

- **Key management**: Private keys should be stored securely (HSM, secure enclave, or encrypted at rest)
- **Trust score manipulation**: Sybil attacks mitigated by requiring vouches from established agents
- **Service availability**: AIP service is a dependency; agents SHOULD cache verified identities
- **Privacy**: DIDs are pseudonymous; metadata disclosure is opt-in

## References

- [AIP GitHub](https://github.com/The-Nexus-Guard/aip)
- [AIP Service API](https://aip-service.fly.dev/docs)
- [PR #1496: Agent Identity and Trust Framework](https://github.com/a2aproject/A2A/pull/1496)
- [A2A Protocol Specification](https://github.com/a2aproject/A2A)
- [W3C Decentralized Identifiers](https://www.w3.org/TR/did-core/)
