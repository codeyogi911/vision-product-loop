from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DISCOVER_PATH = REPO_ROOT / "plugins" / "vision-product-loop" / "scripts" / "discover_project.py"


def load_discover_module():
    spec = importlib.util.spec_from_file_location("vision_loop_discover_project", DISCOVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {DISCOVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


discover_module = load_discover_module()


class DiscoverProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="vision-discovery-test-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir, ignore_errors=True))

    def write(self, relative: str, text: str) -> None:
        path = self.tmpdir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_discovers_docs_agents_and_harnesses(self) -> None:
        self.write("VISION.md", "# Product Promise\n")
        self.write("docs/adr/0001-record.md", "# ADR\n")
        self.write("AGENTS.md", "# Agent instructions\n")
        self.write("package.json", json.dumps({"scripts": {"test": "vitest", "dev": "vite"}}))
        self.write("tests/test_example.py", "def test_example():\n    assert True\n")

        result = discover_module.discover_project(self.tmpdir)

        self.assertIn("VISION.md", result["docs"])
        self.assertIn("docs/adr/0001-record.md", result["docs"])
        self.assertIn("AGENTS.md", result["agents"])
        self.assertIn("package.json", result["architecture"])
        harness_names = {item["name"] for item in result["harnesses"]}
        self.assertIn("test", harness_names)
        self.assertIn("test_example.py", harness_names)


if __name__ == "__main__":
    unittest.main()
