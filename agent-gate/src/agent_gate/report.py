"""Text and JSON reports with deterministic ordering."""

from dataclasses import asdict
import json

from .checks import Violation


def render(violations: list[Violation], agent_count: int, format: str) -> str:
    if format == "json":
        return json.dumps([asdict(item) for item in violations], indent=2)
    lines = [
        f"FAIL {json.dumps(item.agent, ensure_ascii=False)[1:-1]} {item.rule_id} {item.message}"
        for item in violations
    ]
    status = "FAIL" if violations else "PASS"
    lines.append(f"{status}: checked {agent_count} agent(s); {len(violations)} violation(s)")
    return "\n".join(lines)
