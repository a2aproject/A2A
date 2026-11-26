# A2A over Email — Layer-3 Protocol Binding

**Status:** Draft binding for the `jonathancruzate/A2A` fork.  
**Upstream:** `a2aproject/A2A` — HEAD `9fff3e08ab33bb7674e7d98fc7c08ae8592bb4bd` (shallow clone in this repo).  
**Binding identifier:** `EMAIL` · **Binding version:** `1.0` · **Spec:** [`SPEC.md`](SPEC.md)

## Why email, why now

Until 2026-11-05, email was the *legacy* lane in Muse's bridge: the
fallback for counterparties with no hosted A2A endpoint. Every other
binding in upstream A2A assumes the agent runs a server:

| Binding | What the agent must operate |
| --- | --- |
| JSON-RPC | HTTPS endpoint, TLS, bearer-token store |
| gRPC | gRPC server, TLS, token store |
| HTTP+JSON | HTTPS endpoint, TLS, bearer-token store |

That assumption no longer holds for Muse agents. **Every Muse now
gets a first-class mailbox — `<agent>@muse.ai` (Muse Mail)** — verified
2026-11-05 for Muse itself as `jonathan-cruzate-assistant@muse.ai`.
A mailbox is an endpoint:

- **Addressable without hosting.** `mailto:<agent>@muse.ai` needs no
  Cloudflare Worker, no public HTTPS listener, no port, no deploy.
- **Store-and-forward by construction.** The mail system queues,
  retries, and delivers asynchronously — exactly A2A's async task
  model (§3.3.3, §3.5 upstream). No polling server to keep alive.
- **Identity-bearing.** The mailbox *is* the authenticated principal
  in Muse Mail (permanent always-allow counterparties; owner
  addresses are the human's own and are a separate thing). Provenance
  comes from the transport, not from a bearer token pasted into a header.
- **Universally reachable.** Counterparties that cannot receive native
  A2A at all — EX.0 is the live example: it has published no Agent Card
  / endpoint, so Muse → EX.0 native outbound does not exist — are
  reachable by email today, and email reaches agents behind NAT,
  on mobile, or intermittently online.

So this fork inverts the old priority: **email is a first-class
Layer-3 binding**, specified to the same standard as JSON-RPC / gRPC /
HTTP+JSON, carrying the *unchanged* Layer-1 data model and Layer-2
abstract operations. It does not invent a new task model, a new
envelope semantics, or a parallel agent.

```text
Layer 1  Task / Message / Part / Artifact / AgentCard   — UNCHANGED
Layer 2  SendMessage / GetTask / ListTasks / CancelTask /
         GetAgentCard / push / streaming semantics       — UNCHANGED
Layer 3  JSON-RPC | gRPC | HTTP+JSON | EMAIL | SPREADSHEET — TWO NEW
```

**Bindings are per-counterparty capability choices**, declared in
each counterparty's Agent Card — never a global transport pick.
EMAIL is the binding for agents that have their own mailbox
(Muses on `…@muse.ai`; EX.0's email lane). Its sibling in this
fork, [`../spreadsheet-binding/`](../spreadsheet-binding/), is the
binding for agents whose platform gives them first-party Workspace
access but no agent email and no hostable endpoint — Gemini Spark
is the defining case. The same Layer-1 objects and Layer-2
semantics run over both, unchanged; a client uses the first
mutually supported `supportedInterfaces` entry per counterparty.

## What is in this folder

| File | Contents |
| --- | --- |
| `SPEC.md` | The binding specification (normative). Operation mapping, subject envelope, body format, threading, Parts/Artifacts, auth, async, errors. |
| `agent-card-email.example.json` | A complete Agent Card whose *preferred* interface is EMAIL. Drop-in shape for any Muse agent. |
| `reference/a2a_email.py` | Stdlib-only Python reference codec: canonical `Message`/`Task` dict ⇄ (subject, body). Self-test included. |
| `LOCAL-ADOPTION.md` | Inventory of Muse's local surfaces (protocol, card, skills, hooks, client, Worker) and the specific change each needs to adopt this binding. No local surface is edited by this staging copy. |

## The binding in one paragraph

One A2A operation = one email. The `Subject` carries a compact,
machine-readable envelope — `#a2a:v1 #op:… #mid:… #task:… #ctx:…`,
four tokens, each a projection of a canonical field — so a watcher
can route without opening the body. Identity rides on the mail
headers and the Agent Card, task state on the `Task` object, and
ordering on the reply chain and `status.timestamp`; the subject
carries none of those. The body renders the first text Part for
humans, then carries the full canonical object as a delimited JSON
block that is authoritative on conflict. Replies thread with
`In-Reply-To` / `References`; the thread *is* the `contextId`.
Bearer tokens are **never** sent by email; provenance is mailbox
identity, fail-closed. Streaming is `false`; push notifications
are realised as reply emails.

Historical note: the envelope generalises the bridge envelope Muse
ran in production from 2026-09-30 (`#a2a:v1 #from:… #to:… #action:…
#topic:… #status:… #seq:…`). That fuller form is legacy interop
history only — receivers may decode it (SPEC §16), senders never
emit it.

## Relationship to the old plans

- This binding **supersedes** the 2026-10-25 “canonical-A2A cleanup” in
  `~/workspace/agent-bridge/PROTOCOL.md`, which slated the `#a2a:v1`
  email envelope, the EMAIL interface, and the bridge-envelope
  extension for retirement in favour of HTTP-only canonical A2A. That
  premise — email as non-canonical scaffolding — is reversed: the
  envelope is now the subject encoding of a canonical binding.
- It **generalises** the 2026-11-05 Muse Mail migration
  (`MUSE-MAIL-MIGRATION.md`): that switch moved one lane's origination
  to `…@muse.ai` byte-identically. This binding specifies the wire for
  *any* Muse-to-Muse (or Muse-to-any-A2A-agent) email exchange.
