"""Tests for envcheck CLI."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from envcheck.cli import main
from envcheck.checker import CheckReport


def _make_env(tmp_path, content: str, name=".env") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.2.0" in result.output


def test_ok_exits_zero(tmp_path):
    env = _make_env(tmp_path, "FOO=bar\n")
    example = _make_env(tmp_path, "FOO=\n", ".env.example")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--no-color"])
    assert result.exit_code == 0
    assert "All good" in result.output


def test_missing_exits_one(tmp_path):
    _make_env(tmp_path, "FOO=bar\n")
    _make_env(tmp_path, "FOO=\nBAZ=\n", ".env.example")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--no-color"])
    assert result.exit_code == 1
    assert "BAZ" in result.output
    assert "Missing" in result.output


def test_extra_exits_one(tmp_path):
    _make_env(tmp_path, "FOO=bar\nSECRET=x\n")
    _make_env(tmp_path, "FOO=\n", ".env.example")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--no-color"])
    assert result.exit_code == 1
    assert "SECRET" in result.output
    assert "Undocumented" in result.output


def test_allow_extra_ok(tmp_path):
    _make_env(tmp_path, "FOO=bar\nSECRET=x\n")
    _make_env(tmp_path, "FOO=\n", ".env.example")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--allow-extra", "--no-color"])
    assert result.exit_code == 0


def test_empty_value_warning(tmp_path):
    _make_env(tmp_path, "FOO=\n")
    _make_env(tmp_path, "FOO=\n", ".env.example")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--no-color"])
    assert "Empty" in result.output or "empty" in result.output
    # Exit 0 because no missing/extra
    assert result.exit_code == 0


def test_no_env_file_exits_2(tmp_path):
    _make_env(tmp_path, "FOO=\n", ".env.example")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 2


def test_no_example_file_exits_2(tmp_path):
    _make_env(tmp_path, "FOO=bar\n")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path)])
    assert result.exit_code == 2


def test_quiet_suppresses_ok_message(tmp_path):
    _make_env(tmp_path, "FOO=bar\n")
    _make_env(tmp_path, "FOO=\n", ".env.example")
    runner = CliRunner()
    result = runner.invoke(main, [str(tmp_path), "--quiet", "--no-color"])
    assert result.exit_code == 0
    assert "All good" not in result.output
    assert result.output.strip() == ""


def test_explicit_paths(tmp_path):
    env = tmp_path / "myenv"
    env.write_text("A=1\nB=2\n")
    example = tmp_path / "myexample"
    example.write_text("A=\nB=\n")
    runner = CliRunner()
    result = runner.invoke(main, ["--env", str(env), "--example", str(example), "--no-color"])
    assert result.exit_code == 0
