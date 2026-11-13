#!/usr/bin/env python3
"""Check index completeness, links, generated files and search behavior."""
import csv
from pathlib import Path
import re
import subprocess
import tempfile
import shutil
from build_reference import ROOT, render


def check():
    rows = list(csv.DictReader((ROOT / 'coverage.csv').open(encoding='utf-8', newline='')))
    rounds = '2601 2502 2501 2402 2401 2201 2102 2101 2003 2002 2001'.split()
    expected = {f'{r}-{n:02d}' for r in rounds for n in range(1, 17)}
    assert len(rows) == 176 and {r['id'] for r in rows} == expected, 'missing or duplicated ID'
    assert len(list((ROOT / 'topics').glob('*.md'))) == 12
    for row in rows:
        assert row['status'] == 'mapped', row
        assert row['source_url'] == 'https://dev-centralpark.tistory.com/51'
        for topic in row['topics'].split(';'):
            assert topic.startswith('topics/') and (ROOT / topic).is_file(), topic
    for path in ROOT.rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        assert text.count('```') % 2 == 0, f'unclosed fence: {path}'
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in target or target.startswith('#'):
                continue
            assert (path.parent / target.split('#', 1)[0]).exists(), (path, target)
    for path, content in render().items():
        assert path.read_text(encoding='utf-8') == content, f'rebuild {path.name}'
    for path in (ROOT / 'scripts').glob('*.sh'):
        subprocess.run(['bash', '-n', str(path)], check=True)
    with tempfile.TemporaryDirectory(prefix='linuxmaster checks ') as directory:
        copy = Path(directory) / 'path with spaces'
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        script = copy / 'scripts/search.sh'
        for term in ['2601-14', '역방향', 'make menuconfig', 'xfs_quota', '-n']:
            result = subprocess.run(['bash', str(script), term], stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, universal_newlines=True)
            assert result.returncode == 0 and result.stdout, (term, result.stderr)
        for term in ['NO_SUCH_LINUXMASTER_TERM', '$(touch SENTINEL);[*]']:
            result = subprocess.run(['bash', str(script), term], cwd=copy,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            assert result.returncode == 1 and not (copy / 'SENTINEL').exists()
        assert subprocess.run(['bash', str(script)], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE).returncode == 2
    print('PASS: 176 IDs, 12 topics, links, generated files, shell syntax, portable literal search')


if __name__ == '__main__':
    check()
