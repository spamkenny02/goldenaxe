"""Cold-replay a shorter alive combat prefix; never load captured game state."""
import argparse,contextlib,io,json
from pathlib import Path
from run_core import ROOT,run,FrameWrites
from archive_lossless_evidence import sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols


def main():
    p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--frame',type=int,required=True);p.add_argument('--trial',required=True);a=p.parse_args()
    source=(ROOT/'validation'/a.trace).resolve();assert source.is_relative_to(ROOT/'validation')
    c=json.loads((source/'capture.json').read_bytes());controls=json.loads((source/'controls.json').read_bytes());assist,writes=recording(source,c)
    rom=ROOT/'gaw-megadrive.bin';assert sha(rom.read_bytes())==c['rom_sha256'] and c['sram_input'] is None
    end=a.frame;assert 0<end<c['frames'] and assist['first_boss_combat']['frame']<end
    expected={stem:(source/f'{stem}_{end:05d}.{ext}').read_bytes() for stem,ext in [('ram','bin'),('frame','png')]}
    folder=(ROOT/'validation/natural-dungeon-combat'/a.trial).resolve();assert folder.is_relative_to(ROOT/'validation/natural-dungeon-combat') and not folder.exists()
    controls=[row for row in controls if row['frame']<=end]
    presses=[(begin,min(stop,end),button) for begin,stop,button in c['presses'] if begin<=end]
    for i,row in enumerate(controls):
        stop=min(end,controls[i+1]['frame']-1 if i+1<len(controls) else end)
        presses.extend((row['frame'],stop,button) for button in row['buttons'])
    actual_writes=[row for row in writes if row[0]<=end]
    assert actual_writes and actual_writes[-1][0]==assist['release_write_frame']
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom,end,folder,{end},presses,skip_intro=False,ram_writes=FrameWrites(actual_writes),core_options=c['core_options'])
    for stem,ext in [('ram','bin'),('frame','png')]:assert (folder/f'{stem}_{end:05d}.{ext}').read_bytes()==expected[stem]
    # The flattened fixed inputs are now capture.presses. Keep a normalized
    # empty feedback timeline so no old/future controller actions are replayed.
    (folder/'controls.json').write_text('[]\n')
    assist=json.loads(json.dumps(assist));assist['episodes'][-1]['end_frame']=end+1
    assist['writes']=[dict(frame=f,address=address,data_hex=value.hex()) for f,address,value in actual_writes]
    assist['prefix_clip']=dict(source=a.trace,source_capture_sha256=sha((source/'capture.json').read_bytes()),frame=end,whole_ram_png_match=True,primary_state_imports=0)
    for key in ['first_boss_entry','first_boss_combat','first_boss_damage']:
        if assist[key] is not None:assert assist[key]['frame']<=end
    (folder/'assistance.json').write_text(json.dumps(assist,indent=2)+'\n')
    recording(folder,json.loads((folder/'capture.json').read_bytes()))
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');raw=expected['ram']
    data=lambda name,n:bytes(raw[(sy[name]+i)^1] for i in range(n));word=lambda name:int.from_bytes(data(name,2),'big')
    assert word('game_state')==12 and word('hero_health')>0 and word('room_id')==assist['boss_room']
    actors=data('world_actor_state',768)
    state=dict(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),health=word('hero_health'),max_health=word('hero_max_health'),x=word('hero_x')>>8,y=word('hero_y')>>8,hurt=word('hero_hurt'),boss_hp=actors[24])
    report=dict(passed=True,rom_sha256=c['rom_sha256'],source_trace=a.trace,source_frame=end,frames=end,
                combat_prefix_only=True,room_cleared=False,full_dungeon_cleared=False,failure=None,deaths=0,last_state=state,
                assisted_route=True,boss_assistance=False,ram_injections=True,primary_state_imports=0,health_refills=0,
                source_whole_ram_png_exact=True,independent_canonical_replay_required=True,
                driver_sha256=sha(Path(__file__).read_bytes()),
                limits=['Stops before a later failure in the diagnostic source. Every retained input and logged approach write is executed from boot; captured RAM/PNG are compared only,never imported.','This is an alive partial combat prefix,not a boss victory or a healing fixture. A separate canonical replay is required before continuation.'])
    (folder/'clip_driver.py').write_bytes(Path(__file__).read_bytes())
    (folder/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)


if __name__=='__main__':main()
