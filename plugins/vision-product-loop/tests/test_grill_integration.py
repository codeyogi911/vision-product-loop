from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "vision-product-loop"


class GrillIntegrationTests(unittest.TestCase):
    def test_bundled_grill_skill_contract(self) -> None:
        text = (PLUGIN_ROOT / "skills" / "grill-me" / "SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Ask the questions one at a time", text)
        self.assertIn("recommended answer", text)
        self.assertIn("exploring the codebase", text)
        self.assertIn("VISION.md", text)

    def test_main_skill_points_to_bundled_grill(self) -> None:
        skill_dir = PLUGIN_ROOT / "skills" / "vision-product-loop"
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        reference = skill_dir / "REFERENCE.md"
        if reference.is_file():
            text = text + "\n" + reference.read_text(encoding="utf-8")

        self.assertIn("skills/grill-me/SKILL.md", text)
        self.assertIn("recommended answer", text)
        self.assertIn("one at a time", text)
        self.assertIn("update `VISION.md` continuously", text)


if __name__ == "__main__":
    unittest.main()
