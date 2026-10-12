#!/usr/bin/env python3
"""Validate artifact structure and consistency, not vulnerability correctness."""
import argparse
import json
from pathlib import Path

SCHEMAS = Path(__file__).resolve().parents[1] / "assets" / "schemas"

def schema_errors(value, schema, path="$ "):
    errors = []
    kinds = {"object": lambda v: isinstance(v, dict), "array": lambda v: isinstance(v, list), "string": lambda v: isinstance(v, str), "boolean": lambda v: isinstance(v, bool), "integer": lambda v: isinstance(v, int) and not isinstance(v, bool), "null": lambda v: v is None}
    expected = schema.get("type")
    if expected and not any(kinds[k](value) for k in ([expected] if isinstance(expected, str) else expected)):
        return [path + ": invalid type"]
    if "const" in schema and value != schema["const"]: errors.append(path + ": invalid constant")
    if "enum" in schema and value not in schema["enum"]: errors.append(path + ": invalid enum")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value: errors.append(path + ": missing " + key)
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value.keys() - properties.keys(): errors.append(path + ": unknown " + key)
        for key in value.keys() & properties.keys(): errors.extend(schema_errors(value[key], properties[key], path + "." + key))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0): errors.append(path + ": too few items")
        for i, item in enumerate(value): errors.extend(schema_errors(item, schema.get("items", {}), path + f"[{i}]"))
    if isinstance(value, str) and len(value.strip()) < schema.get("minLength", 0): errors.append(path + ": empty text")
    if isinstance(value, int) and not isinstance(value, bool) and value < schema.get("minimum", value): errors.append(path + ": below minimum")
    return errors

def validate(directory, final=False):
    directory = Path(directory)
    errors, data, versions = [], {}, {}
    for name in ("coverage", "findings", "tool-runs", "evidence"):
        try:
            value = json.loads((directory / (name + ".json")).read_text(encoding="utf-8"))
            schema = json.loads((SCHEMAS / (name + ".schema.json")).read_text(encoding="utf-8"))
            problems = schema_errors(value, schema, name)
            errors.extend(problems)
            if not problems:
                data[name] = value["items"]
                versions[name] = value["schema_version"]
        except (OSError, ValueError) as exc:
            errors.append(name + ": cannot load JSON (" + type(exc).__name__ + ")")
    for name, rows in data.items():
        ids = [r["id"] for r in rows]
        if len(ids) != len(set(ids)): errors.append(name + ": duplicate IDs")
    coverage_ids = {r["id"] for r in data.get("coverage", [])}
    for row in data.get("coverage", []):
        status = row["status"]
        if status == "reviewed" and not row["evidence"]: errors.append(row["id"] + ": reviewed requires evidence")
        if status in {"blocked", "not-applicable"} and not row["limitations"]: errors.append(row["id"] + ": requires reason/limitations")
        if final and status == "pending": errors.append(row["id"] + ": pending coverage at finalization")
    if final and versions.get("findings") == "1.0":
        errors.append("findings: legacy 1.0 requires manual classification migration to 1.1 before finalization")
    evidence = {r["id"]: r for r in data.get("evidence", [])}
    for item in evidence.values():
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(item["observed_at"].replace("Z", "+00:00"))
            if dt.tzinfo is None: raise ValueError()
        except ValueError:
            errors.append(item["id"] + ": observed_at requires an offset timestamp")
        if item["sha256"] is not None:
            import re
            if not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
                errors.append(item["id"] + ": invalid sha256")
    for row in data.get("findings", []):
        if versions.get("findings") == "1.2":
            refs = row.get("evidence_ids", [])
            if "evidence_ids" not in row or "threat_ids" not in row:
                errors.append(row["id"] + ": requires evidence_ids and threat_ids")
            if any(ref not in evidence for ref in refs):
                errors.append(row["id"] + ": unknown evidence reference")
            if row["status"] in {"confirmed", "accepted-risk", "fixed"} and not refs:
                errors.append(row["id"] + ": requires registered evidence")
            if row.get("kind") == "security-vulnerability" and row["status"] in {"confirmed", "accepted-risk", "fixed"}:
                expected = {"source-trace": "source", "runtime-test": "runtime"}.get(row.get("verification_basis"))
                if not any(evidence.get(ref, {}).get("type") == expected for ref in refs):
                    errors.append(row["id"] + ": verification basis lacks matching evidence type")
        if versions.get("findings") in {"1.1", "1.2"}:
            for field in ("kind", "verification_basis", "exploitability", "severity_rationale", "verification_limits", "refutation_scope"):
                if field not in row:
                    errors.append(row["id"] + ": requires " + field)
            for field in ("severity_rationale", "verification_limits"):
                if not row.get(field, "").strip():
                    errors.append(row["id"] + ": requires nonempty " + field)
            if row.get("kind") == "security-vulnerability" and row["status"] in {"confirmed", "accepted-risk", "fixed"}:
                if row.get("verification_basis") not in {"source-trace", "runtime-test"}:
                    errors.append(row["id"] + ": confirmed vulnerability requires source trace or runtime verification")
                if row.get("exploitability") not in {"demonstrated", "supported-by-source"}:
                    errors.append(row["id"] + ": confirmed vulnerability requires established exploitability")
                if not row["locations"]:
                    errors.append(row["id"] + ": confirmed vulnerability requires precise locations")
                if not row["counterevidence"].strip():
                    errors.append(row["id"] + ": confirmed vulnerability requires consideration of defenses")
            if row.get("exploitability") == "demonstrated" and row.get("verification_basis") != "runtime-test":
                errors.append(row["id"] + ": demonstrated exploitability requires runtime test")
            if row["status"] == "refuted" and not row.get("refutation_scope", "").strip():
                errors.append(row["id"] + ": refuted requires bounded refutation_scope")

        if any(cid not in coverage_ids for cid in row["coverage_ids"]): errors.append(row["id"] + ": unknown coverage reference")
        if row["status"] in {"confirmed", "accepted-risk", "fixed"} and not row["evidence"]: errors.append(row["id"] + ": requires evidence")
        required_text = {"suspected": "next_steps", "refuted": "counterevidence", "accepted-risk": "risk_acceptance", "fixed": "fix_verification"}.get(row["status"])
        if required_text and not row[required_text].strip(): errors.append(row["id"] + ": requires " + required_text)
    for row in data.get("tool-runs", []):
        if row["status"] in {"completed", "failed"} and row["exit_code"] is None: errors.append(row["id"] + ": missing exit code")
        if row["status"] in {"failed", "unavailable"} and not row["limitations"]: errors.append(row["id"] + ": requires execution limitation")
    if versions.get("findings") == "1.2":
        try:
            plan = json.loads((directory / "audit-plan.json").read_text(encoding="utf-8"))
            plan_schema = json.loads((SCHEMAS / "audit-plan.schema.json").read_text(encoding="utf-8"))
            problems = schema_errors(plan, plan_schema, "audit-plan")
            errors.extend(problems)
            if not problems:
                threat_ids = {r["id"] for r in plan["threats"]}
                if len(threat_ids) != len(plan["threats"]): errors.append("audit-plan: duplicate threat IDs")
                for threat in plan["threats"]:
                    if not threat["coverage_ids"] or any(ref not in coverage_ids for ref in threat["coverage_ids"]):
                        errors.append(threat["id"] + ": threat needs valid coverage references")
                for finding in data.get("findings", []):
                    if any(ref not in threat_ids for ref in finding.get("threat_ids", [])):
                        errors.append(finding["id"] + ": unknown threat reference")
                    if finding.get("kind") == "security-vulnerability" and not finding.get("threat_ids"):
                        errors.append(finding["id"] + ": vulnerability requires threat reference")
                checks = {r["check"] for r in data.get("coverage", [])}
                if any(domain not in checks for domain in plan["required_domains"]):
                    errors.append("audit-plan: required domain missing from coverage")
                if final and (not plan["threats"] or not plan["required_domains"]):
                    errors.append("audit-plan: final audit needs threats and required domains")
        except (OSError, ValueError) as exc:
            errors.append("audit-plan: cannot load JSON (" + type(exc).__name__ + ")")
    if final:
        if not data.get("coverage"): errors.append("Final audit requires nonempty coverage")
        for name in ("inventory.json", "scope.md", "threat-model.md", "report.md"):
            path = directory / name
            if not path.is_file() or not path.read_text(encoding="utf-8").strip(): errors.append("Missing or empty " + name)
    return errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory")
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()
    errors = validate(args.directory, args.final)
    for error in errors: print(error)
    if not errors: print("Artifact structure valid; factual security claims are not verified.")
    raise SystemExit(1 if errors else 0)

if __name__ == "__main__":
    main()
