import json
import tempfile
import unittest
from pathlib import Path
from support import load, complete, write

class ReportModelTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.audit = load('init_audit').initialize(Path(self.tmp.name) / 'audit'); complete(self.audit)
        self.model = load('report_model')

    def test_model_separates_kinds_and_keeps_blocker(self):
        result = self.model.build(self.audit)
        self.assertEqual(result['counts']['security-vulnerability']['confirmed'], 1)
        self.assertEqual(result['counts']['dependency-advisory']['confirmed'], 0)
        self.assertEqual(result['coverage'][1]['status'], 'blocked')
        self.assertEqual(result['metadata']['signature']['status'], 'unsigned')

    def test_incomplete_narrative_rejected(self):
        value = json.loads((self.audit/'report-source.json').read_text()); value['scope_summary']='Replace with scope'
        write(self.audit,'report-source.json',value)
        with self.assertRaises(ValueError): self.model.build(self.audit)

    def test_false_signature_rejected(self):
        value = json.loads((self.audit/'report-metadata.json').read_text()); value['signature']['status']='digitally-signed'
        write(self.audit,'report-metadata.json',value)
        with self.assertRaises(ValueError): self.model.build(self.audit)

    def test_snapshot_mismatch_rejected(self):
        value = json.loads((self.audit/'report-metadata.json').read_text()); value['snapshot']['commit']='other'
        write(self.audit,'report-metadata.json',value)
        with self.assertRaises(ValueError): self.model.build(self.audit)

    def test_false_review_rejected(self):
        value = json.loads((self.audit/'report-metadata.json').read_text()); value['reviewed_by']['name']='Invented'
        write(self.audit,'report-metadata.json',value)
        with self.assertRaises(ValueError): self.model.build(self.audit)
