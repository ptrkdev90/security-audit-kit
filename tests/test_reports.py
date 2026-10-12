import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from support import complete, load, write

class Tags(HTMLParser):
    def __init__(self): super().__init__(); self.tags=[]; self.text=[]
    def handle_starttag(self,tag,attrs): self.tags.append((tag,dict(attrs)))
    def handle_data(self,data): self.text.append(data)

class ReportsTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name); self.audit=load('init_audit').initialize(self.base/'audit'); complete(self.audit)
        self.renderer=load('render_report')

    def test_html_preserves_all_finding_fields_and_gaps(self):
        out=self.renderer.render(self.audit,self.base/'export'); document=(out/'report.html').read_text()
        for text in ['AUD-1','C-2','No runtime access','Source-only; no runtime access','unsigned','verification_limits','counterevidence']:
            self.assertIn(text,document)
        parser=Tags(); parser.feed(document)
        self.assertFalse(any(tag=='script' for tag,_ in parser.tags))
        self.assertFalse(any('src' in attrs for _,attrs in parser.tags))
        self.assertEqual(json.loads((out/'report-model.json').read_text())['counts']['security-vulnerability']['confirmed'],1)

    def test_hostile_text_escaped(self):
        data=json.loads((self.audit/'report-source.json').read_text()); data['executive_outcome']='<script>alert(1)</script><img src="https://evil">'
        write(self.audit,'report-source.json',data)
        out=self.renderer.render(self.audit,self.base/'export'); document=(out/'report.html').read_text()
        self.assertNotIn('<script>',document); self.assertNotIn('<img src=',document)
        self.assertIn('&lt;script&gt;',document)

    def test_output_is_not_overwritten(self):
        self.renderer.render(self.audit,self.base/'export')
        with self.assertRaises(FileExistsError): self.renderer.render(self.audit,self.base/'export')

    def test_malicious_theme_rejected(self):
        theme=dict(self.renderer.DEFAULT_THEME,accent_color='red; background:url(https://evil)')
        write(self.base,'theme.json',theme)
        with self.assertRaises(ValueError): self.renderer.render(self.audit,self.base/'export',self.base/'theme.json')

    def test_german_headings_and_explicit_timezone(self):
        data=json.loads((self.audit/'report-metadata.json').read_text()); data.update(language='de',display_timezone='Europe/Berlin'); write(self.audit,'report-metadata.json',data)
        out=self.renderer.render(self.audit,self.base/'export'); document=(out/'report.html').read_text()
        self.assertIn('Prüfabdeckung',document); self.assertIn('Europe/Berlin',document)
