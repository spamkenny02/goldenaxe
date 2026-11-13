"""Rebuild the accepted V328 entirely from native sources and checked-in assets."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = '368c003f92e0860336c919005ec19f0ae620d6876b4bca8f436f83e682b59dcc'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--sgdk', type=Path, required=True)
    p.add_argument('--java', type=Path, required=True)
    a = p.parse_args()
    out = (ROOT / a.out).resolve()
    assert out.is_relative_to(ROOT / 'validation') and not out.exists()
    out.mkdir(parents=True)
    sdk = a.sgdk.resolve()
    for tool, args in [
        ('build_rc_rom.py', ['--out',str(out/'base'),'--sgdk',str(sdk),'--java',str(a.java.resolve())]),
        ('build_konami_candidate.py', ['--out',str(out/'konami'),'--base',str(out/'base/gaw-megadrive-v0322-rc1.bin'),'--sdk-bin',str(sdk/'bin')]),
        ('build_presentation_candidate.py', ['--out',str(out/'final'),'--base',str(out/'konami/candidate.bin'),'--sdk-bin',str(sdk/'bin')]),
    ]:
        print('Building',tool,flush=True)
        with (out/(tool+'.log')).open('wb') as log:
            subprocess.run([sys.executable,str(ROOT/'tools'/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    data = (out/'final/candidate.bin').read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == EXPECTED and len(data) == 2097152, 'Rebuild differs from accepted V328'
    target = out/'gaw-megadrive-v0328.bin'
    target.write_bytes(data)
    report = dict(passed=True,md_sha256=digest,bytes=len(data),source_build=True,
                  prebuilt_game_rom_used=False,chain=['native V319','credits V320','title V321','dialogue V322','Konami V323','presentation and save guards V328'],
                  frozen_base_save_sha256=hashlib.sha256((ROOT/'megadrive/rebuild-base/save.inc').read_bytes()).hexdigest())
    (out/'source-build-report.json').write_text(json.dumps(report,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=True,rom=str(target),md_sha256=digest)),flush=True)


if __name__ == '__main__':
    main()
