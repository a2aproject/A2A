# Community SDKs

The A2A community builds and maintains SDKs for languages beyond the [official SDKs](./sdk/index.md). These are independently developed, maintained, and tested by their authors.

## SDK Directory

| Language | Repository | Package | Maintainer | Spec Version |
|----------|-----------|---------|------------|-------------|
| 🦀 Rust | [tomtom215/a2a-rust](https://github.com/tomtom215/a2a-rust) | [`a2a-protocol-sdk`](https://crates.io/crates/a2a-protocol-sdk) | [@tomtom215](https://github.com/tomtom215) | 1.0.0 |
| 💧 Elixir | [zeroasterisk/a2a-elixir](https://github.com/zeroasterisk/a2a-elixir) | [`a2a`](https://hex.pm/packages/a2a) | [@zeroasterisk](https://github.com/zeroasterisk) | 1.0.0 |

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
