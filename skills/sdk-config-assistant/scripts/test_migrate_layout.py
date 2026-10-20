"""
Unit tests for migrate_layout.py — moving a working folder from the old layout
(SDK-config-assistant/outputs, SDK-config-coding/sites) to the layout-by-skill one.
Run: python3 -m unittest scripts/test_migrate_layout.py
"""
import datetime
import filecmp
import json
import os
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))

import migrate_layout as ml  # noqa: E402  (after path fix)

HERE = pathlib.Path(__file__).resolve().parent
CODING_COPY = HERE.parents[1] / 'sdk-config-coding' / 'scripts' / 'migrate_layout.py'
OLDER_MTIME = 1_780_000_000
# The script names a duplicate by its folder's local-time date, so compute it the same way.
OLDER_SUFFIX = datetime.datetime.fromtimestamp(OLDER_MTIME).strftime('%Y%m%d')


def _write(p, text=''):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
    return p


def _json(p, data):
    return _write(p, json.dumps(data))


def _case_sensitive(d):
    _write(d / 'Probe')
    sensitive = not (d / 'probe').exists()
    (d / 'Probe').unlink()
    return sensitive


class MigrateLayoutTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def run_it(self, **kw):
        return ml.Migration(self.root, kw.pop('dry_run', False)).run(**kw)

    def old_layout(self):
        """A folder used by the previous version: two runs for one site, one unknown output,
        and a handed-off site with a backup."""
        a = self.root / 'SDK-config-assistant'
        _json(a / 'profiles' / 'acmeretail.json', {
            'customer': {'name': 'Acme Retail', 'productionDomain': 'https://www.acmeretail.com/'},
            'handoff': {'folder': 'SDK-config-coding/sites/www.acmeretail.com/',
                        'backupFolder': 'SDK-config-coding/sites/www.acmeretail.com.bak-20260901-101010/'}})
        _json(a / 'profiles' / 'acmeretail.analytics.json', {'runs': []})
        latest = a / 'outputs' / 'acme-retail'
        _json(latest / 'acme-retail-customer-signal-config.json',
              {'customer': {'productionDomain': 'www.acmeretail.com'}})
        _write(latest / 'acoConnectSdkConfig-acmeretail.js', '// new')
        older = a / 'outputs' / 'acmeretail-2026'
        _write(older / 'acoConnectSdkConfig-acmeretail.js', '// old')
        _write(a / 'outputs' / 'scratch' / 'notes.txt', 'x')
        os.utime(older, (OLDER_MTIME, OLDER_MTIME))
        os.utime(latest, (1_790_000_000, 1_790_000_000))
        c = self.root / 'SDK-config-coding' / 'sites'
        _write(c / 'www.acmeretail.com' / 'acoconnect-loader.js', '// loader')
        _write(c / 'www.acmeretail.com.bak-20260901-101010' / 'acoconnect-loader.js', '// bak')

    def test_empty_folder_is_left_alone(self):
        res = self.run_it()
        self.assertEqual(res['status'], 'nothing_to_do')
        self.assertEqual(ml.names(self.root), set())

    def test_old_layout_moves_to_layout_by_skill(self):
        self.old_layout()
        res = self.run_it()
        self.assertEqual(res['status'], 'migrated')
        top = ml.names(self.root)
        self.assertIn('sdk-config-assistant', top)
        self.assertIn('sdk-config-coding', top)
        self.assertNotIn('SDK-config-assistant', top)
        self.assertNotIn('SDK-config-coding', top)

        a = self.root / 'sdk-config-assistant'
        self.assertEqual((a / 'www.acmeretail.com' / 'acoConnectSdkConfig-acmeretail.js').read_text(), '// new')
        self.assertEqual((a / ('www.acmeretail.com-' + OLDER_SUFFIX) / 'acoConnectSdkConfig-acmeretail.js').read_text(), '// old')
        self.assertTrue((a / 'profiles' / 'acmeretail.analytics.json').is_file())
        # Unknown output stays put, with a note saying why.
        self.assertTrue((a / 'outputs' / 'scratch' / 'notes.txt').is_file())
        self.assertIn('scratch', (a / 'outputs' / 'MIGRATED.txt').read_text())
        self.assertEqual([i['reason'] for i in res['left']], ['host_unknown'])

        c = self.root / 'sdk-config-coding'
        self.assertEqual((c / 'www.acmeretail.com' / 'acoconnect-loader.js').read_text(), '// loader')
        self.assertTrue((c / 'www.acmeretail.com.bak-20260901-101010').is_dir())
        self.assertNotIn('sites', ml.names(c))

        h = json.loads((a / 'profiles' / 'acmeretail.json').read_text())['handoff']
        self.assertEqual(h['folder'], 'sdk-config-coding/www.acmeretail.com/')
        self.assertEqual(h['backupFolder'], 'sdk-config-coding/www.acmeretail.com.bak-20260901-101010/')

    def test_second_run_does_nothing(self):
        self.old_layout()
        self.run_it()
        res = self.run_it()
        self.assertEqual(res['status'], 'nothing_to_do')
        self.assertEqual(res['moved'], [])

    def test_dry_run_changes_nothing_and_reports_the_same_moves(self):
        self.old_layout()
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*'))
        dry = self.run_it(dry_run=True)
        after = sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*'))
        self.assertEqual(before, after)
        real = self.run_it()
        self.assertEqual([m['to'] for m in dry['moved']], [m['to'] for m in real['moved']])
        self.assertEqual(dry['profilesUpdated'], real['profilesUpdated'])

    def test_existing_destination_is_never_overwritten(self):
        _write(self.root / 'sdk-config-coding' / 'www.acmeretail.com' / 'acoconnect-loader.js', '// keep')
        _write(self.root / 'sdk-config-coding' / 'sites' / 'www.acmeretail.com' / 'acoconnect-loader.js', '// other')
        res = self.run_it()
        self.assertEqual((self.root / 'sdk-config-coding' / 'www.acmeretail.com' / 'acoconnect-loader.js').read_text(), '// keep')
        self.assertEqual([i['reason'] for i in res['left']], ['destination_exists'])
        self.assertTrue((self.root / 'sdk-config-coding' / 'sites' / 'MIGRATED.txt').is_file())

    def test_output_host_from_bundle_name_and_profile(self):
        _json(self.root / 'sdk-config-assistant' / 'profiles' / 'northwindtrading.json',
              {'customer': {'productionDomain': 'northwindtrading.co.uk'}})
        _write(self.root / 'sdk-config-assistant' / 'outputs' / 'nw' / 'acoConnectSdkConfig-northwindtrading.js')
        self.run_it()
        self.assertTrue((self.root / 'sdk-config-assistant' / 'northwindtrading.co.uk').is_dir())
        self.assertNotIn('outputs', ml.names(self.root / 'sdk-config-assistant'))

    def test_coding_assistant_old_name(self):
        _write(self.root / 'SDK-coding-assistant' / 'sites' / 'shop.example.com' / 'acoconnect-loader.js')
        self.run_it()
        self.assertTrue((self.root / 'sdk-config-coding' / 'shop.example.com' / 'acoconnect-loader.js').is_file())
        self.assertNotIn('SDK-coding-assistant', ml.names(self.root))

    def test_root_sites_move_only_when_asked(self):
        _write(self.root / 'sites' / 'shop.example.com' / 'acoconnect-loader.js')
        res = self.run_it()
        self.assertTrue(res['rootSites'])
        self.assertTrue((self.root / 'sites' / 'shop.example.com').is_dir())
        self.run_it(include_root_sites=True)
        self.assertTrue((self.root / 'sdk-config-coding' / 'shop.example.com').is_dir())
        self.assertNotIn('sites', ml.names(self.root))

    def test_opened_inside_the_old_coding_folder(self):
        inner = self.root / 'SDK-config-coding'
        _write(inner / 'sites' / 'shop.example.com' / 'acoconnect-loader.js')
        res = ml.Migration(inner).run()
        self.assertEqual(res['status'], 'wrong_root')
        self.assertEqual(res['openIn'], str(self.root))

    def test_both_spellings_merge_on_a_case_sensitive_disk(self):
        if not _case_sensitive(self.root):
            self.skipTest('case-insensitive file system')
        _write(self.root / 'sdk-config-assistant' / 'profiles' / 'a.json', '{}')
        _write(self.root / 'SDK-config-assistant' / 'profiles' / 'a.json', '{"old": 1}')
        _write(self.root / 'SDK-config-assistant' / 'profiles' / 'b.json', '{}')
        res = self.run_it()
        self.assertEqual((self.root / 'sdk-config-assistant' / 'profiles' / 'a.json').read_text(), '{}')
        self.assertTrue((self.root / 'sdk-config-assistant' / 'profiles' / 'b.json').is_file())
        self.assertEqual([i['reason'] for i in res['left']], ['destination_exists'])

    def test_both_skill_copies_are_identical(self):
        self.assertTrue(filecmp.cmp(HERE / 'migrate_layout.py', CODING_COPY, shallow=False),
                        'sdk-config-coding/scripts/migrate_layout.py differs from this copy')


if __name__ == '__main__':
    unittest.main()
