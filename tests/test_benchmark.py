import importlib.util
import unittest
from support import ROOT
spec = importlib.util.spec_from_file_location('benchmark', ROOT / 'scripts/benchmark_context.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

class BenchmarkTest(unittest.TestCase):
    def sample(self, variant):
        return {'case':'api', 'model':'same', 'prompt_sha256':'same-prompt', 'environment_sha256':'same-environment', 'trial':1, 'variant':variant, 'input_tokens':1000, 'output_tokens':200, 'missed_high_impact':0, 'false_positives':0, 'expected_checks':10, 'reviewed_checks':10}

    def test_entry_size_reduced_without_claiming_tokens(self):
        result = module.context_metrics()
        self.assertGreater(result['entry_character_reduction_percent'], 0)
        self.assertIn('not actual token', result['limits'][0])

    def test_token_saving_does_not_hide_quality_regression(self):
        a = self.sample('baseline'); b = self.sample('candidate'); b.update(input_tokens=500, missed_high_impact=1)
        result = module.paired_measurements([a,b])
        self.assertTrue(result['quality_regression']); self.assertGreater(result['mean_pair_reduction_percent'],0)

    def test_unpaired_measurement_rejected(self):
        with self.assertRaises(ValueError): module.paired_measurements([self.sample('baseline')])

    def test_different_models_cannot_be_paired(self):
        a = self.sample('baseline'); b = self.sample('candidate'); b['model']='other'
        with self.assertRaises(ValueError): module.paired_measurements([a,b])

    def test_boolean_token_count_rejected(self):
        a = self.sample('baseline'); a['input_tokens']=True
        with self.assertRaises(ValueError): module.paired_measurements([a,self.sample('candidate')])
