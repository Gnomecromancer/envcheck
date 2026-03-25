"""Parse .env and .env.example files."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EnvEntry:
    key: str
    value: str | None     # None for keys without a value (KEY= or KEY)
    comment: str | None   # inline comment
    is_comment_only: bool = False  # True for lines that are pure comments


def parse_env(path: Path) -> list[EnvEntry]:
    """Parse a .env-style file and return a list of entries.

    Handles:
    - KEY=value
    - KEY="quoted value"
    - KEY='single quoted'
    - KEY=          (empty value)
    - # full-line comments (skipped)
    - export KEY=value
    - Inline comments: KEY=value # comment
    """
    entries: list[EnvEntry] = []
    text = path.read_text(encoding="utf-8", errors="replace")

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Strip optional 'export ' prefix
        if stripped.startswith("export "):
            stripped = stripped[7:].strip()

        # Split on first '='
        if "=" not in stripped:
            # KEY with no value (some .env parsers allow this)
            key = stripped.split()[0]
            entries.append(EnvEntry(key=key, value=None, comment=None))
            continue

        key, _, rest = stripped.partition("=")
        key = key.strip()
        if not key or not _valid_key(key):
            continue

        # Parse value (handle quotes and inline comments)
        value, comment = _parse_value(rest)
        entries.append(EnvEntry(key=key, value=value, comment=comment))

    return entries


def _valid_key(key: str) -> bool:
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key))


def _parse_value(raw: str) -> tuple[str, str | None]:
    """Extract value and optional inline comment from the right side of KEY=..."""
    raw = raw.strip()

    # Quoted strings: consume until closing quote
    if raw.startswith('"'):
        end = raw.find('"', 1)
        if end == -1:
            return raw[1:], None
        value = raw[1:end]
        rest = raw[end + 1:].strip()
        comment = rest[1:].strip() if rest.startswith("#") else None
        return value, comment

    if raw.startswith("'"):
        end = raw.find("'", 1)
        if end == -1:
            return raw[1:], None
        value = raw[1:end]
        rest = raw[end + 1:].strip()
        comment = rest[1:].strip() if rest.startswith("#") else None
        return value, comment

    # Unquoted: split on first '#'
    if "#" in raw:
        value_part, _, comment_part = raw.partition("#")
        return value_part.strip(), comment_part.strip() or None

    return raw, None


def keys(entries: list[EnvEntry]) -> set[str]:
    """Return the set of key names from a list of entries."""
    return {e.key for e in entries}
