import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from support import complete,load,write

@unittest.skipUnless(importlib.util.find_spec('reportlab') and importlib.util.find_spec('pypdf'),'Optional PDF packages unavailable')
class PdfTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.audit=load('init_audit').initialize(self.base/'audit');complete(self.audit)
        self.export=load('render_report').render(self.audit,self.base/'export');self.pdf=load('pdf_report')

    def test_pdf_reconciles_and_is_not_marked_visually_checked(self):
        path=self.pdf.export_pdf(self.audit,self.export/'report.pdf')
        self.assertEqual(load('check_exports').check(self.audit,self.export,True),[])
        receipt=json.loads(path.with_suffix('.export.json').read_text())
        self.assertEqual(receipt['visual_inspection'],'not-performed')
        self.assertEqual(receipt['signature_status'],'unsigned')

    def test_overwrite_rejected(self):
        self.pdf.export_pdf(self.audit,self.export/'report.pdf')
        with self.assertRaises(FileExistsError):self.pdf.export_pdf(self.audit,self.export/'report.pdf')

    def test_long_hostile_text_and_german_survive_pdf(self):
        metadata=json.loads((self.audit/'report-metadata.json').read_text());metadata.update(language='de',display_timezone='Europe/Berlin');write(self.audit,'report-metadata.json',metadata)
        findings=json.loads((self.audit/'findings.json').read_text());findings['items'][0]['impact']='Änderung: <script>kein Code</script> '+('LangerNachweispfad/'*50);write(self.audit,'findings.json',findings)
        other=load('render_report').render(self.audit,self.base/'german');self.pdf.export_pdf(self.audit,other/'report.pdf')
        self.assertEqual(load('check_exports').check(self.audit,other,True),[])
