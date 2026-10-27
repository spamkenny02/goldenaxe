"""Compare the same Earth/warp route before and after observer optimization."""
import json
from run_core import ROOT
from rebase_natural_campaign import evidence
from archive_lossless_evidence import sha

def main():
 roots=[ROOT/'validation/natural-dungeon-combat'/('md-auto-v0293-d6-warp0'+str(i)) for i in [1,2]];cs=[json.loads(evidence(p/'capture.json')) for p in roots];assert cs[0]['frames']==cs[1]['frames']==121939;refs={}
 def read(p):raw=evidence(p);refs[p.relative_to(ROOT).as_posix()]=sha(raw);return raw
 for n in ['controls.json','ram_121939.bin','frame_121939.png']:assert read(roots[0]/n)==read(roots[1]/n),n
 assists=[json.loads(read(p/'assistance.json')) for p in roots];assert assists[0]['writes']==assists[1]['writes']
 reports=[json.loads(read(p/'report.json')) for p in roots];assert all(r['passed'] and r['earth_route_passed'] for r in reports)
 report=dict(passed=True,md_sha256=cs[0]['rom_sha256'],frames=121939,controls_exact=True,whole_ram_bytes=65536,final_png_exact=True,assistance_writes_exact=True,driver_before=reports[0]['driver_sha256'],driver_after=reports[1]['driver_sha256'],evidence=refs,limits=['Optimization of native test controller prefix observation only. No production ROM changes,no primary state import. Source SMS optimization and global timing are not asserted.'])
 (ROOT/'analysis/d6_prefix_optimization_v0293_report.json').write_text(json.dumps(report,indent=2)+'\n');print('D6 prefix optimization:controls,writes,whole RAM and final PNG identical')

if __name__=='__main__':main()
