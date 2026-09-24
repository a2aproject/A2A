# A Nano settlement leg for A2A-SE

**Tags:** docs, settlement, extension, nano

This note describes one concrete settlement currency — Nano (XNO) — that fits under the
**A2A Settlement Extension (A2A-SE) v0.11.0**, and gives a tested example that shows the
lifecycle end to end. It does not add a new extension, a new task state, or a new rail.

## Why Nano fits here

A2A-SE is currency-agnostic by design (SPEC v0.11.0 §2.2.1): the `currency` field exists so
that exchanges and rails can settle in any unit, and agents declare the currency they price in.
Nano is a natural fit for the agent-to-agent case A2A-SE targets — small per-request settlement
between opaque agents where a human is not at the till — because a settled Nano transaction
finalizes in seconds and carries no fee that would erase a small per-request price.

A Nano settlement leg is therefore **an instance of the existing extension**, not a competing
design: an agent that prices in XNO declares `"currency": "XNO"` on its skill pricing
(SPEC v0.11.0 §2.2), points the exchange/rail URL at a Nano-capable front, and uses A2A-SE's
existing terminal-TaskState mapping (SPEC v0.11.0 §3.1).

## AgentCard with a Nano-priced skill

A provider that accepts Nano declares the settlement extension and sets `currency` to `XNO`:

```json
{
  "name": "Nano Sentiment Agent",
  "version": "1.0.0",
  "url": "https://example.com/agents/nano-sentiment",
  "capabilities": {
    "streaming": true,
    "extensions": [
      {
        "uri": "https://a2a-settlement.org/extensions/settlement/v1",
        "description": "Accepts Nano (XNO) settlement via a Nano-capable A2A-SE exchange/rail",
        "required": false,
        "params": {
          "exchangeUrls": [
            "https://nano.exchange.example/api/v1"
          ],
          "preferredExchange": "https://nano.exchange.example/api/v1",
          "accountIds": {
            "https://nano.exchange.example/api/v1": "provider-nano-account"
          },
          "pricing": {
            "sentiment-analysis": {
              "baseTokens": 10,
              "model": "per-request",
              "currency": "XNO"
            }
          }
        }
      }
    ]
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": [
    {
      "id": "sentiment-analysis",
      "name": "Sentiment Analysis",
      "description": "Sentiment analysis priced in Nano.",
      "tags": ["sentiment", "nlp", "text-classification"]
    }
  ]
}
```

## Task lifecycle with a Nano rail under A2A-SE

A2A carries the task; A2A-SE carries the settlement metadata under the `a2a-se` namespace;
a Nano rail (an x402 or AP2 facilitator that settles in Nano, or a Nano-capable exchange front)
moves the value. The lifecycle is A2A-SE's existing mapping (SPEC v0.11.0 §3.1):

```
A2A TaskState       Settlement action              Nano rail
─────────────       ────────────────────         ─────────
SUBMITTED    ──►    Escrow created on the         client locks XNO with the rail
                    exchange (XNO: available → held)

WORKING      ──►    No settlement action           escrow holds while the agent works

INPUT_REQUIRED ──► No settlement action            escrow holds across multi-turn

COMPLETED    ──►    Client releases escrow         rail settles XNO to the provider;
                    (XNO: held → provider's available)  on-chain proof stored under a2a-se

FAILED       ──►    Client refunds escrow          rail refunds / does-not-settle;
                    (XNO: held → client's available)   XNO stays with client

CANCELED     ──►    Client refunds escrow          rail refunds; XNO stays with client

REJECTED     ──►    Client refunds escrow          rail refunds if escrow was created
```

## Settlement metadata for the Nano case

A paid task starts with the standard A2A-SE escrow metadata under `a2a-se`, plus the Nano
rail annotation the example adds:

```json
{
  "jsonrpc": "2.0",
  "method": "SendMessage",
  "id": "1",
  "params": {
    "message": {
      "messageId": "1",
      "role": "ROLE_USER",
      "parts": [{"text": "Analyze the sentiment of this transcript"}],
      "metadata": {
        "a2a-se": {
          "extensionUri": "https://a2a-settlement.org/extensions/settlement/v1",
          "currency": "XNO",
          "amount": "10",
          "exchangeUrl": "https://nano.exchange.example/api/v1",
          "escrowCreated": "2026-09-24T23:50:00Z",
          "escrowId": "escrow-nano-001"
        }
      }
    }
  }
}
```

A message on task COMPLETED records the released settlement with the Nano proof the rail returns:

```json
{
  "jsonrpc": "2.0",
  "method": "SendMessage",
  "id": "2",
  "params": {
    "message": {
      "messageId": "2",
      "role": "ROLE_AGENT",
      "parts": [{"text": "Sentiment result here"}],
      "metadata": {
        "a2a-se": {
          "extensionUri": "https://a2a-settlement.org/extensions/settlement/v1",
          "settlementStatus": "released",
          "currency": "XNO",
          "amount": "10",
          "releasedAt": "2026-09-24T23:50:40Z",
          "settlementProof": "nano:tx_hash_returned_by_the_rail",
          "rail": "x402"
        }
      }
    }
  }
}
```

The fields above are A2A-SE fields in the `a2a-se` namespace. `settlementProof` and `rail` are
the Nano-specific annotation this example adds; they live in the same namespace so a settlement-
unaware caller still parses the message.

## Tested example

The file `nano_a2a_se_example.py` is the smallest thing that proves the lifecycle end to end. It
ties three pieces together with the A2A-SE extension URI and the `a2a-se` metadata field, and
mocks the Nano rail so it is verifiable in isolation before any live mainnet call:

1. **A Nano rail** (an existing Nano x402 building block from nanodirectory, mocked here)
   accepts a `nano:mainnet` settlement and returns an on-chain proof.
2. **An A2A task** moves to COMPLETED (or FAILED for the refund path).
3. **A2A-SE release/refund** is recorded under `a2a-se`, per SPEC v0.11.0 §3.1.

Run it as `python3 nano_a2a_se_example.py`. The assertions at the end are the same checks a
reviewer can run.

To make the example live, replace the mocked `nano_rail_settle` with a live Nano x402 facilitator
call; the A2A task state transitions and the `a2a-se` metadata do not change.

## Relationship to the settlement extension proposal

A2A issue #2198 asks a maintainer to sponsor `experimental-ext-settlement` so release, refund,
and dispute are defined once under a2aproject governance and conformance-testable. The Nano
example here is an instance of that direction: it uses the settlement extension URI and the
existing lifecycle mapping, and it adds Nano as one currency a rail underneath can settle. A
maintainer who sponsors the settlement extension can adopt this as the Nano rail case in the
extension's docs.

A2A issue #2202 already merged a partner listing entry for `x402-list`, showing the project
accepts protocol-level payment integrations. A Nano settlement-leg example is the same kind of
entry, narrow and tested.

## References checked live

- `a2aproject/A2A` documentation tree and CONTRIBUTING — `docs:` PRs accepted; open docs PRs
  2246, 2232, 2222, 2219, 2204 show the pattern.
- `a2a-settlement/a2a-settlement` SPEC.md v0.11.0 — extension URI
  (`https://a2a-settlement.org/extensions/settlement/v1`), currency field (§2.2.1),
  lifecycle mapping (§3.1), `a2a-se` metadata field (§3.2).
- A2A issue #2198 (widrss) and comment #1 (chopmob-cloud) — the settlement-extension ask and
  the rail-side support.
- A2A issue #2202 — merged partner listing for `x402-list`.
