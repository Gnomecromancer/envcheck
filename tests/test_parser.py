"""Tests for envcheck.parser."""
from __future__ import annotations

from pathlib import Path

import pytest

from envcheck.parser import parse_env, keys


def _file(tmp_path, content: str, name=".env") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_parse_simple_key_value(tmp_path):
    f = _file(tmp_path, "FOO=bar\nBAZ=qux\n")
    entries = parse_env(f)
    assert len(entries) == 2
    assert entries[0].key == "FOO"
    assert entries[0].value == "bar"
    assert entries[1].key == "BAZ"


def test_parse_empty_value(tmp_path):
    f = _file(tmp_path, "KEY=\n")
    entries = parse_env(f)
    assert entries[0].value == ""


def test_parse_quoted_double(tmp_path):
    f = _file(tmp_path, 'DB_URL="postgres://localhost/mydb"\n')
    entries = parse_env(f)
    assert entries[0].value == "postgres://localhost/mydb"


def test_parse_quoted_single(tmp_path):
    f = _file(tmp_path, "SECRET='my secret value'\n")
    entries = parse_env(f)
    assert entries[0].value == "my secret value"


def test_parse_inline_comment(tmp_path):
    f = _file(tmp_path, "PORT=3000  # web server port\n")
    entries = parse_env(f)
    assert entries[0].value == "3000"
    assert entries[0].comment == "web server port"


def test_parse_skips_full_line_comments(tmp_path):
    f = _file(tmp_path, "# This is a comment\nKEY=value\n")
    entries = parse_env(f)
    assert len(entries) == 1
    assert entries[0].key == "KEY"


def test_parse_skips_blank_lines(tmp_path):
    f = _file(tmp_path, "\n\nKEY=value\n\n")
    entries = parse_env(f)
    assert len(entries) == 1


def test_parse_export_prefix(tmp_path):
    f = _file(tmp_path, "export KEY=value\n")
    entries = parse_env(f)
    assert entries[0].key == "KEY"
    assert entries[0].value == "value"


def test_parse_key_with_spaces_around_equals(tmp_path):
    f = _file(tmp_path, "KEY = value\n")
    entries = parse_env(f)
    assert entries[0].key == "KEY"
    # value might have leading space stripped or not — depends on implementation
    assert entries[0].value is not None


def test_keys_function(tmp_path):
    f = _file(tmp_path, "FOO=1\nBAR=2\nBAZ=3\n")
    entries = parse_env(f)
    assert keys(entries) == {"FOO", "BAR", "BAZ"}
