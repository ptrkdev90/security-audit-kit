#!/usr/bin/env python3
"""Render evidence-backed architecture as Mermaid and offline SVG. No network."""
import argparse
import html
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET


def checked(model):
    ids = [r['id'] for group in ('boundaries', 'components', 'flows') for r in model[group]]
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', i) for i in ids):
        raise ValueError('Architecture IDs must be unique safe identifiers')
    boundaries = {r['id'] for r in model['boundaries']}
    components = {r['id'] for r in model['components']}
    if any(r['boundary_id'] not in boundaries for r in model['components']):
        raise ValueError('Unknown boundary')
    if any(r['source'] not in components or r['target'] not in components for r in model['flows']):
        raise ValueError('Unknown flow endpoint')


def mermaid_label(value):
    # Numeric entities keep quotes/brackets/newlines/directives inside a quoted label.
    return ''.join(c if c.isascii() and (c.isalnum() or c in ' _-.,:/') else f'#{ord(c)};' for c in str(value))


def mermaid(model):
    checked(model)
    rows = ['flowchart TD']
    for boundary in model['boundaries']:
        rows.append(f'    subgraph {boundary["id"]}["{mermaid_label(boundary["name"])} ({boundary["status"]})"]')
        for node in model['components']:
            if node['boundary_id'] == boundary['id']:
                rows.append(f'        {node["id"]}["{mermaid_label(node["name"])} ({node["status"]})"]')
        rows.append('    end')
    for flow in model['flows']:
        arrow = '-->' if flow['status'] == 'observed' else '-.->'
        label = mermaid_label(f'{flow["id"]}: {flow["label"]} ({flow["status"]})')
        rows.append(f'    {flow["source"]} {arrow}|"{label}"| {flow["target"]}')
    return '\n'.join(rows) + '\n'


def svg(model):
    checked(model)
    # Separate lanes avoid crossing labels for modest local views; split large models.
    if len(model['components']) > 20 or len(model['flows']) > 20:
        raise ValueError('Split architecture into views with at most 20 components and flows')
    ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', ns)
    nodes = model['components']; flows = model['flows']
    width = 700 + len(flows) * 34; height = max(180, 100 + len(nodes) * 100)
    root = ET.Element(f'{{{ns}}}svg', {'viewBox': f'0 0 {width} {height}', 'role': 'img', 'aria-labelledby': 'title desc'})
    def add(tag, attrs=None, text=None, parent=None):
        el = ET.SubElement(parent if parent is not None else root, f'{{{ns}}}{tag}', attrs or {})
        if text is not None: el.text = str(text)
        return el
    add('title', {'id': 'title'}, 'Architecture and trust boundaries')
    add('desc', {'id': 'desc'}, 'Observed flows are solid. Inferred or unknown flows are dashed. Evidence and limitations are listed in the accompanying tables.')
    add('rect', {'width': str(width), 'height': str(height), 'fill': '#f8fafc'})
    add('text', {'x': '20', 'y': '28', 'font-size': '17', 'font-family': 'sans-serif', 'fill': '#0f172a'}, 'Trust boundaries · evidence-backed view')
    positions = {n['id']: 90 + i * 100 for i, n in enumerate(nodes)}
    boundaries = {b['id']: b['name'] for b in model['boundaries']}
    for i, flow in enumerate(flows):
        y1 = positions[flow['source']]; y2 = positions[flow['target']]; lane = 570 + i * 34
        attrs = {'d': f'M 500 {y1} H {lane} V {y2} H 505', 'fill': 'none', 'stroke': '#64748b', 'stroke-width': '2'}
        if flow['status'] != 'observed': attrs['stroke-dasharray'] = '5 4'
        add('path', attrs)
        add('path', {'d': f'M 513 {y2-5} L 503 {y2} L 513 {y2+5}', 'fill': 'none', 'stroke': '#64748b'})
        add('text', {'x': str(lane+5), 'y': str(min(y1,y2)+12), 'font-size': '11', 'font-family': 'sans-serif'}, flow['id'])
    for node in nodes:
        y = positions[node['id']]
        add('rect', {'x': '20', 'y': str(y-34), 'width': '480', 'height': '72', 'rx': '8', 'fill': '#fff', 'stroke': '#94a3b8'})
        # Truncate only diagram labels. Complete names/evidence remain in report tables.
        add('text', {'x': '34', 'y': str(y-8), 'font-size': '15', 'font-family': 'sans-serif', 'fill': '#0f172a'}, node['name'][:52])
        add('text', {'x': '34', 'y': str(y+15), 'font-size': '12', 'font-family': 'sans-serif', 'fill': '#475569'}, f'{node["id"]} · {boundaries[node["boundary_id"]][:30]} · {node["status"]}')
    return ET.tostring(root, encoding='unicode')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('architecture'); parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    try:
        model = json.loads(Path(args.architecture).read_text(encoding='utf-8'))
        mmd, graphic = mermaid(model), svg(model)
        output = Path(args.output_dir); output.mkdir(parents=True, exist_ok=True)
        for filename in ('architecture.mmd', 'architecture.svg'):
            if (output / filename).exists(): raise ValueError('Diagram output exists; use a new directory')
        (output / 'architecture.mmd').write_text(mmd, encoding='utf-8')
        (output / 'architecture.svg').write_text(graphic, encoding='utf-8')
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, 'Diagram export failed: ' + type(exc).__name__ + '\n')

if __name__ == '__main__': main()
