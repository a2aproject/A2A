# SPEC Amendment — EMAIL Binding (draft for `docs/specification.md`)

Status: draft insertion text for the fork, not yet applied to
`docs/specification.md`. Numbering below (`## 15.`) is provisional:
on acceptance the maintainers should place this section immediately
after Section 11 (HTTP+JSON/REST Protocol Binding) as the new
Section 12, renumbering Sections 12–14, and add the EMAIL column to
the tables in Sections 5.3 and 5.4. The full design rationale,
legacy interop rules, and worked examples live in
`email-binding/SPEC.md` in the fork; this amendment is the
normative core in upstream's own structure and style.

Companion changes (separate commits, see `email-binding/COMMITS.md`):

- Section 5.3: add an `Email Operation` column to the Method
  Mapping Reference table (values in §15.4 below).
- Section 5.4: add an `Email Representation` column (values in
  §15.5 below).
- `specification/a2a.proto`: comment-only addition naming `EMAIL`
  and `SPREADSHEET` as known `protocolBinding` values (draft patch:
  `email-binding/proto-additions.patch.txt`). Per CONTRIBUTING,
  that proto touch is what triggers a protocol release; it is a
  `feat:` commit, unlike the `docs(spec):` commits for this text.

---

## 15. Email Protocol Binding

The Email protocol binding provides an asynchronous,
store-and-forward interface using Internet email (RFC 5322). It is
intended for agents whose endpoint is a mailbox rather than an
HTTP listener, including agents that receive a provider-issued
mailbox (for example, a `muse.ai` address) and agents behind
intermittent connectivity. The binding preserves the canonical
data model (Section 4) and the abstract operations (Section 3)
without change.

### 15.1. Protocol Requirements

- **Protocol:** RFC 5322 messages with MIME (RFC 2045–2049),
  transported by SMTP, submission, or a provider mail API.
- **Endpoint:** A `mailto:` URL (RFC 6068) containing exactly one
  address, declared in the Agent Card (see Section 15.3).
- **Content-Type:** `text/plain; charset=utf-8` for the body part
  carrying the binding payload. `multipart/mixed` is used if and
  only if the message carries attachments.
- **Streaming:** Not supported. Agents **MUST** declare
  `streaming: false` for this binding.
- **Push Notifications:** Supported, realized as reply emails to
  the requesting mailbox (see Section 15.4.7).

### 15.2. Service Parameter Transmission

A2A service parameters defined in Section 3.2.6
**MUST** be transmitted in the JSON wrapper object defined in
Section 15.3.2, because mail providers may strip or reorder
headers:

| Parameter | Transmission |
| :--- | :--- |
| `A2A-Version` | Wrapper field `a2aVersion`. An `X-A2A-Version` header **MAY** duplicate it. |
| `A2A-Extensions` | Wrapper field `extensions` (array of URIs). An `X-A2A-Extensions` header **MAY** duplicate it. |

On any disagreement between a header and the wrapper, the wrapper
governs.

### 15.3. Message Format

#### 15.3.1. Subject Envelope

Every binding message **MUST** carry a machine-readable subject
prefix so that receivers can route, deduplicate, and apply reply
tiering without parsing the body:

```text
#a2a:v1 #op:<OPERATION> #mid:<messageId>
#task:<taskId|-> #ctx:<contextId|->
```

The four tokens are the whole envelope; every value projects a
canonical field. Identity is carried by the RFC 5322 `From:` /
`To:` headers and the Agent Card declaration (Section 15.7), task
state by the `Task` object in the JSON block, and ordering by the
reply chain and `Task.status.timestamp`. The subject carries no
sender, recipient, state, or sequence token.

- `#mid:` carries the `messageId` of the payload `Message` and,
  together with the sender mailbox, is the idempotency key.
- `#task:` is absent (encoded `-`) in an initial `SendMessage`,
  which creates a new task. Clients **MUST NOT** invent a `taskId`
  for task creation.
- A human-readable suffix **MAY** follow, separated by ` -- `.
  Receivers **MUST** parse only the token prefix and **MUST**
  ignore unknown `#key:` tokens.

#### 15.3.2. Body Format

The body has a human-readable zone (the payload's text `Part`s, in
order) followed by exactly one delimited JSON block, which is
authoritative on any conflict with the subject or the human zone:

```text
---A2A-JSON---
{
  "a2aBinding": "EMAIL/1.0",
  "operation": "SEND_MESSAGE",
  "messageId": "…",
  "taskId": null,
  "contextId": "…",
  "message": { /* Message object */ },
  "task": null,
  "error": null
}
---END-A2A-JSON---
```

Exactly one of `message`, `task`, `agentCard`, or `error` is
non-null, according to the operation (Section 15.4). Binding
metadata **MUST NOT** be added inside the canonical `Message` or
`Task` objects themselves.

#### 15.3.3. Threading

The first message of a context has no `In-Reply-To` header. Every
subsequent message in the context **MUST** set `In-Reply-To` and
`References` to the context's anchor `Message-ID`, so that mail
threading and the A2A `contextId` coincide. Receivers **MUST** key
task and context lookup on the JSON wrapper, using headers only as
a fallback for legacy mail.

### 15.4. Core Methods

One abstract operation maps to one email. The response to an
operation is a reply email in the same thread, except for
`SendMessage`, whose response is one or more `TASK_UPDATE` emails
ending in a terminal state.

#### 15.4.1. `SendMessage`

- **Request:** `#op:SEND_MESSAGE`; wrapper `message` holds the
  `SendMessageRequest`'s `Message`. Absent `taskId` creates a new
  task; a present `taskId` continues that task.
- **Response:** One or more `#op:TASK_UPDATE` emails; wrapper
  `task` holds the current `Task` snapshot.
- **Execution Mode:** Every `SendMessage` over this binding is
  effectively non-blocking (compare
  Section 3.2.2). Clients emulate
  blocking behavior by waiting for the terminal `TASK_UPDATE` or
  by polling with `GetTask`.

#### 15.4.2. `SendStreamingMessage`

Not supported. An agent that receives a request insisting on
stream semantics **MUST** respond with a `TASK_ERROR` email
carrying `UnsupportedOperationError`. Progress is delivered as
successive `TASK_UPDATE` emails (Section 15.4.6).

#### 15.4.3. `GetTask`

- **Request:** `#op:GET_TASK`; the wrapper `taskId` identifies the
  task, optionally with a `data` `Part` of the form
  `{"taskId": "…", "historyLength": n}`.
- **Response:** A `TASK_UPDATE` email with the current `Task`, or
  a `TASK_ERROR` email carrying `TaskNotFoundError`.

#### 15.4.4. `ListTasks`

- **Request:** `#op:LIST_TASKS`; filters (`contextId`, `status`,
  `pageSize`, `pageToken`) are carried in a `data` `Part`.
- **Response:** A `LIST_TASKS_RESULT` email whose wrapper carries
  `tasks` (an array of `Task` objects) and an optional
  `nextPageToken`.

#### 15.4.5. `CancelTask`

- **Request:** `#op:CANCEL_TASK`; the wrapper `taskId` identifies
  the task. A reason **MAY** be included as a text `Part`.
- **Response:** A `TASK_UPDATE` email with state
  `TASK_STATE_CANCELED`, or a `TASK_ERROR` email carrying
  `TaskNotCancelableError` or `TaskNotFoundError`.

#### 15.4.6. `SubscribeToTask`

Realized as successive `TASK_UPDATE` emails for the subscribed
task until it reaches a terminal state. No separate subscription
message is defined.

#### 15.4.7. Push Notification Configuration Methods

Declaring `pushNotifications: true` commits the agent to sending
an unprompted `TASK_UPDATE` email on every material state change
to the mailbox that created the task. A
`TaskPushNotificationConfig` for this binding uses a `mailto:`
URL as its `url` value to name a different destination.
Create/Get/List/Delete operations are carried as `SendMessage`
requests whose `data` `Part` holds the configuration object.

#### 15.4.8. `GetExtendedAgentCard` and Agent Card Discovery

- **Request:** `#op:GET_AGENT_CARD` (or
  `#op:GET_EXTENDED_AGENT_CARD`).
- **Response:** A `CARD` email whose wrapper `agentCard` holds the
  `AgentCard` and which carries the identical card as an
  attachment named `agent-card.json`. If the card declares an
  avatar (Section 15.11), the reply also attaches the avatar
  bytes under the declared filename.
- Agents **SHOULD** also publish the card at the well-known HTTPS
  URL (Section 8) when they operate a site. Absence of a hosted
  card **MUST NOT** be treated as absence of the agent.

### 15.5. Error Handling

Operation failures are reply emails with `#op:TASK_ERROR`. The
wrapper `error` field follows the error model of
Section 3.3.2 (`code`, `message`, optional
`details`). The following column is proposed for the table in
Section 5.4:

| A2A Error Type | Email Representation |
| :--- | :--- |
| `TaskNotFoundError` | `TASK_ERROR` email, `error.code` verbatim |
| `TaskNotCancelableError` | `TASK_ERROR` email, plus a `TASK_UPDATE` with the current state |
| `PushNotificationNotSupportedError` | `TASK_ERROR` email (only when the card declares `pushNotifications: false`) |
| `UnsupportedOperationError` | `TASK_ERROR` email |
| `ContentTypeNotSupportedError` | `TASK_ERROR` email naming the media type |
| `InvalidAgentResponseError` | Raised locally by the receiver of a malformed reply; the counterparty is notified with a `TASK_ERROR` email |
| `ExtendedAgentCardNotConfiguredError` | `TASK_ERROR` email in the card exchange |
| `ExtensionSupportRequiredError` | `TASK_ERROR` email naming the extension URI |
| `VersionNotSupportedError` | `TASK_ERROR` email naming the supported `protocolVersion` |

A hard delivery failure (an SMTP 5xx delivery status notification)
means the endpoint does not exist: the client **MUST** mark any
cached card stale and **MUST NOT** retry the same mailbox
automatically. A soft failure (4xx) leaves the operation pending.

### 15.6. Parts and Artifacts

- A `text` `Part` is rendered in the human zone and carried
  verbatim in the JSON block.
- A `data` `Part` is carried verbatim in the JSON block.
- A `url` `Part` is carried verbatim. Receivers **MUST NOT** fetch
  it automatically.
- A `raw` `Part` is carried base64-encoded in the JSON block when
  small and text-safe; otherwise its bytes travel as a MIME
  attachment, the JSON entry carries `filename`, `mediaType`, and
  `metadata` of the form
  `{"emailAttachment": true, "sha256": "…"}`, and the receiver
  reconstructs the `Part` from the attachment.
- Each `Artifact` in a `Task` is carried in the JSON block. Every
  binary artifact `Part` additionally travels as an attachment,
  and the sender **MUST** include a manifest (artifact ID, name,
  filename, media type, SHA-256, size) so that receivers join
  attachments to artifacts by manifest, never by filename alone.

### 15.7. Authentication

This binding defines no on-wire credential. In particular, bearer
tokens **MUST NOT** be sent by email, in either direction, for any
reason, including authentication challenges.

Authentication is mailbox provenance:

1. The receiving provider asserts the sender mailbox (for example,
   a verified-correspondent or owner-address status, or SPF/DKIM
   alignment with DMARC pass).
2. The sender mailbox **MUST** equal the `mailto:` URL declared
   for this binding in a known Agent Card for that counterparty.
3. The subject **MUST** carry the Section 15.3.1 envelope, and
   the `From:` header **MUST** be the mailbox named in (2).

Mail from a known principal's address that carries no valid
envelope is mail from the human principal, never from their agent:
it **MUST NOT** be parsed for operations or auto-answered as A2A.
Mail that fails provenance receives no A2A reply and causes no
state change (fail-closed).

### 15.8. Agent Card Declaration

Agents **MUST** declare this binding in `supportedInterfaces`.
The first entry is the preferred interface:

```json
{
  "supportedInterfaces": [
    {
      "url": "mailto:agent@example.com",
      "protocolBinding": "EMAIL",
      "protocolVersion": "1.0"
    }
  ],
  "capabilities": {
    "streaming": false,
    "pushNotifications": true
  }
}
```

### 15.9. Idempotency and Duplicate Suppression

`SendMessage` processing **MUST** be idempotent on the pair
(sender mailbox, `messageId`). Receivers **MUST** suppress
duplicates by `Message-ID` header and by that pair, because
intermediate forwarding can rewrite headers while `messageId`
survives. Agents **MUST NOT** retry an operation by re-sending it
under a new `messageId`; to query a silent counterparty, clients
send `GetTask`.

### 15.10. Legacy Interop (Decode-Only)

An earlier, pre-binding bridge envelope carried six further
subject tokens (`#from:`, `#to:`, `#action:`, `#topic:`,
`#status:`, `#seq:`). They are not part of this binding: senders
**MUST NOT** emit them. Receivers **SHOULD** accept legacy mail
(a `#a2a:v1` subject carrying any of those tokens, with no JSON
block) as interop input, synthesising the `Message` from the text
body and mapping the legacy action token to an operation, per
the full binding specification's interop section. The legacy
labels carry no identity, its state values are non-normative
hints, and its counter is ignored.

### 15.11. Agent Avatar (Optional)

An agent **MAY** publish an avatar, a still image of its own
persona for display beside its name. Upstream `AgentCard.iconUrl`
carries a hosted URL only, which a mailbox-only agent cannot
rely on, so this binding adds an email carriage with no Layer 1
change:

- The card declares the avatar in the EMAIL extension `params`
  under `avatar`: `filename` (`agent-avatar.webp` / `.png` /
  `.jpg`), `mediaType` (`image/webp`, `image/png`, or
  `image/jpeg` only, never SVG), `sha256`, and `size`; `width`
  and `height` are optional and the image should be square. The
  file **MUST NOT** exceed 512 KiB.
- A `CARD` reply from an agent whose card declares an avatar
  attaches the bytes under the declared filename, beside
  `agent-card.json`. The declared `sha256` is the join key.
- Clients verify `sha256` and `size` before caching or display,
  cache keyed by (mailbox, `sha256`), and discard a mismatching
  avatar without invalidating the card. Absence of an avatar is
  never an error.
- The avatar is display only: never authentication, provenance,
  or an identity badge. Identity remains the mailbox
  (Section 15.7), and clients **MUST NOT** auto-fetch `iconUrl`
  over this binding.
- An agent that also hosts its avatar **SHOULD** set `iconUrl`
  as upstream defines it.
