"""Compare original/native attract audio state and PSG, preserving raw differences."""
import argparse
import contextlib
import io
import json
import re
import struct
from pathlib import Path
from archive_lossless_evidence import sha
from run_core import ROOT,run

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--frames',type=int,default=14000);a=p.parse_args();project=a.project.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
    sy={m[2].split('.lto_priv.')[0]:int(m[1],16)&65535 for line in(project/'out/release/symbol.txt').read_text().splitlines()if(m:=re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)',line))}
    core=ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_libretro.dll';cases=[]
    for region in('ntsc','pal'):
        systems={}
        for tag,rom in [('sms',ROOT/'input/original.sms'),('md',project/'out/release/rom.bin')]:
            raw_states=[];states=[];psg=[];queued=[]
            def observe(frame,raw):
                if tag=='sms':record=raw[0x1e00:0x1f90];logical=record
                else:
                    def data(name,size):return bytes(raw[(sy[name]+i)^1]for i in range(size))
                    def word(name):return int.from_bytes(data(name,2),'big')
                    assert not word('sound_unhandled_command'),(region,frame)
                    record=data('sound_ram',400);logical=bytearray(record);track=word('sound_request');delay=word('sound_request_delay');effect=word('sound_effect_request')
                    if track and not delay:logical[6]=track
                    if effect:logical[8]=effect
                    queued.append(dict(frame=frame,track=track,delay=delay,effect=effect))
                raw_states.append(record);states.append(bytes(logical))
            folder=out/(region+'-'+tag)
            with contextlib.redirect_stdout(io.StringIO()):run(rom,a.frames,folder,set(),[],skip_intro=False,core=core,ram_observer=observe,psg_observer=lambda frame,regs:psg.append(tuple(regs)),core_options={'genesis_plus_gx_region_detect':'pal'if region=='pal'else'auto'})
            assert len(states)==len(psg)==a.frames
            (folder/'raw-audio.bin').write_bytes(b''.join(raw_states));(folder/'logical-audio.bin').write_bytes(b''.join(states));(folder/'psg.bin').write_bytes(b''.join(struct.pack('<8i',*r)for r in psg))
            if queued:(folder/'queued-requests.json').write_text(json.dumps(queued,indent=2)+'\n')
            systems[tag]=(raw_states,states,psg)
        differences=[];raw_differences=[];psg_differences=[]
        for frame in range(23,a.frames+1):
            for index,target in[(0,raw_differences),(1,differences)]:
                s=systems['sms'][index][frame-1];m=systems['md'][index][frame-1]
                if s!=m:target.append(dict(frame=frame,indices=[i for i,(x,y)in enumerate(zip(s,m))if x!=y]))
            if systems['sms'][2][frame-1]!=systems['md'][2][frame-1]:psg_differences.append(frame)
        cases.append(dict(region=region,first_frame=23,last_frame=a.frames,raw_state_differences=raw_differences,logical_state_differences=differences,psg_difference_frames=psg_differences))
        print(region,'logical audio differences',len(differences),'PSG differences',len(psg_differences),'examples',differences[:2],flush=True)
    (out/'report.json').write_text(json.dumps(dict(passed=all(not r['logical_state_differences']and not r['psg_difference_frames']for r in cases),cases=cases,md_sha256=sha((project/'out/release/rom.bin').read_bytes()),source_sha256=sha((ROOT/'input/original.sms').read_bytes()),core_sha256=sha(core.read_bytes()),driver_sha256=sha(Path(__file__).read_bytes()),normalization='Pending native foreground requests supply source DE06/DE08 before IRQ acceptance; raw bytes retained separately.',scope='Frames23..end of cold no-input attract loops:400 reader bytes and8 PSG registers. Initial silent startup, PCM and physical hardware are not certified.'),indent=2)+'\n')

if __name__=='__main__':main()
