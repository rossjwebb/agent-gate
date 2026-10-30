# agent-gate — a pre-merge policy gate for AI agents, built with Codex

**What it does:** teams keep AI agent definitions as small TOML files. Before a pull request merges, `agent-gate` checks every agent against a policy and fails the build if one breaks the rules:

| Rule | Catches |
|---|---|
| AG001 | Model not on the approved list |
| AG002 | Monthly budget missing or over the cap |
| AG003 | A risky tool (send email, make payment, delete records, post publicly) enabled with no human sign-off |
| AG004 | Step limit missing or over the cap |
| AG005 | No named owner |
| AG006 | Unknown or misspelt field (e.g. `human_aproval_for`, which would otherwise silently switch off the sign-off) |

Python 3.11+, standard library only, no network, no database. Exit 0 = pass, 1 = violations, 2 = bad input.

```sh
cd agent-gate
export PYTHONPATH=src
python -m unittest discover -s tests          # 24 tests
python -m agent_gate check --policy examples/policy.toml examples/agents/
python -m agent_gate check --policy examples/policy.toml examples/agents/ --format json
```

The examples are invented small-business agents (an invoice chaser that passes, a social poster that trips all six rules).

## How it was built (honestly)

**Codex wrote the code.** All of `agent-gate/` — the package, the tests, the examples, the GitHub Actions workflow and the usage section of its README — was written by OpenAI Codex (Codex CLI 0.162.1, `codex exec`, workspace-write sandbox, signed in with a ChatGPT plan, no API key). No code was hand-edited.

The human side was the spec, the review and the follow-up:

1. **Spec as a prompt** — [`PROMPT-1.md`](PROMPT-1.md): what the tool is, the fields, the six rules with stable IDs, exit codes, "standard library only", and "run the tests and fix anything failing before you finish". The prompt was drafted with help from my AI assistant.
2. **Codex pass 1** — `codex exec -s workspace-write -C . "$(cat PROMPT-1.md)"`. About 2.5 minutes. Codex built the package, ran the suite itself and finished at 22 passing tests.
3. **Review** — running the gate over the whole `examples/` folder showed a real bug: it treated `policy.toml` as an agent and reported six bogus failures.
4. **Codex pass 2** — [`PROMPT-2.md`](PROMPT-2.md) described the bug and asked for a fix plus a regression test. About 50 seconds. 24 tests passing; the gate now reports only the six deliberate violations.

Each step is a separate git commit, so `git log` shows the sequence. Timings and outcomes are in [`BUILD-LOG.md`](BUILD-LOG.md).

## Why this exists

Agent configs drift. Someone bumps a budget, swaps in an unapproved model, or mistypes the one field that switches human approval on, and nobody notices until something has gone out. Checking that in CI, before merge, makes the controls compulsory instead of optional. This is a small, generic version of an idea I've used on bigger agent programmes.

MIT licence (to add before publishing).
