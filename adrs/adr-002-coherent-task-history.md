# ADR-002: Coherent Task History (Timeline + Artifacts)

**Status:** Proposed

**Date:** 2026-07-30

**Decision Makers:** Technical Steering Committee (TSC)

**Technical Story:** [#1991 Coherent Task History](https://github.com/a2aproject/A2A/issues/1991) (v1.1-candidate); builds on [#1794](https://github.com/a2aproject/A2A/issues/1794) / [#1810](https://github.com/a2aproject/A2A/pull/1810) (`generation` ordering primitive)

## Context

A2A exposes what happened during a task through several disconnected places. The
latest agent status message lives in `TaskStatus.message`; client-sent messages,
prior agent messages, progress updates, and artifacts are surfaced separately,
with no single ordered view. A consumer cannot reliably reconstruct the sequence
of an interaction, and `TaskStatus.message` gets overloaded as a lossy, de-facto
history channel.

This matters most for bidirectional / multi-turn interaction. When a task carries
many client and agent messages (including streamed input and output), the
fragmented representation is no longer reconstructable — and the ordering numbers
we already attach to artifacts (`generation`, from #1794/#1810) don't correspond
to anything a consumer can see. The timeline is what gives those generations
meaning: it records, in order, what happened on the wire so that each artifact
and message can be interpreted in context.

It is tempting to record only client/input messages. But an input message often
only makes sense in light of a preceding agent progress update — a user message
may be a direct reaction to one. So the timeline records both client and agent
messages plus progress updates.

Scope: the timeline is explicitly **not** a full trajectory or trace of the
agent's internal execution. It is a full history of the *interaction on the wire*
— enough context to interpret every message and artifact the task produces.

## Decision Drivers

* **Context for every message and artifact on the wire.** In a bidirectional
  stream, consumers need to understand what happened, when, and why. `generation`
  numbers on artifacts are meaningless without an ordered record to anchor them;
  the timeline supplies that context. It is a full history of the interaction on
  the wire (client + agent messages + progress updates), not a trajectory of the
  agent's internal execution.
* **Interleave messages and large/streamed artifacts** without flooding the
  ordered view with per-chunk stream events.
* **Backward compatibility (v1 → v1.1).** Changes should be additive; existing v1
  clients and servers must keep working. Prefer deprecation over removal.
* **Forward compatibility.** Do not foreclose a larger v2 rework (event sourcing,
  unified types, context-level storage).
* **Support input-required / elicitation flows** additively, without redefining
  the existing task states.
* **Ship v1.1.** Avoid scope creep that slips the release; a "boil the ocean"
  rework is the primary risk to timeliness.

## Considered Options

* **Option 1 — Additive timeline + separate artifacts collection (v1.1).** Add a
  `timeline` collection of role-tagged entries (both client and agent messages,
  plus progress updates), ordered by `generation`. Keep a separate `artifacts`
  collection annotated with `start_generation` / `end_generation` so artifacts
  interleave with the timeline without emitting per-chunk events into it. Make
  agent replies first-class `role: agent` timeline entries and soft-deprecate
  `TaskStatus.message`. Represent input-required via an optional `elicitations`
  collection (`state: waiting | blocked | resolved`), deriving
  `BLOCKED`/input-required from it while leaving existing states intact.
* **Option 2 — Full event-sourced / unified model (v2).** Model the task as an
  ordered event log and unify `Message` and `Artifact` into a single
  parts-plus-metadata type (streaming provided by the containing task), possibly
  moving history storage to the context level. Structurally clean, but breaking.
* **Option 3 — Status quo / minimal patch.** Keep the current structure and only
  document ordering conventions over the existing fields.

## Decision Outcome

**Chosen option:** "Option 1 — Additive timeline + separate artifacts collection
(v1.1)", with Option 2 explicitly deferred to v2.

Option 1 delivers the coherent, ordered, replayable history that #1991 asks for
while remaining additive and backward compatible, so it can land in v1.1 without
a migration. It reuses the `generation` ordering primitive already introduced
in #1794/#1810 rather than inventing a new ordering scheme, and keeps
stream-chunk noise out of the ordered view by separating artifacts.

Option 2 captures a real structural insight (that `Message` and `Artifact` are
both "parts + metadata", and that streaming is a property of the containing
task). That insight is directionally right but breaking, so it is recorded here
as the motivation for a **future v2 ADR** rather than adopted now. To avoid
painting v2 into a corner, v1.1 takes two forward-compatible steps: allow
**client-written (bidirectional) artifacts**, and add an origin/`role` signal to
`Artifact` so the input/output distinction is preserved even as the two types
converge.

`TaskStatus.message` is **soft-deprecated with no removal before 2.0**. SDKs keep
populating it with the current logic throughout the v1.x line, so existing
consumers continue to work unchanged; new consumers should read the timeline
instead and should not read `TaskStatus.message` unless they already do. The
field is removed in 2.0.

### Ordering: generation vs. timestamp

The timeline (and artifact interleaving) is ordered by `generation`, not by
wall-clock timestamps. This follows from the `generation` work in #1794/#1810:
timestamps are unreliable across distributed producers and are kept only as
optional correlation/display metadata. This is a property of that ordering
decision rather than a driver of the history model itself, and is called out here
so the timeline inherits it explicitly.

### Consequences

#### Positive

* One ordered, replayable representation of task activity for consumers.
* Large/streamed artifacts interleave correctly without flooding the timeline.
* Additive: no v1 migration required; deprecations are soft.
* Ends the reliance on `TaskStatus.message` as a history channel for new
  consumers, without breaking existing ones.
* Input-required/elicitation is modeled explicitly and aligns with the broader
  ecosystem's elicitation concept, without changing existing task states.
* Leaves a clean path to a v2 event-sourced/unified model.

#### Negative

* Two collections (`timeline` + `artifacts`) plus generation-range annotations
  add representational surface area that a fully unified v2 model would remove.
* `TaskStatus.message` lingers (populated but not to be read) until 2.0, so two
  representations of the latest agent message coexist across the v1.x line.
* Some duplication between v1.1 additive types and an eventual v2 unified type is
  likely; v1.1 accepts short-term redundancy to protect release timing.

#### Neutral

* Timestamps become optional correlation/display metadata rather than an ordering
  key (see *Ordering: generation vs. timestamp*).
* Bidirectional streaming mechanics (how a client streams into an artifact,
  sending messages to a `WORKING` task, input queueing) are specified in the
  bidirectional-streaming thread, not here; this ADR only fixes the history/order
  model they build on.

## Pros and Cons of the Options

### Option 1 — Additive timeline + separate artifacts (v1.1)

Ordered, role-tagged `timeline` keyed by `generation`; separate `artifacts`
collection with `start_generation`/`end_generation`; optional `elicitations`
collection for input-required; `TaskStatus.message` soft-deprecated in favor of
`role: agent` timeline entries.

**Pros:**

* Backward compatible and shippable in v1.1.
* Reuses an existing ordering primitive (`generation`).
* Keeps stream chunks out of the ordered view.
* Explicit, additive input-required/elicitation modeling.
* Forward-compatible with a v2 unification (bidirectional artifacts + `role`).

**Cons:**

* More types/fields than a unified model.
* `TaskStatus.message` remains populated-but-dead until 2.0.
* Accepts some redundancy that v2 would later collapse.

### Option 2 — Full event-sourced / unified model (v2)

Task as an ordered event log; `Message` and `Artifact` collapsed into one
parts-plus-metadata type; possibly context-level history storage.

**Pros:**

* Structurally simplest end state; one type, one ordered log.
* Naturally coherent history by construction.
* Cleanest bidirectional streaming story.

**Cons:**

* Breaking change; requires migration and a major version.
* Large scope; high risk to v1.1 timeline if attempted now.
* Needs its own design (storage location, event schema, compatibility) — a
  separate ADR.

### Option 3 — Status quo / minimal patch

Document ordering over existing fields; no new structure.

**Pros:**

* Least work.
* No new surface area.

**Cons:**

* Does not actually solve #1991 for bidirectional/multi-turn tasks.
* Leaves `TaskStatus.message` overloaded.
* No clean interleaving of streamed artifacts.

## Implementation

v1.1, additive only:

1. Add a `timeline` collection of role-tagged entries (client + agent messages,
   progress updates), ordered by `generation`. Ordering key is `generation` (per
   #1794/#1810), not timestamps; timestamps remain optional metadata.
2. Add/retain a separate `artifacts` collection; annotate artifacts with
   `start_generation` / `end_generation` for interleaving.
3. Allow client-written (bidirectional) artifacts; add an origin/`role` signal to
   `Artifact` to preserve the input/output distinction.
4. Add an optional `elicitations` collection
   (`state: waiting | blocked | resolved`); derive input-required/`BLOCKED` from
   it; leave existing task states unchanged.
5. Soft-deprecate `TaskStatus.message`: agent replies become first-class
   `role: agent` timeline entries. SDKs keep populating `TaskStatus.message` with
   the current logic through v1.x for existing consumers; new consumers read the
   timeline. The field is removed in 2.0.

Bidirectional streaming mechanics are specified separately and depend on this
model.

## Related Decisions

* [ADR-001: Leverage ProtoJSON Specification for JSON Serialization](adr-001-protojson-serialization.md)
* Future: **ADR-00X — Unify Message and Artifact (v2)** (parking-lot; captures
  Option 2's structural direction as a v2 decision)

## References

* [#1991 Coherent Task History](https://github.com/a2aproject/A2A/issues/1991)
* [#1794](https://github.com/a2aproject/A2A/issues/1794) /
  [#1810](https://github.com/a2aproject/A2A/pull/1810) — `generation` ordering
  primitive

## Notes

This ADR deliberately scopes v1.1 to the additive timeline/artifacts model and
records the event-sourced/unified approach as the motivation for a future v2 ADR.
The intent is to solve coherent history now without a breaking change, while the
two forward-compatible hooks (bidirectional artifacts and an `Artifact` origin/
`role`) keep the door open to v2 unification later.
