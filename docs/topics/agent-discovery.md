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

### 1. Well-Known URI (`/.well-known/agent-card.json`)

A simple option for single-agent deployments. The Agent Card is served at a fixed path on the domain, following [RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615).

- **Mechanism:** The A2A Server hosts its Agent Card at `https://{agent-server-domain}/.well-known/agent-card.json`. A client that knows the domain can retrieve it with a single HTTP GET.

- **Process:**
    1. A client knows the domain of the A2A Server (e.g., `smart-thermostat.example.com`).
    2. The client performs an HTTP GET to `https://smart-thermostat.example.com/.well-known/agent-card.json`.
    3. If accessible, the server returns the Agent Card as a JSON response.

- **Advantages:**
    - Minimal setup — one static file or route.
    - Adheres to well-known URI standards.

- **Limitations:**
    - **One Agent Card per domain.** A domain can only advertise a single agent via this path. It does not work for multi-agent or multi-tenant deployments where multiple agents share a domain.
    - Not suitable when different clients should see different sets of agents.

    For deployments with more than one agent, or where per-client visibility is needed, use [AI Catalog discovery](#2-ai-catalog-discovery-well-knownaicatalogjson-preferred) instead.

### 2. AI Catalog Discovery (`/.well-known/ai-catalog.json`) — Preferred

This is the recommended approach for public agents. It supports single-agent deployments, multi-agent hosts, multi-tenant scenarios, and authenticated per-client catalogs — use cases where a single fixed URI is insufficient.

- **Mechanism:** Hosts publish an [AI Catalog](https://ai-catalog.io/) document listing one or more Agent Cards as entries. Each entry either references the Agent Card via a `url` field or embeds it inline via a `data` field. Clients fetch the catalog first, then retrieve any referenced Agent Cards as needed. The conventional unauthenticated location is `/.well-known/ai-catalog.json` (following [RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615)), but the catalog can be served from any URL — for example, an authenticated endpoint that returns only the agents a specific caller is permitted to see.

- **Process:**
    1. A client knows or discovers the catalog URL — either by convention (`https://{domain}/.well-known/ai-catalog.json`) or via out-of-band configuration (documentation, a registry, or an authenticated endpoint).
    2. The client performs an HTTP GET to that catalog URL, supplying credentials if the endpoint requires them.
    3. The catalog returns an array of entries. The client selects the relevant entry (or entries). If the entry has a `url`, the client fetches the Agent Card from that URL. If the entry has a `data` field, the Agent Card is already present inline — no further fetch needed.

- **Example catalog (single agent, referenced by URL):**

    ```json
    {
      "specVersion": "1.0",
      "host": {
        "displayName": "Example Corp",
        "identifier": "did:web:agents.example.com"
      },
      "entries": [
        {
          "identifier": "urn:air:agents.example.com:a2a:assistant",
          "type": "application/a2a-agent-card+json",
          "url": "https://agents.example.com/assistant/agent-card.json"
        }
      ]
    }
    ```

- **Example catalog (single agent, embedded inline):**

    Each entry uses either `url` or `data` — not both. Use `data` to embed the Agent Card directly in the catalog, avoiding a second HTTP fetch. This is convenient when you have a single agent and do not want to host the Agent Card at a separate URL.

    ```json
    {
      "specVersion": "1.0",
      "host": {
        "displayName": "Example Corp",
        "identifier": "did:web:agents.example.com"
      },
      "entries": [
        {
          "identifier": "urn:air:agents.example.com:a2a:assistant",
          "type": "application/a2a-agent-card+json",
          "data": {
            "name": "Assistant Agent",
            "description": "General purpose assistant.",
            "version": "1.0.0",
            "url": "https://agents.example.com/assistant",
            "supportedInterfaces": [
              {
                "url": "https://agents.example.com/assistant",
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0"
              }
            ],
            "skills": []
          }
        }
      ]
    }
    ```

- **Example catalog (multiple agents or tenants):**

    ```json
    {
      "specVersion": "1.0",
      "host": {
        "displayName": "Example Corp",
        "identifier": "did:web:agents.example.com"
      },
      "entries": [
        {
          "identifier": "urn:air:agents.example.com:a2a:assistant",
          "type": "application/a2a-agent-card+json",
          "url": "https://agents.example.com/assistant/agent-card.json"
        },
        {
          "identifier": "urn:air:agents.example.com:a2a:analytics",
          "type": "application/a2a-agent-card+json",
          "url": "https://agents.example.com/analytics/agent-card.json"
        }
      ]
    }
    ```

- **Advantages:**
    - Supports multiple agents and tenants under a single domain.
    - Interoperable with other AI artifact types (e.g., MCP servers, nested catalogs).
    - Adheres to the open [AI Catalog](https://ai-catalog.io/) standard.
    - Facilitates automated discovery.

- **Considerations:**
    - Agent Card URLs in the catalog can be any path; hosts choose the layout.
    - Authentication should be applied to individual Agent Card endpoints for cards containing sensitive information.

### 4. Curated Registries (Catalog-Based Discovery)

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

### 5. Direct Configuration / Private Discovery

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
- **Secure Endpoints:** Implement access controls on the HTTP endpoint serving the Agent Card (e.g., the URL listed in the AI Catalog entry, or a registry API). The methods include:
    - Mutual TLS (mTLS)
    - Network restrictions (e.g., IP ranges)
    - HTTP Authentication (e.g., OAuth 2.0)

- **Registry Selective Disclosure:** Registries return different Agent Cards based on the client's identity and permissions.

Any Agent Card containing sensitive data must be protected with authentication and authorization mechanisms. The A2A specification strongly recommends the use of out-of-band dynamic credentials rather than embedding static secrets within the Agent Card.

## Caching Considerations

Agent Cards describe an agent's capabilities and typically change infrequently — for example, when skills are added or authentication requirements are updated. Applying standard HTTP caching practices to Agent Card endpoints reduces unnecessary network requests while ensuring clients eventually receive updated information.

### Server Guidance

Servers hosting Agent Card endpoints should include HTTP caching headers in their responses. The `Cache-Control` header with an appropriate `max-age` directive allows clients and intermediaries to cache the card for a specified duration. Including an `ETag` header — derived from the card's `version` field or a content hash — enables clients to make conditional requests and avoid re-downloading unchanged cards.

### Client Guidance

Clients fetching Agent Cards should honor standard HTTP caching semantics. When a cached card expires, clients should use conditional requests (for example, `If-None-Match` with the stored `ETag` or `If-Modified-Since`) rather than unconditionally re-fetching the full card. When the server does not provide caching headers, clients may apply a reasonable default cache duration.

For Extended Agent Cards, clients should also follow the session-scoped caching guidance described in the [specification](../specification.md#133-extended-agent-card-access-control).

For normative requirements, see [Section 8.6](../specification.md#86-caching) of the specification.

## Future Considerations

The A2A community explores standardizing registry interactions or advanced discovery protocols.
