"""CLI for envcheck."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from .checker import check, find_env_files


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "directory",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    required=False,
)
@click.option(
    "--env", "env_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    metavar="FILE",
    help="Path to .env file (default: auto-detected).",
)
@click.option(
    "--example", "example_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    metavar="FILE",
    help="Path to .env.example file (default: auto-detected).",
)
@click.option(
    "--allow-extra", is_flag=True, default=False,
    help="Don't flag keys in .env that are absent from .env.example.",
)
@click.option(
    "--no-warn-empty", is_flag=True, default=False,
    help="Don't warn about keys set to empty values.",
)
@click.option(
    "--no-color", is_flag=True, default=False,
    help="Disable ANSI color output.",
)
@click.option(
    "--quiet", "-q", is_flag=True, default=False,
    help="Only print issues (no OK messages). Exit code still reflects status.",
)
@click.version_option(package_name="envcheck")
def main(
    directory: Path,
    env_path: Path | None,
    example_path: Path | None,
    allow_extra: bool,
    no_warn_empty: bool,
    no_color: bool,
    quiet: bool,
) -> None:
    """Check that your .env matches .env.example.

    Finds missing keys, extra undocumented keys, and empty values.
    Exits with code 1 if any required keys are missing or extra keys exist.

    \b
    Examples:
      envcheck                     # auto-detect in current directory
      envcheck /path/to/project
      envcheck --allow-extra       # ignore undocumented keys
      envcheck --env .env.local --example .env.example
    """
    red = (lambda s: s) if no_color else _red
    yellow = (lambda s: s) if no_color else _yellow
    green = (lambda s: s) if no_color else _green
    bold = (lambda s: s) if no_color else _bold
    dim = (lambda s: s) if no_color else _dim

    # Resolve file paths
    if env_path is None or example_path is None:
        found_env, found_example = find_env_files(directory)
        if env_path is None:
            env_path = found_env
        if example_path is None:
            example_path = found_example

    if env_path is None:
        click.echo(red("✗ Could not find .env file."), err=True)
        click.echo(
            dim("  Tip: create a .env file or pass --env <path>"), err=True
        )
        sys.exit(2)

    if example_path is None:
        click.echo(red("✗ Could not find .env.example (or .env.sample / .env.template)."), err=True)
        click.echo(
            dim("  Tip: create a .env.example file or pass --example <path>"), err=True
        )
        sys.exit(2)

    report = check(
        env_path,
        example_path,
        allow_extra=allow_extra,
        warn_empty=not no_warn_empty,
    )

    # Print context
    if not quiet:
        click.echo(
            f"{bold('env')}:     {dim(str(env_path))}\n"
            f"{bold('example')}: {dim(str(example_path))}\n"
        )

    if report.missing:
        click.echo(red(f"✗ Missing ({len(report.missing)}) — required by .env.example but not in .env:"))
        for key in report.missing:
            click.echo(f"    {red(key)}")

    if report.extra:
        click.echo(yellow(f"⚠ Undocumented ({len(report.extra)}) — in .env but not in .env.example:"))
        for key in report.extra:
            click.echo(f"    {yellow(key)}")

    if report.empty:
        click.echo(yellow(f"⚠ Empty ({len(report.empty)}) — keys with no value set:"))
        for key in report.empty:
            click.echo(f"    {yellow(key)}")

    if not quiet:
        if report.ok and not report.empty:
            click.echo(green("✓ All good — .env matches .env.example"))
        elif report.ok:
            click.echo(green("✓ No missing or extra keys") + yellow(" (empty values above)"))

    sys.exit(0 if report.ok else 1)
