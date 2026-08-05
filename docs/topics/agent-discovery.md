# Agent Discovery in A2A

To collaborate using the Agent2Agent (A2A) protocol, AI agents need to first find each other and understand their capabilities. A2A standardizes agent self-descriptions through the **[Agent Card](../specification.md#5-agent-discovery-the-agent-card)**. However, discovery methods for these Agent Cards vary by environment and requirements. The Agent Card defines what an agent offers. Various strategies exist for a client agent to discover these cards. The choice of strategy depends on the deployment environment and security requirements.

## The Role of the Agent Card

The Agent Card is a JSON document that serves as a digital "business card" for an A2A Server (the remote agent). It is crucial for agent discovery and interaction. The key information included in an Agent Card is as follows:

- **Identity:** Includes `name`, `description`, and `provider` information.
- **Service Endpoint:** Specifies the `url` for the A2A service.
- **A2A Capabilities:** Lists supported features such as `streaming` or `pushNotifications`.
- **Authentication:** Details the required `schemes` (e.g., "Bearer", "OAuth2").
- **Skills:** Describes the agent's tasks using `AgentSkill` objects, including `id`, `name`, `description`, `inputModes`, `outputModes`, and `examples`.

Client agents use the Agent Card to determine an agent's suitability, structure requests, and ensure secure communication.

## Discovery Strategies

The following sections detail common strategies used by client agents to discover remote Agent Cards:

### 1. Well-Known URI

This approach is recommended for public agents or agents intended for broad discovery within a specific domain.

- **Mechanism:** A2A Servers make their Agent Card discoverable by hosting it at a standardized, `well-known` URI on their domain. The standard path is `https://{agent-server-domain}/.well-known/agent-card.json`, following the principles of [RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615).

- **Process:**
    1. A client agent knows or programmatically discovers the domain of a potential A2A Server (e.g., `smart-thermostat.example.com`).
    2. The client performs an HTTP GET request to `https://smart-thermostat.example.com/.well-known/agent-card.json`.
    3. If the Agent Card exists and is accessible, the server returns it as a JSON response.

- **Advantages:**
    - Ease of implementation
    - Adheres to standards
    - Facilitates automated discovery

- **Considerations:**
    - Best suited for open or domain-controlled discovery scenarios.
    - Authentication is necessary at the endpoint serving the Agent Card if it contains sensitive details.

### 2. Curated Registries (Catalog-Based Discovery)

This approach is employed in enterprise environments or public marketplaces, where Agent Cards are often managed by a central registry. The curated registry acts as a central repository, allowing clients to query and discover agents based on criteria like "skills" or "tags".

- **Mechanism:** An intermediary service (the registry) maintains a collection of Agent Cards. Clients query this registry to find agents based on various criteria (e.g., skills offered, tags, provider name, capabilities).

- **Process:**
    1. A2A Servers publish their Agent Cards to the registry.
    2. Client agents query the registry's API, and search by criteria such as "specific skills".
    3. The registry returns matching Agent Cards or references.

- **Advantages:**
    - Centralized management and governance.
    - Capability-based discovery (e.g., by skill).
    - Support for access controls and trust frameworks.
    - Applicable in both private and public marketplaces.
- **Considerations:**
    - Requires deployment and maintenance of a registry service.
    - The current A2A specification does not prescribe a standard API for curated registries.

### 3. Direct Configuration / Private Discovery

This approach is used for tightly coupled systems, private agents, or development purposes, where clients are directly configured with Agent Card information or URLs.

- **Mechanism:** Client applications utilize hardcoded details, configuration files, environment variables, or proprietary APIs for discovery.
- **Process:** The process is specific to the application's deployment and configuration strategy.
- **Advantages:** This method is straightforward for establishing connections within known, static relationships.
- **Considerations:**
    - Inflexible for dynamic discovery scenarios.
    - Changes to Agent Card information necessitate client reconfiguration.
    - Proprietary API-based discovery also lacks standardization.

## Securing Agent Cards

Agent Cards include sensitive information, such as:

- URLs for internal or restricted agents.
- Descriptions of sensitive skills.

### Protection Mechanisms

To mitigate risks, the following protection mechanisms should be considered:

- **Authenticated Agent Cards:** We recommend the use of [authenticated extended agent cards](../specification.md#3111-get-extended-agent-card) for sensitive information or for serving a more detailed version of the card.
- **Secure Endpoints:** Implement access controls on the HTTP endpoint serving the Agent Card (e.g., `/.well-known/agent-card.json` or registry API). The methods include:
    - Mutual TLS (mTLS)
    - Network restrictions (e.g., IP ranges)
    - HTTP Authentication (e.g., OAuth 2.0)

- **Registry Selective Disclosure:** Registries return different Agent Cards based on the client's identity and permissions.

Any Agent Card containing sensitive data must be protected with authentication and authorization mechanisms. The A2A specification strongly recommends the use of out-of-band dynamic credentials rather than embedding static secrets within the Agent Card.

## Verifying Agent Identity

Discovery and security tell a client *where* an agent is and *how* to authenticate the connection. They do not answer a different question: *is this agent runtime legitimate?*

Transport-layer mechanisms (TLS, OAuth, mTLS) verify the server's domain identity, but they do not provide cryptographic proof of the agent's own identity, its registration status within a trust framework, or whether its credentials have been revoked. In open agent ecosystems where agents from different organizations interact, clients may need to verify these properties before routing a task.

### The Identity Verification Gap

A2A's current security model establishes trust at the transport layer: TLS verifies the server certificate, and OAuth/OpenID Connect handles authorization. This is sufficient when both agents operate within the same trust boundary (for example, agents within a single enterprise). However, when agents operate across organizational boundaries, additional verification questions arise:

- Is this agent's runtime registered with a trusted authority?
- Has this agent's identity been revoked or suspended?
- Can the agent's public key be resolved to a verifiable decentralized identifier (DID)?
- Was this agent authorized to act on behalf of a specific principal, and within what scope?

These are identity verification questions, distinct from the authorization questions that OAuth answers.

### Ecosystem Approaches

The agent identity ecosystem is actively developing open protocols to address this gap. Several approaches are emerging that complement A2A's existing security model:

#### Trust Registries

Federated trust registries maintain cryptographically signed lists of verified agent runtimes. A client discovering an Agent Card can optionally verify the agent's runtime against such a registry before establishing communication. This verification can be performed locally against a cached registry manifest, without requiring network calls at verification time.

Example open-source implementations include the [Open Agent Trust Registry](https://github.com/FransDevelopment/open-agent-trust-registry) (OATR), which provides permissionless registration via Ed25519 proof-of-key-ownership, domain verification, and a [14-step local verification protocol](https://github.com/FransDevelopment/open-agent-trust-registry/blob/main/spec/03-verification.md) using JWS ([RFC 7515](https://tools.ietf.org/html/rfc7515)) attestations with JSON canonicalization ([RFC 8785](https://tools.ietf.org/html/rfc8785)), the same primitives A2A uses for [Agent Card Signing](../specification.md#84-agent-card-signing).

#### Decentralized Identifiers (DIDs)

[W3C Decentralized Identifiers](https://www.w3.org/TR/did-core/) (DIDs) provide a standard way to resolve an agent's identity to a cryptographic public key without depending on a central identity provider. DID methods such as `did:web` (resolved via `/.well-known/did.json`) and `did:key` (self-contained in the identifier) allow agents to advertise verifiable identities that can be independently resolved.

An [Agent Identity Working Group](https://github.com/corpollc/qntm/issues/5) comprising multiple independent projects has ratified three specs for DID-based agent identity: [DID Resolution v1.0](https://github.com/corpollc/qntm/blob/main/specs/working-group/did-resolution.md), [Entity Verification v1.0](https://github.com/corpollc/qntm/blob/main/specs/working-group/entity-verification.md), and [QSP-1 v1.0](https://github.com/corpollc/qntm/blob/main/specs/working-group/qsp1-envelope.md) (encrypted transport). Cross-implementation [test vectors](https://github.com/corpollc/qntm/tree/main/specs/test-vectors) are available.

#### Capability Discovery

Separate from the Agent Card, capability manifests such as [agent.json](https://github.com/FransDevelopment/agent-json) (hosted at `/.well-known/agent.json`) can declare structured capabilities alongside identity metadata including DIDs and public keys. Because A2A Agent Cards (`/.well-known/agent-card.json`) and capability manifests (`/.well-known/agent.json`) use different well-known paths, they can coexist on the same domain without conflict, allowing services to serve both formats for different consumers.

### Composing Identity Verification with A2A

Identity verification is designed to complement, not replace, A2A's existing security model. A typical verification flow alongside A2A:

1. **Discover** the Agent Card via `/.well-known/agent-card.json` (standard A2A)
2. **Authenticate** using the Agent Card's declared security schemes (OAuth, API key, mTLS)
3. **Optionally verify** the agent's runtime identity against a trust registry or DID resolution
4. **Route the task** only if both authentication and identity verification succeed

Steps 1-2 are existing A2A behavior. Steps 3-4 add an optional identity verification layer that services can adopt incrementally based on their trust requirements.

For a comprehensive treatment of composable trust architecture for agent identity, see [Moore, 2026](https://zenodo.org/records/19263547).

## Caching Considerations

Agent Cards describe an agent's capabilities and typically change infrequently — for example, when skills are added or authentication requirements are updated. Applying standard HTTP caching practices to Agent Card endpoints reduces unnecessary network requests while ensuring clients eventually receive updated information.

### Server Guidance

Servers hosting Agent Card endpoints should include HTTP caching headers in their responses. The `Cache-Control` header with an appropriate `max-age` directive allows clients and intermediaries to cache the card for a specified duration. Including an `ETag` header — derived from the card's `version` field or a content hash — enables clients to make conditional requests and avoid re-downloading unchanged cards.

### Client Guidance

Clients fetching Agent Cards should honor standard HTTP caching semantics. When a cached card expires, clients should use conditional requests (for example, `If-None-Match` with the stored `ETag` or `If-Modified-Since`) rather than unconditionally re-fetching the full card. When the server does not provide caching headers, clients may apply a reasonable default cache duration.

For Extended Agent Cards, clients should also follow the session-scoped caching guidance described in the [specification](../specification.md#133-extended-agent-card-access-control).

For normative requirements, see [Section 8.6](../specification.md#86-caching) of the specification.

## Future Considerations

The A2A community is exploring several areas for standardization:

- **Registry interactions**: Standardizing APIs for curated registries, including trust registries that provide cryptographic verification of agent identity beyond transport-layer authentication.
- **Advanced discovery protocols**: Combining capability discovery with identity verification so that agents can assess both *what* a remote agent offers and *whether* it is a verified participant in a trust framework.
- **Delegation and authorization chains**: Formalizing how delegation proofs propagate through multi-hop agent interactions, enabling agents to verify not only who they are communicating with but what authority that agent has been granted.
