#!/usr/bin/env python3
"""Optional neutral PDF export using installed ReportLab. Never installs or signs."""
import argparse
import hashlib
import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from report_model import build
from render_report import sections, theme_from, value


def export_pdf(audit, output, theme_path=None, font_path=None):
    try:
        import reportlab
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.graphics.shapes import Drawing, Rect, String, Line
    except ImportError as exc: raise RuntimeError('ReportLab unavailable; keep HTML/Markdown and record PDF export blocked') from exc
    model=build(audit); theme=theme_from(theme_path); output=Path(output)
    if output.exists(): raise FileExistsError('PDF output exists')
    if model['metadata']['signature']['status']!='unsigned': raise ValueError('Neutral PDF exporter is unsigned only')
    family='DejaVuSerif.ttf' if theme['font_family']=='serif' else 'DejaVuSans.ttf'
    choices=[Path(font_path)] if font_path else [Path('/usr/share/fonts/truetype/dejavu')/family,Path(reportlab.__file__).parent/'fonts/Vera.ttf']
    font_file=next((p for p in choices if p.is_file()),None)
    if font_file is None: raise RuntimeError('Provide an installed font supporting the report language')
    font=TTFont('AuditBody',str(font_file)); pdfmetrics.registerFont(font)
    for character in json.dumps(model,ensure_ascii=False):
        if not character.isspace() and ord(character) not in font.face.charToGlyph:
            raise ValueError('Selected font does not support all report characters')
    styles=getSampleStyleSheet()
    for name in ('Normal','Title','Heading1','Heading2','Heading3','BodyText'):
        styles[name].fontName='AuditBody'
    for heading in ('Heading1','Heading2','Heading3'): styles[heading].keepWithNext=True
    styles['BodyText'].fontSize=9; styles['BodyText'].leading=13; styles['BodyText'].spaceAfter=7
    styles['Title'].fontSize=26; styles['Title'].leading=32; styles['Title'].textColor=colors.HexColor(theme['accent_color'])
    styles['Heading1'].fontSize=17; styles['Heading1'].leading=22; styles['Heading1'].textColor=colors.HexColor(theme['accent_color'])
    label_style=ParagraphStyle('Label',parent=styles['BodyText'],fontSize=9,textColor=colors.HexColor('#475569'),spaceBefore=5,spaceAfter=2)
    story=[]
    def paragraph(data,style='BodyText'):
        # All report/template strings are escaped before ReportLab XML parsing.
        return Paragraph(html.escape(value(data)).replace('\n','<br/>'),styles[style])
    def fields(data):
        if isinstance(data,list):
            for index,row in enumerate(data):
                if isinstance(row,dict) and 'id' in row: story.append(paragraph(row['id'],'Heading3'))
                fields(row)
                story.append(Spacer(1,7))
        elif isinstance(data,dict):
            for key,entry in data.items():
                row=Table([[Paragraph(html.escape(key),label_style),paragraph(entry)]],colWidths=[112,387],hAlign='LEFT',splitInRow=1)
                row.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
                story.append(row)
        else: story.append(paragraph(data))
    content=sections(model)
    story.append(paragraph(model['metadata']['report_title'],'Title'))
    story.append(paragraph(model['metadata']['project_name'],'Heading2'))
    story.append(Spacer(1,16)); fields(content[0][2]); story.append(PageBreak())
    for sid,title,data in content[1:]:
        story.append(paragraph(title,'Heading1'))
        if sid=='counts':
            columns=['kind','suspected','confirmed','refuted','accepted-risk','fixed']
            rows=[[paragraph(c) for c in columns]]+[[paragraph(kind),*[paragraph(counts[k]) for k in columns[1:]]] for kind,counts in data.items()]
            table=Table(rows,colWidths=[160,70,70,60,80,59],repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eef2ff')),('LINEBELOW',(0,0),(-1,-1),.3,colors.HexColor('#cbd5e1'))]))
            story.append(table); story.append(Spacer(1,10))
        else:
            if sid=='threats' and len(model['architecture']['components']) <= 12 and model['architecture']['components']:
                nodes=model['architecture']['components']; drawing=Drawing(450,60*len(nodes)+30)
                positions={n['id']:60*(len(nodes)-i) for i,n in enumerate(nodes)}
                for flow in model['architecture']['flows']:
                    y1=positions[flow['source']];y2=positions[flow['target']]
                    drawing.add(Line(385,y1,425,y1,strokeColor=colors.grey));drawing.add(Line(425,y1,425,y2,strokeColor=colors.grey));drawing.add(Line(425,y2,385,y2,strokeColor=colors.grey))
                for node in nodes:
                    y=positions[node['id']]
                    drawing.add(Rect(0,y-20,385,43,rx=5,ry=5,fillColor=colors.HexColor('#f8fafc'),strokeColor=colors.HexColor('#94a3b8')))
                    drawing.add(String(10,y+5,node['name'][:45],fontName='AuditBody',fontSize=10))
                    drawing.add(String(10,y-10,f'{node["id"]} / {node["boundary_id"]} / {node["status"]}',fontName='AuditBody',fontSize=8))
                story.append(drawing); story.append(paragraph('Diagram labels may be shortened. Complete flows, evidence and uncertainty follow.'))
            fields(data)
    doc=SimpleDocTemplate(str(output),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=48,bottomMargin=48,title=model['metadata']['report_title'],author=model['metadata']['prepared_by']['name'] or '',pageCompression=1)
    def footer(canvas,document):
        canvas.saveState();canvas.setFont('AuditBody',8);canvas.setFillColor(colors.HexColor('#64748b'))
        canvas.drawString(48,25,model['metadata']['report_id'][:65]);canvas.drawRightString(A4[0]-48,25,str(document.page));canvas.restoreState()
    output.parent.mkdir(parents=True,exist_ok=True)
    # Reserve the destination before rendering; cleanup failed exports.
    fd=os.open(output,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(fd)
    try: doc.build(story,onFirstPage=footer,onLaterPages=footer)
    except Exception:
        output.unlink(missing_ok=True);raise
    receipt={'schema_version':'1.0','exported_at':datetime.now(timezone.utc).isoformat(),'renderer':'ReportLab','renderer_version':reportlab.Version,'font_sha256':hashlib.sha256(font_file.read_bytes()).hexdigest(),'theme':theme,'source_sha256':model['source_sha256'],'pdf_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'signature_status':'unsigned','visual_inspection':'not-performed','limitations':['Render all pages and inspect before claiming layout verified.','Custom template skills require their own exporter; neutral PDF does not reproduce DOCX templates.']}
    receipt_path=output.with_suffix('.export.json')
    with receipt_path.open('x',encoding='utf-8') as stream: json.dump(receipt,stream,indent=2);stream.write('\n')
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('audit');parser.add_argument('--output',required=True);parser.add_argument('--theme');parser.add_argument('--font')
    args=parser.parse_args()
    try: print(export_pdf(args.audit,args.output,args.theme,args.font))
    except (OSError,ValueError,RuntimeError,KeyError) as exc: parser.exit(2,'PDF export failed: '+str(exc)+'\n')

if __name__=='__main__':main()
