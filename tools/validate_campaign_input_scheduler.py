"""Compare overlapping interval compilation against the previous OR loop."""
import json,random
from run_core import ROOT,compile_fixed_inputs,compact_fixed_inputs
from archive_lossless_evidence import sha

def main():
 rng=random.Random(0x292)
 for case in range(2000):
  end=rng.randrange(1,201);rows=[(rng.randrange(-10,end+10),rng.randrange(-10,end+10),rng.randrange(-2,16)) for i in range(rng.randrange(80))];old=[0]*(end+1)
  for a,b,k in rows:
   if k<0:continue
   for f in range(max(0,a),min(end,b)+1):old[f]|=1<<k
  new=compile_fixed_inputs(rows,end);assert old==new
  assert compile_fixed_inputs(compact_fixed_inputs(new,end),end)==new
 report=dict(passed=True,cases=2000,seed=0x292,run_core_sha256=sha((ROOT/'tools/run_core.py').read_bytes()),scope='Inclusive overlapping intervals,negative starts/buttons,zero-length and clipped endpoints compared against the prior mask compiler; canonical intervals reconstructed exactly.')
 (ROOT/'analysis/campaign_v0292_input_scheduler_report.json').write_text(json.dumps(report,indent=2)+'\n');print('2000 interval cases exact')
if __name__=='__main__':main()
