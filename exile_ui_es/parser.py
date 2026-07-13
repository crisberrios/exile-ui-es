import re

LINE_RE = re.compile(r'^\s*([^=]+?)\s*=\s*"([^"]*)"\s*$')

def parse_txt(content: str) -> dict[str, str]:
    """Parse Exile-UI .txt format (key = "value")."""
    result = {}
    for line in content.splitlines():
        # Skip empty lines and comments
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
    """Serialize back to Exile-UI .txt format."""
    lines = []
    for key, value in data.items():
        lines.append(f'\t{key}\t=\t"{value}"')
    return "\n".join(lines) + "\n"