# A2A — PQC credential binding + ZKP receipt in production

**Repo:** a2aproject/a2a
**Related open PRs:** #1886 (compliance gate), #1896 (settlement/CTQ/RFC 9421), #1898 (PEF)
**Type:** Production deployment notice — supplement to open PRs

---

## Production status

AlgoVoi's A2A `verify-payment` skill is **live in production** with ZKP-bound payment evidence for Phase 2 ATB-credentialled agents as of 2026-06-04.

---

## New fields in `verify-payment` task result (Phase 2 ATB sessions only)

```json
{
  "task": {
    "state": "completed",
    "result": {
      "parts": [{"kind": "data", "data": {
        "verified": true,
        "tx_id": "...",
        "settlement_attestation": {"settlement_result": "SETTLED", ...},
        "settlement_attestation_jws": "eyJ...",
        "zkp_receipt_payload": "<base64url unsigned ZKP receipt>",
        "composite_trust_verdict": "TRUSTED"
      }}]
    }
  }
}
```

Response headers also carry:

- `X-ZKP-Receipt-Payload` — same value as `zkp_receipt_payload`
- `X-Composite-Trust-Verdict` — same value as `composite_trust_verdict`

Both are **only present for Phase 2 ATB sessions**. All existing A2A flows are unaffected — no breaking change.

---

## Agent credential flow for A2A

```text
1. Agent → POST /auth/token
   Headers: X-Tenant-Id, Authorization: Bearer <api_key>
   Body: { "atb_zk_credential": "<Falcon-1024 Phase 2 cert>", "spend_cap_usd": 50.0 }
   ← session JWT; ZKP commitment + proof bound to session; spend cap initialized

2. Agent → POST /a2a/message
   Authorization: Bearer <session_token>
   Body: { "skill": "verify-payment", "tx_id": "...", "network": "...", "token": "..." }

3. ← Task completed:
   result.data.zkp_receipt_payload  = <unsigned ZKP receipt payload>
   result.data.composite_trust_verdict = "TRUSTED"
   Spend cap decremented by payment amount
```

The session token covers all A2A skills in the session. `spend_cap_usd` exceeded → `402 agent_spend_cap_exceeded` before the facilitator is called.

---

## Composite trust verdict

The verdict composes the A2A settlement attestation with the ZKP receipt. Independently reproducible:

```http
POST https://api.algovoi.co.uk/compliance/trust-query
Content-Type: application/json

{
  "receipts": [
    {
      "settlement_result": "SETTLED",
      "settlement_provider_did": "did:web:api.algovoi.co.uk"
    },
    {
      "type": "zkp_receipt",
      "threshold_met": true,
      "bench_issuer": "did:web:agent-trust-bench.algovoi.co.uk"
    }
  ]
}
```

```json
{
  "trust_outcome": "TRUSTED",
  "composite_hash": "36042eb288b6557aed801ed9a2fe6e077b31bd7261a4dffbe8107ef078867f10",
  "receipt_count": 2
}
```

Possible verdicts: `TRUSTED` · `PROVISIONAL` (`PENDING_FINALITY`) · `INSUFFICIENT_EVIDENCE` · `UNTRUSTED`.
Specified in [`draft-hopley-x402-composite-trust-query`](https://datatracker.ietf.org/doc/draft-hopley-x402-composite-trust-query/) — open PR #1896.

---

## Validation stages

### Stage 1 — Specification

| Reference | Subject |
| --- | --- |
| [`draft-hopley-x402-pqc-credential-binding`](https://datatracker.ietf.org/doc/draft-hopley-x402-pqc-credential-binding/) | Falcon-1024 / ML-DSA-65 (NIST FIPS 204/206) credential binding to A2A payment authorization — under editor review |
| [`draft-hopley-x402-federation-zkp`](https://datatracker.ietf.org/doc/draft-hopley-x402-federation-zkp/) | Cross-issuer ZKP composition; composite commitment: `SHA-256(domain ‖ comm_0 ‖ … ‖ nonce)` — under editor review |
| [`draft-hopley-x402-composite-trust-query`](https://datatracker.ietf.org/doc/draft-hopley-x402-composite-trust-query/) | Composite trust verdict — open PR #1896 |
| [IACR ePrint 2026/109852](https://eprint.iacr.org/2026/109852) | *"Agent Trust Bench: Adversarial Payment Profiling for Autonomous Agents with Post-Quantum Credential Binding and Cross-Issuer Federation"* — under IACR editor review |

### Stage 2 — Implementation

Production deployment to `api.algovoi.co.uk` as of 2026-06-04:

- `algovoi-federation-validator` v0.1.1 — 59/59 tests pass
- `algovoi-zkp-receipt` v0.1.0 — 13/13 tests pass
- Gateway agent auth + ZKP receipt pipeline — 75/75 tests pass
- ATB ZKP service (Rust / Bulletproofs / Ristretto255) — live

### Stage 3 — Cross-language conformance

`zkp_receipt_v1` payload canonicalization validated byte-for-byte across 8 independent JCS implementations:

| Language | Result |
| --- | --- |
| Python `rfc8785 0.1.4` | **8/8 PASS** |
| Node.js `canonicalize 3.0.0` | **8/8 PASS** |
| Ruby `json-canonicalization 1.0.0` | **8/8 PASS** |
| PHP `root23/php-json-canonicalization 1.0.1` | **8/8 PASS** |
| Go `gowebpki/jcs v1.0.1` | **8/8 PASS** |
| Rust / Java / .NET | By transitivity — 320/320 prior attestation |

Attestation: [`2026-06-04-zkp-receipt-v1-cross-validation.md`](https://github.com/chopmob-cloud/algovoi-jcs-conformance-vectors/blob/main/_attestations/2026-06-04-zkp-receipt-v1-cross-validation.md)
Cumulative: **664/664** byte-for-byte agreements across 9 vector sets, 8 JCS implementations.

### Stage 4 — Live production smoke

- 13/13 service checks pass
- All four CTQ verdicts verified live
- ATB bench score: 128/138 (92.8%)
- 7 chains: Algorand, VOI, Hedera, Stellar, Base, Solana, Tempo

---

## Licensing — these packages are not open source

Three deployment paths are available:

**1. Hosted commercial application**
Use `api.algovoi.co.uk` directly — the full PQC/ZKP/Federation stack is live under the standard AlgoVoi 0.50% transaction fee. No additional license required. The `verify-payment` ZKP fields are available to all session-authenticated A2A tenants.

**2. Commercial Docker instances**
Run `algovoi-federation-validator` and `algovoi-zkp-receipt` as Docker containers on your own infrastructure under the **AlgoVoi Commercial License v1.0**. Production-grade Docker images are available to license holders. Evaluation use (non-commercial, non-production) is free.

**3. Enterprise / OEM / acquisition**
Custom on-premises deployments, white-label integrations, and acquisition enquiries. Contact [hello@algovoi.co.uk](mailto:hello@algovoi.co.uk).

---

The **self-hosted implementation packages are proprietary and will not be open-sourced under any circumstances**:

| Package | License |
| --- | --- |
| `algovoi-federation-validator` | **AlgoVoi Commercial License v1.0 — not open source** |
| `algovoi-zkp-receipt` | **AlgoVoi Commercial License v1.0 — not open source** |

There is no Apache, MIT, or community-license path for these packages. Production deployment, revenue-generating use, or managed-service operation requires a written Commercial License Agreement. Contact [hello@algovoi.co.uk](mailto:hello@algovoi.co.uk).

All 31 AlgoVoi substrate packages remain Apache 2.0.

---

*AlgoVoi (chopmob-cloud) -- [docs.algovoi.co.uk/pqc-substrate](https://docs.algovoi.co.uk/pqc-substrate)*
