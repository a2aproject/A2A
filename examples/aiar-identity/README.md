# AIAR Identity Extension — Example Payloads

This folder contains example JSON payloads for the
[Agent Identity and Accountability Reporting (AIAR) extension](../../docs/extensions/aiar-identity-v0.md).

**Extension URI:** `https://github.com/a2aproject/A2A/extensions/aiar.identity/v0`

## Files

| File | Description |
| :--- | :--- |
| `agent-card.json` | A standard Agent Card without the AIAR extension |
| `agent-card.signed.json` | An Agent Card with the AIAR extension declared, including issuer metadata and JWS signature |
| `message.request.json` | A `SendMessage` request with AIAR identity requirements in metadata |
| `message.response.json` | A task response including an AIAR proof bundle in metadata |
| `proof-bundle.json` | A standalone proof bundle object (as returned by `aiar.getProofBundle`) |

## Signature Values

The JWS `protected`, `payload`, and `signature` values in these examples are
**illustrative placeholders**. In a real deployment:

- `protected` is a base64url-encoded JSON object containing `{"alg":"ES256","kid":"example-key-2025-01"}`.
- `payload` is the JCS-canonicalized Agent Card (for card signatures) or a proof-of-possession claims object (for runtime proofs).
- `signature` is the actual ECDSA/EdDSA/RSA signature output.

## How to Verify an Agent Card Signature

1. **Fetch the Agent Card** from `/.well-known/agent-card.json`.

2. **Locate the AIAR extension** in `capabilities.extensions[]` by matching the
    URI `https://github.com/a2aproject/A2A/extensions/aiar.identity/v0`.

3. **Extract identity fields** from `params`:
    - `issuer` — the organizational identity URI
    - `kid` — the key identifier
    - `jws` — the JWS signature object

4. **Resolve the signing key**:
    - If `issuer` is an HTTPS URL: GET `{issuer}/.well-known/jwks.json` and
        find the key where `kid` matches.
    - If `issuer` is a DID: resolve the DID document and find the verification
        method matching `kid`.

5. **Reconstruct the signing input**:
    - Copy the Agent Card JSON.
    - Remove the `jws` field from the AIAR extension's `params`.
    - Apply RFC 8785 (JCS) canonicalization to produce a deterministic byte string.

6. **Verify the JWS**:
    - Decode the `protected` header to get `alg`.
    - Verify the signature over the canonicalized payload using the resolved key.

7. **Check issuer trust**:
    - Verify that `issuer` is in your Trusted Issuer Set (a client policy decision).

## How to Verify a Runtime Proof Bundle

1. **Extract the proof bundle** from the response `metadata` under the key
    `https://github.com/a2aproject/A2A/extensions/aiar.identity/v0/proof_bundle`.

2. **Check timestamps**:
    - `issuedAt` should not be in the future.
    - `expiresAt` should not be in the past.
    - If `requireFreshnessSeconds` was specified in the request, verify that
        `issuedAt` is within the freshness window.

3. **Verify `cardDigest`**:
    - Fetch the Agent Card and compute its JCS-canonicalized SHA-256 hash.
    - Compare with `cardDigest` (after removing the `sha256:` prefix and
        base64url-decoding).

4. **Verify `proofOfPossession`**:
    - Decode the JWS payload to extract claims (`iss`, `sub`, `cardDigest`,
        `iat`, `exp`, `nonce`).
    - Verify the JWS signature using the key resolved from `kid` / `issuer`.
    - Verify that `iss` matches the `issuer` in the proof bundle.
    - Verify that `cardDigest` in the claims matches the top-level `cardDigest`.

5. **Validate attestations** (optional):
    - For `"type": "uri"` attestations, fetch and validate the linked document.
    - For `"type": "vc"` attestations, verify the Verifiable Credential.

## Trusted Issuer Set (Client Policy)

The AIAR extension does not prescribe a global trust model. Each client
maintains its own Trusted Issuer Set. A simple implementation might be a
static allowlist:

```json
{
  "trustedIssuers": [
    "https://example.com",
    "https://trusted-partner.org"
  ]
}
```

More sophisticated implementations might integrate with organizational PKI,
trust registries, or Verifiable Credential ecosystems.
