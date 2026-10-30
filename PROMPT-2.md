Small follow-up on agent-gate (in ./agent-gate):

When I ran `python -m agent_gate check --policy examples/policy.toml examples/` the gate treated policy.toml as an agent and reported 6 bogus violations for an agent called "policy". Fix it two ways:
1. Move the example agents into `examples/agents/` (keep `examples/policy.toml` where it is) and update the README and workflow paths.
2. In the CLI, if the policy file sits inside the agents path, skip it when collecting agent files, and add a test for that.

Keep everything else as it is. Run the full test suite and make sure it passes before you finish.
