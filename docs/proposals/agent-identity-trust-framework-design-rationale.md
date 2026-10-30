# Design Rationale: Agent Identity Verification and Trust Signals

**Companion to**: [Agent Identity and Trust Framework Proposal](./agent-identity-trust-framework.md)
**Date**: 2026-02-17
**Author**: Abdel Fane (@abdelsfane)

This document explains the design decisions behind the Agent Identity and Trust Framework proposal. It follows the format of an Architecture Decision Record (ADR).

## Context

The A2A protocol treats agents as standard enterprise applications (Section 7.1), relying on TLS and OAuth for security. This model works for client-server interactions where both parties are known entities, but breaks down in multi-agent ecosystems where:

- Agents discover each other dynamically through registries or well-known URIs
- Agents delegate tasks to other agents they have no prior relationship with
- The agent ecosystem is open — anyone can publish an AgentCard

The current security model verifies the domain hosting an agent (TLS) and authenticates the client accessing the agent (OAuth/API keys), but does not verify the agent's identity or trustworthiness. This is analogous to verifying that a website uses HTTPS but not verifying who operates it — a gap that the web addressed with Extended Validation certificates and Certificate Transparency.

## Decision Drivers

- Agent impersonation via registry poisoning or domain takeover is exploitable today
- Enterprise adoption requires verified identity and compliance certifications
- Multi-agent delegation requires authorization boundaries that do not exist
- AgentCard signing is currently MAY — most implementations will not do it
- The existing proto has extension points (`metadata`, `AgentExtension`) that avoid schema changes
- The A2A roadmap identifies Agent Registry as a longer-term item but provides no identity framework for it

## Considered Options

- **Option 1**: Extension-based identity with three verification levels and trust signals
- **Option 2**: W3C Verifiable Credentials (VCs) and Decentralized Identifiers (DIDs)
- **Option 3**: X.509 certificate hierarchy for agent identity
- **Option 4**: Do nothing — rely on TLS and existing signing

## Decision Outcome

**Chosen option: Option 1** — Extension-based identity with three verification levels and trust signals.

This option requires no protobuf schema changes, builds on existing JWS signing infrastructure, and provides a pragmatic path from zero-trust to verified identity without requiring external credential infrastructure.

### Consequences

**Positive:**

- No breaking changes to the protobuf schema
- Existing agents continue to work — they operate at Level 0 (`SELF_ASSERTED`)
- Progressive adoption: agents can start with Level 0 and upgrade to Level 1/2 as needed
- DNS verification (Level 1) requires no third-party infrastructure
- Compatible with future DID/VC integration if the ecosystem matures

**Negative:**

- Self-asserted trust signals can be fabricated (mitigated by attestation requirements for high-trust scenarios)
- DNS verification requires DNSSEC for security against spoofing
- Organization verification requires trust registries that do not yet exist for agents (chicken-and-egg problem)
- Delegation chain signing adds complexity and message size

**Neutral:**

- The identity framework is an extension, not core protocol — adoption depends on ecosystem momentum

## Analysis of Options

### Option 1: Extension-Based Identity (Chosen)

Use AgentExtension and metadata fields for identity, trust signals, and delegation context.

**Pros:**

- Zero schema changes
- Uses existing extension mechanisms
- Progressive adoption path (Level 0 -> 1 -> 2)
- DNS verification is simple and well-understood
- Compatible with the existing AgentCard signing infrastructure

**Cons:**

- Not enforced by schema — relies on convention and client implementation
- Trust registry infrastructure does not exist yet

### Option 2: W3C Verifiable Credentials (VCs) and DIDs

Agents present Verifiable Credentials proving their identity. Discovery uses DID resolution.

**Pros:**

- Standardized, interoperable credential format
- Decentralized — no single trust authority required
- Rich credential types (organizational identity, compliance, capability)

**Cons:**

- Significant complexity (DID methods, resolution, DID documents, VC schemas)
- DID ecosystem is still maturing — adoption is low
- Requires DID infrastructure that most agent developers do not have
- Overhead of DID resolution for every agent interaction
- A2A does not currently use any W3C decentralized identity standards

### Option 3: X.509 Certificate Hierarchy

Agent identity backed by X.509 certificates issued by certificate authorities.

**Pros:**

- Well-understood PKI model
- Revocation infrastructure exists (CRL, OCSP)
- Bridges to existing enterprise PKI deployments

**Cons:**

- Heavyweight — X.509 certificates add significant overhead for agent-to-agent interactions
- Certificate lifecycle management (issuance, renewal, revocation) is operationally costly
- Does not map cleanly to agent-specific attributes (skills, capabilities)
- Certificate authorities are centralized chokepoints
- The A2A ecosystem is not analogous to the web PKI — agents are more dynamic than servers

### Option 4: Do Nothing

Rely on existing TLS and optional JWS signing.

**Pros:**

- No additional complexity
- Existing implementations are unaffected

**Cons:**

- Agent impersonation remains trivial
- No trust evaluation is possible
- Enterprise adoption is blocked for security-sensitive use cases
- Delegation chains have no authorization boundaries
- The security gap widens as the ecosystem grows

## Implementation

1. Define the `https://a2a-protocol.org/extensions/agent-identity` extension
2. Document identity verification levels (0, 1, 2) in the specification
3. Document trust signal types and attestation format
4. Upgrade AgentCard signing from MAY to MUST for production
5. Document delegation chain structure and signing
6. Document message signing for integrity-sensitive messages
7. Add revocation endpoint specification
8. Provide reference implementation in at least two languages

## References

- [A2A Protocol Specification v1.0 RC](https://github.com/a2aproject/A2A/blob/main/specification/json/README.md)
- [RFC 7515: JSON Web Signature](https://tools.ietf.org/html/rfc7515)
- [RFC 8785: JSON Canonicalization Scheme](https://tools.ietf.org/html/rfc8785)
- [W3C Verifiable Credentials Data Model](https://www.w3.org/TR/vc-data-model/)
- [W3C Decentralized Identifiers](https://www.w3.org/TR/did-core/)
- [Certificate Transparency (RFC 6962)](https://tools.ietf.org/html/rfc6962)
