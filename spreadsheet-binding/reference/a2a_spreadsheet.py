#!/usr/bin/env python3
"""
a2a_spreadsheet — A2A SPREADSHEET binding v1.0 reference codec (stdlib only).

Sheet layout **v2** (SPEC.md §4): every column is a canonical A2A
field name, or the object's canonical `metadata` serialised in a
`metadata_json` column. Encoders write v2 only; decoders accept v2
and legacy layout v1 (SPEC Appendix B, read-side compatibility).

  encode_request(message, kind, token=None) -> Requests row (v2 dict)
  decode_request_row(row)                   -> (envelope, Message)
  encode_result(task, token=...)            -> Results row (v2 dict)
  decode_result_row(row)                    -> (envelope, Task|None, error|None)
  encode_note / decode_note_row             -> Notes row <-> Message
  encode_cancel / encode_get_agent_card     -> reserved-kind Requests rows
  encode_card_row / decode_card_row         -> Card tab row <-> AgentCard
  card_layout_version(card)                 -> "2" | "1" (SPEC §4.0)
  get_task(requests, results, id, token)    -> Task | None   (SPEC §8.3, local read)
  list_tasks(requests, results, ...)        -> [Task, ...]   (SPEC §8.4, local scan)
  parse_spreadsheet_url / spreadsheet_urn   -> endpoint identity (§2.1)

Rows are dicts keyed by column names; `row_to_cells` / `cells_to_row`
convert to/from positional cell lists in header order (pass the
matching *_COLUMNS_V2 or *_COLUMNS_V1 list). No network, no Sheets
API, no credentials: the caller's provider adapter moves rows; this
module is the wire codec + the row-free read operations.
"""

from __future__ import annotations

import json
import re
import secrets
import uuid
from datetime import datetime, timezone

BINDING = "SPREADSHEET/1.0"
A2A_VERSION = "1.0"
DOORBELL_SUBJECT = "A2A-Event"
LAYOUT_VERSION = "2"

# Sheet layout v2 headers (SPEC §4) — the write form.
REQUEST_COLUMNS = ["appended_at", "message_id", "task_id", "context_id",
                   "kind", "parts_json", "metadata_json"]
RESULT_COLUMNS = ["appended_at", "task_id", "context_id", "status",
                  "task_json", "metadata_json"]
NOTE_COLUMNS = ["appended_at", "message_id", "parts_json", "metadata_json"]
CARD_COLUMNS = ["appended_at", "card_version", "card_json"]

# Sheet layout v1 headers (SPEC Appendix B) — decode only.
REQUEST_COLUMNS_V1 = ["appended_at", "request_id", "token", "kind",
                      "params_json", "context"]
RESULT_COLUMNS_V1 = ["appended_at", "request_id", "token", "kind",
                     "status", "result_json"]
NOTE_COLUMNS_V1 = ["appended_at", "priority", "note"]

RESERVED_KINDS = {"a2a.get_task", "a2a.list_tasks", "a2a.cancel",
                  "a2a.get_agent_card", "a2a.get_extended_agent_card"}

# Results status vocabulary -> canonical Task state (SPEC §7.2).
# Verbatim TASK_STATE_* passes through; legacy spellings decode only.
STATUS_TO_STATE = {
    "done": "TASK_STATE_COMPLETED",
    "error": "TASK_STATE_FAILED",
    "working": "TASK_STATE_WORKING",
    "cancelled": "TASK_STATE_CANCELED",
    "input_required": "TASK_STATE_INPUT_REQUIRED",
    "auth_required": "TASK_STATE_AUTH_REQUIRED",
    "submitted": "TASK_STATE_SUBMITTED",
    "rejected": "TASK_STATE_REJECTED",
}
KNOWN_STATES = set(STATUS_TO_STATE.values()) | {"TASK_STATE_UNSPECIFIED"}
TERMINAL_STATES = {"TASK_STATE_COMPLETED", "TASK_STATE_FAILED",
                   "TASK_STATE_CANCELED", "TASK_STATE_REJECTED"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_token() -> str:
    """Per-message a2a.token: >= 64 bits of entropy (SPEC §6.5)."""
    return "t-" + secrets.token_hex(8)


def row_layout(row: dict, kind: str) -> str:
    """Detect a row dict's layout version from its column names."""
    if kind == "request":
        return "2" if "message_id" in row else "1"
    if kind == "result":
        return "2" if "task_json" in row else "1"
    if kind == "note":
        return "2" if "parts_json" in row else "1"
    return "2"  # Card columns are identical in both layouts


def parse_spreadsheet_url(url: str) -> str:
    """Extract the spreadsheet ID — the endpoint identity (SPEC §2.1)."""
    m = re.search(r"/spreadsheets/d/([^/]+)", url or "")
    if m:
        return m.group(1)
    m = re.fullmatch(r"urn:a2a:spreadsheet:(.+)", (url or "").strip())
    if m:
        return m.group(1)
    raise ValueError(f"not a SPREADSHEET binding URL: {url!r}")


def spreadsheet_url(spreadsheet_id: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"


def spreadsheet_urn(spreadsheet_id: str) -> str:
    return f"urn:a2a:spreadsheet:{spreadsheet_id}"


def row_to_cells(row: dict, columns: list[str]) -> list[str]:
    return ["" if row.get(c) is None else str(row.get(c)) for c in columns]


def cells_to_row(cells: list, columns: list[str]) -> dict:
    cells = list(cells) + [""] * (len(columns) - len(cells))
    return {c: cells[i] for i, c in enumerate(columns)}


def _json_cell(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _parse_cell(raw, default, what: str):
    try:
        return json.loads(raw) if raw else default
    except json.JSONDecodeError as e:
        raise ValueError(f"{what} is not valid JSON: {e}") from e


# ---------------------------------------------------------------- Requests

def encode_request(message: dict, *, kind: str, token: str | None = None,
                   appended_at: str | None = None) -> dict:
    """Encode a canonical Message as a v2 Requests row (SPEC §§4.1, 6).

    parts_json is the Message's canonical Parts array, verbatim.
    metadata_json is the Message's metadata; the per-message auth
    token rides there as `a2a.token` (§6.5), and referenceTaskIds
    ride there too. `token=` supplies/overrides the token.
    """
    metadata = dict(message.get("metadata") or {})
    if token is not None:
        metadata["a2a.token"] = token
    elif not metadata.get("a2a.token"):
        metadata["a2a.token"] = new_token()
    refs = message.get("referenceTaskIds")
    if refs:
        metadata.setdefault("referenceTaskIds", refs)
    return {
        "appended_at": appended_at or _now(),
        "message_id": str(message.get("messageId") or uuid.uuid4()),
        "task_id": str(message.get("taskId") or ""),
        "context_id": str(message.get("contextId") or ""),
        "kind": kind,
        "parts_json": _json_cell(message.get("parts") or []),
        "metadata_json": _json_cell(metadata),
    }


def decode_request_row(row: dict) -> tuple[dict, dict]:
    """Decode a Requests row (v2 or v1) -> (envelope, canonical Message).

    SPEC §6 (v2) and Appendix B (v1 legacy decode).
    """
    if row_layout(row, "request") == "1":
        return _decode_request_row_v1(row)
    parts = _parse_cell(row.get("parts_json"), [], "parts_json")
    if not isinstance(parts, list):
        raise ValueError("parts_json must be a JSON array of Parts (SPEC §6.3)")
    metadata = _parse_cell(row.get("metadata_json"), {}, "metadata_json")
    if not isinstance(metadata, dict):
        raise ValueError("metadata_json must be a JSON object (SPEC §4.1)")
    msg = {"messageId": str(row.get("message_id")), "role": "ROLE_USER",
           "parts": parts}
    if row.get("task_id"):
        msg["taskId"] = str(row["task_id"])
    if row.get("context_id"):
        msg["contextId"] = str(row["context_id"])
    refs = metadata.pop("referenceTaskIds", None)
    if refs:
        msg["referenceTaskIds"] = refs
    if metadata:
        msg["metadata"] = metadata
    env = {"layout": "2", "message_id": str(row.get("message_id")),
           "task_id": str(row.get("task_id") or "") or None,
           "context_id": str(row.get("context_id") or "") or None,
           "token": metadata.get("a2a.token"), "kind": row.get("kind"),
           "appended_at": row.get("appended_at")}
    return env, msg


def _decode_request_row_v1(row: dict) -> tuple[dict, dict]:
    """Legacy layout v1 Requests decode (SPEC Appendix B)."""
    params = _parse_cell(row.get("params_json"), {}, "params_json")
    if not isinstance(params, dict):
        raise ValueError("params_json must be a JSON object (layout v1, SPEC §6.3)")
    data = {k: v for k, v in params.items() if not k.startswith("_")}
    parts = [{"data": data, "mediaType": "application/json"}]
    if isinstance(params.get("_text"), str):
        parts.insert(0, {"text": params["_text"]})
    if isinstance(params.get("_url"), str):
        parts.append({"url": params["_url"], "mediaType": "text/uri-list"})
    ctx_raw = (row.get("context") or "").strip()
    context_id, refs = None, None
    if ctx_raw.startswith("{"):
        try:
            cj = json.loads(ctx_raw)
            context_id, refs = cj.get("contextId"), cj.get("referenceTaskIds")
        except json.JSONDecodeError:
            context_id = ctx_raw  # opaque label, v1 §6.5(c)
    elif ctx_raw:
        context_id = ctx_raw  # bare contextId or opaque label
    msg = {"messageId": str(row.get("request_id")), "role": "ROLE_USER",
           "parts": parts}
    if context_id:
        msg["contextId"] = context_id
    if refs:
        msg["referenceTaskIds"] = refs
    metadata = {}
    if isinstance(params.get("_a2a"), dict):
        metadata["a2a"] = params["_a2a"]
    if row.get("token"):
        metadata["a2a.token"] = row["token"]
    if metadata:
        msg["metadata"] = metadata
    env = {"layout": "1", "message_id": str(row.get("request_id")),
           "request_id": str(row.get("request_id")),
           "task_id": str(row.get("request_id")),  # v1: Task.id == request_id
           "context_id": context_id, "token": row.get("token"),
           "kind": row.get("kind"), "appended_at": row.get("appended_at"),
           "context": ctx_raw or None}
    return env, msg


def encode_cancel(*, target_task_id: str, target_token: str,
                  token: str | None = None, message_id: str | None = None,
                  context_id: str | None = None,
                  appended_at: str | None = None) -> dict:
    """CancelTask as an append-only v2 Requests row (SPEC §8.5.1).

    The target is identified by its canonical task_id in the data
    Part; ownership is proven by `a2a.target_token` in metadata —
    the a2a.token of the original message that created the task.
    """
    msg = {"messageId": message_id or str(uuid.uuid4()), "role": "ROLE_USER",
           "parts": [{"data": {"target_task_id": str(target_task_id)},
                      "mediaType": "application/json"}],
           "metadata": {"a2a.target_token": target_token}}
    if context_id:
        msg["contextId"] = context_id
    return encode_request(msg, kind="a2a.cancel", token=token,
                          appended_at=appended_at)


def encode_get_agent_card(*, token: str | None = None,
                          message_id: str | None = None,
                          appended_at: str | None = None) -> dict:
    """CARD-REQUEST fallback row (SPEC §3.2)."""
    msg = {"messageId": message_id or str(uuid.uuid4()), "role": "ROLE_USER",
           "parts": [{"data": {}, "mediaType": "application/json"}]}
    return encode_request(msg, kind="a2a.get_agent_card", token=token,
                          appended_at=appended_at)


# ---------------------------------------------------------------- Results

def encode_result(task: dict, *, token: str,
                  appended_at: str | None = None) -> dict:
    """Encode a canonical Task as a v2 Results row (SPEC §§4.2, 7).

    status is the verbatim TASK_STATE_* state. metadata_json mirrors
    the Task's metadata and echoes the triggering message's
    a2a.token (§9.2). A FAILED task whose metadata carries an
    `error` object is encoded with task_json = the error object
    (§11), as upstream returns errors, not Tasks.
    """
    state = (task.get("status") or {}).get("state", "TASK_STATE_UNSPECIFIED")
    metadata = dict(task.get("metadata") or {})
    metadata["a2a.token"] = token
    err = metadata.get("error")
    if state == "TASK_STATE_FAILED" and isinstance(err, dict):
        payload = err
    else:
        payload = dict(task)
        payload["metadata"] = metadata
    return {
        "appended_at": appended_at or _now(),
        "task_id": str(task.get("id") or ""),
        "context_id": str(task.get("contextId") or ""),
        "status": state,
        "task_json": _json_cell(payload),
        "metadata_json": _json_cell(metadata),
    }


def decode_result_row(row: dict) -> tuple[dict, dict | None, dict | None]:
    """Decode a Results row (v2 or v1) -> (envelope, Task|None, error|None)."""
    if row_layout(row, "result") == "1":
        return _decode_result_row_v1(row)
    raw_status = (row.get("status") or "").strip()
    state = STATUS_TO_STATE.get(raw_status, raw_status)
    if state not in KNOWN_STATES:
        raise ValueError(f"unknown Results status: {raw_status!r}")
    payload = _parse_cell(row.get("task_json"), {}, "task_json")
    metadata = _parse_cell(row.get("metadata_json"), {}, "metadata_json")
    env = {"layout": "2", "task_id": str(row.get("task_id") or "") or None,
           "context_id": str(row.get("context_id") or "") or None,
           "token": metadata.get("a2a.token"),
           "appended_at": row.get("appended_at"),
           "status": raw_status, "state": state}
    if isinstance(payload, dict) and "code" in payload and "status" not in payload:
        return env, None, payload  # §11 error object
    if not isinstance(payload, dict) or "id" not in payload:
        raise ValueError("task_json must be a canonical Task object (SPEC §7.3)")
    return env, payload, None


def _decode_result_row_v1(row: dict) -> tuple[dict, dict | None, dict | None]:
    """Legacy layout v1 Results decode (SPEC §7.2/§7.3, Appendix B)."""
    raw_status = (row.get("status") or "").strip()
    state = STATUS_TO_STATE.get(raw_status, raw_status)
    if state and state not in KNOWN_STATES:
        raise ValueError(f"unknown Results status: {raw_status!r}")
    payload = _parse_cell(row.get("result_json"), {}, "result_json")
    env = {"layout": "1", "request_id": str(row.get("request_id")),
           "message_id": str(row.get("request_id")),
           "task_id": str(row.get("request_id")),  # v1: Task.id == request_id
           "token": row.get("token"), "kind": row.get("kind"),
           "appended_at": row.get("appended_at"),
           "status": raw_status, "state": state}
    if raw_status == "error" or (isinstance(payload, dict) and "code" in payload
                                 and "id" not in payload and state == "TASK_STATE_FAILED"
                                 and set(payload) <= {"code", "message", "details"}):
        return env, None, payload
    if isinstance(payload, dict) and "status" in payload and "id" in payload:
        task = payload  # full canonical Task form
    else:  # legacy plain answer object -> wrap (§7.3 interop)
        task = {
            "id": str(row.get("request_id")),
            "status": {"state": state or "TASK_STATE_UNSPECIFIED"},
            "artifacts": [{"artifactId": f"{row.get('request_id')}-result",
                           "parts": [{"data": payload,
                                      "mediaType": "application/json"}]}],
            "history": [{"messageId": str(row.get("request_id")),
                         "role": "ROLE_USER", "parts": []}],
        }
    return env, task, None


# ---------------------------------------------------------------- Notes / Card

def encode_note(message: dict, *, appended_at: str | None = None) -> dict:
    """Encode a bare (non-task) Message as a v2 Notes row (SPEC §4.3).

    Priority rides in metadata_json as `a2a.priority` (a plain
    `priority` metadata key is accepted as input and canonicalised).
    """
    metadata = dict(message.get("metadata") or {})
    priority = metadata.pop("a2a.priority", None) or metadata.pop("priority", None)
    metadata["a2a.priority"] = priority or "normal"
    return {"appended_at": appended_at or _now(),
            "message_id": str(message.get("messageId") or uuid.uuid4()),
            "parts_json": _json_cell(message.get("parts") or []),
            "metadata_json": _json_cell(metadata)}


def decode_note_row(row: dict) -> dict:
    """Decode a Notes row (v2 or v1) -> canonical non-task Message (§8.8)."""
    if row_layout(row, "note") == "1":
        priority = row.get("priority") or "normal"
        return {"messageId": None, "role": "ROLE_AGENT",
                "parts": [{"text": row.get("note", "")}],
                "metadata": {"a2a.priority": priority, "priority": priority}}
    parts = _parse_cell(row.get("parts_json"), [], "parts_json")
    metadata = _parse_cell(row.get("metadata_json"), {}, "metadata_json")
    msg = {"role": "ROLE_AGENT", "parts": parts}
    if row.get("message_id"):
        msg["messageId"] = str(row["message_id"])
    if metadata:
        msg["metadata"] = metadata
    return msg


def encode_card_row(card: dict, *, appended_at: str | None = None) -> dict:
    """Card tab row; card_json is the canonical AgentCard (SPEC §4.4)."""
    return {"appended_at": appended_at or _now(),
            "card_version": str(card.get("version", "")),
            "card_json": _json_cell(card)}


def decode_card_row(row: dict) -> dict:
    return _parse_cell(row.get("card_json"), {}, "card_json")


def card_layout_version(card: dict) -> str:
    """The deployment's declared sheet layout (SPEC §4.0).

    Read from the SPREADSHEET extension's params.sheetLayout inside
    card_json; absence means layout v1.
    """
    for ext in (card.get("capabilities") or {}).get("extensions") or []:
        params = ext.get("params") or {}
        if "sheetLayout" in params:
            return str(params["sheetLayout"])
    return "1"


# ------------------------------------------------------- local reads (§8.3/8.4)

def _task_link_ids(task: dict) -> set[str]:
    """messageIds a Task is linked to, via its history (SPEC §7.1)."""
    return {str(m.get("messageId")) for m in task.get("history") or []
            if isinstance(m, dict) and m.get("messageId") is not None}


def get_task(requests: list[dict], results: list[dict],
             task_id: str, token: str) -> dict | None:
    """GetTask as a local read (SPEC §8.3). None == TaskNotFoundError.

    A Results row whose a2a.token echo does not match the presented
    token is treated as absent exactly like a missing row: existence
    is never leaked to a non-holder of the token (§9.2).
    """
    latest = terminal = None
    for r in results:  # row order is authoritative (§10.3)
        env, task, err = decode_result_row(r)
        if env.get("task_id") != str(task_id) or env.get("token") != token:
            continue
        if err is not None:
            terminal = {"id": str(task_id),
                        "status": {"state": "TASK_STATE_FAILED"},
                        "metadata": {"error": err}}
            latest = terminal
        elif task is not None:
            latest = task
            if task["status"]["state"] in TERMINAL_STATES:
                terminal = task
    if latest is not None:
        return terminal or latest
    for req in requests:
        env, _msg = decode_request_row(req)
        if env.get("task_id") == str(task_id) and env.get("token") == token:
            return {"id": str(task_id),
                    "status": {"state": "TASK_STATE_SUBMITTED"}}
    return None


def list_tasks(requests: list[dict], results: list[dict], *,
               context_id: str | None = None,
               state: str | None = None) -> list[dict]:
    """ListTasks as a local scan (SPEC §8.4)."""
    tokens: dict[str, str] = {}
    order: list[str] = []
    for r in results:  # answered tasks first, in row order (§10.3)
        env, task, _err = decode_result_row(r)
        tid = env.get("task_id")
        if not tid or tid in tokens:
            continue
        # Link back to the originating message via Task history,
        # to learn the token that authenticates this task.
        linked = _task_link_ids(task) if task else set()
        tok = None
        for req in requests:
            renv, _m = decode_request_row(req)
            if renv["message_id"] in linked:
                tok = renv.get("token")
                break
        tokens[tid] = env.get("token") or tok
        order.append(tid)
    for req in requests:  # then tasks known only as submitted
        env, _msg = decode_request_row(req)
        if env.get("task_id") and env["task_id"] not in tokens:
            tokens[env["task_id"]] = env.get("token")
            order.append(env["task_id"])
    out = []
    for tid in order:
        task = get_task(requests, results, tid, tokens.get(tid))
        if task is None:
            continue
        if context_id and task.get("contextId") != context_id:
            continue
        if state and task["status"]["state"] != state:
            continue
        out.append(task)
    return out


def is_terminal(task: dict | None) -> bool:
    return bool(task) and task.get("status", {}).get("state") in TERMINAL_STATES


# ---------------------------------------------------------------- self-test

if __name__ == "__main__":
    SHEET_ID = "<SPREADSHEET_ID>"
    assert parse_spreadsheet_url(spreadsheet_url("<SPREADSHEET_ID>")) \
        == "<SPREADSHEET_ID>"
    assert parse_spreadsheet_url(spreadsheet_urn(SHEET_ID)) == SHEET_ID
    print("ENDPOINT PARSE: OK")

    # ---- v2 request round-trip (§§4.1, 6): canonical columns only
    original = {
        "messageId": "42", "role": "ROLE_USER", "contextId": "bridge-ctx-7",
        "referenceTaskIds": ["task-7"],
        "parts": [{"data": {"origin": "JFK", "destination": "FLL",
                            "date": "2026-11-14"},
                   "mediaType": "application/json"},
                  {"text": "Window seat if tied"}],
    }
    row = encode_request(original, kind="flights.search", token="t-9f2c-test",
                         appended_at="2026-11-01T14:00:00Z")
    assert list(row) == REQUEST_COLUMNS and row_layout(row, "request") == "2"
    print("REQUEST ROW (v2):", row_to_cells(row, REQUEST_COLUMNS))
    env, decoded = decode_request_row(cells_to_row(
        row_to_cells(row, REQUEST_COLUMNS), REQUEST_COLUMNS))
    assert env["kind"] == "flights.search" and env["token"] == "t-9f2c-test"
    assert env["task_id"] is None and env["context_id"] == "bridge-ctx-7"
    assert decoded["messageId"] == "42" and decoded["contextId"] == "bridge-ctx-7"
    assert decoded["referenceTaskIds"] == ["task-7"]  # via metadata_json (§6.5)
    assert decoded["parts"] == original["parts"]
    assert decoded["metadata"]["a2a.token"] == "t-9f2c-test"
    print("REQUEST (v2) ROUND-TRIP: OK")

    # ---- v1 legacy Requests row still decodes (Appendix B)
    legacy_req = {"appended_at": "2026-11-01T14:00:00Z", "request_id": "42",
                  "token": "t-9f2c-test", "kind": "flights.search",
                  "params_json": '{"origin": "JFK", "destination": "FLL", "date": "2026-11-14"}',
                  "context": "bridge-ctx-7"}
    lenv, lmsg = decode_request_row(legacy_req)
    assert lenv["layout"] == "1" and lmsg["messageId"] == "42"
    assert lmsg["parts"][0]["data"]["destination"] == "FLL"
    assert lmsg["metadata"]["a2a.token"] == "t-9f2c-test"
    print("REQUEST (v1 legacy) DECODE: OK")

    # ---- v2 task round-trip (§§4.2, 7): task_id column, history linkage
    task = {
        "id": "task-42", "contextId": "bridge-ctx-7",
        "status": {"state": "TASK_STATE_COMPLETED",
                   "timestamp": "2026-11-01T14:01:14Z"},
        "artifacts": [{"artifactId": "task-42-result",
                       "parts": [{"data": {"flights": [{"carrier": "Example Air",
                                                         "price": 189}],
                                            "currency": "USD"},
                                  "mediaType": "application/json"}]}],
        "history": [original],
    }
    rrow = encode_result(task, token="t-9f2c-test",
                         appended_at="2026-11-01T14:01:14Z")
    assert list(rrow) == RESULT_COLUMNS and row_layout(rrow, "result") == "2"
    assert rrow["task_id"] == "task-42" and rrow["status"] == "TASK_STATE_COMPLETED"
    print("RESULT ROW (v2):", row_to_cells(rrow, RESULT_COLUMNS)[:4], "…")
    renv, rtask, rerr = decode_result_row(cells_to_row(
        row_to_cells(rrow, RESULT_COLUMNS), RESULT_COLUMNS))
    assert rerr is None and renv["token"] == "t-9f2c-test"
    assert rtask["id"] == "task-42" and rtask["status"] == task["status"]
    assert rtask["artifacts"] == task["artifacts"]
    assert rtask["metadata"]["a2a.token"] == "t-9f2c-test"  # §9.2 echo
    assert _task_link_ids(rtask) == {"42"}
    print("RESULT (v2) ROUND-TRIP: OK")

    # ---- v1 legacy Results rows still decode (§7.2/§7.3, Appendix B)
    legacy = {"appended_at": "2026-11-01T14:01:14Z", "request_id": "42",
              "token": "t-9f2c-test", "kind": "flights.search", "status": "done",
              "result_json": '{"currency": "USD", "cheapest": 189}'}
    lenv2, ltask, lerr2 = decode_result_row(legacy)
    assert lerr2 is None and lenv2["layout"] == "1"
    assert ltask["status"]["state"] == "TASK_STATE_COMPLETED"
    assert ltask["artifacts"][0]["parts"][0]["data"]["cheapest"] == 189
    print("RESULT (v1 legacy done/plain) DECODE: OK")

    # ---- local reads over v2 rows: GetTask / ListTasks (§8.3/§8.4)
    requests, results = [row], [rrow]
    assert get_task(requests, results, "task-42", "t-9f2c-test")["id"] == "task-42"
    assert get_task(requests, results, "task-42", "wrong-token") is None  # §9.2 no leak
    assert get_task(requests, results, "task-999", "t-9f2c-test") is None
    pending = encode_request(
        {"messageId": "43", "role": "ROLE_USER", "taskId": "task-43",
         "parts": [{"data": {"symbol": "NVDA"}, "mediaType": "application/json"}]},
        kind="finance.quote", token="t-pend-1", appended_at="2026-11-01T14:05:00Z")
    assert get_task([pending], [], "task-43", "t-pend-1")["status"]["state"] \
        == "TASK_STATE_SUBMITTED"
    assert [t["id"] for t in list_tasks(requests, results)] == ["task-42"]
    assert [t["id"] for t in list_tasks(requests + [pending], results)] \
        == ["task-42", "task-43"]
    print("GET_TASK / LIST_TASKS (v2): OK")

    # ---- cancellation in v2 terms (§8.5.1): task_id + metadata proof
    crow = encode_cancel(target_task_id="task-42", target_token="t-9f2c-test",
                         token="t-cancel-1", message_id="44",
                         context_id="bridge-ctx-7",
                         appended_at="2026-11-01T14:02:00Z")
    assert list(crow) == REQUEST_COLUMNS
    cenv, cmsg = decode_request_row(crow)
    assert cenv["kind"] == "a2a.cancel"
    assert cmsg["parts"][0]["data"] == {"target_task_id": "task-42"}
    assert cmsg["metadata"]["a2a.target_token"] == "t-9f2c-test"
    assert cmsg["metadata"]["a2a.token"] == "t-cancel-1"  # cancel's own token
    print("CANCEL ROW (v2) ROUND-TRIP: OK")

    # ---- error mapping (§11): FAILED + error object in task_json
    erow = encode_result(
        {"id": "task-42", "status": {"state": "TASK_STATE_FAILED"},
         "metadata": {"error": {"code": "UnsupportedOperationError",
                                "message": "unknown kind: bogus.kind"}}},
        token="t-9f2c-test")
    eenv, etask, eerr = decode_result_row(erow)
    assert erow["status"] == "TASK_STATE_FAILED" and etask is None
    assert eerr["code"] == "UnsupportedOperationError"
    print("ERROR ROW (v2) ROUND-TRIP: OK")

    # ---- notes + card in v2 terms (§§4.3, 4.4)
    nrow = encode_note({"messageId": "n-1", "role": "ROLE_AGENT",
                        "parts": [{"text": "Heads-up: fares refresh at 15:00 UTC."}],
                        "metadata": {"priority": "info"}},
                       appended_at="2026-11-01T14:03:00Z")
    assert list(nrow) == NOTE_COLUMNS
    nmsg = decode_note_row(cells_to_row(row_to_cells(nrow, NOTE_COLUMNS),
                                        NOTE_COLUMNS))
    assert nmsg["parts"][0]["text"].startswith("Heads-up")
    assert nmsg["metadata"]["a2a.priority"] == "info"  # priority is metadata now
    legacy_note = {"appended_at": "2026-11-01T14:03:00Z", "priority": "info",
                   "note": "Heads-up: fares refresh at 15:00 UTC."}
    assert decode_note_row(legacy_note)["metadata"]["a2a.priority"] == "info"
    card = {"name": "Gemini Spark", "version": "1.0.0",
            "capabilities": {"streaming": False, "pushNotifications": True,
                             "extendedAgentCard": False,
                             "extensions": [{
                                 "uri": "https://a2a-protocol.org/bindings/spreadsheet/v1",
                                 "required": False,
                                 "params": {"sheetLayout": "2",
                                            "doorbellSubject": "A2A-Event"}}]},
            "supportedInterfaces": [{"protocolBinding": "SPREADSHEET",
                                     "protocolVersion": "1.0",
                                     "url": spreadsheet_url("<SPREADSHEET_ID>")}]}
    crow2 = encode_card_row(card)
    assert list(crow2) == CARD_COLUMNS
    assert decode_card_row(crow2) == card
    assert card_layout_version(card) == "2"          # declared in card_json (§4.0)
    assert card_layout_version({"name": "Old"}) == "1"  # absence == v1
    print("NOTE + CARD (v2) ROUND-TRIP: OK")
    print("SELF-TEST: PASS (v2 request + v2 task + v1 legacy request/result "
          "+ get/list + v2 cancel + v2 error + v2 note/card)")
