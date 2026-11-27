# A2A Email Protocol Binding — Specification

**Version:** 1.0 (Draft, 2026-11-05)  
**Binding identifier:** `EMAIL`  
**Binding URI (custom-binding form, upstream §5.8):** `https://a2a-protocol.org/bindings/email/v1` (proposed identifier, experimental: this binding is not yet an official a2aproject binding; the URI follows the upstream governance namespace in docs/topics/extension-and-binding-governance.md and is used as an identifier only, HTTP access is not expected)  
**Upstream base:** A2A Protocol Specification v1.0, `a2aproject/A2A` @ `9fff3e0`.  
**Layers affected:** Layer 3 only. Layer 1 (canonical data model) and
Layer 2 (abstract operations) are **normatively unchanged** by this
document. Where this document and upstream conflict on L1/L2 semantics,
upstream governs.

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and
**MAY** are to be interpreted as in RFC 2119 / RFC 8174.

---

## 1. Scope

This binding maps every Layer-2 abstract operation onto Internet
email (RFC 5322 messages, transported by SMTP / submission / IMAP /
provider APIs) so that an agent whose only
endpoint is a mailbox can be a full A2A peer.

In scope: operation mapping, Agent Card declaration and discovery,
subject envelope, body encoding, threading, `Part`/`Artifact`
encoding, service-parameter carriage, authentication and provenance,
async delivery semantics, idempotency, and error mapping.

Out of scope: mailbox provisioning, mail-provider APIs (a binding
implementation adapts its provider (an agent mailbox service,
IMAP/SMTP, or a mail API) behind §§5–6), and human email UX.

## 2. Binding identification and Agent Card declaration

### 2.1 Supported interface entry (REQUIRED shape)

An agent offering this binding **MUST** declare it in
`AgentCard.supportedInterfaces`. The first entry is the preferred
interface (upstream `AgentCard` semantics), so an email-first agent
lists EMAIL first:

```json
{
  "protocolBinding": "EMAIL",
  "protocolVersion": "1.0",
  "url": "mailto:agent@example.com"
}
```

- `protocolBinding` **MUST** be the string `EMAIL` for
  discoverability by existing Muse tooling. Implementations that
  follow upstream §5.8 strictly **MAY** additionally publish the URI
  form `https://a2a-protocol.org/bindings/email/v1` (proposed identifier, experimental: this binding is not yet an official a2aproject binding; the URI follows the upstream governance namespace in docs/topics/extension-and-binding-governance.md and is used as an identifier only, HTTP access is not expected) as a
  second entry for the same `url`; clients **MUST** treat the two as
  the same binding.
- `protocolVersion` is the *binding* version (`1.0`), independent of
  the Agent Card's own `version` field.
- `url` **MUST** be a `mailto:` URI (RFC 6068) containing exactly one
  addr-spec: the agent's mailbox. Display names, query parameters,
  and multiple recipients **MUST NOT** appear.
- An agent **MAY** declare EMAIL alongside JSONRPC / GRPC /
  HTTP+JSON entries. A client **SHOULD** prefer the counterparty's
  first mutually supported entry.

### 2.2 Capabilities

An EMAIL-only or EMAIL-preferred card **MUST** declare honestly:

```json
"capabilities": {
  "streaming": false,
  "pushNotifications": true,
  "extendedAgentCard": false
}
```

- `streaming: false` — email has no server-push stream;
  `SendStreamingMessage` and `SubscribeToTask` are realised as
  successive reply emails (§11), never as a held connection, and a
  literal streaming request **MUST** fail with
  `UnsupportedOperationError` if the client insists on stream
  semantics (see §8.6).
- `pushNotifications: true` — realised *by reply email* (§11.2), not
  by webhook. `TaskPushNotificationConfig.url` in this binding is a
  `mailto:` URL.
- The card **SHOULD** carry the extension declaration in §2.4 so
  receivers can recognise the envelope form (§6) from the card.

### 2.3 Security declaration

The EMAIL interface **MUST NOT** list `bearerAuth` (or any
token/secret scheme) in its per-skill or per-interface security
requirements. Mailbox authentication is declared once, as an
extension parameter (§12), not as an upstream `SecurityScheme`,
because no credential traverses the wire. A card that also offers
HTTP bindings declares `bearerAuth` for *those* interfaces only.

### 2.4 Envelope extension declaration

```json
{
  "uri": "https://a2a-protocol.org/bindings/email/v1",
  "description": "A2A EMAIL binding v1.0: canonical Task/Message JSON over email; subject carries the #a2a:v1 envelope.",
  "required": false,
  "params": {
    "envelope": "#a2a:v1 #op:<OP> #mid:<messageId> #task:<taskId|-> #ctx:<contextId|->",
    "auth": "mailbox-identity; see SPEC §12. Bearer tokens are never sent by email."
  }
}
```

This supersedes the former `…/a2a-extensions/bridge-envelope/v1`
extension, whose `params.envelope` and `provenance` are subsumed
by §§6 and 12 of this spec; its task-state hints survive only as
decode-side interop (§16).

### 2.5 Agent avatar (OPTIONAL)

An agent **MAY** publish an avatar: a still image of the agent's
own persona, for display next to its name in inboxes, contact
lists, and coordination surfaces. Upstream Layer 1 already
provides one carriage for this, the optional `AgentCard.iconUrl`
field, but a URL alone does not serve a mailbox-only agent, which
has no reliable place to host it, and §9.2 forbids receivers from
auto-fetching URLs. This binding therefore adds an email-native
carriage alongside `iconUrl`, without changing Layer 1:

- An agent that hosts its avatar **SHOULD** set `iconUrl` to its
  URL, exactly as upstream defines it.
- An agent offering the avatar over email **MUST** declare it in
  the §2.4 extension's `params`, under an `avatar` object:

```json
"avatar": {
  "filename": "agent-avatar.webp",
  "mediaType": "image/webp",
  "sha256": "<lowercase hex SHA-256 of the avatar bytes>",
  "size": 48210,
  "width": 1600,
  "height": 1600
}
```

- `filename` **MUST** be `agent-avatar.` plus the extension for
  the media type (`.webp`, `.png`, `.jpg`). `mediaType` **MUST**
  be one of `image/webp`, `image/png`, or `image/jpeg`; SVG and
  other scriptable or vector formats **MUST NOT** be used.
  `sha256` and `size` (bytes) are **REQUIRED**; `width` and
  `height` (pixels) are **OPTIONAL**, and the image **SHOULD**
  be square.
- The avatar file **MUST NOT** exceed 512 KiB (524,288 bytes).
  An animated image **MAY** be sent; a client **MAY** render
  only its first frame.
- Carriage is by attachment in the `CARD` exchange (§3a): a
  `CARD` reply from an agent whose card declares an avatar
  **MUST** attach the avatar bytes under the declared
  `filename`, in addition to the `agent-card.json` attachment.
  The declared `sha256` is the join key between card and
  attachment, exactly as §9.3 manifests join artifacts to MIME
  parts; filename alone **MUST NOT** be trusted.
- A client **MUST** verify `sha256` and `size` against the
  attachment before caching or displaying it. On mismatch it
  **MUST** discard the avatar; the card itself stays valid when
  its own provenance (§12) passes, because the avatar carries
  no normative data. Clients cache the avatar keyed by
  (mailbox, `sha256`); a changed hash invalidates the cached
  copy even inside the §3 card-cache window, and the client
  re-obtains it on the next `CARD` exchange.
- Absence of an avatar is never an error and never affects
  conformance: a client falls back to a locally rendered
  placeholder (for example the agent's initials).
- The avatar is display only. It **MUST NOT** be used for
  authentication, provenance, or any identity decision; identity
  over this binding is the mailbox (§§4, 12), and a client
  **MUST NOT** present an avatar as a verified identity badge.
  Over this binding a client **MUST NOT** auto-fetch `iconUrl`
  either (§9.2); the attachment is the email carriage, and any
  URL fetch is a separate decision under the client's own
  policy on another binding.

## 3. Discovery — how a client obtains the Agent Card

Email-first means discovery **MUST** work with no HTTP server.
Two mechanisms are specified; an agent **MUST** support (a) and
**SHOULD** support (b). A client **MUST** try them in this order:

**(a) By email — `CARD` exchange (primary).**

1. Client sends a `GET_AGENT_CARD` email (§8.7) to the mailbox it
   already knows (from a prior message, a directory, or the
   principal). No task is created.
2. Agent replies in-thread with a `CARD` email: the complete
   Agent Card JSON as (i) the authoritative JSON block in the body
   (§7.3, `kind: "agentCard"`) **and** (ii) an attachment named
   exactly `agent-card.json` (`application/json`). The two copies
   **MUST** be byte-equivalent JSON values. If the card declares
   an avatar (§2.5), the reply **MUST** also attach the avatar
   bytes under the declared `filename`; the client verifies and
   caches it per §2.5.
3. If the card carries upstream `signatures` (JWS, `AgentCard`),
   the client **SHOULD** verify them before trusting non-EMAIL
   interfaces discovered from it. An unsigned card is acceptable
   over this binding when provenance (§12) passes, because the
   transport already authenticates the sender mailbox.

**(b) Well-known HTTPS URL (secondary, when the agent has a site).**

`https://<domain>/.well-known/agent-card.json`, exactly as upstream.
The domain is the agent operator's published
domain, if any; absence of a hosted card **MUST NOT** be treated as
absence of the agent — fall back to (a).

Caching: a client **MAY** cache a card keyed by mailbox address.
It **MUST** re-validate by `CARD-REQUEST` when a message fails with
`VersionNotSupportedError` or when the cached card is older than
24 h. `GetExtendedAgentCard` over email follows the same exchange
with `#op:GET_EXTENDED_AGENT_CARD`; it **MUST** fail with
`ExtendedAgentCardNotConfiguredError` when
`capabilities.extendedAgentCard` is false.

## 4. Addressing and agent identifiers

- **Mailbox** = endpoint. One mailbox **SHOULD** map to one agent.
  Plus-addressing (`name+agent@…`) **MUST NOT** be used to multiplex
  distinct A2A agents onto one mailbox under this binding; the
  legacy `+agent` Gmail aliases remain readable for interop (§16)
  but are not EMAIL-binding endpoints.
- **Identity is the mailbox address itself.** This binding defines
  no agent identifiers of its own: an agent is identified by the
  `mailto:` URL of the EMAIL interface in its Agent Card
  (upstream `AgentCard.supportedInterfaces`), and the RFC 5322
  `From:` / `To:` headers carry those addresses on the wire (§12).
  There is no sender/recipient token in the subject (§6).
- `From:` **MUST** be the sending agent's card-declared mailbox.
  `To:` **MUST** contain exactly the receiving agent's mailbox for
  binding traffic. Human principals **MUST NOT** be Cc'd on binding
  traffic unless the operation explicitly concerns them.

## 5. Transport requirements

- Messages are RFC 5322 mail with MIME (RFC 2045–2049). The body
  encoding in §7 is the `text/plain; charset=utf-8` body part.
  Multipart mail (`multipart/mixed`) is used iff there are
  attachments (§9.3).
- `Message-ID:` **MUST** be present, globally unique, and **SHOULD**
  embed the A2A `messageId`: `<a2a-<messageId>@<sender-domain>>`.
  It is the deduplication anchor alongside `messageId` (§13).
- Transport confidentiality relies on the mail system's TLS
  (submission / transport) and provider storage; this binding adds
  no payload encryption. Senders **MUST NOT** place secrets,
  bearer tokens, OTPs, or credentials in any binding email (§12.4).
- Maximum sizes: the JSON block **SHOULD** be ≤ 256 KiB and total
  message (with attachments) ≤ 10 MiB. Larger artifacts go by `url`
  Part (§9.2), never by inflating the mail.

## 6. Subject envelope (normative)

### 6.1 Grammar

Every binding email — request, response, update, error — **MUST**
carry this subject. Order is fixed; unknown `#key:` tokens **MUST**
be ignored by receivers, never treated as errors.

```text
subject   = "#a2a:v1" 1*( SP token )
token     = "#op:" operation
          / "#mid:" message-id
          / "#task:" task-id / "-"
          / "#ctx:" context-id / "-"
          ; human suffix MAY follow, separated by " -- ":
          / "--" *( VCHAR )
operation = "SEND_MESSAGE" / "GET_TASK" / "LIST_TASKS"
          / "CANCEL_TASK" / "GET_AGENT_CARD"
          / "GET_EXTENDED_AGENT_CARD" / "TASK_UPDATE"
          / "TASK_ERROR" / "CARD" / "LIST_TASKS_RESULT"
```

The four tokens are the whole envelope. Every value is a
projection of a canonical Layer-1/Layer-2 field; identity is
carried by the `From:` / `To:` headers and the Agent Card (§4),
task state by the `Task` object in Zone J (§7.3), and ordering
by the reply chain and `status.timestamp` (§10.2). No other
`#key:` token is defined by this binding; the historical tokens
of that pre-binding bridge envelope are decode-side interop
only (§16) and **MUST NOT** be emitted.

Example (new task):

```text
#a2a:v1 #op:SEND_MESSAGE #mid:9f2c… #task:- #ctx:ctx-7d31…
```

Example (task completed, same context):

```text
#a2a:v1 #op:TASK_UPDATE #mid:a104… #task:task-51… #ctx:ctx-7d31…
```

### 6.2 Field semantics

| Token | Source of truth | Rule |
| --- | --- | --- |
| `#op:` | §8 | The Layer-2 operation this email performs. The JSON block (§7) repeats it; on conflict the JSON block governs. |
| `#mid:` | `Message.messageId` | The canonical `messageId` of the payload message (for `Task` payloads: `task.status.message.messageId` if present, else the transport `Message-ID` local-part). **MUST** be globally unique; it is the idempotency key. |
| `#task:` | `Task.id` | Absent/`-` in an initial `SEND_MESSAGE` means *create a new task*. Present means the email concerns that task. Clients **MUST NOT** invent a taskId for creation (upstream §3.4.2). |
| `#ctx:` | `contextId` | Groups the thread (§10.1). `-` only before assignment (initial request may omit a context; the reply assigns it and every later email carries it). |

A watcher **MUST** be able to route, dedupe (§13), and apply reply
tiering from the subject + `From:` alone, without parsing the body.
Anything safety-relevant (provenance, payload) still requires §§7/12.

### 6.3 Human readability

A sender **MAY** append `-- <short human phrase>` after the last
token. Receivers **MUST** parse only the token prefix. The legacy
free-form subjects (`#muse bridge: …`) are interop input only (§16).

## 7. Body format (normative)

The `text/plain` body has three zones, in order:

### 7.1 Zone H — human rendering (REQUIRED)

The concatenation of the payload's text Parts, in order, verbatim,
followed — for `Task` payloads — by a one-line status summary
(`Task <id>: <state>`). If there is no text Part, Zone H is a single
line naming the operation. Zone H is what a human who
opens the mail reads; it carries no normative data beyond Zone J.

### 7.2 Delimiter

A line containing exactly:

```text
---A2A-JSON---
```

then the JSON block, then a line containing exactly
`---END-A2A-JSON---`. Exactly one such block per email.

### 7.3 Zone J — canonical JSON block (AUTHORITATIVE)

A single JSON object (UTF-8, pretty-printing optional):

```json
{
  "a2aBinding": "EMAIL/1.0",
  "operation": "SEND_MESSAGE",
  "messageId": "9f2c…",
  "taskId": null,
  "contextId": "ctx-7d31…",
  "message": { "…canonical Message (proto-JSON)…" },
  "task": null,
  "error": null
}
```

- Exactly one of `message` / `task` / `agentCard` / `error` payload
  keys is non-null, per §8's table (`agentCard` is used by `CARD`).
  `ListTasks` replies use `task: null` plus `"tasks": [ … ]`.
- `message` and `task` values are the upstream proto-JSON forms of
  `Message` and `Task` (field names as in `a2a.proto`'s JSON
  mapping: `messageId`, `taskId`, `contextId`, `role`, `parts`,
  `status.state`, …). **No binding-specific fields may be added
  inside them.** Binding metadata lives only in the wrapper.
- On any conflict between subject, Zone H, and Zone J, **Zone J
  governs**; subject governs only routing when Zone J is unparseable
  (then the email **MUST** be treated as `TASK_ERROR` /
  `InvalidAgentResponseError`, §14).
- Attachments never replace Zone J; they supplement it (§9).

## 8. Operation mapping (normative)

One Layer-2 call = one email; its response = one reply email (§10),
except `SEND_MESSAGE`, whose *response stream* is one-or-more
`TASK_UPDATE` emails ending in a terminal state.

| # | Layer-2 operation | Request `#op:` | Request payload (Zone J) | Response `#op:` | Response payload |
| --- | --- | --- | --- | --- | --- |
| 8.1 | `SendMessage` | `SEND_MESSAGE` | `message` — canonical `Message`; `taskId` absent ⇒ new task, present ⇒ continue task; `contextId` optional | `TASK_UPDATE` (×N) | `task` — canonical `Task` incl. `status`, `history`, `artifacts` |
| 8.2 | `SendStreamingMessage` | — not offered — | — | `TASK_ERROR` | `error: UnsupportedOperationError` if attempted with stream semantics; otherwise treat as 8.1 |
| 8.3 | `GetTask` | `GET_TASK` | `message` with one `data` Part `{"taskId": "…", "historyLength": n?}` — or wrapper `taskId` alone | `TASK_UPDATE` | `task` (current snapshot) or `TASK_ERROR: TaskNotFoundError` |
| 8.4 | `ListTasks` | `LIST_TASKS` | `message.data` Part `{"contextId": "…?", "status": "TASK_STATE_…?", "pageSize": n?, "pageToken": "…?"}` | `LIST_TASKS_RESULT` | `"tasks": [Task, …]`, `"nextPageToken": "…?"` in wrapper |
| 8.5 | `CancelTask` | `CANCEL_TASK` | wrapper `taskId` + `message` (reason as text Part, optional) | `TASK_UPDATE` | `task` with `TASK_STATE_CANCELED`, or `TASK_ERROR: TaskNotCancelableError` / `TaskNotFoundError` |
| 8.6 | `SubscribeToTask` | `SEND_MESSAGE` with `data` Part `{"subscribe": "<taskId>"}` | as 8.1 | `TASK_UPDATE` (×N) | successive `task` snapshots until terminal — the email realisation of the stream |
| 8.7 | `GetAgentCard` | `GET_AGENT_CARD` | `message` with empty/text Part | `CARD` | `agentCard` + `agent-card.json` attachment (§3a) |
| 8.8 | `GetExtendedAgentCard` | `GET_EXTENDED_AGENT_CARD` | as 8.7 | `CARD` | extended `agentCard`, or `TASK_ERROR: ExtendedAgentCardNotConfiguredError` / `UnsupportedOperationError` |
| 8.9 | Push-config ops (`Create/Get/List/DeleteTaskPushNotificationConfig`) | `SEND_MESSAGE` with `data` Part `{"pushConfig": {…}}` | `TaskPushNotificationConfig` JSON; `url` **MUST** be `mailto:` | `TASK_UPDATE` | `task` + wrapper `"pushConfig"` echo; unsupported ⇒ `PushNotificationNotSupportedError` (only if card says `pushNotifications: false`) |

Notes:

- **Work vs. query.** “Work on it / continue” is `SEND_MESSAGE`;
  a pure status query is `GET_TASK`. The binding has no third
  form; the legacy bridge's combined query-and-work token is
  decode-side interop only (§16).
- Every request **MUST** receive at least one response email, even
  if only a `TASK_ERROR` or a `TASK_STATE_SUBMITTED` acknowledgement.
  Silence is never a valid A2A response over this binding.

## 9. Parts and Artifacts

### 9.1 Part mapping

Canonical `Part` is a oneof: `text` | `raw` (bytes) | `url` |
`data` (arbitrary JSON), plus `filename`, `mediaType`, `metadata`.

| Part kind | Zone H | Zone J | Attachment |
| --- | --- | --- | --- |
| `text` | Verbatim, in order, first | Verbatim in `parts[]` | Never |
| `data` | One-line summary MAY be rendered (`[data: <keys>]`); omission allowed | Verbatim JSON value in `parts[]` — authoritative | Never (unless > 256 KiB: then `url` fallback, §5) |
| `url` | The URL on its own line | Verbatim in `parts[]` | Never auto-fetched by receiver |
| `raw` (≤ 256 KiB, text-safe media type) | Not rendered | Base64 string in `parts[]` (proto-JSON bytes encoding) | Optional duplicate |
| `raw` (binary or > 256 KiB) | `[attachment: <filename>]` line | `parts[]` entry with `raw` **omitted**, `filename` + `mediaType` + `metadata: {"emailAttachment": true, "sha256": "…"}` | **REQUIRED** — the bytes travel as a MIME attachment with that filename/media type |
| (legacy file part: `filename` + content) | as `raw` | as `raw` | as `raw` |

Receivers **MUST** reconstruct `raw` from the attachment when
`metadata.emailAttachment` is true, verify `sha256` when present,
and **MUST** fail with `ContentTypeNotSupportedError` — not silent
truncation — for a media type they cannot accept.

### 9.2 URL parts

A `url` Part is a reference, not a fetch instruction. Receivers
**MUST NOT** fetch it automatically (SSRF / tracking). Fetching is
an agent decision under its own policy.

### 9.3 Artifacts

A `Task.artifacts[]` entry maps to:

1. Its canonical JSON in the `Task` inside Zone J — including each
   artifact Part per §9.1 — **plus**
2. For every binary/`raw` artifact Part, a MIME attachment as in
   §9.1, **plus**
3. A manifest: if any attachment exists, the sender **MUST** add a
   `data` Part (or wrapper-adjacent artifact manifest in the Task's
   `metadata.emailArtifactManifest`) listing
   `{artifactId, name, filename, mediaType, sha256, size}` per
   attachment. The manifest is the join key between Zone J and MIME;
   filename alone **MUST NOT** be trusted as the join.

## 10. Threading, context, and ordering

### 10.1 Thread = context

- The first email of a context carries no `In-Reply-To`. Its
  `Message-ID` anchors the thread.
- Every subsequent email in the context **MUST** set
  `In-Reply-To: <previous Message-ID>` (or the context anchor) and
  `References:` containing the anchor `Message-ID`. Mail clients'
  threading and the A2A `contextId` therefore coincide.
- All emails sharing a `contextId` **SHOULD** share the `References`
  root. A receiver **MUST** key task/context lookup on Zone J's
  `contextId`/`taskId`, using headers only as a fallback when
  Zone J is missing (legacy mail, §16).
- One context **MAY** contain many tasks; one task belongs to
  exactly one context (upstream §3.4).

### 10.2 Ordering (no sequence numbers)

This binding defines **no sequence counter** — upstream A2A has
none, and email's store-and-forward delivery (§11.1) cannot
guarantee arrival order anyway. Ordering rests on upstream and
RFC 5322 mechanisms only:

- **Conversation order** is the reply chain: `In-Reply-To` /
  `References` (§10.1) plus the `contextId` grouping.
- **State order** is `Task.status.timestamp` (upstream `Task`
  field): per task, the snapshot with the newest
  `status.timestamp` is current, and `Task.history` records the
  message sequence the agent itself observed.
- A receiver that suspects it missed an update does not infer
  one from a gap — there are no gap signals on this wire. It
  polls with `GET_TASK` (§11.1) and reconciles by
  `status.timestamp` (§11.3).

### 10.3 Multi-turn and INPUT_REQUIRED

`TASK_STATE_INPUT_REQUIRED` / `TASK_STATE_AUTH_REQUIRED` are
ordinary `TASK_UPDATE` emails whose status message asks the
question. The client continues by `SEND_MESSAGE` in the same
thread with the same `taskId` + `contextId` (upstream §3.4.3).
`AUTH_REQUIRED` over email **MUST NOT** solicit credentials in the
reply (§12.4); it names the out-of-band step the principal must do.

## 11. Async semantics

### 11.1 Store-and-forward is the model

Email delivery is asynchronous, provider-queued, and unbounded-delay
in the worst case (minutes typical; hours possible). Therefore:

- `SendMessageConfiguration.return_immediately` defaults are
  reinterpreted: over email *every* `SendMessage` is effectively
  non-blocking. A sender **MUST NOT** expect the terminal
  `TASK_UPDATE` in any bounded time and **MUST NOT** re-send the
  same `messageId` as a retry (§13).
- Blocking behaviour is emulated client-side: poll by `GET_TASK`
  (§8.3) with backoff (suggested: 5 min, 15 min, 1 h), or simply
  wait for push (§11.2). A task with no update for 24 h is *stale*,
  not failed; the client **SHOULD** send one `GET_TASK` before
  escalating to the principal.

### 11.2 Push notifications = reply email

Declaring `pushNotifications: true` commits the agent to sending a
`TASK_UPDATE` email, unprompted, on every *material* state change
(state transition, new artifact, INPUT_REQUIRED) for tasks created
over this binding, to the mailbox that created the task. No webhook
is involved. Explicit `TaskPushNotificationConfig` (§8.9) may name
a different `mailto:` destination; absent a config, the creator's
mailbox is the destination. This is the binding's realisation of
upstream §3.5's push mechanism; ordering guarantee (§11.3) applies.

### 11.3 Ordering

Per task, an agent **MUST** emit `TASK_UPDATE`s in state order and
**MUST NOT** emit an older state after a newer one. Receivers
**MUST** tolerate cross-email reordering by comparing
`(taskId, status.timestamp)`: a strictly older snapshot never
overwrites a newer known state.

### 11.4 Polling = inbox watch

The client-side “poll” is an inbox watch (IMAP IDLE, provider hook,
or periodic scan). Watchers dedupe on §13 keys and wake the
agent only on new `messageId`s. Polling cadence is a local policy,
not a wire property.

## 12. Authentication, provenance, and security

### 12.1 Mailbox identity replaces bearer tokens

There is **no bearer token, API key, shared secret, or auth line**
in this binding — none in the subject, body, headers, or
attachments, ever (see §12.4). Authentication is:

1. **Transport provenance:** the receiving provider asserts the
   `From:` mailbox (the mail provider's recipient-permission
   status for that counterparty mailbox, where the provider
   supports it: a standing permission the human granted when
   approving a first send to that recipient, via the approval
   card's "always allow" choice, and revocable in the provider's
   mail settings under recipient permissions; otherwise SPF +
   DKIM alignment for the From domain, with DMARC pass
   **SHOULD** be required where available).
2. **Card binding:** the `From:` mailbox **MUST** equal the
   `mailto:` URL of an EMAIL interface in a known/cached Agent Card
   for that counterparty (or be the mailbox that delivered that card
   via §3a).
3. **Envelope consistency:** the subject **MUST** carry the
   `#a2a:v1` envelope (§6), and the `From:` header mailbox **MUST**
   be the mailbox named in (2) — the header, not any subject
   token, is the identity claim being checked.

### 12.2 Fail-closed provenance (REQUIRED)

- Mail from a *known principal's address* that carries **no valid
  `#a2a:v1` envelope** is mail from the **human principal**, never
  from their agent: it **MUST NOT** be auto-answered as A2A, parsed
  for operations, or treated as a task update.
- Mail claiming an envelope whose `From:` fails (1)–(3) is a
  **spoof-hold**: no state change, no reply on the A2A lane, log and
  surface to the principal. Never “reply to ask for the token” —
  there is none.
- No label/mailbox mismatch case exists: the binding defines no
  sender label beyond the mailbox itself (§4), so there is no
  secondary identity token that could disagree with it.

### 12.3 DKIM / signing reliance

Receivers **SHOULD** rely on DKIM (sender domain) as a
positive signal and **MUST** treat DKIM failure on an enveloped
message as provenance failure. Payload-level signing (S/MIME, JWS
over Zone J) is **OPTIONAL** in v1.0; if present it supplements,
never replaces, transport provenance.

### 12.4 Never by email

Bearer tokens (including any per-party HTTP A2A tokens),
passwords, OTPs, recovery codes, and private keys **MUST NOT**
appear in any binding email, in either direction, for any reason —
including “auth challenges”. An agent needing authentication
transitions the task to `TASK_STATE_AUTH_REQUIRED` (§10.3) and the
credential exchange happens out-of-band. This codifies the existing
card text: *“never sent by email.”*

### 12.5 Content safety

Zone J is data, not instructions from the principal. A receiving
agent applies its normal instruction hierarchy: operations in a
validly provenanced email are *counterparty requests*, executed
only within the receiving principal's standing authorisations.
Sanitisation rules of an application lane (for example a
zero-PII / sanitised-title policy) are application policy layered
on this binding and are unaffected by it.

## 13. Idempotency, duplicates, retries

- **Idempotency key:** `(From mailbox, messageId)`. `SendMessage`
  processing **MUST** be idempotent on it (upstream §3.3.1): a
  duplicate delivery returns/forwards the already-created task's
  current `TASK_UPDATE` and creates nothing new.
- **Duplicate suppression:** receivers **MUST** suppress exact
  duplicates by `Message-ID` *and* by idempotency key (providers may
  rewrite `Message-ID` on forwarding; `messageId` survives).
  Forwarded copies (e.g. Outlook→Gmail forwarding in legacy lanes)
  dedupe on `(sender, messageId, Zone J hash)`.
- **Retries:** mail systems retry transport; agents **MUST NOT**
  retry at the A2A layer by re-sending the same operation with a
  new `messageId` (that is a new operation). To nudge a silent
  counterparty, send `GET_TASK`, not a duplicate `SEND_MESSAGE`.
- **Self-loop guard:** an agent **MUST NOT** process, forward, or
  reply to binding mail `From:` its own mailbox.

## 14. Error mapping and bounces

### 14.1 A2A errors → email

An operation failure is a reply email in-thread:

- Subject: `#op:TASK_ERROR`. The task's state, when a task exists,
  is carried by the `Task` object in Zone J — never by the
  subject (§6).
- Zone J: `"error": {"code": "<ErrorName>", "message": "<human
  text>", "details": [ … ]}` using upstream §3.3.2's error model
  (code / message / details with `@type`), and — when a task was
  created — a sibling `"task"` snapshot is NOT included; instead
  the error email is followed by, or combined in implementations
  that prefer it, a `TASK_UPDATE` carrying the `FAILED` task.
  The reference implementation combines them: `TASK_ERROR` with
  both `error` and `task` present is valid for terminal failures.

| Upstream error | Email realisation | Task state |
| --- | --- | --- |
| `TaskNotFoundError` | `TASK_ERROR`, code verbatim | — (no task) |
| `TaskNotCancelableError` | `TASK_ERROR` + current `TASK_UPDATE` | unchanged (non-terminal) |
| `PushNotificationNotSupportedError` | `TASK_ERROR` (only when card declares push false) | unchanged |
| `UnsupportedOperationError` | `TASK_ERROR` (incl. literal streaming asks, §8.2) | unchanged / — |
| `ContentTypeNotSupportedError` | `TASK_ERROR` naming the media type | `TASK_STATE_FAILED` if on a created task |
| `InvalidAgentResponseError` | Raised *locally* by the receiver of a malformed reply; surfaced to principal; counterparty notified by `TASK_ERROR` with this code | local |
| `ExtendedAgentCardNotConfiguredError` | `TASK_ERROR` on `CARD` exchange (§8.8) | — |
| `ExtensionSupportRequiredError` | `TASK_ERROR` naming the extension URI | — |
| `VersionNotSupportedError` | `TASK_ERROR` naming supported `protocolVersion` (`1.0`); also the trigger to re-run §3 discovery | — |
| Auth / provenance failure (§12.2) | **No A2A reply** (spoof-hold, silent to sender) | no state change |
| Internal / transient agent failure | `TASK_ERROR` with generic code + `TASK_STATE_FAILED` task update, or a `TASK_STATE_WORKING` update promising a later terminal update — never silence | `FAILED` or `WORKING` |

### 14.2 Bounces and delivery failure (SMTP DSN)

- A hard bounce (5xx DSN, unknown mailbox) for a request means the
  endpoint does not exist: the client **MUST** mark the cached card
  stale, **MUST NOT** retry the same mailbox automatically, and
  surfaces the failure to its principal.
- A soft bounce / delay DSN (4xx) is informational: the operation
  remains pending; §11.1 polling rules apply.
- An agent receiving a bounce for a `TASK_UPDATE` it sent treats
  the *notification* as undelivered but the *task state* as
  unchanged and authoritative in its own store; it **SHOULD** note
  the bounce in the task's `metadata`.
- Auto-replies (vacation, “ mailbox full” non-DSN) are not A2A
  messages: no envelope ⇒ §12.2 human-mail handling, never parsed.

## 15. Service parameters

Upstream §3.2.6 parameters are carried as follows (custom bindings
must specify this):

| Parameter | Email carriage |
| --- | --- |
| `A2A-Version` | Wrapper field `"a2aVersion": "1.0"` in Zone J; binding version is `protocolVersion` from the card. An `X-A2A-Version: 1.0` header **MAY** duplicate it. Mismatch ⇒ `VersionNotSupportedError`. |
| `A2A-Extensions` | Wrapper field `"extensions": ["<uri>", …]` in Zone J; `X-A2A-Extensions` header **MAY** duplicate it. |
| (binding-reserved) | `X-A2A-Binding: EMAIL/1.0` header **SHOULD** be sent; receivers **MUST NOT** require it (providers strip headers). The subject envelope + Zone J are the reliable carriers. |

Header names are case-insensitive; Zone J is authoritative on any
header/body disagreement.

## 16. Interop with an earlier bridge envelope (decode-only)

Before this binding, an earlier bridge envelope carried six further
subject tokens: `#from:`, `#to:`, `#action:`, `#topic:`,
`#status:`, `#seq:` (full historical form: `#a2a:v1 #from:<agent>
#to:<agent> #action:<ACTION> #topic:<slug> #status:<state>
#seq:<n>`, in later bridge mail joined by some or all of the §6
tokens). Those tokens are **not part of this binding**. Senders
implementing this binding **MUST NOT** emit any of them; the
normative subject is §6 exactly.

Receivers **SHOULD** still decode them, as interop only:

- A subject containing `#a2a:v1` and any legacy token, with no
  Zone J block, is legacy mail. The receiver synthesises the
  `Message` from the text body and maps the legacy action token
  to an operation: `SEND` / `STAGE` / `RELAY` → `SEND_MESSAGE`;
  `RECHECK` → `GET_TASK` when the mail carries no new work
  content, else `SEND_MESSAGE`; `STATUS-QUERY` → `GET_TASK` /
  `LIST_TASKS`; `CARD-REQUEST` → `GET_AGENT_CARD`; `CANCEL` →
  `CANCEL_TASK`; `CONFIRM` / `REPORT` → `TASK_UPDATE`.
- The legacy state hints (`STAGE` ≈ `TASK_STATE_SUBMITTED`,
  `RECHECK` / `REPORT` ≈ `TASK_STATE_WORKING`, `CONFIRM` ≈
  `TASK_STATE_COMPLETED`) are non-normative triage hints only;
  the `Task` JSON is the only normative state.
- The legacy sender/recipient labels carry no identity: identity
  is the `From:` mailbox (§12), exactly as for binding mail.
- The legacy counter is ignored entirely; ordering is §10.2.
- A binding-form message (§6 envelope + Zone J) that also carries
  a stray legacy token is decoded as binding mail; the legacy
  token is ignored, like any unknown token (§6.1).

A one-line body envelope used by an application lane is an
*application payload* (a `data`-equivalent line inside a
`SEND_MESSAGE` text Part), not a binding element; it is carried
unchanged inside §7 bodies for that lane.

## 17. Conformance

An implementation conforms to EMAIL binding v1.0 iff it:

1. Declares the §2.1 interface and §2.2 capabilities honestly.
2. Emits and parses §§6–7 exactly (Zone J authoritative).
3. Implements §8 operations 8.1, 8.3, 8.5, 8.7 (minimum set) and
   fails the rest per §14 rather than silently ignoring them.
4. Threads per §10.1 and orders task state per §10.2; dedupes
   per §13.
5. Enforces §12 provenance fail-closed and never transmits
   credentials (§12.4).
6. Sends a terminal `TASK_UPDATE` (or `TASK_ERROR`) for every
   task it creates — no silent tasks.
7. If its card declares an avatar, carries it per §2.5 (declared
   hash and size, attached in the `CARD` exchange); a card with
   no avatar declaration conforms without one.

## Appendix A — Worked example (abridged)

Request (`SEND_MESSAGE`, new task) — subject as in §6.1; body:

```text
Could you check availability for a meeting next week?

---A2A-JSON---
{
  "a2aBinding": "EMAIL/1.0",
  "operation": "SEND_MESSAGE",
  "messageId": "9f2c1e…",
  "taskId": null,
  "contextId": "ctx-7d31…",
  "message": {
    "messageId": "9f2c1e…",
    "role": "ROLE_USER",
    "contextId": "ctx-7d31…",
    "parts": [{ "text": "Could you check availability for a meeting next week?" }]
  },
  "task": null,
  "error": null
}
---END-A2A-JSON---
```

Terminal reply (`TASK_UPDATE`, `TASK_STATE_COMPLETED`) carries the
full `Task` in `"task"`, `"message": null`, same `contextId`,
`In-Reply-To` set to the request's `Message-ID`.
