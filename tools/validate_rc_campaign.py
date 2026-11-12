"""Replay a fixed MD regression route on the layout-preserving RC, from boot."""
import argparse,csv,hashlib,json,time
from run_core import ROOT,run,FrameWrites
from validate_playable_sprite_limit import symbols


def main():
    p=argparse.ArgumentParser();p.add_argument('--region',choices=['ntsc','pal'],required=True);p.add_argument('--rom',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    rom=ROOT/a.rom;digest=hashlib.sha256(rom.read_bytes()).hexdigest();assert digest=='1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'
    manifest=json.loads((ROOT/'testkit/manifest.json').read_bytes());route=manifest['routes']['md_'+a.region]
    csvpath=ROOT/'testkit/routes'/route['csv'];assert hashlib.sha256(csvpath.read_bytes()).hexdigest()==route['csv_sha256']
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');presses=[];writes=FrameWrites();end=route['frames']
    with csvpath.open(newline='') as stream:
        for row in csv.DictReader(stream):
            first,last,mask,guard=(int(row[k]) for k in ('start','end','mask','guard'))
            presses.extend((first,last,k) for k in range(16) if mask&(1<<k))
            if guard!=-1:writes.extend((f,sy['hero_hurt'],guard.to_bytes(2,'big')) for f in range(first,last+1))
    out=ROOT/a.out;assert out.resolve().is_relative_to(ROOT/'validation') and not out.exists()
    ending=False;state={};rooms=set();overlaps=[];deaths=0;previous_game=None;started=time.monotonic()
    def observe(frame,raw):
        nonlocal ending,deaths,previous_game
        word=lambda n:raw[sy[n]]|(raw[sy[n]+1]<<8)
        game=word('game_state');room=word('room_id');rooms.add(room)
        crystals=sum(bool(raw[(sy['game_save_state']+0x1f+n)^1]&128) for n in range(9))
        state.update(game=game,room=room,health=word('hero_health'),crystals=crystals,audio_error=word('sound_unhandled_command'))
        assert state['audio_error']==0,(frame,'audio error')
        if game==20 and previous_game!=20:deaths+=1
        previous_game=game;ending|=game==14
        if word('hero_hurt')>128:
            for n in range(16):
                at=sy['world_actor_state']+n*48;kind=raw[at^1];hp=raw[(at+24)^1]
                if hp and (0x63<=kind<=0x6d or 0x78<=kind<=0x7c):overlaps.append(dict(frame=frame,room=room,kind=kind,hp=hp))
        if frame%50000==0:print('RC CAMPAIGN',a.region,frame,end,state,flush=True)
    run(rom,end,out,{end},presses,skip_intro=False,ram_writes=writes,ram_observer=observe,
        core_options={'genesis_plus_gx_region_detect':'pal' if a.region=='pal' else 'auto'})
    passed=ending and not deaths and not overlaps and all(state[k]==v for k,v in route['expected_final'].items())
    result=dict(passed=passed,md_sha256=digest,region=a.region,frames=end,ending_seen=ending,final=state,
        normal_deaths=deaths,approach_guard_writes=len(writes),live_boss_guard_overlap_frames=len({v['frame'] for v in overlaps}),
        overlap_examples=overlaps[:20],boss_assistance=bool(overlaps),sram_imports=0,
        route_csv_sha256=route['csv_sha256'],visited_rooms=sorted(rooms),seconds=time.monotonic()-started,
        final_ram_sha256=hashlib.sha256((out/f'ram_{end:05d}.bin').read_bytes()).hexdigest(),
        scope='Actual fixed controller campaign to ending on RC. Only recorded approach guard; live boss guard audited. No inventory, actor, HP, quest or SRAM fixtures. Not every NPC/side branch or hardware fidelity.')
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
    if not passed:raise SystemExit(1)


if __name__=='__main__':main()
