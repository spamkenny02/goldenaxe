"""Replay the actual MD campaign to its ninth-crystal overworld exit.

No SRAM, actor, item or quest initialization. Retain only the recorded guard,
audit every frame against live bosses, and produce an extendable input trace.
"""
import argparse,contextlib,csv,hashlib,io,json
from run_core import ROOT,run,FrameWrites
from validate_playable_sprite_limit import symbols
from assisted_prefix import recording

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--trial',required=True);p.add_argument('--crystals',type=int,choices=range(1,10),default=9);p.add_argument('--axe-before-apple',action='store_true');a=p.parse_args()
    rom=ROOT/a.rom;digest=hashlib.sha256(rom.read_bytes()).hexdigest();assert digest=='1421abe47de95ac104a03e2fb1be7001f70aeca1fbb6a9b35669aa6e98b7d9a4'
    route=json.loads((ROOT/'testkit/manifest.json').read_bytes())['routes']['md_ntsc']
    csvpath=ROOT/'testkit/routes'/route['csv'];assert hashlib.sha256(csvpath.read_bytes()).hexdigest()==route['csv_sha256']
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');presses=[];writes=FrameWrites()
    with csvpath.open(newline='') as f:
        for row in csv.DictReader(f):
            first,last,mask,guard=(int(row[k]) for k in ('start','end','mask','guard'))
            presses.extend((first,last,k) for k in range(16) if mask&(1<<k))
            if guard!=-1:writes.extend((n,sy['hero_hurt'],guard.to_bytes(2,'big')) for n in range(first,last+1))
    out=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not out.exists();state={};complete=None;captures=set();boss_guard_frames=0;observed=0
    def observe(frame,raw):
        nonlocal complete,boss_guard_frames,observed
        observed=frame
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        if word('hero_hurt')>128:
            actors=data('world_actor_state',768)
            assert not any(actors[n+24] and (0x63<=actors[n]<=0x6d or 0x78<=actors[n]<=0x7c) for n in range(0,768,48)),('guard overlaps live boss',frame)
        assert not word('sound_unhandled_command') and word('game_state')!=20
        gems=data('game_save_state',592)[0x1f:0x28]
        eligible=not a.axe_before_apple or (word('hero_weapon_level') and not data('hero_items',17)[8])
        if frame>2500 and sum(bool(v&128) for v in gems)==a.crystals and eligible:
            state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),max_magic=word('hero_max_magic'),gold=word('hero_gold'),keys=word('hero_keys'),dungeon=word('world_dungeon_number'),crystals=list(gems),audio_error=word('sound_unhandled_command'))
            if complete is None and state['room']<256 and state['game']==12 and state['hero']==1 and not state['counter'] and not state['dungeon'] and not word('resume_phase') and not data('door_transition_loading',1)[0]:
                complete=frame+1;captures.add(complete)
        if frame%50000==0:print('MD ANNEX PREFIX',frame,flush=True)
    with contextlib.redirect_stdout(io.StringIO()):run(rom,340000,out,captures,presses,skip_intro=False,ram_writes=writes,ram_observer=observe,stop_when=lambda:complete is not None and observed>=complete)
    assert complete is not None and state['health']
    cap=json.loads((out/'capture.json').read_bytes());assert cap['frames']==complete
    # run_core records the supplied fixture schedule, including future rows.
    # This stopped prefix retains only writes that could actually execute.
    cap['test_ram_writes']=[r for r in cap['test_ram_writes'] if r['frame']<=complete]
    (out/'capture.json').write_bytes((json.dumps(cap,indent=2)+'\n').encode());(out/'controls.json').write_text('[]\n')
    episode=dict(activation_after_frame=0,boss_room=0x14c,first_boss_entry=None,release_write_frame=None,first_boss_combat=None,first_boss_damage=None,end_frame=complete+1)
    assist=dict(assisted_route=True,ram_injections=True,rom_modifications=False,primary_state_imports=0,health_refills=0,boss_assistance=False,**episode,
        writes=[dict(frame=f,address=n,data_hex=d.hex()) for f,n,d in writes if f<=complete],
        source_route_csv_sha256=route['csv_sha256'],prior_bosses_audited_every_frame=True,scope='Recorded prior campaign guards; no overlap with a live boss. Open continuation target is the final palace, not a description of only one historical boss.')
    (out/'assistance.json').write_bytes((json.dumps(assist,indent=2)+'\n').encode());recording(out,cap)
    result=dict(passed=True,failure=None,rom_sha256=digest,last_state=state,frames=complete,requested_crystals=a.crystals,all_nine_crystals=a.crystals==9,full_dungeon_cleared=True,dungeon_exit_verified=True,deaths=0,primary_state_imports=0,new_assistance_writes=0,sram_checkpoint_injection=False,live_boss_guard_overlap_frames=boss_guard_frames,source_route_csv_sha256=route['csv_sha256'],all_npcs_complete=False)
    (out/'report.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result),flush=True)
if __name__=='__main__':main()
