# JSON Schema Reference

This page provides JSON Schema definitions for A2A protocol types. These schemas are **auto-generated from [proto definitions](https://github.com/a2aproject/A2A/tree/main/specification/a2a.proto)** and are non-normative — the proto source is the authoritative reference.

## Bundle

Download all schemas as a single file:

```
https://a2a-protocol.org/spec/a2a.json
```

## Individual Schemas

| Type | Description |
|------|-------------|
| [AgentCard](https://a2a-protocol.org/spec/AgentCard.json) | Agent identity and capabilities |
| [Task](https://a2a-protocol.org/spec/Task.json) | Async task state |
| [TaskStatus](https://a2a-protocol.org/spec/TaskStatus.json) | Task status details |
| [Message](https://a2a-protocol.org/spec/Message.json) | Inter-agent message |
| [Part](https://a2a-protocol.org/spec/Part.json) | Message content part |
| [Artifact](https://a2a-protocol.org/spec/Artifact.json) | Task artifact |
| [TaskStatusUpdateEvent](https://a2a-protocol.org/spec/TaskStatusUpdateEvent.json) | Task status update event |
| [TaskArtifactUpdateEvent](https://a2a-protocol.org/spec/TaskArtifactUpdateEvent.json) | Task artifact update event |
| [AgentCapabilities](https://a2a-protocol.org/spec/AgentCapabilities.json) | Agent capability declaration |
| [AgentSkill](https://a2a-protocol.org/spec/AgentSkill.json) | Agent skill description |
| [AgentExtension](https://a2a-protocol.org/spec/AgentExtension.json) | Agent extension |
| [AuthenticationInfo](https://a2a-protocol.org/spec/AuthenticationInfo.json) | Authentication info |
| [AgentInterface](https://a2a-protocol.org/spec/AgentInterface.json) | Agent interface definition |
| [AgentProvider](https://a2a-protocol.org/spec/AgentProvider.json) | Agent provider info |
| [SecurityScheme](https://a2a-protocol.org/spec/SecurityScheme.json) | Security scheme |

## Usage

Reference a schema in your `agent.json` using the `$schema` keyword. Most editors will then provide autocompletion and validation:

```json
{
  "$schema": "https://a2a-protocol.org/spec/AgentCard.json",
  "name": "My Agent",
  "description": "A helpful agent"
}
```

## Regenerating Schemas

Schemas are generated from proto definitions via `scripts/proto_to_json_schema.sh`. To rebuild:

```bash
# Bundle only (original behavior)
./scripts/proto_to_json_schema.sh specification/json/a2a.json

# Bundle + individual schemas
./scripts/proto_to_json_schema.sh specification/json/a2a.json docs/spec
```

Output is published to `a2a-protocol.org/spec/` via MkDocs. Do not edit generated files directly — update the proto source instead.
