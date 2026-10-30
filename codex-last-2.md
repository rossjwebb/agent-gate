Done in `./agent-gate`:

- Moved example agents into `examples/agents/`, keeping the policy in place.
- Updated README, workflow, and test paths.
- Excluded the policy by resolved path during collection, with regression tests.

All **24 tests pass**. Your original command now checks 2 agents and reports only the 6 intentional `social-poster` violations.