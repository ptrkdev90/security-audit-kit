#!/usr/bin/env python3
"""Build a single inspectable report model from validated canonical audit artifacts."""
import hashlib
import json
from pathlib import Path
from validate_audit import validate

SOURCE_FILES = ('inventory.json', 'scope.md', 'threat-model.md', 'audit-plan.json',
                'architecture.json', 'coverage.json', 'findings.json', 'evidence.json',
                'tool-runs.json', 'report-source.json', 'report-metadata.json')


def build(directory):
    directory = Path(directory)
    errors = validate(directory, final=True)
    if errors: raise ValueError('Audit validation failed: ' + '; '.join(errors))
    records = {}
    hashes = {}
    for name in SOURCE_FILES:
        path = directory / name
        if path.is_symlink(): raise ValueError('Report source cannot be a symlink')
        raw = path.read_bytes(); hashes[name] = hashlib.sha256(raw).hexdigest()
        records[name] = json.loads(raw) if name.endswith('.json') else raw.decode('utf-8')
    if records['findings.json']['schema_version'] != '1.2': raise ValueError('Migrate findings manually to 1.2 before export')
    metadata = records['report-metadata.json']
    snapshot = records['inventory.json'].get('git', {})
    if metadata['snapshot']['commit'] != snapshot.get('commit') or metadata['snapshot']['dirty'] != bool(snapshot.get('working_tree')):
        raise ValueError('Report metadata snapshot differs from inventory')
    kinds = ('security-vulnerability', 'dependency-advisory', 'control-gap', 'hardening', 'evidence-gap')
    statuses = ('suspected', 'confirmed', 'refuted', 'accepted-risk', 'fixed')
    counts = {kind: {status: sum(r['kind'] == kind and r['status'] == status for r in records['findings.json']['items']) for status in statuses} for kind in kinds}
    return {'schema_version': '1.0', 'metadata': metadata, 'narrative': records['report-source.json'],
            'architecture': records['architecture.json'], 'plan': records['audit-plan.json'],
            'findings': records['findings.json']['items'], 'coverage': records['coverage.json']['items'],
            'evidence': records['evidence.json']['items'], 'tool_runs': records['tool-runs.json']['items'],
            'counts': counts, 'source_sha256': hashes,
            'limitations': records['inventory.json'].get('limitations', []),
            'scope_document': records['scope.md'], 'threat_document': records['threat-model.md']}
