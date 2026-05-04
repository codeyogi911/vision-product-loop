from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "vision-product-loop"


class ModuleVisionTests(unittest.TestCase):
    def test_root_vision_defines_module_visions(self) -> None:
        text = (REPO_ROOT / "VISION.md").read_text(encoding="utf-8")

        self.assertIn("Module Visions And Deep Modules", text)
        self.assertIn("visions/<module-id>.md", text)
        for term in (
            "Module",
            "Interface",
            "Implementation",
            "Depth",
            "Seam",
            "Adapter",
            "Leverage",
            "Locality",
        ):
            self.assertIn(term, text)

    def test_context_names_intelligence_layer(self) -> None:
        text = (REPO_ROOT / "CONTEXT.md").read_text(encoding="utf-8")

        self.assertIn("Module Vision", text)
        self.assertIn("Intelligence Layer", text)
        self.assertIn("Interface", text)
        self.assertIn("Implementation", text)
        self.assertIn("Locality", text)

    def test_intelligence_layer_has_module_vision(self) -> None:
        text = (REPO_ROOT / "visions" / "intelligence-layer.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Intelligence Layer Vision", text)
        self.assertIn("Parent vision", text)
        self.assertIn("Implementation Options", text)
        self.assertIn("Acceptance Checks", text)
        self.assertIn("Open Questions", text)

    def test_skill_uses_architecture_deepening_language(self) -> None:
        text = (
            PLUGIN_ROOT
            / "skills"
            / "vision-product-loop"
            / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("improve-codebase-architecture", text)
        self.assertIn("CONTEXT.md", text)
        self.assertIn("docs/adr/", text)
        self.assertIn("visions/<module-id>.md", text)
        self.assertIn("Intelligence Layer", text)


if __name__ == "__main__":
    unittest.main()
