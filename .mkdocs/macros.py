"""
Custom MkDocs macros for A2A documentation.

This module provides macros for rendering Protocol Buffer definitions
as markdown tables.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def define_env(env):
    """
    Define custom macros for MkDocs.

    This function is called by the mkdocs-macros plugin.
    """

    @env.macro
    def proto_to_table(proto_file: str, message_name: str) -> str:
        """
        Parse a Protocol Buffer message definition and render it with description and table.

        Args:
            proto_file: Relative path to the .proto file (e.g., "specification/grpc/a2a.proto")
            message_name: Name of the message to extract (e.g., "Message")

        Returns:
            Markdown representation with description before table and notes after
        """
        # Resolve the proto file path relative to the project root
        project_root = Path(env.conf['docs_dir']).parent
        proto_path = project_root / proto_file

        if not proto_path.exists():
            return f"**Error:** Proto file not found: {proto_file}"

        # Read the proto file content
        content = proto_path.read_text(encoding='utf-8')

        # Extract the message definition between the region markers
        pattern = rf'// --8<-- \[start:{re.escape(message_name)}\](.*?)// --8<-- \[end:{re.escape(message_name)}\]'
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return f"**Error:** Message '{message_name}' not found in {proto_file}"

        message_content = match.group(1)

        # Extract description (before message), fields, and notes (after message)
        description, fields, notes = _parse_proto_message_full(message_content)

        if not fields:
            return f"**Error:** No fields found in message '{message_name}'"

        # Build the output
        output = []

        if description:
            output.append(description)
            output.append('')  # Empty line

        output.append(_generate_markdown_table(fields))

        if notes:
            output.append('')  # Empty line
            output.append(notes)

        return '\n'.join(output)

    @env.macro
    def proto_enum_to_table(proto_file: str, enum_name: str) -> str:
        """
        Parse a Protocol Buffer enum definition and render it with description and table.

        Args:
            proto_file: Relative path to the .proto file
            enum_name: Name of the enum to extract

        Returns:
            Markdown representation with description before table and notes after
        """
        # Resolve the proto file path relative to the project root
        project_root = Path(env.conf['docs_dir']).parent
        proto_path = project_root / proto_file

        if not proto_path.exists():
            return f"**Error:** Proto file not found: {proto_file}"

        # Read the proto file content
        content = proto_path.read_text(encoding='utf-8')

        # Extract the enum definition between the region markers
        pattern = rf'// --8<-- \[start:{re.escape(enum_name)}\](.*?)// --8<-- \[end:{re.escape(enum_name)}\]'
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return f"**Error:** Enum '{enum_name}' not found in {proto_file}"

        enum_content = match.group(1)

        # Extract description (before enum), values, and notes (after enum)
        description, values, notes = _parse_proto_enum_full(enum_content)

        if not values:
            return f"**Error:** No values found in enum '{enum_name}'"

        # Build the output
        output = []

        if description:
            output.append(description)
            output.append('')  # Empty line

        output.append(_generate_enum_table(values))

        if notes:
            output.append('')  # Empty line
            output.append(notes)

        return '\n'.join(output)


def _parse_proto_message_full(content: str) -> Tuple[str, List[Dict[str, str]], str]:
    """
    Parse proto message content and extract description, fields, and notes.

    Returns:
        Tuple of (description_before, fields, notes_after)
    """
    fields = []
    lines = content.split('\n')
    current_comment = []
    description_lines = []
    notes_lines = []
    inside_message = False
    message_ended = False

    for line in lines:
        stripped = line.strip()

        # Collect description before the message declaration
        if not inside_message and not message_ended:
            if stripped.startswith('//'):
                comment_text = stripped[2:].strip()
                # Skip protolint directives and region markers
                if not comment_text.startswith('protolint:') and not comment_text.startswith('--8<--'):
                    description_lines.append(comment_text)
            elif stripped.startswith('message '):
                inside_message = True
                continue
            elif stripped:  # Non-comment, non-message line
                continue

        # Collect notes after the message ends
        elif message_ended:
            if stripped.startswith('//'):
                comment_text = stripped[2:].strip()
                if not comment_text.startswith('protolint:') and not comment_text.startswith('--8<--'):
                    notes_lines.append(comment_text)
            continue

        # Process content inside the message
        elif inside_message:
            # Check if message has ended
            if stripped == '}':
                message_ended = True
                continue

            # Collect comment lines for fields
            if stripped.startswith('//'):
                comment_text = stripped[2:].strip()
                # Skip protolint directives and region markers
                if not comment_text.startswith('protolint:') and not comment_text.startswith('--8<--'):
                    current_comment.append(comment_text)
            # Parse field definition
            elif stripped and not stripped.startswith('message') and not stripped.startswith('enum'):
                # Check for optional keyword
                optional_match = re.match(
                    r'optional\s+(repeated\s+)?([\w.]+)\s+([\w_]+)\s*=\s*\d+(\s*\[(.*?)\])?;',
                    stripped
                )

                if optional_match:
                    # This is an optional field
                    is_repeated = optional_match.group(1) is not None
                    field_type = optional_match.group(2)
                    field_name = optional_match.group(3)
                    annotations = optional_match.group(5) or ''
                    is_optional = True
                    is_required = False
                else:
                    # Try regular field pattern
                    field_match = re.match(
                        r'(repeated\s+)?([\w.]+)\s+([\w_]+)\s*=\s*\d+(\s*\[(.*?)\])?;',
                        stripped
                    )

                    if field_match:
                        is_repeated = field_match.group(1) is not None
                        field_type = field_match.group(2)
                        field_name = field_match.group(3)
                        annotations = field_match.group(5) or ''
                        is_optional = False
                        # Check if field is required via annotation
                        is_required = 'REQUIRED' in annotations
                    else:
                        field_match = None

                if optional_match or field_match:
                    # Convert proto type to readable format
                    readable_type = _format_proto_type(field_type, is_repeated)

                    # Join comment lines
                    description = ' '.join(current_comment) if current_comment else ''

                    # Determine required column value
                    if is_required:
                        required_value = 'Yes'
                    elif is_optional:
                        required_value = 'Optional'
                    else:
                        required_value = 'No'

                    fields.append({
                        'name': _snake_to_camel_case(field_name),
                        'type': readable_type,
                        'required': required_value,
                        'description': description
                    })

                    # Reset comment buffer
                    current_comment = []
                else:
                    # Check for oneof blocks
                    oneof_match = re.match(r'oneof\s+([\w_]+)\s*{', stripped)
                    if not oneof_match:
                        current_comment = []

    description = ' '.join(description_lines).strip()
    notes = ' '.join(notes_lines).strip()

    return description, fields, notes


def _parse_proto_message(content: str) -> List[Dict[str, str]]:
    """
    Parse proto message content and extract field information.

    Returns:
        List of field dictionaries with 'name', 'type', 'required', and 'description'
    """
    _, fields, _ = _parse_proto_message_full(content)
    return fields


def _parse_proto_enum_full(content: str) -> Tuple[str, List[Dict[str, str]], str]:
    """
    Parse proto enum content and extract description, values, and notes.

    Returns:
        Tuple of (description_before, values, notes_after)
    """
    values = []
    lines = content.split('\n')
    current_comment = []
    description_lines = []
    notes_lines = []
    inside_enum = False
    enum_ended = False

    for line in lines:
        stripped = line.strip()

        # Collect description before the enum declaration
        if not inside_enum and not enum_ended:
            if stripped.startswith('//'):
                comment_text = stripped[2:].strip()
                # Skip protolint directives and region markers
                if not comment_text.startswith('protolint:') and not comment_text.startswith('--8<--'):
                    description_lines.append(comment_text)
            elif stripped.startswith('enum '):
                inside_enum = True
                continue
            elif stripped:  # Non-comment, non-enum line
                continue

        # Collect notes after the enum ends
        elif enum_ended:
            if stripped.startswith('//'):
                comment_text = stripped[2:].strip()
                if not comment_text.startswith('protolint:') and not comment_text.startswith('--8<--'):
                    notes_lines.append(comment_text)
            continue

        # Process content inside the enum
        elif inside_enum:
            # Check if enum has ended
            if stripped == '}':
                enum_ended = True
                continue

            # Collect comment lines
            if stripped.startswith('//'):
                comment_text = stripped[2:].strip()
                # Skip protolint directives and region markers
                if not comment_text.startswith('protolint:') and not comment_text.startswith('--8<--'):
                    current_comment.append(comment_text)
            # Parse enum value definition
            elif stripped and not stripped.startswith('enum'):
                value_match = re.match(r'([\w_]+)\s*=\s*(\d+);', stripped)

                if value_match:
                    value_name = value_match.group(1)

                    # Join comment lines
                    description = ' '.join(current_comment) if current_comment else ''

                    values.append({
                        'name': value_name,
                        'description': description
                    })

                    # Reset comment buffer
                    current_comment = []

    description = ' '.join(description_lines).strip()
    notes = ' '.join(notes_lines).strip()

    return description, values, notes


def _parse_proto_enum(content: str) -> List[Dict[str, str]]:
    """
    Parse proto enum content and extract value information.

    Returns:
        List of value dictionaries with 'name' and 'description'
    """
    _, values, _ = _parse_proto_enum_full(content)
    return values


def _format_proto_type(proto_type: str, is_repeated: bool) -> str:
    """
    Format proto type to a more readable format.
    """
    # Map proto types to readable types
    type_map = {
        'string': 'string',
        'int32': 'integer',
        'int64': 'integer',
        'bool': 'boolean',
        'bytes': 'bytes',
        'google.protobuf.Struct': 'object',
        'google.protobuf.Timestamp': 'timestamp',
    }

    readable_type = type_map.get(proto_type, proto_type)

    if is_repeated:
        return f'array of {readable_type}'

    return readable_type


def _snake_to_camel_case(snake_str: str) -> str:
    """
    Convert snake_case to camelCase for field names.
    """
    components = snake_str.split('_')
    # Keep the first component lowercase, capitalize the rest
    return components[0] + ''.join(x.title() for x in components[1:])


def _generate_markdown_table(fields: List[Dict[str, str]]) -> str:
    """
    Generate a markdown table from field definitions.
    """
    # Table header
    table = "| Field | Type | Required | Description |\n"
    table += "|-------|------|----------|-------------|\n"

    # Table rows
    for field in fields:
        name = field['name']
        field_type = field['type']
        required = field['required']
        description = field['description'].replace('\n', ' ').replace('|', '\\|')

        table += f"| `{name}` | {field_type} | {required} | {description} |\n"

    return table


def _generate_enum_table(values: List[Dict[str, str]]) -> str:
    """
    Generate a markdown table from enum values.
    """
    # Table header with much wider Value column hint
    table = "| Value | Description |\n"
    table += "|:--------------------------------------|:------------|\n"

    # Table rows
    for value in values:
        name = value['name']
        description = value['description'].replace('\n', ' ').replace('|', '\\|')

        table += f"| `{name}` | {description} |\n"

    return table
