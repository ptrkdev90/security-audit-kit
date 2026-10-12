import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins/security-audit/skills/software-security-audit/scripts"

def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

init = load("init_audit")
inventory = load("inventory")
validator = load("validate_audit")

class HelpersTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.audit = init.initialize(self.base / "audit")

    def write(self, name, rows):
        (self.audit / (name + ".json")).write_text(json.dumps({"schema_version": "1.0", "items": rows}))

    def coverage(self, status="reviewed"):
        return {"id": "C-1", "component": "api", "paths": ["api.py"], "check": "object authorization", "applicability": "user-controlled object ID", "status": status, "method": "source trace", "evidence": ["api.py:10-40"], "limitations": []}

    def finding(self):
        return {"id": "AUD-1", "title": "Object access", "status": "confirmed", "severity": "high", "confidence": "high", "component": "api", "locations": [{"path": "api.py", "line": 12}], "coverage_ids": ["C-1"], "prerequisites": "authenticated user", "attack_path": "input to unscoped query", "impact": "other user's records", "verification": "source trace", "evidence": ["api.py:12"], "counterevidence": "", "remediation": "scope query", "next_steps": "", "risk_acceptance": "", "fix_verification": ""}

    def test_new_audit_valid_but_not_final(self):
        self.assertEqual(validator.validate(self.audit), [])
        self.assertTrue(validator.validate(self.audit, True))

    def test_init_does_not_overwrite(self):
        marker = self.audit / "report.md"
        marker.write_text("preserve")
        with self.assertRaises(FileExistsError): init.initialize(self.audit)
        self.assertEqual(marker.read_text(), "preserve")

    def test_inventory_symlink_and_exclusions(self):
        target = self.base / "target"; target.mkdir()
        (target / "app.csproj").write_text("secret-content-not-read")
        (target / "node_modules").mkdir()
        (target / "node_modules/hidden.txt").write_text("hidden")
        outside = self.base / "outside.txt"; outside.write_text("outside-secret")
        (target / "escape.txt").symlink_to(outside)
        result = inventory.collect(target)
        self.assertEqual([x["path"] for x in result["files"]], ["app.csproj"])
        self.assertEqual(result["stack_indicators"], ["dotnet"])
        self.assertNotIn("outside-secret", json.dumps(result))
        self.assertNotIn("secret-content-not-read", json.dumps(result))
        self.assertEqual(len(result["skipped"]), 2)

    def test_final_review_with_blocker_is_structurally_valid(self):
        row = self.coverage("blocked"); row["evidence"] = []; row["limitations"] = ["Runtime unavailable; request test credentials"]
        self.write("coverage", [row])
        (self.audit / "inventory.json").write_text("{}")
        self.assertEqual(validator.validate(self.audit, True), [])

    def test_pending_and_missing_evidence_rejected(self):
        row = self.coverage(); row["evidence"] = []
        self.write("coverage", [row])
        self.assertTrue(validator.validate(self.audit))
        row["status"] = "pending"; self.write("coverage", [row])
        self.assertTrue(any("pending" in x for x in validator.validate(self.audit, True)))

    def test_findings_references_and_status_requirements(self):
        self.write("coverage", [self.coverage()])
        row = self.finding(); self.write("findings", [row])
        self.assertEqual(validator.validate(self.audit), [])
        for status, field in [("suspected", "next_steps"), ("refuted", "counterevidence"), ("accepted-risk", "risk_acceptance"), ("fixed", "fix_verification")]:
            row["status"] = status; self.write("findings", [row])
            self.assertTrue(any(field in x for x in validator.validate(self.audit)))
        row["status"] = "confirmed"; row["coverage_ids"] = ["absent"]
        self.write("findings", [row])
        self.assertTrue(any("reference" in x for x in validator.validate(self.audit)))

    def test_duplicate_ids_and_malformed_json_rejected(self):
        self.write("coverage", [self.coverage(), self.coverage()])
        self.assertTrue(any("duplicate" in x for x in validator.validate(self.audit)))
        (self.audit / "findings.json").write_text("invalid")
        self.assertTrue(any("cannot load" in x for x in validator.validate(self.audit)))

    def test_schema_rejects_boolean_line_and_extra_fields(self):
        row = self.finding(); row["locations"][0]["line"] = True; row["extra"] = 1
        self.write("findings", [row])
        errors = validator.validate(self.audit)
        self.assertTrue(any("invalid type" in x for x in errors))
        self.assertTrue(any("unknown extra" in x for x in errors))

    def test_unavailable_tool_needs_reason(self):
        row = {"id": "T-1", "tool": "semgrep", "version": "unavailable", "command": "not run", "target": "target", "utc_time": "2026-10-12T00:00:00Z", "status": "unavailable", "exit_code": None, "network_use": "none", "rules_or_database": "none", "output": "", "limitations": []}
        self.write("tool-runs", [row])
        self.assertTrue(validator.validate(self.audit))
        row["limitations"] = ["Not installed; manual review only"]
        self.write("tool-runs", [row])
        self.assertEqual(validator.validate(self.audit), [])

if __name__ == "__main__": unittest.main()
