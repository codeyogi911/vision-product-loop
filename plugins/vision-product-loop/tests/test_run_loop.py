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
SCRIPT_DIR = REPO_ROOT / "plugins" / "vision-product-loop" / "scripts"
RUN_LOOP_PATH = SCRIPT_DIR / "run_loop.py"
SELF_CHECK_PATH = SCRIPT_DIR / "self_check.py"


def load_module(name: str, path: Path):
    sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


run_loop_module = load_module("vision_loop_run_loop", RUN_LOOP_PATH)
self_check_module = load_module("vision_loop_self_check_for_run_loop", SELF_CHECK_PATH)


@unittest.skipIf(
    os.environ.get("VISION_LOOP_SKIP_VALIDATION_CAPTURE") == "1",
    "avoid recursive run-loop validation",
)
class RunLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="vision-run-loop-test-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir, ignore_errors=True))
        self.plugin_root = self.tmpdir / "plugins" / "vision-product-loop"
        shutil.copytree(REPO_ROOT / "plugins" / "vision-product-loop", self.plugin_root)
        shutil.copy2(REPO_ROOT / "VISION.md", self.tmpdir / "VISION.md")
        shutil.copy2(REPO_ROOT / "CONTEXT.md", self.tmpdir / "CONTEXT.md")
        shutil.copytree(REPO_ROOT / "visions", self.tmpdir / "visions")
        self.state_path = self.tmpdir / ".vision-loop" / "state.json"

    def test_marks_complete_when_no_gaps_and_validation_passes(self) -> None:
        state, exit_code = run_loop_module.run_loop(
            self.tmpdir,
            self.plugin_root,
            self.state_path,
            slice_budget=5,
            run_tests=True,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(state["status"], "complete")
        self.assertEqual(state["stop_reason"], "vision_complete")
        self.assertEqual(state["vision_file"], "VISION.md")
        phases = [event["phase"] for event in state["loop_events"]]
        self.assertEqual(phases, ["research", "build", "verify", "test", "reflect"])
        harness_ids = {item["id"] for item in state["harnesses"]}
        self.assertIn("plugin-self-check", harness_ids)
        self.assertIn("plugin-unittest-suite", harness_ids)

        written = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.assertEqual(written["status"], "complete")

    def test_self_check_exits_zero_after_loop_marks_complete(self) -> None:
        run_loop_module.run_loop(
            self.tmpdir,
            self.plugin_root,
            self.state_path,
            slice_budget=5,
            run_tests=True,
        )

        state, exit_code = self_check_module.run_self_check(
            self.tmpdir,
            self.plugin_root,
            self.state_path,
            run_tests=False,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(state["status"], "complete")
        self.assertEqual(state["stop_reason"], "vision_complete")

    def test_reports_selected_gap_when_plugin_is_incomplete(self) -> None:
        (self.plugin_root / "README.md").unlink()

        state, exit_code = run_loop_module.run_loop(
            self.tmpdir,
            self.plugin_root,
            self.state_path,
            slice_budget=5,
            run_tests=False,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(state["status"], "planning")
        self.assertEqual(state["stop_reason"], "gap_selected")
        self.assertEqual(state["selected_gap"]["id"], "missing-readme")


if __name__ == "__main__":
    unittest.main()
