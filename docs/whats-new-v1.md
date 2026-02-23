# What's New in A2A Protocol v1.0

This document provides a comprehensive overview of changes from A2A Protocol v0.3.0 to v1.0. The v1.0 release represents a significant maturation of the protocol with enhanced clarity, stronger specifications, and important structural improvements.

## Overview of Major Themes

The v1.0 release focuses on four major themes:

### 1. **Protocol Maturity and Standardization**

- Leverage formal specification standards (RFC 9457, RFC 8785, RFC 7515) where possible
- Stricter adherence to industry-standard patterns for REST, gRPC, and JSON-RPC bindings
- Enhanced versioning strategy with explicit backward compatibility rules
- Comprehensive error taxonomy with protocol-specific mappings

### 2. **Enhanced Type Safety and Clarity**

- Removal of discriminator `kind` fields in favor of JSON member-based polymorphism
- **Breaking:** Enum values changed from `kebab-case` to `SCREAMING_SNAKE_CASE` for compliance with the ProtoJSON specification
- Stricter field naming conventions (`camelCase` for JSON)
- More precise timestamp specifications (ISO 8601 with millisecond precision)
- Better-defined data types with clearer Optional vs Required semantics

### 3. **Improved Developer Experience**

- Renamed operations for consistency and clarity
- Reorganized Agent Card structure for better logical grouping
- Enhanced extension mechanism with versioning and requirement declarations
- More explicit service parameter handling (A2A-Version, A2A-Extensions headers)
- **Simplified ID format** - Removed complex compound IDs (e.g., `tasks/{id}`) in favor of simple UUIDs
- **Protocol versioning per interface** - Each AgentInterface specifies its own protocol version for better backward compatibility
- **Multi-tenancy support** - Native tenant scoping in gRPC requests

### 4. **Enterprise-Ready Features**

- Agent Card signature verification using JWS and JSON Canonicalization
- Formal specification of all three protocol bindings with equivalence guarantees
- Enhanced security scheme declarations with mutual TLS support
- **Modern OAuth 2.0 flows** - Added Device Code flow (RFC 8628), removed deprecated implicit/password flows
- **PKCE support** - Added `pkce_required` field to Authorization Code flow for enhanced security
- Cursor-based pagination for scalable task listing

---

## Behavioral Changes for Core Operations

### Send Message (`message/send` → **`SendMessage`**)

**v0.3.0 Behavior:**

- Operation named `message/send`
- Less formal specification of when `Task` vs `Message` is returned

**v1.0 Changes:**

- **✅ RENAMED:** Operation now **`SendMessage`**
- **✅ CLARIFIED:** More precise specification of Task vs Message return semantics

### Send Streaming Message (`message/stream` → **SendStreamingMessage**)

**v0.3.0 Behavior:**

- Operation named `message/stream`
- Stream events had `kind` discriminator field

**v1.0 Changes:**

- **✅ RENAMED:** Operation now **`SendStreamingMessage`**
- **✅ BREAKING:** Stream events no longer have `kind` field
    - Use JSON member names to discriminate between `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent`
- **✅ REMOVED:** `final` boolean field removed from TaskStatusUpdateEvent. Leverage protocol binding specific stream closure mechanism instead.
- **✅ CLARIFIED:** Multiple concurrent streams allowed; all receive same ordered events

### Get Task (`tasks/get` → **GetTask**)

**v0.3.0 Behavior:**

- Operation named `tasks/get`
- Returns task with status, artifacts, and optionally history
- Less formal specification of what "include history" means

**v1.0 Changes:**

- **✅ RENAMED:** Operation now **GetTask**
- **✅ NEW:** `createdAt` and `lastModified` timestamp fields added to Task object
- **✅ CLARIFIED:** More precise specification of history inclusion behavior
- **✅ NEW:** Task object now includes `extensions[]` array in messages and artifacts
- **✅ CLARIFIED:** Authentication/authorization scoping - servers MUST only return tasks visible to caller

### List Tasks (`tasks/list` → **ListTasks**)

**v0.3.0 Behavior:**

- Operation named `tasks/list`
- Available in gRPC and REST only
- Basic pagination with page numbers

**v1.0 Changes:**

- **✅ RENAMED:** Operation now **ListTasks**
- **✅ BREAKING:** Changed to cursor-based pagination for scalability
    - Request: `cursor` (opaque token from previous response), `limit` (max results)
    - Response: `tasks[]`, `nextCursor` (for next page)
- **✅ NEW:** Enhanced filtering capabilities with more explicit specifications
- **✅ CLARIFIED:** Task visibility scoped to authenticated caller

### Cancel Task (`tasks/cancel` → **CancelTask**)

**v0.3.0 Behavior:**

- Operation named `tasks/cancel`
- Request with taskId, returns Task

**v1.0 Changes:**

- **✅ RENAMED:** Operation now **CancelTask**
- **✅ CLARIFIED:** More precise specification of when cancellation is allowed
- **✅ CLARIFIED:** Task state transitions for cancellation scenarios

### Get Agent Card (Well-known URI and **GetExtendedAgentCard**)

**v0.3.0 Behavior:**

- Discovery via `/.well-known/agent-card.json`
- Extended card via `agent/getAuthenticatedExtendedCard`
- `supportsAuthenticatedExtendedCard` boolean at top level

**v1.0 Changes:**

- **✅ RENAMED:** `agent/getAuthenticatedExtendedCard` → **GetExtendedAgentCard**
- **✅ BREAKING:** `supportsAuthenticatedExtendedCard` moved to `capabilities.extendedAgentCard`
- **✅ NEW:** Canonicalization (RFC 8785) clarified for Agent Card signature
- **✅ BREAKING:** `protocolVersion` moved from AgentCard to individual AgentInterface objects
- **✅ BREAKING:** `preferredTransport` and `additionalInterfaces` consolidated into `supportedInterfaces[]`
    - Each interface has `url`, `protocolBinding`, and `protocolVersion`

### Subscribe to task (`tasks/resubscribe` → **SubscribeToTask**)

**v0.3.0 Behavior:**

- Used `tasks/resubscribe` to reconnect interrupted SSE streams
- Backfill behavior implementation-dependent

**v1.0 Changes:**

- **✅ RENAMED:** Operation now **SubscribeToTask**
- **✅ CLARIFIED:** Formal specification of streaming subscription lifecycle
- **✅ CLARIFIED:** Stream closure behavior when task reaches terminal state
- **✅ CLARIFIED:** Multiple concurrent subscriptions supported per task

### Push Notification Operations

**v0.3.0 Operations:**

- `tasks/pushNotificationConfig/set`
- `tasks/pushNotificationConfig/get`
- `tasks/pushNotificationConfig/list`
- `tasks/pushNotificationConfig/delete`

**v1.0 Changes:**

- **✅ RENAMED:** Operations now **CreatePushNotificationConfig**, **GetPushNotificationConfig**, **ListPushNotificationConfigs**, **DeletePushNotificationConfig**
- **✅ NEW:** `createdAt` timestamp field added to PushNotificationConfig
- **✅ CLARIFIED:** Push notification payloads now use StreamResponse format

### NEW: Multi-Tenancy Support

**v0.3.0:**

- No native multi-tenancy support in protocol
- Tenants handled implicitly via authentication or URL paths

**v1.0 Changes:**

- **✅ NEW:** `tenant` field added to all gRPC request messages
- **✅ NEW:** `tenant` field added to `AgentInterface` to specify default tenant
- **✅ CLARIFIED:** Tenant can be provided per-request or inherited from AgentInterface
- **✅ USE CASE:** Enables agents to serve multiple organizations from single endpoint

**Example:**

```protobuf
// Represents a request for the `SendMessage` method.
message SendMessageRequest {
  // Optional tenant, provided as a path parameter.
  string tenant = 4;
  // The message to send to the agent.
  Message message = 1 [(google.api.field_behavior) = REQUIRED];
  // Configuration for the send request.
  SendMessageConfiguration configuration = 2;
  // A flexible key-value map for passing additional context or parameters.
  google.protobuf.Struct metadata = 3;
}
```

### Protocol Simplifications

#### ID Format Simplification (#1389)

**v0.3.0:**

- Some operations used complex compound IDs like `tasks/{taskId}`
- Required clients/servers to construct/deconstruct resource names

**v1.0 Changes:**

- **✅ BREAKING:** All IDs are now simple literals
- **✅ BREAKING:** Operations that previously used compound IDs now separate parent and resource ID
    - Example: `tasks/{taskId}/pushNotificationConfigs/{configId}` → separate `task_id` and `config_id` fields
- **✅ BENEFIT:** Simpler to implement - IDs map directly to database keys

#### HTTP URL Path Simplification (#1269)

**v0.3.0:**

- HTTP+JSON binding used `/v1/` prefix in URLs
- Example: `POST /v1/message:send`

**v1.0 Changes:**

- **✅ BREAKING:** Removed `/v1` prefix from HTTP+JSON URL paths
- **✅ NEW:** Examples: `POST /message:send`, `GET /tasks/{id}`
- **✅ RATIONALE:** Version specified in `AgentInterface.protocolVersion` field instead
- **✅ BENEFIT:** Cleaner URLs, version management at interface level

---

## Structural Changes in Core Model Objects

### Task Object

**Removed Fields:**

- ⛔ `kind`: Discriminator field removed (was always "task")

### TaskStatus Object

**Modified Fields:**

- ✅ `state`: **BREAKING** - Enum values changed from lowercase to `SCREAMING_SNAKE_CASE` with `TASK_STATE_` prefix
    - v0.3.0: `"submitted"`, `"working"`, `"completed"`, `"failed"`, `"canceled"`, `"rejected"`, `"input-required"`, `"auth-required"`
    - v1.0: `"TASK_STATE_SUBMITTED"`, `"TASK_STATE_WORKING"`, `"TASK_STATE_COMPLETED"`, `"TASK_STATE_FAILED"`, `"TASK_STATE_CANCELED"`, `"TASK_STATE_REJECTED"`, `"TASK_STATE_INPUT_REQUIRED"`, `"TASK_STATE_AUTH_REQUIRED"`
- ✅ `timestamp`: Now explicitly ISO 8601 UTC with millisecond precision (YYYY-MM-DDTHH:mm:ss.sssZ)

**Removed Fields:**

- None

**Example Migration:**

```json
// v0.3.0
{
  "status": {
    "state": "completed",
    "timestamp": "2024-03-15T10:15:00Z"
  }
}

// v1.0
{
  "status": {
    "state": "TASK_STATE_COMPLETED",
    "timestamp": "2024-03-15T10:15:00.000Z"
  }
}
```

### Message Object

**Added Fields:**

- ✅ `extensions[]`: Array of extension URIs applicable to this message

**Modified Fields:**

- ✅ `role`: **BREAKING** - Enum values changed from lowercase to `SCREAMING_SNAKE_CASE` with `ROLE_` prefix
    - v0.3.0: `"user"`, `"agent"`
    - v1.0: `"ROLE_USER"`, `"ROLE_AGENT"`

**Example Migration:**

```json
// v0.3.0
{
  "role": "user",
  "parts": [{"kind": "text", "text": "Hello"}]
}

// v1.0
{
  "role": "ROLE_USER",
  "parts": [{"text": "Hello"}],
}
```

**Behavior Changes:**

- Parts array now uses member-based discrimination instead of `kind` field

### Part Object

**BREAKING CHANGE - Complete Redesign:**

The Part structure has been completely redesigned in v1.0. Instead of separate TextPart, FilePart, and DataPart message types, there is now a single unified `Part` message.

**v0.3.0 Structure (Separate Types):**

```json
// Text example
{
  "kind": "text",
  "text": "Hello world"
}

// File example
{
  "kind": "file",
  "file": {
    "fileWithUri": "https://example.com/doc.pdf",
    "mimeType": "application/pdf"
  }
}

// Data example
{
  "kind": "data",
  "data": {"key": "value"}
}
```

**v1.0 Structure (Unified Part):**

```json
// Text example
{
  "text": "Hello world",
  "mediaType": "text/plain"
}

// File with URL example
{
  "url": "https://example.com/doc.pdf",
  "filename": "doc.pdf",
  "mediaType": "application/pdf"
}

// File with raw bytes example
{
  "raw": "base64encodedcontent==",
  "filename": "image.png",
  "mediaType": "image/png"
}

// Data example
{
  "data": {"key": "value"},
  "mediaType": "application/json"
}
```

**Changes:**

- ⛔ **REMOVED:** Separate `TextPart`, `FilePart`, and `DataPart` types
- ⛔ **REMOVED:** `kind` discriminator field
- ⛔ **REMOVED:** Nested `file` object structure
- ✅ **NEW:** Single unified `Part` message with `oneof content` field
- ✅ **NEW:** Content type determined by which field is present: `text`, `raw`, `url`, or `data`
- ✅ **NEW:** `mediaType` field (replaces `mimeType`) - available for all part types
- ✅ **NEW:** `filename` field - available for all part types (not just files)
- ✅ **NEW:** `raw` field for inline binary content (base64 in JSON)
- ✅ **NEW:** `url` field for file references (replaces `file.fileWithUri`)

**Migration Examples:**

```typescript
// v0.3.0
const textPart = { kind: "text", text: "Hello" };
const filePart = { kind: "file", file: { fileWithUri: "https://...", mimeType: "image/png" } };
const dataPart = { kind: "data", data: { key: "value" } };

// v1.0
const textPart = { text: "Hello", mediaType: "text/plain" };
const filePart = { url: "https://...", mediaType: "image/png", filename: "image.png" };
const dataPart = { data: { key: "value" }, mediaType: "application/json" };

// Discrimination changed from kind field to member presence
if (part.kind === "text") { ... }  // v0.3.0
if ("text" in part) { ... }        // v1.0
```

### Artifact Object

**Added Fields:**

- ✅ `extensions[]`: Array of extension URIs

**Modified Fields:**

- ✅ `parts[]`: Now uses member-based Part discrimination (see Part changes above)

### AgentCard Object

**Added Fields:**

- ✅ `supportedInterfaces[]`: Array of `AgentInterface` objects

**Removed Fields:**

- ⛔ `protocolVersion`: Removed from AgentCard (now in each AgentInterface)
- ⛔ `preferredTransport`: Consolidated into `supportedInterfaces`
- ⛔ `additionalInterfaces`: Consolidated into `supportedInterfaces`
- ⛔ `supportsAuthenticatedExtendedCard`: Moved to `capabilities.extendedAgentCard`
- ⛔ `url`: Primary endpoint now in `supportedInterfaces[0].url`

**Structure Example:**

**v0.3.0:**

```json
{
  "protocolVersion": "0.3",
  "url": "https://agent.example.com/a2a",
  "preferredTransport": "JSONRPC",
  "supportsAuthenticatedExtendedCard": true,
  "additionalInterfaces": [...]
}
```

**v1.0:**

```json
{
  "supportedInterfaces": [
    {
      "url": "https://agent.example.com/a2a",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    }
  ],
  "capabilities": {
    "extendedAgentCard": true
  },
  "signatures": [...]
}
```

### AgentCapabilities Object

**Removed Fields:**

- ⛔ `stateTransitionHistory` - Removed as no API implementation existed for this feature

**Rationale:**

The `stateTransitionHistory` capability flag was misleading as v1.0 has no corresponding API to:

- Store status history in Task objects
- Retrieve status history via Get/List operations
- Query historical state transitions

This capability may be reintroduced in a future version with proper implementation.

**Modified Fields:**

- ✅ `extendedAgentCard`: Moved from top-level `supportsAuthenticatedExtendedCard` field

### PushNotificationConfig Object

**Added Fields:**

- ✅ `configId`: Unique identifier for the configuration
- ✅ `createdAt`: Timestamp - Configuration creation time

**Modified Fields:**

- ✅ `authentication`: Enhanced PushNotificationAuthenticationInfo structure

### Stream Event Objects

**TaskStatusUpdateEvent:**

**v0.3.0:**

```json
{
  "kind": "taskStatusUpdate",
  "taskId": "...",
  "contextId": "...",
  "status": {...},
  "final": true
}
```

**v1.0:**

```json
{
  "taskStatusUpdate": {
    "taskId": "...",
    "contextId": "...",
    "status": {...}
  }
}
```

**Changes:**

- ⛔ **REMOVED:** `kind` discriminator
- ⛔ **REMOVED:** `final` boolean field (stream closure indicates completion instead)
- ✅ **NEW PATTERN:** Event type determined by JSON member name (`taskStatusUpdate` or `taskArtifactUpdate`)
- ✅ **CLARIFIED:** Terminal state indicated by protocol-specific stream closure mechanism

**TaskArtifactUpdateEvent:**

**v0.3.0:**

```json
{
  "kind": "taskArtifactUpdate",
  "taskId": "...",
  "contextId": "...",
  "artifact": {...}
}
```

**v1.0:**

```json
{
  "taskArtifactUpdate": {
    "taskId": "...",
    "contextId": "...",
    "artifact": {...},
    "index": 0
  }
}
```

**Changes:**

- ⛔ **REMOVED:** `kind` discriminator
- ✅ **NEW PATTERN:** Wrapped in `taskArtifactUpdate` object
- ✅ **NEW:** `index` field indicates artifact position in task's artifacts array

### OAuth 2.0 Security Updates (#1303)

v1.0 modernizes OAuth 2.0 support in alignment with OAuth 2.0 Security Best Current Practice (BCP).

**Removed Flows (Deprecated by OAuth BCP):**

- ⛔ `ImplicitOAuthFlow` - Deprecated due to token leakage risks in browser history/logs
- ⛔ `PasswordOAuthFlow` - Deprecated due to credential exposure risks

**Added Flows:**

- ✅ `DeviceCodeOAuthFlow` (RFC 8628) - For CLI tools, IoT devices, and input-constrained scenarios
    - Provides `device_authorization_url` endpoint
    - Supports `verification_uri`, `user_code` pattern
    - Ideal for headless environments

**Enhanced Security:**

- ✅ `pkce_required` field added to `AuthorizationCodeOAuthFlow` (RFC 7636)
    - Indicates whether PKCE (Proof Key for Code Exchange) is mandatory
    - Protects against authorization code interception attacks
    - Recommended for all OAuth clients, required for public clients

**Migration Guide:**

```typescript
// v0.3.0 - Implicit Flow (now removed)
{
  "implicitFlow": {
    "authorizationUrl": "https://auth.example.com/authorize",
    "scopes": {"read": "Read access"}
  }
}

// v1.0 - Use Authorization Code + PKCE instead
{
  "authorizationCodeFlow": {
    "authorizationUrl": "https://auth.example.com/authorize",
    "tokenUrl": "https://auth.example.com/token",
    "pkceRequired": true,
    "scopes": {"read": "Read access"}
  }
}
```

---

## New Dependencies on Other Specifications

v1.0 introduces several new formal dependencies on industry-standard specifications:

### Added Specifications

#### ✅ RFC 9457 - Problem Details for HTTP APIs

- **Purpose:** Standardized error response format
- **Usage:** HTTP+JSON binding error responses
- **Impact:** More consistent, machine-readable error handling in REST APIs

#### ✅ RFC 8785 - JSON Canonicalization Scheme (JCS)

- **Purpose:** Deterministic JSON serialization for signing
- **Usage:** Agent Card signature verification
- **Impact:** Enables cryptographic verification of Agent Card integrity
- **Details:** Canonical form used before JWS signing (excludes `signatures` field)

#### ✅ RFC 7515 - JSON Web Signature (JWS)

- **Purpose:** Cryptographic signing standard
- **Usage:** Agent Card signatures field
- **Impact:** Industry-standard signature format for trust verification
- **Details:** Supports detached signatures with public key retrieval via `jku` or trusted keystores

#### ✅ Google API Design Guidelines

- **Purpose:** gRPC best practices and conventions
- **Usage:** gRPC binding design patterns
- **Impact:** Better alignment with gRPC ecosystem expectations

#### ✅ ISO 8601

- **Purpose:** Timestamp format standard
- **Usage:** All timestamp fields (createdAt, lastModified, timestamp)
- **Impact:** Explicit format requirement: UTC with millisecond precision (YYYY-MM-DDTHH:mm:ss.sssZ)

### Existing Dependencies (Retained from v0.3.0)

- JSON-RPC 2.0
- gRPC / Protocol Buffers 3
- HTTP/HTTPS (various RFCs)
- Server-Sent Events (SSE) - W3C specification
- RFC 8615 - Well-known URIs
- OAuth 2.0, OpenID Connect (for authentication)
- TLS (RFC 8446 recommended)

### Complementary Protocol

**Model Context Protocol (MCP):**

- Relationship clarified: MCP handles tool/resource integration, A2A handles agent-to-agent coordination
- Protocols are complementary, not competing
- Agents may support both protocols for different use cases

---

## Impact on Developers

### Breaking Changes Requiring Code Updates

#### 1. Part Type Unification (CRITICAL IMPACT)

The most significant breaking change: TextPart, FilePart, and DataPart types have been removed and replaced with a single unified Part structure.

**Before (v0.3.0):**

```typescript
// Separate types with kind discriminator
if (part.kind === "text") {
  return part.text;
} else if (part.kind === "file") {
  if (part.file.fileWithUri) {
    return fetchFile(part.file.fileWithUri);
  } else {
    return part.file.fileWithBytes;
  }
} else if (part.kind === "data") {
  return part.data;
}
```

**After (v1.0):**

```typescript
// Unified Part with oneof content
if ("text" in part) {
  return part.text;
} else if ("url" in part) {
  return fetchFile(part.url);
} else if ("raw" in part) {
  return decodeBase64(part.raw);
} else if ("data" in part) {
  return part.data;
}
```

#### 2. Stream Event Discriminator Pattern (HIGH IMPACT)

Stream events changed from kind-based to wrapper-based discrimination:

**Before (v0.3.0):**

```typescript
if (event.kind === "taskStatusUpdate") {
  handleStatusUpdate(event);
} else if (event.kind === "taskArtifactUpdate") {
  handleArtifactUpdate(event);
}
```

**After (v1.0):**

```typescript
if ("taskStatusUpdate" in event) {
  handleStatusUpdate(event.taskStatusUpdate);
} else if ("taskArtifactUpdate" in event) {
  handleArtifactUpdate(event.taskArtifactUpdate);
}
```

#### 3. Agent Card Structure (HIGH IMPACT)

Agent discovery and capability checking requires updates:

**Before (v0.3.0):**

```typescript
const endpoint = agentCard.url;
const transport = agentCard.preferredTransport;
const supportsExtended = agentCard.supportsAuthenticatedExtendedCard;
```

**After (v1.0):**

```typescript
const primaryInterface = agentCard.supportedInterfaces[0];
const endpoint = primaryInterface.url;
const transport = primaryInterface.protocolBinding;
const supportsExtended = agentCard.capabilities.extendedAgentCard;
```

#### 4. Pagination (MEDIUM IMPACT)

List Tasks implementation must switch from page-based to cursor-based:

**Before (v0.3.0):**

```typescript
const response = await listTasks({ page: 1, perPage: 50 });
```

**After (v1.0):**

```typescript
let cursor = undefined;
do {
  const response = await listTasks({ cursor, limit: 50 });
  // process response.tasks
  cursor = response.nextCursor;
} while (cursor);
```

#### 5. Enum Value Changes (HIGH IMPACT)

All enum values now use SCREAMING_SNAKE_CASE with type prefixes:

**TaskState:**

```typescript
// v0.3.0
if (task.status.state === "completed") { ... }
if (task.status.state === "input-required") { ... }

// v1.0
if (task.status.state === "TASK_STATE_COMPLETED") { ... }
if (task.status.state === "TASK_STATE_INPUT_REQUIRED") { ... }
```

**MessageRole:**

```typescript
// v0.3.0
const message = { role: "user", parts: [...] };

// v1.0
const message = { role: "ROLE_USER", parts: [...] };
```

**Complete Mapping:**

- `"submitted"` → `"TASK_STATE_SUBMITTED"`
- `"working"` → `"TASK_STATE_WORKING"`
- `"completed"` → `"TASK_STATE_COMPLETED"`
- `"failed"` → `"TASK_STATE_FAILED"`
- `"canceled"` → `"TASK_STATE_CANCELED"`
- `"rejected"` → `"TASK_STATE_REJECTED"`
- `"input-required"` → `"TASK_STATE_INPUT_REQUIRED"`
- `"auth-required"` → `"TASK_STATE_AUTH_REQUIRED"`
- `"user"` → `"ROLE_USER"`
- `"agent"` → `"ROLE_AGENT"`

#### 6. Field Name Changes (LOW IMPACT)

- `file.mimeType` → `mediaType`
- Operation names (aliases provided during transition)

### New Capabilities to Leverage

#### 1. Execution Mode Control

```typescript
// Wait for task completion (Default)
const result = await sendMessage(message, { nonBlocking: false });

// Return immediately, poll later
const task = await sendMessage(message, { nonBlocking: true });
```

#### 2. Agent Card Signature Verification

```typescript
if (agentCard.signatures && agentCard.signatures.length > 0) {
  const verified = await verifyAgentCardSignature(agentCard);
  if (!verified) {
    throw new Error("Agent Card signature verification failed");
  }
}
```

#### 3. Extension Requirements

```typescript
const requiredExtensions = agentCard.extensions
  .filter(ext => ext.required)
  .map(ext => ext.uri);

// Check if client supports required extensions
if (!clientSupportsAll(requiredExtensions)) {
  throw new Error("Missing required extension support");
}
```

#### 4. Enhanced Timestamp Tracking

```typescript
const taskAge = Date.now() - new Date(task.createdAt).getTime();
const timeSinceUpdate = Date.now() - new Date(task.lastModified).getTime();
```

#### 5. Versioning Negotiation

```typescript
// Client sends A2A-Version header
headers["A2A-Version"] = "1.0";

// Server validates and rejects if unsupported
if (!supportedVersions.includes(requestedVersion)) {
  throw new VersionNotSupportedError();
}
```

### Migration Strategy Recommendations

#### Phase 1: Compatibility Layer

1. Add support for parsing both old and new discriminator patterns
2. Implement version detection based on protocol version
3. Support both Agent Card structures during transition

#### Phase 2: Dual Support

1. Update all APIs to emit v1.0 format
2. Maintain backward compatibility readers for v0.3.0
3. Add A2A-Version header handling
4. Implement cursor-based pagination alongside legacy page-based

#### Phase 3: v1.0 Only

1. Deprecate v0.3.0 compatibility code
2. Remove legacy discriminator parsing
3. Remove page-based pagination
4. Clean up dual-format support code

#### Backward Compatibility Strategy (#1401)

v1.0 introduces a formal approach to protocol versioning that enables SDK backward compatibility.

**Protocol Version Per Interface:**

- Each `AgentInterface` now specifies its own `protocolVersion` field
- Agents can support multiple protocol versions simultaneously by exposing multiple interfaces
- Clients negotiate version by selecting appropriate interface from Agent Card

**SDK Implementation Pattern:**

```typescript
// SDK can support multiple protocol versions
class A2AClient {
  async connect(agentCardUrl: string) {
    const card = await this.getAgentCard(agentCardUrl);

    // Find best matching interface
    const interface = card.supportedInterfaces.find(i =>
      this.supportedVersions.includes(i.protocolVersion)
    );

    if (!interface) {
      throw new Error("No compatible protocol version");
    }

    // Use version-specific adapter
    return this.createAdapter(interface.protocolVersion, interface);
  }
}
```

**Benefits:**

- SDKs can maintain support for multiple protocol versions
- Agents can gradually migrate by supporting both old and new versions
- Clients automatically select best compatible version
- Enables graceful deprecation of old protocol versions

### Testing Considerations

- Test with both v0.3.0 and v1.0 formatted data
- Validate Agent Card signature verification
- Test cursor-based pagination edge cases (empty results, single page, etc.)
- Verify proper handling of new error types
- Test extension requirement validation

### Recommended Priority

#### Critical (Do Immediately)

- Update Part and streaming event parsing (discriminator pattern)
- Update Agent Card parsing (structure changes)
- Add A2A-Version header to all requests

#### High (Within 1 Month)

- Implement cursor-based pagination
- Update enum value handling (state field)
- Add non_blocking parameter support

#### Medium (Within 3 Months)

- Implement Agent Card signature verification
- Add extension requirement checking
- Update timestamp handling to ISO 8601 format
- Implement new error types

#### Low (Nice to Have)

- Add createdAt/lastModified timestamp tracking
- Leverage enhanced metadata capabilities
- Implement mutual TLS authentication support

---

## Conclusion

A2A Protocol v1.0 represents a significant step forward in protocol maturity while maintaining the core architectural principles of v0.3.0. The changes focus on standardization, type safety, and enterprise readiness, requiring developers to update their implementations but providing clearer specifications and better developer experience in return.

The breaking changes, while requiring code updates, are straightforward to implement and improve code clarity. The new capabilities around versioning, signatures, and enhanced extensions provide a solid foundation for future protocol evolution within the v1.x line.

Developers should plan for a phased migration approach, prioritizing the critical breaking changes while gradually adopting new capabilities over time.
