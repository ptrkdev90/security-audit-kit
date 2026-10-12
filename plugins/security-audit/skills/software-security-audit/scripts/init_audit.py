#!/usr/bin/env python3
"""Create audit bookkeeping in a NEW directory. No target execution."""
import argparse
import json
from pathlib import Path

def initialize(output):
    output = Path(output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    templates = Path(__file__).resolve().parents[1] / "assets" / "templates"
    for name in ("scope.md", "threat-model.md", "report.md", "checkpoint.md", "architecture.json"):
        (output / name).write_text((templates / name).read_text(encoding="utf-8"), encoding="utf-8")
    for name in ("coverage", "findings", "tool-runs", "evidence"):
        (output / (name + ".json")).write_text(json.dumps({"schema_version": "1.2" if name == "findings" else "1.0", "items": []}, indent=2) + "\n", encoding="utf-8")
    (output / "audit-plan.json").write_text(json.dumps({"schema_version": "1.0", "scope_summary": "Establish scope before review", "threats": [], "required_domains": [], "limitations": []}, indent=2) + "\n", encoding="utf-8")
    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        print(initialize(args.output))
    except (OSError, ValueError) as exc:
        parser.exit(2, "Cannot create new audit directory: " + str(exc) + "\n")

if __name__ == "__main__":
    main()
