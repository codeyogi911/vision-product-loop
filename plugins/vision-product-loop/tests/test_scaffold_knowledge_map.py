from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "plugins" / "vision-product-loop" / "scripts"
SCAFFOLD_PATH = SCRIPT_DIR / "scaffold_knowledge_map.py"


def load_module(name: str, path: Path):
    sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


scaffold = load_module("scaffold_knowledge_map_under_test", SCAFFOLD_PATH)


class ScaffoldKnowledgeMapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="vision-knowledge-map-test-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))
        (self.tmp / "VISION.md").write_text("# Vision\n", encoding="utf-8")

    def test_detect_reports_missing_layout_on_fresh_repo(self) -> None:
        report = scaffold.detect(self.tmp)
        files = {f.path: f for f in report.files}
        self.assertTrue(files["VISION.md"].exists)
        self.assertFalse(files["ARCHITECTURE.md"].exists)
        self.assertFalse(files["CLAUDE.md"].exists)
        dirs = {d.path: d for d in report.dirs}
        self.assertFalse(dirs["docs/adr"].exists)
        self.assertFalse(dirs["docs/exec-plans/active"].exists)

    def test_apply_creates_minimum_layout_idempotently(self) -> None:
        first = scaffold.apply(self.tmp)
        self.assertIn("docs/adr", first.created_dirs)
        self.assertIn("docs/exec-plans/active", first.created_dirs)
        self.assertIn("docs/exec-plans/completed", first.created_dirs)
        adr_template = self.tmp / "docs" / "adr" / "template.md"
        adr_0001 = self.tmp / "docs" / "adr" / "0001-record-architecture-decisions.md"
        self.assertTrue(adr_template.is_file())
        self.assertTrue(adr_0001.is_file())
        self.assertTrue((self.tmp / "ARCHITECTURE.md").is_file())
        self.assertTrue((self.tmp / "CLAUDE.md").is_file())
        self.assertTrue((self.tmp / "AGENTS.md").is_file())

        # Second apply must not re-create or overwrite anything.
        adr_0001.write_text("# Custom user-edited ADR 0001\n", encoding="utf-8")
        second = scaffold.apply(self.tmp)
        self.assertEqual(second.created_dirs, [])
        self.assertIn("docs/adr/0001-record-architecture-decisions.md", second.skipped_files)
        self.assertEqual(
            adr_0001.read_text(encoding="utf-8"),
            "# Custom user-edited ADR 0001\n",
        )

    def test_apply_does_not_overwrite_existing_map_files(self) -> None:
        (self.tmp / "CLAUDE.md").write_text("# Pre-existing map\n", encoding="utf-8")
        report = scaffold.apply(self.tmp)
        self.assertIn("CLAUDE.md", report.skipped_files)
        self.assertEqual(
            (self.tmp / "CLAUDE.md").read_text(encoding="utf-8"),
            "# Pre-existing map\n",
        )

    def test_apply_creates_claude_as_symlink_to_agents(self) -> None:
        scaffold.apply(self.tmp)
        claude = self.tmp / "CLAUDE.md"
        agents = self.tmp / "AGENTS.md"
        self.assertTrue(claude.is_symlink())
        # Either a bare filename or a relative path that resolves to AGENTS.md.
        target = (claude.parent / claude.readlink()).resolve()
        self.assertEqual(target, agents.resolve())
        # Reading through the symlink yields the canonical content.
        self.assertEqual(
            claude.read_text(encoding="utf-8"),
            agents.read_text(encoding="utf-8"),
        )

    def test_apply_skips_symlink_when_claude_already_exists(self) -> None:
        legacy = self.tmp / "CLAUDE.md"
        legacy.write_text("# Legacy hand-written map\n", encoding="utf-8")
        scaffold.apply(self.tmp)
        # Legacy file is preserved as-is; no symlink is created over it.
        self.assertFalse(legacy.is_symlink())
        self.assertEqual(
            legacy.read_text(encoding="utf-8"),
            "# Legacy hand-written map\n",
        )

    def test_knowledge_map_gate_fires_when_no_adr_dir(self) -> None:
        gate = scaffold.knowledge_map_gate(self.tmp)
        self.assertIsNotNone(gate)
        self.assertEqual(gate["reason"], "knowledge_map_required")

    def test_knowledge_map_gate_fires_with_only_bootstrap_adr(self) -> None:
        scaffold.apply(self.tmp)
        gate = scaffold.knowledge_map_gate(self.tmp)
        self.assertIsNotNone(gate)
        self.assertEqual(gate["reason"], "knowledge_map_required")

    def test_knowledge_map_gate_passes_with_a_product_adr(self) -> None:
        scaffold.apply(self.tmp)
        product_adr = self.tmp / "docs" / "adr" / "0002-pick-runtime.md"
        product_adr.write_text(
            "# 2. Pick runtime\n\n## Status\n\nAccepted\n\n"
            "## Context\n\nx\n\n## Decision\n\ny\n\n## Consequences\n\nz\n",
            encoding="utf-8",
        )
        self.assertIsNone(scaffold.knowledge_map_gate(self.tmp))

    def test_detect_finds_scattered_decision_artefacts(self) -> None:
        notes_dir = self.tmp / "notes"
        notes_dir.mkdir()
        (notes_dir / "auth-decision.md").write_text("# Auth decision\n", encoding="utf-8")
        (notes_dir / "rfc-storage.md").write_text("# Storage RFC\n", encoding="utf-8")
        (notes_dir / "shopping-list.md").write_text("# Eggs\n", encoding="utf-8")

        report = scaffold.detect(self.tmp)
        paths = {hit.path for hit in report.scattered_decisions}
        self.assertIn("notes/auth-decision.md", paths)
        self.assertIn("notes/rfc-storage.md", paths)
        self.assertNotIn("notes/shopping-list.md", paths)

    def test_detect_does_not_double_count_existing_adrs(self) -> None:
        scaffold.apply(self.tmp)
        report = scaffold.detect(self.tmp)
        scattered_paths = {hit.path for hit in report.scattered_decisions}
        self.assertNotIn(
            "docs/adr/0001-record-architecture-decisions.md", scattered_paths
        )

    def test_detect_flags_missing_vision(self) -> None:
        (self.tmp / "VISION.md").unlink()
        report = scaffold.detect(self.tmp)
        self.assertTrue(any("VISION.md is missing" in note for note in report.notes))


if __name__ == "__main__":
    unittest.main()
