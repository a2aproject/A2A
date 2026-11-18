# Proposal: Agent Identity Trust Framework Roadmap

**Author**: Abdel Fane (OpenA2A, @abdelsfane)
**Date**: 2026-05-13
**Status**: Draft
**Target**: A2A Protocol v1.0 through v2.0

## Purpose

This document describes the planned trajectory for the Agent Identity Trust Framework (A2A-IDF) across four protocol cycles. v1.0 is the current proposal in [agent-identity-trust-framework.md](./agent-identity-trust-framework.md) and pull request [#1496](https://github.com/a2aproject/A2A/pull/1496). v1.1, v1.2, and v2.0 are forward-looking scopes that other implementers can plan against.

The intent is reduced coordination overhead: peers building identity-adjacent specs (Envoys signature/v1, CTEF claim envelopes, APS payments) can align release cycles, schema deltas, and conformance fixtures against a published trajectory instead of reacting per pull request.

## Versioning model

Each version pins a normative scope and a set of conformance shapes. Implementations declare which version they target; conformance suites publish fixtures per version; consumers select which version to require for trust evaluation.

Versions are additive within a major. Within v1.x, all v1.0 shapes remain valid; v1.1 and v1.2 introduce new types and registries that v1.0 verifiers can ignore without breaking trust evaluation. v2.0 introduces a major-cycle break (post-quantum keying) coordinated with the A2A protocol's own v2 timeline.

## v1.0: current proposal

**Scope.** Verification levels, dual-shape keyid resolution, attestation envelopes, delegation chain structure, and RFC 9421 wire signature integration.

| Element | Reference |
| ------- | --------- |
| Verification levels 0/1/2 | [agent-identity-trust-framework.md](./agent-identity-trust-framework.md) §1, §3 |
| Dual-shape keyid resolution | [agent-identity-trust-framework.md](./agent-identity-trust-framework.md) §6; pull request [#1496](https://github.com/a2aproject/A2A/pull/1496) §6 |
| Attestation envelope shape | [agent-identity-trust-framework.md](./agent-identity-trust-framework.md) §4 |
| Delegation chain envelope | [agent-identity-trust-framework.md](./agent-identity-trust-framework.md) §7 |
| Wire signature composition (RFC 9421 + Ed25519) | [Envoys signature/v1](https://envoys.me/specs/signature/v1) §1-§4 (informative); A2A-IDF §6 (normative reference) |
| Reference SDK | [`@opena2a/a2a-idf`](https://www.npmjs.com/package/@opena2a/a2a-idf) (Apache-2.0, npm) |
| Reference conformance suite | [`opena2a-org/a2a-idf-conformance`](https://github.com/opena2a-org/a2a-idf-conformance) (Apache-2.0) |
| Specification landing page | [opena2a.org/identity](https://opena2a.org/identity) |

**Target merge window.** A2A Protocol v1.1 candidate cycle. Coordination thread is on pull request [#1496](https://github.com/a2aproject/A2A/pull/1496).

**External dependencies.**
- RFC 9421 (HTTP Message Signatures): stable.
- RFC 9530 (Content-Digest): stable.
- RFC 8785 (JSON Canonicalization Scheme): stable.
- Envoys signature/v1: v1.4.0 stable (composes via §6 dual-shape).
- CTEF claim envelopes: tracked via [issue #1786](https://github.com/a2aproject/A2A/issues/1786) (informative reference; not blocking).
- APS bilateral receipts and delegation chains: tracked via [issue #1575](https://github.com/a2aproject/A2A/issues/1575) (composition demonstrated via conformance fixtures `bilateral-receipt.json` and `delegation-chain-3link.json`).

## v1.1: vouching attestations

**Scope.** A vouching attestation type that lets one verified issuer endorse another agent without taking on full attestation responsibility. Formalizes the issuer / vouchee / scope / expiry shape so chain-of-trust evaluators can resolve cross-issuer trust without ad-hoc rules.

**Driver.** First raised by [@aeoess](https://github.com/aeoess) on the 2026-02-23 trust-framework thread. Use case is multi-org settings where Issuer A (audit firm) wants to vouch for Agent B (operated by Org C) without becoming the originating attester for every claim about B. The vouching shape sits between Level 1 (domain-verified) and Level 2 (organization-verified) and is composable with both.

**Normative additions.**
- A new attestation type `vouching` with required fields `issuer`, `vouchee`, `scope`, `issuedAt`, `expiresAt`, `signature`.
- Scope is a structured authorization domain (path-based, capability-based, or both), not a free-text description.
- Verifier rules: a vouching attestation contributes to trust evaluation only when the issuer itself meets the required verification level for the action being authorized; vouches do not chain transitively past depth 1 by default.

**Coordination dependencies.**
- CTEF claim envelope shape (issue [#1786](https://github.com/a2aproject/A2A/issues/1786)): if the v0.3.x envelope shape stabilizes a generic "attestation" envelope, the vouching type ships as a content-type within that envelope. Otherwise A2A-IDF defines the envelope directly.
- APS receipt schema (issue [#1575](https://github.com/a2aproject/A2A/issues/1575)): vouching does not interact with payment receipts; the two are orthogonal.

**Target merge window.** A2A Protocol v1.1.x maintenance cycle, candidate Q3 2026.

## v1.2: federated revocation registry

**Scope.** An append-only revocation log so a verifier can determine that a previously trusted attestation has been revoked without contacting the original issuer. Design follows certificate-transparency log conventions: signed tree heads, inclusion proofs, log witnesses operated by a subset of issuers.

**Driver.** Raised by [@aeoess](https://github.com/aeoess) on the 2026-02-23 trust-framework thread. Today, revocation requires the verifier to contact the issuer's endpoint and trust the response; that endpoint is a privacy leak (the issuer learns which agents the verifier is evaluating) and a centralized chokepoint. CT-style logs solve both.

**Normative additions.**
- A `revocation` record type containing `attestationId`, `revokedAt`, `reason`, `issuerSignature`.
- A log structure: Merkle tree with signed tree heads, witnessed by a subset of issuers (initial bootstrap target: 3 of 5 witness consensus).
- Verifier rules: a verifier consulting a recent enough signed tree head (within a configurable freshness window) is entitled to evaluate revocation status without contacting the issuer directly.
- A `revocationProof` field on attestation envelopes contains an inclusion proof against a specific tree head, so consumers can cache attestations across sessions.

**Coordination dependencies.**
- v1.1 vouching shape (this proposal): revocation log records vouching attestations and primary attestations identically; the type field distinguishes.
- Witness governance: needs an A2A working group resolution on which issuers operate witnesses. Candidate witness set is the agreed conformance suite operators (OpenA2A, @aeoess, @jschoemaker, @kenneives, @lawcontinue).

**Target merge window.** A2A Protocol v1.2.x cycle, candidate Q4 2026 through Q1 2027.

## v2.0: post-quantum signature agility

**Scope.** Add ML-DSA-65 (formerly Dilithium-65) as a second normative signature algorithm alongside Ed25519, and define an algorithm-agility framework so future signature algorithms compose without protocol-level breaking changes.

**Driver.** The A2A protocol cannot remain Ed25519-only indefinitely. NIST has finalized FIPS-204 (ML-DSA); the window for orderly migration is the v2 cycle, not later. A v2.0 break is the appropriate moment because keyid resolution shapes, attestation envelopes, and delegation chain payloads all need a `signatureAlgorithm` field that v1.x verifiers do not require.

**Normative additions.**
- Algorithm registry: Ed25519 (continued), ML-DSA-65 (added), ML-DSA-87 (optional for high-assurance contexts).
- Hybrid keying: verifiers MUST accept either Ed25519 or ML-DSA-65 signatures during the v2.0 transition window; agents SHOULD ship both signature types in parallel for at least one minor cycle before deprecating Ed25519-only mode.
- Keyid resolution: each verification method in a DID Document declares its `signatureAlgorithm` (defaulting to Ed25519 for v1.x backward compatibility).
- Algorithm-agility framework: every signature-carrying envelope (RFC 9421 wire signatures, attestation envelopes, delegation links, revocation records) gets an `alg` field; absence of `alg` is interpreted as Ed25519.

**Coordination dependencies.**
- A2A Protocol v2 cycle: this proposal targets the same cycle so the migration story is coordinated.
- RFC tracking: any IETF document standardizing ML-DSA in HTTP Message Signatures becomes a normative reference; absent such a document, A2A-IDF v2.0 defines the integration directly.
- Envoys signature/v1 next major: if Envoys ships its own ML-DSA support before A2A-IDF v2.0, the dual-shape resolution principle continues to apply (per-method `signatureAlgorithm` declaration in the DID Document side; explicit `alg` parameter in the compact form side).

**Target merge window.** A2A Protocol v2.0 candidate cycle, candidate 2027.

## Coordination map

Per-release pinning is the convergent practice across the companion specs in this map: each project pins byte-stable conformance vectors per SDK release, and verifiers compose against known vector sets rather than a moving `HEAD`. Cross-spec references below carry version pins and content hashes in the corresponding conformance fixture sets.

| Companion spec | Owner | Layer | Interaction with A2A-IDF |
| -------------- | ----- | ----- | ----------------------- |
| [Envoys signature/v1 (issue #1829)](https://github.com/a2aproject/A2A/issues/1829) | @jschoemaker | Wire (per-message RFC 9421 + Ed25519) | A2A-IDF §6 dual-shape resolution interoperates with Envoys §6 compact form. Conformance fixtures byte-match Envoys §13 vectors. |
| [CTEF claim envelopes (issue #1786)](https://github.com/a2aproject/A2A/issues/1786) | @aeoess | Identity claims | A2A-IDF attestation envelopes and CTEF claim envelopes are orthogonal layers. If CTEF stabilizes a generic envelope shape, A2A-IDF attestation types ship as content within it. |
| [APS, Agent Passport System (issue #1575)](https://github.com/a2aproject/A2A/issues/1575) | @aeoess | Delegation and continuity | APS composes with A2A-IDF at the identity, scoped-authority, and mutual-authentication surfaces; it does not replace the A2A-IDF wire signature. APS treats that signature as the transport layer and carries delegation and receipt structure above it. Per-version composition detail in the sub-section below. |
| [Hippo Ed25519 reference (lawcontinue/hippo-auth)](https://github.com/lawcontinue/hippo-auth) | @lawcontinue | Wire reference implementation | Hippo's Ed25519 reference library is a peer implementation against Envoys §1-§4. A2A-IDF §6 follow-up planned to incorporate Hippo's `tag` parameter and SHA-512 acceptance work. |
| [CTEF v0.3.x release coordination (v0.3.3 working doc)](https://github.com/agentgraph-co/agentgraph/blob/main/docs/standards/v0.3.3-working-doc.md) | @kenneives | Cross-thread release coordination | A2A-IDF aligns minor-version timing with CTEF cycles to share review cycles for envelope shape changes. The substrate envelope work on the same issue is tracked separately in the row above. |

### APS per-version composition

Source: [`aeoess/agent-passport-system`](https://github.com/aeoess/agent-passport-system) (Apache-2.0, npm, IETF Internet-Draft `draft-pidlisnyi-aps-01`). Per-version detail contributed by @aeoess.

- **v1.0**. APS signed agent identity and scoped delegation with monotonic narrowing align with A2A-IDF §1–§4. Mutual authentication composes with §6 wire signature.
- **v1.1**. APS delegation chains can express issuer / vouchee / scope / expiry assertions as delegation grants without re-signing the A2A-IDF envelope.
- **v1.2**. APS cascade revocation composes with an external append-only revocation registry by reference, not replacement.
- **v2.0**. APS signatures are JOSE-tagged and profile-defined, so an Ed25519 to ML-DSA-65 transition can be handled as a profile update rather than a protocol rewrite.

APS pins byte-stable conformance vectors per SDK release at [`aeoess/aps-conformance-suite`](https://github.com/aeoess/aps-conformance-suite). Downstream implementers verify against the pinned fixtures for a given release even when the SDK moves, so composition stays reproducible across version boundaries.

### Related substrate work (not in this map)

OpenA2A's identity and trust spec set ([AIP](https://github.com/opena2a-org/agent-identity-protocol), [ATP](https://github.com/opena2a-org/agent-trust-protocol), [ATX](https://github.com/opena2a-org/atx-spec)) is tracked separately on [`a2aproject/A2A#1876`](https://github.com/a2aproject/A2A/issues/1876) for coordination visibility. That set does not yet meet the maturity bar this map applies (single implementation today, reference build plugin not yet shipped, no peer-cosigned conformance fixtures comparable to APS or CTEF), so it is not in the table above. The cross-link is here so peers tracking the four-layer split know the work exists and is on path.

## Non-goals (across all versions)

- **No required hosted infrastructure.** A2A-IDF does not require any specific registry, attestation issuer, or hosted service. Reference implementations exist but are not normative.
- **No proprietary signature formats.** All signatures are over IETF-standardized canonical forms (RFC 9421 base, RFC 8785 JCS payload).
- **No protocol-level deprecation of TLS or AgentCard signing.** A2A-IDF supplements §7.2 (TLS) and §8.4 (AgentCard signing) by adding agent-level identity. Both lower-layer mechanisms remain valid and recommended.
- **No assumption of online verifiers.** Every verification path supports offline evaluation given the right pre-fetched material (DNS records, attestations, revocation tree heads, keyid documents).

## Engagement and tracking

| Surface | Where |
| ------- | ----- |
| Specification pull request | [a2aproject/A2A#1496](https://github.com/a2aproject/A2A/pull/1496) |
| Reference SDK source | [github.com/opena2a-org/a2a-idf-sdk](https://github.com/opena2a-org/a2a-idf-sdk) |
| Reference SDK package | [`@opena2a/a2a-idf`](https://www.npmjs.com/package/@opena2a/a2a-idf) |
| Reference conformance suite | [github.com/opena2a-org/a2a-idf-conformance](https://github.com/opena2a-org/a2a-idf-conformance) |
| Specification landing page | [opena2a.org/identity](https://opena2a.org/identity) |
| Coordination with companion specs | [a2aproject/A2A#1829](https://github.com/a2aproject/A2A/issues/1829) (Envoys), [#1786](https://github.com/a2aproject/A2A/issues/1786) (CTEF), [#1575](https://github.com/a2aproject/A2A/issues/1575) (APS) |

Implementers planning around this roadmap can open issues on `a2aproject/A2A` referencing the relevant version section, or coordinate directly on the related issue threads.
