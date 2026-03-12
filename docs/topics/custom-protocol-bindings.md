# Custom Protocol Bindings

The A2A protocol ships with three standard bindings—JSON-RPC, gRPC, and
HTTP+JSON/REST—that cover the majority of deployment scenarios. Custom protocol
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
list. Each entry identifies the transport, the endpoint URL, and the A2A
protocol version it implements.

```json
{
  "supportedInterfaces": [
    {
      "url": "wss://agent.example.com/a2a/websocket",
      "protocolBinding": "WEBSOCKET",
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
[Protocol Binding Requirements and Interoperability](specification.md#5-protocol-binding-requirements-and-interoperability)
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
[Error Code Mappings](specification.md#54-error-code-mappings) section, showing
how each A2A error type (e.g., `TaskNotFoundError`,
`UnsupportedOperationError`) is expressed in the custom binding's native error
format.

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

The A2A protocol provides extension points that allow agents to advertise and
negotiate custom transport bindings. This section defines a formal governance
framework for how custom protocol bindings are proposed, developed, promoted,
and maintained within the A2A organization.

### Binding Tiers

This framework defines two tiers of custom protocol bindings within the A2A
organization. Anyone may develop and publish their own custom protocol bindings
independently; these tiers apply specifically to bindings hosted under the
`a2aproject` GitHub organization.

#### Official Bindings

Official custom protocol bindings are developed and maintained under the
`a2aproject` GitHub organization and officially recommended by the TSC.

**Repository Structure:**

- Binding repositories use the `cpb-` prefix:
    `github.com/a2aproject/cpb-{name}`
- Examples: `cpb-websocket`, `cpb-mqtt`, `cpb-amqp`
- Each repository has designated maintainers identified in `MAINTAINERS.md`

**Requirements:**

- Binding specifications MUST use the same language as the core specification
    ([RFC 2119](https://tools.ietf.org/html/rfc2119))
- Bindings MUST be licensed under Apache 2.0
- Bindings MUST have at least one reference implementation
- Bindings SHOULD have associated documentation on the A2A website

#### Experimental Bindings

Experimental bindings provide an incubation pathway for community contributors
to prototype and collaborate on custom binding ideas before graduation to
official status.

**Repository Structure:**

- Experimental repositories use the `experimental-cpb-` prefix:
    `github.com/a2aproject/experimental-cpb-{name}`
- Example: `experimental-cpb-websocket`

**Creation Requirements:**

- An experimental binding repository can ONLY be created with sponsorship from
    an A2A Maintainer
- The sponsoring Maintainer is responsible for initial oversight of the
    experimental binding
- Experimental repositories MUST clearly indicate their experimental/non-official
    status in the README
- Any published packages MUST use naming that clearly indicates experimental
    status
- The TSC retains oversight, including the ability to archive or remove
    experimental repositories

### Binding Lifecycle

Bindings progress through the following phases.

#### Proposal Phase

Any community member may propose a custom protocol binding:

1. **Open an Issue**: Create an issue in the main `a2aproject/A2A` repository
    describing:
    - An abstract describing the binding's transport and use case
    - Motivation explaining why the existing standard bindings do not satisfy
        the requirement
    - An initial technical approach or specification draft
2. **Community Discussion**: The proposal is open for community feedback and
    refinement

#### Maintainer Sponsorship

For a proposal to proceed to experimental status:

1. **Secure a Sponsor**: An A2A Maintainer must agree to sponsor the binding
    proposal
2. **Repository Creation**: The sponsoring Maintainer creates the
    `experimental-cpb-*` repository under `a2aproject`
3. **Oversight**: The sponsoring Maintainer provides initial oversight and
    ensures alignment with A2A design principles

#### Experimental Development

While in experimental status:

- Contributors iterate on the specification and reference implementations
- The experimental binding MAY be used by early adopters with the understanding
    that breaking changes are expected
- Community feedback is gathered and incorporated
- The experimental repository MUST clearly indicate its non-official status

#### Graduation to Official Binding

To graduate an experimental binding to official status:

1. **Maturity Requirements**:
    - At least one production-quality reference implementation
    - Documentation meeting A2A standards
    - Evidence of community adoption or interest
    - Clear maintainer commitment for ongoing maintenance
2. **Graduation Proposal**: Open an issue in `a2aproject/A2A` with:
    - Reference to the experimental repository and its implementations
    - Summary of community feedback and adoption
    - Proposed maintainers for the official binding
3. **TSC Vote**:
    - The proposal is added to the TSC meeting agenda
    - **Quorum Requirement**: At least 50% of TSC voting members must be
        present
    - **Approval**: Requires majority vote of those in attendance (per A2A
        governance)
    - The TSC may request revisions before a final vote
4. **Acceptance**:
    - Upon approval, the repository is renamed from `experimental-cpb-*` to
        `cpb-*`
    - Documentation is added to the A2A website's custom protocol bindings page

#### Official Binding Iteration

Once official, bindings may be iterated on:

- Binding repository maintainers are responsible for day-to-day governance
- Changes SHOULD be coordinated via the relevant working group if one exists
- Breaking changes require a new binding identifier
- Breaking changes require TSC review
- Maintainers SHOULD coordinate with SDK maintainers for implementation updates

#### Promotion to Core Protocol

Some custom bindings may eventually transition to core protocol bindings. This
is governed through the existing A2A specification enhancement process:

- A proposal is submitted following the standard specification change process
- The proposal references the official binding and its adoption
- TSC vote with standard quorum and majority requirements applies
- Not all custom bindings are suitable for core inclusion; many will remain as
    custom bindings indefinitely

### SDK Support

A2A SDKs MAY implement custom protocol bindings. Where implemented:

- Custom protocol bindings MUST be disabled by default and require explicit
    opt-in
- SDK documentation SHOULD list supported custom protocol bindings
- SDK maintainers have full autonomy over binding support decisions
- Custom protocol binding support is not required for protocol conformance

### Legal Requirements

#### Licensing

Official custom protocol bindings MUST be available under the Apache 2.0
license, consistent with the core A2A project.

#### Contributor License Grant

By submitting a contribution to an official A2A custom protocol binding
repository, contributors represent that:

1. They have the legal authority to grant the rights
2. The contribution is original work or they have sufficient rights to submit it
3. They grant to the Linux Foundation and recipients a perpetual, worldwide,
    non-exclusive, royalty-free license to use, reproduce, modify, and
    distribute the contribution

#### Antitrust

Custom protocol binding developers acknowledge that:

- They may compete with other participants
- They have no obligation to implement any binding
- They are free to develop competing bindings
- Status as an official binding does not create an exclusive relationship
