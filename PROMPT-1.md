Build a small, self-contained Python project in this directory called `agent-gate`.

What it is: a pre-merge policy gate for AI agent configs. Teams keep agent definitions in TOML files. Before a pull request merges, `agent-gate` checks every agent against a policy file and fails the build if any agent breaks the rules.

Constraints:
- Python 3.11+, standard library only (use `tomllib`). No third-party dependencies.
- Package layout: `src/agent_gate/` with `__init__.py`, `__main__.py`, `cli.py`, `policy.py`, `checks.py`, `report.py`. Add a `pyproject.toml` with a console script `agent-gate`.
- CLI: `python -m agent_gate check --policy policy.toml agents/` (agents/ may be a directory of `*.toml` files or a single file). Options: `--format text|json`. Exit 0 if all agents pass, 1 if any violation, 2 for usage/parse errors (with a clear message, never a traceback).
- Agent file fields: `name`, `owner`, `model`, `monthly_budget_gbp`, `tools` (list of strings), `human_approval_for` (list of tools that need sign-off), `max_steps`.
- Policy file: `allowed_models` (list), `max_monthly_budget_gbp`, `max_steps`, `risky_tools` (list, e.g. send_email, make_payment, delete_records, post_publicly), `require_owner` (bool).
- Rules, each with a stable ID: AG001 model not on allowlist; AG002 budget missing or over the cap; AG003 a risky tool is enabled without being listed in human_approval_for; AG004 max_steps missing or over the cap; AG005 owner missing when required; AG006 unknown or misspelt field in an agent file (catch typos like `human_aproval_for`).
- Text output: one line per violation `FAIL <agent> <rule-id> <message>`, then a summary line. JSON output: a stable machine-readable list.
- `examples/`: a `policy.toml`, one compliant agent (`invoice-chaser.toml`), and one non-compliant agent (`social-poster.toml`) that trips several rules. Use made-up, generic small-business examples only.
- Tests with `unittest` in `tests/` covering every rule, the exit codes, JSON output and a malformed TOML file. `python -m unittest discover -s tests` must pass.
- A GitHub Actions example at `.github/workflows/agent-gate.yml` that runs the gate on pull requests.
- A short README section "Usage" (I'll write the rest of the README myself).

Run the tests yourself and fix anything failing before you finish. Keep the code small and readable.
