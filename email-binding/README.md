# A2A over Email - Layer-3 Protocol Binding

**Status:** Draft, proposed and experimental. Not an official
a2aproject binding. The binding identifier follows the upstream
governance namespace as a proposal (see
`docs/topics/extension-and-binding-governance.md` in this repo).
**Upstream:** `a2aproject/A2A` v1.0 specification.
**Binding identifier:** `EMAIL` - **Binding version:** `1.0`
**Spec:** [`SPEC.md`](SPEC.md)

## Why email

Every standard A2A binding assumes the agent runs a server:

| Binding | What the agent must operate |
| --- | --- |
| JSON-RPC | HTTPS endpoint, TLS, credential store |
| gRPC | gRPC server, TLS, credential store |
| HTTP+JSON | HTTPS endpoint, TLS, credential store |

Many agents have no hostable endpoint but do have a mailbox of
their own. A mailbox is an endpoint:

- **Addressable without hosting.** A `mailto:` address needs no
  public listener, port, or deploy.
- **Store-and-forward by construction.** The mail system queues,
  retries, and delivers asynchronously, matching A2A's async
  task model.
- **Identity-bearing.** The mailbox address in the Agent Card is
  the identity. Provenance comes from the transport (the
  provider's allowed-correspondent status, or SPF and DKIM
  alignment), not from a credential sent in a message.
- **Universally reachable.** Email reaches agents behind NAT, on
  mobile, or intermittently online.

This binding specifies email as a Layer-3 binding to the same
standard as the standard bindings, carrying the unchanged
Layer-1 data model and Layer-2 abstract operations. It invents
no new task model.

```text
Layer 1  Task / Message / Part / Artifact / AgentCard   - UNCHANGED
Layer 2  SendMessage / GetTask / ListTasks / CancelTask /
         GetAgentCard / push / streaming semantics       - UNCHANGED
Layer 3  JSON-RPC | gRPC | HTTP+JSON | EMAIL             - ONE NEW
```

**Bindings are per-counterparty capability choices**, declared
in each agent's Agent Card. A client selects the first mutually
supported entry in a peer's `supportedInterfaces`. This folder
is the EMAIL binding. A sibling spreadsheet binding, for agents
whose platform offers shared documents but no mailbox, lives in
`../spreadsheet-binding/`.

## What is in this folder

| File | Contents |
| --- | --- |
| `SPEC.md` | The binding specification (normative). Operation mapping, subject envelope, body format, threading, Parts and Artifacts, provenance, async, errors, conformance. |
| `agent-card-email.example.json` | A complete Agent Card whose preferred interface is EMAIL, with placeholder values only (`agent@example.com`). Replace every value with your own agent's. |
| `reference/a2a_email.py` | Stdlib-only Python reference codec: canonical Message and Task dicts to and from (subject, body). Self-test included. |

## The binding in one paragraph

One A2A operation is one email. The subject carries a compact
envelope, `#a2a:v1 #op:... #mid:... #task:... #ctx:...`, four
tokens, each a projection of a canonical field, so routing can
happen without opening the body. Identity rides on the mail
headers and the Agent Card, task state on the Task object, and
ordering on the reply chain and `status.timestamp`. The body
renders the text parts for humans, then carries the full
canonical object as a delimited JSON block that is authoritative
on conflict. Replies thread with In-Reply-To and References, and
the thread is the contextId. No credential is ever sent by
email. Streaming is false, and push notifications are realised
as reply emails.

## Discovery, the upstream way

Upstream A2A offers three discovery strategies, and this binding
supports all three, in the order a client supports them:

1. **Well-known URI:** `https://<domain>/.well-known/agent-card.json`
2. **Curated registry:** a registry returns cards by skill or tag
3. **Direct configuration:** a user configures a peer's mailbox
   or card directly. This is how a specific peer is added, and
   it is a separate step from adopting the protocol. A worked
   add-a-peer template ships with the Muse adoption skill,
   maintained in the contributor's fork (see the pull request
   description), not in this repository.

Email adds one transport-native form of the third strategy: a
`GET_AGENT_CARD` email to a configured mailbox, answered by a
`CARD` email carrying the card (SPEC section 3).
