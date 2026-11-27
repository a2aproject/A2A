# A2A over Spreadsheet — Layer-3 Protocol Binding

**Status:** Draft, proposed and experimental. Not an official a2aproject binding.
**Upstream:** `a2aproject/A2A` — HEAD `9fff3e08ab33bb7674e7d98fc7c08ae8592bb4bd`.
**Binding identifier:** `SPREADSHEET` · **Binding version:** `1.0` · **Spec:** [`SPEC.md`](SPEC.md)
**Origin:** this binding generalises a production agent-to-agent spreadsheet lane into a platform-neutral specification. Any agent platform with shared-spreadsheet access and no mailbox can implement it.

## Why a spreadsheet, why this counterparty

Bindings in this fork are **per-counterparty capability choices**,
declared in each agent's Agent Card — not a single global transport:

| Counterparty capability | Binding |
| --- | --- |
| Agent has its own mailbox (Muses on `…@muse.ai`, EX.0's email lane) | **EMAIL** (`../email-binding/`) |
| Agent's platform gives it first-party Workspace access but **no agent email and no hosted endpoint** | **SPREADSHEET** (this folder) |
| Agent runs an HTTPS server | JSON-RPC / gRPC / HTTP+JSON (upstream) |

Gemini Spark is the defining case of the second row. It cannot
communicate via email as an agent: it has no agent mailbox to send
from or be addressed at, and it cannot run a server. What it *does*
have, natively and without per-call approval prompts, is Google
Workspace — Gmail as a *trigger*, and Google Sheets as a surface it
can read and append to inside unattended scheduled runs. Two proven
facts force this binding's shape:

1. **Custom-MCP tool calls stall Gemini Spark's unattended runs** on
   per-call “Allow/Deny” prompts (verified 2026-10-09 – 2026-10-12,
   reads included). A first-party Sheet append raises no such prompt.
2. **Structured data passes; prose instructions are blocked** by
   Gemini policy in unattended runs. So rows carry
   `kind + parts_json` (data only), and all standing instructions
   live in Gemini Spark's own A2A skill (`gemini-spark-a2a-spreadsheet`) — never in the transport.

A shared Sheet is therefore Gemini Spark's mailbox: append-only tabs are
the wire, a one-line alert email is only the doorbell (§3), and each
agent's own store — not the sheet — stays the system of record.

```text
Layer 1  Task / Message / Part / Artifact / AgentCard   — UNCHANGED
Layer 2  SendMessage / GetTask / ListTasks / CancelTask /
         GetAgentCard / push / streaming semantics       — UNCHANGED
Layer 3  JSON-RPC | gRPC | HTTP+JSON | EMAIL | SPREADSHEET — TWO NEW
```

The same Layer-1 objects and Layer-2 semantics run over EMAIL and
SPREADSHEET unchanged. A client picks, per counterparty, the first
mutually supported `supportedInterfaces` entry in that
counterparty's card. Nothing about a Task changes when its binding
does.

## What is in this folder

| File | Contents |
| --- | --- |
| `SPEC.md` | The binding specification (normative). Sheet/tab/column contract, canonical mapping, doorbell, Card tab, cancellation on an append-only medium, auth, cleanup, async, errors. |
| `agent-card-spreadsheet.example.json` | A complete Agent Card (Gemini Spark) whose *preferred* — and only A2A — interface is SPREADSHEET. |
| `reference/a2a_spreadsheet.py` | Stdlib-only Python reference codec: canonical `Message`/`Task` dict ⇄ sheet row dicts, plus in-memory `GetTask`/`ListTasks`/cancel logic. Self-test included. |
| `../skills/gemini-spark-a2a-spreadsheet/` | The Gemini Spark adoption skill (SKILL.md-first) for running this binding. |

## The binding in one paragraph

One A2A `SendMessage` = one appended row in the shared sheet's
**Requests** tab: `appended_at | message_id | task_id |
context_id | kind | parts_json | metadata_json` (sheet layout
**v2** — every column is a canonical A2A field name, or the
object's metadata in a `metadata_json` column), where
`(message_id, metadata a2a.token)` is the idempotency key, `kind`
is the dotted skill invocation (`flights.search`,
`finance.quote`, …), and `parts_json` is the Message's canonical
Parts array as structured JSON — never prose. The responder
answers with one row in **Results** (`appended_at | task_id |
context_id | status | task_json | metadata_json`), `status` the
verbatim `TASK_STATE_*` value of `Task.status.state`; free-form,
non-task communication goes in **Notes**. Appending a Requests row rings the
doorbell: a bound Apps Script `On change` trigger (15 s
CacheService debounce) sends a fixed-subject `A2A-Event` email to
the account the responder watches, whose email-triggered schedule
processes the queue immediately — live end-to-end latency ~74 s
(2026-11-01), versus up to an hour under the retired hourly poll.
Email here is a *wake signal only*; it carries no A2A payload.
Consumers commit matched rows to their own store, then delete them:
the sheet is a lane, never the record. (The live deployment below
still runs sheet layout v1 columns and migrates separately;
readers accept both layouts — see SPEC Appendix B.)

## Live deployment (the proof, not a proposal)

- Sheet: **“A2A - Results”**, keyed everywhere by spreadsheet ID +
  tab names, never by display title (renamed from “Muse Bridge —
  Results” 2026-11-01 with zero mechanical breakage).
- Doorbell: `onBridgeChange` Apps Script, trigger *From spreadsheet
  — On change*, subject exactly `A2A-Event`.
- Responder: Gemini Spark schedule **“Process Muse bridge
  requests”** (UI title “A2A”), email-triggered on
  `subject:"A2A-Event"`, Active; legacy hourly schedule Paused.
- Sender/poller: Muse `mcp-queue.py` (enqueue + Requests mirror) and
  `sheet-poller.py` behind the `spark-sheet-poll` hook (300 s); the
  live lane still runs layout v1, matching rows on its
  `(request_id, token)` pair → commit to KV → delete Results row →
  prune finished Requests rows → ingest and clear Notes.
