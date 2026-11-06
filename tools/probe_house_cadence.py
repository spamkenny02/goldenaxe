"""Measure natural indoor NPC and bitmap cadence without aligning clocks."""
import argparse,contextlib,io,json
from archive_lossless_evidence import sha
from audit_item_reward_visuals import sms_pixels,md_pixels
from run_core import ROOT,run
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols


def main():
    p=argparse.ArgumentParser();p.add_argument('--house',choices=['first','second'],default='first');p.add_argument('--pal',action='store_true');p.add_argument('--menu',action='store_true');p.add_argument('--trial',default='02');a=p.parse_args()
    region='pal'if a.pal else'auto';tag=a.house+'-'+region+('-menu'if a.menu else'-idle')+'-'+a.trial
    out=ROOT/'validation/house-cadence-v0315'/tag;assert not out.exists()
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    route=[(2950,2958,7),(3000,3020,4)]if a.house=='first'else[(2950,2965,5),(3000,3023,6),(3050,3061,4),(3100,3110,4)]
    inputs=PRESSES[:11]+route+([(3350,3355,0),(3400,3405,0)]if a.menu else[])
    results={}
    for system,rom in [('sms',ROOT/'input/original.sms'),('md',ROOT/'gaw-megadrive.bin')]:
        rows=[];current=None;cells=None
        def observe(frame,raw):
            nonlocal current,cells
            if frame<3200:return
            if system=='sms':
                state=raw[0x1d];room=int.from_bytes(raw[0xb9:0xbb],'little');clock=raw[0x2f];scan=raw[0xaa];tile=raw[0x9e0];meta=raw[0x1c00:0x1ca0]
            else:
                def word(n,size=2):return int.from_bytes(bytes(raw[(sy[n]+i)^1]for i in range(size)),'big')
                state=word('game_state');room=word('room_id');clock=(word('vtimer',4)-word('world_clock_shift',4))&255;scan=word('house_animation_scan');tile=raw[(sy['scratch']+0xe0)^1];meta=bytes(raw[(sy['scratch']+0x800+i)^1]for i in range(160))
            if cells is None and state==12:cells=[i for i,value in enumerate(meta)if 0x24<=value<0x30]
            current=dict(frame=frame,game=state,room=room,clock=clock,scan=scan,tile=tile,cells={str(i):meta[i]for i in cells or[]})
            rows.append(current)
        def video(frame,vram):
            if current is None:return
            tile=current['tile'];pixels=bytes(value for n in range(4)for value in (sms_pixels(vram,tile+n)if system=='sms'else md_pixels(vram,tile+n+16)))
            current['bitmap_sha256']=sha(pixels)
            words={}
            for i in cells or[]:
                x=(i%16)*2;y=(i//16)*2;entry=[]
                for dy,dx in [(0,0),(0,1),(1,0),(1,1)]:
                    at=0x3800+(y+dy)*64+(x+dx)*2 if system=='sms'else 0xe000+(y+dy+2)*128+(x+dx)*2
                    word=int.from_bytes(vram[at:at+2],'little');entry.append(word&511 if system=='sms'else(word&2047)-16)
                words[str(i)]=entry
            current['physical_npc_tiles']=words
        folder=out/system
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom,4000,folder,{3300,3500,4000},([(200,220,0)]if system=='sms'else[])+inputs,ram_observer=observe,vram_observer=video,core_options={'genesis_plus_gx_region_detect':region})
        assert rows and all(row['room']==(0 if a.house=='first'else 2)for row in rows)
        (folder/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
        results[system]=dict(frames=len(rows),bitmap_states=len({r['bitmap_sha256']for r in rows}),npc_cells=cells,first=rows[0],last=rows[-1])
    (out/'report.json').write_text(json.dumps(dict(md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),natural_input_only=True,region=region,house=a.house,menu=a.menu,driver_sha256=sha((ROOT/'tools/probe_house_cadence.py').read_bytes()),results=results),indent=2)+'\n')
    print('Natural house cadence recorded',tag,flush=True)


if __name__=='__main__':main()
