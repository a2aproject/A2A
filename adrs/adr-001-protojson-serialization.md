# ADR-001: Leverage ProtoJSON Specification for JSON Serialization

**Status:** Accepted

**Date:** 2025-11-18

**Decision Makers:** Technical Steering Committee (TSC)

**Technical Story:** JSON serialization approach for A2A specification

## Context

The A2A specification defines message structures using Protocol Buffers (proto definitions) but also needs to support JSON serialization for HTTP/REST-based communication and JSONRPC payloads. We needed to establish a normative approach for how JSON payloads should be serialized based on the proto definitions referenced by the specification.

Without a clearly specified approach to JSON serialization from proto definitions, implementers could create incompatible JSON representations, leading to interoperability issues across different A2A implementations.

## Decision Drivers

* Need for a standardized, well-documented approach to JSON serialization
* Ability to leverage existing Protocol Buffer tooling
* Clear specification for handling edge cases and type mappings
* Idiomatic use of JSON conventions
* Coupling of specification to tool chain

## Considered Options

* ProtoJSON (canonical JSON encoding for Protocol Buffers)
* Explicit transformation rules defined in the A2A specification

## Decision Outcome

**Chosen option:** "ProtoJSON specification"

The TSC has decided to leverage the ProtoJSON specification as the normative approach to serializing JSON based on the proto definition referenced by the specification. This provides a well-defined, standardized way to convert Protocol Buffer messages to JSON format.

This decision was made with some reservation due to the dependency on ProtoJSON mechanisms and potential impact on protocol bindings unrelated to protobuf and gRPC. However, the decision is reversible if we identify significant issues during implementation, at which point we can duplicate the ProtoJSON conventions in the A2A specification where applicable and describe differences as needed.

### Consequences

#### Positive

* Standardized approach with clear documentation and specification
* Wide ecosystem support with mature libraries across multiple languages
* Consistent behavior across different implementations
* Reduced ambiguity in JSON representation
* Built-in handling for proto3 types and conventions
* Provides well-defined rules for wire-unsafe changes
* Removes the need to define data type handling rules for dates and numbers in the A2A specification

#### Negative

* **Breaking change**: This decision will result in breaking changes to existing JSON payloads, specifically relating to the casing of enum values (ProtoJSON uses SCREAMING_SNAKE_CASE for enums)
* **Loss of roundtrip capability**: We will not be able to roundtrip unknown values because ProtoJSON doesn't support preserving unknown fields in the JSON representation
* Migration effort required for existing implementations
* **Ugly enums** Developers are not used to seeing enum values in SCREAMING_SNAKE_CASE in JSON, which may lead to confusion or errors during implementation
* Changes to the ProtoJSON specification for the benefit of gRPC could have an impact on other protocol bindings.
* Enums require a "unspecified" value even when they are only used for required fields to meet Proto best practices.
* Certain field names need to have less than optimal names to avoid conflicts with proto keywords. e.g. message.

#### Neutral

* Implementations must follow ProtoJSON specification strictly
* Documentation must clearly communicate the breaking changes

## References

* [ProtoJSON format](https://protobuf.dev/programming-guides/json/)

## Notes

This decision was made to ensure long-term interoperability and maintainability of the A2A specification. While it introduces breaking changes in the short term, the benefits of standardization and ecosystem alignment outweigh the migration costs.

Implementers should be aware that the enum casing change is the most visible breaking change and should plan accordingly for version transitions.
