import re
import unittest

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTO_PATH = REPO_ROOT / 'specification' / 'a2a.proto'
WHATS_NEW_PATH = REPO_ROOT / 'docs' / 'whats-new-v1.md'
SPEC_PATH = REPO_ROOT / 'docs' / 'specification.md'

_FIELD_RE = re.compile(
    r'^\s*(?:optional|repeated|required)?\s*'
    r'(?:map\s*<[^>]+>|[\w.]+)\s+'
    r'([A-Za-z_]\w*)\s*=\s*\d+',
    re.MULTILINE,
)


def proto_json_name(field_name: str) -> str:
    parts = field_name.split('_')
    return parts[0] + ''.join(part.capitalize() for part in parts[1:])


def message_fields(proto_text: str, message_name: str) -> set[str]:
    marker = f'message {message_name}'
    start = proto_text.find(marker)
    if start < 0:
        raise AssertionError(f'message {message_name} not found in proto')
    brace = proto_text.find('{', start)
    if brace < 0:
        raise AssertionError(f'message {message_name} has no body')
    depth = 0
    for index, char in enumerate(proto_text[brace:], start=brace):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                body = proto_text[brace + 1 : index]
                body = re.sub(r'//.*?$', '', body, flags=re.MULTILINE)
                return set(_FIELD_RE.findall(body))
    raise AssertionError(f'message {message_name} is unclosed')


def after_v1_pagination_fence(markdown: str) -> str:
    section = re.search(
        r'#### 4\. Pagination.*?(?=#### |\Z)',
        markdown,
        re.DOTALL,
    )
    if not section:
        raise AssertionError('pagination section not found')
    fence = re.search(
        r'\*\*After \(v1\.0\):\*\*\s*```(?:typescript|ts|js)?\n(.*?)```',
        section.group(0),
        re.DOTALL,
    )
    if not fence:
        raise AssertionError('After (v1.0) pagination fence not found')
    return fence.group(1)


class ProtoJsonNameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proto = PROTO_PATH.read_text(encoding='utf-8')
        cls.whats_new = WHATS_NEW_PATH.read_text(encoding='utf-8')
        cls.spec = SPEC_PATH.read_text(encoding='utf-8')
        cls.request_fields = message_fields(cls.proto, 'ListTasksRequest')
        cls.response_fields = message_fields(cls.proto, 'ListTasksResponse')

    def test_list_tasks_proto_defines_pagination_fields(self):
        self.assertIn('page_size', self.request_fields)
        self.assertIn('page_token', self.request_fields)
        self.assertIn('page_size', self.response_fields)
        self.assertIn('next_page_token', self.response_fields)
        self.assertNotIn('cursor', self.request_fields)
        self.assertNotIn('limit', self.request_fields)
        self.assertNotIn('next_cursor', self.response_fields)

    def test_v1_after_pagination_uses_protojson_names(self):
        fence = after_v1_pagination_fence(self.whats_new)
        self.assertIn(proto_json_name('page_token'), fence)
        self.assertIn(proto_json_name('page_size'), fence)
        self.assertIn(proto_json_name('next_page_token'), fence)
        self.assertNotIn('nextCursor', fence)
        self.assertNotIn('limit:', fence)
        self.assertNotIn('"cursor"', fence)
        self.assertNotIn('cursor:', fence)

    def test_specification_does_not_read_agentcard_protocol_versions(self):
        self.assertNotIn('protocolVersions', self.spec)
        self.assertIn('supportedInterfaces[].protocolVersion', self.spec)


if __name__ == '__main__':
    unittest.main()
