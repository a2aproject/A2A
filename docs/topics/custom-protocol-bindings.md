# Custom Protocol Bindings

The A2A protocol ships with three standard bindings (JSON-RPC, gRPC, and
HTTP+JSON/REST) that cover the majority of deployment scenarios. Custom protocol
bindings let implementers expose A2A operations over additional transport
mechanisms not covered by the standard set.

Custom protocol bindings are a complementary but distinct concept to
[Extensions](extensions.md). Extensions modify the *behavior* of protocol
interactions by adding new data, methods, or state transitions on top of an
existing transport. Custom protocol bindings change the *transport layer*
itself—for example, exposing A2A over WebSockets for low-latency bidirectional
communication, or over MQTT for IoT environments with constrained connectivity.

## Declaration in the Agent Card

Custom protocol bindings are declared in the Agent Card's `supportedInterfaces`
list. Each entry identifies the transport by URI, the endpoint URL, and the A2A
protocol version it implements. The `protocolBinding` field should be a URI that uniquely identifies the
binding (see [Section 5.8 of the specification](../specification.md#58-custom-binding-identification)
for the normative requirement and versioning guidance).

```json
{
  "supportedInterfaces": [
    {
      "url": "wss://agent.example.com/a2a/websocket",
      "protocolBinding": "https://a2a-protocol.org/bindings/websocket",
      "protocolVersion": "1.0"
    }
  ]
}
```

Agents that support multiple bindings list all of them. Clients parse
`supportedInterfaces` in order and select the first transport they support, so
entries should be listed in preference order.

## Requirements

Custom protocol bindings must comply with all requirements in the
[Protocol Binding Requirements and Interoperability](../specification.md#5-protocol-binding-requirements-and-interoperability)
section of the specification. In particular:

- **All core operations must be supported.** The binding must expose every
    operation defined in the abstract operations layer (send message, get task,
    cancel task, streaming, push notifications, etc.).
- **The data model must be preserved.** All data structures must be
    functionally equivalent to the canonical Protocol Buffer definitions. JSON
    serializations must use camelCase field names, and timestamps must be
    ISO 8601 strings in UTC.
- **Behavior must be consistent.** Semantically equivalent requests must
    produce semantically equivalent results regardless of which binding is used.

## Key Areas to Specify

A custom binding specification must address each of the following areas.

### Data Type Mappings

Document how each Protocol Buffer type is represented in the custom transport,
including:

- Binary data encoding (e.g., base64 for text-based transports)
- Enum representation (strings, integers, or named constants)
- Timestamp format (ISO 8601 strings in UTC per the core convention)

### Service Parameters

Service parameters are key-value pairs used to carry horizontally applicable
context such as tracing identifiers or authentication hints. The binding
specification must state:

- The mechanism used to carry service parameters (e.g., custom message headers,
    a top-level metadata field)
- Any character encoding or size constraints on keys and values
- Any names reserved by the binding itself

For transports that lack native header support, a common pattern is to embed
service parameters as a JSON object in a dedicated metadata field, for example
`a2a-service-parameters`.

### Error Mapping

The binding must map all A2A error types to transport-native error
representations while preserving their semantic meaning. Provide a mapping
table equivalent to the one in the specification's
[Error Code Mappings](../specification.md#54-error-code-mappings) section, showing
how each A2A error type (e.g., `TaskNotFoundError`, `UnsupportedOperationError`) is expressed in the custom binding's native error format.

### Streaming

If the transport supports streaming, document:

- The stream mechanism (e.g., WebSocket frames, chunked encoding, long polling)
- Ordering guarantees (events must be delivered in the order they were
    generated)
- Reconnection behavior when a connection is interrupted
- How stream completion or termination is signaled to the client

If the transport does not support streaming, state this limitation clearly in
the Agent Card so clients can fall back to polling.

### Authentication and Authorization

Document how authentication credentials declared in the Agent Card are
transmitted using the custom transport. Define how authentication challenges are
communicated to clients and ensure the custom binding does not inadvertently
bypass the agent's primary security controls.

## Interoperability Testing

Before publishing a custom binding, verify that:

- All operations behave identically to the standard bindings for the same
    logical requests
- Error conditions, large payloads, and long-running tasks are handled correctly
- Any intentional deviations from standard binding behavior are clearly
    documented
- Sample requests and responses are included in the specification to help
    implementers

## Governance

The A2A organization uses a formal governance framework for how custom protocol
bindings are proposed, developed, promoted, and maintained. Official bindings
use the `https://a2a-protocol.org/bindings/` URI prefix and are hosted under
the `a2aproject` organization with the `cpb-` repository prefix (experimental
bindings use `experimental-cpb-`). A2A SDKs SHOULD implement official custom
protocol bindings.

For the full governance process—including tiers, lifecycle, SDK support, and
legal requirements—see the
[Extension and Protocol Binding Governance](extension-and-binding-governance.md)
page.
