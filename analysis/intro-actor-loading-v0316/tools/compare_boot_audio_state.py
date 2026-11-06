"""Compare natural boot audio reader/PSG state without RAM injections."""
import argparse
import contextlib
import hashlib
import io
import json
import re
import struct
from pathlib import Path
from archive_lossless_evidence import sha
from run_core import ROOT,run

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    project=a.project.resolve();out=a.out.resolve();assert project.is_relative_to(ROOT/'validation') and out.is_relative_to(ROOT/'validation')
    out.mkdir(exist_ok=False);core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_libretro.dll';cases=[]
    for region in ('ntsc','pal'):
        records={}
        for tag,rom,symbols in [('baseline',ROOT/'gaw-megadrive.bin',ROOT/'megadrive/out/release/symbol.txt'),('candidate',project/'out/release/rom.bin',project/'out/release/symbol.txt')]:
            sy={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in symbols.read_text().splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
            rows=[];psg=[]
            def observe(frame,raw):
                def data(name,size):return bytes(raw[(sy[name]+i)^1]for i in range(size))
                assert data('sound_unhandled_command',2)==b'\0\0'
                rows.append(data('sound_ram',400)+data('sound_effect_request',2))
            with contextlib.redirect_stdout(io.StringIO()):
                run(rom,6500,out/(region+'-'+tag),set(),[],skip_intro=False,core=core,ram_observer=observe,
                    psg_observer=lambda frame,regs:psg.append(struct.pack('<8H',*regs)),core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
            assert len(rows)==len(psg)==6500
            records[tag]=(rows,psg)
        state_diffs=[n+1 for n,(s,m)in enumerate(zip(records['baseline'][0],records['candidate'][0]))if s!=m]
        psg_diffs=[n+1 for n,(s,m)in enumerate(zip(records['baseline'][1],records['candidate'][1]))if s!=m]
        cases.append(dict(region=region,state_difference_frames=state_diffs,psg_difference_frames=psg_diffs,
            state_sha256={k:sha(b''.join(v[0]))for k,v in records.items()},psg_sha256={k:sha(b''.join(v[1]))for k,v in records.items()}))
        print(region,'audio-state differences',len(state_diffs),'PSG differences',len(psg_diffs),flush=True)
    result=dict(passed=all(not r['state_difference_frames']and not r['psg_difference_frames']for r in cases),cases=cases,
        baseline_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),md_sha256=sha((project/'out/release/rom.bin').read_bytes()),
        core_sha256=sha(core.read_bytes()),driver_sha256=sha(Path(__file__).read_bytes()),frames_per_region=6500,ram_writes=0,sram_imports=0,
        scope='Every frame:400 sound reader bytes, pending effect request and8 PSG registers. Baseline equivalence only; no PCM or original SMS audio fidelity claim.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
