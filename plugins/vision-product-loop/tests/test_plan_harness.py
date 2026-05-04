from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLAN_PATH = REPO_ROOT / "plugins" / "vision-product-loop" / "scripts" / "plan_harness.py"


def load_plan_module():
    spec = importlib.util.spec_from_file_location("vision_loop_plan_harness", PLAN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {PLAN_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


plan_module = load_plan_module()


class HarnessPlanTests(unittest.TestCase):
    def test_plans_harness_when_project_has_none(self) -> None:
        discovery = {
            "docs": ["VISION.md"],
            "agents": [],
            "architecture": ["package.json"],
            "harnesses": [],
        }

        plan = plan_module.plan_harness(discovery)

        self.assertEqual(plan["strategy"], "create-minimal-harness")
        self.assertEqual(plan["recommended"]["name"], "test:vision")
        self.assertIn("shortest evidence path", plan["reason"])

    def test_reuses_existing_harness(self) -> None:
        discovery = {
            "docs": ["VISION.md"],
            "agents": [],
            "architecture": [],
            "harnesses": [
                {
                    "kind": "file",
                    "name": "test_self_check.py",
                    "path": "plugins/vision-product-loop/tests/test_self_check.py",
                }
            ],
        }

        plan = plan_module.plan_harness(discovery)

        self.assertEqual(plan["strategy"], "reuse-existing-harness")
        self.assertEqual(plan["recommended"]["name"], "test_self_check.py")


if __name__ == "__main__":
    unittest.main()
