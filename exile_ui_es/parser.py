"""Parser for Exile-UI .txt format files (UI.txt, client.txt).

Format: key = "value" with tabs, ;## comments, and significant structure.
The file structure (comments, empty lines, tab formatting) MUST be preserved
because Exile-UI's AHK parser depends on it.
"""

import re
from collections.abc import Callable

LINE_RE = re.compile(r'^\s*([^=]+?)\s*=\s*"([^"]*)"\s*$')


def parse_txt(content: str) -> dict[str, str]:
    """Parse Exile-UI .txt format, returning {key: value} dict.

    Only extracts key=value pairs. Comments and structure are ignored.
    Use translate_txt_file() for structure-preserving translations.
    """
    result = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(";##"):
            continue
        match = LINE_RE.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2)
            result[key] = value
    return result


def serialize_txt(data: dict[str, str]) -> str:
    """Serialize dict back to Exile-UI .txt format (key = "value").

    WARNING: This loses all comments and structure. Prefer
    translate_txt_file() for production use.
    """
    lines = []
    for key, value in data.items():
        lines.append(f'\t{key}\t=\t"{value}"')
    return "\n".join(lines) + "\n"


def translate_txt_file(
    content: str, translate_fn: Callable[[dict[str, str]], dict[str, str]]
) -> str:
    """Translate an Exile-UI .txt file PRESERVING all comments and structure.

    Reads the file line by line. For each key=value line, looks up the
    translation and replaces only the value part. Comments and empty
    lines pass through unchanged.

    Args:
        content: Raw file content
        translate_fn: Function that takes the parsed dict and returns
                      a translated dict

    Returns:
        Translated file content with original structure preserved
    """
    # First pass: parse to get translation mapping
    original = parse_txt(content)
    translated = translate_fn(original)

    # Second pass: apply translations line by line
    result_lines = []
    for line in content.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith(";##"):
            result_lines.append(line)
            continue
        match = LINE_RE.match(line)
        if match:
            key = match.group(1).strip()
            if key in translated and translated[key] != match.group(2):
                # Replace only the value, preserving the rest of the line
                old_value = match.group(2)
                new_value = translated[key]
                # Find where value starts in the line (after first quote)
                value_start = line.index(f'"{old_value}"')
                before = line[:value_start]
                after = line[value_start + len(f'"{old_value}"'):]
                new_line = f'{before}"{new_value}"{after}'
                result_lines.append(new_line)
            else:
                result_lines.append(line)
        else:
            result_lines.append(line)

    return "".join(result_lines)