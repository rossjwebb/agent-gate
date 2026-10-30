## Usage

Requires Python 3.11+. From the `agent-gate` directory, run directly from
source using only the standard library:

```sh
export PYTHONPATH=src
python -m agent_gate check --policy examples/policy.toml examples/invoice-chaser.toml
python -m agent_gate check --policy examples/policy.toml examples/social-poster.toml --format json
python -m unittest discover -s tests
```

For the `agent-gate` console command, install with `python -m pip install .`.
The included build backend and application use only the standard library;
installation does not need to download any build dependencies.

```sh
agent-gate check --policy policy.toml agents/
python -m agent_gate check --policy policy.toml agents/ --format json
```

The input may be a single file or a directory searched recursively for `*.toml`.
Keep the policy outside the agent directory. The examples use fictional model
names; replace these with your team's model identifiers. `invoice-chaser` passes;
`social-poster` deliberately violates all six rules.

Text reports show one `FAIL <agent> <rule-id> <message>` line per violation and
a summary. JSON reports are a list of objects with `agent`, `rule_id`, and
`message` keys, or `[]` when everything passes. Files, rules, and tool names
have deterministic ordering. Missing or blank names fall back to the filename.

Exit codes: **0** pass, **1** policy violations, **2** usage, file, TOML, or
schema errors. Errors go to stderr. Invalid field types, negative/non-finite
budgets, non-positive step limits, and empty input directories are errors.
Missing budgets and step limits are policy violations. Tool lists default to
empty when absent; unknown agent fields produce AG006.

Copy `.github/workflows/agent-gate.yml` to the repository root's
`.github/workflows/` to activate it. It assumes this project lives in
`agent-gate/`; remove `working-directory` if the project is the repository root.
Change the final command to check your actual agent directory, and require
the job in your repository's branch protection settings to block merges.
