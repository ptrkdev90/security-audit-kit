#!/usr/bin/env python3
"""Export matching Markdown, static offline HTML and JSON from a validated audit."""
import argparse
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from report_model import build
from diagrams import svg

LABELS = {
 'en': {'outcome':'Executive outcome','scope':'Scope and snapshot','threats':'Architecture and threats','findings':'Findings and observations','coverage':'Coverage and blockers','tools':'Tool execution','evidence':'Evidence register','limits':'Limitations','remediation':'Remediation and retest','compliance':'Compliance readiness','signoff':'Review and sign-off','counts':'Counts by kind and status','not_provided':'Not provided','unsigned':'Unsigned'},
 'de': {'outcome':'Ergebnis und Entscheidungen','scope':'Umfang und geprüfter Stand','threats':'Architektur und Bedrohungen','findings':'Befunde und Beobachtungen','coverage':'Prüfabdeckung und blockierte Prüfungen','tools':'Werkzeugläufe','evidence':'Nachweisregister','limits':'Einschränkungen','remediation':'Behebung und erneute Prüfung','compliance':'Compliance-Readiness','signoff':'Review und Freigabe','counts':'Anzahl nach Befundart und Status','not_provided':'Nicht angegeben','unsigned':'Nicht unterzeichnet'}
}
DEFAULT_THEME = {'schema_version':'1.0','name':'Neutral','version':'1.0','accent_color':'#2563eb','font_family':'sans-serif'}


def theme_from(path=None):
    theme = json.loads(Path(path).read_text(encoding='utf-8')) if path else dict(DEFAULT_THEME)
    import re
    if set(theme) != set(DEFAULT_THEME) or theme['schema_version'] != '1.0' or not isinstance(theme['name'],str) or not isinstance(theme['version'],str): raise ValueError('Invalid theme contract')
    if not isinstance(theme['accent_color'], str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', theme['accent_color']): raise ValueError('Invalid theme color')
    if theme['font_family'] not in {'sans-serif','serif'}: raise ValueError('Invalid theme font')
    return theme


def value(data):
    if data is None: return 'Not provided'
    if isinstance(data, dict): return '\n'.join(str(k) + ': ' + value(v) for k,v in data.items())
    if isinstance(data, list): return '\n'.join('- ' + value(v) for v in data) or '—'
    if isinstance(data, bool): return 'true' if data else 'false'
    return str(data)


def sections(model):
    meta, narrative = model['metadata'], model['narrative']
    dates = {}
    for key in ('audit_started_at','audit_ended_at','generated_at'):
        dates[key] = datetime.fromisoformat(meta[key].replace('Z','+00:00')).astimezone(ZoneInfo(meta['display_timezone'])).isoformat() + ' [' + meta['display_timezone'] + ']'
    cover = {'project':meta['project_name'],'report_id':meta['report_id'],'report_version':meta['report_version'],'report_status':meta['report_status'],'snapshot':meta['snapshot'],**dates,'prepared_by':meta['prepared_by'],'confidentiality':meta['confidentiality'],'signature_status':meta['signature']['status']}
    return [('cover',meta['report_title'],cover),
            ('outcome',LABELS[meta['language']]['outcome'],narrative['executive_outcome']),
            ('counts',LABELS[meta['language']]['counts'],model['counts']),
            ('limits',LABELS[meta['language']]['limits'],{'report':narrative['limitations'],'inventory':model['limitations'],'architecture':model['architecture']['limitations'],'plan':model['plan']['limitations'],'blocked_checks':[{'id':r['id'],'check':r['check'],'limitations':r['limitations']} for r in model['coverage'] if r['status']=='blocked']}),
            ('scope',LABELS[meta['language']]['scope'],{'audience':narrative.get('audience',[]),'glossary':narrative.get('glossary',[]),'summary':narrative['scope_summary'],'snapshot':meta['snapshot'],'scope_document':model['scope_document']}),
            ('threats',LABELS[meta['language']]['threats'],{'summary':narrative['threat_summary'],'architecture':model['architecture'],'threats':model['plan']['threats'],'threat_document':model['threat_document']}),
            ('findings',LABELS[meta['language']]['findings'],model['findings']),
            ('coverage',LABELS[meta['language']]['coverage'],model['coverage']),
            ('tools',LABELS[meta['language']]['tools'],model['tool_runs']),
            ('evidence',LABELS[meta['language']]['evidence'],model['evidence']),
            ('remediation',LABELS[meta['language']]['remediation'],narrative['remediation_summary']),
            ('compliance',LABELS[meta['language']]['compliance'],{'summary':narrative['compliance_summary'],'matrix':model.get('compliance_matrix'),'documentation_profile':model.get('documentation_profile')}),
            ('signoff',LABELS[meta['language']]['signoff'],{'prepared_by':meta['prepared_by'],'reviewed_by':meta['reviewed_by'],'approved_by':meta['approved_by'],'signature':meta['signature'],'full_metadata':meta})]


def markdown(model):
    # Code fences escape even adversarial Markdown/HTML without creating active links.
    out = []
    for _, title, data in sections(model):
        safe_title = __import__('re').sub(r'([\\`*_{}\[\]()#+.!|>])', r'\\\1', html.escape(title.replace('\n',' ')))
        out.extend(['## ' + safe_title, ''])
        content = value(data)
        longest = max((len(run) for run in __import__('re').findall(r'`+',content)),default=0)
        fence = '`' * max(3,longest+1)
        out.extend([fence+'text',content,fence,''])
    return '\n'.join(out)


def html_report(model, theme=None):
    theme = theme or dict(DEFAULT_THEME); lang = model['metadata']['language']
    esc = lambda x: html.escape(str(x), quote=True)
    def details(data):
        if isinstance(data, dict):
            return '<dl>' + ''.join('<dt>'+esc(k)+'</dt><dd><pre>'+esc(value(v))+'</pre></dd>' for k,v in data.items()) + '</dl>'
        if isinstance(data,list):
            return ''.join('<article>'+details(item)+'</article>' for item in data) or '<p>—</p>'
        return '<p class="prose">'+esc(value(data))+'</p>'
    contents = sections(model)
    nav = '<nav aria-label="Contents"><ul>'+''.join(f'<li><a href="#{sid}">{esc(title)}</a></li>' for sid,title,_ in contents[1:])+'</ul></nav>'
    blocks = []
    for sid,title,data in contents:
        extra = ''
        if sid == 'threats':
            try: extra = '<figure>'+svg(model['architecture'])+'<figcaption>'+esc('Observed flows are solid; uncertain flows are dashed. Full evidence and limitations follow.')+'</figcaption></figure>'
            except ValueError: extra = '<p>Diagram omitted: split large architecture into smaller views. Complete model follows.</p>'
        content = details(data)
        if sid == 'counts':
            statuses = ['suspected','confirmed','refuted','accepted-risk','fixed']
            content = '<table><thead><tr><th>Kind</th>'+''.join('<th>'+esc(k)+'</th>' for k in statuses)+'</tr></thead><tbody>'+''.join('<tr><th>'+esc(kind)+'</th>'+''.join('<td>'+str(counts[k])+'</td>' for k in statuses)+'</tr>' for kind,counts in data.items())+'</tbody></table>'
        heading = 'h1' if sid == 'cover' else 'h2'
        blocks.append(f'<section id="{sid}"><{heading}>{esc(title)}</{heading}>{extra}{content}</section>')
    css = f'''@page {{ size: A4; margin: 18mm; @bottom-center {{content: counter(page) " / " counter(pages); font-size: 9pt;}} }}
:root {{ --accent: {theme['accent_color']}; }}
* {{box-sizing:border-box}} body {{margin:0;background:#e2e8f0;color:#172033;font:15px/1.55 {theme['font_family']};}}
main {{max-width:1000px;margin:32px auto;background:#fff;padding:48px;}}
h1 {{font-size:34px;line-height:1.2}} h2 {{font-size:24px;color:var(--accent);border-bottom:1px solid #cbd5e1;padding-bottom:8px;}}
section {{margin:32px 0;scroll-margin-top:20px}} #cover {{border-top:8px solid var(--accent);padding-top:16px;}}
nav ul {{display:flex;flex-wrap:wrap;gap:8px 24px;padding-left:20px}} a {{color:var(--accent)}}
dl {{display:grid;grid-template-columns:190px minmax(0,1fr);gap:8px 20px;}} dt {{font-weight:bold;overflow-wrap:anywhere}} dd {{margin:0;min-width:0;}}
pre,.prose {{white-space:pre-wrap;overflow-wrap:anywhere;word-break:normal;margin:0;font:inherit;}}
table {{border-collapse:collapse;width:100%;font-size:13px}} th,td {{text-align:left;padding:6px;border-bottom:1px solid #cbd5e1;overflow-wrap:anywhere}}
article {{border:1px solid #cbd5e1;border-left:4px solid var(--accent);padding:20px;margin:16px 0;}}
svg {{width:100%;height:auto}} figure {{margin:20px 0}} figcaption {{font-size:13px;color:#475569}}
@media(max-width:700px) {{main {{margin:0;padding:20px}} dl {{grid-template-columns:1fr}} dt {{margin-top:12px}}}}
@media print {{body {{background:white;font-size:10pt}} main {{max-width:none;margin:0;padding:0}} nav {{display:none}} #cover {{break-after:page}} h1,h2,dt {{break-after:avoid}} article {{break-inside:auto}} section {{margin:18px 0}} dl {{grid-template-columns:145px minmax(0,1fr)}} }}'''
    return '<!doctype html><html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;; img-src data:; base-uri &#39;none&#39;; form-action &#39;none&#39;"><title>'+esc(model['metadata']['report_title'])+'</title><style>'+css+'</style></head><body><main>'+blocks[0]+nav+''.join(blocks[1:])+'</main></body></html>'


def render(directory, output, theme_path=None):
    model = build(directory); theme = theme_from(theme_path)
    if model['metadata']['signature']['status'] != 'unsigned': raise ValueError('Neutral exporter is unsigned only; use a separately authorized signing workflow')
    md, document = markdown(model), html_report(model, theme)
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    for name, content in [('report.md',md),('report.html',document),('report-model.json',json.dumps(model,indent=2,ensure_ascii=False)+'\n')]:
        (output / name).write_text(content,encoding='utf-8')
    receipt = {'schema_version':'1.0','exported_at':datetime.now(timezone.utc).isoformat(),'theme':theme,'signature_status':'unsigned','exporter_plugin_version':json.loads((Path(__file__).resolve().parents[3]/'.claude-plugin/plugin.json').read_text())['version'],'schema_versions':model['schema_versions'],'source_sha256':model['source_sha256'],
               'output_sha256':{name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in ('report.md','report.html','report-model.json')},
               'checks':['Shared canonical model used for all outputs','Text escaped; no JavaScript, remote resources or template code'],
               'limitations':['No PDF or visual inspection performed by HTML renderer','Custom template skill/DOCX fidelity requires its own export workflow']}
    (output/'export-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('audit'); parser.add_argument('--output',required=True); parser.add_argument('--theme')
    args = parser.parse_args()
    try: print(render(args.audit,args.output,args.theme))
    except (OSError,ValueError,KeyError,TypeError) as exc: parser.exit(2,'Report export failed: '+str(exc)+'\n')

if __name__=='__main__': main()
