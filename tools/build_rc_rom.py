"""Clean source build plus the three audited, fixed-address 68000 corrections."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--sgdk',type=Path,required=True);p.add_argument('--java',type=Path,required=True);a=p.parse_args()
    out=(ROOT/a.out).resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists()
    out.mkdir(parents=True);project=out/'project';project.mkdir()
    for name in ('src','research','z80'):shutil.copytree(ROOT/'megadrive'/name,project/name)
    with (out/'compile.log').open('wb') as log:
        subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'tools/build_private_candidate.ps1'),
            '-Project',str(project),'-Sgdk',a.sgdk.resolve().as_posix(),'-Java',a.java.resolve().as_posix(),'-PaddingByte','255'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    base=project/'out/release/rom.bin'
    assert hashlib.sha256(base.read_bytes()).hexdigest()=='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e'
    steps=[('build_credits_border_overlay.py','credits','candidate.bin'),('build_title_publication_overlay.py','title','candidate.bin'),('build_dialogue_empty_width_candidate.py','dialogue','candidate.bin')]
    for tool,name,filename in steps:
        target=out/name
        with (out/(name+'.log')).open('wb') as log:
            subprocess.run([sys.executable,str(ROOT/'tools'/tool),'--out',str(target),
                '--base',str(base),'--sdk-bin',str(a.sgdk.resolve()/'bin')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        # Credits and title builders use their own historical names.
        options=[p for p in target.glob('*.bin') if p.name!='overlay.bin']
        base=next(p for p in options if hashlib.sha256(p.read_bytes()).hexdigest() in (
            '9e5b0abed80678ce864a0bb796c17e97047d1d34e5227a5275bf9336129ceaff',
            '89c5833351312ffaa591efb1939161910a298af06437080e2cf84fb3fb8ac86e',
            '1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'))
    digest=hashlib.sha256(base.read_bytes()).hexdigest();assert digest=='1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'
    target=out/'gaw-megadrive-v0322-rc1.bin';shutil.copyfile(base,target)
    report=dict(passed=True,md_sha256=digest,source_build=True,base_program_sha256='d3ea2a83ea24ed8a0d3c9857f9fbe70d000a4f73358452c1887f40e78966c56e',
        overlays=['credits_border.s','title_publication.s','dialogue_empty_width.s'],bytes=target.stat().st_size,
        source_manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for directory in ('src','research','z80','overlays') for p in (ROOT/'megadrive'/directory).rglob('*') if p.is_file()})
    (out/'source-build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(passed=True,rom=str(target),md_sha256=digest)),flush=True)


if __name__=='__main__':main()
