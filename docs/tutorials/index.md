# Get Started with A2A

The A2A protocol is an open standard that enables seamless communication and
collaboration between AI agents. It provides a common language for agents built
using diverse frameworks and by different vendors, fostering interoperability
and breaking down silos. Agents are autonomous problem-solvers that act
independently within their environment. A2A allows agents from different
developers, built on different frameworks, and owned by different organizations
to unite and work together.

## Why Use the A2A Protocol

A2A addresses key challenges in AI agent collaboration. It provides
a standardized approach for agents to interact. This section explains the
problems A2A solves and the benefits it offers.

### Problems that A2A Solves

Consider a user request for an AI assistant to plan an international trip. This
task involves orchestrating multiple specialized agents, such as:

- A flight booking agent
- A hotel reservation agent
- An agent for local tour recommendations
- A currency conversion agent

Without A2A, integrating these diverse agents presents several challenges:

- **Agent Exposure**: Developers often wrap agents as tools to expose them to
    other agents, similar to how tools are exposed in a Multi-agent Control
    Platform (Model Context Protocol). However, this approach is inefficient because agents are
    designed to negotiate directly. Wrapping agents as tools limits their capabilities.
    A2A allows agents to be exposed as they are, without requiring this wrapping.
- **Custom Integrations**: Each interaction requires custom, point-to-point
    solutions, creating significant engineering overhead.
- **Slow Innovation**: Bespoke development for each new integration slows
    innovation.
- **Scalability Issues**: Systems become difficult to scale and maintain as
    the number of agents and interactions grows.
- **Interoperability**: This approach limits interoperability,
    preventing the organic formation of complex AI ecosystems.
- **Security Gaps**: Ad hoc communication often lacks consistent security
    measures.

The A2A protocol addresses these challenges by establishing interoperability for
AI agents to interact reliably and securely.

## How the A2A Protocol Works

A2A defines how independent AI agent systems interact. It provides
a standardized way for agents to communicate and collaborate.

- It utilizes JSON-RPC 2.0 over HTTP(S) for structuring and transmitting messages.
- It allows agents to advertise their capabilities and be found by others through *Agent Cards*.
- It outlines workflows for initiating, progressing, and completing tasks.
- It facilitates the exchange of text, files, and structured data.
- It offers guidelines for secure communication and managing long-running tasks.

## Supported Languages and Code Samples

The A2A Project currently hosts SDKs in four languages (Python, JS, Java, .NET)
and contributors are adding more, including Go.

The following table lists the supported languages and their stability.

| Language   | Support  |
| :--------- | :------- |
| Python     | [Stable](https://github.com/a2aproject/a2a-python) |
| Java       | [Stable](https://github.com/a2aproject/a2a-java)   |
| JavaScript | [Stable](https://github.com/a2aproject/a2a-js)     |
| C#/.NET    | [Stable](https://github.com/a2aproject/a2a-dotnet) |
| Go         | [In Progress](https://github.com/a2aproject/a2a-go)|

The A2A project provides numerous samples across supported languages in the [a2a-samples repository](https://github.com/a2aproject/a2a-samples)

