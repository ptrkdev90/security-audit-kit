import json
import tempfile
import unittest
from pathlib import Path
from support import load, complete, write

class EvidenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.audit = load('init_audit').initialize(Path(self.tmp.name) / 'audit')
        self.finding = complete(self.audit)
        self.validate = load('validate_audit').validate

    def mutate(self, name, update):
        data = json.loads((self.audit / name).read_text()); update(data); write(self.audit, name, data)

    def test_complete_source_audit_retains_runtime_gap(self):
        self.assertEqual(self.validate(self.audit, True), [])

    def test_scanner_evidence_cannot_support_source_confirmation(self):
        self.mutate('evidence.json', lambda d: d['items'][0].update(type='scanner'))
        self.assertTrue(any('matching evidence' in e for e in self.validate(self.audit)))

    def test_unknown_evidence(self):
        self.mutate('findings.json', lambda d: d['items'][0].update(evidence_ids=['absent']))
        self.assertTrue(any('unknown evidence' in e for e in self.validate(self.audit)))

    def test_duplicate_evidence(self):
        self.mutate('evidence.json', lambda d: d['items'].append(d['items'][0]))
        self.assertTrue(any('duplicate' in e for e in self.validate(self.audit)))

    def test_timestamp_requires_timezone(self):
        self.mutate('evidence.json', lambda d: d['items'][0].update(observed_at='2026-10-12T20:00:00'))
        self.assertTrue(any('timestamp' in e for e in self.validate(self.audit)))

    def test_hash_rejects_arbitrary_text(self):
        self.mutate('evidence.json', lambda d: d['items'][0].update(sha256='fake'))
        self.assertTrue(any('sha256' in e for e in self.validate(self.audit)))

    def test_unknown_threat(self):
        self.mutate('findings.json', lambda d: d['items'][0].update(threat_ids=['unknown']))
        self.assertTrue(any('unknown threat' in e for e in self.validate(self.audit)))

    def test_uncovered_domain(self):
        self.mutate('audit-plan.json', lambda d: d['required_domains'].append('tenant isolation'))
        self.assertTrue(any('domain missing' in e for e in self.validate(self.audit)))

    def test_unmapped_threat(self):
        self.mutate('audit-plan.json', lambda d: d['threats'][0].update(coverage_ids=[]))
        self.assertTrue(any('coverage references' in e for e in self.validate(self.audit)))

    def test_no_plan_cannot_finalize(self):
        (self.audit / 'audit-plan.json').unlink()
        self.assertTrue(any('audit-plan' in e for e in self.validate(self.audit, True)))
