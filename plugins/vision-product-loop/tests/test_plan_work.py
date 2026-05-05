from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "plugins" / "vision-product-loop" / "scripts"
PLAN_WORK_PATH = SCRIPT_DIR / "plan_work.py"


def load_plan_work_module():
    sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("vision_loop_plan_work", PLAN_WORK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {PLAN_WORK_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


plan_work_module = load_plan_work_module()


class WorkPlanTests(unittest.TestCase):
    def write_project(self, root: Path) -> None:
        (root / "VISION.md").write_text("# Vision\n", encoding="utf-8")
        (root / "TODOS.md").write_text(
            "# TODOs\n\n"
            "## Validate mobile brief/action mode\n\n"
            "What: Test the mobile brief/action mode against real founder scenarios.\n\n"
            "Why: Mobile must stay focused on approval and urgent action.\n\n"
            "Context: Use 5-10 real operational scenarios before hardening.\n",
            encoding="utf-8",
        )
        (root / "package.json").write_text(
            json.dumps(
                {
                    "scripts": {
                        "test": "node --test test/*.test.mjs",
                        "web:typecheck": "npm --prefix apps/web run typecheck",
                        "web:test": "npm --prefix apps/web run test",
                        "eval:all": "npm --prefix apps/web run eval:all",
                    }
                }
            ),
            encoding="utf-8",
        )
        # Satisfy the knowledge-map gate so plan_work returns a sprint, not a
        # gate-blocked stub. Tests focused on planning logic (not the gate)
        # need this fixture; gate behaviour has its own tests below.
        adr_dir = root / "docs" / "adr"
        adr_dir.mkdir(parents=True, exist_ok=True)
        (adr_dir / "0002-pick-mobile-surface.md").write_text(
            "# 2. Pick mobile surface\n\n"
            "## Status\n\nAccepted\n\n"
            "## Context\n\nFounders need mobile-first approval flows.\n\n"
            "## Decision\n\nShip a mobile web surface.\n\n"
            "## Consequences\n\nDesktop comes later.\n",
            encoding="utf-8",
        )

    def test_builds_task_plan_from_open_todo(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-plan-work-") as tmp:
            root = Path(tmp)
            self.write_project(root)

            plan = plan_work_module.plan_work(root)

        task = plan["sprint"]["tasks"][0]
        self.assertEqual(plan["planning_granularity"], "sprint_task_subtask")
        self.assertEqual(plan["test_cadence"], "task_end")
        self.assertEqual(task["source"], "todos")
        self.assertEqual(task["title"], "Validate mobile brief/action mode")
        self.assertGreaterEqual(len(task["subtasks"]), 4)

    def test_task_end_validation_keeps_broad_tests_out_of_subtasks(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-plan-work-") as tmp:
            root = Path(tmp)
            self.write_project(root)

            plan = plan_work_module.plan_work(root)

        task = plan["sprint"]["tasks"][0]
        broad_test_markers = {"run_now"}
        non_close_subtasks = task["subtasks"][:-1]
        self.assertTrue(
            all(subtask["broad_tests"] not in broad_test_markers for subtask in non_close_subtasks)
        )
        self.assertEqual(task["validation"]["cadence"], "task_end")
        self.assertIn("npm run web:typecheck", task["validation"]["task_close_commands"])
        self.assertIn("npm run web:test", task["validation"]["task_close_commands"])

    def test_prefers_open_state_gap_over_todo(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-plan-work-") as tmp:
            root = Path(tmp)
            self.write_project(root)
            state_dir = root / ".vision-loop"
            state_dir.mkdir()
            (state_dir / "state.json").write_text(
                json.dumps(
                    {
                        "gaps": [
                            {
                                "id": "operating-ledger-review",
                                "status": "open",
                                "vision_anchor": "Work Orders need review evidence.",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            plan = plan_work_module.plan_work(root)

        task = plan["sprint"]["tasks"][0]
        self.assertEqual(task["source"], "loop-state-gap")
        self.assertEqual(task["title"], "operating-ledger-review")

    def test_gate_blocks_plan_when_no_product_adrs_exist(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-plan-work-gate-") as tmp:
            root = Path(tmp)
            (root / "VISION.md").write_text("# Vision\n", encoding="utf-8")
            # No docs/adr/ directory — gate must fire.
            plan = plan_work_module.plan_work(root)

        self.assertNotIn("sprint", plan)
        self.assertEqual(plan["gate"]["reason"], "knowledge_map_required")
        self.assertIn("knowledge-map", " ".join(plan["gate"]["next_actions"]))

    def test_gate_blocks_plan_with_only_bootstrap_adr(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-plan-work-gate-") as tmp:
            root = Path(tmp)
            (root / "VISION.md").write_text("# Vision\n", encoding="utf-8")
            adr_dir = root / "docs" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "0001-record-architecture-decisions.md").write_text(
                "# 1. Record architecture decisions\n", encoding="utf-8"
            )
            plan = plan_work_module.plan_work(root)

        self.assertNotIn("sprint", plan)
        self.assertEqual(plan["gate"]["reason"], "knowledge_map_required")

    def test_gate_can_be_bypassed_for_diagnostics(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-plan-work-gate-") as tmp:
            root = Path(tmp)
            (root / "VISION.md").write_text("# Vision\n", encoding="utf-8")
            plan = plan_work_module.plan_work(
                root,
                enforce_knowledge_map_gate=False,
            )

        self.assertNotIn("gate", plan)
        self.assertIn("sprint", plan)

    def test_skips_todo_with_completed_status_detail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-plan-work-") as tmp:
            root = Path(tmp)
            self.write_project(root)
            (root / "TODOS.md").write_text(
                "# TODOs\n\n"
                "## Design the ecommerce operator Skill Registry\n\n"
                "Status: First design pass complete in docs/vertical-agent.md.\n\n"
                "## Validate mobile brief/action mode\n\n"
                "What: Test the mobile brief/action mode against real founder scenarios.\n",
                encoding="utf-8",
            )

            plan = plan_work_module.plan_work(root)

        task = plan["sprint"]["tasks"][0]
        self.assertEqual(task["title"], "Validate mobile brief/action mode")


if __name__ == "__main__":
    unittest.main()
