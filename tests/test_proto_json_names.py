#!/usr/bin/env python3
"""Guard docs against invented ProtoJSON field names."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTO_PATH = REPO_ROOT / "specification" / "a2a.proto"
WHATS_NEW_PATH = REPO_ROOT / "docs" / "whats-new-v1.md"
SPEC_PATH = REPO_ROOT / "docs" / "specification.md"

# Proto3 JSON names are lowerCamelCase of the proto field name.
# See https://protobuf.dev/programming-guides/json/
_FIELD_RE = re.compile(
    r"^(?:repeated|optional|required|map<[^>]+>)?\s*"
    r"[A-Za-z0-9_.]+\s+([a-z][a-z0-9_]*)\s*=\s*\d+",
)


def proto_json_name(field_name: str) -> str:
    parts = field_name.split("_")
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


def message_fields(proto_text: str, message_name: str) -> dict[str, str]:
    header = re.search(
        rf"^message\s+{re.escape(message_name)}\s+\{{",
        proto_text,
        flags=re.MULTILINE,
    )
    if header is None:
        raise AssertionError(f"message {message_name} not found in {PROTO_PATH}")

    depth = 0
    body_started = False
    fields: dict[str, str] = {}
    for line in proto_text[header.start() :].splitlines():
        depth += line.count("{") - line.count("}")
        if not body_started:
            body_started = True
            continue
        if depth <= 0:
            break
        stripped = line.split("//", 1)[0].strip()
        match = _FIELD_RE.match(stripped)
        if match:
            name = match.group(1)
            fields[name] = proto_json_name(name)
    if not fields:
        raise AssertionError(f"no fields parsed for message {message_name}")
    return fields


def after_v1_pagination_fence(markdown: str) -> str:
    section = re.search(
        r"#### 4\. Pagination.*?\*\*After \(v1\.0\):\*\*\s*```(?:typescript)?\n(.*?)```",
        markdown,
        flags=re.DOTALL,
    )
    if section is None:
        raise AssertionError("v1.0 ListTasks After snippet not found")
    return section.group(1)


class ProtoJsonNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proto_text = PROTO_PATH.read_text(encoding="utf-8")
        cls.whats_new = WHATS_NEW_PATH.read_text(encoding="utf-8")
        cls.specification = SPEC_PATH.read_text(encoding="utf-8")
        cls.request_fields = message_fields(cls.proto_text, "ListTasksRequest")
        cls.response_fields = message_fields(cls.proto_text, "ListTasksResponse")

    def test_list_tasks_proto_fields_use_page_token_names(self) -> None:
        self.assertIn("page_size", self.request_fields)
        self.assertIn("page_token", self.request_fields)
        self.assertNotIn("cursor", self.request_fields)
        self.assertNotIn("limit", self.request_fields)
        self.assertEqual(self.request_fields["page_size"], "pageSize")
        self.assertEqual(self.request_fields["page_token"], "pageToken")

        self.assertIn("next_page_token", self.response_fields)
        self.assertIn("page_size", self.response_fields)
        self.assertNotIn("next_cursor", self.response_fields)
        self.assertEqual(self.response_fields["next_page_token"], "nextPageToken")
        self.assertEqual(self.response_fields["page_size"], "pageSize")

    def test_v1_after_pagination_snippet_uses_protojson_names(self) -> None:
        snippet = after_v1_pagination_fence(self.whats_new)
        request_json_names = set(self.request_fields.values())
        response_json_names = set(self.response_fields.values())

        self.assertIn("pageToken", request_json_names)
        self.assertIn("pageSize", request_json_names)
        self.assertIn("nextPageToken", response_json_names)
        self.assertIn("pageToken", snippet)
        self.assertIn("pageSize", snippet)
        self.assertIn("nextPageToken", snippet)

        self.assertNotIn("nextCursor", snippet)
        self.assertNotIn('"cursor"', snippet)
        self.assertNotIn("cursor:", snippet)
        self.assertNotIn("limit:", snippet)

    def test_specification_does_not_read_protocol_versions_on_agent_card(self) -> None:
        self.assertNotIn("protocolVersions", self.specification)
        self.assertIn("supportedInterfaces[].protocolVersion", self.specification)


if __name__ == "__main__":
    unittest.main()
