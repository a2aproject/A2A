# Extensions in A2A

The core Agent2Agent (A2A) protocol provides a robust foundation for inter-agent
communication. However, specific domains or advanced use cases often require
additional structure, custom data, or new interaction patterns beyond the
generic methods. Extensions are A2A's powerful mechanism for layering new
capabilities onto the core protocol.

Extensions allow for extending the A2A protocol with new data, requirements,
RPC methods, and state machines. Agents declare their support for specific
extensions in their Agent Card, and clients can then opt-in to the behavior
offered by an extension as part of requests they make to the agent. Extensions
are identified by a URI and defined by their own specification. Anyone is able
to define, publish, and implement an extension.

The flexibility of extensions allows for customizing A2A without fragmenting
the core standard, fostering innovation and domain-specific optimizations.

## Scope of Extensions

The exact set of possible ways to use extensions is intentionally broad,
facilitating the ability to expand A2A beyond currently known use cases.
However, some foreseeable applications include:

-   **Data-only extensions**: Exposing new, structured information in the Agent
    Card that doesn't impact the request/response flow. For example, an
    extension could add structured data about an agent's GDPR compliance.
-   **Profile extensions**: Overlaying additional structure and state change
    requirements on the core request/response messages. This type effectively
    acts as a profile on the core A2A protocol, narrowing the space of allowed
    values (for example, requiring all messages to use `DataParts` adhering to
    a specific schema).
-   **Method extensions (extended skills)**: Adding entirely new RPC methods
    beyond the core set defined by the protocol. An Extended Skill refers to a
    capability or function an agent gains or exposes specifically through the
    implementation of an extension that defines new RPC methods. For example, a
    `task-history` extension might add a `tasks/search` RPC method to retrieve
    a list of previous tasks, effectively providing the agent with a new,
    extended skill.
- **State machine extensions**: Adding new states or transitions to the task
  state machine.

## Limitations

There are some changes to the protocol that extensions do not allow, primarily
to prevent breaking core type validations:

-   **Changing the definition of core data structures**: For example, adding new
    fields or removing required fields to protocol-defined data structures).
    Extensions should place custom attributes in the metadata map present on
    core data structures.
-   **Adding new values to enum types**: Extensions should use existing enum values
    and annotate additional semantic meaning in the metadata field.

## Extension Declaration

Agents declare their support for extensions in their Agent Card by including
`AgentExtension` objects within their `AgentCapabilities` object.

The following table describes the fields of the `AgentExtension` object:

| Field Name  | Type    | Required | Description                                                                                                                               |
| ----------- | ------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `uri`       | `string`| Yes      | The URI that uniquely identifies the extension. Implementations use this URI to activate, and clients use it to determine compatibility. |
| `required`  | `boolean`| No       | Indicates whether the agent requires clients to use this extension for specific interactions.                                             |
| `description`| `string`| No       | A brief explanation of how the agent uses the declared extension.                                                                         |
| `params`    | `object` | No       | Extension-specific configuration parameters, as defined by the extension's specification.                                                  |


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
stricter requirements. When an Agent Card declares an extension as `required:
true`, it signals to clients that some aspect of the extension impacts how
requests are structured or processed, and that the client must abide by it.
Agents should not mark data-only extensions as required. If a client does not
request activation of a required extension, or fails to follow its protocol,
the agent should reject the incoming request with an appropriate error.

## Extension Specification

The detailed behavior and structure of an extension are defined by its
specification. While the exact format is not mandated, it should contain at
least:

*   The specific URI(s) that identify the extension.
*   The schema and meaning of objects specified in the `params` field of the
    `AgentExtension` object.
*   Schemas of any additional data structures communicated between client and
    agent.
*   Details of new request/response flows, additional endpoints, or any other
    logic required to implement the extension.

## Extension Dependencies

Extensions may depend on other extensions. This can be a required dependency
(where the extension cannot function without the dependent) or an optional one
(where additional functionality is enabled if another extension is present).
Extension specifications should document these dependencies. It is the client's
responsibility to activate an extension and all its required dependencies as
listed in the extension's specification.

## Extension Activation

Extensions default to being inactive, providing a "default to baseline"
experience for extension-unaware clients. Clients and agents perform
negotiation to determine which extensions are active for a specific request.

1.  **Client request**: A client requests extension activation by including the
    `X-A2A-Extensions` header in the HTTP request to the agent. The value is a
    comma-separated list of extension URIs the client intends to activate.
2.  **Agent processing**: Agents are responsible for identifying supported
    extensions in the request and performing the activation. Any requested
    extensions not supported by the agent can be ignored.
3.  **Response**: Once the agent has identified all activated extensions, the
    response SHOULD include the `X-A2A-Extensions` header, listing all
    extensions that were successfully activated for that request.

**Example request showing extension activation:**

```text
POST /agents/eightball HTTP/1.1
Host: example.com
Content-Type: application/json
X-A2A-Extensions: https://example.com/ext/konami-code/v1
Content-Length: 519
{
  "jsonrpc": "2.0",
  "method": "message/send",
  "id": "1",
  "params": {
    "message": {
      "kind": "message",
      "messageId": "1",
      "role": "user",
      "parts": [{"kind": "text", "text": "Oh magic 8-ball, will it rain today?"}]
    },
    "metadata": {
      "https://example.com/ext/konami-code/v1/code": "motherlode"
    }
  }
}
```

**Corresponding response echoing activated extensions:**

```text
HTTP/1.1 200 OK
Content-Type: application/json
X-A2A-Extensions: https://example.com/ext/konami-code/v1
Content-Length: 338
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "kind": "message",
    "messageId": "2",
    "role": "agent",
    "parts": [{"kind": "text", "text": "That's a bingo!"}]
  }
}
```

## Implementation Considerations

While the A2A protocol defines the "what" of extensions, this section provides
guidance on the "how"—best practices for authoring, versioning, and
distributing extension implementations.

-   **Versioning**: Extension specifications evolve. It is
    crucial to have a clear versioning strategy to ensure that clients and
    agents can negotiate compatible implementations.
    - **Recommendation**: Use the extension's URI as the primary version
        identifier, ideally including a version number (for example,
        `https://example.com/ext/my-extension/v1`).
    - **Breaking changes**: A new URI MUST be used when introducing a breaking
        change to an extension's logic, data structures, or required parameters.
    - Handling Mismatches: If a client requests a version not supported by
        the agent, the agent SHOULD ignore the activation request for that
        extension; it MUST NOT fall back to a different version.
-   **Discoverability and publication**:
    - **Specification hosting**: The extension specification document **should** be
        hosted at the extension's URI.
    - **Permanent identifiers**: Authors are encouraged to use a permanent
        identifier service, such as `w3id.org`, for their extension URIs to
        prevent broken links.
    - **Community registry (future)**: The A2A community may establish a
        central registry for discovering and browsing available extensions in
        the future.
-   **Packaging and reusability (A2A SDKs and libraries)**:
    To promote adoption, extension logic should be packaged into reusable
        libraries that can be easily integrated into existing A2A client and
        server applications.
    - An extension implementation should be distributed as a
        standard package for its language ecosystem (for example, a PyPI
        package for Python, an npm package for TypeScript/JavaScript).
    - The goal should be a near "plug-and-play"
        experience for developers. A well-designed extension package should
        allow a developer to add it to their server with minimal code, for
        example:

        ```python
        # Hypothetical Python Server Integration
        from konami_code_extension import CheatCodeHandler
        from a2a.server import A2AServer, DefaultRequestHandler

        # Using a2a.server, a component of the A2A Python library
        # The extension hooks into the request handler to process its logic
        extension = CheatCodeHandler(description="")
        extension.add_cheat(
            code="motherlode",
            hint="When your sims need extra cash fast",
        )
        extension.add_cheat(
            code="thereisnocowlevel",
            hint="You might deny it, but we've seen the evidence of those cows.",
        )
        request_handler = DefaultRequestHandler(
            agent_executor=MyAgentExecutor(extension),
            task_store=InMemoryTaskStore(),
            extensions=[extension]
        )
        server = A2AServer(agent_card, request_handler)
        server.run()
        ```

        This example showcases how A2A SDKs or libraries (like `a2a.server` in
        Python) facilitate the implementation of A2A agents and extensions.
-   **Security**:
    Extensions modify the core behavior of the A2A protocol, and therefore
        introduce new security considerations:
    
    - **Input validation**: Any new data fields, parameters, or methods
        introduced by an extension MUST be rigorously validated. Treat all
        extension-related data from an external party as untrusted input.    
    - **Scope of required extensions**: Be mindful when marking an extension as
        `required: true` in an Agent Card. This creates a hard dependency for
        all clients and should only be used for extensions fundamental to the
        agent's core function and security (for example, a message signing
        extension).      
    - **Authentication and authorization**: If an extension adds new methods,
        the implementation MUST ensure these methods are subject to the same
        authentication and authorization checks as the core A2A methods. An
        extension MUST NOT provide a way to bypass the agent's primary security
        controls.
