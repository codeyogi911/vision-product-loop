from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "plugins" / "vision-product-loop" / "scripts"
SCAFFOLD_PATH = SCRIPT_DIR / "scaffold_knowledge_map.py"
LINT_PATH = SCRIPT_DIR / "lint_knowledge_map.py"


def load_module(name: str, path: Path):
    sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


scaffold = load_module("scaffold_knowledge_map_for_lint_tests", SCAFFOLD_PATH)
lint = load_module("lint_knowledge_map_under_test", LINT_PATH)


class LintKnowledgeMapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="vision-knowledge-map-lint-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        (self.tmp / "VISION.md").write_text("# Vision\n", encoding="utf-8")
        scaffold.apply(self.tmp)
        self.state_path = self.tmp / ".vision-loop" / "state.json"

    def test_freshly_scaffolded_layout_passes(self) -> None:
        report = lint.run_lint(self.tmp, self.state_path)
        errors = [i for i in report.issues if i.severity == "error"]
        self.assertTrue(report.passed, msg=f"errors: {errors}")
        self.assertEqual(errors, [])

    def test_oversized_map_file_fails_budget_rule(self) -> None:
        big = "\n".join(f"line {i}" for i in range(200)) + "\n"
        (self.tmp / "CLAUDE.md").write_text(big, encoding="utf-8")
        report = lint.run_lint(self.tmp, self.state_path, line_budget=100)
        self.assertFalse(report.passed)
        rules = {i.rule for i in report.issues if i.severity == "error"}
        self.assertIn("map-line-budget", rules)

    def test_broken_link_in_map_file_fails(self) -> None:
        broken = (
            "# CLAUDE.md\n\n"
            "See [missing](docs/does-not-exist.md).\n"
        )
        (self.tmp / "CLAUDE.md").write_text(broken, encoding="utf-8")
        report = lint.run_lint(self.tmp, self.state_path)
        self.assertFalse(report.passed)
        self.assertTrue(
            any(
                i.rule == "map-link-broken" and "does-not-exist" in i.detail
                for i in report.issues
            )
        )

    def test_external_links_are_ignored(self) -> None:
        ok = (
            "# CLAUDE.md\n\n"
            "See [home](https://example.com).\n"
            "See [vision](VISION.md).\n"
        )
        (self.tmp / "CLAUDE.md").write_text(ok, encoding="utf-8")
        report = lint.run_lint(self.tmp, self.state_path)
        self.assertTrue(report.passed)

    def test_adr_missing_section_fails(self) -> None:
        bad_adr = self.tmp / "docs" / "adr" / "0002-broken.md"
        bad_adr.write_text("# 2. Broken\n\n## Status\n\nAccepted\n", encoding="utf-8")
        report = lint.run_lint(self.tmp, self.state_path)
        self.assertFalse(report.passed)
        rules = {i.rule for i in report.issues if i.severity == "error"}
        self.assertIn("adr-missing-section", rules)

    def test_exec_plan_in_active_marked_closed_fails(self) -> None:
        plan = self.tmp / "docs" / "exec-plans" / "active" / "auth-rewrite.md"
        plan.write_text("# Plan: auth rewrite\n", encoding="utf-8")
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps({"closed_exec_plans": ["auth-rewrite"]}),
            encoding="utf-8",
        )
        report = lint.run_lint(self.tmp, self.state_path)
        self.assertFalse(report.passed)
        rules = {i.rule for i in report.issues if i.severity == "error"}
        self.assertIn("exec-plan-stale", rules)


if __name__ == "__main__":
    unittest.main()
