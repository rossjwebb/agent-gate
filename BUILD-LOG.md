# Build log — agent-gate (30 Oct 2026, times GMT)

| Time | Step | Result |
|---|---|---|
| 10:35 | Fresh folder `~/codex-ambassadors/codex-build`, `git init`. Spec saved as `PROMPT-1.md` and committed. | — |
| 10:36–10:38 | **Codex pass 1**: `codex exec -s workspace-write -C . "$(cat PROMPT-1.md)"` (Codex CLI 0.162.1, ChatGPT sign-in, reasoning effort high). | Package, 6 rules, text/JSON output, examples, workflow, 22 tests. Codex ran the tests itself: 22/22 pass. ~38k tokens. |
| 10:39 | Human review: `python -m unittest` → 22 OK. Ran the gate on `examples/` → **bug**: `policy.toml` read as an agent, 6 bogus violations. Compliant agent alone → exit 0. | Bug logged as `PROMPT-2.md`. |
| 10:40 | **Codex pass 2**: same command with `PROMPT-2.md`. | Example agents moved to `examples/agents/`, CLI skips the policy file by resolved path, 2 regression tests added. ~23k tokens. |
| 10:41 | Human re-check. | **24/24 tests pass.** `examples/` → 2 agents, 6 intended violations, exit 1. `invoice-chaser` alone → PASS, exit 0. |

Not done yet: licence file, public GitHub repo (waiting for review), CI run on GitHub itself.

Raw Codex transcripts: `codex-run-1.log`, `codex-run-2.log`. Codex's own summaries: `codex-last-1.md`, `codex-last-2.md`.
