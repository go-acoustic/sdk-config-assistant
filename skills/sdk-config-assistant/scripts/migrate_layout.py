#!/usr/bin/env python3
"""Move an SDK Config working folder from the old layout to the layout-by-skill one.

Old layout (inside the folder the user added):
    SDK-config-assistant/outputs/<anything>/   generated SDK Config, review, test guide
    SDK-config-assistant/profiles/             website profiles + analytics sidecars
    SDK-config-coding/sites/<host>/            handed-off sites (coding assistant)
    SDK-coding-assistant/sites/<host>/         handoffs made under the coding assistant's old name

New layout:
    sdk-config-assistant/<host>/               generated SDK Config, review, test guide
    sdk-config-assistant/profiles/             website profiles + analytics sidecars (unchanged)
    sdk-config-coding/<host>/                  handed-off sites
    sdk-config-analysis/                       analysis reports (created by that skill when it writes one)

<host> is the production hostname exactly as the handoff writes it (lower case, `www.` kept).

Rules: nothing is deleted or overwritten. A folder whose destination already exists, or an
output folder whose host can't be worked out, stays where it is and is listed under `left`.
An old folder is removed only once it is empty. Running it again on a migrated folder does
nothing. The same file ships in sdk-config-assistant/scripts and sdk-config-coding/scripts;
keep the two copies identical (test_migrate_layout.py checks this).

Usage: migrate_layout.py ROOT [--dry-run] [--include-root-sites]
    --include-root-sites   also move ROOT/sites/* (a coding project in the old layout) into
                           ROOT/sdk-config-coding/. Only the coding assistant passes this, and
                           only after the user agreed.
Prints one JSON object: {"status": "migrated" | "nothing_to_do" | "wrong_root" | "error", ...}
"""
import datetime
import json
import os
import pathlib
import re
import sys

ASSISTANT, CODING = 'sdk-config-assistant', 'sdk-config-coding'
LEGACY_TOP = {'SDK-config-assistant': ASSISTANT, 'SDK-config-coding': CODING}
LEGACY_SITES = ('SDK-config-coding/sites/', 'SDK-coding-assistant/sites/')
JUNK = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}


def host_of(domain):
    """Same normalisation as the handoff script in sdk-config-assistant/SKILL.md (E-3)."""
    v = re.sub(r'^[a-z][a-z0-9+.-]*://', '', (domain or '').strip().lower())
    return v.split('/')[0].split('?')[0].split('#')[0].split(':')[0].rstrip('.')


def domain_slug(v):
    """Same rule as generate_sdk_patched.domain_slug — the bundle file name's slug."""
    v = re.sub(r'^www\d*\.', '', (v or '').lower().strip()).split('.')[0]
    return re.sub(r'[^a-z0-9]', '', v) or 'customer'


def names(d):
    """Directory entries, case preserved. Used instead of exists() because on a
    case-insensitive disk `sdk-config-assistant` 'exists' when only `SDK-config-assistant` does."""
    try:
        return set(os.listdir(d))
    except OSError:
        return set()


def read_json(p):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None


class Migration:
    def __init__(self, root, dry_run=False):
        self.root, self.dry = pathlib.Path(root), dry_run
        self.stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        self.moved, self.left, self.profiles_updated, self.removed = [], [], [], []
        self.pending = {}  # dst folder -> lower-cased names claimed by moves (matters in a dry run)

    def rel(self, p):
        return str(pathlib.Path(p).relative_to(self.root))

    def top(self, new):
        """The top-level folder for `new`. In a dry run step 1 hasn't renamed anything, so
        later steps read from whichever spelling is on disk."""
        present = names(self.root)
        if self.dry and new not in present:
            for old, n in LEGACY_TOP.items():
                if n == new and old in present:
                    return self.root / old
        return self.root / new

    def rel_new(self, p):
        r = self.rel(p)
        for old, new in LEGACY_TOP.items():
            if r == old or r.startswith(old + '/'):
                return new + r[len(old):]
        return r

    def move(self, src, dst):
        self.moved.append({'from': self.rel(src), 'to': self.rel_new(dst)})
        self.pending.setdefault(dst.parent, set()).add(dst.name.lower())
        if not self.dry:
            os.rename(src, dst)

    def leave(self, p, reason):
        self.left.append({'path': self.rel(p), 'reason': reason})

    def free_name(self, parent, base, mtime):
        """`base`, else `base-YYYYMMDD`, else `base-YYYYMMDD-HHMMSS` (the coding handoff's
        'alongside' naming), else None."""
        taken = {n.lower() for n in names(parent)} | self.pending.get(parent, set())
        t = datetime.datetime.fromtimestamp(mtime)
        for n in (base, base + '-' + t.strftime('%Y%m%d'), base + '-' + t.strftime('%Y%m%d-%H%M%S')):
            if n.lower() not in taken:
                return n
        return None

    # -- step 1: lower-case the two top-level folders, or merge if both spellings exist ------
    def top_level(self):
        for old, new in LEGACY_TOP.items():
            present = names(self.root)
            if old not in present:
                continue
            if new not in present:
                # A case-only rename needs two steps on a case-insensitive disk.
                tmp = self.root / ('.migrating-' + new + '-' + self.stamp)
                self.moved.append({'from': old, 'to': new})
                if not self.dry:
                    os.rename(self.root / old, tmp)
                    os.rename(tmp, self.root / new)
            else:
                # Case-sensitive disk with both spellings: an older plugin version ran after a
                # migration. Merge what doesn't clash.
                self.merge(self.root / old, self.root / new)

    def merge(self, src, dst):
        for n in sorted(names(src) - JUNK):
            if n in names(dst):
                if (src / n).is_dir() and (dst / n).is_dir() and n in ('outputs', 'profiles', 'sites'):
                    if not self.dry:
                        (dst / n).mkdir(exist_ok=True)
                    self.merge(src / n, dst / n)
                else:
                    self.leave(src / n, 'destination_exists')
            else:
                self.move(src / n, dst / n)
        self.remove_if_empty(src)

    def remove_if_empty(self, d):
        if self.dry or not d.is_dir():
            return
        for j in JUNK & names(d):
            try:
                (d / j).unlink()
            except OSError:
                pass
        if not names(d):
            d.rmdir()
            self.removed.append(self.rel(d))

    # -- step 2: flatten sites/ into sdk-config-coding/ ------------------------------------
    def flatten(self, sites, dst):
        if not sites.is_dir():
            return
        if not self.dry:
            dst.mkdir(exist_ok=True)
        for n in sorted(names(sites) - JUNK):
            src = sites / n
            if n.lower() in {x.lower() for x in names(dst)} | self.pending.get(dst, set()):
                self.leave(src, 'destination_exists')
            else:
                self.move(src, dst / n)
        self.remove_if_empty(sites)

    def coding(self, include_root_sites):
        dst = self.top(CODING)
        self.flatten(dst / 'sites', dst)
        if 'SDK-coding-assistant' in names(self.root):
            self.flatten(self.root / 'SDK-coding-assistant' / 'sites', dst)
            self.remove_if_empty(self.root / 'SDK-coding-assistant')
        if include_root_sites:
            self.flatten(self.root / 'sites', dst)

    # -- step 3: outputs/<anything> -> sdk-config-assistant/<host> ---------------------------
    def profiles(self):
        d = self.top(ASSISTANT) / 'profiles'
        out = []
        for p in sorted(d.glob('*.json')) if d.is_dir() else []:
            if p.name.endswith('.analytics.json') or p.name.startswith('.'):
                continue
            data = read_json(p)
            if isinstance(data, dict):
                out.append((p, data))
        return out

    def host_for_output(self, folder, profiles):
        for cfg in sorted(folder.glob('*-customer-signal-config.json')):
            data = read_json(cfg)
            h = host_of(((data or {}).get('customer') or {}).get('productionDomain'))
            if h:
                return h
        hosts = set()
        for js in folder.glob('acoConnectSdkConfig-*.js'):
            if js.name.endswith('.tamperMonkeyConfig.js'):
                continue
            ds = js.name[len('acoConnectSdkConfig-'):-len('.js')]
            for _, d in profiles:
                raw = (d.get('customer') or {}).get('productionDomain') if isinstance(d.get('customer'), dict) else None
                # The generator slugs the raw value; match the hostname too in case it held a URL.
                if raw and ds in (domain_slug(raw), domain_slug(host_of(raw))):
                    hosts.add(host_of(raw))
        hosts.discard('')
        if len(hosts) == 1:
            return hosts.pop()
        # Last resort: the folder is named after a profile file (its slug).
        for p, d in profiles:
            if folder.name.lower() == p.stem.lower() and isinstance(d.get('customer'), dict):
                return host_of(d['customer'].get('productionDomain')) or None
        return None

    def outputs(self):
        adir = self.top(ASSISTANT)
        out = adir / 'outputs'
        if not out.is_dir():
            return
        profiles = self.profiles()
        folders = [out / n for n in names(out) - JUNK if (out / n).is_dir()]
        # Newest first, so the latest run of a site gets the plain <host> name.
        for f in sorted(folders, key=lambda p: p.stat().st_mtime, reverse=True):
            host = self.host_for_output(f, profiles)
            if not host or host in ('profiles', 'outputs'):
                self.leave(f, 'host_unknown')
                continue
            n = self.free_name(adir, host, f.stat().st_mtime)
            if not n:
                self.leave(f, 'destination_exists')
                continue
            self.move(f, adir / n)
        for n in sorted(names(out) - JUNK):
            if not (out / n).is_dir():
                self.leave(out / n, 'not_a_folder')
        self.remove_if_empty(out)

    # -- step 4: rewrite the handoff folder recorded in each profile -----------------------
    def rewrite_profiles(self):
        for p, data in self.profiles():
            h = data.get('handoff')
            if not isinstance(h, dict):
                continue
            changed = False
            for k in ('folder', 'backupFolder'):
                v = h.get(k)
                if isinstance(v, str) and v.startswith(LEGACY_SITES):
                    h[k] = CODING + '/' + v.split('/sites/', 1)[1]
                    changed = True
            if changed:
                self.profiles_updated.append(self.rel_new(p))
                if not self.dry:
                    tmp = p.with_name('.' + p.name + '.tmp')
                    tmp.write_text(json.dumps(data, indent=2), encoding='utf-8')
                    json.loads(tmp.read_text(encoding='utf-8'))
                    os.replace(tmp, p)

    # -- leftovers: say why something is still in an old folder ---------------------------
    def note_leftovers(self):
        if self.dry or not self.left:
            return
        by_dir = {}
        for item in self.left:
            by_dir.setdefault(str(pathlib.Path(item['path']).parent), []).append(item)
        for d, items in by_dir.items():
            target = self.root / d
            if not target.is_dir():
                continue
            lines = ['These items were not moved when this folder was migrated to the layout-by-skill',
                     'structure (' + self.stamp + '). Nothing was deleted. Move them by hand if you need them:', '']
            lines += ['- ' + pathlib.Path(i['path']).name + ' — ' + {
                'destination_exists': 'a folder with the same name already exists in the new location',
                'host_unknown': "the website it belongs to couldn't be worked out",
                'not_a_folder': 'a loose file, not a site folder',
            }.get(i['reason'], i['reason']) for i in items]
            (target / 'MIGRATED.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    def run(self, include_root_sites=False):
        here = self.root.name.lower()
        if here in (CODING, 'sdk-coding-assistant') and 'sites' in names(self.root):
            return {'status': 'wrong_root', 'openIn': str(self.root.parent)}
        self.top_level()
        self.coding(include_root_sites)
        self.outputs()
        self.rewrite_profiles()
        self.note_leftovers()
        changed = self.moved or self.profiles_updated
        return {'status': 'migrated' if changed else 'nothing_to_do', 'dryRun': self.dry,
                'moved': self.moved, 'left': self.left, 'profilesUpdated': self.profiles_updated,
                'removed': self.removed,
                'rootSites': (not include_root_sites) and (self.root / 'sites').is_dir()}


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    if len(args) != 1:
        print(json.dumps({'status': 'error', 'reason': 'usage: migrate_layout.py ROOT [--dry-run] [--include-root-sites]'}))
        return 2
    root = pathlib.Path(args[0])
    if not root.is_dir():
        print(json.dumps({'status': 'error', 'reason': 'root_not_found'}))
        return 2
    try:
        res = Migration(root, '--dry-run' in argv).run('--include-root-sites' in argv)
    except OSError as e:
        res = {'status': 'error', 'reason': type(e).__name__, 'detail': str(e)[:200]}
    print(json.dumps(res, indent=1))
    return 0 if res['status'] != 'error' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
