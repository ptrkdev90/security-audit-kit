"""Run packaged CLIs as users invoke them, including failure paths."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from support import SKILL,complete,load,write

class EndToEndTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)

    def run_cli(self,name,*args,expected=0):
        result=subprocess.run([sys.executable,str(SKILL/'scripts'/name),*map(str,args)],capture_output=True,text=True,timeout=40)
        self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
        return result

    def test_packaged_pipeline_with_spaces(self):
        audit=self.base/'audit with spaces'
        self.run_cli('init_audit.py','--output',audit);complete(audit)
        self.run_cli('validate_audit.py',audit,'--final')
        self.run_cli('diagrams.py',audit/'architecture.json','--plan',audit/'audit-plan.json','--output-dir',audit/'diagrams')
        export=audit/'export';self.run_cli('render_report.py',audit,'--output',export)
        self.run_cli('check_exports.py',audit,export)
        if importlib.util.find_spec('reportlab') and importlib.util.find_spec('pypdf'):
            self.run_cli('pdf_report.py',audit,'--output',export/'report.pdf')
            self.run_cli('check_exports.py',audit,export,'--pdf')

    def test_incomplete_audit_cannot_export(self):
        audit=self.base/'audit';self.run_cli('init_audit.py','--output',audit)
        self.run_cli('render_report.py',audit,'--output',self.base/'export',expected=2)
        self.assertFalse((self.base/'export').exists())

    def test_duplicate_init_cannot_overwrite(self):
        audit=self.base/'audit';self.run_cli('init_audit.py','--output',audit)
        (audit/'report.md').write_text('Keep this')
        self.run_cli('init_audit.py','--output',audit,expected=2)
        self.assertEqual((audit/'report.md').read_text(),'Keep this')

    def test_checkpoint_cli_reports_changes(self):
        target=self.base/'target';target.mkdir();(target/'app.py').write_text('v1')
        write(self.base,'allowlist.json',['app.py']);write(self.base,'context.json',{'scope':'source'})
        args=['--root',target,'--allowlist',self.base/'allowlist.json','--context',self.base/'context.json']
        self.run_cli('checkpoint.py',*args,'--output',self.base/'start.json')
        (target/'app.py').write_text('v2')
        self.run_cli('checkpoint.py',*args,'--previous',self.base/'start.json','--output',self.base/'resume.json')
        result=json.loads((self.base/'resume.json').read_text())
        self.assertEqual(result['resume']['reuse_decision'],'invalidated')

    def test_documentation_claim_without_evidence_rejected(self):
        audit=load('init_audit').initialize(self.base/'audit');complete(audit)
        write(audit,'documentation-profile.json',{'schema_version':'1.0','items':[{'standard':'ISO example','edition':'example','source_url':'https://example.invalid','verified_at':'2026-10-12','full_text_reviewed':True,'applicability':'reference-only','rationale':'Synthetic example','evidence_ids':[]}]})
        result=self.run_cli('validate_audit.py',audit,'--final',expected=1)
        self.assertIn('full-text review requires evidence',result.stdout)
