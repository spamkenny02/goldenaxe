"""Run the existing hardware sprite-scroll checks in an immutable v314 sandbox."""
import json
import shutil
import sys
from pathlib import Path

import validate_scroll_objects as checks
from archive_lossless_evidence import sha
from run_core import ROOT


def main():
    sandbox = ROOT / 'validation/scroll-objects-v0314'
    assert not sandbox.exists(), 'Preserve existing recordings; never overwrite a run'
    digest = sha((ROOT / 'gaw-megadrive.bin').read_bytes())
    assert digest == 'c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
    for name in ('gaw-megadrive.bin', 'input/original.sms',
                 'megadrive/out/release/symbol.txt',
                 'validation/sms-vertical-check/ram_03120.bin'):
        destination = sandbox / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    checks.ROOT = sandbox
    regions = []
    for region, suffix in [('auto', ''), ('pal', '-pal')]:
        sys.argv = [__file__] + (['--pal'] if suffix else [])
        checks.main()
        report = json.loads((sandbox / f'validation/scroll_objects{suffix}_report.json').read_bytes())
        assert report['md_sha256'] == digest and len(report['cases']) == 4
        for case in report['cases']:
            for result in case['checks'].values():
                assert not result['nonhero_sprite_errors']
                assert result['gameplay_resumes'] and result['old_object_flags_cleared']
                assert result['primary_living_mask_preserved']
        regions.append(report)
    evidence = {}
    for path in sorted(sandbox.rglob('*')):
        if path.is_file():
            evidence[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    for path in [Path(__file__), ROOT / 'tools/validate_scroll_objects.py']:
        evidence[path.relative_to(ROOT).as_posix()] = sha(path.read_bytes())
    result = dict(passed=True, version=314, md_sha256=digest,
                  regions=regions, direction_region_cases=8, evidence=evidence,
                  scope='Controlled visible actors and coin, real edge crossings and hardware sprite tables. Old objects disappear during all four exterior scroll directions in both regions; gameplay and persistence resume. Not a proof of every background pixel, dungeon scroll, enemy AI or whole-game fidelity.')
    target = ROOT / 'analysis/scroll_objects_v0314_report.json'
    assert not target.exists()
    target.write_text(json.dumps(result, indent=2) + '\n')
    print('V314 exterior scroll object checks passed in both regions', flush=True)


if __name__ == '__main__':
    main()
