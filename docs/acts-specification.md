# A2A Conformance Test Specification (ACTS)

**Version:** 0.1.0 (Draft)
**Status:** Proposal
**Target A2A Version:** 1.0

## 1. Introduction

### 1.1. Purpose

The A2A Conformance Test Specification (ACTS) defines a language-neutral, declarative format for specifying conformance tests for implementations of the [Agent2Agent (A2A) Protocol](https://a2a-protocol.org). An ACTS file describes **what** to test and **what to expect**, not **how** to execute the test. Any programming language or framework can implement a test runner that consumes ACTS files.

The goals of this format are:

- **Unify** fragmented conformance testing efforts across the A2A ecosystem.
- **Decouple** test definitions from test infrastructure so that SDK teams can write runners in their own language while testing against one canonical set of tests.
- **Ensure interoperability** by verifying that every conforming SDK produces and consumes wire-level messages that any other conforming SDK can understand.

### 1.2. Scope

ACTS covers **conformance testing** of a single A2A implementation — verifying that a server (or client) correctly implements the protocol as defined in the A2A specification.

ACTS does **not** cover:

- **Interoperability testing** (connecting SDK A's client to SDK B's server). However, ACTS is designed so that if two implementations each pass the full conformance suite, they will interoperate.
- **Performance or load testing.**
- **Application-level behavior** beyond what the protocol requires.

### 1.3. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

- **SUT** — System Under Test. The A2A server implementation being tested.
- **Runner** — A program that reads ACTS files, executes the described tests against a SUT, and reports results.
- **Test** — A single named scenario that verifies one or more protocol requirements.
- **Step** — An individual action within a test (e.g., send a message, check the response).
- **Suite** — A named grouping of related tests.

### 1.4. File Format

ACTS files are expressed in [YAML 1.2](https://yaml.org/spec/1.2.2/). Runners SHOULD also accept equivalent JSON input. All examples in this specification use YAML.

### 1.5. Notational Conventions

Data structures in this specification are defined using [CDDL (Concise Data Definition Language)](https://www.rfc-editor.org/rfc/rfc8610) as extended by [RFC 9165](https://www.rfc-editor.org/rfc/rfc9165). CDDL rules describe the logical structure; the serialization is YAML (or JSON).

In CDDL definitions:

- `text` corresponds to a YAML string.
- `int` corresponds to a YAML integer.
- `bool` corresponds to a YAML boolean.
- `any` corresponds to any YAML value.
- `? key` denotes an optional field.
- `* key` denotes zero or more entries.
- `+ key` denotes one or more entries.

---

## 2. Document Structure

An ACTS document is a YAML file whose root is a map conforming to the `acts-document` rule.

```cddl
acts-document = {
  acts_version: text,              ; Version of the ACTS format (e.g., "1.0")
  spec_version: text,              ; A2A spec version these tests target (e.g., "1.0")
  ? spec_ref: text,                ; URL to the A2A specification
  ? metadata: metadata,
  ? variables: { * text => text }, ; Default variables available to all tests
  ? include: [+ text],             ; List of ACTS files to include (for master files)
  ? suites: [+ suite]              ; At least one of include or suites MUST be present
}

metadata = {
  ? title: text,
  ? description: text,
  ? authors: [+ text],
  ? license: text
}
```

An ACTS document MUST contain at least one of `suites` or `include`. A master file MAY use only `include` to reference other ACTS files without defining its own suites.

### Example

```yaml
acts_version: "1.0"
spec_version: "1.0"
spec_ref: "https://github.com/a2aproject/A2A/blob/main/docs/specification.md"

metadata:
  title: "A2A v1.0 Official Conformance Tests"
  description: "Canonical test suite for A2A protocol v1.0 implementations"

variables:
  baseUrl: "{{env.A2A_BASE_URL}}"

suites:
  - id: discovery
    name: "Agent Card Discovery"
    tests: [...]
```

---

## 3. Suites and Tests

### 3.1. Suite

A suite is a named group of related tests.

```cddl
suite = {
  id: text,                        ; Unique identifier (kebab-case)
  name: text,                      ; Human-readable name
  ? description: text,
  ? tags: [+ text],                ; Tags inherited by all tests in the suite
  tests: [+ test]
}
```

### 3.2. Test

A test is a single conformance scenario. It declares which protocol requirements it verifies, its conformance level, and an ordered list of steps.

```cddl
test = {
  id: text,                        ; Unique requirement ID (e.g., "CORE-SEND-001")
  name: text,                      ; Human-readable name
  ? description: text,             ; What this test verifies and why
  ? spec_ref: text,                ; Section reference in the A2A spec
  level: conformance-level,
  ? tags: [+ text],
  ? transport: [+ transport-binding],  ; Omit to apply to all bindings
  ? preconditions: preconditions,
  ? requires_behaviors: [+ text],  ; SUT behavior prefixes this test depends on (see §11)
  ? origin: text,                  ; URL to issue/PR where this test originated
  steps: [+ step]
}

conformance-level = "must" / "should" / "may"

transport-binding = "jsonrpc" / "grpc" / "rest"
```

**Conformance levels** map to RFC 2119 keywords:

| Level | Meaning |
|-------|---------|
| `must` | Absolute requirement. Failure means the implementation is non-conformant. |
| `should` | Recommended behavior. Failure means the implementation is conformant but may have reduced interoperability. |
| `may` | Optional behavior. Passing provides additional interoperability. |

### 3.3. Preconditions

Preconditions describe what the SUT must advertise or support for the test to be applicable. If preconditions are not met, the runner MUST mark the test as **skipped**, not failed.

```cddl
preconditions = {
  ? capabilities: { * text => any },   ; Required AgentCard capability fields
  ? skills: [+ { id: text }],          ; Required skill IDs in the AgentCard
  ? transport: [+ transport-binding],   ; Required transport binding
  ? extensions: [+ text],              ; Required extension URIs
  ? description: text                  ; Human-readable precondition summary
}
```

### Example

```yaml
- id: STREAM-ORDER-001
  name: "Streaming events never regress state"
  description: >
    When an agent streams status updates, the task state MUST
    follow the state machine and never move backward
    (e.g., COMPLETED must not be followed by WORKING).
  spec_ref: "specification.md#section-3.5.2"
  level: must
  tags: [streaming, ordering]
  preconditions:
    capabilities:
      streaming: true
  steps: [...]
```

---

## 4. Steps

Steps are the building blocks of a test. They execute sequentially within a test. Each step performs one action and optionally asserts expectations on the result.

**Test isolation:** Tests within a suite (or across suites) MUST NOT share state. Each test starts with a clean context — no tasks, captures, or side effects carry over from previous tests. Runners MAY execute tests in any order or in parallel.

```cddl
step = server-step / client-step / assertion-step / raw-step

server-step = {
  id: text,                         ; Unique within the test
  ? description: text,
  action: abstract-operation,       ; Abstract A2A operation name
  request: request-params,          ; Parameters for the operation
  ? expect: expect-block,           ; Expected response assertions
  ? expect_error: expect-error,     ; Expected error (mutually exclusive with expect)
  ? expect_stream: expect-stream,   ; Streaming assertions (for streaming operations)
  ? capture: { + text => text },    ; Variable capture: varName => response.path
  ? repeat: repeat-config,          ; Polling/retry configuration
  ? delay_ms: int                   ; Delay before executing this step
}

client-step = {
  id: text,
  ? description: text,
  type: "client_test",
  golden_response: golden-response, ; A canonical wire response for the client to parse
  expect_parsed: { * text => assertion } ; Assertions on the parsed result
}

assertion-step = {
  id: text,
  ? description: text,
  assertion: inline-assertion       ; Assert against a prior step's response
}
```

### 4.1. Abstract Operations

Tests reference abstract A2A operations rather than wire-level method names. The runner maps each abstract operation to the appropriate wire format for the transport binding under test.

```cddl
abstract-operation =
  "send_message" /
  "send_streaming_message" /
  "get_task" /
  "list_tasks" /
  "cancel_task" /
  "subscribe_to_task" /
  "get_agent_card" /
  "get_extended_agent_card" /
  "create_push_config" /
  "get_push_config" /
  "list_push_configs" /
  "delete_push_config"
```

The runner MUST translate each abstract operation to the correct wire representation:

| Abstract Operation | JSON-RPC Method | gRPC RPC | REST |
|---|---|---|---|
| `send_message` | `SendMessage` | `SendMessage` | `POST /message:send` |
| `send_streaming_message` | `SendStreamingMessage` | `SendStreamingMessage` | `POST /message:stream` |
| `get_task` | `GetTask` | `GetTask` | `GET /tasks/{id}` |
| `list_tasks` | `ListTasks` | `ListTasks` | `GET /tasks` |
| `cancel_task` | `CancelTask` | `CancelTask` | `POST /tasks/{id}:cancel` |
| `subscribe_to_task` | `SubscribeToTask` | `SubscribeToTask` | `GET /tasks/{id}:subscribe` |
| `get_agent_card` | *(HTTP GET)* | *(HTTP GET)* | `GET /.well-known/agent-card.json` |
| `create_push_config` | `CreatePushNotificationConfig` | `CreatePushNotificationConfig` | `POST /tasks/{id}/pushNotifications` |
| `get_push_config` | `GetPushNotificationConfig` | `GetPushNotificationConfig` | `GET /tasks/{id}/pushNotifications/{configId}` |
| `list_push_configs` | `ListPushNotificationConfigs` | `ListPushNotificationConfigs` | `GET /tasks/{id}/pushNotifications` |
| `delete_push_config` | `DeletePushNotificationConfig` | `DeletePushNotificationConfig` | `DELETE /tasks/{id}/pushNotifications/{configId}` |

### 4.2. Assertion Root

Different A2A operations return different response shapes. The **assertion root** — the object against which `expect`, `capture`, and `repeat.until` paths are resolved — depends on the operation:

| Operation | Response Type | Assertion Root |
|---|---|---|
| `send_message` | `SendMessageResponse` | The `SendMessageResponse` object (contains `task` or `message`) |
| `send_streaming_message` | Stream of `StreamResponse` | Per-event (see §7) |
| `get_task` | `Task` | The `Task` object directly |
| `list_tasks` | `ListTasksResponse` | The `ListTasksResponse` object (contains `tasks` array) |
| `cancel_task` | `Task` | The `Task` object directly |
| `subscribe_to_task` | Stream of `StreamResponse` | Per-event (see §7) |
| `get_agent_card` | `AgentCard` | The `AgentCard` object directly |
| `get_extended_agent_card` | `AgentCard` | The `AgentCard` object directly |
| `create_push_config` | `PushNotificationConfig` | The `PushNotificationConfig` object directly |
| `get_push_config` | `PushNotificationConfig` | The `PushNotificationConfig` object directly |
| `list_push_configs` | `ListPushNotificationConfigsResponse` | The response object (contains `configs` array) |
| `delete_push_config` | *(empty)* | N/A |

For operations that return a wrapper (like `SendMessageResponse`), assertions reference fields within the wrapper. For operations that return a domain object directly (like `get_task` → `Task`), assertions reference fields on that object.

**Example — the difference matters:**

```yaml
# send_message returns SendMessageResponse → root includes task/message discriminator
- id: send
  action: send_message
  expect:
    task:                           # SendMessageResponse.task
      id: {type: string}
      status:
        state: TASK_STATE_COMPLETED
  capture:
    taskId: task.id                 # path from SendMessageResponse root

# get_task returns Task directly → root IS the Task
- id: get
  action: get_task
  request:
    id: "{{send.taskId}}"
  expect:
    id: "{{send.taskId}}"           # Task.id — no "task." prefix needed
    status:
      state: TASK_STATE_COMPLETED
```

The runner MUST unwrap transport-level framing (JSON-RPC envelope, gRPC message wrapper, HTTP response) before applying assertions. The assertion root is always the **A2A domain object**, not the transport wrapper.

### 4.3. Request Parameters

Request parameters use the abstract A2A data model — not the wire format. The runner handles serialization.

If the request includes a `message` and no `messageId` is specified, the runner MUST auto-generate a unique `messageId` (e.g., a UUID) for the message. The A2A specification requires every message to have a `messageId`.

```cddl
request-params = {
  ; For send_message / send_streaming_message:
  ? message: {
      role: text,                   ; e.g., "ROLE_USER"
      parts: [+ part],
      ? messageId: text,
      ? taskId: text,
      ? contextId: text,
      * text => any                 ; Additional fields
    },
  ? configuration: {
      ? returnImmediately: bool,
      ? historyLength: int,
      * text => any
    },

  ; For get_task / cancel_task / subscribe_to_task:
  ? id: text,                       ; Task ID
  ? historyLength: int,

  ; For list_tasks:
  ? contextId: text,
  ? cursor: text,
  ? pageSize: int,

  ; For push config operations:
  ? taskId: text,
  ? pushNotificationConfig: any,

  ; Catch-all for future fields:
  * text => any
}

part = {
  ? text: text,
  ? data: any,
  ? file: {
      ? url: text,
      ? raw: text,                  ; base64-encoded bytes
      ? mediaType: text,
      ? name: text
    },
  * text => any
}
```

### 4.4. Raw Wire Steps

For transport-specific tests that must assert exact wire-level behavior, steps MAY use `raw_request` and `raw_expect` instead of `action`/`request`/`expect`:

```cddl
raw-step = {
  id: text,
  ? description: text,
  raw_request: {
    method: "GET" / "POST" / "PUT" / "DELETE",
    path: text,
    ? headers: { * text => text },
    ? body: any,                    ; Exact body to send
    ? rawBody: text                 ; Raw string body (for malformed JSON tests)
  },
  ? raw_expect: {
    ? status: int,                  ; HTTP status code
    ? headers: { * text => assertion },
    ? body: { * text => assertion }
  },
  ? capture: { + text => text }
}
```

Raw steps are used when the test must verify wire-level details that the abstract operation layer intentionally hides (e.g., HTTP status codes, header values, malformed input handling).

> **Note:** Raw steps are inherently transport-specific. A test containing only raw steps MUST specify a `transport` filter.

---

## 5. Assertions

Assertions are the core of the format. They describe expected values using a compact DSL that can express exact matches, type checks, existence checks, and more.

### 5.1. Assertion Grammar

```cddl
assertion =
  exact-match /                     ; Bare value: exact equality
  assertion-object                  ; Map with assertion operators

exact-match = text / int / float / bool / null

assertion-object = {
  ; Type checking
  ? type: "string" / "number" / "boolean" / "array" / "object" / "null",

  ; Existence
  ? exists: true,                   ; Field is present (any value)
  ? absent: true,                   ; Field is NOT present

  ; String matching
  ? contains: text,                 ; Substring match
  ? matches: text,                  ; Regular expression match (ECMA-262)
  ? starts_with: text,
  ? ends_with: text,

  ; Numeric comparison
  ? gte: number,                    ; Greater than or equal
  ? lte: number,                    ; Less than or equal
  ? gt: number,                     ; Greater than
  ? lt: number,                     ; Less than

  ; Array length
  ? count: int,                     ; Exact array length
  ? count_gte: int,                 ; Length >= N
  ? count_lte: int,                 ; Length <= N

  ; Enum / alternatives
  ? one_of: [+ any],               ; Value is one of these

  ; Combinators
  ? all_of: [+ assertion],         ; All assertions must pass
  ? any_of: [+ assertion],         ; At least one assertion must pass
  ? not: assertion                  ; Assertion must NOT pass
}

number = int / float
```

### 5.2. Assertion Paths and Nesting

Assertions in `expect` blocks use **YAML nesting** to mirror the structure of the response object. Each level of nesting corresponds to a level of object nesting in the response.

```yaml
expect:
  task:
    status:
      state: TASK_STATE_COMPLETED    # Asserts response.task.status.state
    artifacts:
      - parts:
          - text: {type: string}     # Asserts response.task.artifacts[0].parts[0].text
```

**Dot-path notation** (e.g., `artifacts[0].parts[0].text`) MUST NOT be used as YAML keys in `expect` blocks. YAML would parse `artifacts[0].parts[0].text` as a literal string key, not a path expression. Runners MUST interpret `expect` blocks as nested YAML maps that mirror the response structure.

The one exception is **`capture` paths** and **`repeat.until` expressions**, which use dot-path strings as *values* (not keys):

```yaml
capture:
  taskId: task.id                   # dot-path as a VALUE — this is correct
```

For **array access** in assertions, use YAML array syntax:

```yaml
expect:
  artifacts:
    - parts:                         # First artifact's parts
        - text: {type: string}       # First part is a text part
```

For assertions that must apply to **any element** in an array (rather than a specific index), use `assertion-step` with collection assertions (see §5.5).

When a path appears in a `capture` value, `repeat.until` expression, or `collection-match.path`, it uses dot-path notation with bracket indexing:

```
task.id                             ; Nested field
task.artifacts[0].parts[0].text     ; Array indexing
task.artifacts[*].parts[*]          ; Wildcard (collection assertions only)
```

### 5.3. Exact Match

A bare scalar value asserts exact equality:

```yaml
expect:
  task:
    status:
      state: TASK_STATE_COMPLETED     # exact string match
```

### 5.4. Operator Assertions

An assertion map applies one or more operators:

```yaml
expect:
  task:
    id: {type: string}                       # type check
    status:
      state: {one_of: [TASK_STATE_SUBMITTED, TASK_STATE_WORKING]}
    artifacts: {type: array, count_gte: 1}   # combined operators
```

When multiple operators appear in one assertion map, they are combined with AND semantics — all operators must pass.

### 5.5. Collection Assertions

For asserting properties across array elements:

```cddl
inline-assertion = {
  source: text,                     ; Reference to a prior step's response
  ? any: collection-match,          ; At least one element matches
  ? all: collection-match,          ; Every element matches
  ? none: collection-match          ; No element matches
}

collection-match = {
  path: text,                       ; Dot-path with wildcards (e.g., "result.task.artifacts[*].parts[*]")
  match: { * text => assertion }    ; Assertions each matching element must satisfy
}
```

### Example

```yaml
- id: verify-text-artifact
  assertion:
    source: "{{send.response}}"
    any:
      path: result.task.artifacts[*].parts[*]
      match:
        text: {type: string}
```

---

## 6. Expect Blocks

### 6.1. Standard Expect

For non-streaming operations, `expect` describes the expected response.

```cddl
expect-block = {
  ? result_type: "task" / "message",  ; Which oneof field must be present
  ? task: { * text => assertion },    ; Assertions on the task (if result_type is "task")
  ? message: { * text => assertion }, ; Assertions on the message (if result_type is "message")
  * text => assertion                 ; Dot-path assertions on the full response
}
```

When `result_type` is specified, the runner MUST verify that the response contains the corresponding field and does NOT contain the alternative. For example, `result_type: task` means the response must contain a `task` field and must not contain a `message` field at the result level.

### 6.2. Error Expect

For operations expected to fail, `expect_error` describes the expected error.

```cddl
expect-error = {
  error_type: a2a-error-type,        ; Abstract A2A error name
  ? message: assertion,              ; Assertion on the error message string
  ? details: { * text => assertion } ; Assertions on error details/metadata
}

a2a-error-type =
  "TaskNotFoundError" /
  "TaskNotCancelableError" /
  "UnsupportedOperationError" /
  "ContentTypeNotSupportedError" /
  "InvalidParamsError" /
  "VersionNotSupportedError" /
  "PushNotificationNotSupportedError" /
  "StreamingNotSupportedError" /
  "ExtensionSupportRequiredError" /
  "ExtendedCardNotSupportedError" /
  "JSONParseError" /
  "MethodNotFoundError" /
  "InternalError"
```

The runner MUST map each abstract error type to the transport-specific representation:

| Abstract Error | JSON-RPC Code | gRPC Status | REST HTTP Status |
|---|---|---|---|
| `TaskNotFoundError` | -32001 | `NOT_FOUND` | 404 |
| `TaskNotCancelableError` | -32002 | `FAILED_PRECONDITION` | 409 |
| `UnsupportedOperationError` | -32004 | `UNIMPLEMENTED` | 405 |
| `ContentTypeNotSupportedError` | -32005 | `INVALID_ARGUMENT` | 415 |
| `InvalidParamsError` | -32602 | `INVALID_ARGUMENT` | 400 |
| `VersionNotSupportedError` | -32006 | `UNIMPLEMENTED` | 406 |
| `PushNotificationNotSupportedError` | -32003 | `UNIMPLEMENTED` | 501 |
| `StreamingNotSupportedError` | -32007 | `UNIMPLEMENTED` | 501 |
| `JSONParseError` | -32700 | `INVALID_ARGUMENT` | 400 |
| `MethodNotFoundError` | -32601 | `UNIMPLEMENTED` | 501 |
| `InternalError` | -32603 | `INTERNAL` | 500 |

> **Note:** This mapping table is derived from the A2A specification. Runners MUST consult the normative A2A specification for authoritative error code mappings. If this table conflicts with the A2A specification, the A2A specification takes precedence.

### Example

```yaml
- id: CORE-ERR-001
  name: "TaskNotFoundError on missing task"
  level: must
  steps:
    - id: get-missing
      action: get_task
      request:
        id: "00000000-0000-0000-0000-000000000000"
      expect_error:
        error_type: TaskNotFoundError
        message: {type: string}
```

---

## 7. Streaming Assertions

Streaming operations (`send_streaming_message`, `subscribe_to_task`) return an ordered sequence of events rather than a single response. The `expect_stream` block provides assertions for this.

```cddl
expect-stream = {
  ? min_count: int,                 ; Minimum number of events
  ? max_count: int,                 ; Maximum number of events
  ? timeout_ms: int,                ; Maximum time to wait for stream completion
  ? ordering: ordering-rule,        ; Ordering constraint on task states

  ; Event-level assertions
  ? events: [+ event-assertion],

  ; Final event assertion
  ? final_event: { * text => assertion },

  ; All-events assertion (applied to every event)
  ? each_event: { * text => assertion }
}

ordering-rule = "monotonic_state"   ; Task states never regress

event-assertion = {
  ? description: text,
  ? match: "exact_position" / "any_position",  ; Default: exact_position
  ? index: int,                     ; Specific event index (0-based)

  ; Exactly one of these StreamResponse payload types:
  ? status_update: { * text => assertion },
  ? artifact_update: { * text => assertion },
  ? task: { * text => assertion },
  ? message: { * text => assertion },

  ; Or a generic assertion on the event:
  * text => assertion
}
```

### 7.1. Ordering Rules

When `ordering: monotonic_state` is specified, the runner MUST verify that task state transitions in the event stream follow the A2A state machine and never regress illegally.

The A2A task states are:

- **Non-terminal:** `TASK_STATE_SUBMITTED`, `TASK_STATE_WORKING`, `TASK_STATE_INPUT_REQUIRED`, `TASK_STATE_AUTH_REQUIRED`
- **Terminal:** `TASK_STATE_COMPLETED`, `TASK_STATE_FAILED`, `TASK_STATE_CANCELED`, `TASK_STATE_REJECTED`

The valid transitions are:

```
SUBMITTED → WORKING
WORKING → COMPLETED | FAILED | CANCELED | REJECTED | INPUT_REQUIRED | AUTH_REQUIRED
INPUT_REQUIRED → WORKING           (client sent more input)
AUTH_REQUIRED → WORKING             (authorization was provided)
```

A state MAY repeat (e.g., multiple WORKING events). The following transitions are **illegal** and MUST cause a test failure:

- Any state → SUBMITTED (SUBMITTED is only the initial state)
- Any terminal state → any state (terminal states are final)

Note that `INPUT_REQUIRED → WORKING` and `AUTH_REQUIRED → WORKING` are valid (the interrupted condition was resolved). The `monotonic_state` rule enforces "no regression from terminal states" and "no illegal transitions," not a simple linear progression.

### Example

```yaml
- id: CORE-STREAM-001
  name: "Basic streaming lifecycle"
  level: must
  preconditions:
    capabilities:
      streaming: true
  steps:
    - id: stream
      action: send_streaming_message
      request:
        message:
          role: ROLE_USER
          parts:
            - text: "generate streaming output"
      expect_stream:
        min_count: 2
        ordering: monotonic_state
        events:
          - description: "A status update to WORKING"
            match: any_position
            status_update:
              status:
                state: TASK_STATE_WORKING
          - description: "At least one artifact update"
            match: any_position
            artifact_update:
              artifact:
                parts: {count_gte: 1}
        final_event:
          one_of:
            - task:
                status:
                  state: TASK_STATE_COMPLETED
            - status_update:
                final: true
                status:
                  state: TASK_STATE_COMPLETED
```

---

## 8. Variables and Capture

### 8.1. Variables

ACTS supports variable interpolation using double-brace syntax: `{{expression}}`.

```cddl
; Variable reference syntax (within text values):
;   {{variableName}}       — top-level variable
;   {{stepId.varName}}     — captured variable from a prior step
;   {{env.ENV_VAR_NAME}}   — environment variable
;   {{$uuid}}              — generate a fresh UUID (each occurrence produces a new value)
```

Variables defined in the document-level `variables` map are available to all tests. Variables captured in a step (via `capture`) are scoped to that test and available in subsequent steps.

### 8.2. Capture

A `capture` block extracts values from a response for use in later steps.

```cddl
; In a step:
capture = { + text => text }
; Key:   variable name to assign
; Value: dot-path into the response
```

### Example

```yaml
steps:
  - id: create
    action: send_message
    request:
      message:
        role: ROLE_USER
        parts:
          - text: "start a task"
    capture:
      taskId: task.id
      contextId: task.contextId

  - id: retrieve
    action: get_task
    request:
      id: "{{create.taskId}}"
    expect:
      id: "{{create.taskId}}"
      status:
        state: TASK_STATE_COMPLETED
```

When the runner resolves `{{create.taskId}}`, it substitutes the value captured from the `create` step's response at the path `task.id`.

---

## 9. Polling and Retry

Some A2A patterns involve polling (e.g., `returnImmediately: true` followed by `GetTask` until completion). The `repeat` block on a step instructs the runner to re-execute the step until a condition is met.

```cddl
repeat-config = {
  until: text,                      ; Condition expression (see below)
  ? max_attempts: int,              ; Maximum retry attempts (default: 10)
  ? delay_ms: int,                  ; Delay between attempts in milliseconds (default: 1000)
  ? backoff: "none" / "linear" / "exponential"  ; Backoff strategy (default: "none")
}
```

### 9.1. Until Expressions

The `until` field contains a condition expression. The following forms are supported:

```
path == value                       ; Equality
path != value                       ; Inequality
path in [value1, value2, ...]       ; Value is one of the listed values
```

Where `path` is a dot-path into the step's response, `value` is a literal to compare against, and `[value1, value2, ...]` is a list of acceptable values. The runner re-executes the step until the expression evaluates to true or `max_attempts` is exhausted.

If `max_attempts` is exhausted without the condition becoming true, the step MUST be marked as failed.

### Example

```yaml
- id: poll
  action: get_task
  request:
    id: "{{start.taskId}}"
  expect:
    status:
      state: {type: string}
  repeat:
    until: status.state in [TASK_STATE_COMPLETED, TASK_STATE_FAILED]
    max_attempts: 15
    delay_ms: 2000
    backoff: linear
```

---

## 10. Client Tests (Golden Responses)

Most ACTS tests verify server behavior: send a request, check the response. Client tests invert this: they provide a canonical wire response and assert that the client (SDK) parses it correctly.

```cddl
client-step = {
  id: text,
  ? description: text,
  type: "client_test",
  golden_response: {
    ? status: int,                  ; HTTP status code
    ? headers: { * text => text },
    body: any                       ; The exact response body
  },
  expect_parsed: { * text => assertion }
}
```

Client tests are valuable for catching interop bugs: they ensure that every SDK can parse responses produced by any other conformant SDK. The golden responses in the official test suite represent the canonical wire format.

### Example

```yaml
- id: CLIENT-PARSE-001
  name: "Client parses a canonical SendMessage task response"
  level: must
  steps:
    - id: parse
      type: client_test
      golden_response:
        status: 200
        headers:
          Content-Type: application/json
        body:
          jsonrpc: "2.0"
          id: "1"
          result:
            task:
              id: "abc-123"
              contextId: "ctx-456"
              status:
                state: TASK_STATE_COMPLETED
                timestamp: "2026-01-01T00:00:00Z"
              artifacts:
                - artifactId: "art-1"
                  parts:
                    - text: "hello world"
      expect_parsed:
        task:
          id: "abc-123"
          status:
            state: TASK_STATE_COMPLETED
          artifacts:
            - parts:
                - text: "hello world"
```

---

## 11. SUT Behavior Contract

ACTS tests are declarative: they describe what to send and what to expect. But to produce deterministic, verifiable responses, the SUT must exhibit specific behaviors in response to specific inputs.

ACTS uses a **message-prefix convention**: the text content of the first message part signals to the SUT what behavior to exhibit. This eliminates the need for a side-channel API to control the SUT.

### 11.1. Behavior Definition

```cddl
sut-behaviors = {
  acts_version: text,
  behaviors: [+ behavior]
}

behavior = {
  prefix: text,                     ; Message text prefix that triggers this behavior
  description: text,                ; What the SUT should do
  ? response_type: "task" / "message",
  ? terminal_state: text,           ; Expected terminal TaskState
  ? artifacts: [+ artifact-spec],   ; Artifacts to include in the response
  ? delay_ms: int,                  ; Simulated processing delay
  ? streaming: bool                 ; Whether this applies to streaming requests
}

artifact-spec = {
  ? text: text,
  ? data: any,
  ? file: { name: text, mediaType: text },
  ? fileUrl: { url: text, name: text, mediaType: text }
}
```

### 11.2. Standard Prefixes

The following prefixes form the standard SUT behavior contract. Any SUT that implements these behaviors can be tested with the official ACTS test suite.

| Prefix | Behavior |
|--------|----------|
| `tck-complete-task` | Complete the task with a text response message. |
| `tck-input-required` | Return task in `TASK_STATE_INPUT_REQUIRED` state. |
| `tck-reject-task` | Reject the task with an error. |
| `tck-message-response` | Return a `Message` (not a `Task`). |
| `tck-artifact-text` | Complete with a text artifact. |
| `tck-artifact-file` | Complete with a file artifact (inline bytes). |
| `tck-artifact-file-url` | Complete with a file URL artifact. |
| `tck-artifact-data` | Complete with a structured data artifact. |
| `tck-long-running` | Simulate long-running work (delayed completion). |
| `tck-multi-turn` | Require multiple turns (INPUT_REQUIRED → done). |
| `tck-cancel` | Accept and remain in WORKING state until canceled. |
| `tck-stream-basic` | Stream: status(working) → artifact → status(completed). |
| `tck-stream-chunked` | Stream: chunked artifact across multiple events. |
| `tck-task-failure` | Complete with `TASK_STATE_FAILED` and error message. |

### Example SUT Behaviors File

```yaml
acts_version: "1.0"
behaviors:
  - prefix: "tck-complete-task"
    description: "Complete the task with a text response"
    response_type: task
    terminal_state: TASK_STATE_COMPLETED

  - prefix: "tck-message-response"
    description: "Return a direct Message, not a Task"
    response_type: message

  - prefix: "tck-artifact-text"
    description: "Complete with a text artifact"
    response_type: task
    terminal_state: TASK_STATE_COMPLETED
    artifacts:
      - text: "Generated text content"

  - prefix: "tck-long-running"
    description: "Simulate long-running processing"
    response_type: task
    terminal_state: TASK_STATE_COMPLETED
    delay_ms: 5000

  - prefix: "tck-stream-basic"
    description: "Stream status updates and an artifact"
    response_type: task
    terminal_state: TASK_STATE_COMPLETED
    streaming: true
    artifacts:
      - text: "Streamed content"
```

---

## 12. Runner Requirements

This section defines requirements for ACTS-compliant test runners.

### 12.1. Input

A runner MUST accept one or more ACTS YAML files (or equivalent JSON). A runner MUST validate input against the ACTS structure defined in this specification before executing tests.

### 12.2. Variable Resolution

A runner MUST resolve variables in the following order of precedence (highest first):

1. Step-level captured variables (`{{stepId.varName}}`)
2. Document-level `variables` map
3. Environment variables (`{{env.VAR_NAME}}`)
4. Built-in generators (`{{$uuid}}`)

If a variable cannot be resolved, the runner MUST fail the step with a clear error message.

### 12.3. Transport Mapping

A runner MUST support at least one transport binding. When a test specifies `transport`, the runner MUST skip the test if it does not support any of the listed bindings. When `transport` is omitted, the runner MUST execute the test against whichever binding(s) it supports.

### 12.4. Protocol Compliance

When executing abstract operations, the runner MUST produce protocol-compliant requests:

- **A2A-Version header:** The runner MUST include the `A2A-Version` header (or gRPC metadata equivalent) on all requests, set to the `spec_version` from the ACTS document, unless the test is specifically testing version negotiation behavior (e.g., VER-* tests that deliberately omit or alter the header).
- **messageId generation:** If a request includes a `message` and no `messageId` is specified in the test, the runner MUST auto-generate a unique `messageId` (e.g., a UUID). The A2A specification requires every message to have a `messageId`.
- **JSON-RPC envelope:** For JSON-RPC transport, the runner MUST wrap the request parameters in a valid JSON-RPC 2.0 request object (with `jsonrpc`, `method`, and `id` fields) and unwrap the JSON-RPC envelope from responses before applying assertions.
- **Base URL:** The runner MUST be configurable with the SUT's base URL. The document-level `baseUrl` variable is available for raw wire steps that construct URLs manually, but abstract operations derive the URL from the runner's configuration and the operation's standard path.

### 12.5. Precondition Evaluation

Before executing a test, the runner MUST evaluate its `preconditions`. If the SUT does not meet the preconditions (e.g., its agent card does not advertise the required capabilities), the runner MUST mark the test as **skipped**.

### 12.6. Reporting

A runner SHOULD produce a structured report containing, for each test:

- Test ID and name
- Conformance level
- Result: `pass`, `fail`, `skip`, or `error`
- For failures: which step failed, which assertion failed, expected vs. actual values
- Execution time

The report format is not prescribed by this specification. Runners MAY produce JSON, JUnit XML, HTML, or any other format.

### 12.7. Conformance Summary

A runner SHOULD produce a conformance summary categorized by level:

```
MUST:   45/47 passed (2 skipped)
SHOULD: 12/15 passed (1 failed, 2 skipped)
MAY:     8/10 passed (2 skipped)
```

An implementation is considered **A2A conformant** if and only if all `must`-level tests pass (excluding skipped tests whose preconditions were not met).

---

## 13. Requirement ID Scheme

Every test MUST have a unique `id` that serves as its requirement identifier. IDs follow the pattern:

```
CATEGORY-AREA-NNN
```

Where:

| Prefix | Category |
|--------|----------|
| `CORE` | Core operations (SendMessage, GetTask, CancelTask, ListTasks) |
| `STREAM` | Streaming (SendStreamingMessage, SubscribeToTask, event ordering) |
| `PUSH` | Push notifications (config CRUD, webhook delivery) |
| `CARD` | Agent Card discovery and structure |
| `DM` | Data model and serialization (field naming, enums, timestamps) |
| `JSONRPC` | JSON-RPC binding-specific behavior |
| `GRPC` | gRPC binding-specific behavior |
| `REST` | HTTP+JSON/REST binding-specific behavior |
| `VER` | Version negotiation |
| `INTEROP` | Tests derived from cross-SDK interop bugs |
| `CLIENT` | Client-side parsing tests (golden responses) |

The `AREA` component provides finer grouping within a category (e.g., `SEND`, `GET`, `CANCEL`, `ERR`, `HIST`, `SSE`, `FMT`).

---

## 14. Complete Example

The following is a complete, minimal ACTS file demonstrating the key features.

```yaml
acts_version: "1.0"
spec_version: "1.0"

metadata:
  title: "A2A v1.0 Core Conformance Tests (Excerpt)"

variables:
  baseUrl: "{{env.A2A_BASE_URL}}"

suites:
  - id: core-operations
    name: "Core Operations"
    tests:

      # ── SendMessage: completed task ─────────────────────────────
      - id: CORE-SEND-001
        name: "SendMessage returns a completed task"
        description: >
          Send a message to the agent. The response MUST contain a Task
          in TASK_STATE_COMPLETED state.
        spec_ref: "specification.md#3.1.1"
        level: must
        tags: [send-message, task]
        requires_behaviors: [tck-complete-task]
        steps:
          - id: send
            action: send_message
            request:
              message:
                role: ROLE_USER
                parts:
                  - text: "tck-complete-task hello"
            expect:
              result_type: task
              task:
                id: {type: string}
                status:
                  state: TASK_STATE_COMPLETED
            capture:
              taskId: task.id
              contextId: task.contextId

          - id: get
            action: get_task
            request:
              id: "{{send.taskId}}"
            expect:
              id: "{{send.taskId}}"
              status:
                state: TASK_STATE_COMPLETED

      # ── SendMessage: message-only response ──────────────────────
      - id: CORE-SEND-003
        name: "SendMessage returns a Message (not a Task)"
        description: >
          When the agent handles a request without creating a task,
          it MUST return a Message with role ROLE_AGENT.
        spec_ref: "specification.md#3.1.1"
        level: must
        tags: [send-message, message-only]
        requires_behaviors: [tck-message-response]
        steps:
          - id: send
            action: send_message
            request:
              message:
                role: ROLE_USER
                parts:
                  - text: "tck-message-response hello"
            expect:
              result_type: message
              message:
                role: ROLE_AGENT
                parts: {count_gte: 1}

      # ── CancelTask ─────────────────────────────────────────────
      - id: CORE-CANCEL-001
        name: "CancelTask cancels a working task"
        spec_ref: "specification.md#3.1.5"
        level: must
        tags: [cancel, task]
        requires_behaviors: [tck-cancel]
        steps:
          - id: start
            action: send_message
            request:
              message:
                role: ROLE_USER
                parts:
                  - text: "tck-cancel start work"
              configuration:
                returnImmediately: true
            expect:
              result_type: task
              task:
                status:
                  state: {one_of: [TASK_STATE_SUBMITTED, TASK_STATE_WORKING]}
            capture:
              taskId: task.id

          - id: cancel
            action: cancel_task
            request:
              id: "{{start.taskId}}"
            expect:
              id: "{{start.taskId}}"
              status:
                state: TASK_STATE_CANCELED

      # ── Error: TaskNotFound ─────────────────────────────────────
      - id: CORE-ERR-001
        name: "GetTask with non-existent ID returns TaskNotFoundError"
        spec_ref: "specification.md#4.2"
        level: must
        tags: [error, task-not-found]
        steps:
          - id: get-missing
            action: get_task
            request:
              id: "00000000-0000-0000-0000-000000000000"
            expect_error:
              error_type: TaskNotFoundError
              message: {type: string}

      # ── Streaming ───────────────────────────────────────────────
      - id: CORE-STREAM-001
        name: "Basic streaming lifecycle"
        spec_ref: "specification.md#3.1.2"
        level: must
        tags: [streaming]
        requires_behaviors: [tck-stream-basic]
        preconditions:
          capabilities:
            streaming: true
        steps:
          - id: stream
            action: send_streaming_message
            request:
              message:
                role: ROLE_USER
                parts:
                  - text: "tck-stream-basic hello"
            expect_stream:
              min_count: 2
              ordering: monotonic_state
              final_event:
                task:
                  status:
                    state: TASK_STATE_COMPLETED

      # ── Multi-turn ──────────────────────────────────────────────
      - id: CORE-MULTI-001
        name: "Multi-turn conversation with INPUT_REQUIRED"
        spec_ref: "specification.md#3.1.1"
        level: must
        tags: [multi-turn, input-required]
        requires_behaviors: [tck-multi-turn]
        steps:
          - id: turn1
            action: send_message
            request:
              message:
                role: ROLE_USER
                parts:
                  - text: "tck-multi-turn start"
            expect:
              result_type: task
              task:
                status:
                  state: TASK_STATE_INPUT_REQUIRED
            capture:
              taskId: task.id
              contextId: task.contextId

          - id: turn2
            action: send_message
            request:
              message:
                role: ROLE_USER
                taskId: "{{turn1.taskId}}"
                contextId: "{{turn1.contextId}}"
                parts:
                  - text: "done"
            expect:
              result_type: task
              task:
                id: "{{turn1.taskId}}"
                status:
                  state: TASK_STATE_COMPLETED

      # ── Polling ─────────────────────────────────────────────────
      - id: CORE-EXEC-001
        name: "Long-running task with polling"
        spec_ref: "specification.md#3.1.1"
        level: must
        tags: [long-running, polling]
        requires_behaviors: [tck-long-running]
        steps:
          - id: start
            action: send_message
            request:
              message:
                role: ROLE_USER
                parts:
                  - text: "tck-long-running start"
              configuration:
                returnImmediately: true
            expect:
              result_type: task
              task:
                status:
                  state: {one_of: [TASK_STATE_SUBMITTED, TASK_STATE_WORKING]}
            capture:
              taskId: task.id

          - id: poll
            action: get_task
            request:
              id: "{{start.taskId}}"
            expect:
              status:
                state: {type: string}
            repeat:
              until: status.state in [TASK_STATE_COMPLETED, TASK_STATE_FAILED]
              max_attempts: 15
              delay_ms: 2000

  - id: discovery
    name: "Agent Card Discovery"
    tests:

      - id: CARD-DISC-001
        name: "Agent card is retrievable"
        spec_ref: "specification.md#5"
        level: must
        tags: [discovery, agent-card]
        steps:
          - id: get-card
            action: get_agent_card
            request: {}
            expect:
              name: {type: string}
              supportedInterfaces: {type: array, count_gte: 1}
              skills: {type: array}

  - id: data-model
    name: "Data Model & Serialization"
    tests:

      - id: DM-SERIAL-001
        name: "JSON serialization uses camelCase field names"
        spec_ref: "specification.md#2.3"
        level: must
        transport: [jsonrpc, rest]
        tags: [serialization, wire-format]
        steps:
          - id: send
            action: send_message
            request:
              message:
                role: ROLE_USER
                parts:
                  - text: "tck-complete-task camelCase test"
            expect:
              result_type: task
              task:
                id: {type: string}
            # Runner must additionally verify raw response keys are camelCase

      - id: DM-SERIAL-005
        name: "Server ignores unrecognized fields"
        spec_ref: "specification.md#2.3"
        level: must
        tags: [serialization, tolerance]
        steps:
          - id: send
            action: send_message
            request:
              message:
                role: ROLE_USER
                parts:
                  - text: "tck-complete-task with extra fields"
                futureField: "should be ignored"
                extraNested:
                  foo: "bar"
            expect:
              result_type: task
              task:
                status:
                  state: TASK_STATE_COMPLETED
```

---

## 15. File Organization

The official A2A conformance test suite SHOULD be organized as follows:

```
a2a-conformance/
├── acts-spec.md                   # This specification
├── v1.0/                          # Tests for A2A spec v1.0
│   ├── suite.yaml                 # Master file listing all test files
│   ├── discovery.yaml             # CARD-* tests
│   ├── core-operations.yaml       # CORE-* tests
│   ├── streaming.yaml             # STREAM-* tests
│   ├── error-handling.yaml        # Error tests (CORE-ERR-*, CORE-CAP-*)
│   ├── multi-turn.yaml            # CORE-MULTI-* tests
│   ├── push-notifications.yaml    # PUSH-* tests
│   ├── data-model.yaml            # DM-* tests
│   ├── history.yaml               # CORE-HIST-* tests
│   ├── version-negotiation.yaml   # VER-* tests
│   ├── transport-jsonrpc.yaml     # JSONRPC-* tests
│   ├── transport-grpc.yaml        # GRPC-* tests
│   ├── transport-rest.yaml        # REST-* tests
│   ├── client-parsing.yaml        # CLIENT-* golden response tests
│   ├── interop.yaml               # INTEROP-* tests (from cross-SDK bugs)
│   └── sut-behaviors.yaml         # Standard SUT behavior contract
└── v0.3/                          # Backward compatibility tests (if needed)
    └── ...
```

The `suite.yaml` master file references all test files in the version directory:

```yaml
acts_version: "1.0"
spec_version: "1.0"
include:
  - discovery.yaml
  - core-operations.yaml
  - streaming.yaml
  - error-handling.yaml
  - multi-turn.yaml
  - push-notifications.yaml
  - data-model.yaml
  - history.yaml
  - version-negotiation.yaml
  - transport-jsonrpc.yaml
  - transport-grpc.yaml
  - transport-rest.yaml
  - client-parsing.yaml
  - interop.yaml
```

---

## 16. Versioning

The ACTS format itself is versioned independently of the A2A protocol. The `acts_version` field in each document identifies the format version. The `spec_version` field identifies which A2A protocol version the tests target.

When the ACTS format evolves:

- **Patch** (e.g., 1.0.1): Clarifications, typo fixes. No structural changes.
- **Minor** (e.g., 1.1): New optional fields, new assertion operators. Backward-compatible.
- **Major** (e.g., 2.0): Breaking changes to the format structure.

Runners MUST reject documents with an `acts_version` major version they do not support.

---

## Appendix A: Full CDDL Grammar

This appendix consolidates all CDDL definitions from the specification into a single grammar.

```cddl
; ── Document ──────────────────────────────────────────────────────
acts-document = {
  acts_version: text,
  spec_version: text,
  ? spec_ref: text,
  ? metadata: metadata,
  ? variables: { * text => text },
  ? include: [+ text],             ; For suite.yaml: list of files to include
  ? suites: [+ suite]              ; At least one of include or suites MUST be present
}

metadata = {
  ? title: text,
  ? description: text,
  ? authors: [+ text],
  ? license: text
}

; ── Suite ─────────────────────────────────────────────────────────
suite = {
  id: text,
  name: text,
  ? description: text,
  ? tags: [+ text],
  tests: [+ test]
}

; ── Test ──────────────────────────────────────────────────────────
test = {
  id: text,
  name: text,
  ? description: text,
  ? spec_ref: text,
  level: conformance-level,
  ? tags: [+ text],
  ? transport: [+ transport-binding],
  ? preconditions: preconditions,
  ? requires_behaviors: [+ text],  ; SUT behavior prefixes this test depends on
  ? origin: text,
  steps: [+ step]
}

conformance-level = "must" / "should" / "may"
transport-binding = "jsonrpc" / "grpc" / "rest"

preconditions = {
  ? capabilities: { * text => any },
  ? skills: [+ { id: text }],
  ? transport: [+ transport-binding],
  ? extensions: [+ text],
  ? description: text
}

; ── Steps ─────────────────────────────────────────────────────────
step = server-step / client-step / assertion-step / raw-step

server-step = {
  id: text,
  ? description: text,
  action: abstract-operation,
  request: request-params,
  ? expect: expect-block,
  ? expect_error: expect-error,
  ? expect_stream: expect-stream,
  ? capture: { + text => text },
  ? repeat: repeat-config,
  ? delay_ms: int
}

client-step = {
  id: text,
  ? description: text,
  type: "client_test",
  golden_response: {
    ? status: int,
    ? headers: { * text => text },
    body: any
  },
  expect_parsed: { * text => assertion }
}

assertion-step = {
  id: text,
  ? description: text,
  assertion: inline-assertion
}

raw-step = {
  id: text,
  ? description: text,
  raw_request: {
    method: "GET" / "POST" / "PUT" / "DELETE",
    path: text,
    ? headers: { * text => text },
    ? body: any,
    ? rawBody: text
  },
  ? raw_expect: {
    ? status: int,
    ? headers: { * text => assertion },
    ? body: { * text => assertion }
  },
  ? capture: { + text => text }
}

; ── Operations ────────────────────────────────────────────────────
abstract-operation =
  "send_message" /
  "send_streaming_message" /
  "get_task" /
  "list_tasks" /
  "cancel_task" /
  "subscribe_to_task" /
  "get_agent_card" /
  "get_extended_agent_card" /
  "create_push_config" /
  "get_push_config" /
  "list_push_configs" /
  "delete_push_config"

; ── Request ───────────────────────────────────────────────────────
request-params = {
  ? message: {
      role: text,
      parts: [+ part],
      ? messageId: text,
      ? taskId: text,
      ? contextId: text,
      * text => any
    },
  ? configuration: {
      ? returnImmediately: bool,
      ? historyLength: int,
      * text => any
    },
  ? id: text,
  ? historyLength: int,
  ? contextId: text,
  ? cursor: text,
  ? pageSize: int,
  ? taskId: text,
  ? pushNotificationConfig: any,
  * text => any
}

part = {
  ? text: text,
  ? data: any,
  ? file: {
      ? url: text,
      ? raw: text,
      ? mediaType: text,
      ? name: text
    },
  * text => any
}

; ── Expect ────────────────────────────────────────────────────────
expect-block = {
  ? result_type: "task" / "message",
  ? task: { * text => assertion },
  ? message: { * text => assertion },
  * text => assertion
}

expect-error = {
  error_type: a2a-error-type,
  ? message: assertion,
  ? details: { * text => assertion }
}

a2a-error-type =
  "TaskNotFoundError" /
  "TaskNotCancelableError" /
  "UnsupportedOperationError" /
  "ContentTypeNotSupportedError" /
  "InvalidParamsError" /
  "VersionNotSupportedError" /
  "PushNotificationNotSupportedError" /
  "StreamingNotSupportedError" /
  "ExtensionSupportRequiredError" /
  "ExtendedCardNotSupportedError" /
  "JSONParseError" /
  "MethodNotFoundError" /
  "InternalError"

; ── Streaming ─────────────────────────────────────────────────────
expect-stream = {
  ? min_count: int,
  ? max_count: int,
  ? timeout_ms: int,
  ? ordering: ordering-rule,
  ? events: [+ event-assertion],
  ? final_event: { * text => assertion },
  ? each_event: { * text => assertion }
}

ordering-rule = "monotonic_state"

event-assertion = {
  ? description: text,
  ? match: "exact_position" / "any_position",
  ? index: int,
  ? status_update: { * text => assertion },
  ? artifact_update: { * text => assertion },
  ? task: { * text => assertion },
  ? message: { * text => assertion },
  * text => assertion
}

; ── Assertions ────────────────────────────────────────────────────
assertion = exact-match / assertion-object

exact-match = text / int / float / bool / null

assertion-object = {
  ? type: "string" / "number" / "boolean" / "array" / "object" / "null",
  ? exists: true,
  ? absent: true,
  ? contains: text,
  ? matches: text,
  ? starts_with: text,
  ? ends_with: text,
  ? gte: number,
  ? lte: number,
  ? gt: number,
  ? lt: number,
  ? count: int,
  ? count_gte: int,
  ? count_lte: int,
  ? one_of: [+ any],
  ? all_of: [+ assertion],
  ? any_of: [+ assertion],
  ? not: assertion
}

number = int / float

; ── Collection Assertions ─────────────────────────────────────────
inline-assertion = {
  source: text,
  ? any: collection-match,
  ? all: collection-match,
  ? none: collection-match
}

collection-match = {
  path: text,
  match: { * text => assertion }
}

; ── Polling ───────────────────────────────────────────────────────
repeat-config = {
  until: text,
  ? max_attempts: int,
  ? delay_ms: int,
  ? backoff: "none" / "linear" / "exponential"
}

; ── SUT Behaviors ─────────────────────────────────────────────────
sut-behaviors = {
  acts_version: text,
  behaviors: [+ behavior]
}

behavior = {
  prefix: text,
  description: text,
  ? response_type: "task" / "message",
  ? terminal_state: text,
  ? artifacts: [+ artifact-spec],
  ? delay_ms: int,
  ? streaming: bool
}

artifact-spec = {
  ? text: text,
  ? data: any,
  ? file: { name: text, mediaType: text },
  ? fileUrl: { url: text, name: text, mediaType: text }
}
```

---

## Appendix B: Existing Requirement ID Inventory

The following requirement IDs are carried forward from existing conformance testing efforts (primarily the A2A TCK). New tests SHOULD follow the same naming pattern.

### CORE (Core Operations)
| ID | Description |
|----|-------------|
| CORE-SEND-001 | SendMessage returns a completed task |
| CORE-SEND-002 | SendMessage to a terminal task returns UnsupportedOperationError |
| CORE-SEND-003 | ContentTypeNotSupportedError detected by SDK |
| CORE-GET-001 | GetTask returns the current state of an existing task |
| CORE-CANCEL-001 | CancelTask returns the task with updated state |
| CORE-CANCEL-002 | CancelTask on a terminal task returns TaskNotCancelableError |
| CORE-MULTI-001 | Multi-turn conversation with INPUT_REQUIRED |
| CORE-MULTI-005 | SendMessage with only taskId infers contextId |
| CORE-MULTI-006 | SendMessage with taskId + wrong contextId returns error |
| CORE-EXEC-001 | Long-running task with returnImmediately and polling |
| CORE-ERR-001 | Server returns appropriate errors with actionable info |
| CORE-ERR-002 | Server validates input parameters |
| CORE-CAP-001 | Push operations return error when not supported |
| CORE-CAP-002 | Streaming operations return error when not supported |
| CORE-CAP-003 | Extended agent card returns error when not supported |
| CORE-CAP-004 | Required extension missing returns error |
| CORE-HIST-001 | GetTask with historyLength=0 returns no history |
| CORE-HIST-002 | GetTask history count ≤ historyLength |
| CORE-HIST-003 | SendMessage with historyLength=0 returns no history |
| CORE-HIST-004 | GetTask with historyLength>0 may return persisted messages |
| CORE-HIST-005 | History messages in chronological order |
| CORE-HIST-006 | History content matches exchanged messages |

### STREAM (Streaming)
| ID | Description |
|----|-------------|
| STREAM-ORDER-001 | Task states never regress; last event is terminal |
| STREAM-ORDER-002 | Events broadcast to all active streams |
| STREAM-ORDER-003 | Each stream receives same events in same order |
| STREAM-ORDER-004 | Closing one stream does not affect others |
| STREAM-SUB-001 | First SubscribeToTask event contains a Task |
| STREAM-SUB-002 | SubscribeToTask stream closes at terminal state |
| STREAM-SUB-003 | SubscribeToTask on terminal task returns error |
| STREAM-SUB-004 | SubscribeToTask on non-existent task returns TaskNotFoundError |

### CARD (Agent Card Discovery)
| ID | Description |
|----|-------------|
| CARD-DISC-001 | Agent card is retrievable |
| CARD-STRUCT-001 | AgentCard contains required fields |
| CARD-PROTO-001 | supportedInterfaces is non-empty |
| CARD-PROTO-002 | Each interface validates against AgentInterface schema |
| CARD-CACHE-001 | Agent Card includes Cache-Control header |
| CARD-CACHE-002 | Agent Card includes ETag header |
| CARD-CACHE-003 | Agent Card may include Last-Modified header |

### DM (Data Model & Serialization)
| ID | Description |
|----|-------------|
| DM-TASK-001 | Task has required fields (id, status) |
| DM-MSG-001 | Message has required fields (role, parts, messageId) |
| DM-PART-001 | Part oneof semantics |
| DM-ART-001 | Artifact has required fields |
| DM-STATUS-001 | TaskStatus.state field present |
| DM-SERIAL-001 | JSON uses camelCase field names |
| DM-SERIAL-002 | Enum values are strings, not integers |
| DM-SERIAL-003 | Timestamps use ISO 8601 with Z suffix |
| DM-SERIAL-005 | Implementations ignore unrecognized fields |

### PUSH (Push Notifications)
| ID | Description |
|----|-------------|
| PUSH-CREATE-001 | CreatePushNotificationConfig returns the config |
| PUSH-CREATE-002 | Config persists and can be retrieved |
| PUSH-GET-001 | GetPushNotificationConfig returns details |
| PUSH-GET-002 | GetPushNotificationConfig with nonexistent ID errors |
| PUSH-LIST-001 | ListPushNotificationConfigs includes created config |
| PUSH-DEL-001 | DeletePushNotificationConfig removes config |
| PUSH-DEL-002 | Deleting already-deleted config is idempotent |
| PUSH-DELIVER-001 | Agent includes auth credentials in webhook |
| PUSH-DELIVER-002 | Agent attempts delivery at least once |
| PUSH-DELIVER-003 | Webhook payload uses StreamResponse format |

### JSONRPC (JSON-RPC Binding)
| ID | Description |
|----|-------------|
| JSONRPC-FMT-001 | Response conforms to JSON-RPC 2.0 |
| JSONRPC-FMT-002 | Content-Type is application/json |
| JSONRPC-SVC-001 | Method names match spec |
| JSONRPC-SVC-002 | Service parameters in HTTP headers |
| JSONRPC-SSE-001 | SSE events are JSON-RPC 2.0 responses |
| JSONRPC-SSE-002 | Error types map to correct JSON-RPC codes |
| JSONRPC-ERR-001 | Error object has code, message, optional data |
| JSONRPC-ERR-002 | A2A errors use codes -32001 to -32099 |
| JSONRPC-ERR-003 | Errors include ErrorInfo in data array |

### GRPC (gRPC Binding)
| ID | Description |
|----|-------------|
| GRPC-SVC-001 | A2AService responds and validates against proto |
| GRPC-SVC-002 | Uses Protocol Buffers v3 |
| GRPC-META-001 | Service parameters in gRPC metadata |
| GRPC-ERR-001 | Errors include ErrorInfo in status details |
| GRPC-ERR-002 | Errors map to correct gRPC status codes |
| GRPC-ERR-003 | Streaming uses server streaming RPCs |

### VER (Version Negotiation)
| ID | Description |
|----|-------------|
| VER-SERVER-002 | Unsupported A2A-Version returns VersionNotSupportedError |
| VER-SERVER-003 | Empty A2A-Version treated as 0.3 |

### BIND (Protocol Binding)
| ID | Description |
|----|-------------|
| BIND-FIELD-001 | All supported protocols declared in AgentCard |
