# Community SDKs

The A2A community builds and maintains SDKs for languages beyond the [official SDKs](./sdk/index.md). These are independently developed, maintained, and tested by their authors.

## SDK Directory

| Language | Repository | Stars | Package | Spec |
|----------|-----------|-------|---------|------|
| 🦀 Rust | [tomtom215/a2a-rust](https://github.com/tomtom215/a2a-rust) | ![Stars](https://img.shields.io/github/stars/tomtom215/a2a-rust?style=flat-square) | [![Crate](https://img.shields.io/crates/v/a2a-protocol-sdk?style=flat-square)](https://crates.io/crates/a2a-protocol-sdk) | 1.0.0 |
| 🦀 Rust | [EmilLindfors/a2a-rs](https://github.com/EmilLindfors/a2a-rs) | ![Stars](https://img.shields.io/github/stars/EmilLindfors/a2a-rs?style=flat-square) | [![Crate](https://img.shields.io/crates/v/a2a-rs?style=flat-square)](https://crates.io/crates/a2a-rs) | 0.3.0 |
| 🍎 Swift | [tolgaki/a2a-client-swift](https://github.com/tolgaki/a2a-client-swift) | ![Stars](https://img.shields.io/github/stars/tolgaki/a2a-client-swift?style=flat-square) | [SPM v1.0.5](https://github.com/tolgaki/a2a-client-swift) | 1.0.0 |
| 💧 Elixir | [actioncard/a2a-elixir](https://github.com/actioncard/a2a-elixir) | ![Stars](https://img.shields.io/github/stars/actioncard/a2a-elixir?style=flat-square) | [![Hex](https://img.shields.io/hexpm/v/a2a?style=flat-square)](https://hex.pm/packages/a2a) | 0.2.0 |

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
