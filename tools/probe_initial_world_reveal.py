"""Capture natural story closing, initial loading and world reveal on both systems."""
import argparse,contextlib,io,json,shutil
from pathlib import Path
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--symbols',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--pal',action='store_true');p.add_argument('--last-ack',type=int,default=2400);a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'validation') and not out.exists();out.mkdir(parents=True)
    shutil.copyfile(Path(__file__),out/'driver.py')
    sy=symbols(a.symbols);region='pal'if a.pal else'auto';results={}
    inputs=[row if row[0]!=2400 else(a.last_ack,a.last_ack+10,row[2])for row in PRESSES[:8]]
    end=max(2650,a.last_ack+250);start=2380 if a.last_ack==2400 else a.last_ack-20
    for tag,rom in [('sms',ROOT/'input/original.sms'),('md',a.rom)]:
        rows=[];current=None
        def observe(frame,raw):
            nonlocal current
            if frame<start:return
            if tag=='sms':
                row=dict(game=raw[0x1d],room=int.from_bytes(raw[0xb9:0xbb],'little'),hero=raw[0x301],clock=raw[0x2f],x=raw[0x313],y=raw[0x311])
            else:
                def word(n,size=2):return int.from_bytes(bytes(raw[(sy[n]+i)^1]for i in range(size)),'big')
                row=dict(game=word('game_state'),room=word('room_id'),hero=word('hero_state'),clock=(word('vtimer',4)-word('world_clock_shift',4))&255,x=word('hero_x')>>8,y=word('hero_y')>>8,phase=word('resume_phase'),contour=word('resume_contour'),fade_step=word('resume_fade_step'))
            current=dict(frame=frame,**row);rows.append(current)
        def vram(frame,raw):
            if current is None:return
            bits=[]
            for y in range(24):
                for x in range(32):
                    at=0x3800+y*64+x*2 if tag=='sms'else 0xe000+(y+2)*128+x*2
                    word=int.from_bytes(raw[at:at+2],'little');tile=word&511 if tag=='sms'else(word&2047)-16;bits.append(tile!=255)
            current['nonblank_cells']=sum(bits)
            current['occupancy_hex']=bytes(sum(int(bits[i+n])<<n for n in range(8))for i in range(0,768,8)).hex()
        folder=out/tag
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom,end,folder,set(range(start,start+181))|{end},([(200,220,0)]if tag=='sms'else[])+inputs,ram_observer=observe,vram_observer=vram,core_options={'genesis_plus_gx_region_detect':region})
        cap=json.loads((folder/'capture.json').read_bytes());assert not cap['test_ram_writes'] and cap['sram_input']is None
        (folder/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
        initial=next(row for row in rows if row['room']==0x95 and row['game']==12)
        ready=next(row for row in rows if row['room']==0x95 and row['game']==12 and row['hero']==1)
        results[tag]=dict(rom_sha256=cap['rom_sha256'],first_state12=initial['frame'],first_hero_ready=ready['frame'],final=rows[-1])
    result=dict(region=region,last_ack=a.last_ack,natural_input_only=True,results=results,driver_sha256=sha(Path(__file__).read_bytes()),scope='Natural closing story and first world only. State12/hero readiness,physical tile occupancy and frame captures;global source clock and full gameplay remain separate.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print({k:{n:v for n,v in r.items()if n!='final'}for k,r in results.items()},flush=True)


if __name__=='__main__':main()
