# Payment Evidence Frame

## Overview

A **Payment Evidence Frame (PEF)** is a transport-agnostic JSON envelope that
wraps any payment lifecycle receipt under a named `claim_type`, a deterministic
`frame_id`, and an optional transport-layer signature.

PEF is defined by the IETF Internet-Draft
[`draft-hopley-x402-payment-evidence-frame`](https://datatracker.ietf.org/doc/draft-hopley-x402-payment-evidence-frame/).
This page describes how PEF is used within A2A task artifacts.

---

## Why PEF in A2A

When a payment agent completes a task and returns a receipt as an artifact, the
orchestrator faces three practical problems:

1. **Type identification** -- the orchestrator must know what kind of receipt it
   is without parsing the inner format.
2. **Stable reference** -- the orchestrator needs an identifier that does not
   change if the receipt is re-serialised or if a signature is appended later.
3. **Tamper detection** -- the orchestrator must be able to confirm the inner
   receipt has not been altered without re-parsing it end-to-end.

PEF solves all three at the envelope level, before any inner-format parsing
occurs. The outer frame carries enough metadata for orchestration logic
(`claim_type`, `frame_id`, `receipt_hash`), while the inner `receipt` object
remains the authoritative domain record.

---

## claim_type Taxonomy

The `claim_type` field is a closed string enum. Each value corresponds to a
distinct payment lifecycle event.

| `claim_type`           | Lifecycle stage                       | Typical inner format            |
| :--------------------- | :------------------------------------ | :------------------------------ |
| `payment_admission`    | Compliance screen result              | `compliance-receipt-v1`         |
| `payment_settlement`   | Settlement confirmation               | `settlement-attestation-v1`     |
| `payment_cancellation` | Mandate or order termination          | `cancellation-receipt-v1`       |
| `payment_refund`       | Post-settlement refund                | `refund-receipt-v1`             |
| `composite_verdict`    | Verifier-of-verifier trust conclusion | `composite-trust-query-v1`      |

An orchestrator that does not recognise a `claim_type` value SHOULD treat the
frame as opaque and forward it without modification.

---

## Frame Fields

| Field                | Type    | Required | Description                                                                           |
| :------------------- | :------ | :------- | :------------------------------------------------------------------------------------ |
| `pef_version`        | string  | yes      | Specification version. Currently `"1"`.                                               |
| `claim_type`         | string  | yes      | Closed enum; see taxonomy above.                                                      |
| `receipt_format`     | string  | yes      | Inner receipt format identifier, e.g. `"compliance-receipt-v1"`.                      |
| `receipt`            | object  | yes      | The inner receipt verbatim.                                                           |
| `receipt_hash`       | string  | yes      | `sha256:<hex>` of the JCS-canonical form of `receipt`.                                |
| `frame_id`           | string  | yes      | `sha256:<hex>` of the JCS-canonical form of the frame preimage (see below).           |
| `frame_provider_did` | string  | yes      | DID URI of the party that issued this frame.                                          |
| `frame_timestamp_ms` | integer | yes      | Frame creation time as Unix epoch milliseconds.                                       |
| `canon_version`      | string  | yes      | Canonicalisation algorithm URI. MUST be `"urn:x402:canonicalisation:jcs-rfc8785-v1"`. |
| `signature`          | string  | no       | Opaque RFC 9421 transport evidence; see Signature Scope below.                        |

All string values are UTF-8. Integer values are JSON numbers with no fractional
part.

---

## frame_id Derivation

The `frame_id` is computed over the **frame preimage**: the frame object with
`frame_id` and `signature` fields excluded before serialisation.

Derivation steps:

1. Construct the frame object with all required fields present and `frame_id`
   and `signature` absent.
2. Serialise to JSON using JCS canonicalisation (RFC 8785).
3. Compute SHA-256 over the canonical byte sequence.
4. Encode as the lowercase hex string prefixed with `sha256:`.

```text
frame_id = "sha256:" + hex( sha256( JCS( frame_without_frame_id_and_signature ) ) )
```

This derivation ensures that `frame_id` is stable: adding a `signature` field
after the fact does not change the identifier. Orchestrators may record or index
`frame_id` before signing has occurred.

---

## Usage as a Task Artifact

A payment agent attaches a PEF as an A2A task artifact. The artifact contains a
single part with `mediaType: "application/json"`, where the `data` field carries
the complete frame object.

Example artifact for a settlement confirmation:

```json
{
  "artifactId": "artifact-uuid-123",
  "name": "Payment Evidence",
  "parts": [
    {
      "mediaType": "application/json",
      "data": {
        "pef_version": "1",
        "claim_type": "payment_settlement",
        "receipt_format": "settlement-attestation-v1",
        "frame_provider_did": "did:web:payments.example.com",
        "frame_timestamp_ms": 1748563200000,
        "canon_version": "urn:x402:canonicalisation:jcs-rfc8785-v1",
        "receipt": {
          "status": "SETTLED",
          "chain": "base",
          "tx_hash": "0x3c4f1e2a...",
          "settled_at_ms": 1748563195000
        },
        "receipt_hash": "sha256:a1b2c3d4e5f6...",
        "frame_id": "sha256:3c4f1e2a9b8d..."
      }
    }
  ]
}
```

An orchestrator receiving this artifact can:

- Read `claim_type` to determine routing logic without inspecting `receipt`.
- Verify `receipt_hash` to confirm `receipt` has not been altered.
- Index `frame_id` as a stable cross-system reference.
- Treat the optional `signature` field as opaque provenance evidence. RFC 9421
  verification is scoped to the original HTTP exchange; see Signature Scope
  below.

---

## frame_id Stability

Because `frame_id` and `signature` are excluded from the preimage, a signer may
attach a `signature` to a frame that has already been distributed without
invalidating any previously recorded `frame_id` references.

This property is useful in multi-agent pipelines where:

- An upstream agent issues a frame and records `frame_id` in a ledger.
- A signing service later attaches a `signature` field.
- A downstream verifier confirms integrity using the same `frame_id` that was
  logged before signing occurred.

Implementations MUST NOT include `frame_id` or `signature` in the preimage
computation.

---

## Signature Scope

An RFC 9421 signature is verifiable only against the HTTP message that carried
it. A verifier reconstructs the signature base (RFC 9421 Section 2.5) from the
covered component values of that message and the signature parameters
serialised in the `Signature-Input` field (Section 4.1), then checks the value
from the `Signature` field (Section 4.2) against that base (Section 3.2). The
frame body is bound into such a signature only when the message includes a
`Content-Digest` field (RFC 9530) over the body and `content-digest` is among
the covered components. The bare signature value alone is therefore not
verifiable.

Consequences for A2A carriage:

- Verification of `signature` is scoped to the original HTTP transport. It
  requires the captured `Signature` and `Signature-Input` field values and the
  covered component values of that exchange.
- Once a frame is re-carried as an A2A `DataPart`, that HTTP context is
  generally absent. A verifier MUST then treat the frame as **unsigned at the
  frame layer**, regardless of the embedded `signature` value, unless the
  artifact carries a separate self-contained proof.
- A verifier MUST NOT reconstruct a `Signature-Input`, infer covered
  components, or derive verification key material from `frame_provider_did`.
- Conformance suites SHOULD include a negative vector: a signed frame
  serialised through an A2A artifact with no accompanying HTTP context, for
  which signature verification MUST fail (report unverified) rather than
  succeed.

This scoping preserves the stability property above: `frame_id`,
`receipt_hash`, and the JCS preimage remain verifiable offline from the frame
alone. Only the transport signature requires its originating HTTP exchange.

---

## Reference Implementation

Two reference implementations are published under the Apache 2.0 licence:

- **Python**: [algovoi-pef on PyPI](https://pypi.org/project/algovoi-pef/)
- **TypeScript**: [@algovoi/pef on npm](https://www.npmjs.com/package/@algovoi/pef)

Both implementations expose helpers for frame construction, `frame_id`
derivation, `receipt_hash` computation, and structural verification. Neither
performs RFC 9421 verification at the frame layer, consistent with the
Signature Scope section above. They share a common test-vector corpus to
ensure byte-for-byte agreement across languages.

---

## Normative Reference

- IETF Internet-Draft `draft-hopley-x402-payment-evidence-frame`:
  <https://datatracker.ietf.org/doc/draft-hopley-x402-payment-evidence-frame/>
- RFC 8785 -- JSON Canonicalization Scheme (JCS):
  <https://www.rfc-editor.org/rfc/rfc8785>
- RFC 9421 -- HTTP Message Signatures:
  <https://www.rfc-editor.org/rfc/rfc9421>
- RFC 9530 -- Digest Fields:
  <https://www.rfc-editor.org/rfc/rfc9530>
