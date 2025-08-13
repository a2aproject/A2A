# Agent Discovery in A2A

To collaborate using the Agent2Agent (A2A) protocol, AI agents must first find each other and understand their capabilities. A2A standardizes agent self-descriptions through the **[Agent Card](../specification.md#5-agent-discovery-the-agent-card)**. However, discovery methods for these Agent Cards vary by environment and requirements.

## The Role of the Agent Card

The Agent Card is a JSON document, a digital "business card" for an A2A Server (the remote agent). It's crucial for discovery and interaction. Key information includes:

- **Identity:** `name`, `description`, `provider` information.
- **Service endpoint:** The `url` for the A2A service.
- **A2A capabilities:** Supported features like `streaming` or `pushNotifications`.
- **Authentication:** Required `schemes` (e.g., "Bearer", "OAuth2").
- **Skills:** Agent's tasks (`AgentSkill` objects) with `id`, `name`, `description`, `inputModes`, `outputModes`, and `examples`.

Client agents use the Agent Card to determine suitability, structure requests, and ensure secure communication.

## Discovery Strategies

Here are common strategies for client agents to discover remote agent Agent Cards:

### 1. Well-Known URI

Recommended for public agents or those for broad discoverability within a domain.

- **Mechanism:** A2A Servers host Agent Cards at a standardized, "well-known" path.
- **Standard Path:** `https://{agent-server-domain}/.well-known/agent-card.json` ([RFC 8615](https://www.ietf.org/rfc/rfc8615.txt)).
- **Process:** 
    1. Client agents find a potential A2A Server's domain (e.g., `smart-thermostat.example.com`).
    2. The client sends an HTTP `GET` to `https://smart-thermostat.example.com/.well-known/agent-card.json`.
    3. The server returns the Agent Card as JSON if accessible.
- **Advantages:** Simple, standardized, and enables automated discovery.
- **Considerations:** Best for open or domain-controlled discovery. The endpoint may require authentication for sensitive cards.

### 2. Curated Registries (Catalog-Based Discovery)

For enterprise environments or marketplaces, Agent Cards are published to a central registry.

- **Mechanism:** A registry maintains Agent Cards. Clients query it based on criteria (e.g., skills, tags).
- **Process:**
    1. A2A Servers register Agent Cards with the registry.
    2. Client agents query the registry's API (e.g., "find agents with 'image-generation' skill").
    3. The registry returns matching Agent Cards or references.
- **Advantages:**
    - Centralized management and governance.
    - Discovery by capabilities, not just domain names.
    - Access controls and trust mechanisms.
    - Company-specific or public marketplaces.
- **Considerations:** Requires a registry service. A2A doesn't define a standard API for registries.

### 3. Direct Configuration / Private Discovery

For tightly coupled systems, private agents, or development, clients may be directly configured with Agent Card information or URLs.

- **Mechanism:** Client applications use hardcoded details, config files, environment variables, or private APIs.
- **Process:** Application-specific.
- **Advantages:** Simple for known, static relationships.
- **Considerations:** Inflexible for dynamic discovery. Changes may require client reconfiguration. Proprietary API-based discovery is not standardized.

## Securing Agent Cards

Agent Cards may contain protected information, such as:

-   The `url` of an internal or restricted agent. 
-   `authentication.credentials` details (e.g., OAuth token URL). **Do not** store secrets in Agent Cards. 
-   Descriptions of sensitive skills.

**Protection Mechanisms:**

- **Endpoint access control:** Secure the HTTP endpoint serving the Agent Card (e.g., `/.well-known/agent-card.json`, registry API) if not for public access.
    -   **mTLS:** Require mutual TLS. 
    -   **Network restrictions:** Limit to specific IP ranges or networks. 
    -   **Authentication:** Require HTTP authentication (e.g., OAuth 2.0). 
- **Selective disclosure by registries:** Registries can return different cards based on client identity and permissions.

If an Agent Card contains sensitive data (**not recommended** for secrets), it **must** be protected with strong authentication and authorization. A2A encourages out-of-band dynamic credentials, not static secrets in the Agent Card.

## Future Considerations

The A2A community may explore standardizing registry interactions or advanced discovery protocols. Feedback is welcome to enhance A2A agent discoverability and interoperability.
