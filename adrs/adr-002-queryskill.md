# ADR 002: Dynamic Skill Introspection (`QuerySkill`)

## Status
Proposed

## Context
The A2A protocol today relies entirely on the `AgentCard` for capability discovery. That card is a static, cached document published at `/.well-known/agent.json` or accessed via `GetExtendedAgentCard`.
The problem is that agent capabilities are not truly static. They vary based on load, configuration, runtime environment, available models, feature flags, and context.
An orchestrator agent has no way to ask: "Can you handle this specific task right now, with these parameters?"
The result is that orchestrators either over-delegate (sending tasks to agents that will fail) or under-delegate (avoiding agents whose card looks uncertain). There is also no concept of partial capability — an agent that can do 80% of a requested skill but not the full scope cannot express that today.

## Decision
We will add a `QuerySkill` RPC to `a2a.proto` as a capability declaration, not a task execution.

The design has three layers:
1.  **Proto definition**: Add `SkillQueryRequest` and `SkillQueryResult` messages, and the `SkillSupportLevel` enum with values `SUPPORTED`, `PARTIAL`, and `UNSUPPORTED`.
2.  **Protocol binding**: Map to JSON-RPC as `skills/query`, to gRPC as `QuerySkill` on the existing `A2AService`, and to HTTP/REST as `POST /skills/{skill_id}/query`. All bindings must return `UnsupportedOperationError` if the server hasn't declared `capabilities.skill_query: true` in its `AgentCard`.
3.  **Caching and staleness**: `SkillQueryResult` includes a `cache_ttl_seconds` field. Furthermore, we define `stale-if-error` semantics: if a `QuerySkill` call fails transiently, the orchestrator MAY use a cached `SUPPORTED` result for up to 2 × `cache_ttl_seconds`.

## Consequences
*   **Proactive Capability Checking:** Clients can avoid costly `SendMessage` calls when the agent cannot support the specific request right now.
*   **Partial Negotiation:** Agents can use the `constraints` map to request changes from the client (e.g., chunking smaller files).
*   **Explicit declaration:** Agents must opt into this by setting `skill_query = true` in their capabilities, maintaining compatibility.

## Rejected Alternatives
*   **Using `GetExtendedAgentCard`:** This is too coarse and cannot carry the varied runtime context without combinatorial explosion.
*   **Adding a `supports` field to `SendMessage`:** This requires the client to fully constuct the message payload (potentially including large artifacts) before discovering unsupportability, defeating the core benefit.
*   **Polling `GetTask` for failures:** This is reactive, not proactive, and still incurs the initial transmission and processing cost. The chosen design is proactive and non-destructive.
