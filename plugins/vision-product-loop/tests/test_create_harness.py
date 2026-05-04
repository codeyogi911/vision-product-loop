from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CREATE_PATH = REPO_ROOT / "plugins" / "vision-product-loop" / "scripts" / "create_harness.py"


def load_create_module():
    spec = importlib.util.spec_from_file_location("vision_loop_create_harness", CREATE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {CREATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


create_module = load_create_module()


def scripted_plan() -> dict:
    return {
        "strategy": "create-minimal-harness",
        "recommended": {
            "kind": "new-scripted-check",
            "name": "vision_smoke_check",
            "command": "python3 scripts/vision_smoke_check.py",
        },
    }


class CreateHarnessTests(unittest.TestCase):
    def test_dry_run_does_not_write_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-create-harness-") as tmp:
            root = Path(tmp)
            result = create_module.create_harness(root, scripted_plan())

            self.assertTrue(result["dry_run"])
            self.assertFalse((root / "scripts" / "vision_smoke_check.py").exists())
            self.assertEqual(result["changes"][0]["action"], "planned")

    def test_apply_creates_scripted_check(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-create-harness-") as tmp:
            root = Path(tmp)
            (root / "VISION.md").write_text("# Vision\n", encoding="utf-8")

            result = create_module.create_harness(root, scripted_plan(), apply=True)

            script_path = root / "scripts" / "vision_smoke_check.py"
            self.assertFalse(result["dry_run"])
            self.assertTrue(script_path.is_file())
            run = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(run.returncode, 0)
            self.assertIn("vision smoke check passed", run.stdout)

    def test_apply_protects_existing_file_without_force(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-create-harness-") as tmp:
            root = Path(tmp)
            script_path = root / "scripts" / "vision_smoke_check.py"
            script_path.parent.mkdir(parents=True)
            script_path.write_text("custom", encoding="utf-8")

            result = create_module.create_harness(root, scripted_plan(), apply=True)

            self.assertEqual(script_path.read_text(encoding="utf-8"), "custom")
            self.assertEqual(result["changes"][0]["action"], "skipped")


if __name__ == "__main__":
    unittest.main()
