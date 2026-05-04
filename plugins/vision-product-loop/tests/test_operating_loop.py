from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "vision-product-loop"


LOOP_PHASES = ("Research", "Build", "Verify", "Test", "Reflect")


class OperatingLoopTests(unittest.TestCase):
    def test_root_vision_defines_operating_loop(self) -> None:
        text = (REPO_ROOT / "VISION.md").read_text(encoding="utf-8")

        self.assertIn("Operating Loop", text)
        for phase in LOOP_PHASES:
            self.assertIn(f"{phase}:", text)
        self.assertIn("When the user returns", text)
        self.assertIn("Evidence Harnesses", text)
        self.assertIn("A harness is an evidence-producing capability", text)

    def test_context_defines_loop_and_harness(self) -> None:
        text = (REPO_ROOT / "CONTEXT.md").read_text(encoding="utf-8")

        self.assertIn("Operating Loop", text)
        self.assertIn("Harness", text)
        self.assertIn("Research, Build, Verify, Test, and Reflect", text)
        self.assertIn("evidence-producing capability", text)

    def test_skill_uses_loop_phases_and_harness_interface(self) -> None:
        text = (
            PLUGIN_ROOT
            / "skills"
            / "vision-product-loop"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        for phase in LOOP_PHASES:
            self.assertIn(f"{phase}:", text)
        self.assertIn("harness as an evidence-producing capability", text)
        self.assertIn("When the user returns", text)

    def test_readme_documents_operating_loop(self) -> None:
        text = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Operating Loop", text)
        self.assertIn("Research, Build, Verify, Test, Reflect", text)
        self.assertIn("A harness is an evidence-producing capability", text)

    def test_self_check_state_has_loop_fields(self) -> None:
        text = (PLUGIN_ROOT / "scripts" / "self_check.py").read_text(
            encoding="utf-8"
        )

        self.assertIn('"phase"', text)
        self.assertIn('"iteration"', text)
        self.assertIn('"harnesses"', text)
        self.assertIn('"reflection"', text)


if __name__ == "__main__":
    unittest.main()
