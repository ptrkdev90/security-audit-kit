import json
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from support import complete, load, write

class ArchitectureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.audit = load('init_audit').initialize(Path(self.tmp.name) / 'audit'); complete(self.audit)
        self.arch = json.loads((self.audit / 'architecture.json').read_text())
        self.diagram = load('diagrams')

    def test_mermaid_and_svg_escape_hostile_labels(self):
        self.arch['components'][0]['name'] = '<script>alert(1)</script>"\nclick N_api "https://evil"'
        mmd = self.diagram.mermaid(self.arch); graphic = self.diagram.svg(self.arch)
        self.assertNotIn('\nclick', mmd); self.assertNotIn('<script>', graphic)
        ET.fromstring(graphic)
        self.assertIn('#34;', mmd)

    def test_unsafe_identifier_rejected(self):
        self.arch['components'][0]['id'] = 'a\nclick'
        with self.assertRaises(ValueError): self.diagram.mermaid(self.arch)

    def test_observed_component_requires_evidence(self):
        self.arch['components'][0]['evidence_ids'] = []
        write(self.audit, 'architecture.json', self.arch)
        self.assertTrue(any('requires evidence' in x for x in load('validate_audit').validate(self.audit)))

    def test_uncertain_boundary_requires_limitations(self):
        self.arch['boundaries'][0].update(status='unknown', evidence_ids=[], limitations=[])
        write(self.audit, 'architecture.json', self.arch)
        self.assertTrue(any('requires limitations' in x for x in load('validate_audit').validate(self.audit)))

    def test_flow_endpoint_must_exist(self):
        self.arch['flows'] = [{'id': 'F1', 'source': 'missing', 'target': 'N_api', 'label': 'read', 'protocol': 'HTTPS', 'data': ['order'], 'authentication': 'unknown', 'authorization': 'unknown', 'failure_behavior': 'unknown', 'status': 'unknown', 'evidence_ids': [], 'limitations': ['No runtime']}]
        write(self.audit, 'architecture.json', self.arch)
        self.assertTrue(any('endpoint' in x for x in load('validate_audit').validate(self.audit)))
        with self.assertRaises(ValueError): self.diagram.svg(self.arch)

    def test_unknown_attack_flow_is_rejected(self):
        plan = {'threats': [{'id': 'TH1', 'flow_ids': ['missing']}]}
        with self.assertRaises(ValueError): self.diagram.attack_views(self.arch, plan)

    def test_source_hypothesis_does_not_invent_diagram_flow(self):
        self.assertEqual(self.diagram.attack_views(self.arch, {'threats': [{'id': 'TH1', 'flow_ids': []}]}), {})
