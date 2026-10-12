import json
import tempfile
import unittest
from pathlib import Path
from support import complete,load,write

class MigrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
        self.audit=load('init_audit').initialize(self.base/'old');complete(self.audit)
        names=load('migrate_audit').REPLACEMENTS
        self.review={name:json.loads((self.audit/file).read_text()) for name,file in names.items()}
        self.review.update(reviewed_by='Synthetic reviewer',reason='Manually re-evaluated fixture findings')
        self.review['report-metadata']['report_version']='1.1'
        legacy=json.loads((self.audit/'findings.json').read_text());legacy['schema_version']='1.1'
        for item in legacy['items']:item.pop('evidence_ids');item.pop('threat_ids')
        write(self.audit,'findings.json',legacy)
        self.module=load('migrate_audit')

    def test_manual_migration_preserves_source_and_identity(self):
        original=(self.audit/'findings.json').read_bytes()
        output=self.module.migrate(self.audit,self.base/'new',self.review)
        self.assertEqual((self.audit/'findings.json').read_bytes(),original)
        self.assertEqual((output/'previous-version/findings.json').read_bytes(),original)
        self.assertEqual(load('validate_audit').validate(output,True),[])

    def test_no_silent_decisions(self):
        del self.review['evidence']
        with self.assertRaises(ValueError):self.module.migrate(self.audit,self.base/'new',self.review)

    def test_migration_cannot_drop_findings(self):
        self.review['findings']['items']=[]
        with self.assertRaises(ValueError):self.module.migrate(self.audit,self.base/'new',self.review)

    def test_report_version_must_change(self):
        self.review['report-metadata']['report_version']='1.0'
        with self.assertRaises(ValueError):self.module.migrate(self.audit,self.base/'new',self.review)

    def test_old_signature_does_not_carry_forward(self):
        self.review['report-metadata']['signature']['status']='digitally-signed'
        with self.assertRaises(ValueError):self.module.migrate(self.audit,self.base/'new',self.review)

    def test_nested_output_rejected(self):
        with self.assertRaises(ValueError):self.module.migrate(self.audit,self.audit/'new',self.review)
