"""Stable policy rules for agent definitions."""

from dataclasses import dataclass

from .policy import Policy, validate_field


AGENT_FIELDS = {
    "name": "string",
    "owner": "string",
    "model": "string",
    "monthly_budget_gbp": "budget",
    "tools": "strings",
    "human_approval_for": "strings",
    "max_steps": "steps",
}


@dataclass(frozen=True)
class Violation:
    agent: str
    rule_id: str
    message: str


def check_agent(data: dict, policy: Policy, fallback_name: str) -> list[Violation]:
    for key, kind in AGENT_FIELDS.items():
        if key in data:
            validate_field(key, data[key], kind)

    name = data.get("name", "").strip() or fallback_name
    violations = []

    def fail(rule: str, message: str) -> None:
        violations.append(Violation(name, rule, message))

    if data.get("model") not in policy.allowed_models:
        fail("AG001", f"model {data.get('model')!r} is not on the allowlist")

    budget = data.get("monthly_budget_gbp")
    if budget is None:
        fail("AG002", "monthly_budget_gbp is missing")
    elif budget > policy.max_monthly_budget_gbp:
        fail("AG002", f"monthly_budget_gbp {budget} exceeds cap {policy.max_monthly_budget_gbp}")

    unapproved = (
        (set(data.get("tools", [])) & set(policy.risky_tools))
        - set(data.get("human_approval_for", []))
    )
    for tool in sorted(unapproved):
        fail("AG003", f"risky tool {tool!r} requires human_approval_for")

    steps = data.get("max_steps")
    if steps is None:
        fail("AG004", "max_steps is missing")
    elif steps > policy.max_steps:
        fail("AG004", f"max_steps {steps} exceeds cap {policy.max_steps}")

    if policy.require_owner and not data.get("owner", "").strip():
        fail("AG005", "owner is required")

    for key in sorted(data.keys() - AGENT_FIELDS.keys()):
        fail("AG006", f"unknown agent field {key!r}")
    return violations
