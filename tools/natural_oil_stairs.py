"""Continue a real C7->1F approach through both stairs, oil gift and house exit."""
import argparse
import contextlib
import io
import json
from pathlib import Path
from run_core import ROOT, run
from natural_dungeon_combat import walk
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True)
    a=p.parse_args();source=ROOT/'validation/natural-dungeon-route'/a.prefix
    driver=Path(__file__).read_bytes()
    c=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and prior['failure'] is None and prior['house_outside']==0xc7 and prior['house_target']==0x1f
    assert not c['test_ram_writes'] and c['sram_input'] is None
    proof=source.with_name(source.name+'-fixed-replay')/'replay_report.json'
    assert json.loads(proof.read_bytes())['passed']
    rom=ROOT/'gaw-megadrive.bin';assert sha(rom.read_bytes())==c['rom_sha256']
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');start=c['frames']
    controls=json.loads((source/'controls.json').read_bytes());timeline=[()]*(start+1)
    for i,row in enumerate(controls):
        end=controls[i+1]['frame']-1 if i+1<len(controls) else start
        timeline[row['frame']:end+1]=[tuple(row['buttons'])]*(end-row['frame']+1)
    folder=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not folder.exists()
    state={};events=[];captures={start};first=done=failure=previous=None;observed=0;tilemap=b'';last_direction=0

    def observe(f,raw):
        nonlocal first,done,failure,previous,observed,tilemap
        observed=f
        if f<start:return
        data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
        word=lambda n:int.from_bytes(data(n,2),'big')
        tilemap=data('sms_vram',16384)[0x3800:0x3e00]
        state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),
                     x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),gold=word('hero_gold'),
                     magic=word('hero_magic'),oil=data('hero_items',17)[8],outside=word('house_return_room'),
                     flags=data('game_save_state',592)[0x117],modal=word('house_dialogue_active'),
                     audio_error=word('sound_unhandled_command'))
        if first is None:
            first=dict(state);assert first['room']==0x1f and first['outside']==0xc7 and not first['oil'] and first['health']>0
        if state['outside']!=0xc7:failure='outside_context_changed'
        if not state['health'] or state['game']==20:failure='hero_died'
        if state['audio_error']:failure='native_audio_error'
        key=tuple(state[n] for n in ['room','game','oil','flags','modal'])
        if key!=previous:events.append(dict(frame=f,**state));captures.add(f+1);previous=key
        if state['room']==0xc7 and state['game']==12 and state['hero']==1 and state['oil'] and state['flags']&2 and done is None:
            done=f;captures.add(f+100)

    def choose(f):
        nonlocal last_direction
        if f<=start:return list(timeline[f])
        if failure or done is not None:return []
        if state.get('modal') or state.get('game')==22:return [8] if f%40==0 else []
        if state.get('game')!=12 or state.get('hero')!=1:return []
        if state['counter']:return [4+last_direction]
        point=state['x'],state['y']
        if not state['oil']:
            goal=(104,24) if state['room']==0x1f else (104,56);direction=0
            if state['room']==0x1f and point[0]==104 and point[1]<=24:
                last_direction=0;return [4]
        else:
            goal=(104,152) if state['room']==0xf else (136,152);direction=1
            if point[0]==goal[0] and point[1]>=152:
                last_direction=1;return [5]
        if point==goal:last_direction=direction;return [4+last_direction]
        path=walk(tilemap,point,lambda q:q==goal)
        if path:last_direction=path[0];return [4+last_direction]
        return []

    def controller(f):
        value=choose(f)
        if f>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=f,buttons=list(value)))
        return value

    with contextlib.redirect_stdout(io.StringIO()):
        run(rom,start+5000,folder,captures,c['presses'],skip_intro=False,input_provider=controller,ram_observer=observe,
            stop_when=lambda:bool(failure) or done is not None and observed>=done+100,core_options=c['core_options'])
    visited=list(dict.fromkeys(e['room'] for e in events))
    passed=done is not None and not failure and 0xf in visited and state['gold']==first['gold'] and state['magic']==first['magic']
    result=dict(passed=passed,failure=failure or (None if passed else 'frame_limit'),rom_sha256=c['rom_sha256'],
                source_prefix=a.prefix,first_state=first,last_state=state,visited=visited,complete_frame=done,
                ram_injections=False,sram_checkpoint_injection=False,primary_state_imports=0,
                source_route_replay_sha256=sha(proof.read_bytes()),driver_sha256=sha(driver),
                scope='Normal boot and recorded approach,real C7 doorway,both indoor stairs,oil gift and exterior exit. No RAM/SRAM fixture or actor mutation.')
    for name,value in [('report',result),('events',events),('controls',controls)]:
        (folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
    (folder/'oil_stairs_driver.py').write_bytes(driver)
    print(result)


if __name__=='__main__':main()
