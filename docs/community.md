# A2A Community Hub

Welcome to the official community hub for the **Agent2Agent (A2A) protocol**! A2A is an open, standardized protocol that enables seamless interoperability and collaboration between AI agents across all frameworks and vendors.

---

## Recent News & Blog Posts

Stay up-to-date with the latest announcements, tutorials, and insights from the A2A team and our community.

- **[Announcing Agent Payments Protocol (AP2)](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agent-payments-protocol-ap2)** - *September 16*
- **[A2A Extensions Empowering Custom Agent Functionality](https://developers.googleblog.com/en/a2a-extensions-empowering-custom-agent-functionality/)** - *September 9*
- **[A2A protocol: Demystifying Tasks vs Messages](https://discuss.google.dev/t/a2a-protocol-demystifying-tasks-vs-messages/255879)** - *August 18*
- **[End-to-end evaluation of multi-agent systems on Vertex AI](https://discuss.google.dev/t/end-to-end-evaluation-of-multi-agent-systems-on-vertex-ai-with-cloud-run-deployment-for-a2a-agents/250552)** - *August 7*
- **[Agent2Agent (A2A) protocol is getting an upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade?e=48754805)** - *July 26*

---

## Use Case Highlights

A2A unlocks powerful new ways for AI agents to collaborate and solve complex problems. Here are a few examples of what's possible:

- **Multi-Agent Workflows:** Chain specialized agents together to automate complex processes, like candidate sourcing for hiring or streamlining supply chain logistics.
- **Agent Marketplaces:** Create platforms where agents can discover and utilize the capabilities of other agents from different providers.
- **Cross-Platform Integration:** Connect agents built on different frameworks—like LangGraph, BeeAI, and more—to work together seamlessly.
- **Evaluating Multi-Agent Systems:** Use frameworks like Vertex AI to assess the performance and success of collaborative agent trajectories.

---

## Community Spotlight

### Featured Contributions

A2A is an open-source protocol, and we thrive on community contributions. A huge thank you to everyone who has helped build and improve A2A! Here are some recent highlights:

- [Python Quickstart Tutorial (PR#202)](https://github.com/a2aproject/A2A/pull/202)
- [LlamaIndex sample implementation (PR#179)](https://github.com/a2aproject/A2A/pull/179)
- [Autogen sample server (PR#232)](https://github.com/a2aproject/A2A/pull/232)
- [AG2 + MCP example (PR#230)](https://github.com/a2aproject/A2A/pull/230)
- [PydanticAI example (PR#127)](https://github.com/a2aproject/A2A/pull/127)

### The Word on the Street

The launch of A2A has sparked lively discussions and positive reactions across various social and video platforms.

- **Microsoft's Semantic Kernel:** Asha Sharma, Head of AI Platform Product at Microsoft, [announced on LinkedIn](https://www.linkedin.com/posts/aboutasha_a2a-ugcPost-7318649411704602624-0C_8) that "Semantic Kernel now speaks A2A," enabling instant, secure interoperability.
- **Matt Pocock's Diagramming:** Well-known developer educator Matt Pocock [shared diagrams on X](https://x.com/mattpocockuk/status/1910002033018421400) explaining the A2A protocol, which were liked and reposted hundreds of times.
- **Craig McLuckie's "Hot Take":** Craig McLuckie shared his thoughts on [LinkedIn](https://www.linkedin.com/posts/craigmcluckie_hot-take-on-agent2agent-vs-mcp-google-just-activity-7315939233792176128-4rGQ), highlighting A2A's focus on interactions *between* agentic systems as a sensible approach.
- **Zachary Huang's Deep Dive:** In his [YouTube video](https://www.youtube.com/watch?v=wrCF8MoXC_I), Zachary explains how A2A complements MCP, with A2A handling communication between agents and MCP connecting agents to tools.

---

## A2A Integrations

These agentic frameworks have built-in A2A integration, making it easy to get started:

- [Agent Development Kit (ADK)](https://google.github.io/adk-docs/a2a/)
- [Agno](https://docs.agno.com/agent-os/interfaces/a2a/introduction)
- [AG2](https://docs.ag2.ai/latest/docs/user-guide/a2a/)
- [BeeAI Framework](https://framework.beeai.dev/integrations/a2a)
- [CrewAI](https://docs.crewai.com/en/learn/a2a-agent-delegation)
- [Hector](https://github.com/kadirpekel/hector)
- [LangGraph](https://docs.langchain.com/langsmith/server-a2a)
- [LiteLLM](https://docs.litellm.ai/docs/a2a)
- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/a2a-agent)
- [Pydantic AI](https://ai.pydantic.dev/a2a/)
- [Slide (Tyler)](https://slide.mintlify.app/guides/a2a-integration)
- [Strands Agents](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/)

## Community SDKs

Building an A2A agent in a language not covered by the [official SDKs](./sdk/index.md)? These community-maintained implementations have you covered.

### 🦀 Rust — a2a-rust

![Stars](https://img.shields.io/github/stars/tomtom215/a2a-rust?style=flat-square) [![Crate](https://img.shields.io/crates/v/a2a-protocol-sdk?style=flat-square)](https://crates.io/crates/a2a-protocol-sdk)

[tomtom215/a2a-rust](https://github.com/tomtom215/a2a-rust) · A2A spec v1.0.0 · Full SDK with JSON-RPC, REST, WebSocket, and gRPC transports.

### 🦀 Rust — a2a-rs

![Stars](https://img.shields.io/github/stars/EmilLindfors/a2a-rs?style=flat-square) [![Crate](https://img.shields.io/crates/v/a2a-rs?style=flat-square)](https://crates.io/crates/a2a-rs)

[EmilLindfors/a2a-rs](https://github.com/EmilLindfors/a2a-rs) · A2A spec v0.3.0 · Modular workspace with core protocol, AP2 extension, and agent framework.

### 🍎 Swift — A2AClient

![Stars](https://img.shields.io/github/stars/tolgaki/a2a-client-swift?style=flat-square)

[tolgaki/a2a-client-swift](https://github.com/tolgaki/a2a-client-swift) · A2A spec v1.0.0 · Swift Package Manager. iOS 15+, macOS 12+, watchOS 8+, tvOS 15+.

### 💧 Elixir — a2a

![Stars](https://img.shields.io/github/stars/actioncard/a2a-elixir?style=flat-square) [![Hex](https://img.shields.io/hexpm/v/a2a?style=flat-square)](https://hex.pm/packages/a2a)

[actioncard/a2a-elixir](https://github.com/actioncard/a2a-elixir) · A2A spec v0.2.0 · OTP-native with Agent behaviour, TaskStore, and supervision tree.

!!! tip "Want to add your SDK?"
    Open an issue on [a2aproject/A2A](https://github.com/a2aproject/A2A/issues/new?title=Community%20SDK%20Submission) with a link to your repository and published package.

**Requirements:** Spec compliance, published package on standard registry, documentation, tests with CI, Apache 2.0 license, and active maintenance.

## The Future is Interoperable

The excitement surrounding Google's A2A protocol clearly indicates a strong belief in its potential to revolutionize multi-agent AI systems. By providing a standardized way for AI agents to communicate and collaborate, A2A is poised to unlock new levels of automation and innovation. As enterprises increasingly adopt AI agents, A2A represents a crucial step towards realizing the full power of interconnected AI ecosystems.

**Join the growing community building the future of AI interoperability with A2A!**
