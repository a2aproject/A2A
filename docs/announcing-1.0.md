# Introducing A2A Protocol v1.0: Building a Mature Agent Ecosystem

The A2A (Agent2Agent) Protocol has officially reached version 1.0, marking a major milestone in a collaborative, community-led effort to define how AI agents interoperate at scale. Built through open contribution and evolving alongside real-world implementation feedback, v1.0 represents the protocol reaching a level of maturity and stability that the community is confident standing behind — with a focus on standardization, type safety, and a refined developer experience.

## Key Highlights of v1.0

**Standardization & Maturity:** v1.0 formally adopts a suite of industry standards — RFC 9457 for error handling, RFC 8785 (JSON Canonicalization Scheme) for Agent Card signing, and RFC 7515 (JWS) for security. The release also introduces stricter adherence to REST, gRPC, and JSON-RPC patterns, as well as a comprehensive versioning strategy with explicit backward compatibility rules.

**Enhanced Type Safety:** v1.0 replaces `kind` discriminator fields with JSON member-based polymorphism, making it easier to determine content types by checking which field is present. Enum values have been standardized to `SCREAMING_SNAKE_CASE` — for example, task states are now `TASK_STATE_COMPLETED` instead of `completed`, and message roles are `ROLE_USER` instead of `user`. Timestamps are now explicitly ISO 8601 UTC with millisecond precision.

**Enterprise-Ready Features:** Security gets a major upgrade with Agent Card signature verification using JWS and JSON Canonicalization. OAuth 2.0 support is modernized — the Device Code flow (RFC 8628) is added, deprecated implicit and password flows are removed, and PKCE support is introduced for the Authorization Code flow. Critically, v1.0 adds **native multi-tenancy support**: a new `tenant` field on gRPC requests allows a single agent endpoint to serve multiple organizations without URL-based workarounds.

**Improved Developer Experience:** All operations have been renamed for consistency — `message/send` becomes `SendMessage`, `tasks/get` becomes `GetTask`, `tasks/cancel` becomes `CancelTask`, and so on. Complex compound IDs like `tasks/{id}` are replaced with simple UUID literals. The `/v1/` prefix is removed from HTTP URL paths, with versioning now handled at the `AgentInterface` level. Task listing has also moved from page-number pagination to cursor-based pagination for better scalability.

## Breaking Changes to Know About

The most impactful change for developers is the **complete redesign of the `Part` object**. The separate `TextPart`, `FilePart`, and `DataPart` types are gone — replaced by a single unified `Part` message where content type is determined by which field is present (`text`, `url`, `raw`, or `data`). The `mimeType` field is also renamed to `mediaType` across all part types.

Streaming also changes: the `kind` discriminator field is removed from stream events (use JSON member names to distinguish `TaskStatusUpdateEvent` from `TaskArtifactUpdateEvent`), and the `final` boolean field is removed from `TaskStatusUpdateEvent` in favor of transport-level stream closure signals.

The `AgentCard` structure sees significant restructuring too — `protocolVersion` moves from the top-level card to individual `AgentInterface` objects, and `preferredTransport`/`additionalInterfaces` are consolidated into a single `supportedInterfaces[]` array.

## Migration Path

The A2A team recommends a phased approach: start by building a compatibility layer that translates v0.3.0 structures to v1.0, then run dual support while updating consumers, before cutting over to v1.0 exclusively. The Part type unification and enum value changes are flagged as the most critical items to address immediately.

## The Protocol's Relationship with MCP

v1.0 also formally clarifies A2A's relationship with the Model Context Protocol (MCP): MCP handles tool integration for individual agents, while A2A orchestrates the coordination *between* agents. They are complementary, not competing.

## The Path Forward

A2A v1.0 is a foundation for a reliable, multi-agent future — one with the security, scalability, and interoperability required for production AI environments.

More details are available at: [a2a-protocol.org](https://a2a-protocol.org/latest/whats-new-v1/).
