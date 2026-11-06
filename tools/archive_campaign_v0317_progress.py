"""Preserve closed v317 campaign evidence, then remove intermediate RAM/VDP copies."""
import gzip,json,os,re,subprocess
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence


def idle():
    command="Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.ProcessId -ne "+str(os.getpid())+" -and $_.CommandLine -match 'v0317' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
    r=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
    assert not r.stdout.strip(),'Campaign jobs still active: '+r.stdout


def main():
    idle();out=ROOT/'analysis/campaign-v0317-progress'
    target=ROOT/'analysis/campaign_v0317_cleanup_report.json';assert not target.exists()
    roots=[]
    for family in ('natural-dungeon-route','natural-dungeon-combat','natural-service-route'):
        roots.extend(p for p in (ROOT/'validation'/family).iterdir() if p.is_dir() and 'v0317-' in p.name)
    roots.extend(p for p in (ROOT/'validation').iterdir() if p.is_dir() and p.name.startswith('v0317-'))
    roots.append(ROOT/'validation/campaign-v0317')
    assert roots and all(p.resolve().is_relative_to(ROOT/'validation') for p in roots)
    files=[p for folder in roots for p in folder.rglob('*') if p.is_file()]
    files.extend(p for p in (ROOT/'tools').glob('*v0317.py'))
    files.extend(p for p in (ROOT/'analysis').glob('*v0317_report.json'))
    pattern=re.compile(r'^(ram|vram|cram|vdp_regs)_(\d+)\.bin$')
    endpoints={};candidates=[]
    for p in files:
        match=pattern.fullmatch(p.name)
        if not match:continue
        capture=p.parent/'capture.json';assert capture.exists()
        c=json.loads(capture.read_bytes())
        name=p.relative_to(ROOT).as_posix()
        if int(match[2])==c['frames']:endpoints[name]=sha(p.read_bytes())
        else:candidates.append(p)
    tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
    assert all(p.relative_to(ROOT).as_posix() not in tracked for p in candidates)
    rom_hash=sha((ROOT/'gaw-megadrive.bin').read_bytes())
    manifest=freeze(ROOT,out,files,dict(version=317,md_sha256=rom_hash,
        scope='Closed fresh campaign stages and rejected controller diagnostics; all endpoints, PNGs, sources, symbols and numbered ROMs retained.'),roots,cleanup=False)
    idle();removed=[]
    for p in candidates:
        p=p.resolve();assert p.is_relative_to(ROOT/'validation') and any(p.is_relative_to(r.resolve()) for r in roots)
        name=p.relative_to(ROOT).as_posix();item=manifest['compressed'][name]
        raw=p.read_bytes();assert sha(raw)==item['raw_sha256']
        assert gzip.decompress((out/item['stored']).read_bytes())==raw
        p.unlink();removed.append(dict(path=name,bytes=len(raw)))
    manifest['removed_verified_generated']=removed
    temp=out/'manifest.json.tmp';temp.write_text(json.dumps(manifest,indent=2)+'\n');temp.replace(out/'manifest.json')
    for name,digest in endpoints.items():assert sha((ROOT/name).read_bytes())==digest
    if removed:
        first=removed[0];assert sha(evidence(ROOT/first['path']))==manifest['compressed'][first['path']]['raw_sha256']
    assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==rom_hash
    raw_bytes=sum(r['bytes'] for r in removed)
    stored=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
    result=dict(passed=True,version=317,md_sha256=rom_hash,closed_roots=len(roots),
        removed_files=len(removed),removed_bytes=raw_bytes,archive_bytes=stored,
        net_artifact_bytes_freed=raw_bytes-stored,protected_endpoint_files=len(endpoints),
        archive=out.relative_to(ROOT).as_posix()+'/manifest.json',
        limits='Only intermediate generated RAM/VDP files removed after lossless gzip/SHA readback. ROMs, endpoints, PNGs, code, symbols and SRAM remain.')
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
