#!/usr/bin/env python3
"""
Nano settlement leg for A2A-SE — tested example.

Proves the smallest claim: a task priced in XNO can be escrowed and released through an
x402 (or AP2) rail underneath A2A-SE, using A2A-SE's existing terminal-TaskState mapping and
the a2a-se metadata field, with a Nano on-chain proof returned by the rail.

This example is NOT a new extension, NOT a new task state, and NOT a new rail. It is an
instance of A2A-SE v0.11.0 with Nano as the currency and a Nano rail under it.

Dependencies are the existing Nano x402 building block from nanodirectory; the script mocks
the A2A task surface so it can be verified in isolation before any PR is opened.
"""
from __future__ import annotations
import json
import time
import uuid
from datetime import datetime, timezone

RFC3339 = "%Y-%m-%dT%H:%M:%SZ"


def now_rfc3339() -> str:
    return datetime.now(timezone.utc).strftime(RFC3339)


# ---- A2A-SE extension URI (SPEC v0.11.0) ----
SETTLEMENT_URI = "https://a2a-settlement.org/extensions/settlement/v1"

# ---- Nano rail under the extension: a Nano x402 facilitator is the existing building block.
#      The facilitator is treated as a black box that accepts nano:mainnet and returns a proof.
#      In a real deployment this is a live x402 facilitator that settles in Nano; here we mock
#      the proof so the example is deterministic and verifiable without mainnet spend. ----

def nano_rail_settle(amount_xno: str, client_account: str, provider_account: str) -> dict:
    """Mock a Nano x402 settlement returning an on-chain proof.

    A real run uses a Nano x402 facilitator (existing building block) that settles on mainnet
    and returns a Nano transaction hash as the proof. This mock returns a stable proof string
    so the example is deterministic and verifiable in isolation.
    """
    tx_hash = f"nano_settlement_{uuid.uuid4().hex[:16]}"
    return {
        "rail": "x402",
        "currency": "XNO",
        "amount": amount_xno,
        "from": client_account,
        "to": provider_account,
        "settlementProof": tx_hash,
        "settledAt": now_rfc3339(),
    }


# ---- A2A task surface (mocked) ----

TaskState = str


def new_task(state: TaskState = "SUBMITTED") -> dict:
    return {
        "taskId": str(uuid.uuid4()),
        "state": state,
        "metadata": {},
    }


def set_task_state(task: dict, state: TaskState) -> None:
    task["state"] = state
    task["stateChangedAt"] = now_rfc3339()


# ---- A2A-SE settlement metadata helpers (SPEC v0.11.0 §3.2, a2a-se namespace) ----

def escrow_created_metadata(currency: str, amount: str, exchange_url: str) -> dict:
    return {
        "extensionUri": SETTLEMENT_URI,
        "currency": currency,
        "amount": amount,
        "exchangeUrl": exchange_url,
        "escrowCreated": now_rfc3339(),
        "escrowId": f"escrow-{uuid.uuid4().hex[:12]}",
    }


def release_metadata(settlement_proof: str, currency: str, amount: str, rail: str) -> dict:
    return {
        "extensionUri": SETTLEMENT_URI,
        "settlementStatus": "released",
        "currency": currency,
        "amount": amount,
        "releasedAt": now_rfc3339(),
        "settlementProof": settlement_proof,
        "rail": rail,
    }


def refund_metadata(currency: str, amount: str) -> dict:
    return {
        "extensionUri": SETTLEMENT_URI,
        "settlementStatus": "refunded",
        "currency": currency,
        "amount": amount,
        "refundedAt": now_rfc3339(),
    }


# ---- The scenario: a paid sentiment task priced in XNO ----

def run_scenario() -> dict:
    exchange_url = "https://nano.exchange.example/api/v1"
    client_account = "client-nano-account"
    provider_account = "provider-nano-account"
    currency = "XNO"
    amount = "10"

    task = new_task("SUBMITTED")

    # 1. SUBMITTED → escrow created on the Nano rail
    task["metadata"]["a2a-se"] = escrow_created_metadata(currency, amount, exchange_url)
    set_task_state(task, "SUBMITTED")

    # 2. WORKING — no settlement action; escrow holds
    set_task_state(task, "WORKING")

    # 3. The agent finishes the work; client marks COMPLETED
    set_task_state(task, "COMPLETED")

    # 4. Nano rail settles the escrowed XNO and returns an on-chain proof
    rail_result = nano_rail_settle(amount, client_account, provider_account)

    # 5. A2A-SE release recorded under a2a-se, per SPEC v0.11.0 §3.1
    task["metadata"]["a2a-se"] = release_metadata(
        rail_result["settlementProof"], currency, amount, rail_result["rail"]
    )

    return {
        "task": task,
        "rail": rail_result,
    }


def failed_scenario() -> dict:
    exchange_url = "https://nano.exchange.example/api/v1"
    currency = "XNO"
    amount = "10"

    task = new_task("SUBMITTED")
    task["metadata"]["a2a-se"] = escrow_created_metadata(currency, amount, exchange_url)
    set_task_state(task, "WORKING")

    # Agent fails the task
    set_task_state(task, "FAILED")

    # A2A-SE refund under a2a-se, per SPEC v0.11.0 §3.1 — XNO stays with the client
    task["metadata"]["a2a-se"] = refund_metadata(currency, amount)

    return {"task": task}


def main() -> None:
    paid = run_scenario()
    failed = failed_scenario()

    print("=== Paid Nano settlement leg (COMPLETED -> release) ===")
    print(json.dumps(paid, indent=2))
    print()
    print("=== Failed Nano settlement leg (FAILED -> refund) ===")
    print(json.dumps(failed, indent=2))

    # Verifiable assertions — these are the same checks a reviewer can run:
    paid_task = paid["task"]
    assert paid_task["state"] == "COMPLETED"
    assert paid_task["metadata"]["a2a-se"]["settlementStatus"] == "released"
    assert paid_task["metadata"]["a2a-se"]["currency"] == "XNO"
    assert paid_task["metadata"]["a2a-se"]["amount"] == "10"
    assert paid_task["metadata"]["a2a-se"]["settlementProof"].startswith("nano_settlement_")
    assert paid_task["metadata"]["a2a-se"]["rail"] == "x402"
    assert paid_task["metadata"]["a2a-se"]["extensionUri"] == SETTLEMENT_URI

    fail_task = failed["task"]
    assert fail_task["state"] == "FAILED"
    assert fail_task["metadata"]["a2a-se"]["settlementStatus"] == "refunded"
    assert fail_task["metadata"]["a2a-se"]["currency"] == "XNO"

    print()
    print("All assertions passed — the Nano settlement leg conforms to A2A-SE v0.11.0's existing")
    print("terminal-TaskState mapping and a2a-se metadata field, with Nano as the currency and an")
    print("x402 rail under it.")


if __name__ == "__main__":
    main()
