"""Compare .env against .env.example and produce a diff report."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .parser import parse_env, keys, EnvEntry


@dataclass
class CheckReport:
    missing: list[str] = field(default_factory=list)
    """Keys defined in .env.example but absent from .env."""

    extra: list[str] = field(default_factory=list)
    """Keys in .env that are not in .env.example."""

    empty: list[str] = field(default_factory=list)
    """Keys in .env with empty/None values (potentially not set)."""

    @property
    def ok(self) -> bool:
        return not self.missing and not self.extra

    @property
    def total_issues(self) -> int:
        return len(self.missing) + len(self.extra)


def check(
    env_path: Path,
    example_path: Path,
    *,
    allow_extra: bool = False,
    warn_empty: bool = True,
) -> CheckReport:
    """Compare env_path against example_path.

    Args:
        env_path: Path to the .env file.
        example_path: Path to the .env.example file.
        allow_extra: If True, keys in .env not in .env.example are not flagged.
        warn_empty: If True, collect keys with empty values in the report.
    """
    env_entries = parse_env(env_path)
    example_entries = parse_env(example_path)

    env_keys = keys(env_entries)
    example_keys = keys(example_entries)

    missing = sorted(example_keys - env_keys)
    extra = [] if allow_extra else sorted(env_keys - example_keys)

    empty: list[str] = []
    if warn_empty:
        for entry in env_entries:
            if entry.key in example_keys and (entry.value is None or entry.value == ""):
                empty.append(entry.key)
        empty.sort()

    return CheckReport(missing=missing, extra=extra, empty=empty)


def find_env_files(root: Path) -> tuple[Path | None, Path | None]:
    """Find .env and .env.example files under root."""
    env = root / ".env" if (root / ".env").is_file() else None
    example = None
    for name in (".env.example", ".env.sample", ".env.template"):
        candidate = root / name
        if candidate.is_file():
            example = candidate
            break
    return env, example
