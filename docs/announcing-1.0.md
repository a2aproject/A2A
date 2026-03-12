# A2A Protocol Ships v1.0: Production-Ready Standard for Agent-to-Agent Communication

The A2A Protocol community today are announcing the release of A2A Protocol v1.0, marking the first stable, production-ready version of the open standard for communication between AI agents. The protocol is guided by a technical steering committee with representatives from eight major technology companies.

As organizations build increasingly sophisticated multi-agent systems, interoperability has become the defining challenge. Teams can coordinate agents effectively within a single platform, but connecting those systems across technology stacks and organizational boundaries remains difficult. A2A addresses that challenge by combining support for multiple protocol bindings, seamless version negotiation, and a common semantic model so agents can interoperate across systems with predictable behavior.

The v1.0 release emphasizes maturity rather than reinvention: the core ideas remain intact, while rough edges have been removed, ambiguous areas clarified, and enterprise deployment requirements addressed more directly.

## Delivering on enterprise requirements

The v1.0 release introduces several capabilities aimed at production environments where trust, scale, and operational control are non-negotiable.

- **Heterogeneous environment support** enables interoperability across diverse technology stacks through multi-protocol bindings and version negotiation, so enterprises are not tied to a single vendor or platform.
- **Multi-tenancy support** allows a single endpoint to securely host many agents.
- **Signed Agent Cards** provide cryptographic verification of agent identity and metadata, establishing trust before interaction across organizational boundaries.
- **Improved security posture** modernizes security flows and removes legacy patterns that are no longer aligned with current best practices.

Together, these changes move A2A from early adopter implementations toward broader enterprise confidence, especially in regulated or multi-party scenarios.

## Web-aligned architecture for scale

A2A v1.0 aligns with core architectural principles of the web: stateless, layered architecture, standard protocol bindings, and infrastructure-friendly communication patterns. That alignment matters operationally because organizations can scale agent interactions with the same proven load balancing, gateway, security and observability patterns they already use for web systems.

The standard builds on industry-proven protocols, including JSON+HTTP, gRPC, and JSON-RPC. It also keeps the barrier to entry low: in its simplest form, an A2A interaction can begin with a single HTTP request.

A2A also gives consumers flexibility in how they receive results. Depending on workload and operational needs, clients can use polling, streaming, or webhooks to consume task updates and responses.

## Complementary to MCP, not a replacement

The release also reinforces A2A's relationship with the Model Context Protocol (MCP), a point that has generated confusion in early ecosystem discussions.

MCP and A2A solve different layers of the problem. MCP is commonly used for tool and context integration at the individual agent level. A2A focuses on communication and coordination between agents. In practice, many systems will use both: MCP inside agents, A2A between agents.

## Smooth migration from earlier versions

The v1.0 release tightens specification behavior, which includes breaking changes in the interaction protocol. AgentCard, however, has evolved in a backward-compatible way and now allows agents to advertise support for both existing v0.3 protocol behavior and v1.0 simultaneously. This enables clients to migrate progressively rather than through a single cutover.

That approach is intended to protect current investments while still delivering the benefits of a cleaner, more durable standard.

## Why this release matters now

AI agents are increasingly deployed across departments, products, and partner ecosystems. At that scale, the key question is no longer whether agents can coordinate within one stack, but whether they can collaborate reliably across organizational and platform boundaries. Open protocols determine whether organizations can compose best-of-breed systems or become locked into isolated stacks.

A2A v1.0 gives the market a stronger foundation for open multi-agent collaboration. The community is now focused on delivering multi-language v1.0 SDK support to help developers build conformant solutions with ease.

The complete v1.0 materials, including specification and migration documentation, are available at [a2a-protocol.org](https://a2a-protocol.org) and on [GitHub](https://github.com/a2aproject/A2A).

---

**About A2A Protocol**
The Agent-to-Agent (A2A) Protocol is an open standard that enables AI agents to discover capabilities, communicate, and delegate tasks across teams, products, and organizations. The A2A Technical Steering Committee includes representatives from AWS, Cisco, Google, IBM Research, Microsoft, Salesforce, SAP, and ServiceNow.

**Media Contact**
A2A Protocol Community
[https://a2a-protocol.org](https://a2a-protocol.org)
