"""Losslessly compact closed D9 intermediate captures; retain every endpoint and screenshot."""
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'tools'))
from archive_lossless_evidence import freeze

project_validation = (root / 'validation/c0046-campaign01/isolated/project/validation').resolve()
reports = [root / 'analysis' / name for name in
           ('palc0046_d9_midboss_report.json', 'palc0046_d9_report.json')]
folders = set()
for report in reports:
    data = json.loads(report.read_bytes())
    assert data['passed'] and data['candidate'] == 'c0046' and data['region'] == 'pal'
    folders.update((root / stage['trace']).resolve() for stage in data['stages'])
paths = {Path(__file__).resolve(), *reports}
endpoints = []
generated_bytes = 0
for folder in sorted(folders):
    assert folder.is_relative_to(project_validation)
    capture = json.loads((folder / 'capture.json').read_bytes())
    assert capture['rom_sha256'] == '9e747d38e0c6fb2d69b7c1aa8c2b296a61e8b6af41171d14e543ed9a6cb49cf5'
    end = capture['frames']
    endpoints.append((folder / f'ram_{end:05d}.bin').relative_to(root).as_posix())
    assert (folder / f'ram_{end:05d}.bin').is_file()
    for path in folder.iterdir():
        if not re.fullmatch(r'(ram|vram|cram|vdp_regs)_\d+\.bin', path.name):
            continue
        if int(path.stem.rsplit('_', 1)[1]) == end:
            continue
        paths.add(path)
        generated_bytes += path.stat().st_size
assert generated_bytes > 0
freeze(root, root / 'analysis/palc0046-d9-intermediate-captures', paths,
       dict(passed=True, lossless_archive_only=True, new_gameplay_milestone=False,
            closed_stage_folders=len(folders), generated_bytes_before=generated_bytes,
            retained_ram_endpoints=endpoints, retained_all_screenshots=True,
            scope='Closed D9 intermediate capture binaries only; gzip SHA/readback before deletion. '
                  'Every stage endpoint, screenshot, recording and numbered ROM is retained.'),
       sorted(folders), cleanup=True)
for name in endpoints:
    assert (root / name).is_file()
