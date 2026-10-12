#!/usr/bin/env python3
"""Check packaging and local links without network or third-party dependencies."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    manifest = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert manifest["name"] == "security-audit-kit" and manifest["owner"]["name"]
    for plugin in manifest["plugins"]:
        path = ROOT / plugin["source"]
        assert path.resolve().is_relative_to(ROOT.resolve())
        local = json.loads((path / ".claude-plugin/plugin.json").read_text())
        assert local["name"] == plugin["name"] and local["version"] == plugin["version"]
    skill = ROOT / "plugins/security-audit/skills/software-security-audit"
    text = (skill / "SKILL.md").read_text()
    assert text.startswith("---\nname: software-security-audit\ndescription:")
    assert len(text.splitlines()) < 500 and "TODO" not in text
    for relative in re.findall(r"\]\(([^)]+)\)", text):
        assert (skill / relative).is_file(), relative
    for path in (skill / "assets/schemas").glob("*.json"):
        json.loads(path.read_text())
    print("Repository manifests, skill frontmatter and resource links valid.")

if __name__ == "__main__":
    main()
