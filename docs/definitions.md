# A2A Definition/Schema

=== "Protobuf"
    <h3>Protobuf</h3>
    The normative A2A protocol definition in Protocol Buffers (proto3 syntax).
    This is the source of truth for the A2A protocol specification.

    <h3>Download</h3>

    You can download the proto file directly: [`a2a.proto`](spec/a2a.proto)

    <h3>Definition</h3>

    ```protobuf
    --8<-- "docs/spec/a2a.proto"
    ```

=== "JSON"
    <h3>JSON</h3>
    The A2A protocol JSON Schema definition (JSON Schema 2020-12 compliant).
    This schema is automatically generated from the protocol buffer definitions and bundled into a single file with all message definitions.

    <h3>Download</h3>

    You can download the version-specific schema file directly: [`a2a.json`](spec/a2a.json)

    When viewing this source file on GitHub, use the [latest published schema](https://a2a-protocol.org/latest/spec/a2a.json) because the version-specific files are generated during documentation builds and are not committed to the repository.

    <h3>Definition</h3>

    ```json
    --8<-- "docs/spec/a2a.json"
    ```
