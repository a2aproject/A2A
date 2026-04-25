# JSON Schema Reference

This page provides JSON Schema definitions for A2A protocol types. These schemas are **auto-generated from [proto definitions](https://github.com/a2aproject/A2A/tree/main/specification/a2a.proto)** and are non-normative — the proto source is the authoritative reference.

## Bundle

Download all schemas as a single file:

```
https://a2a-protocol.org/spec/a2a.json
```

## Individual Schemas

| Type | Description | `$schema` URL |
|------|-------------|---------------|
| [AgentCard](https://a2a-protocol.org/spec/AgentCard.json) | Agent identity and capabilities | `https://a2a-protocol.org/spec/AgentCard.json` |
| [Task](https://a2a-protocol.org/spec/Task.json) | Async task state | `https://a2a-protocol.org/spec/Task.json` |
| [TaskStatus](https://a2a-protocol.org/spec/TaskStatus.json) | Task status details | `https://a2a-protocol.org/spec/TaskStatus.json` |
| [Message](https://a2a-protocol.org/spec/Message.json) | Inter-agent message | `https://a2a-protocol.org/spec/Message.json` |
| [Part](https://a2a-protocol.org/spec/Part.json) | Message content part | `https://a2a-protocol.org/spec/Part.json` |
| [Artifact](https://a2a-protocol.org/spec/Artifact.json) | Task artifact | `https://a2a-protocol.org/spec/Artifact.json` |
| [TaskStatusUpdateEvent](https://a2a-protocol.org/spec/TaskStatusUpdateEvent.json) | Task status update event | `https://a2a-protocol.org/spec/TaskStatusUpdateEvent.json` |
| [TaskArtifactUpdateEvent](https://a2a-protocol.org/spec/TaskArtifactUpdateEvent.json) | Task artifact update event | `https://a2a-protocol.org/spec/TaskArtifactUpdateEvent.json` |
| [AgentCapabilities](https://a2a-protocol.org/spec/AgentCapabilities.json) | Agent capability declaration | `https://a2a-protocol.org/spec/AgentCapabilities.json` |
| [AgentSkill](https://a2a-protocol.org/spec/AgentSkill.json) | Agent skill description | `https://a2a-protocol.org/spec/AgentSkill.json` |
| [AgentExtension](https://a2a-protocol.org/spec/AgentExtension.json) | Agent extension | `https://a2a-protocol.org/spec/AgentExtension.json` |
| [AuthenticationInfo](https://a2a-protocol.org/spec/AuthenticationInfo.json) | Authentication info | `https://a2a-protocol.org/spec/AuthenticationInfo.json` |
| [AgentInterface](https://a2a-protocol.org/spec/AgentInterface.json) | Agent interface definition | `https://a2a-protocol.org/spec/AgentInterface.json` |
| [AgentProvider](https://a2a-protocol.org/spec/AgentProvider.json) | Agent provider info | `https://a2a-protocol.org/spec/AgentProvider.json` |
| [SecurityScheme](https://a2a-protocol.org/spec/SecurityScheme.json) | Security scheme | `https://a2a-protocol.org/spec/SecurityScheme.json` |

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
