# A2A Spreadsheet Protocol Binding — Specification

**Version:** 1.0 (Draft, 2026-11-05; sheet layout v2, 2026-11-06)
**Binding identifier:** `SPREADSHEET`
**Binding URI (custom-binding form, upstream §5.8):** `https://a2a-protocol.org/bindings/spreadsheet/v1`
**Upstream base:** A2A Protocol Specification v1.0, `a2aproject/A2A` @ `9fff3e0`.
**Layers affected:** Layer 3 only. Layer 1 (canonical data model) and
Layer 2 (abstract operations) are **normatively unchanged**. Where
this document and upstream conflict on L1/L2 semantics, upstream
governs.
**Provenance:** This binding formalises the Muse ↔ Gemini Spark
sheet lane live since 2026-10-12 and event-driven since 2026-11-01
(`muse-gemini-a2a-bridge/README.md` is its replication guide and is
incorporated by reference for setup). Sheet layout **v1** (the
original draft of this spec) carried the live lane's legacy column
names; sheet layout **v2** (§4) renames every column to its
canonical A2A field name. The live Muse ↔ Gemini Spark deployment
still runs layout v1 columns and migrates separately — this spec
and its adoption skills teach v2, and nothing about v2 changes the
live sheet.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and
**MAY** are to be interpreted as in RFC 2119 / RFC 8174.

---

## 1. Scope

This binding maps the Layer-2 abstract operations onto a shared
spreadsheet — three (plus one, §4.4) append-only tabs acting as
mailbox queues — for counterparties whose platform provides
first-party spreadsheet access in unattended runs but no agent
email address and no hostable endpoint (the Gemini Spark case).

In scope: endpoint identification, tab/column contract (sheet
layout v2, with layout v1 defined for decoders in Appendix B),
canonical `Message`/`Task` mapping, the structured-data-only rule,
wake-up (doorbell) and polling, Agent Card discovery, provenance,
idempotency, cleanup, async semantics, and error mapping.

Out of scope: spreadsheet-provider APIs (Google Sheets in the
reference deployment; any provider with equivalent append/read/
delete-row primitives and sharing ACLs can host the binding),
responder-internal execution, and the contents of any `kind`
namespace (skill semantics belong to the agents' cards).

## 2. Binding identification and Agent Card declaration

### 2.1 Supported interface entry (REQUIRED shape)

```json
{
  "protocolBinding": "SPREADSHEET",
  "protocolVersion": "1.0",
  "url": "https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit"
}
```

- `protocolBinding` **MUST** be `SPREADSHEET`. The URI form
  `https://a2a-protocol.org/bindings/spreadsheet/v1` **MAY**
  be published as an additional entry for the same endpoint;
  clients **MUST** treat the two as the same binding.
- `url` **MUST** be the spreadsheet's canonical HTTPS URL. The
  endpoint identity is the **spreadsheet ID** — the token between
  `/d/` and the next `/` — extracted by parsing `url`. The
  equivalent URN form `urn:a2a:spreadsheet:<SPREADSHEET_ID>` **MAY**
  be used in local configuration files (the reference deployment's
  `bridge-sheet.json` stores the bare ID) but **MUST NOT** replace
  the URL in a published card.
- Clients and servers **MUST** key all state by
  `(spreadsheet ID, tab name)`. The spreadsheet's **display title
  MUST NOT** be used as a key, a match string, or a capability
  check: titles are renamable cosmetics. (Live proof: "Muse Bridge
  — Results" → "A2A - Results", 2026-11-01, no breakage. Prompts
  that must *name* the sheet to a human-facing agent are display
  strings and are updated on rename, but they are not identifiers.)
- One spreadsheet serves exactly one ordered agent pair in v1.0.
  Multiplexing several responders onto one sheet is out of scope.

### 2.2 Capabilities

```json
"capabilities": {
  "streaming": false,
  "pushNotifications": true,
  "extendedAgentCard": false
}
```

- `streaming: false` — there is no stream. Progress is successive
  Results rows (§8.6).
- `pushNotifications: true` — realised by the doorbell (§5) in the
  responder direction and by consumer polling (§5.3) in the
  requester direction. It is push *notification*, not push
  *payload*: the payload always travels in the sheet.
- A SPREADSHEET-only agent declares **no** `securitySchemes` for
  this interface (§9). There is no bearer token on this wire.

### 2.3 Extension declaration

```json
{
  "uri": "https://a2a-protocol.org/bindings/spreadsheet/v1",
  "description": "A2A SPREADSHEET binding v1.0, sheet layout v2: SendMessage = Requests row, Task = Results row, Notes = non-task Messages. Structured data only; standing instructions live in the responder's A2A skill, never in rows.",
  "required": false,
  "params": {
    "tabs": ["Requests", "Results", "Notes", "Card"],
    "doorbellSubject": "A2A-Event",
    "idempotency": "(message_id, metadata a2a.token)",
    "sheetLayout": "2"
  }
}
```

The `sheetLayout` param is the deployment's layout declaration
(§4.0): it lives in the Card tab's `card_json`, inside this
extension's `params` — the binding's defined extension point — so
the canonical `AgentCard` object itself is unmodified. Absence of
`sheetLayout` means layout v1 (Appendix B).

## 3. Discovery — obtaining the Agent Card

Primary mechanism is *inside the transport*, so no separate
hosting is needed:

1. **Card tab (normative, §4.4).** The responder maintains a `Card`
   tab whose single data row holds its complete current Agent Card
   JSON. A client that can read the sheet already has the card —
   no operation round-trip is required. The card also declares the
   deployment's sheet layout (§2.3).
2. **CARD-REQUEST fallback.** If the `Card` tab is absent (the
   pre-spec live sheet has only three tabs; adding `Card` is
   additive and non-breaking), the client appends a Requests row
   with `kind: "a2a.get_agent_card"` (§8.7). The responder answers
   with a completed Task whose artifact `data` Part is the card
   JSON (carried in that answer's Results `task_json`, §7.3)
   **and** creates/populates the `Card` tab, so the fallback runs
   at most once.
3. **Well-known HTTPS URL** MAY additionally be published, as
   upstream, when the agent has a site. It is never required here.

Caching mirrors the EMAIL binding: key by spreadsheet ID,
re-read the Card tab when a `VersionNotSupportedError` occurs or
the cache is older than 24 h.

## 4. The sheet contract — layout v2

Row 1 of every tab is a frozen header row with exactly these
columns, in this order. Data rows are appended after it. Column
sets are versioned by this spec; a reader **MUST** ignore trailing
extra columns and **MUST** fail closed (surface, don't guess) on a
missing required column.

**Layout principle (v2).** Every column is either a canonical A2A
field — named exactly as in `a2a.proto` / the JSON schema
(`messageId`, `taskId`, `contextId`, `parts`, `status`,
`artifacts`) — or binding metadata carried in a `metadata_json`
column, the serialised form of the object's canonical `metadata`
(the A2A extension point). There are no bespoke field names on the
v2 wire. Appendix B maps every v1 column to its v2 successor.

### 4.0 Layout versioning

- This section defines sheet layout **v2**. Writers **MUST**
  write v2. Readers **MUST** accept v2 and v1 (Appendix B).
- A deployment declares its layout in the Card tab: the
  SPREADSHEET extension's `params.sheetLayout` inside `card_json`
  (§2.3). Local configuration (`bridge-sheet.json`) carries the
  same fact as `layout_version: 2`.
- The live Muse ↔ Gemini Spark deployment still runs layout v1
  and migrates separately; a v1 deployment's rows remain fully
  decodable by any conforming v2 reader.

### 4.1 Requests — sender appends, responder reads

A Requests row **is** a canonical `Message` sent via `SendMessage`:

```text
appended_at | message_id | task_id | context_id | kind | parts_json | metadata_json
```

| Column | Type / rule |
| --- | --- |
| `appended_at` | ISO 8601 UTC timestamp of the append (sender clock). Informational ordering aid; row order (§10.3) governs. |
| `message_id` | Canonical `Message.messageId`, verbatim. Unique per spreadsheet. **Together with `metadata_json`'s `a2a.token`, the idempotency key (§10.1).** |
| `task_id` | Canonical `Message.taskId`. Empty when the message starts a new task; otherwise the `Task.id` it addresses. |
| `context_id` | Canonical `Message.contextId`, the value only. May be empty. (`referenceTaskIds`, when needed, ride in `metadata_json`, §6.5.) |
| `kind` | Dotted invocation name, §6.2. |
| `parts_json` | Canonical array of `Part` objects, §6.3. Structured data **only** (§6.4). |
| `metadata_json` | Canonical `Message.metadata` as a JSON object. **MUST** carry the key `a2a.token` (§6.5). |

### 4.2 Results — responder appends, sender reads

A Results row **is** a canonical `Task`:

```text
appended_at | task_id | context_id | status | task_json | metadata_json
```

| Column | Type / rule |
| --- | --- |
| `appended_at` | ISO 8601 UTC timestamp of the append. |
| `task_id` | Canonical `Task.id` — equals `task_json`'s `id`. Assigned by the responder when the triggering message started a new task. |
| `context_id` | Canonical `Task.contextId`. |
| `status` | Canonical `TaskStatus.state`, verbatim `TASK_STATE_*` only (§7.2). |
| `task_json` | The full canonical `Task` object (§7.3); for operation failures, the A2A error object (§11). |
| `metadata_json` | Canonical `Task.metadata` serialised; **MUST** equal `task_json`'s `metadata` and **MUST** echo `a2a.token` from the triggering message (§9.2). |

One Requests row is answered by **one terminal** Results row,
optionally preceded by `working` rows (§7.4). A Results row is
linked to its triggering message by `task_json.history` (the
Task's history carries the message, §7.1) — there are no
request-correlation columns in v2.

### 4.3 Notes — responder appends, sender reads

A Notes row **is** a non-task canonical `Message`:

```text
appended_at | message_id | parts_json | metadata_json
```

Free-form, non-task communication (§8.8): the binding realisation
of a bare Layer-1 `Message` with no `Task`. The note text is a
`text` Part inside `parts_json`. Priority rides in
`metadata_json` under the key `a2a.priority` (**SHOULD** be one of
`info` | `normal` | `urgent`; readers **MUST** accept any value,
defaulting unknown values to `normal`). A note is *communication*,
not a task payload, so §6.4's structured-data rule does not apply
to its text Part — but a note **MUST NOT** be used to smuggle a
task past §6.4.

### 4.4 Card — responder maintains

```text
appended_at | card_version | card_json
```

Exactly one data row (row 2) is current; the responder **replaces**
it in place on card changes — the single sanctioned exception to
append-only (§10.4). `card_version` duplicates the card's own
`version` field for cheap change detection. `card_json` is the
complete canonical `AgentCard` object, including the layout
declaration in its SPREADSHEET extension params (§2.3). Readers
**MUST** tolerate a missing `Card` tab (see §3, fallback 2).

### 4.5 Cell and size limits

Provider cell limits bind (Google Sheets: 50 000 characters/cell).
`parts_json` / `task_json` / `card_json` **SHOULD** be ≤ 40 000
characters. Larger payloads travel by reference: a `url` Part or a
`data` Part containing a store key (§6.3), never by splitting JSON
across rows — the binding defines no chunking, and a reader
encountering an over-limit truncated cell **MUST** treat the row
as `InvalidAgentResponseError`, never parse a prefix.

## 5. Wake-up: the doorbell, and polling fallback

A spreadsheet cannot push. This binding specifies exactly one push
mechanism and one fallback; payload **never** travels by either.

### 5.1 Doorbell (REQUIRED for the responder direction)

A bound Apps Script on the sheet, function `onBridgeChange`,
trigger **From spreadsheet — On change**, whose *only* job is:

1. Read the `Requests` tab; if it has no data rows, stop.
2. Debounce: check a `CacheService` script-cache key
   (`RECENT_ALERT`); if present, stop. Otherwise set it with a
   **15-second** TTL. (Collapses batch-insert change storms into
   one alert; live value, normative here.)
3. Send one email via `MailApp.sendEmail` to the single account
   the responding agent watches, with subject **exactly**
   `A2A-Event` and a one-line body naming that a request is
   pending. The body carries **no** request data, no row contents,
   no instructions.

The script **MUST NOT** write to the sheet, process rows, poll, or
create/delete triggers. (Live anti-pattern, 2026-11-03: a proposed
replacement polled every 15 min, wrote a non-existent Status
column over the payload column, and deleted all triggers. All
three behaviours are prohibited by this paragraph.)

### 5.2 Responder wake semantics

The responder's processing schedule is **email-triggered** on
`subject:"A2A-Event"` (exact-subject filter). On wake it reads
*all* pending Requests rows (§8.1), not just the newest — the
doorbell is a hint that work exists, not a work item. The legacy
time-based (hourly) processing schedule **MUST** be paused when
the doorbell schedule is active, so the queue has one processor.

### 5.3 Polling fallback (both directions)

- If the doorbell fails (trigger disabled, mail undelivered), a
  time-based responder schedule **MAY** poll Requests as a
  backstop; suggested cadence 60 min (the live legacy value) —
  correctness never depends on it, only latency does.
- The requester direction (Results/Notes) has **no doorbell in the
  live deployment** and none is required: the requester's poller
  reads Results + Notes on a fixed cadence — live: **300 s**
  (`spark-sheet-poll` hook, zero-token unless rows exist) — and
  that cadence **SHOULD** be ≤ 5 min. A responder **MAY**
  additionally send an `A2A-Event`-subject email to a
  requester-watched mailbox as a Results doorbell; requesters
  **MUST** treat it, too, as a content-free hint.

## 6. SendMessage mapping — the Requests row

### 6.1 Identity mapping

| Canonical field | Sheet carriage (v2) |
| --- | --- |
| `Message.messageId` | The `message_id` column, verbatim. A sender wanting a UUID `messageId` uses a UUID `message_id`. (Consumers MAY namespace it locally by endpoint — `<spreadsheet_id>:<message_id>` — in their own stores; the wire value is unmodified.) |
| Idempotency key | `(message_id, metadata_json.a2a.token)` jointly. `message_id` alone is *not* sufficient (a guessed/duplicated ID with the wrong token matches nothing, §9.2). |
| `Message.taskId` | The `task_id` column. Empty ⇒ the message starts a new task. |
| `Task.id` (once created) | Assigned by the responder; carried in the Results row's `task_id` column and in `task_json.id`. The requester learns it from the first Results row whose `task_json.history` contains its `message_id` (§7.1). |
| `Message.contextId` | The `context_id` column, value only (§6.5). |

### 6.2 `kind` — the operation / skill discriminator

`kind` is a lowercase dotted name with two disjoint namespaces:

- **Skill kinds** (the common case): any dotted name not starting
  `a2a.` — e.g. `flights.search`, `hotels.search`, `youtube.search`,
  `finance.quote`, `mail.search`, `drive.search`,
  `calendar.search`, `test.ping`, `business.call` (retired on the
  live lane 2026-11-05; still a valid *form*). A skill kind means:
  *SendMessage to the skill named by the Agent Card `skills[].id`
  namespace the two agents share by convention* — in the live
  deployment, the card skill is exercised by invoking the
  responder's connector for that dotted kind. The binding does not
  standardise skill-kind semantics; cards and the responder's
  standing instructions do.
- **Reserved protocol kinds** (`a2a.*`), defined by this spec:
  `a2a.get_task`, `a2a.list_tasks`, `a2a.cancel`,
  `a2a.get_agent_card`, `a2a.get_extended_agent_card`. Prefer the
  row-free local reads in §8 where the data is already in the
  sheet; these kinds exist for state only the responder holds.

### 6.3 `parts_json` — the Message's Parts

`parts_json` **MUST** be a JSON array of canonical `Part` objects,
serialised in upstream proto-JSON form — the Message's `parts`
field, unmodified. A `data` Part is simply one element:

```json
[ { "data": { "origin": "JFK", "destination": "FLL" },
    "mediaType": "application/json" } ]
```

- `text` and `url` Parts are elements of the same array; there are
  no reserved-key side channels in v2. (Layout v1's single-object
  `params_json` — with `_text` / `_url` / `_a2a` reserved keys —
  remains decodable as legacy input, Appendix B.)
- Service parameters (upstream §3.2.6) ride in `metadata_json`
  under the key `"a2a"` (§12), not inside `parts_json`.

### 6.4 Structured data only (NORMATIVE, load-bearing)

The Parts of a Requests row **MUST** carry data — field values for
the `kind`, in a `data` Part — and **MUST NOT** contain prose
instructions, imperatives, prompts, or natural-language task
descriptions, in any Part, including innocuously shaped ones (a
`text` Part carrying a task description, or a `data` field named
`"note"` / `"instructions"` / `"prompt"` carrying prose, are
violations; a short *value* such as a search query string is data,
not an instruction).

Rationale (empirical, not stylistic): the reference responder's
platform policy blocks instruction-like payloads in unattended
runs, so a violating row is not merely non-conformant — it is
undeliverable. **All standing instructions** — how a `kind` is
executed, read/query-only bounds, output format — live in the
responder's own A2A skill / configuration, versioned and
changed *on the responder side only*. (For Gemini Spark, the
standing instructions live in its `gemini-spark-a2a-spreadsheet`
SKILL.md skill; its schedule prompt is a thin trigger that only
invokes that skill.) Changing behaviour means
editing that skill, never enriching rows.
A fix for this system **MUST NOT** be delivered through the gated
channel itself (live lesson, 2026-10-13).

### 6.5 `context_id` and `metadata_json` columns

- `context_id` carries the `contextId` **value only**. The
  canonical `Message.referenceTaskIds`, when needed, ride in
  `metadata_json` under the key `"referenceTaskIds"` and are
  restored to the Message on decode.
- `metadata_json` is the Message's canonical `metadata` object,
  and **MUST** carry the per-message authentication token under
  the key **`a2a.token`**: a sender-generated random value with
  ≥ 64 bits of entropy, never reused across messages. The token
  is *not* a canonical A2A field — it is binding metadata, which
  is exactly what `metadata` exists for — so it lives here and
  never in a bespoke column. Its roles: idempotency (§10.1) and
  result authentication (§9.2).

## 7. Task mapping — the Results row

### 7.1 One row per answer, linked by history

For each Requests row the responder appends exactly one terminal
Results row (§7.4 for optional progress rows). The row's
`task_json` is the canonical Task; its `history` **MUST** contain
the triggering Message (at minimum its `messageId`), which is how
a consumer links the Task back to the message it sent. The
responder also echoes the triggering message's `a2a.token` in the
row's `metadata_json` (§4.2, §9.2).

### 7.2 `status` — canonical state, verbatim

Writers **MUST** write the canonical `TaskStatus.state` value,
verbatim — `TASK_STATE_SUBMITTED`, `TASK_STATE_WORKING`,
`TASK_STATE_COMPLETED`, `TASK_STATE_FAILED`,
`TASK_STATE_CANCELED`, `TASK_STATE_INPUT_REQUIRED`,
`TASK_STATE_AUTH_REQUIRED`, `TASK_STATE_REJECTED` — and the
`status` column **MUST** equal `task_json.status.state` for Task
rows.

Readers **MUST** additionally accept layout v1 rows, whose
`status` spellings map as follows (decode-side compatibility
only; these spellings are never written in v2):

| v1 Results `status` | Canonical `Task.status.state` | Notes |
| --- | --- | --- |
| `done` | `TASK_STATE_COMPLETED` | Live legacy value. |
| `error` | `TASK_STATE_FAILED` | Reason in the v1 `result_json` (§11). |
| `working` | `TASK_STATE_WORKING` | Non-terminal (§7.4). |
| `cancelled` | `TASK_STATE_CANCELED` | Terminal answer to a cancelled task (Appendix B). |
| `input_required` | `TASK_STATE_INPUT_REQUIRED` | Non-terminal; task continues via a new Requests row with the same `context_id`. |
| `TASK_STATE_*` (verbatim) | itself | Also written by some v1 responders. |

### 7.3 `task_json` — the Task object

`task_json` **MUST** be the canonical `Task` proto-JSON
(`id`, `contextId`, `status{state, message?, timestamp}`,
`artifacts[]`, `history[]`, `metadata` as applicable), with the
answer in `artifacts[].parts[]` (`data` / `text` Parts) or in
`status.message.parts[]`. For operation failures, `task_json`
instead carries the A2A error object (§11) and `status` is
`TASK_STATE_FAILED`.

Layout v1 interop: a v1 row's `result_json` **SHOULD** have been
the same Task object, but the live form is often a plain answer
object (e.g. `{"price": …, "currency": …}`). A v2 decoder **MUST**
accept a v1 plain object and wrap it as: a `Task` with the §7.2
mapped state and one Artifact whose single `data` Part is that
object. The plain form is never written in v2.

### 7.4 Progress and multi-row tasks

A responder **MAY** append `TASK_STATE_WORKING` (and at most, in
practice, a few) Results rows before the terminal row for long
work. Successive rows for one task share `task_id`; the latest
row in row order is the task's current state (§10.3). Consumers
treat non-terminal rows as notifications only — they update local
state but never commit-and-clear (§10.2 cleanup keys off the
terminal row). `SubscribeToTask` is realised by this mechanism
plus §5.3 polling; there is no other subscription.

### 7.5 Parts and Artifacts inside JSON

Parts follow upstream proto-JSON exactly (`text` | `raw` base64 |
`url` | `data`). Binary `raw` Parts are subject to §4.5: anything
that would blow the cell limit travels by `url` Part (a link the
consumer *chooses* to fetch under its own policy — never
auto-fetched, cf. EMAIL binding §9.2) or not at all. There are no
attachments on this binding; the row *is* the envelope and the
payload.

## 8. Operation mapping (normative)

| # | Layer-2 operation | Realisation |
| --- | --- | --- |
| 8.1 | `SendMessage` | Append Requests row (§6). Response = terminal Results row (§7). Blocking semantics are client-emulated: wait for the matching Results row (doorbell/poll), with §10 timeout posture — never re-send. |
| 8.2 | `SendStreamingMessage` | Not offered. Attempted ⇒ `UnsupportedOperationError` Results row. §7.4 is the progress mechanism. |
| 8.3 | `GetTask` | **Local read, no row written:** find Results rows by `task_id` column. Latest row ⇒ that Task. Only non-terminal rows ⇒ Task in that state (e.g. `TASK_STATE_WORKING`). A Requests row carrying that `task_id` (or whose message created the task, once a Results row has linked it) with no Results row ⇒ `TASK_STATE_SUBMITTED`. Neither ⇒ `TaskNotFoundError` (local). Token rule: the caller must present the `a2a.token` of a message in the task's history; a Results row whose `metadata_json.a2a.token` echo does not match is treated as absent (existence is not leaked to a non-holder, §9.2). State held only inside the responder (rare) is queried via kind `a2a.get_task`, whose `data` Part carries `{"task_id": "…"}`. |
| 8.4 | `ListTasks` | **Local scan, no row written:** enumerate distinct `task_id`s from Results rows (plus Requests rows carrying a `task_id`), joining each task to its messages via `task_json.history`; filter by `context_id`/`status` as requested, order by `appended_at`. Pagination is offset over the scan (`pageSize`/`pageToken` = row offset as string). Kind `a2a.list_tasks` exists for responder-held state, mirroring §8.3. |
| 8.5 | `CancelTask` | Append-only cancellation, §8.5.1 below. |
| 8.6 | `SubscribeToTask` | §7.4 + §5.3. No row of its own. |
| 8.7 | `GetAgentCard` | Read Card tab (§3.1); fallback kind `a2a.get_agent_card` (§3.2). |
| 8.8 | (non-task) `Message` | Notes tab (§4.3). A Notes row decodes to a `Message{role: ROLE_AGENT, parts: <from parts_json>, metadata: <from metadata_json, incl. a2a.priority>}` with no task. Senders of notes never expect a Results row; a reply, if any, is a Requests row or a note in the reverse deployment's sheet. |
| 8.9 | `GetExtendedAgentCard` | Unsupported unless the Card declares `extendedAgentCard: true`; otherwise a `a2a.get_extended_agent_card` row is answered with a `TASK_STATE_FAILED` Results row carrying `ExtendedAgentCardNotConfiguredError` (§11). |
| 8.10 | Push-config ops | No webhook exists on this binding. `CreateTaskPushNotificationConfig` with a `mailto:` URL naming the doorbell recipient is a **no-op success** (the doorbell already notifies); with any other URL ⇒ `PushNotificationNotSupportedError`. Get/List/Delete mirror that stance. |

### 8.5.1 CancelTask on an append-only medium (honest semantics)

Rows are never edited or deleted to effect a cancellation —
deletion is cleanup (§10.2), and conflating the two would destroy
the audit trail before commit. Cancellation is itself a request:

1. Requester appends a Requests row: `kind: "a2a.cancel"`, a
   **fresh** `message_id` and a fresh `a2a.token` of its own. Its
   `data` Part carries `{"target_task_id": "…"}` — the target is
   identified by its canonical `task_id`. Ownership is proven via
   `metadata_json`: the cancel row's metadata **MUST** carry
   **`a2a.target_token`** — the `a2a.token` value of the original
   message that created the target task (§9.2). Its `context_id`
   = the target's `contextId`.
2. Responder, on processing: if the target has **no terminal
   Results row yet**, it abandons the work, appends the target's
   terminal Results row with `status: "TASK_STATE_CANCELED"`, and
   answers the cancel row with its own terminal Results row,
   `status: "TASK_STATE_COMPLETED"`, whose `task_json` is a Task
   for the cancel message carrying an artifact `data` Part
   `{"cancelled": "<target_task_id>"}`.
3. If the target is **already terminal**, it answers the cancel
   row with `status: "TASK_STATE_FAILED"` and `task_json` =
   `{"code": "TaskNotCancelableError", …}` — cancellation is
   idempotent only while non-terminal (upstream §3.3.1); a
   duplicate cancel of an already-cancelled target returns the
   `TASK_STATE_CANCELED` state as a `TASK_STATE_COMPLETED`
   answer, not an error.
4. Race honesty: append-only means a cancel can lose the race —
   the target may complete between the cancel append and the
   responder's read. Case 3 then applies. The binding **MUST NOT**
   pretend otherwise (no "cancel pending" state is defined).

## 9. Authentication and provenance

### 9.1 The ACL is the authentication

There is no credential on the wire. Access control is the
spreadsheet's sharing ACL: the sheet **MUST** be shared with
exactly the two agents' operating accounts (plus the principals'
accounts as owners) and **MUST NOT** be link-shared or public.
Write access to Requests is the capability to invoke; write access
to Results/Notes/Card is the capability to answer. A party that
can read the sheet but should not invoke is given read-only
access by the owner — and responders **SHOULD** additionally
ignore Requests rows whose append account (where the provider
exposes revision attribution) is outside the ACL allowlist.

### 9.2 `(message_id, a2a.token)` is result authentication

The sender generates the message's `a2a.token` (sufficient
entropy: ≥ 64 bits, unguessable), carries it in the Requests
row's `metadata_json`, and records the pair
`(message_id, a2a.token)` in its own store at send time. A Results
row is committed **iff** (a) its `task_json.history` links it to
a `message_id` with a pending request in the consumer's store,
**and** (b) its `metadata_json.a2a.token` echo exactly matches
that message's token. Unmatched rows are **never** committed and
**never** silently dropped: they stay in the sheet and are
surfaced (§10.2). The pair is simultaneously the idempotency key
(§10.1) and the proof that a result belongs to a request the
consumer actually sent — the spreadsheet analogue of the EMAIL
binding's mailbox provenance, adapted to a shared medium where
`From:` does not exist.

### 9.3 No secrets in rows, ever

Beyond `a2a.token` (a message-scoped matching secret, not a
credential), rows **MUST NOT** contain bearer tokens, API keys,
passwords, or OTPs — the sheet is a shared document, not a vault
(cf. EMAIL §12.4). The doorbell email likewise carries nothing
(§5.1).

## 10. Idempotency, cleanup, ordering, async

### 10.1 Idempotency and duplicates

- Appending the same `(message_id, a2a.token)` Requests row twice
  is a duplicate delivery: the responder **MUST** process it once
  (its store, keyed by the pair, is the dedup record) and answer
  once; a duplicate terminal Results row is ignored by the
  consumer on the same key.
- Same `message_id`, *different* `a2a.token` = key collision, not
  a duplicate: neither row is trusted for the other; surface it.

### 10.2 Cleanup — the sheet is transport, not the record

Each agent's own store (reference: Muse's KV queue) is canonical.
The sheet is cleared aggressively once state is committed:

1. **Results:** consumer commits a matched terminal row to its
   store, **verifies the commit, then deletes that row**
   (verify-then-clear). Unmatched rows are kept and surfaced.
2. **Requests:** the requester-side poller prunes Requests rows
   whose request is done in its store. The responder **MUST NOT**
   delete Requests rows (it does not own the requester's record
   of what was asked).
3. **Notes:** consumer ingests each note into its inbox store,
   verifies, then clears the Notes data rows.
4. **Card:** never pruned (§4.4).

Cleanup deletion is the *only* deletion this binding performs,
and §8.5.1 cancellation never masquerades as cleanup.

### 10.3 Ordering

Row order within a tab is append order and is authoritative;
`appended_at` is a cross-check (clocks differ). Per task, Results
rows arrive working → terminal; consumers apply §7.4 in row order
and never let a later-read non-terminal row regress a committed
terminal state.

### 10.4 Async semantics and latency

Store-and-forward throughout: `streaming: false`; every operation
is effectively non-blocking (cf. EMAIL §11.1). Expected latency is
doorbell latency, not poll latency: **live-measured ≈ 74 s
end-to-end** (Requests append → `A2A-Event` → responder run →
Results row) on 2026-11-01, against up to 60 min under the retired
hourly design. No latency is *guaranteed*: a task with no Results
row after 24 h is stale, not failed — the requester **SHOULD**
probe once via §8.3's local read (i.e. re-scan) and then escalate
to its principal, never by re-sending the request (that would
duplicate under a new key; nudging reuses §8.4/`a2a.get_task`).

## 11. Error mapping

Operation failures are terminal Results rows with
`status: "TASK_STATE_FAILED"` and `task_json` an error object
`{"code": "<ErrorName>", "message": "<human text>", "details": […]?}`
in upstream §3.3.2's model. (Layout v1 wrote these as
`status: "error"` rows with the object in `result_json`;
decoders map them identically.)

| Upstream error | Sheet realisation |
| --- | --- |
| `TaskNotFoundError` | §8.3 local verdict, or a `TASK_STATE_FAILED` row answering `a2a.get_task` / `a2a.cancel` for an unknown target |
| `TaskNotCancelableError` | `TASK_STATE_FAILED` row answering the `a2a.cancel` row (§8.5.1 case 3) |
| `PushNotificationNotSupportedError` | `TASK_STATE_FAILED` row per §8.10 |
| `UnsupportedOperationError` | `TASK_STATE_FAILED` row (streaming asks, unknown reserved `a2a.*` kind) |
| `ContentTypeNotSupportedError` | `TASK_STATE_FAILED` row naming the offending media type / oversize payload (§4.5) |
| `InvalidAgentResponseError` | Raised *locally* on malformed `task_json` / truncated cell; row kept, surfaced, never committed |
| `ExtendedAgentCardNotConfiguredError` | `TASK_STATE_FAILED` row per §8.9 |
| `VersionNotSupportedError` | `TASK_STATE_FAILED` row naming supported version (`1.0`); trigger to re-read Card tab |
| Unknown skill `kind` | `TASK_STATE_FAILED` row, code `UnsupportedOperationError`, message naming the kind — never silence |
| Responder execution failure | `TASK_STATE_FAILED` row with a generic code + human message in the error object |

Transport failures (sheet unreachable, ACL revoked) are not A2A
errors: no row can carry them. The affected agent surfaces them to
its principal through its own channels and retries under §10.4 —
it **MUST NOT** fall back to delivering the payload by doorbell
email, prose payloads, or any other channel (§6.4, §5.1).

## 12. Service parameters

Sheets have no headers. `A2A-Version` and `A2A-Extensions` ride in
`metadata_json` under the key `"a2a"` (of the form
`{"version": "1.0", "extensions": [ …uris… ]}`) on Requests and,
symmetrically, in the Task's `metadata` under key `"a2a"` on
Results (present both inside `task_json.metadata` and in the
mirrored `metadata_json` column, §4.2). Absence means `1.0` / no
extensions. The binding reserves no other transport-level names;
tab names and column headers in §4 are the binding's fixed
vocabulary.

## 13. Conformance

An implementation conforms to SPREADSHEET binding v1.0 iff it:

1. Declares §2.1's interface; keys everything by spreadsheet ID +
   tab name, never title.
2. Writes sheet layout v2 (§4) exactly, declares it per §4.0, and
   reads both v2 and v1 (Appendix B). Card tolerated-absent per §3.
3. Emits/parses §§6–7 (structured data only; canonical
   `TASK_STATE_*` on write; both status vocabularies accepted on
   read of v1 rows).
4. Implements §8.1, §8.3, §8.4, §8.7 (minimum set) and fails the
   rest per §11 rather than ignoring them.
5. Rings and honours the §5 doorbell (responder side) and polls
   per §5.3 (requester side).
6. Enforces §9 (ACL-only access, token-matched commits,
   unmatched rows surfaced) and §10.2 verify-then-clear cleanup.
7. Never places instructions in rows (§6.4) or payloads in the
   doorbell (§5.1).

## Appendix A — Worked example (layout v2 shapes)

Requests row (a skill invocation):

```text
appended_at:  2026-11-01T14:00:00Z
message_id:   42
task_id:      (empty — new task)
context_id:   bridge-ctx-7
kind:         flights.search
parts_json:   [{"data":{"origin":"JFK","destination":"FLL","date":"2026-11-14"},"mediaType":"application/json"}]
metadata_json: {"a2a.token":"t-9f2c…"}
```

Results row (the Task; `history` links it to message `42`):

```text
appended_at:  2026-11-01T14:01:14Z
task_id:      task-42
context_id:   bridge-ctx-7
status:       TASK_STATE_COMPLETED
task_json:    {"id":"task-42","contextId":"bridge-ctx-7","status":{"state":"TASK_STATE_COMPLETED","timestamp":"2026-11-01T14:01:14Z"},"artifacts":[{"artifactId":"task-42-result","parts":[{"data":{"flights":[{"carrier":"…","price":189}],"currency":"USD"},"mediaType":"application/json"}]}],"history":[{"messageId":"42","role":"ROLE_USER","parts":[{"data":{"origin":"JFK","destination":"FLL","date":"2026-11-14"},"mediaType":"application/json"}]}],"metadata":{"a2a.token":"t-9f2c…"}}
metadata_json: {"a2a.token":"t-9f2c…"}
```

End-to-end elapsed: ~74 s, of which the sheet itself is
near-instant — the budget is doorbell mail delivery plus the
responder schedule's start.

## Appendix B — Sheet layout v1 (legacy) and the v1 → v2 mapping

Layout v1 is the original column contract, inherited from the
live lane. It is **decode-only**: conforming readers MUST accept
it, conforming writers MUST NOT emit it. The live Muse ↔
Gemini Spark deployment still runs v1 and migrates separately.

| Tab | v1 column | v2 column | Mapping |
| --- | --- | --- | --- |
| Requests | `appended_at` | `appended_at` | Unchanged. |
| Requests | `request_id` | `message_id` | Same value, canonical name. v1 `request_id` also served as the task handle (v1 `Task.id` = `request_id`); v2 separates `task_id`. |
| Requests | `token` | *(metadata)* | Moves into `metadata_json` as the key `a2a.token`. |
| Requests | `kind` | `kind` | Unchanged (binding-level routing, §6.2). |
| Requests | `params_json` | `parts_json` | v1: a single JSON object decoded as one `data` Part (reserved keys `_text`/`_url` lifted to Parts, `_a2a` to metadata). v2: the canonical Parts array itself. |
| Requests | `context` | `context_id` | v1: bare contextId, or JSON `{"contextId","referenceTaskIds"}`, or an opaque label. v2: contextId value only; `referenceTaskIds` ride in `metadata_json`. |
| Results | `appended_at` | `appended_at` | Unchanged. |
| Results | `request_id` | *(history)* | Dropped as a column. The linkage is `task_json.history[].messageId`; v1 decode sets it from `request_id`. |
| Results | `token` | *(metadata)* | Moves into `metadata_json` as the echoed `a2a.token`. |
| Results | `kind` | *(dropped)* | The Task does not carry the invocation kind; recoverable from the linked message. |
| Results | `status` | `status` | Same column; v1 legacy spellings (`done`/`error`/`working`/`cancelled`/`input_required`) decode per §7.2 and are never written in v2. |
| Results | `result_json` | `task_json` | v1: Task object or plain answer object (wrapped on decode, §7.3). v2: the canonical Task object (or §11 error object). |
| Results | — | `task_id`, `context_id`, `metadata_json` | New in v2: the Task's canonical identifiers as columns, and its `metadata` mirrored for cheap filtering. |
| Notes | `appended_at` | `appended_at` | Unchanged. |
| Notes | `priority` | *(metadata)* | Moves into `metadata_json` as the key `a2a.priority`. v1 decode restores it there (and as `priority` for convenience). |
| Notes | `note` | `parts_json` | v1: bare text. v2: a `text` Part inside the Parts array. v1 decode wraps the text as one Part. Also new in v2: the `message_id` column. |
| Card | `appended_at` | `appended_at` | Unchanged. |
| Card | `card_version` | `card_version` | Unchanged. |
| Card | `card_json` | `card_json` | Unchanged in form: the canonical `AgentCard` object. In v2 the card additionally declares the layout via extension `params.sheetLayout` (§2.3). |

Cancel in v1 terms (for decoders): a v1 `a2a.cancel` row carried
`params_json {"target_request_id": "…", "target_token": "…"}` —
decode `target_request_id` as the target `task_id` and
`target_token` as the `a2a.target_token` proof of §8.5.1.
