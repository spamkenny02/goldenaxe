"""Compare natural name cursor, repeat state and queued/accepted sound effects."""
import argparse
import contextlib
import io
import json
from pathlib import Path

from archive_lossless_evidence import sha
from run_core import ROOT,run
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--symbols',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--pal',action='store_true');a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'validation');out.mkdir(parents=True,exist_ok=False);sy=symbols(a.symbols)
    result={}
    for tag,rom in [('sms',ROOT/'input/original.sms'),('md',a.rom)]:
        rows=[]
        def observe(frame,raw):
            if frame<1100:return
            if tag=='sms':
                audio=raw[0x1e00:0x1f90];cursor=raw[0xa0];position=raw[0x1120]//2
                pending=audio[8];repeat=raw[0x1122]
            else:
                def data(name,size):return bytes(raw[(sy[name]+i)^1]for i in range(size))
                def word(name):return int.from_bytes(data(name,2),'big')
                audio=data('sound_ram',400);cursor=word('name_cursor');position=word('name_position');pending=word('sound_effect_request');repeat=None
                assert not word('sound_unhandled_command')
            rows.append(dict(frame=frame,cursor=cursor,position=position,pending=pending,repeat=repeat,
                             accepted=audio[15],effects=audio[256:400].hex()))
        folder=out/tag
        with contextlib.redirect_stdout(io.StringIO()):run(rom,1500,folder,set(),[(200,220,0)]+PRESSES[:6],
            skip_intro=False,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':'pal'if a.pal else'auto'})
        (folder/'observations.json').write_text(json.dumps(rows,indent=2)+'\n');result[tag]=rows
    differences=[]
    for s,m in zip(result['sms'],result['md']):
        if s['frame']>1450:continue
        bad={key:[s[key],m[key]]for key in ('cursor','position','pending','accepted')if s[key]!=m[key]}
        if bad:differences.append(dict(frame=s['frame'],fields=bad))
    report=dict(md_sha256=sha(a.rom.read_bytes()),region='pal'if a.pal else'ntsc',differences=differences,
                driver_sha256=sha(Path(__file__).read_bytes()),ram_writes=0,sram_imports=0)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Name controller differences:',len(differences),differences[:10],flush=True)


if __name__=='__main__':main()
