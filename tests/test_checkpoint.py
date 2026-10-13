import tempfile
import unittest
from pathlib import Path
from support import load

class CheckpointTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); (self.root / 'api.py').write_text('source')
        self.module = load('checkpoint'); self.context = {'scope': 'source', 'tool': 'v1', 'deployment': 'unknown'}

    def snapshot(self): return self.module.capture(self.root, ['api.py'], self.context)

    def test_unchanged_needs_manual_review(self):
        before = self.snapshot(); result = self.module.compare(before, self.snapshot())
        self.assertFalse(result['requires_review']); self.assertEqual(result['reuse_decision'], 'eligible-for-manual-review')

    def test_content_change_invalidates(self):
        before = self.snapshot(); (self.root / 'api.py').write_text('new')
        self.assertEqual(self.module.compare(before, self.snapshot())['changed_paths'], ['api.py'])

    def test_tool_or_scope_change_invalidates(self):
        before = self.snapshot(); self.context['tool'] = 'v2'
        self.assertTrue(self.module.compare(before, self.snapshot())['requires_review'])

    def test_deleted_file_invalidates(self):
        before = self.snapshot(); (self.root / 'api.py').unlink()
        self.assertEqual(self.module.compare(before, self.snapshot())['missing_paths'], ['api.py'])

    def test_symlink_and_traversal_rejected(self):
        (self.root / 'linked.py').symlink_to(self.root / 'api.py')
        for path in ('linked.py', '../api.py', '/api.py', '.git/config', 'C:\\api.py'):
            with self.subTest(path=path), self.assertRaises(ValueError): self.module.capture(self.root, [path], self.context)

    def test_credential_file_not_read(self):
        (self.root / '.env').write_text('PRIVATE')
        with self.assertRaises(ValueError): self.module.capture(self.root, ['.env'], self.context)

    def test_expired_baseline(self):
        before = self.snapshot(); before['captured_at'] = '2000-01-01T00:00:00Z'
        self.assertTrue(self.module.compare(before, self.snapshot())['requires_review'])

    def test_no_source_or_context_contents_in_snapshot(self):
        self.context['private'] = 'PRIVATE'
        import json
        value = json.dumps(self.snapshot())
        self.assertNotIn('PRIVATE', value); self.assertNotIn('"source"', value)

    def test_empty_allowlist_rejected(self):
        with self.assertRaises(ValueError): self.module.capture(self.root, [], self.context)
