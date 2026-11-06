"""Observe natural opening and house-entry clocks without modifying either game."""
import argparse,contextlib,io,json
from run_core import ROOT,run
from archive_lossless_evidence import sha
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols


def main():
    p=argparse.ArgumentParser();p.add_argument('--pal',action='store_true');p.add_argument('--house',choices=['first','second'],default='first');p.add_argument('--trial',default='02');a=p.parse_args()
    region='pal'if a.pal else'auto';out=ROOT/'validation/house-entry-clock-v0315'/(a.house+'-'+region+'-'+a.trial);assert not out.exists()
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    route=[(2950,2958,7),(3000,3020,4)]if a.house=='first'else[(2950,2965,5),(3000,3023,6),(3050,3061,4),(3100,3110,4)]
    for tag,rom in [('sms',ROOT/'input/original.sms'),('md',ROOT/'gaw-megadrive.bin')]:
        rows=[]
        def observe(frame,raw):
            if frame<1800:return
            if tag=='sms':
                row=dict(game=raw[0x1d],room=int.from_bytes(raw[0xb9:0xbb],'little'),graphics=raw[0x40],hero=raw[0x301],counter=raw[0x304],x=raw[0x313],y=raw[0x311],clock=raw[0x2f],scan=raw[0xaa],scan_high=raw[0xab])
            else:
                def word(n,size=2):return int.from_bytes(bytes(raw[(sy[n]+i)^1]for i in range(size)),'big')
                row={n:word(symbol)for n,symbol in [('game','game_state'),('room','room_id'),('graphics','world_graphics_class'),('hero','hero_state'),('counter','hero_counter'),('scan','house_animation_scan')]}
                row.update(x=word('hero_x')>>8,y=word('hero_y')>>8,clock=(word('vtimer',4)-word('world_clock_shift',4))&255,clock_shift=word('world_clock_shift',4),door_loading=raw[sy['door_transition_loading']^1],resume_phase=word('resume_phase'))
            rows.append(dict(frame=frame,**row))
        with contextlib.redirect_stdout(io.StringIO()):
            run(rom,3250,out/tag,{2800,3100,3250},([(200,220,0)]if tag=='sms'else[])+PRESSES[:11]+route,ram_observer=observe,core_options={'genesis_plus_gx_region_detect':region})
        (out/tag/'observations.json').write_text(json.dumps(rows,indent=2)+'\n')
    (out/'report.json').write_text(json.dumps(dict(md_sha256=sha((ROOT/'gaw-megadrive.bin').read_bytes()),source_sha256=sha((ROOT/'input/original.sms').read_bytes()),driver_sha256=sha((ROOT/'tools/probe_house_entry_clock.py').read_bytes()),region=region,house=a.house,natural_input_only=True),indent=2)+'\n')
    print('Natural house entry clocks recorded',a.house,region,flush=True)


if __name__=='__main__':main()
