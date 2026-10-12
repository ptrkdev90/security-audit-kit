#!/usr/bin/env python3
"""Reconcile export hashes and retained claims; never infer visual approval."""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from report_model import build
from render_report import LABELS

class Text(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True);self.parts=[];self.unsafe=[]
    def handle_data(self,data): self.parts.append(data)
    def handle_starttag(self,tag,attrs):
        attributes=dict(attrs)
        if tag in {'script','iframe','object','embed','form','link'}: self.unsafe.append(tag)
        if any(k.startswith('on') or k in {'src','srcset'} for k in attributes): self.unsafe.append(tag+' active attribute')
        if tag=='a' and not attributes.get('href','#').startswith('#'):self.unsafe.append('external link')


def normalize(text): return re.sub(r'\s+','',text)


def required_strings(model):
    rows=[]
    for finding in model['findings']:
        for key in ('id','title','kind','status','severity','confidence','verification','verification_limits','attack_path','impact','counterevidence','remediation','next_steps','risk_acceptance','fix_verification','refutation_scope'):
            if finding[key]: rows.append(finding[key])
    for group in ('coverage','evidence','tool_runs'):
        for row in model[group]:
            rows.append(row['id'])
            rows.extend(row.get('limitations',[]))
    rows.extend(model['narrative']['limitations'])
    rows.extend(LABELS[model['metadata']['language']][key] for key in ('limits','coverage','signoff'))
    return rows


def check(audit,export,with_pdf=False):
    model=build(audit);export=Path(export);errors=[]
    receipt=json.loads((export/'export-receipt.json').read_text(encoding='utf-8'))
    if receipt['source_sha256']!=model['source_sha256']:errors.append('Source changed after export')
    for name in ('report.md','report.html','report-model.json'):
        path=export/name
        if path.is_symlink():errors.append('Symlink export: '+name);continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=receipt['output_sha256'].get(name):errors.append('Output hash mismatch: '+name)
    exported_model=json.loads((export/'report-model.json').read_text())
    if exported_model!=model:errors.append('Exported model differs from canonical audit')
    parser=Text();parser.feed((export/'report.html').read_text(encoding='utf-8'))
    errors.extend(parser.unsafe)
    html_text=normalize(' '.join(parser.parts));md_text=normalize((export/'report.md').read_text(encoding='utf-8'))
    for required in required_strings(model):
        if normalize(required) not in html_text:errors.append('HTML missing claim: '+required[:80])
        if normalize(required) not in md_text:errors.append('Markdown missing claim: '+required[:80])
    if with_pdf:
        try: from pypdf import PdfReader
        except ImportError: raise RuntimeError('pypdf unavailable; PDF text verification blocked')
        pdf=export/'report.pdf';pdf_receipt=json.loads(pdf.with_suffix('.export.json').read_text())
        if pdf_receipt['source_sha256']!=model['source_sha256']:errors.append('PDF source changed')
        if hashlib.sha256(pdf.read_bytes()).hexdigest()!=pdf_receipt['pdf_sha256']:errors.append('PDF hash mismatch')
        reader=PdfReader(pdf); body=[]
        for number,page in enumerate(reader.pages,1):
            def retain_body(text,cm,tm,font,size):
                # Match only this renderer's footer; extractor coordinates can drift
                # for split paragraphs inside translated tables.
                is_footer=size==8 and text.strip() in {model['metadata']['report_id'][:65],str(number)}
                if not is_footer: body.append(text)
            page.extract_text(visitor_text=retain_body)
        text=normalize('\n'.join(body))
        if not reader.pages:errors.append('PDF has no pages')
        for required in required_strings(model):
            if normalize(required) not in text:errors.append('PDF missing claim: '+required[:80])
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('audit');parser.add_argument('export');parser.add_argument('--pdf',action='store_true');args=parser.parse_args()
    try: errors=check(args.audit,args.export,args.pdf)
    except (OSError,ValueError,KeyError,RuntimeError) as exc:parser.exit(2,'Export check blocked: '+str(exc)+'\n')
    for error in errors:print(error)
    if not errors:print('Export content and hashes reconciled. Visual layout and factual claims are not validated.')
    raise SystemExit(bool(errors))

if __name__=='__main__':main()
