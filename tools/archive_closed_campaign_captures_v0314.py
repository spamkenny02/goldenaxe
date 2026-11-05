"""Archive closed D1-D7 intermediate captures; preserve every endpoint and ROM."""
import argparse,gzip,json,re,subprocess
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence
PLAN=ROOT/'validation/closed-captures-v0314-plan.json'
OUT=ROOT/'analysis/closed-captures-v0314'
REPORT=ROOT/'analysis/closed_capture_cleanup_v0314_report.json'
PATTERN=re.compile(r'^(ram|vram|cram|vdp_regs)_(\d+)\.bin$')

def idle():
    command=r"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and ($_.CommandLine -match 'v0314-d[1-7]-' -or $_.CommandLine -match 'tools[/\\](continue|finish|resume)_d[1-7].*v0314') } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
    r=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
    assert not r.stdout.strip(),'D1-D7 validation is still active: '+r.stdout

def bounded(name):
    p=(ROOT/name).resolve();assert p.is_relative_to(ROOT/'validation') and PATTERN.fullmatch(p.name)
    return p

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args();idle()
    assert not REPORT.exists(),'Cleanup already finalized'
    if not args.apply:
        candidates=[];endpoints={};roots=[]
        for family in ('natural-dungeon-route','natural-dungeon-combat','natural-service-route'):
            for folder in sorted((ROOT/'validation'/family).iterdir()):
                if not folder.is_dir() or not re.search(r'v0314-d[1-7]-',folder.name):continue
                assert folder.resolve().is_relative_to(ROOT/'validation'/family)
                capture=folder/'capture.json'
                if not capture.exists():continue
                c=json.loads(capture.read_bytes());assert c['rom_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
                roots.append(folder.relative_to(ROOT).as_posix())
                for p in folder.glob('*.bin'):
                    m=PATTERN.fullmatch(p.name)
                    if not m:continue
                    name=p.relative_to(ROOT).as_posix();bounded(name)
                    if int(m[2])==c['frames']:endpoints[name]=sha(p.read_bytes());continue
                    st=p.stat();candidates.append(dict(path=name,bytes=st.st_size,mtime_ns=st.st_mtime_ns))
        assert candidates and endpoints
        plan=dict(rom_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),roots=roots,candidates=candidates,protected_endpoints=endpoints,raw_bytes=sum(r['bytes']for r in candidates))
        PLAN.write_text(json.dumps(plan,indent=2)+'\n');print(len(candidates),'intermediate files;',plan['raw_bytes'],'bytes;',len(endpoints),'endpoint files protected');return
    plan=json.loads(PLAN.read_bytes());assert plan['rom_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
    for row in plan['candidates']:
        p=bounded(row['path']);st=p.stat();assert row['path']not in tracked and st.st_size==row['bytes'] and st.st_mtime_ns==row['mtime_ns']
    for name,h in plan['protected_endpoints'].items():assert sha((ROOT/name).read_bytes())==h
    paths=[bounded(r['path'])for r in plan['candidates']]+[PLAN,ROOT/'tools/archive_closed_campaign_captures_v0314.py']
    manifest=freeze(ROOT,OUT,paths,dict(version=314,scope='Only closed D1-D7 intermediate RAM/VDP captures; every actual endpoint,PNG,source,symbol,SRAM and ROM retained',rom_sha256=plan['rom_sha256']),[ROOT/p for p in plan['roots']],cleanup=False)
    idle();removed=[];roundtrip=None
    for i,row in enumerate(plan['candidates']):
        p=bounded(row['path']);item=manifest['compressed'][row['path']];raw=p.read_bytes();assert sha(raw)==item['raw_sha256']
        p.unlink()
        if i==0:
            try:
                recovered=evidence(p);assert recovered==raw
                roundtrip=dict(path=row['path'],sha256=sha(recovered),bytes=len(recovered))
            except Exception:
                p.write_bytes(raw);raise
        removed.append(dict(path=row['path'],bytes=len(raw)))
    manifest['removed_verified_generated']=removed
    temp=OUT/'manifest.json.tmp';temp.write_text(json.dumps(manifest,indent=2)+'\n');temp.replace(OUT/'manifest.json')
    for name,h in plan['protected_endpoints'].items():assert sha((ROOT/name).read_bytes())==h
    assert plan['rom_sha256']==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    stored=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file());raw=sum(r['bytes']for r in removed)
    report=dict(passed=True,md_sha256=plan['rom_sha256'],removed_files=len(removed),removed_bytes=raw,archive_bytes=stored,net_artifact_bytes_freed=raw-stored,protected_endpoint_files=len(plan['protected_endpoints']),endpoint_hashes_unchanged=True,first_deleted_capture_roundtrip=roundtrip,archive='analysis/closed-captures-v0314/manifest.json',scope='Only intermediate capture files removed after complete lossless archive readback. No public ROM,source,symbol,PNG or SRAM deletion. D8 and later live runs excluded.')
    REPORT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
