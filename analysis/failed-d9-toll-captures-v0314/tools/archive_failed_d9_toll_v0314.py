"""Archive closed failed D9 coin trials and remove only intermediate binary captures."""
import json,re,subprocess
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from rebase_natural_campaign import evidence

def main():
 out=ROOT/'analysis/failed-d9-toll-captures-v0314';assert not out.exists()
 command=r"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -match 'tools[\/](guarded|natural)_exterior_toll_v0314.py' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
 result=subprocess.run(['powershell','-NoProfile','-Command',command],capture_output=True,text=True,check=True);assert not result.stdout.strip(),result.stdout
 family=(ROOT/'validation/natural-service-route').resolve();pattern=re.compile(r'^(ram|vram|cram|vdp_regs)_(\d+)\.bin$');roots=[];paths=[];protected={};removed=[]
 for n in range(1,11):
  folder=(family/f'md-v0314-d9-earned-toll{n:02d}').resolve();assert folder.parent==family and folder.is_dir()
  report=folder/'report.json'
  if report.exists():
   r=json.loads(report.read_bytes());assert not r['passed']and r['failure']in('hero_died','frame_limit')
  else:assert json.loads((folder/'interrupted_diagnostic.json').read_bytes())['passed']is False
  roots.append(folder);latest={}
  binaries=[]
  for p in folder.iterdir():
   if not p.is_file():continue
   m=pattern.fullmatch(p.name)
   if m:
    binaries.append(p);key=m[1]
    if key not in latest or int(m[2])>latest[key][0]:latest[key]=(int(m[2]),p)
   else:paths.append(p)
  ends={row[1]for row in latest.values()}
  for p in ends:protected[p.relative_to(ROOT).as_posix()]=sha(p.read_bytes())
  for p in binaries:
   if p not in ends:paths.append(p);removed.append(p)
 assert removed and protected
 paths.append(__import__('pathlib').Path(__file__).resolve());before=sha((ROOT/'gaw-megadrive.bin').read_bytes());assert before=='c53381c459a1e6254a8c9f1cfad1b8cda482cc0614697ad566133b28335e07a7'
 first=removed[0];first_raw=first.read_bytes()
 manifest=freeze(ROOT,out,paths,dict(version=314,md_sha256=before,scope='Ten closed failed/interrupted controller-only coin trials. No positive campaign proof or ROM altered. Most recent actual binary captures per case are retained.'),roots,cleanup=True)
 assert not first.exists()and evidence(first)==first_raw
 for name,h in protected.items():assert sha((ROOT/name).read_bytes())==h
 assert sha((ROOT/'gaw-megadrive.bin').read_bytes())==before
 raw=sum(x['bytes']for x in manifest['removed_verified_generated']);stored=sum(p.stat().st_size for p in out.rglob('*')if p.is_file())
 r=dict(passed=True,md_sha256=before,scope='Housekeeping only, not a gameplay success. Original ROM, public numbered ROMs, source, all PNG/controls/reports and latest actual failure captures preserved.',cases=10,removed_files=len(manifest['removed_verified_generated']),removed_bytes=raw,archive_bytes=stored,net_artifact_bytes_freed=raw-stored,protected_binary_files=len(protected),protected_hashes_unchanged=True,removed_capture_recovered_exactly=True,archive='analysis/failed-d9-toll-captures-v0314/manifest.json')
 (ROOT/'analysis/failed_d9_toll_cleanup_v0314_report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
