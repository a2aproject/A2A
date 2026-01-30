"""Custom MkDocs macros for A2A documentation.

This module provides macros for rendering Protocol Buffer definitions
as markdown tables.
"""

from pathlib import Path
from typing import Any

from proto_schema_parser.ast import (
    Comment,
    Enum,
    Field,
    MapField,
    Message,
    OneOf,
    Option,
)
from proto_schema_parser.parser import Parser
from tabulate import tabulate


# -----------------------------------------------------------------------------
# Constants & Configuration
# -----------------------------------------------------------------------------

PRIMITIVE_TYPES = {
    'string',
    'int32',
    'int64',
    'bool',
    'bytes',
    'google.protobuf.Struct',
    'google.protobuf.Timestamp',
    'google.protobuf.Value',
    'google.protobuf.Empty',
    'double',
    'float',
    'uint32',
    'uint64',
    'sint32',
    'sint64',
    'fixed32',
    'fixed64',
    'sfixed32',
    'sfixed64',
}

TYPE_MAPPING = {
    'string': 'string',
    'int32': 'integer',
    'int64': 'integer',
    'uint32': 'integer',
    'uint64': 'integer',
    'sint32': 'integer',
    'sint64': 'integer',
    'fixed32': 'integer',
    'fixed64': 'integer',
    'sfixed32': 'integer',
    'sfixed64': 'integer',
    'bool': 'boolean',
    'bytes': 'bytes',
    'google.protobuf.Struct': 'object',
    'google.protobuf.Timestamp': 'timestamp',
    'google.protobuf.Value': 'any',
    'google.protobuf.Empty': 'empty',
}

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------


def _is_primitive_type(proto_type: str) -> bool:
    """Check if a proto type is a primitive type that shouldn't be linked."""
    return proto_type in PRIMITIVE_TYPES


def _snake_to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def _extract_comments(element: Any) -> str:
    """Clean and combine comments from an AST element."""
    if hasattr(element, 'comments') and element.comments:
        cleaned = []
        for c in element.comments:
            # strip // and whitespace
            text = c.strip()
            if text.startswith('//'):
                text = text[2:]
            elif text.startswith('/*'):
                text = text[2:]
                if text.endswith('*/'):
                    text = text[:-2]
            c = ' '.join(l.strip().lstrip('*').strip() for l in text.strip().split('\n') if l.strip())

            if not c.startswith(('protolint:', '--8<--', 'Next ID:')) and c:
                cleaned.append(c)
        return ' '.join(cleaned)
    return ''


def _attach_comments(elements: list[Any]) -> None:
    """Recursively attach preceding comments to each non-comment element."""
    current_comments = []
    for el in elements:
        if isinstance(el, Comment):
            current_comments.append(el.text)
        else:
            # Attach collected comments to this element
            el.comments = current_comments
            current_comments = []
            # Recursively handle nested elements (e.g. inside Message or OneOf)
            if hasattr(el, 'elements') and el.elements:
                _attach_comments(el.elements)


def _get_option_value(options: list[Option], name: str) -> str | None:
    """Helper to find a value in a list of AST Options (e.g. json_name)."""
    if not options:
        return None
    for opt in options:
        if opt.name == name:
            return opt.value.strip('"')
    return None


def _format_type_for_docs(
    proto_type: str,
    is_repeated: bool = False,
    is_map: bool = False,
    map_key: str = None,
) -> str:
    """Formats the type string with Markdown links."""

    def format_single_type(t_name) -> str:
        # Handle fully qualified names by taking only the last part for the link label,
        # but keep it if it's a known google.protobuf type we mapped.
        readable = TYPE_MAPPING.get(t_name, t_name.split('.')[-1])
        if not _is_primitive_type(t_name):
            # Create a slug for the link. Messages are usually CamelCase, so lowercase it.
            anchor = t_name.lower().split('.')[-1]
            return f'[`{readable}`](#{anchor})'
        return f'`{readable}`'

    if is_map:
        key_fmt = TYPE_MAPPING.get(map_key, map_key)
        val_fmt = format_single_type(proto_type)
        return f'map of {key_fmt} to {val_fmt}'

    formatted = format_single_type(proto_type)
    if is_repeated:
        return f'array of {formatted}'

    return formatted


def _find_message(elements: list[Any], name: str) -> Message | None:
    """Recursively find a message by name."""
    for el in elements:
        if isinstance(el, Message):
            if el.name == name:
                return el
            nested = _find_message(el.elements, name)
            if nested:
                return nested
    return None


def _find_enum(elements: list[Any], name: str) -> Enum | None:
    """Recursively find an enum by name."""
    for el in elements:
        if isinstance(el, Enum) and el.name == name:
            return el
        if isinstance(el, Message):
            nested = _find_enum(el.elements, name)
            if nested:
                return nested
    return None


# -----------------------------------------------------------------------------
# Main Macros
# -----------------------------------------------------------------------------


def _parse_proto(env: Any, proto_file: str):
    """Parses a .proto file and returns the AST with comments attached."""
    project_root = Path(env.conf['docs_dir']).parent
    proto_path = project_root / proto_file

    if not proto_path.exists():
        raise FileNotFoundError(f'Proto file not found: {proto_file}')

    parser = Parser()
    with open(proto_path, encoding='utf-8') as f:
        file_ast = parser.parse(f.read())

    # Associate comments with elements
    _attach_comments(file_ast.file_elements)
    return file_ast


def define_env(env):
    """Define custom macros for MkDocs."""

    @env.macro
    def proto_to_table(
        message_name: str, proto_file: str = 'specification/a2a.proto'
    ) -> str:
        """Parses a .proto file and renders a message table."""
        try:
            file_ast = _parse_proto(env, proto_file)
        except FileNotFoundError as e:
            return f'**Error:** {e}'

        # Find the specific message object
        target_message = _find_message(file_ast.file_elements, message_name)

        if not target_message:
            return (
                f"**Error:** Message '{message_name}' not found in {proto_file}"
            )

        # Extract data
        rows = []
        oneof_groups = {}  # Map[oneof_name] -> List[field_names]

        # Iterate over elements inside the message
        # elements can be Field, MapField, OneOf, Enum, Message, etc.
        for el in target_message.elements:
            # 1. Handle Standard Fields
            if isinstance(el, Field):
                row = _process_field(el)
                rows.append(row)

            # 2. Handle Map Fields
            elif isinstance(el, MapField):
                row = _process_map_field(el)
                rows.append(row)

            # 3. Handle OneOf (flatten these into the main table, but track them)
            elif isinstance(el, OneOf):
                oneof_groups[el.name] = []
                for oneof_el in el.elements:
                    if isinstance(oneof_el, Field):
                        # Process field normally
                        row = _process_field(oneof_el, is_oneof=True)
                        rows.append(row)
                        # Add display name to group tracker
                        oneof_groups[el.name].append(
                            row[0].strip('`')
                        )  # Remove code ticks for the note

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
    ) -> str:
        """Parses a .proto file and renders an Enum table."""
        try:
            file_ast = _parse_proto(env, proto_file)
        except FileNotFoundError as e:
            return f'**Error:** {e}'

        target_enum = _find_enum(file_ast.file_elements, enum_name)

        if not target_enum:
            return f"**Error:** Enum '{enum_name}' not found in {proto_file}"

        rows = []
        for el in target_enum.elements:
            # Enum elements are usually EnumValue
            # Note: proto-schema-parser might call them EnumValue or just extract them.
            # Checking attribute availability is safest.
            if hasattr(el, 'name') and hasattr(el, 'number'):
                desc = (
                    _extract_comments(el).replace('\n', ' ').replace('|', '\\|')
                )
                rows.append([f'`{el.name}`', desc])

        if not rows:
            return f"**Error:** No values found in enum '{enum_name}'"

        output = []
        enum_desc = _extract_comments(target_enum)
        if enum_desc:
            output.append(enum_desc)
            output.append('')

        # Force column width hack using alignment if needed, but standard tabulate usually suffices.
        # If you need specific widths, CSS is better, but here is standard MD.
        headers = ['Value', 'Description']
        output.append(tabulate(rows, headers, tablefmt='github'))

        return '\n'.join(output)


# -----------------------------------------------------------------------------
# Field Processors
# -----------------------------------------------------------------------------


def _process_field(field: Field, is_oneof: bool = False) -> list[str]:
    """Converts a standard Field object into a table row."""
    # Determine Display Name (json_name vs snake_case)
    json_name = _get_option_value(field.options, 'json_name')
    display_name = json_name if json_name else _snake_to_camel_case(field.name)

    # Determine Type
    is_repeated = field.cardinality and field.cardinality.value == 'REPEATED'
    type_str = _format_type_for_docs(field.type, is_repeated=is_repeated)

    # Determine Required/Optional
    req_val = 'No'

    # 1. Check Cardinality (proto2 or proto3 'optional'/'repeated')
    if field.cardinality:
        cv = field.cardinality.value
        if cv == 'REQUIRED':
            req_val = 'Yes'
        elif cv == 'OPTIONAL':
            req_val = 'Optional'
        elif cv == 'REPEATED':
            req_val = 'No'  # Or maybe "Repeated" if you prefer, but standard is No/Yes/Optional

    # 2. Check Options (google.api.field_behavior)
    if req_val == 'No':
        for opt in field.options:
            if opt.name == '(google.api.field_behavior)':
                opt_val = str(opt.value)
                if 'REQUIRED' in opt_val:
                    req_val = 'Yes'
                    break

    if is_oneof:
        req_val = 'Optional (OneOf)'

    # Description
    desc = _extract_comments(field).replace('\n', ' ').replace('|', '\\|')

    return [f'`{display_name}`', type_str, req_val, desc]


def _process_map_field(field: MapField) -> list[str]:
    """Converts a MapField object into a table row."""
    # Map fields also have options (like json_name)
    json_name = _get_option_value(field.options, 'json_name')
    display_name = json_name if json_name else _snake_to_camel_case(field.name)

    type_str = _format_type_for_docs(
        field.value_type, is_map=True, map_key=field.key_type
    )

    # Maps are inherently repeated/optional in structure, usually marked as No or Optional
    req_val = 'No'

    desc = _extract_comments(field).replace('\n', ' ').replace('|', '\\|')

    return [f'`{display_name}`', type_str, req_val, desc]
