import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_gate.checks import check_agent
from agent_gate.policy import Policy


class RuleTests(unittest.TestCase):
    def setUp(self):
        self.policy = Policy(["approved"], 50, 20, ["send_email", "make_payment"], True)
        self.agent = {
            "name": "example",
            "owner": "accounts",
            "model": "approved",
            "monthly_budget_gbp": 50,
            "tools": ["read_invoices", "send_email"],
            "human_approval_for": ["send_email"],
            "max_steps": 20,
        }

    def rules(self):
        return [item.rule_id for item in check_agent(self.agent, self.policy, "fallback")]

    def test_compliant_at_caps(self):
        self.assertEqual(self.rules(), [])

    def test_ag001_unapproved_or_missing_model(self):
        self.agent["model"] = "other"
        self.assertEqual(self.rules(), ["AG001"])
        del self.agent["model"]
        self.assertEqual(self.rules(), ["AG001"])

    def test_ag002_over_cap_or_missing_budget(self):
        self.agent["monthly_budget_gbp"] = 50.01
        self.assertEqual(self.rules(), ["AG002"])
        del self.agent["monthly_budget_gbp"]
        self.assertEqual(self.rules(), ["AG002"])

    def test_ag003_each_unapproved_risky_tool_once(self):
        self.agent["tools"] += ["make_payment", "send_email"]
        self.agent["human_approval_for"] = []
        results = check_agent(self.agent, self.policy, "fallback")
        self.assertEqual([item.rule_id for item in results], ["AG003", "AG003"])
        self.assertIn("make_payment", results[0].message)
        self.assertIn("send_email", results[1].message)

    def test_ag003_missing_approval_list(self):
        del self.agent["human_approval_for"]
        self.assertEqual(self.rules(), ["AG003"])

    def test_unused_risky_tools_need_no_approval(self):
        self.agent["tools"] = ["read_invoices"]
        self.agent["human_approval_for"] = []
        self.assertEqual(self.rules(), [])

    def test_ag004_over_cap_or_missing_steps(self):
        self.agent["max_steps"] = 21
        self.assertEqual(self.rules(), ["AG004"])
        del self.agent["max_steps"]
        self.assertEqual(self.rules(), ["AG004"])

    def test_ag005_missing_or_blank_owner(self):
        del self.agent["owner"]
        self.assertEqual(self.rules(), ["AG005"])
        self.agent["owner"] = "  "
        self.assertEqual(self.rules(), ["AG005"])

    def test_owner_optional(self):
        del self.agent["owner"]
        policy = Policy(["approved"], 50, 20, [], False)
        self.assertEqual(check_agent(self.agent, policy, "fallback"), [])

    def test_ag006_typo_does_not_grant_approval(self):
        self.agent["human_aproval_for"] = self.agent.pop("human_approval_for")
        self.assertEqual(self.rules(), ["AG003", "AG006"])

    def test_fallback_name(self):
        del self.agent["name"]
        del self.agent["owner"]
        self.assertEqual(check_agent(self.agent, self.policy, "fallback")[0].agent, "fallback")

    def test_invalid_types_and_ranges_are_errors(self):
        cases = [
            ("monthly_budget_gbp", True), ("monthly_budget_gbp", -1),
            ("monthly_budget_gbp", float("nan")), ("monthly_budget_gbp", float("inf")),
            ("max_steps", True), ("max_steps", 2.5), ("max_steps", 0),
            ("tools", "send_email"), ("tools", [1]),
            ("human_approval_for", [False]), ("owner", 42), ("name", []),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                agent = {**self.agent, field: value}
                with self.assertRaisesRegex(ValueError, field):
                    check_agent(agent, self.policy, "fallback")


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.policy = ROOT / "examples" / "policy.toml"

    def run_cli(self, *args):
        env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
        return subprocess.run(
            [sys.executable, "-m", "agent_gate", *map(str, args)],
            cwd=self.directory, env=env, text=True, capture_output=True,
        )

    def check(self, path, *args):
        return self.run_cli("check", "--policy", self.policy, path, *args)

    def assert_error(self, result):
        self.assertEqual(result.returncode, 2)
        self.assertIn("error:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_pass_exit_and_text_summary(self):
        result = self.check(ROOT / "examples" / "invoice-chaser.toml")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "PASS: checked 1 agent(s); 0 violation(s)\n")

    def test_violation_exit_and_text_lines(self):
        result = self.check(ROOT / "examples" / "social-poster.toml")
        self.assertEqual(result.returncode, 1, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 7)
        for index, line in enumerate(lines[:-1], 1):
            self.assertTrue(line.startswith(f"FAIL social-poster AG00{index} "), line)
        self.assertEqual(lines[-1], "FAIL: checked 1 agent(s); 6 violation(s)")

    def test_json_list_schema_and_pass(self):
        result = self.check(ROOT / "examples" / "social-poster.toml", "--format", "json")
        self.assertEqual(result.returncode, 1)
        items = json.loads(result.stdout)
        self.assertEqual([item["rule_id"] for item in items], [f"AG00{i}" for i in range(1, 7)])
        for item in items:
            self.assertEqual(set(item), {"agent", "rule_id", "message"})
            self.assertEqual(item["agent"], "social-poster")
            self.assertIsInstance(item["message"], str)
        result = self.check(ROOT / "examples" / "invoice-chaser.toml", "--format", "json")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), [])

    def test_recursive_directory_and_stable_order(self):
        content = (ROOT / "examples" / "social-poster.toml").read_text()
        (self.directory / "z.toml").write_text(content.replace("social-poster", "last"))
        nested = self.directory / "nested"
        nested.mkdir()
        (nested / "a.toml").write_text(content.replace("social-poster", "first"))
        (self.directory / "ignored.txt").write_text("not TOML")
        first = self.check(self.directory, "--format", "json")
        second = self.check(self.directory, "--format", "json")
        self.assertEqual(first.returncode, 1)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual([item["agent"] for item in json.loads(first.stdout)], ["first"] * 6 + ["last"] * 6)

    def test_malformed_agent_toml(self):
        path = self.directory / "broken.toml"
        path.write_text('name = "unterminated')
        result = self.check(path)
        self.assert_error(result)
        self.assertIn("broken.toml", result.stderr)

    def test_malformed_or_invalid_policy(self):
        original = self.policy.read_text()
        self.policy = self.directory / "policy.toml"
        for content in ["bad = [", "", original.replace("max_steps = 20", "max_steps = true"), original + "typo = 1\n"]:
            with self.subTest(content=content):
                self.policy.write_text(content)
                self.assert_error(self.check(ROOT / "examples" / "invoice-chaser.toml"))

    def test_invalid_agent_schema(self):
        path = self.directory / "bad-types.toml"
        path.write_text('tools = "send_email"')
        result = self.check(path)
        self.assert_error(result)
        self.assertIn("tools must be", result.stderr)

    def test_invalid_utf8(self):
        path = self.directory / "bad-encoding.toml"
        path.write_bytes(b"\xff")
        self.assert_error(self.check(path))

    def test_missing_path_or_empty_directory(self):
        self.assert_error(self.check(self.directory / "missing.toml"))
        self.assert_error(self.check(self.directory))

    def test_usage_errors(self):
        for args in [(), ("check",), ("unknown",), ("check", "--format", "xml")]:
            with self.subTest(args=args):
                self.assert_error(self.run_cli(*args))


if __name__ == "__main__":
    unittest.main()
