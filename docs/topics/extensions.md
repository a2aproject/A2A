# Extensions in A2A

The Agent2Agent (A2A) protocol provides a strong foundation for inter-agent
communication. However, specific domains or advanced use cases often require
additional structure, custom data, or new interaction patterns beyond the
generic methods. Extensions are A2A's powerful mechanism for layering new capabilities onto the
base protocol.

Extensions allow for extending the A2A protocol with new data, requirements,
RPC methods, and state machines. Agents declare their support for specific
extensions in their Agent Card, and clients can then opt in to the behavior
offered by an extension as part of requests they make to the agent. Extensions
are identified by a URI and defined by their own specification. Anyone is able to define, publish, and implement an extension.

The flexibility of extensions allows for customizing A2A without fragmenting
the core standard, fostering innovation and domain-specific optimizations.

## Scope of Extensions

The exact set of possible ways to use extensions is intentionally broad,
facilitating the ability to expand A2A beyond known use cases.
However, some foreseeable applications include:

- **Data-only Extensions**: Exposing new, structured information in the Agent
    Card that doesn't impact the request-response flow. For example, an
    extension could add structured data about an agent's GDPR compliance.
- **Profile Extensions**: Overlaying additional structure and state change
    requirements on the core request-response messages. This type effectively
    acts as a profile on the core A2A protocol, narrowing the space of allowed
    values (for example, requiring all messages to use `DataParts` adhering to
    a specific schema). This can also include augmenting existing states in the
    task state machine by using metadata. For example, an extension could define
    a 'generating-image' substate when `TaskStatus.state` is 'working' and
    `TaskStatus.message.metadata["generating-image"]` is true.
- **Method Extensions (Extended Skills)**: Adding entirely new RPC methods
    beyond the core set defined by the protocol. An Extended Skill refers to a
    capability or function an agent gains or exposes specifically through the
    implementation of an extension that defines new RPC methods. For example, a
    `task-history` extension might add a `tasks/search` RPC method to retrieve
    a list of previous tasks, effectively providing the agent with a new,
    extended skill.
- **State Machine Extensions**: Adding new states or transitions to the task
  state machine.

## List of Example Extensions

| Extension | Description |
| :-------- | :------------ |
| [Secure Passport Extension](https://github.com/a2aproject/a2a-samples/tree/main/extensions/secure-passport) | Adds a trusted, contextual layer for immediate personalization and reduced overhead (v1). |
| [Hello World or Timestamp Extension](https://github.com/a2aproject/a2a-samples/tree/main/extensions/timestamp) | A simple extension demonstrating how to augment base A2A types by adding timestamps to the `metadata` field of `Message` and `Artifact` objects (v1). |
| [Traceability Extension](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/extensions/traceability) | Explore the Python implementation and basic usage of the Traceability Extension (v1). |
| [Agent Gateway Protocol (AGP) Extension](https://github.com/a2aproject/a2a-samples/tree/main/extensions/agp) | A Core Protocol Layer or Routing Extension that introduces Autonomous Squads (ASq) and routes Intent payloads based on declared Capabilities, enhancing scalability (v1). |

## Extension Governance

The A2A protocol provides extension points in the specification, allowing
agents to advertise and negotiate extended capabilities. This section defines
a formal governance framework for how extensions are proposed, developed,
promoted, and maintained within the A2A organization.

### Extension Tiers

This framework defines two tiers of extensions within the A2A organization.
Anyone may develop and publish their own extensions independently; these tiers
apply specifically to extensions hosted under the `a2aproject` GitHub
organization.

#### Official Extensions

Official extensions are developed and maintained under the `a2aproject` GitHub
organization, officially recommended by the TSC, and use the
`https://a2a-protocol.org/extensions/` URI prefix.

**Repository Structure:**

- Extension repositories use the `ext-` prefix:
    `github.com/a2aproject/ext-{name}`
- Examples: `ext-ui`, `ext-payments`, `ext-auth`
- Each repository has designated maintainers identified in `MAINTAINERS.md`

**Requirements:**

- Extension specifications MUST use the same language as the core
    specification ([RFC 2119](https://tools.ietf.org/html/rfc2119))
- Extensions MUST be licensed under Apache 2.0
- Extensions MUST have at least one reference implementation
- Extensions SHOULD have associated documentation on the A2A website

#### Experimental Extensions

Experimental extensions provide an incubation pathway for community
contributors to prototype and collaborate on extension ideas before graduation
to official status.

**Repository Structure:**

- Experimental repositories use the `experimental-ext-` prefix:
    `github.com/a2aproject/experimental-ext-{name}`
- Example: `experimental-ext-orchestration`

**Creation Requirements:**

- An experimental extension repository can ONLY be created with sponsorship
    from an A2A Maintainer
- The sponsoring Maintainer is responsible for initial oversight of the
    experimental extension
- Experimental repositories MUST clearly indicate their
    experimental/non-official status in the README
- Any published packages MUST use naming that clearly indicates experimental
    status
- The TSC retains oversight, including the ability to archive or remove
    experimental repositories

### Extension Lifecycle

Extensions progress through the following phases:

#### Proposal Phase

Any community member may propose an extension:

1. **Open an Issue**: Create an issue in the main `a2aproject/A2A` repository
    describing:
    - An abstract describing the extension's purpose
    - Motivation explaining why this cannot be achieved with the core protocol
    - An initial technical approach or specification draft
2. **Community Discussion**: The proposal is open for community feedback and
    refinement

#### Maintainer Sponsorship

For a proposal to proceed to experimental status:

1. **Secure a Sponsor**: An A2A Maintainer must agree to sponsor the extension
    proposal
2. **Repository Creation**: The sponsoring Maintainer creates the
    `experimental-ext-*` repository under `a2aproject`
3. **Oversight**: The sponsoring Maintainer provides initial oversight and
    ensures alignment with A2A design principles

#### Experimental Development

While in experimental status:

- Contributors iterate on the specification and reference implementations
- The experimental extension MAY be used by early adopters with the
    understanding that breaking changes are expected
- Community feedback is gathered and incorporated
- The experimental repository MUST clearly indicate its non-official status

#### Graduation to Official Extension

To graduate an experimental extension to official status:

1. **Maturity Requirements**:
    - At least one production-quality reference implementation
    - Documentation meeting A2A standards
    - Evidence of community adoption or interest
    - Clear maintainer commitment for ongoing maintenance
2. **Graduation Proposal**: Open an issue in `a2aproject/A2A` with:
    - Reference to the experimental repository and its implementations
    - Summary of community feedback and adoption
    - Proposed maintainers for the official extension
3. **TSC Vote**:
    - The proposal is added to the TSC meeting agenda
    - **Quorum Requirement**: At least 50% of TSC voting members must be
        present
    - **Approval**: Requires majority vote of those in attendance (per A2A
        governance)
    - The TSC may request revisions before a final vote
4. **Acceptance**:
    - Upon approval, the repository is renamed from `experimental-ext-*` to
        `ext-*`
    - Documentation is added to the A2A website's extensions page

#### Official Extension Iteration

Once official, extensions may be iterated on without further TSC review for
non-breaking changes:

- Extension repository maintainers are responsible for day-to-day governance
- Changes SHOULD be coordinated via the relevant working group if one exists
- Breaking changes require a new extension identifier
- Maintainers SHOULD coordinate with SDK maintainers for implementation
    updates

#### Promotion to Core Protocol

Some extensions may eventually transition to core protocol features. This is
governed through the existing A2A specification enhancement process:

- A proposal is submitted following the standard specification change process
- The proposal references the official extension and its adoption
- TSC vote with standard quorum and majority requirements applies
- Not all extensions are suitable for core inclusion; many will remain as
    extensions indefinitely

### SDK Extension Support

A2A SDKs MAY implement extensions. Where implemented:

- Extensions MUST be disabled by default and require explicit opt-in
- SDK documentation SHOULD list supported extensions
- SDK maintainers have full autonomy over extension support decisions
- Extension support is not required for protocol conformance

### Legal Requirements

#### Licensing

Official extensions MUST be available under the Apache 2.0 license, consistent
with the core A2A project.

#### Contributor License Grant

By submitting a contribution to an official A2A extension repository,
contributors represent that:

1. They have the legal authority to grant the rights
2. The contribution is original work or they have sufficient rights to submit
    it
3. They grant to the Linux Foundation and recipients a perpetual, worldwide,
    non-exclusive, royalty-free license to use, reproduce, modify, and
    distribute the contribution

#### Antitrust

Extension developers acknowledge that:

- They may compete with other participants
- They have no obligation to implement any extension
- They are free to develop competing extensions
- Status as an official extension does not create an exclusive relationship

## Limitations

There are some changes to the protocol that extensions don't allow, primarily
to prevent breaking core type validations:

- **Changing the Definition of Core Data Structures**: For example, adding new
    fields or removing required fields to protocol-defined data structures.
    Extensions should place custom attributes in the `metadata` map present on
    core data structures.
- **Adding New Values to Enum Types**: Extensions should use existing enum values
    and annotate additional semantic meaning in the `metadata` field.

## Extension Declaration

Agents declare their support for extensions in their Agent Card by including
`AgentExtension` objects within their `AgentCapabilities` object.

```ts { .no-copy }
--8<-- "types/src/types.ts:AgentExtension"
```

The following is an example of an Agent Card with an extension:

```json
{
  "name": "Magic 8-ball",
  "description": "An agent that can tell your future... maybe.",
  "version": "0.1.0",
  "url": "https://example.com/agents/eightball",
  "capabilities": {
    "streaming": true,
    "extensions": [
      {
        "uri": "https://example.com/ext/konami-code/v1",
        "description": "Provide cheat codes to unlock new fortunes",
        "required": false,
        "params": {
          "hints": [
            "When your sims need extra cash fast",
            "You might deny it, but we've seen the evidence of those cows."
          ]
        }
      }
    ]
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": [
    {
      "id": "fortune",
      "name": "Fortune teller",
      "description": "Seek advice from the mystical magic 8-ball",
      "tags": ["mystical", "untrustworthy"]
    }
  ]
}
```

## Required Extensions

While extensions generally offer optional functionality, some agents may have
stricter requirements. When an Agent Card declares an extension as
`required: true`, it signals to clients that some aspect of the extension impacts how
requests are structured or processed, and that the client must abide by it.
Agents shouldn't mark data-only extensions as required. If a client does not
request activation of a required extension, or fails to follow its protocol,
the agent should reject the incoming request with an appropriate error.

## Extension Specification

The detailed behavior and structure of an extension are defined by its
**specification**. While the exact format is not mandated, it should contain at
least:

- The specific URI(s) that identify the extension.
- The schema and meaning of objects specified in the `params` field of the
    `AgentExtension` object.
- Schemas of any additional data structures communicated between client and
    agent.
- Details of new request-response flows, additional endpoints, or any other
    logic required to implement the extension.

## Extension Dependencies

Extensions might depend on other extensions. This can be a required dependency
(where the extension cannot function without the dependent) or an optional one
(where additional functionality is enabled if another extension is present).
Extension specifications should document these dependencies. It is the client's
responsibility to activate an extension and all its required dependencies as
listed in the extension's specification.

## Extension Activation

Extensions default to being inactive, providing a baseline
experience for extension-unaware clients. Clients and agents perform
negotiation to determine which extensions are active for a specific request.

1. **Client Request**: A client requests extension activation by including the
    `A2A-Extensions` header in the HTTP request to the agent. The value is a
    comma-separated list of extension URIs the client intends to activate.
2. **Agent Processing**: Agents are responsible for identifying supported
    extensions in the request and performing the activation. Any requested
    extensions not supported by the agent can be ignored.
3. **Response**: Once the agent has identified all activated extensions, the
    response SHOULD include the `A2A-Extensions` header, listing all
    extensions that were successfully activated for that request.

![A2A Extension Flow Diagram](https://storage.googleapis.com/gweb-developer-goog-blog-assets/images/Screenshot_2025-09-04_at_13.03.31.original.png){ width="70%" style="margin:20px auto;display:block;" }

**Example request showing extension activation:**

```http
POST /agents/eightball HTTP/1.1
Host: example.com
Content-Type: application/json
A2A-Extensions: https://example.com/ext/konami-code/v1
Content-Length: 519
{
  "jsonrpc": "2.0",
  "method": "SendMessage",
  "id": "1",
  "params": {
    "message": {
      "messageId": "1",
      "role": "ROLE_USER",
      "parts": [{"text": "Oh magic 8-ball, will it rain today?"}]
    },
    "metadata": {
      "https://example.com/ext/konami-code/v1/code": "motherlode"
    }
  }
}
```

**Corresponding response echoing activated extensions:**

```http
HTTP/1.1 200 OK
Content-Type: application/json
A2A-Extensions: https://example.com/ext/konami-code/v1
Content-Length: 338
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "message": {
      "messageId": "2",
      "role": "ROLE_AGENT",
      "parts": [{"text": "That's a bingo!"}]
    }
  }
}
```

## Implementation Considerations

While the A2A protocol defines the functionality of extensions, this section
provides guidance on their implementation—best practices for authoring,
versioning, and distributing extension implementations.

- **Versioning**: Extension specifications evolve. It is
    crucial to have a clear versioning strategy to ensure that clients and
    agents can negotiate compatible implementations.
    - **Recommendation**: Use the extension's URI as the primary version
        identifier, ideally including a version number (for example,
        `https://example.com/ext/my-extension/v1`).
    - **Breaking Changes**: A new URI MUST be used when introducing a breaking
        change to an extension's logic, data structures, or required parameters.
    - Handling Mismatches: If a client requests a version not supported by
        the agent, the agent SHOULD ignore the activation request for that
        extension; it MUST NOT fall back to a different version.
- **Discoverability and Publication**:
    - **Specification Hosting**: The extension specification document **should** be
        hosted at the extension's URI.
    - **Permanent Identifiers**: Authors are encouraged to use a permanent
        identifier service, such as `w3id.org`, for their extension URIs to
        prevent broken links.
    - **Community Registry**: The A2A [Extension Governance](#extension-governance)
        framework defines a tiered system for official and experimental
        extensions hosted under the `a2aproject` organization, including a
        lifecycle for proposing and promoting extensions.
- **Packaging and Reusability (A2A SDKs and Libraries)**:
    To promote adoption, extension logic should be packaged into reusable
        libraries that can be integrated into existing A2A client and
        server applications.
    - An extension implementation should be distributed as a
        standard package for its language ecosystem (for example, a PyPI package
        for Python, an npm package for TypeScript/JavaScript).
    - The objective is to provide a streamlined integration experience for
        developers. A well-designed extension package should allow a developer
        to add it to their server with minimal code, for example:

        ```python
        --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/adk_expense_reimbursement/__main__.py"
        ```

        This example showcases how A2A SDKs or libraries such as `a2a.server` in
        Python facilitate the implementation of A2A agents and extensions.

- **Security**: Extensions modify the core behavior of the A2A protocol, and therefore
    introduce new security considerations:

    - **Input Validation**: Any new data fields, parameters, or methods
        introduced by an extension MUST be rigorously validated. Treat all
        extension-related data from an external party as untrusted input.
    - **Scope of Required Extensions**: Be mindful when marking an extension as
        `required: true` in an Agent Card. This creates a hard dependency for
        all clients and should only be used for extensions fundamental to the
        agent's core function and security (for example, a message signing
        extension).
    - **Authentication and Authorization**: If an extension adds new methods,
        the implementation MUST ensure these methods are subject to the same
        authentication and authorization checks as the core A2A methods. An
        extension MUST NOT provide a way to bypass the agent's primary security
        controls.

For more information, see the [A2A Extensions: Empowering Custom Agent Functionality](https://developers.googleblog.com/en/a2a-extensions-empowering-custom-agent-functionality/) blog post.
