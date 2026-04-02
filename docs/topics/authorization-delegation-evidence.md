# Authorization, Delegation & Audit Evidence for Agent-to-Agent Interactions

This document proposes an extension to the A2A protocol that addresses
authorization schemes, delegation chains, and audit evidence for multi-agent
systems. It is motivated by the authorization gaps identified in the current
specification and by emerging regulatory requirements for transparency and
accountability in autonomous agent systems.

**Related issues:**
[#19 (Delegated User Authorization)](https://github.com/a2aproject/A2A/issues/19),
[#71 (Auth RFC)](https://github.com/a2aproject/A2A/issues/71),
[#1404 (Capability-Based Auth)](https://github.com/a2aproject/A2A/issues/1404)

**Status:** Proposal

---

## 1. Abstract

The A2A protocol provides authentication primitives via OAuth 2.0, API keys, and
OpenID Connect, and describes authorization as implementation-specific
(see [Enterprise Features](enterprise-ready.md) and
[Section 13.1](../specification.md#131-data-access-and-authorization-scoping)).
However, the protocol does not currently define:

1. A **capability-based authorization model** that agents can advertise and
   verify at the protocol level.
2. A **delegation mechanism** for multi-hop agent chains where Agent A
   authorizes Agent B to act on its behalf, verifiable by Agent C.
3. A normative **audit evidence format** that enables independent third-party
   verification of agent actions.

These gaps become acute as agent systems scale beyond bilateral interactions.
In multi-agent workflows spanning organizational boundaries, the absence of
standardized authorization semantics leads to ambient authority patterns,
unverifiable delegation chains, and audit records that cannot be independently
validated.

Industry data reinforces the urgency: a 2025 survey by the Cloud Security
Alliance found that 88% of organizations deploying autonomous agents reported
at least one security incident related to excessive agent permissions, while
only 21% had visibility into the full permission chain of multi-agent
workflows. Regulatory frameworks are converging on explicit requirements for
agent transparency: the EU AI Act (enforcement beginning August 2, 2026)
mandates transparency obligations for AI systems under Article 50, and the
NIST AI Agent Standards Initiative has identified authorization gaps in
multi-agent systems as a priority research area.

This proposal defines three interconnected capabilities as an A2A extension,
designed to be adopted incrementally and to remain backward-compatible with
existing implementations.

## 2. Design Principles

The extension is guided by five principles:

1. **Principle of least authority.** Agents request the minimal set of scopes
   required for each task. No ambient authority.
2. **Fail-closed defaults.** If authorization cannot be verified, the action
   is denied. If evidence cannot be recorded, the action should not proceed.
3. **Independent verifiability.** Any party with the evidence records and
   public keys can verify the integrity of the audit trail without trusting
   the system that wrote it.
4. **Incremental adoption.** Each of the three capabilities (authorization,
   delegation, evidence) can be adopted independently. Existing A2A
   implementations continue to function without modification.
5. **Algorithm agility.** Cryptographic algorithms are parameters, not
   hardcoded choices. Implementations can upgrade signing algorithms without
   protocol changes.

## 3. AgentCard Authorization Extension

This section defines optional fields that an agent MAY include in its
AgentCard to advertise authorization capabilities. These fields are
communicated as extension parameters using the A2A
[extension mechanism](extensions.md).

**Extension URI:** `urn:a2a:ext:authorization:v1`

### 3.1. Extension Parameters

When an agent declares support for this extension, the `params` field of the
`AgentExtension` object SHOULD include:

| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| `authorization_model` | `string` | Yes | One of `"CAPABILITY"`, `"ROLE"`, or `"ATTRIBUTE"`. |
| `required_scopes` | `string[]` | No | Scopes that the caller must possess to interact with this agent. |
| `delegation_supported` | `boolean` | No | Whether the agent accepts delegation chains. Default: `false`. |
| `max_delegation_depth` | `integer` | No | Maximum number of hops in an accepted delegation chain. `0` means no delegation. |
| `evidence_required` | `boolean` | No | Whether the agent requires callers to support audit evidence. Default: `false`. |
| `credential_lifetime_seconds` | `integer` | No | Maximum accepted lifetime for capability tokens, in seconds. |
| `revocation_endpoint` | `string` (URI) | No | Endpoint for checking credential revocation status. |

**Example AgentCard with authorization extension:**

```json
{
  "name": "Trade Execution Agent",
  "description": "Executes equity trades on behalf of authorized agents.",
  "version": "1.0.0",
  "url": "https://example.com/agents/trade-executor",
  "capabilities": {
    "extensions": [
      {
        "uri": "urn:a2a:ext:authorization:v1",
        "description": "Capability-based authorization with delegation and audit evidence",
        "required": true,
        "params": {
          "authorization_model": "CAPABILITY",
          "required_scopes": ["trade.execute", "portfolio.read"],
          "delegation_supported": true,
          "max_delegation_depth": 2,
          "evidence_required": true,
          "credential_lifetime_seconds": 3600,
          "revocation_endpoint": "https://example.com/.well-known/a2a/revocations"
        }
      }
    ]
  },
  "defaultInputModes": ["application/json"],
  "defaultOutputModes": ["application/json"],
  "skills": [
    {
      "id": "execute-trade",
      "name": "Execute Trade",
      "description": "Execute an equity trade within authorized scope"
    }
  ]
}
```

### 3.2. Authorization Models

The `authorization_model` field indicates the authorization paradigm the
agent uses:

- **`CAPABILITY`**: The caller presents a capability token containing
  explicit scopes. Authorization is determined by verifying the token and
  matching requested scopes against granted scopes.
- **`ROLE`**: The caller presents a role identifier. Authorization is
  determined by mapping roles to permitted operations.
- **`ATTRIBUTE`**: Authorization is determined by evaluating attributes of
  the caller, the resource, and the environment against a policy
  (Attribute-Based Access Control).

This proposal focuses primarily on the capability model, as it provides
the strongest guarantees against ambient authority and is most amenable to
cross-organizational verification.

## 4. Capability-Based Authorization

### 4.1. Scope Grammar

Scopes follow a hierarchical, dot-separated grammar:

```text
scope       = segment *("." segment)
segment     = 1*( ALPHA / DIGIT / "-" / "_" )
wildcard    = scope ".*"
```

**Examples:**

- `trade.execute` — permission to execute trades
- `portfolio.read` — permission to read portfolio data
- `trade.*` — permission for all trade-related operations
- `finance.trade.execute` — a more specific scope within a hierarchy

Scope hierarchies are interpreted as containment: a grant of `trade`
implicitly grants `trade.execute`, `trade.cancel`, and any other scope
prefixed by `trade.`.

### 4.2. Scope Verification

When a client agent sends a request to a server agent, the server agent
verifies that the client's capability token contains sufficient scopes
for the requested operation.

**Verification algorithm (pseudocode):**

```text
function verify_scopes(requested: list of string, granted: list of string) -> boolean:
    for each req in requested:
        matched = false
        for each g in granted:
            if req == g:
                matched = true
            else if req starts with g + ".":
                matched = true    // g is a parent scope
            else if g ends with ".*" and req starts with g[:-1]:
                matched = true    // wildcard grant (g[:-1] strips "*", keeps ".")
        if not matched:
            return false
    return true
```

### 4.3. Capability Token Format

Capability tokens are transmitted in the `Authorization` HTTP header or
in the request `metadata` under the extension namespace. The token
structure is:

| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| `issuer` | `string` | Yes | Identifier of the entity that issued the token. |
| `subject` | `string` | Yes | Identifier of the agent the token was issued to. |
| `scopes` | `string[]` | Yes | List of granted scopes. |
| `issued_at` | `string` (ISO 8601) | Yes | When the token was issued. |
| `expires_at` | `string` (ISO 8601) | Yes | When the token expires. |
| `signature` | `string` (base64url) | Yes | Cryptographic signature over the token payload. |
| `algorithm` | `string` | Yes | Signing algorithm (e.g., `"Ed25519"`, `"ES256"`, `"ML-DSA-87"`). |

**Example capability token (JSON representation):**

```json
{
  "issuer": "agent-registry.example.com",
  "subject": "portfolio-manager-agent-7a3f",
  "scopes": ["trade.execute", "portfolio.read"],
  "issued_at": "2026-03-04T12:00:00Z",
  "expires_at": "2026-03-04T13:00:00Z",
  "signature": "<base64url-encoded-signature>",
  "algorithm": "Ed25519"
}
```

### 4.4. Confused Deputy Mitigation

To prevent confused deputy attacks, authorization checks MUST distinguish
between the **requester** (the agent initiating the request) and the
**executor** (the agent performing the action). The server agent MUST
verify:

1. The capability token's `subject` matches the authenticated caller
   identity.
2. The requested scopes are sufficient for the requested operation.
3. The token has not expired and has not been revoked.

If any check fails, the server MUST reject the request with HTTP 403.

## 5. Delegation Chains

Delegation enables multi-hop agent workflows where Agent A authorizes
Agent B to act on its behalf, and Agent B can present this delegation
to Agent C for verification. This is the core technical contribution
of this proposal, directly addressing [#19](https://github.com/a2aproject/A2A/issues/19).

### 5.1. Delegation Link

Each hop in a delegation chain is represented by a `DelegationLink`:

| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| `delegator` | `string` | Yes | Identifier of the delegating agent. |
| `delegate` | `string` | Yes | Identifier of the agent receiving delegated authority. |
| `scopes` | `string[]` | Yes | Scopes being delegated (must be equal to or narrower than the granting agent's scopes). |
| `issued_at` | `string` (ISO 8601) | Yes | When the delegation was created. |
| `expires_at` | `string` (ISO 8601) | Yes | When the delegation expires. |
| `delegation_proof` | `string` (base64url) | Yes | Cryptographic signature by the delegating agent over the link payload. |
| `algorithm` | `string` | Yes | Signing algorithm used for the proof. |
| `nonce` | `string` | Yes | Unique value to prevent replay attacks. |

**Example delegation chain (two hops):**

```json
{
  "delegation_chain": [
    {
      "delegator": "portfolio-manager-agent-7a3f",
      "delegate": "trade-router-agent-b2c4",
      "scopes": ["trade.execute"],
      "issued_at": "2026-03-04T12:00:00Z",
      "expires_at": "2026-03-04T12:30:00Z",
      "delegation_proof": "<base64url-encoded-proof>",
      "algorithm": "Ed25519",
      "nonce": "a1b2c3d4e5f6"
    },
    {
      "delegator": "trade-router-agent-b2c4",
      "delegate": "market-access-agent-d8e9",
      "scopes": ["trade.execute"],
      "issued_at": "2026-03-04T12:00:30Z",
      "expires_at": "2026-03-04T12:15:00Z",
      "delegation_proof": "<base64url-encoded-proof>",
      "algorithm": "Ed25519",
      "nonce": "f6e5d4c3b2a1"
    }
  ]
}
```

### 5.2. Chain Verification

The receiving agent verifies a delegation chain by checking each link
in sequence. If any link fails verification, the entire chain is
invalid.

**Verification algorithm (pseudocode):**

```text
function verify_delegation_chain(chain: list of DelegationLink) -> VerificationResult:
    current_time = now()

    // Step 0: Verify chain depth against policy
    if len(chain) > max_delegation_depth:
        return VerificationResult(
            valid: false,
            failure_point: 0,
            reason: "exceeds_max_depth"
        )

    for i, link in enumerate(chain):
        // Step 1: Verify the cryptographic signature
        signer_key = resolve_public_key(link.delegator)
        payload = canonical_bytes(link without delegation_proof)
        if not verify_signature(signer_key, link.delegation_proof, payload, link.algorithm):
            return VerificationResult(
                valid: false,
                failure_point: i,
                reason: "invalid_signature"
            )

        // Step 2: Verify scope narrowing (scopes can only narrow, never widen)
        if i > 0:
            if not verify_scopes(link.scopes, chain[i - 1].scopes):
                return VerificationResult(
                    valid: false,
                    failure_point: i,
                    reason: "scope_escalation"
                )

        // Step 3: Verify temporal validity
        if link.expires_at < current_time:
            return VerificationResult(
                valid: false,
                failure_point: i,
                reason: "expired"
            )

        // Step 4: Verify temporal nesting (child cannot outlive parent)
        if i > 0:
            if link.expires_at > chain[i - 1].expires_at:
                return VerificationResult(
                    valid: false,
                    failure_point: i,
                    reason: "temporal_exceeds_parent"
                )

        // Step 5: Verify chain continuity (delegate of link N must match
        //         the delegator of link N+1)
        if i > 0:
            if link.delegator != chain[i - 1].delegate:
                return VerificationResult(
                    valid: false,
                    failure_point: i,
                    reason: "chain_discontinuity"
                )

        // Step 6: Check revocation status
        if is_revoked(link.delegator, link.delegate, link.nonce):
            return VerificationResult(
                valid: false,
                failure_point: i,
                reason: "revoked"
            )

    return VerificationResult(
        valid: true,
        chain_length: len(chain),
        effective_scopes: chain[-1].scopes,
        effective_expiry: min(link.expires_at for link in chain)
    )
```

### 5.3. Key Properties

The delegation chain design guarantees the following properties:

- **Scope narrowing only.** Each successive link in the chain may grant
  equal or fewer scopes than its parent. Scope escalation is a
  verification failure.
- **Temporal intersection.** A child delegation cannot exceed the lifetime
  of its parent. The effective expiry of the chain is the minimum
  `expires_at` across all links.
- **Chain continuity.** The `delegate` of link *N* must equal the
  `delegator` of link *N+1*. Any gap invalidates the chain.
- **Fail-closed.** If any link fails any verification step, the entire
  chain is rejected. There is no partial acceptance.
- **Revocation propagation.** Revoking link *N* implicitly invalidates
  all links *N+1*, *N+2*, ..., because chain continuity cannot be
  established through a revoked link.
- **Offline verification.** Given the delegation chain and the signing
  agents' public keys, verification can proceed without callbacks
  to the original granting agent. This is critical for latency-sensitive
  and disconnected environments.
- **Replay protection.** The `nonce` field ensures that each delegation
  link is unique. Verifiers SHOULD maintain a nonce registry for active
  delegations.

### 5.4. Delegation in A2A Requests

Delegation chains are transmitted in the request `metadata` under the
extension namespace key:

```json
{
  "jsonrpc": "2.0",
  "method": "SendMessage",
  "id": "1",
  "params": {
    "message": {
      "messageId": "msg-001",
      "role": "ROLE_USER",
      "parts": [{"text": "Execute trade: 100 shares AAPL at market"}]
    },
    "metadata": {
      "urn:a2a:ext:authorization:v1/delegation_chain": [],
      "urn:a2a:ext:authorization:v1/capability_token": {}
    }
  }
}
```

The `delegation_chain` value is an array of `DelegationLink` objects (see
Section 5.1). The `capability_token` value is a `CapabilityToken` object
(see Section 4.3).

## 6. Trust Scoring

Trust scoring provides a quantitative signal for authorization decisions
based on an agent's observable track record. It is not a replacement for
cryptographic verification but serves as an additional input for
risk-based authorization policies.

### 6.1. Penalty-Based Model

Trust scores use a penalty-based model. All agents begin at a score of
1.0. Only verifiable, observable evidence can reduce the score. Agents
cannot inflate their own score through self-reported signals.

**Scoring algorithm (pseudocode):**

```text
function compute_trust_score(agent_id: string, evidence_store) -> float:
    score = 1.0
    records = evidence_store.get_records(agent_id)

    // Penalty 1: Evidence chain integrity violation (-0.5)
    if not verify_chain_integrity(records):
        score = score - 0.5

    // Penalty 2: Outcome failures (up to -0.4, excludes PENDING)
    outcomes = [r for r in records where r.outcome_status in ("ACHIEVED", "FAILED", "PARTIAL")]
    if len(outcomes) > 0:
        achieved = count(o in outcomes where o.outcome_status == "ACHIEVED")
        failure_rate = 1.0 - (achieved / len(outcomes))
        score = score - (failure_rate * 0.4)

    // Penalty 3: Credential staleness (-0.1)
    if days_since_last_credential_rotation(agent_id) > 90:
        score = score - 0.1

    return max(round(score, 4), 0.0)
```

### 6.2. Trust Levels

| Score Range | Level | Interpretation |
| :---------- | :---- | :------------- |
| >= 0.9 | HIGH | Agent has a strong track record with intact evidence chain. |
| >= 0.5 | MODERATE | Some issues detected; additional verification recommended. |
| > 0.0 | LOW | Significant issues detected; restrict to low-risk operations. |
| 0.0 | NONE | No history, or trust fully depleted. |

### 6.3. Design Constraints

- **No self-reporting.** Trust scores are derived exclusively from
  observable evidence records and cryptographic verification. An agent
  cannot submit data that increases its own score.
- **Absence is not penalized.** New agents with no history receive a
  score of 1.0 (benefit of the doubt). Trust is reduced only by
  verifiable negative evidence.
- **Per-agent chain integrity.** Each agent's evidence chain is
  evaluated independently. An agent is not penalized for chain integrity
  failures of other agents.
- **Observable outcomes only.** Trust reflects whether the agent's
  declared intent matched the observed outcome. Intent without outcome
  data is not scored.

## 7. Audit Evidence Format

This section defines a normative format for append-only, tamper-evident
records of agent actions. These records enable independent third-party
verification without requiring trust in the system that produced them.

### 7.1. Evidence Record

Each action that an agent performs (or declines to perform) SHOULD
produce an evidence record:

| Field | Type | Required | Description |
| :---- | :--- | :------- | :---------- |
| `record_id` | `string` | Yes | Unique identifier for this record. |
| `agent_id` | `string` | Yes | Identifier of the agent that performed the action. |
| `task_id` | `string` | No | The A2A task ID, if applicable. |
| `action_type` | `string` | Yes | The type of action (e.g., `"trade.execute"`, `"data.read"`). |
| `intent` | `object` | Yes | Structured description of the intended action. |
| `decision` | `string` | Yes | One of `"ALLOW"`, `"DENY"`, `"ABSTAIN"`. |
| `outcome` | `object` | No | Structured description of the observed outcome, when available. |
| `outcome_status` | `string` | No | One of `"ACHIEVED"`, `"FAILED"`, `"PARTIAL"`, `"PENDING"`. |
| `timestamp_utc` | `string` (ISO 8601) | Yes | When the action occurred, in UTC. |
| `prev_record_hash` | `string` (hex) | Yes | SHA-256 hash of the previous record (or 64 hex zeros for the first record). |
| `record_hash` | `string` (hex) | Yes | SHA-256 hash of this record (see Section 7.2). |
| `signature` | `string` (base64url) | No | Cryptographic signature over the `record_hash`. |
| `signature_algorithm` | `string` | No | Algorithm used for the signature. |

**Example evidence record:**

```json
{
  "record_id": "ev-2026-03-04-001",
  "agent_id": "trade-executor-agent-d8e9",
  "task_id": "task-abc-123",
  "action_type": "trade.execute",
  "intent": {
    "symbol": "AAPL",
    "quantity": 100,
    "side": "buy",
    "order_type": "market"
  },
  "decision": "ALLOW",
  "outcome": {
    "status": "filled",
    "fill_price": 187.42,
    "fill_quantity": 100
  },
  "outcome_status": "ACHIEVED",
  "timestamp_utc": "2026-03-04T12:01:15Z",
  "prev_record_hash": "a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90",
  "record_hash": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8091a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d",
  "signature": "<base64url-encoded-signature>",
  "signature_algorithm": "Ed25519"
}
```

### 7.2. Hash Chain Construction

Evidence records form a tamper-evident chain. Each record's hash is
computed over the previous record's hash concatenated with the
canonical representation of the current record (excluding the hash
fields themselves):

```text
record_hash = SHA-256(
    prev_record_hash || canonical_json(record without record_hash and prev_record_hash)
)
```

Where `canonical_json` produces a deterministic JSON encoding:
sorted keys, no extraneous whitespace, UTF-8 encoding.

The first record in an agent's chain uses `prev_record_hash` =
`"0000000000000000000000000000000000000000000000000000000000000000"`
(64 hex zeros).

### 7.3. Chain Verification

Any party with access to the evidence records can independently verify
the chain integrity:

```text
function verify_chain_integrity(records: list of EvidenceRecord) -> boolean:
    for i, record in enumerate(records):
        // Reconstruct the expected hash
        record_without_hashes = record without record_hash and prev_record_hash
        expected_hash = SHA-256(record.prev_record_hash || canonical_json(record_without_hashes))

        if expected_hash != record.record_hash:
            return false

        // Verify chain linkage
        if i > 0 and record.prev_record_hash != records[i - 1].record_hash:
            return false

        // Verify signature if present
        if record.signature is not null:
            agent_key = resolve_public_key(record.agent_id)
            if not verify_signature(agent_key, record.signature, expected_hash, record.signature_algorithm):
                return false

    return true
```

### 7.4. Normative Requirements

Implementations supporting the evidence extension:

1. **Append-only.** Evidence records MUST NOT be modified after creation.
   Historical records MUST NOT be deleted or altered.
2. **Independent verifiability.** The hash chain MUST be verifiable by
   any party with the records and the signing agent's public key,
   without trusting the system that wrote the records.
3. **Fail-closed recommendation.** If an evidence record cannot be
   written (e.g., due to storage failure), the associated action
   SHOULD NOT proceed. Implementations MAY choose to proceed with
   degraded audit capability, but MUST log the evidence write failure.
4. **Complete records.** Evidence records MUST include intent and
   decision. The outcome field SHOULD be populated when the outcome is
   known (immediately or asynchronously).
5. **Cryptographic signatures.** Implementations SHOULD sign evidence
   records. For long-lived audit trails (regulatory retention periods
   exceeding 10 years), post-quantum signature algorithms such as
   ML-DSA-87 (FIPS 204) are RECOMMENDED.

## 8. Authorization Flows

This section describes three normative authorization flows that combine
the capabilities defined above.

### 8.1. Flow 1: Direct Authorization

The simplest flow. A client agent presents a capability token to a
server agent.

```text
Client Agent                              Server Agent
     |                                         |
     |--- SendMessage (with capability token) -->
     |                                         |
     |                          verify_scopes(requested, token.scopes)
     |                          verify token signature, expiry, revocation
     |                                         |
     |                          decision: ALLOW or DENY
     |                          write evidence record
     |                                         |
     |<-- Task result (with evidence record) --|
```

### 8.2. Flow 2: Delegated Authorization

A multi-hop flow where an upstream agent delegates authority through
one or more intermediaries.

```text
User / Orchestrator       Agent A              Agent B              Agent C
        |                   |                    |                    |
        |-- credential ---->|                    |                    |
        |                   |                    |                    |
        |                   |-- delegation(A->B, scopes) ----------->|
        |                   |                    |                    |
        |                   |                    |-- delegation(B->C, narrowed scopes) ->|
        |                   |                    |                    |
        |                   |                    |    verify_delegation_chain([A->B, B->C])
        |                   |                    |    verify_scopes(requested, chain.effective_scopes)
        |                   |                    |    decision: ALLOW or DENY
        |                   |                    |    write evidence record
        |                   |                    |                    |
        |                   |                    |<-- result ---------|
        |                   |<-- result ---------|                    |
        |<-- result --------|                    |                    |
```

### 8.3. Flow 3: Trust-Gated Authorization

Authorization is conditioned on the caller's trust score. This is
useful for operations where the risk level varies and the server agent
wants to apply proportional controls.

```text
Agent A                                   Agent B
  |                                         |
  |--- SendMessage (with token + chain) --->|
  |                                         |
  |                          trust = compute_trust_score(Agent A)
  |                          if trust < threshold:
  |                              DENY (insufficient trust)
  |                          else:
  |                              verify_scopes(...)
  |                              verify_delegation_chain(...)
  |                              decision: ALLOW or DENY
  |                              write evidence record
  |                                         |
  |<-- Task result (with evidence) ---------|
```

## 9. Worked Examples

### 9.1. Financial Services: Trade Execution

A portfolio management agent needs to execute a trade through a
specialized execution agent, via an intermediary routing agent.

1. **Authorization setup.** The portfolio manager holds a capability
   token with scopes `["trade.execute", "portfolio.read"]`, issued by
   the organization's agent registry with a 1-hour expiry.
2. **Delegation.** The portfolio manager creates a delegation link to
   the trade router with scopes `["trade.execute"]` (narrowed from the
   original set) and a 30-minute expiry.
3. **Second hop.** The trade router creates a delegation link to the
   market access agent with the same scope `["trade.execute"]` and a
   15-minute expiry (further narrowed temporally).
4. **Verification.** The market access agent receives the chain
   `[portfolio-manager -> trade-router, trade-router -> market-access]`,
   verifies all signatures, confirms scope narrowing, confirms temporal
   nesting, and checks no links are revoked.
5. **Execution and evidence.** The market access agent executes the
   trade, writes an evidence record with intent (buy 100 AAPL at
   market), decision (ALLOW), and outcome (filled at 187.42), linked
   to the previous record in its evidence chain.
6. **Audit.** A compliance officer independently verifies the evidence
   chain and delegation chain without accessing the market access
   agent's internal systems.

### 9.2. Healthcare: Patient Data Access

A diagnostic agent needs to access patient records held by a data
custodian agent, with strict scope controls mandated by healthcare
regulations.

1. The diagnostic agent presents a capability token with scope
   `["patient.records.read"]` and a delegation chain from the
   treating physician's agent.
2. The data custodian verifies the chain, confirms the scope is
   limited to read access (no `patient.records.write`), and confirms
   the temporal bounds fall within the treatment episode.
3. The data custodian writes an evidence record containing the access
   intent, decision, and a reference to the accessed record set
   (without embedding patient data in the evidence).
4. The evidence chain provides an auditable trail for regulatory
   compliance review.

### 9.3. Supply Chain: Multi-Vendor Coordination

An orchestration agent coordinates procurement across multiple vendor
agents, each with different trust levels.

1. The orchestration agent evaluates each vendor agent's trust score.
   Vendor agents with HIGH trust (>= 0.9) may proceed with standard
   authorization. Vendor agents with MODERATE trust (>= 0.5) require
   additional scope restrictions. Vendor agents with LOW trust (> 0.0)
   are restricted to read-only scopes, and agents with NONE trust (0.0)
   are rejected entirely.
2. Delegation chains are scoped per vendor: `["procurement.quote"]`
   for quoting, `["procurement.order"]` added only for the selected
   vendor after evaluation.
3. Each vendor agent writes evidence records for every quote and order
   action, creating independent audit trails.
4. Credential rotation is enforced: the orchestration agent's
   revocation endpoint allows immediate revocation of any vendor
   delegation if anomalies are detected.

## 10. Security Considerations

### 10.1. Post-Quantum Readiness

Evidence records may need to remain verifiable for decades (regulatory
retention requirements). Signature algorithms based on elliptic curves
(Ed25519, ECDSA) may become vulnerable to quantum computing attacks
within this timeframe.

Implementations SHOULD support algorithm agility by treating the
`algorithm` field as a negotiable parameter. For long-lived evidence,
post-quantum algorithms such as ML-DSA-87 (FIPS 204, standardized
August 2024) are RECOMMENDED.

### 10.2. Key Management

- Public keys for signature verification MUST be discoverable through
  the agent's AgentCard or a referenced key distribution endpoint.
- Private key material MUST NOT appear in evidence records, delegation
  links, capability tokens, logs, or API responses.
- Key rotation MUST be possible without breaking active delegation
  chains. Implementations SHOULD support a grace period where both
  old and new keys are accepted.

### 10.3. Replay Protection

- Capability tokens MUST include an expiry time.
- Delegation links MUST include a `nonce` field.
- Verifiers SHOULD maintain a nonce registry for the duration of the
  token/delegation lifetime to detect replay attempts.
- Evidence records are inherently replay-protected by the hash chain
  (each record's hash depends on its predecessor).

### 10.4. Revocation

- Revocation checks SHOULD be performed at verification time.
- The `revocation_endpoint` in the AgentCard extension parameters
  SHOULD support both individual credential revocation and bulk
  revocation (e.g., all delegations from a specific agent).
- Revocation propagation MUST complete within a bounded time.
  Implementations SHOULD document their revocation propagation latency.

### 10.5. Evidence Integrity Under Adversarial Conditions

- An adversary who compromises an agent's signing key can forge future
  evidence records but cannot alter historical records without
  breaking the hash chain.
- Implementations SHOULD periodically checkpoint evidence chain hashes
  to an independent tamper-evident store (e.g., a transparency log or
  distributed ledger) to provide additional assurance against
  undetected chain replacement attacks.

## 11. Compatibility

### 11.1. Backward Compatibility

This proposal is fully backward-compatible with the existing A2A
protocol:

- All new fields are defined as extension parameters, not modifications
  to core data structures.
- Existing A2A implementations that do not support this extension
  continue to function without modification.
- The extension uses the standard A2A extension activation mechanism
  (`A2A-Extensions` header).

### 11.2. Incremental Adoption

The three capabilities can be adopted independently:

- **Authorization only.** An agent can advertise and enforce
  capability-based scopes without supporting delegation or evidence.
- **Authorization + delegation.** An agent can support delegation
  chains without requiring evidence records.
- **Full stack.** An agent can require all three capabilities for
  maximum assurance.

### 11.3. Integration with Existing Authentication

This extension complements, rather than replaces, the existing A2A
authentication mechanisms (OAuth 2.0, API keys, OIDC). Authentication
establishes the caller's identity; this extension establishes what the
caller is authorized to do, whether that authority was delegated, and
provides a verifiable record of what actually happened.

## 12. References

- EU AI Act, Regulation (EU) 2024/1689, Article 50 (Transparency obligations)
- NIST AI 600-1, Artificial Intelligence Risk Management Framework: Generative AI Profile
- [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final), Module-Lattice-Based Digital Signature Standard (ML-DSA)
- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110), HTTP Semantics (Authorization header)
- [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519), JSON Web Token (JWT)
- [A2A Protocol Specification](../specification.md), Sections 13.1-13.4 (Security)
- [A2A Extensions](extensions.md), Extension mechanism documentation
- Dennis, J. B. and Van Horn, E. C., "Programming Semantics for Multiprogrammed Computations," Communications of the ACM, 1966 (foundational capability-based security)
- Miller, M. S. et al., "Capability Myths Demolished," Technical Report, 2003
