"""C7/55->1F/0F golden-apple/magic-oil gift and exit.

The legacy state key 'oil' means inventory slot8, actually the GOLDEN APPLE.
Original reward item12 label at BBEB confirms it; magic oil is item6/slot2.
"""
import argparse
import contextlib
import io
import json
from pathlib import Path
from run_core import ROOT, run, FrameWrites
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--sms',action='store_true');p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True);p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--outside',type=lambda v:int(v,0),default=0xc7)
    p.add_argument('--rom');a=p.parse_args();assert a.outside in (0xc7,0x55);inventory_offset=8 if a.outside==0xc7 else 2;source=ROOT/'validation/natural-dungeon-route'/a.prefix
    driver=Path(__file__).read_bytes()
    c=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and prior['failure'] is None and prior['house_outside']==a.outside and prior['house_target']==0x1f
    assert c['sram_input'] is None
    writes=prefix_writes(source,c,a.assisted_prefix)
    proof=source.with_name(source.name+(f"-assisted-fixed-replay-{c['frames']}" if writes else '-fixed-replay'))/'replay_report.json'
    assert json.loads(proof.read_bytes())['passed']
    rom=ROOT/'input/original.sms' if a.sms else ROOT/(a.rom or 'gaw-megadrive.bin');assert sha(rom.read_bytes())==c['rom_sha256']
    sy=symbols(ROOT/'megadrive/out/release/symbol.txt');start=c['frames']
    controls=json.loads((source/'controls.json').read_bytes());timeline=[()]*(start+1)
    for i,row in enumerate(controls):
        end=controls[i+1]['frame']-1 if i+1<len(controls) else start
        timeline[row['frame']:end+1]=[tuple(row['buttons'])]*(end-row['frame']+1)
    folder=ROOT/'validation/natural-service-route'/(('sms-' if a.sms else 'md-')+a.trial);assert not folder.exists()
    state={};events=[];captures={start};first=done=failure=previous=None;observed=0;tilemap=b'';last_direction=0

    def observe(f,raw):
        nonlocal first,done,failure,previous,observed,tilemap
        observed=f
        if f<start:return
        if a.sms:
            tilemap=raw[0x1600:0x1c00]
            state.update(room=int.from_bytes(raw[0xb9:0xbb],'little'),game=raw[0x1d],hero=raw[0x301],counter=raw[0x304],x=raw[0x313],y=raw[0x311],health=raw[0x318],gold=raw[0xdd],magic=raw[0xdb],oil=raw[0xe0+inventory_offset],outside=raw[0xbb],flags=raw[0x100+a.outside],modal=raw[0x1d]==22,audio_error=0)
        else:
            data=lambda n,k:bytes(raw[(sy[n]+i)^1] for i in range(k))
            word=lambda n:int.from_bytes(data(n,2),'big')
            tilemap=data('sms_vram',16384)[0x3800:0x3e00]
            state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),
                         x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),gold=word('hero_gold'),
                         magic=word('hero_magic'),oil=data('hero_items',17)[inventory_offset],outside=word('house_return_room'),
                         flags=data('game_save_state',592)[0x50+a.outside],modal=word('house_dialogue_active'),
                         audio_error=word('sound_unhandled_command'))
        if first is None:
            first=dict(state);assert first['room']==0x1f and first['outside']==a.outside and not first['oil'] and first['health']>0
        if state['outside']!=a.outside:failure='outside_context_changed'
        if not state['health'] or state['game']==20:failure='hero_died'
        if state['audio_error']:failure='native_audio_error'
        key=tuple(state[n] for n in ['room','game','oil','flags','modal'])
        if key!=previous:events.append(dict(frame=f,**state));captures.add(f+1);previous=key
        if state['room']==a.outside and state['game']==12 and state['hero']==1 and state['oil'] and state['flags']&2 and done is None:
            done=f;captures.add(f+100)

    def choose(f):
        nonlocal last_direction
        if f<=start:return list(timeline[f])
        if failure or done is not None:return []
        if state.get('modal') or state.get('game')==22:return [8] if f%40==0 else []
        # The SMS reward waits for acknowledgment while game remains 12;
        # it does not expose the MD house_dialogue_active host flag.
        if a.sms and state.get('oil') and state.get('room')==0xf and (state.get('x'),state.get('y'))==(104,56):
            last_direction=1
            return [5,8] if f%40==0 else [5]
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
            stop_when=lambda:bool(failure) or done is not None and observed>=done+100,core_options=c['core_options'],ram_writes=FrameWrites(writes))
    visited=list(dict.fromkeys(e['room'] for e in events))
    passed=done is not None and not failure and 0xf in visited and state['gold']==first['gold'] and state['magic']==first['magic']
    result=dict(outside=a.outside,inventory_offset=inventory_offset,passed=passed,failure=failure or (None if passed else 'frame_limit'),rom_sha256=c['rom_sha256'],
                source_prefix=a.prefix,first_state=first,last_state=state,visited=visited,complete_frame=done,
                ram_injections=bool(writes),assisted_route=bool(writes),new_assistance_writes=0,sram_checkpoint_injection=False,primary_state_imports=0,
                source_route_replay_sha256=sha(proof.read_bytes()),driver_sha256=sha(driver),
                reward_name='golden_apple' if inventory_offset==8 else 'magic_oil',reward_inventory_offset=inventory_offset,legacy_state_key='oil',
                scope='Normal recorded approach, actual doorway, both indoor stairs, specified consumable gift and exterior exit. Inherited approach aid only; no new resource or progression writes.')
    for name,value in [('report',result),('events',events),('controls',controls)]:
        (folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
    if writes:
        assist=json.loads((source/'assistance.json').read_bytes())
        assist['writes']=[dict(frame=f,address=address,data_hex=value.hex())for f,address,value in writes]
        (folder/'assistance.json').write_bytes((json.dumps(assist,indent=2)+'\n').encode())
        recording(folder,json.loads((folder/'capture.json').read_bytes()))
    (folder/'oil_stairs_driver.py').write_bytes(driver)
    print(result)


if __name__=='__main__':main()
