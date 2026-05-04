from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLAN_PATH = REPO_ROOT / "plugins" / "vision-product-loop" / "scripts" / "plan_orchestration.py"


def load_plan_module():
    spec = importlib.util.spec_from_file_location("vision_loop_plan_orchestration", PLAN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {PLAN_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


plan_module = load_plan_module()


class OrchestrationPlanTests(unittest.TestCase):
    def test_keeps_blocking_work_local(self) -> None:
        plan = plan_module.plan_orchestration(
            [
                {
                    "id": "selected-gap",
                    "title": "Implement selected gap",
                    "blocking": True,
                    "independent": False,
                }
            ],
            allow_delegation=True,
        )

        self.assertEqual(plan["local"][0]["id"], "selected-gap")
        self.assertEqual(plan["delegate"], [])

    def test_delegates_independent_sidecar_when_allowed(self) -> None:
        plan = plan_module.plan_orchestration(
            [
                {
                    "id": "doc-scan",
                    "title": "Scan docs for harness references",
                    "blocking": False,
                    "independent": True,
                }
            ],
            allow_delegation=True,
        )

        self.assertEqual(plan["delegate"][0]["id"], "doc-scan")
        self.assertEqual(plan["local"], [])

    def test_blocks_autonomy_boundary_crossing_task(self) -> None:
        plan = plan_module.plan_orchestration(
            [
                {
                    "id": "publish-marketplace",
                    "title": "Publish marketplace entry",
                    "blocking": False,
                    "independent": True,
                }
            ],
            allow_delegation=True,
        )

        self.assertEqual(plan["blocked"][0]["id"], "publish-marketplace")
        self.assertIn("autonomy_boundary", plan["blocked"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
