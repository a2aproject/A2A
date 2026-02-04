# Task Progress Metadata Extension v1

**Status:** Draft (v1)  
**Owner:** bittr.ai team  
**Date:** 2026-02-04  
**Extension URI (canonical key):** `https://a2aproject.github.io/extensions/task-progress/v1`

---

## 1. Overview

This document defines a **profile/metadata extension** for A2A that standardizes how agents report **structured task progress** (including multiple concurrent progress trackers) without changing any core A2A data structures.

### Goals
- Provide a **UI-friendly**, machine-readable progress schema.
- Support **multiple concurrent trackers** (e.g., parallel tool calls).
- Work with existing A2A update mechanisms (polling, SSE, push notifications).
- Remain **fully compliant** with A2A extension constraints (metadata-only).

### Non-goals (explicitly out of scope for v1)
- ETA prediction or time-to-complete estimates.
- Cost estimation / token usage accounting.
- Defining new core RPCs, adding proto fields, or adding enum values.
- Standardizing tool-call tracing beyond progress reporting.

---

## 2. Compliance with A2A extension rules

This extension:
- **MUST NOT** add fields to core A2A types.
- **MUST NOT** add enum values.
- **MUST** encode all extension data in existing `metadata` fields.

---

## 3. Activation and declaration

### 3.1 Agent Card declaration
Agents supporting this extension SHOULD declare it in `capabilities.extensions`:

```json
{
  "capabilities": {
    "extensions": [
      {
        "uri": "https://a2aproject.github.io/extensions/task-progress/v1",
        "required": false,
        "description": "Structured task progress reporting",
        "params": {
          "maxTrackers": 20,
          "maxMessageChars": 512,
          "maxIdChars": 128,
          "recommendedMaxUpdatesPerSecond": 2
        }
      }
    ]
  }
}
```

### 3.2 Request activation
Clients activate the extension by including its URI in `A2A-Extensions`.

---

## 4. Where progress metadata lives

Progress data MAY be attached in any of these metadata locations:

1) **TaskStatus message metadata (recommended canonical location)**
- `Task.status.message.metadata[EXT_URI]`

2) **TaskStatusUpdateEvent metadata (recommended for streaming updates)**
- `TaskStatusUpdateEvent.metadata[EXT_URI]`

The extension does **not** require Task metadata (`Task.metadata`) to be updated, but implementations MAY mirror the current progress there for convenience.

---

## 5. Data model

### 5.1 Top-level payload
The metadata entry at key `EXT_URI` MUST be an object with the following shape:

```json
{
  "trackers": [ /* 0..maxTrackers ProgressTracker */ ],
  "aggregate": { /* optional ProgressAggregate */ }
}
```

### 5.2 ProgressTracker
Each tracker represents one independently progressing unit of work (e.g., “tool-call-7”, “download-assets”).

Required:
- `id` (string): stable identifier for the tracker within the task.

Optional:
- `progress` (number): current progress value.
- `total` (number): total progress value. If omitted, total is unknown.
- `message` (string): human-readable hint for UI.
- `status` (string): one of `"running" | "completed" | "failed"`.
- `startedAt` (string): RFC 3339 timestamp.
- `updatedAt` (string): RFC 3339 timestamp.

Semantics:
- If `total` is present, `0 <= progress <= total` MUST hold.
- For a given `(task_id, tracker.id)`, `progress` SHOULD be monotonic non-decreasing across updates when `total` is present.
- If `status="completed"`, implementations SHOULD set `progress==total` when `total` is present.
- Trackers MAY be omitted from later updates once `status` is terminal (`completed` or `failed`).

### 5.3 ProgressAggregate
The optional `aggregate` is a convenience for clients that want a single progress bar.

Fields:
- `progress` (number)
- `total` (number, optional)
- `message` (string, optional)

Semantics:
- If provided, aggregate SHOULD be consistent with trackers, but clients MUST treat it as advisory (not authoritative).

---

## 6. Update and rate-limiting guidance

- Agents SHOULD avoid emitting progress updates at high frequency.
- Agents SHOULD follow `recommendedMaxUpdatesPerSecond` if declared; otherwise default guidance is **≤ 2 updates/sec per tracker**.
- Clients MUST tolerate bursty or delayed updates and MUST NOT assume continuous streaming.

---

## 7. Backward compatibility

- Extension-unaware clients will ignore the metadata entry.
- Extension-unaware agents will ignore activation and may omit progress metadata.
- The presence of this extension MUST NOT change the meaning of core task states.

---

## 8. JSON Schema (normative)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://a2aproject.github.io/extensions/task-progress/v1/schema.json",
  "title": "A2A Task Progress Metadata Extension v1",
  "type": "object",
  "required": ["trackers"],
  "properties": {
    "trackers": {
      "type": "array",
      "items": { "$ref": "#/definitions/tracker" },
      "maxItems": 100
    },
    "aggregate": { "$ref": "#/definitions/aggregate" }
  },
  "additionalProperties": false,
  "definitions": {
    "tracker": {
      "type": "object",
      "required": ["id"],
      "properties": {
        "id": { "type": "string", "minLength": 1, "maxLength": 128 },
        "progress": { "type": "number" },
        "total": { "type": "number" },
        "message": { "type": "string", "maxLength": 512 },
        "status": { "type": "string", "enum": ["running", "completed", "failed"] },
        "startedAt": { "type": "string", "format": "date-time" },
        "updatedAt": { "type": "string", "format": "date-time" }
      },
      "additionalProperties": false
    },
    "aggregate": {
      "type": "object",
      "properties": {
        "progress": { "type": "number" },
        "total": { "type": "number" },
        "message": { "type": "string", "maxLength": 512 }
      },
      "additionalProperties": false
    }
  }
}
```

Implementations MAY further restrict `maxItems` to the declared `maxTrackers`.

---

## 9. Examples (informative)

### 9.1 Single tracker, known total

```json
{
  "metadata": {
    "https://a2aproject.github.io/extensions/task-progress/v1": {
      "trackers": [
        {"id": "tool-call-1", "progress": 50, "total": 100, "message": "Processing image 50/100", "status": "running"}
      ],
      "aggregate": {"progress": 50, "total": 100}
    }
  }
}
```

### 9.2 Multiple trackers, unknown total

```json
{
  "metadata": {
    "https://a2aproject.github.io/extensions/task-progress/v1": {
      "trackers": [
        {"id": "download", "progress": 12, "message": "Downloaded 12 files"},
        {"id": "index", "progress": 3, "message": "Indexed 3 shards"}
      ]
    }
  }
}
```

---

## 10. Conformance test vectors (normative)

1) **Valid / monotonic**: tracker progresses 0→10→10 with total=10.
2) **Valid / unknown total**: total omitted; progress increments.
3) **Invalid / progress > total**: reject as schema violation.
4) **Invalid / status invalid**: reject as schema violation.
5) **Advisory**: aggregate present but inconsistent with trackers; clients MUST not treat as an error.
