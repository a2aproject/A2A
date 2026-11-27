#!/usr/bin/env python3
"""
a2a_email — A2A EMAIL binding v1.0 reference codec (stdlib only).

Implements SPEC.md §§6-7, 8, 10 for this binding:
  encode_message(message, ...) -> (subject, body)
  encode_task(task, ...)       -> (subject, body)
  encode_error(...)            -> (subject, body)
  decode_email(subject, body)  -> dict(envelope, wrapper, message, task, error, agentCard)
  build_headers(...)           -> dict of RFC 5322 headers (Message-ID, In-Reply-To, References, X-A2A-*)
  parse_subject(subject)       -> envelope dict

Design notes
------------
- Canonical objects are plain dicts in upstream proto-JSON shape
  (messageId, taskId, contextId, role, parts[], status{state,...}).
  This module never mutates Layer-1 fields; binding metadata lives
  only in the wrapper object (§7.3).
- Zone J (the delimited JSON block) is authoritative; the subject
  envelope is a routing projection of it.
- No network, no mail library, no credentials. Sending/reading mail
  is the caller's provider adapter (Muse Mail, IMAP/SMTP, ...).
"""

from __future__ import annotations

import json
import re
import uuid

BINDING = "EMAIL/1.0"
A2A_VERSION = "1.0"

OPS = {
    "SEND_MESSAGE", "GET_TASK", "LIST_TASKS", "CANCEL_TASK",
    "GET_AGENT_CARD", "GET_EXTENDED_AGENT_CARD",
    "TASK_UPDATE", "TASK_ERROR", "CARD", "LIST_TASKS_RESULT",
}
TASK_STATES = {
    "TASK_STATE_UNSPECIFIED", "TASK_STATE_SUBMITTED", "TASK_STATE_WORKING",
    "TASK_STATE_COMPLETED", "TASK_STATE_FAILED", "TASK_STATE_CANCELED",
    "TASK_STATE_INPUT_REQUIRED", "TASK_STATE_REJECTED", "TASK_STATE_AUTH_REQUIRED",
}

# The token regex stays tolerant on decode: it also captures the
# legacy pre-binding tokens (from/to/action/topic/status/seq) so
# parse_subject can surface them for SPEC §16 interop. Encoding
# never emits them — see _subject.
_TOKEN_RE = re.compile(r"#(from|to|op|action|topic|status|seq|mid|task|ctx):([^\s]+)")
_JSON_RE = re.compile(
    r"^---A2A-JSON---\s*$\n(.*?)\n^---END-A2A-JSON---\s*$",
    re.MULTILINE | re.DOTALL,
)


def _text_of(parts: list[dict] | None) -> str:
    out = []
    for p in parts or []:
        if isinstance(p, dict) and isinstance(p.get("text"), str):
            out.append(p["text"])
    return "\n\n".join(out)


def _subject(*, op, mid, task_id, context_id, human_suffix=None) -> str:
    """The clean normative envelope (SPEC §6): marker + four tokens.

    Identity rides on the RFC 5322 From:/To: headers, task state on
    the Zone J Task object — neither appears in the subject."""
    subj = (
        f"#a2a:v1 #op:{op} #mid:{mid} "
        f"#task:{task_id or '-'} #ctx:{context_id or '-'}"
    )
    if human_suffix:
        subj += f" -- {human_suffix}"
    return subj


def _body(wrapper: dict, human_text: str) -> str:
    human = (human_text or "").strip()
    if not human:
        human = f"A2A {wrapper['operation']} (see JSON block below)."
    return (
        f"{human}\n\n---A2A-JSON---\n"
        f"{json.dumps(wrapper, indent=2, ensure_ascii=False, sort_keys=False)}\n"
        f"---END-A2A-JSON---\n"
    )


def _wrapper(*, operation, message_id, task_id, context_id,
             message=None, task=None, error=None, agent_card=None,
             extra: dict | None = None) -> dict:
    w = {
        "a2aBinding": BINDING,
        "a2aVersion": A2A_VERSION,
        "operation": operation,
        "messageId": message_id,
        "taskId": task_id,
        "contextId": context_id,
        "message": message,
        "task": task,
        "error": error,
    }
    if agent_card is not None:
        w["agentCard"] = agent_card
    if extra:
        w.update(extra)
    return w


# ---------------------------------------------------------------- encode

def encode_message(message: dict, *, operation: str = "SEND_MESSAGE",
                   human_suffix: str | None = None) -> tuple[str, str]:
    """Encode a canonical Message dict as an EMAIL-binding (subject, body).

    Absent message['taskId'] means 'create a new task' (SPEC §6.2/§8.1).
    Addressing (From:/To:) is the caller's mail layer: the envelope
    carries no sender/recipient tokens (SPEC §4/§6).
    """
    if operation not in OPS:
        raise ValueError(f"unknown operation: {operation!r}")
    mid = message.get("messageId") or str(uuid.uuid4())
    msg = dict(message)
    msg.setdefault("messageId", mid)
    task_id = msg.get("taskId")
    context_id = msg.get("contextId")
    w = _wrapper(operation=operation, message_id=mid, task_id=task_id,
                 context_id=context_id, message=msg)
    subj = _subject(op=operation, mid=mid, task_id=task_id,
                    context_id=context_id, human_suffix=human_suffix)
    return subj, _body(w, _text_of(msg.get("parts")))


def encode_task(task: dict, *, operation: str = "TASK_UPDATE",
                message_id: str | None = None,
                human_suffix: str | None = None) -> tuple[str, str]:
    """Encode a canonical Task dict (status update / GetTask reply)."""
    if operation not in ("TASK_UPDATE", "LIST_TASKS_RESULT"):
        raise ValueError(f"encode_task operation must be TASK_UPDATE/LIST_TASKS_RESULT, got {operation!r}")
    status = (task.get("status") or {}).get("state")
    if status is not None and status not in TASK_STATES:
        raise ValueError(f"unknown task state: {status!r}")
    status_msg = (task.get("status") or {}).get("message") or {}
    mid = message_id or status_msg.get("messageId") or str(uuid.uuid4())
    human = _text_of(status_msg.get("parts")) or f"Task {task.get('id')}: {status or 'TASK_STATE_UNSPECIFIED'}"
    w = _wrapper(operation=operation, message_id=mid, task_id=task.get("id"),
                 context_id=task.get("contextId"), task=task)
    subj = _subject(op=operation, mid=mid, task_id=task.get("id"),
                    context_id=task.get("contextId"),
                    human_suffix=human_suffix)
    return subj, _body(w, human)


def encode_error(error: dict, *, task: dict | None = None,
                 message_id: str | None = None,
                 task_id: str | None = None, context_id: str | None = None,
                 human_suffix: str | None = None) -> tuple[str, str]:
    """Encode an A2A error (SPEC §14.1). `error` = {code, message, details?}."""
    mid = message_id or str(uuid.uuid4())
    eff_task_id = task_id or (task or {}).get("id")
    eff_ctx = context_id or (task or {}).get("contextId")
    human = f"A2A error {error.get('code')}: {error.get('message', '')}".strip()
    w = _wrapper(operation="TASK_ERROR", message_id=mid, task_id=eff_task_id,
                 context_id=eff_ctx, task=task, error=error)
    subj = _subject(op="TASK_ERROR", mid=mid, task_id=eff_task_id,
                    context_id=eff_ctx, human_suffix=human_suffix)
    return subj, _body(w, human)


def encode_agent_card(card: dict, *, message_id: str | None = None,
                      context_id: str | None = None,
                      human_suffix: str | None = None) -> tuple[str, str]:
    """Encode a CARD reply (SPEC §3a). Caller also attaches agent-card.json."""
    mid = message_id or str(uuid.uuid4())
    human = f"Agent Card for {card.get('name', 'agent')} (v{card.get('version', '?')}). See JSON block / agent-card.json attachment."
    w = _wrapper(operation="CARD", message_id=mid, task_id=None,
                 context_id=context_id, agent_card=card)
    subj = _subject(op="CARD", mid=mid, task_id=None,
                    context_id=context_id, human_suffix=human_suffix)
    return subj, _body(w, human)


# ---------------------------------------------------------------- headers

def build_headers(*, sender_domain: str, message_id: str, context_id: str | None = None,
                  in_reply_to: str | None = None, references: list[str] | None = None) -> dict:
    """RFC 5322 / threading headers for one binding email (SPEC §§5, 10.1, 15)."""
    h = {
        "Message-ID": f"<a2a-{message_id}@{sender_domain}>",
        "X-A2A-Binding": BINDING,
        "X-A2A-Version": A2A_VERSION,
    }
    if in_reply_to:
        h["In-Reply-To"] = in_reply_to
    refs = list(references or [])
    if in_reply_to and in_reply_to not in refs:
        refs.append(in_reply_to)
    if refs:
        h["References"] = " ".join(refs)
    if context_id:
        h["X-A2A-Context"] = context_id
    return h


# ---------------------------------------------------------------- decode

def parse_subject(subject: str) -> dict:
    """Parse the #a2a:v1 subject envelope. Returns {} if not binding mail."""
    if not subject or "#a2a:v1" not in subject:
        return {}
    env = {"version": "v1"}
    for key, val in _TOKEN_RE.findall(subject):
        env[key] = int(val) if key == "seq" and val.isdigit() else (None if val == "-" else val)
    return env


def decode_email(subject: str, body: str) -> dict:
    """Decode an EMAIL-binding email into its canonical payload.

    Returns:
      {envelope, wrapper, operation, message, task, error, agentCard, humanText}
    Raises ValueError on binding mail whose Zone J is missing/malformed
    (caller maps that to InvalidAgentResponseError, SPEC §7.3/§14).
    Non-binding mail (no #a2a:v1) returns envelope={} and wrapper=None —
    SPEC §12.2: treat as human-principal mail, never as A2A.
    """
    env = parse_subject(subject or "")
    if not env:
        return {"envelope": {}, "wrapper": None, "operation": None,
                "message": None, "task": None, "error": None,
                "agentCard": None, "humanText": (body or "").strip()}
    m = _JSON_RE.search(body or "")
    if not m:
        raise ValueError("A2A email missing ---A2A-JSON--- block")
    try:
        wrapper = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise ValueError(f"A2A JSON block is not valid JSON: {e}") from e
    if wrapper.get("a2aBinding") not in (BINDING, "EMAIL/1.0"):
        raise ValueError(f"unexpected a2aBinding: {wrapper.get('a2aBinding')!r}")
    human = (body or "")[: m.start()].strip()
    return {
        "envelope": env,
        "wrapper": wrapper,
        "operation": wrapper.get("operation") or env.get("op"),
        "message": wrapper.get("message"),
        "task": wrapper.get("task"),
        "error": wrapper.get("error"),
        "agentCard": wrapper.get("agentCard"),
        "humanText": human,
    }


def is_terminal(task: dict | None) -> bool:
    state = ((task or {}).get("status") or {}).get("state")
    return state in {"TASK_STATE_COMPLETED", "TASK_STATE_FAILED",
                     "TASK_STATE_CANCELED", "TASK_STATE_REJECTED"}


# ---------------------------------------------------------------- self-test

if __name__ == "__main__":
    original = {
        "messageId": "11111111-2222-3333-4444-555555555555",
        "role": "ROLE_USER",
        "contextId": "ctx-7d31-example",
        "parts": [
            {"text": "Please relay this calendar block to the work calendar."},
            {"data": {"descriptor": "travel time", "window": "2026-11-06T13:25:00-05:00/2026-11-06T14:00:00-05:00"},
             "mediaType": "application/json"},
        ],
    }
    subj, body = encode_message(original, operation="SEND_MESSAGE")
    print("SUBJECT:", subj)
    dec = decode_email(subj, body)
    assert dec["operation"] == "SEND_MESSAGE", dec
    assert dec["message"] == {**original}, f"message round-trip mismatch:\n{dec['message']}\nvs\n{original}"
    # Clean envelope (SPEC §6): marker + op/mid/task/ctx, nothing else.
    assert set(dec["envelope"]) == {"version", "op", "mid", "task", "ctx"}, dec["envelope"]
    assert dec["envelope"]["op"] == "SEND_MESSAGE"
    assert dec["envelope"]["mid"] == original["messageId"]
    assert dec["envelope"]["task"] is None
    assert dec["envelope"]["ctx"] == "ctx-7d31-example"
    assert "seq" not in dec["wrapper"]
    assert "calendar block" in dec["humanText"]
    print("MESSAGE ROUND-TRIP: OK")

    task = {
        "id": "task-51-example",
        "contextId": "ctx-7d31-example",
        "status": {"state": "TASK_STATE_COMPLETED",
                   "message": {"messageId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                               "role": "ROLE_AGENT",
                               "parts": [{"text": "Relayed and confirmed."}]},
                   "timestamp": "2026-11-06T14:05:00Z"},
        "artifacts": [],
        "history": [original],
    }
    subj2, body2 = encode_task(task)
    print("SUBJECT2:", subj2)
    dec2 = decode_email(subj2, body2)
    assert dec2["task"] == task, "task round-trip mismatch"
    assert set(dec2["envelope"]) == {"version", "op", "mid", "task", "ctx"}, dec2["envelope"]
    assert dec2["envelope"]["task"] == "task-51-example"
    # Task state lives in the Task object, never in the subject (§6).
    assert dec2["task"]["status"]["state"] == "TASK_STATE_COMPLETED"
    assert is_terminal(dec2["task"]) is True
    print("TASK ROUND-TRIP: OK")

    esubj, ebody = encode_error(
        {"code": "TaskNotFoundError", "message": "no such task: task-nope"},
        task_id="task-nope", context_id="ctx-7d31-example")
    dec3 = decode_email(esubj, ebody)
    assert dec3["operation"] == "TASK_ERROR" and dec3["error"]["code"] == "TaskNotFoundError"
    print("ERROR ROUND-TRIP: OK")
    print("SELF-TEST: PASS (message + task + error round-trips)")
