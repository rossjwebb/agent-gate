"""Command-line entry point."""

import argparse
from pathlib import Path
import sys

from .checks import check_agent
from .policy import Policy, load_toml
from .report import render


def agent_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise ValueError(f"{path}: agent path does not exist or is not a file/directory")
    files = sorted(path.rglob("*.toml"))
    files = [file for file in files if file.is_file()]
    if not files:
        raise ValueError(f"{path}: no agent TOML files found")
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agent-gate")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="check agents against a policy")
    check.add_argument("--policy", type=Path, required=True)
    check.add_argument("--format", choices=("text", "json"), default="text")
    check.add_argument("agents", type=Path, help="agent TOML file or directory (recursive)")
    args = parser.parse_args(argv)

    try:
        policy = Policy.load(args.policy)
        files = agent_files(args.agents)
        violations = []
        for path in files:
            data = load_toml(path)
            try:
                violations.extend(check_agent(data, policy, path.stem))
            except ValueError as exc:
                raise ValueError(f"{path}: {exc}") from None
    except (ValueError, OSError) as exc:
        print(f"agent-gate: error: {exc}", file=sys.stderr)
        return 2

    print(render(violations, len(files), args.format))
    return 1 if violations else 0
