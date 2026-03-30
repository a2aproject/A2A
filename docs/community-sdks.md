# Community SDKs

The A2A community builds and maintains SDKs for languages beyond the [official SDKs](./sdk/index.md). These are independently developed, maintained, and tested by their authors.

## SDK Directory

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
    Open an issue on [a2aproject/A2A](https://github.com/a2aproject/A2A/issues) with a link to your repository and published package. See the [requirements below](#requirements-for-listing).

## Requirements for Listing

Community SDKs should meet these minimum criteria:

- **Spec compliance** — implements core A2A operations (agent card, task send/get/cancel, streaming)
- **Published package** — available on the language's standard registry
- **Documentation** — README with quickstart and API reference
- **Tests** — automated test suite with CI
- **License** — Apache 2.0 (matching the A2A project)
- **Active maintenance** — responsive to issues, tracks spec updates

## Official SDKs

For official A2A SDKs maintained under the `a2aproject` organization, see the [SDK documentation](./sdk/index.md).

## Framework Integrations

For A2A support built into agent frameworks (ADK, LangGraph, CrewAI, etc.), see the [Community Hub](./community.md#a2a-integrations).
