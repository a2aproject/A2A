"""Custom MkDocs macros for A2A documentation.

This module provides macros for rendering Protocol Buffer definitions
as markdown tables.
"""

from pathlib import Path
from typing import Any

from proto_schema_parser.ast import (
    Comment,
    Enum,
    EnumValue,
    Field,
    MapField,
    Message,
    Method,
    OneOf,
    Service,
)
from proto_schema_parser.parser import Parser
from tabulate import tabulate


# -----------------------------------------------------------------------------
# Configuration & Helpers
# -----------------------------------------------------------------------------

TYPE_MAP = {
    'string': 'string',
    'int32': 'integer',
    'int64': 'integer',
    'bool': 'boolean',
    'bytes': 'bytes',
    'double': 'float',
    'float': 'float',
    'google.protobuf.Struct': 'object',
    'google.protobuf.Timestamp': 'timestamp',
    'google.protobuf.Value': 'any',
    'google.protobuf.Empty': 'empty',
}

# -----------------------------------------------------------------------------
# Main Macros
# -----------------------------------------------------------------------------


def define_env(env):
    """Define custom macros for MkDocs."""

    def _parse_proto(file_path: str):
        """Parses a .proto file and returns the AST with comments attached."""
        full_path = Path(env.conf['docs_dir']).parent / file_path
        if not full_path.exists():
            raise FileNotFoundError(f'Proto not found: {file_path}')
        ast = Parser().parse(full_path.read_text(encoding='utf-8'))
        _attach_comments(ast.file_elements)
        return ast.file_elements

    @env.macro
    def proto_to_table(
        message_name: str, proto_file: str = 'specification/a2a.proto'
    ) -> str:
        """Parses a .proto file and renders a message table."""
        try:
            elements = _parse_proto(proto_file)
        except FileNotFoundError as e:
            return f'**Error:** {e}'

        # Find the specific message object
        target_message = _find_type(elements, message_name, Message)
        if not target_message:
            return f'**Error:** Message `{message_name}` not found.'

        # Extract data
        rows = []
        oneof_groups = {}  # Map[oneof_name] -> List[field_names]

        # Iterate over elements inside the message
        # elements can be Field, MapField, OneOf, Enum, Message, etc.
        for el in target_message.elements:
            # Handle Standard/Map Fields
            if isinstance(el, Field | MapField):
                rows.append(_process_field(el))
            elif isinstance(el, OneOf):
                for oneof_el in el.elements:
                    if isinstance(oneof_el, Field):
                        # Process field normally
                        row = _process_field(oneof_el, is_oneof=True)
                        rows.append(row)
                        # Add display name to group tracker
                        oneof_groups.setdefault(el.name, []).append(
                            row[0].strip('`')  # Remove code ticks for the note
                        )

        if not rows:
            return 'None'

        # Generate Output
        output = []

        # Message Description
        msg_desc = _extract_comments(target_message)
        if msg_desc:
            output.append(msg_desc)
            output.append('')

        # Render Table
        headers = ['Field', 'Type', 'Required', 'Description']
        output.append(tabulate(rows, headers, tablefmt='github'))

        # Add OneOf Notes
        if oneof_groups:
            output.append('')
            for _, fields in oneof_groups.items():
                if len(fields) > 1:
                    field_list = ', '.join(f'`{f}`' for f in fields)
                    output.append(
                        f'**Note:** A `{message_name}` MUST contain exactly one of the following: {field_list}'
                    )

        return '\n'.join(output)

    @env.macro
    def proto_enum_to_table(
        enum_name: str, proto_file: str = 'specification/a2a.proto'
    ):
        """Parses a .proto file and renders an Enum table."""
        try:
            elements = _parse_proto(proto_file)
            el = _find_type(elements, enum_name, Enum)
            if not el:
                return f'**Error:** Enum `{enum_name}` not found.'

            rows = [
                [f'`{e.name}`', _extract_comments(e)]
                for e in el.elements
                if isinstance(e, EnumValue)
            ]
            return f'{_extract_comments(el)}\n\n' + tabulate(
                rows, ['Value', 'Description'], tablefmt='github'
            )
        except Exception as e:
            return f'**Error:** {e}'

    @env.macro
    def proto_service_to_table(
        service_name: str, proto_file: str = 'specification/a2a.proto'
    ) -> str:
        """Parses a .proto file and renders a Service table."""
        try:
            elements = _parse_proto(proto_file)
            service = _find_type(elements, service_name, Service)
            if not service:
                return f'**Error:** Service `{service_name}` not found.'

            rows = []
            for el in service.elements:
                if isinstance(el, Method):
                    # Request Type
                    # input_type is a MessageType(type='...', stream=True/False)
                    req_str = _format_type_for_docs(el.input_type.type)
                    if el.input_type.stream:
                        req_str = f'stream {req_str}'

                    # Response Type
                    res_str = _format_type_for_docs(el.output_type.type)
                    if el.output_type.stream:
                        res_str = f'stream {res_str}'

                    rows.append(
                        [
                            f'`{el.name}`',
                            req_str,
                            res_str,
                            _extract_comments(el),
                        ]
                    )

            if not rows:
                return 'None'

            headers = ['Method', 'Request', 'Response', 'Description']
            return tabulate(rows, headers, tablefmt='github')

        except Exception as e:
            return f'**Error:** {e}'


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------


def _extract_comments(element: Any) -> str:
    """Clean and combine comments from an AST element."""
    cleaned_parts = []
    raw_comments = getattr(element, 'comments', []) or []

    for comment in raw_comments:
        text = (
            comment.strip()
            .removeprefix('//')
            .removeprefix('/*')
            .removesuffix('*/')
        )
        lines = (
            line.strip().removeprefix('*').strip() for line in text.splitlines()
        )
        combined = ' '.join(filter(None, lines))

        if combined and not combined.startswith(
            ('protolint:', '--8<--', 'Next ID:')
        ):
            cleaned_parts.append(combined)

    return ' '.join(cleaned_parts)


def _attach_comments(elements: list[Any]) -> None:
    """Recursively attach preceding comments to each non-comment element."""
    buffer = []
    for el in elements:
        if isinstance(el, Comment):
            buffer.append(el.text)
        else:
            # Attach collected comments to this element
            el.comments = buffer
            buffer = []
            # Recursively handle nested elements (e.g. inside Message or OneOf)
            if hasattr(el, 'elements'):
                _attach_comments(el.elements)


def _format_type_for_docs(
    proto_type: str, is_repeated: bool = False, map_key: str | None = None
) -> str:
    """Formats the type name with Markdown links for non-primitive types."""
    # Handle fully qualified names by taking only the last part for the link label,
    # but keep it if it's a known google.protobuf type we mapped.
    display_name = TYPE_MAP.get(proto_type, proto_type.split('.')[-1])
    is_primitive = proto_type in TYPE_MAP or proto_type.startswith(
        'google.protobuf'
    )

    # Create a slug for the link. Messages are usually CamelCase, so lowercase it.
    label = f'`{display_name}`'
    if not is_primitive:
        label = f'[{label}](#{display_name.lower()})'

    if map_key:
        key_label = TYPE_MAP.get(map_key, map_key)
        return f'map of {key_label} to {label}'

    if is_repeated:
        return f'array of {label}'

    return label


def _find_type(elements: list[Any], name: str, target_cls: type) -> Any | None:
    """Recursively searches for a Message or Enum by name."""
    for el in elements:
        if getattr(el, 'name', None) == name and isinstance(el, target_cls):
            return el
        if isinstance(el, Message):
            found = _find_type(el.elements, name, target_cls)
            if found:
                return found
    return None


def _process_field(field: Field, is_oneof: bool = False) -> list[str]:
    """Converts a Field or MapField object into a table row."""
    options = getattr(field, 'options', [])
    cardinality_obj = getattr(field, 'cardinality', None)
    cardinality = (
        getattr(cardinality_obj, 'value', None) if cardinality_obj else None
    )

    # Determine Display Name (json_name vs snake_case)
    json_name = next(
        (o.value.strip('"') for o in options if o.name == 'json_name'), None
    )
    display_name = json_name or _snake_to_camel_case(field.name)

    # Determine Type
    is_map = isinstance(field, MapField)
    is_repeated = cardinality == 'REPEATED'

    type_to_format = field.value_type if is_map else field.type
    map_key = getattr(field, 'key_type', None)

    type_str = _format_type_for_docs(type_to_format, is_repeated, map_key)

    # Determine Required/Optional
    has_required_behavior = any(
        'REQUIRED' in str(opt.value)
        for opt in options
        if 'field_behavior' in opt.name
    )

    if is_oneof:
        req_val = 'Optional (OneOf)'
    elif cardinality == 'REQUIRED' or has_required_behavior:
        req_val = 'Yes'
    else:
        req_val = 'No'

    desc = _extract_comments(field)

    return [f'`{display_name}`', type_str, req_val, desc]


def _snake_to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
