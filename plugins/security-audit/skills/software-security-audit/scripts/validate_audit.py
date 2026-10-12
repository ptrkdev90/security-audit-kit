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
    architecture_flows = set()
    if (directory / "architecture.json").exists():
        try:
            architecture = json.loads((directory / "architecture.json").read_text(encoding="utf-8"))
            arch_schema = json.loads((SCHEMAS / "architecture.schema.json").read_text(encoding="utf-8"))
            problems = schema_errors(architecture, arch_schema, "architecture")
            errors.extend(problems)
            if not problems:
                import re
                groups = {name: {r["id"] for r in architecture[name]} for name in ("boundaries", "components", "flows")}
                architecture_flows = groups["flows"]
                ids = [row["id"] for group in groups for row in architecture[group]]
                if len(ids) != len(set(ids)): errors.append("architecture: duplicate IDs")
                for group in groups:
                    for row in architecture[group]:
                        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", row["id"]):
                            errors.append("architecture: unsafe ID")
                        if any(ref not in evidence for ref in row["evidence_ids"]):
                            errors.append(row["id"] + ": unknown architecture evidence")
                        if row["status"] == "observed" and not row["evidence_ids"]:
                            errors.append(row["id"] + ": observed architecture requires evidence")
                        if row["status"] != "observed" and not row["limitations"]:
                            errors.append(row["id"] + ": uncertain architecture requires limitations")
                for row in architecture["components"]:
                    if row["boundary_id"] not in groups["boundaries"]:
                        errors.append(row["id"] + ": unknown trust boundary")
                for row in architecture["flows"]:
                    if row["source"] not in groups["components"] or row["target"] not in groups["components"]:
                        errors.append(row["id"] + ": unknown flow endpoint")
                if final and versions.get("findings") == "1.2" and (not architecture["components"] or not architecture["stakeholders"] or not architecture["concerns"]):
                    errors.append("architecture: final audit requires components, stakeholders and concerns")
        except (OSError, ValueError) as exc:
            errors.append("architecture: cannot load JSON (" + type(exc).__name__ + ")")
    elif versions.get("findings") == "1.2":
        errors.append("architecture: missing architecture.json")
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
                    if any(ref not in architecture_flows for ref in threat["flow_ids"]):
                        errors.append(threat["id"] + ": unknown threat flow reference")
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
    if versions.get("findings") == "1.2":
        for record in ("report-source", "report-metadata"):
            try:
                value = json.loads((directory / (record + ".json")).read_text(encoding="utf-8"))
                schema = json.loads((SCHEMAS / (record + ".schema.json")).read_text(encoding="utf-8"))
                problems = schema_errors(value, schema, record)
                errors.extend(problems)
                if not problems and final:
                    if record == "report-source":
                        if any("Replace with" in str(v) for v in value.values()):
                            errors.append("report-source: unresolved starter text")
                    else:
                        from datetime import datetime
                        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
                        try: ZoneInfo(value["display_timezone"])
                        except ZoneInfoNotFoundError: errors.append("report-metadata: unknown timezone")
                        dates = {}
                        for key in ("audit_started_at", "audit_ended_at", "generated_at"):
                            try:
                                dates[key] = datetime.fromisoformat((value[key] or "").replace("Z", "+00:00"))
                                if dates[key].tzinfo is None: raise ValueError()
                            except (ValueError, TypeError): errors.append("report-metadata: requires timestamp " + key)
                        if len(dates) == 3 and all(v.tzinfo is not None for v in dates.values()) and not (dates["audit_started_at"] <= dates["audit_ended_at"] <= dates["generated_at"]):
                            errors.append("report-metadata: invalid audit timestamp order")
                        if not value["report_id"] or not value["project_name"]:
                            errors.append("report-metadata: report ID and project required")
                        for key, date_key in (("reviewed_by", "reviewed_at"), ("approved_by", "approved_at")):
                            signoff = value[key]
                            if signoff["name"] or signoff[date_key]:
                                if not signoff["name"] or not signoff[date_key] or not signoff["evidence_ids"]:
                                    errors.append("report-metadata: sign-off requires identity, date and evidence")
                            if any(ref not in evidence for ref in signoff["evidence_ids"]): errors.append("report-metadata: unknown sign-off evidence")
                        signature = value["signature"]
                        if signature["status"] == "unsigned":
                            if signature["type"] != "none" or any(signature[k] is not None for k in ("signer", "signed_at", "verification_result")) or signature["evidence_ids"]:
                                errors.append("report-metadata: unsigned state contradicts signature fields")
                        elif not signature["signer"] or not signature["signed_at"] or not signature["evidence_ids"]:
                            errors.append("report-metadata: signature requires authorized evidence")
                        if any(ref not in evidence for ref in signature["evidence_ids"]): errors.append("report-metadata: unknown signature evidence")
            except (OSError, ValueError) as exc:
                errors.append(record + ": cannot load JSON (" + type(exc).__name__ + ")")
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
