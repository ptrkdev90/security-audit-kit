"""Synthetic artifacts shared by contract and export tests; no production data."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/security-audit/skills/software-security-audit'

def load(name):
    import sys
    script_dir = str(SKILL / 'scripts')
    if script_dir not in sys.path: sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location(name, SKILL / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def write(directory, name, value):
    (directory / name).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def complete(directory):
    write(directory, 'inventory.json', {'root': '/synthetic/project', 'git': {'commit': 'a'*40, 'working_tree': ''}, 'limitations': ['Synthetic source-only test']})
    write(directory, 'coverage.json', {'schema_version': '1.0', 'items': [
        {'id': 'C-1', 'component': 'api', 'paths': ['api.py'], 'check': 'object authorization', 'applicability': 'User chooses resource ID', 'status': 'reviewed', 'method': 'source trace', 'evidence': ['api.py:12'], 'limitations': ['Runtime not tested']},
        {'id': 'C-2', 'component': 'deployment', 'paths': ['deployment'], 'check': 'runtime authorization', 'applicability': 'Deployed API', 'status': 'blocked', 'method': 'runtime test', 'evidence': [], 'limitations': ['No runtime access']} ]})
    write(directory, 'audit-plan.json', {'schema_version': '1.0', 'scope_summary': 'Synthetic API and unavailable runtime', 'required_domains': ['object authorization', 'runtime authorization'], 'limitations': ['Synthetic source-only test'], 'threats': [{'id': 'TH-1', 'component': 'api', 'asset': 'orders', 'actor': 'authenticated user', 'entry_point': 'GET /orders/{id}', 'abuse_case': 'Read another owner\u2019s order', 'priority': 'high', 'coverage_ids': ['C-1', 'C-2'], 'flow_ids': []}]})
    write(directory, 'evidence.json', {'schema_version': '1.0', 'items': [{'id': 'E-1', 'type': 'source', 'locator': 'api.py:12', 'snapshot': 'a'*40, 'observed_at': '2026-10-12T20:00:00Z', 'summary': 'Route passes chosen ID to unscoped query', 'limitations': ['Runtime unavailable'], 'sha256': None}]})
    write(directory, "architecture.json", {"schema_version": "1.0", "viewpoint": "Security boundaries", "stakeholders": ["developer", "reviewer"], "concerns": ["Cross-user access"], "boundaries": [{"id": "B_api", "name": "API", "status": "observed", "evidence_ids": ["E-1"], "limitations": ["Runtime unavailable"]}], "components": [{"id": "N_api", "name": "Orders API", "type": "server", "boundary_id": "B_api", "status": "observed", "evidence_ids": ["E-1"], "limitations": ["Runtime unavailable"]}], "flows": [], "limitations": ["Synthetic source-only test"]})
    finding = {'id': 'AUD-1', 'title': 'Missing object authorization', 'status': 'confirmed', 'severity': 'high', 'confidence': 'high', 'component': 'api', 'locations': [{'path': 'api.py', 'line': 12}], 'coverage_ids': ['C-1'], 'prerequisites': 'Authenticated user chooses an existing order ID', 'attack_path': 'Chosen ID reaches an unscoped query and response', 'impact': 'Cross-user disclosure', 'verification': 'Source trace of middleware, handler and query', 'evidence': ['api.py:12'], 'counterevidence': 'Authentication exists; no object check in middleware or query', 'remediation': 'Scope query to authorized owner', 'next_steps': '', 'risk_acceptance': '', 'fix_verification': '', 'kind': 'security-vulnerability', 'verification_basis': 'source-trace', 'exploitability': 'supported-by-source', 'severity_rationale': 'Sensitive cross-user access', 'verification_limits': 'Source-only; deployment unavailable', 'refutation_scope': '', 'evidence_ids': ['E-1'], 'threat_ids': ['TH-1']}
    write(directory, 'findings.json', {'schema_version': '1.2', 'items': [finding]})
    for name in ('scope.md', 'threat-model.md', 'report.md'):
        (directory / name).write_text('# Synthetic audit\n\nSource-only scope; runtime blocked. AUD-1 is supported by source.\n', encoding='utf-8')
    return finding
