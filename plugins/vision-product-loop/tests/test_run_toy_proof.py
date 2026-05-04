from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "plugins" / "vision-product-loop" / "scripts"
TOY_PATH = SCRIPT_DIR / "run_toy_proof.py"


def load_toy_module():
    sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("vision_loop_run_toy_proof", TOY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {TOY_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


toy_module = load_toy_module()


class ToyProofTests(unittest.TestCase):
    def test_runs_toy_project_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vision-toy-proof-") as tmp:
            target = Path(tmp) / "target"

            proof = toy_module.run_toy_proof(target)

            self.assertTrue(proof["passed"])
            self.assertEqual(proof["initial_harness_count"], 0)
            self.assertGreater(proof["final_harness_count"], 0)
            self.assertTrue((target / "scripts" / "vision_smoke_check.py").is_file())
            proof_file = target / ".vision-loop" / "toy-proof.json"
            self.assertTrue(proof_file.is_file())
            written = json.loads(proof_file.read_text(encoding="utf-8"))
            self.assertTrue(written["passed"])


if __name__ == "__main__":
    unittest.main()
