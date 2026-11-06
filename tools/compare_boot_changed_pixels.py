"""Compare baseline/candidate changed boot pixels to the original SMS frames."""
import argparse
import contextlib
import io
import json
from pathlib import Path

import numpy as np

from archive_lossless_evidence import sha
from run_core import ROOT,run
from summarize_initial_world_candidate06 import indexed_pixels


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--comparison',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--baseline',type=Path,default=ROOT/'versions/v0316-8b94f2e0/gaw-megadrive-v0316.bin');a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'validation');out.mkdir(parents=True,exist_ok=False)
    comparison=json.loads(a.comparison.read_bytes());assert comparison['md_sha256']==sha(a.rom.read_bytes())
    cases=[]
    for case in comparison['cases']:
        region=case['region'];frames=set(case['difference_frames'])
        for tag,rom in [('sms',ROOT/'input/original.sms'),('baseline',a.baseline),('candidate',a.rom)]:
            with contextlib.redirect_stdout(io.StringIO()):run(rom,6500,out/(region+'-'+tag),frames,[],skip_intro=False,
                core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
        records=[]
        for frame in sorted(frames):
            pixels={tag:np.frombuffer(indexed_pixels(out/(region+'-'+tag)/f'frame_{frame:05d}.png','sms'if tag=='sms'else'md'),dtype=np.uint8).reshape(-1,3)for tag in ('sms','baseline','candidate')}
            different=np.any(pixels['baseline']!=pixels['candidate'],axis=1)
            old=np.all(pixels['baseline']==pixels['sms'],axis=1);new=np.all(pixels['candidate']==pixels['sms'],axis=1)
            records.append(dict(frame=frame,changed_viewport_pixels=int(different.sum()),
                                baseline_matches_source=int((different&old).sum()),candidate_matches_source=int((different&new).sum()),
                                neither_matches_source=int((different&~old&~new).sum())))
        cases.append(dict(region=region,frames=records));print(region,records,flush=True)
    result=dict(md_sha256=sha(a.rom.read_bytes()),baseline_sha256=sha(a.baseline.read_bytes()),cases=cases,
                source_sha256=sha((ROOT/'input/original.sms').read_bytes()),comparison_sha256=sha(a.comparison.read_bytes()),
                driver_sha256=sha(Path(__file__).read_bytes()),ram_writes=0,sram_imports=0,
                scope='Only pixels changed from baseline, in the normalized192-line viewport. No whole-source framebuffer equality claim.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
