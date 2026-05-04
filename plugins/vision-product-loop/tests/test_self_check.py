from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SELF_CHECK_PATH = REPO_ROOT / "plugins" / "vision-product-loop" / "scripts" / "self_check.py"


def load_self_check_module():
    spec = importlib.util.spec_from_file_location("vision_loop_self_check", SELF_CHECK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SELF_CHECK_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


self_check = load_self_check_module()


class SelfCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="vision-loop-test-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir, ignore_errors=True))
        self.plugin_root = self.tmpdir / "plugins" / "vision-product-loop"
        shutil.copytree(REPO_ROOT / "plugins" / "vision-product-loop", self.plugin_root)
        shutil.copy2(REPO_ROOT / "VISION.md", self.tmpdir / "VISION.md")
        shutil.copy2(REPO_ROOT / "CONTEXT.md", self.tmpdir / "CONTEXT.md")
        shutil.copytree(REPO_ROOT / "visions", self.tmpdir / "visions")
        self.state_path = self.tmpdir / ".vision-loop" / "state.json"

    def run_check(self):
        return self_check.run_self_check(
            self.tmpdir,
            self.plugin_root,
            self.state_path,
        )

    def test_writes_state_file(self) -> None:
        (self.plugin_root / "README.md").unlink()

        state, exit_code = self.run_check()

        self.assertEqual(exit_code, 0)
        self.assertTrue(self.state_path.is_file())
        written_state = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(written_state["vision_file"], "VISION.md")
        self.assertIn(written_state["phase"], {"research", "reflect"})
        self.assertEqual(written_state["iteration"], 0)
        self.assertIsInstance(written_state["harnesses"], list)
        self.assertIn("reflection", written_state)
        self.assertEqual(written_state["status"], state["status"])
        self.assertEqual(written_state["stop_reason"], "gap_selected")
        self.assertIsNotNone(written_state["evidence"])

    def test_reports_gap_when_main_skill_is_missing(self) -> None:
        skill_path = (
            self.plugin_root
            / "skills"
            / "vision-product-loop"
            / "SKILL.md"
        )
        skill_path.unlink()

        state, exit_code = self.run_check()

        self.assertEqual(exit_code, 0)
        self.assertEqual(state["selected_gap"]["id"], "missing-main-skill")
        self.assertEqual(state["stop_reason"], "gap_selected")
        self.assertIn("missing-main-skill", {gap["id"] for gap in state["gaps"]})

    def test_reports_gap_when_capability_artifact_is_missing(self) -> None:
        discovery_path = self.plugin_root / "scripts" / "discover_project.py"
        if discovery_path.exists():
            discovery_path.unlink()

        state, exit_code = self.run_check()

        self.assertEqual(exit_code, 0)
        gap_ids = {gap["id"] for gap in state["gaps"]}
        self.assertIn(
            "capability-project-discovery-discovery-helper-missing-artifact",
            gap_ids,
        )

    def test_reports_invalid_capability_rubric_json(self) -> None:
        rubric_path = self.plugin_root / "capability_rubric.json"
        rubric_path.write_text("{not-json", encoding="utf-8")

        state, exit_code = self.run_check()

        self.assertEqual(exit_code, 0)
        self.assertEqual(state["selected_gap"]["id"], "invalid-capability-rubric-json")

    @unittest.skipIf(
        os.environ.get("VISION_LOOP_SKIP_VALIDATION_CAPTURE") == "1",
        "avoid recursive validation-capture test",
    )
    def test_records_validation_tests_when_requested(self) -> None:
        state, _exit_code = self_check.run_self_check(
            self.tmpdir,
            self.plugin_root,
            self.state_path,
            run_tests=True,
        )

        validation = [
            item for item in state["evidence"] if item["check"] == "validation_tests"
        ]
        self.assertEqual(len(validation), 1)
        self.assertTrue(validation[0]["passed"])


if __name__ == "__main__":
    unittest.main()
