# Multi-Tenancy and Multi-Agent Routing

A single A2A endpoint can serve multiple agents or tenants. The A2A protocol
does not prescribe a specific routing implementation — operators are free to
choose the approach that best fits their infrastructure. This document describes
the routing mechanisms the protocol supports and the rules clients must follow
when a routing identifier is advertised in an Agent Card.

## Overview

A common deployment pattern is to place several agents behind a single host or
reverse-proxy. From the outside the agents are reachable at the same base URL,
but each individual agent needs to be distinguished so that requests are
delivered to the right backend.

Three complementary approaches are available:

### 1. URL-Based Routing (Sub-Path)

Each agent is assigned a distinct URL prefix. The Agent Card for each agent
advertises its own `url` in `supportedInterfaces`, so clients automatically
send requests to the correct path.

```json
// Agent Card for the "billing" agent
{
  "name": "Billing Agent",
  "supportedInterfaces": [
    {
      "url": "https://agents.example.com/billing",
      "protocolBinding": "HTTP+JSON",
      "protocolVersion": "1.0"
    }
  ]
}
```

```json
// Agent Card for the "support" agent
{
  "name": "Support Agent",
  "supportedInterfaces": [
    {
      "url": "https://agents.example.com/support",
      "protocolBinding": "HTTP+JSON",
      "protocolVersion": "1.0"
    }
  ]
}
```

The gateway or reverse-proxy routes `/billing/*` and `/support/*` to the
appropriate backend without any changes to the A2A protocol messages themselves.
This is the simplest approach and requires no special client awareness beyond
reading the Agent Card.

### 2. Header-Based Routing

When sub-paths are not convenient (for example, when all agents share the same
base URL), the gateway can route on a custom HTTP header or on the contents of
the standard `Authorization` header.

Examples:

- A bearer token whose claims identify the target agent or organisation.
- An API key that maps to a particular tenant in the gateway's configuration.
- A proprietary header such as `X-Agent-ID: billing`.

Header-based routing is transparent to the A2A protocol — the agent's
`supportedInterfaces` entries declare the same URL for each agent, and the
gateway resolves the target based on the header value. Authentication headers
are already declared in the Agent Card's `securitySchemes` and `security`
fields; custom routing headers can be documented as an extension or as
operator-specific configuration.

### 3. Body-Based Routing Using the `tenant` Field

Every A2A request message contains an optional `tenant` field. This is an
**opaque string** whose value is defined entirely by the server operator; the
protocol does not impose any format or semantics on it. A gateway or agent
implementation can inspect this field and forward the request to the appropriate
backend.

The `tenant` value that a client should use for a particular agent is advertised
in the `AgentInterface` entry inside `supportedInterfaces`:

```json
{
  "name": "Billing Agent",
  "supportedInterfaces": [
    {
      "url": "https://agents.example.com/a2a",
      "protocolBinding": "HTTP+JSON",
      "protocolVersion": "1.0",
      "tenant": "billing"
    }
  ]
}
```

**Client requirement**: If a selected `AgentInterface` entry has a non-empty
`tenant` field, the client **MUST** include that value in the `tenant` field of
every request message body sent to that interface. See
[Section 8.3.2](../specification.md#832-client-protocol-selection) of the
specification for the normative rule.

A server MAY use the `tenant` field to represent any routing key that suits its
deployment — agent identifiers, workspace slugs, organisation IDs, or any other
opaque discriminator.

## Combining Approaches

The three approaches are not mutually exclusive. For example, a deployment could
use URL-based routing to distinguish between major product lines and rely on the
`tenant` field to distinguish individual customers within each product line. The
appropriate combination depends on the operator's architecture and the
capabilities of the gateway in use.

## Discovering Multiple Agents

When multiple agents are deployed behind a shared host, each agent **SHOULD**
have its own Agent Card published at an appropriate location (see
[Agent Discovery](./agent-discovery.md)). Clients retrieve each agent's card
independently and use the `supportedInterfaces` information it contains — including
any `tenant` value — to communicate with the correct agent.
