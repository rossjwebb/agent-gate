"""TOML loading and policy validation."""

from dataclasses import dataclass
import math
from pathlib import Path
import tomllib


def load_toml(path: Path) -> dict:
    try:
        with path.open("rb") as stream:
            return tomllib.load(stream)
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError(f"{path}: {exc}") from None


def validate_field(key: str, value: object, kind: str) -> None:
    """Reject malformed values rather than silently skipping policy checks."""
    if kind == "strings":
        valid = isinstance(value, list) and all(
            isinstance(item, str) and item.strip() for item in value
        )
        expected = "a list of non-empty strings"
    elif kind == "budget":
        valid = type(value) in (int, float) and value >= 0
        if type(value) is float:
            valid = valid and math.isfinite(value)
        expected = "a finite, non-negative number"
    elif kind == "steps":
        valid = type(value) is int and value > 0
        expected = "a positive integer"
    elif kind == "bool":
        valid = type(value) is bool
        expected = "a boolean"
    else:
        valid = isinstance(value, str)
        expected = "a string"
    if not valid:
        raise ValueError(f"{key} must be {expected}")


@dataclass(frozen=True)
class Policy:
    allowed_models: list[str]
    max_monthly_budget_gbp: int | float
    max_steps: int
    risky_tools: list[str]
    require_owner: bool

    @classmethod
    def load(cls, path: Path) -> "Policy":
        data = load_toml(path)
        fields = {
            "allowed_models": "strings",
            "max_monthly_budget_gbp": "budget",
            "max_steps": "steps",
            "risky_tools": "strings",
            "require_owner": "bool",
        }
        try:
            unknown = sorted(data.keys() - fields.keys())
            if unknown:
                raise ValueError(f"unknown policy field(s): {', '.join(unknown)}")
            for key, kind in fields.items():
                if key not in data:
                    raise ValueError(f"missing policy field: {key}")
                validate_field(key, data[key], kind)
        except ValueError as exc:
            raise ValueError(f"{path}: {exc}") from None
        return cls(**data)
