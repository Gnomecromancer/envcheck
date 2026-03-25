"""Tests for envcheck.checker."""
from __future__ import annotations

from pathlib import Path

import pytest

from envcheck.checker import check, find_env_files


def _make_env(tmp_path, content: str, name=".env") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_all_ok(tmp_path):
    env = _make_env(tmp_path, "FOO=bar\nBAZ=qux\n")
    example = _make_env(tmp_path, "FOO=\nBAZ=\n", ".env.example")
    report = check(env, example)
    assert report.ok
    assert report.missing == []
    assert report.extra == []


def test_missing_key(tmp_path):
    env = _make_env(tmp_path, "FOO=bar\n")
    example = _make_env(tmp_path, "FOO=\nBAZ=\n", ".env.example")
    report = check(env, example)
    assert not report.ok
    assert "BAZ" in report.missing
    assert "FOO" not in report.missing


def test_extra_key(tmp_path):
    env = _make_env(tmp_path, "FOO=bar\nSECRET=abc\n")
    example = _make_env(tmp_path, "FOO=\n", ".env.example")
    report = check(env, example)
    assert not report.ok
    assert "SECRET" in report.extra


def test_allow_extra_suppresses_extra(tmp_path):
    env = _make_env(tmp_path, "FOO=bar\nSECRET=abc\n")
    example = _make_env(tmp_path, "FOO=\n", ".env.example")
    report = check(env, example, allow_extra=True)
    assert report.ok
    assert report.extra == []


def test_empty_value_warning(tmp_path):
    env = _make_env(tmp_path, "FOO=\nBAZ=set\n")
    example = _make_env(tmp_path, "FOO=\nBAZ=\n", ".env.example")
    report = check(env, example, warn_empty=True)
    assert "FOO" in report.empty
    assert "BAZ" not in report.empty


def test_no_warn_empty(tmp_path):
    env = _make_env(tmp_path, "FOO=\n")
    example = _make_env(tmp_path, "FOO=\n", ".env.example")
    report = check(env, example, warn_empty=False)
    assert report.empty == []


def test_multiple_missing(tmp_path):
    env = _make_env(tmp_path, "")
    example = _make_env(tmp_path, "A=\nB=\nC=\n", ".env.example")
    report = check(env, example)
    assert sorted(report.missing) == ["A", "B", "C"]


# ── find_env_files ────────────────────────────────────────────────────────────

def test_find_env_files_standard(tmp_path):
    (tmp_path / ".env").write_text("K=v")
    (tmp_path / ".env.example").write_text("K=")
    env, example = find_env_files(tmp_path)
    assert env == tmp_path / ".env"
    assert example == tmp_path / ".env.example"


def test_find_env_files_sample(tmp_path):
    (tmp_path / ".env").write_text("K=v")
    (tmp_path / ".env.sample").write_text("K=")
    _, example = find_env_files(tmp_path)
    assert example == tmp_path / ".env.sample"


def test_find_env_files_missing(tmp_path):
    env, example = find_env_files(tmp_path)
    assert env is None
    assert example is None
