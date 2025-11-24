"""
Custom MkDocs macros for A2A documentation.

This module provides macros for rendering Protocol Buffer definitions
as markdown tables.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _is_primitive_type(proto_type: str) -> bool:
    """Check if a proto type is a primitive type that shouldn't be linked."""
    primitive_types = {
        'string', 'int32', 'int64', 'bool', 'bytes',
        'google.protobuf.Struct', 'google.protobuf.Timestamp'
    }
    return proto_type in primitive_types


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
        description, fields, notes, oneof_groups = _parse_proto_message_full(message_content)

        if not fields:
            return f"**Error:** No fields found in message '{message_name}'"

        # Build the output
        output = []

        if description:
            output.append(description)
            output.append('')  # Empty line

        output.append(_generate_markdown_table(fields))

        # Add oneof notes after the table
        if oneof_groups:
            output.append('')  # Empty line
            for oneof_name, oneof_fields in oneof_groups.items():
                if len(oneof_fields) > 1:
                    field_list = ', '.join(f'`{field}`' for field in oneof_fields)
                    output.append(f'**Note:** A {message_name} MUST contain exactly one of the following: {field_list}')

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


def _should_skip_comment(comment_text: str) -> bool:
    """Check if a comment line should be skipped (protolint directives, region markers, etc.)."""
    return (comment_text.startswith('protolint:') or
            comment_text.startswith('--8<--') or
            comment_text.startswith('Next ID:'))


def _parse_field_definition(field_def: str) -> Optional[Dict[str, any]]:
    """
    Parse a single field definition and extract its components.

    Returns:
        Dict with keys: field_type, field_name, annotations, is_repeated, is_optional, is_required
        or None if the field definition doesn't match any known pattern
    """
    # Check for map type first
    map_match = re.match(
        r'map<[\w.]+,\s*([\w.]+)>\s+([\w_]+)\s*=\s*\d+(\s*\[(.*?)\])?;',
        field_def
    )
    if map_match:
        return {
            'field_type': f'map<{map_match.group(1)}>',
            'field_name': map_match.group(2),
            'annotations': map_match.group(4) or '',
            'is_repeated': False,
            'is_optional': False,
            'is_required': 'REQUIRED' in (map_match.group(4) or '')
        }

    # Check for optional keyword
    optional_match = re.match(
        r'optional\s+([\w.]+)\s+([\w_]+)\s*=\s*\d+(\s*\[(.*?)])?;',
        field_def
    )
    if optional_match:
        return {
            'field_type': optional_match.group(1),
            'field_name': optional_match.group(2),
            'annotations': optional_match.group(4) or '',
            'is_repeated': False,
            'is_optional': True,
            'is_required': False
        }

    # Try regular field pattern
    field_match = re.match(
        r'(repeated\s+)?([\w.]+)\s+([\w_]+)\s*=\s*\d+(\s*\[(.*?)\])?;',
        field_def
    )
    if field_match:
        annotations = field_match.group(5) or ''
        return {
            'field_type': field_match.group(2),
            'field_name': field_match.group(3),
            'annotations': annotations,
            'is_repeated': field_match.group(1) is not None,
            'is_optional': False,
            'is_required': 'REQUIRED' in annotations
        }

    return None


def _get_display_name(field_name: str, annotations: str) -> str:
    """Extract display name from json_name annotation or convert from snake_case."""
    json_name_match = re.search(r'json_name\s*=\s*"([^"]+)"', annotations)
    if json_name_match:
        return json_name_match.group(1)
    return _snake_to_camel_case(field_name)


def _determine_required_value(is_required: bool, is_optional: bool) -> str:
    """Determine the required column value for a field."""
    if is_required:
        return 'Yes'
    elif is_optional:
        return 'Optional'
    return 'No'


def _parse_proto_message_full(content: str) -> Tuple[str, List[Dict[str, str]], str, Dict[str, List[str]]]:
    """
    Parse proto message content and extract description, fields, and notes.

    Returns:
        Tuple of (description_before, fields, notes_after, oneof_groups)
        where oneof_groups is a dict mapping oneof names to lists of field names
    """
    fields = []
    oneof_groups = {}
    lines = content.split('\n')
    current_comment = []
    description_lines = []
    notes_lines = []
    inside_message = False
    message_ended = False
    inside_oneof = False
    current_oneof_name = None
    accumulated_line = ''

    for line in lines:
        stripped = line.strip()

        # Collect description before the message declaration
        if not inside_message and not message_ended:
            if stripped.startswith('//'):
                comment_text = stripped[2:].strip()
                if not _should_skip_comment(comment_text):
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
                if not _should_skip_comment(comment_text):
                    notes_lines.append(comment_text)
            continue

        # Process content inside the message
        elif inside_message:
            # Check if message has ended
            if stripped == '}' and not inside_oneof:
                message_ended = True
                continue

            # Check for end of oneof block
            if stripped == '}' and inside_oneof:
                inside_oneof = False
                current_oneof_name = None
                continue

            # Check for start of oneof block
            oneof_match = re.match(r'oneof\s+([\w_]+)\s*{', stripped)
            if oneof_match:
                inside_oneof = True
                current_oneof_name = oneof_match.group(1)
                oneof_groups[current_oneof_name] = []
                continue

            # Collect comment lines for fields
            if stripped.startswith('//'):
                comment_text = stripped[2:].strip()
                if not _should_skip_comment(comment_text):
                    current_comment.append(comment_text)
            # Parse field definition - handle multi-line definitions
            elif stripped and not stripped.startswith('message') and not stripped.startswith('enum'):
                # Accumulate line if it doesn't end with semicolon
                if accumulated_line:
                    accumulated_line += ' ' + stripped
                else:
                    accumulated_line = stripped

                # Process only when we have a complete field definition (ends with semicolon)
                if not accumulated_line.endswith(';'):
                    continue

                # Parse the complete field definition
                field_info = _parse_field_definition(accumulated_line)
                accumulated_line = ''  # Reset for next field

                if field_info:
                    # Convert proto type to readable format
                    readable_type = _format_proto_type(
                        field_info['field_type'],
                        field_info['is_repeated']
                    )

                    # Join comment lines
                    description = ' '.join(current_comment) if current_comment else ''

                    # Get display name and required value
                    display_name = _get_display_name(
                        field_info['field_name'],
                        field_info['annotations']
                    )
                    required_value = _determine_required_value(
                        field_info['is_required'],
                        field_info['is_optional']
                    )

                    fields.append({
                        'name': display_name,
                        'type': readable_type,
                        'required': required_value,
                        'description': description
                    })

                    # Track oneof fields
                    if inside_oneof and current_oneof_name:
                        oneof_groups[current_oneof_name].append(display_name)

                    # Reset comment buffer
                    current_comment = []
                else:
                    # Reset comment buffer if not a field
                    if not inside_oneof:
                        current_comment = []

    description = ' '.join(description_lines).strip()
    notes = ' '.join(notes_lines).strip()

    return description, fields, notes, oneof_groups


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
                if not _should_skip_comment(comment_text):
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


def _format_proto_type(proto_type: str, is_repeated: bool) -> str:
    """
    Format proto type to a more readable format with links to specification.
    Non-primitive types are automatically linked to their anchor in specification.md.
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

    # Check for map type first
    map_match = re.match(r'map<(.+)>', proto_type)
    if map_match:
        value_type = map_match.group(1)
        readable_value_type = type_map.get(value_type, value_type)
        # Create link for non-primitive types
        if not _is_primitive_type(value_type):
            readable_value_type = f'[`{readable_value_type}`](#{value_type})'
        else:
            readable_value_type = f'`{readable_value_type}`'
        return f'map of {readable_value_type}'

    readable_type = type_map.get(proto_type, proto_type)

    # Create link for non-primitive types
    if not _is_primitive_type(proto_type):
        formatted_type = f'[`{readable_type}`](#{proto_type})'
    else:
        formatted_type = f'`{readable_type}`'

    if is_repeated:
        return f'array of {formatted_type}'

    return formatted_type


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
