"""Receive a real curser hit, defeat the curser, and consume actual Magic Oil.

The inherited approach guard is released, never HP, inventory or actor state.
"""
import argparse,contextlib,io,json,hashlib
from validate_playable_sprite_limit import symbols
from md_readonly_view import md_to_sms_view
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording,EPISODE_KEYS
from natural_dungeon_combat import walk


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',required=True)
    p.add_argument('--trace',required=True);p.add_argument('--trial',required=True);a=p.parse_args()
    source=ROOT/'validation'/a.trace;cap=json.loads((source/'capture.json').read_bytes())
    prior=json.loads((source/'report.json').read_bytes());assert prior['failure'] is None and prior['target_room_reached']
    rom=ROOT/a.rom;assert hashlib.sha256(rom.read_bytes()).hexdigest()==cap['rom_sha256'];sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    start=cap['frames'];initial=md_to_sms_view((source/f'ram_{start:05d}.bin').read_bytes(),sy)
    assert initial[0xe2] and not initial[0xbf] and initial[0x318]>32
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],last,k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=list(prefix_writes(source,cap,True))
    writes.append((start+1,sy['hero_hurt'],b'\0\0'))
    out=ROOT/'validation/natural-dungeon-combat'/('md-auto-'+a.trial);assert not out.exists()
    state={};cursers=[];first_curse=None;first_cure=None;done=None;failure=None;observed=0;direction=0;captures={start};events=[]
    def observe(frame,raw):
        nonlocal observed,first_curse,first_cure,done,failure,cursers
        observed=frame
        if frame<start:return
        r=bytearray(md_to_sms_view(raw,sy));r[0x600:0x900]=bytes(raw[(sy['world_actor_state']+i)^1] for i in range(768))
        assert not (raw[sy['sound_unhandled_command']]|raw[sy['sound_unhandled_command']+1]<<8),'Native audio error'
        state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
            x=r[0x313],y=r[0x311],health=r[0x318],hurt=r[0x305],curse=r[0xbf],oil=r[0xe2],selected=r[0xdf],slot=r[0xa0],
            gold=r[0xdd],magic=r[0xdb],tilemap=bytes(r[0x1600:0x1c00]))
        cursers=[dict(slot=i,x=r[0x600+i*48+19],y=r[0x600+i*48+17],hp=r[0x600+i*48+24])
            for i in range(16) if r[0x600+i*48]==0x53 and r[0x600+i*48+24]]
        if frame==start:assert cursers
        if state['curse'] and first_curse is None:
            assert state['hurt']<=128 and state['oil']==initial[0xe2]
            first_curse=dict(frame=frame,health=state['health']);captures.add(frame+1)
        if first_curse and not state['curse'] and not state['oil'] and first_cure is None:
            assert not cursers;first_cure=dict(frame=frame,health=state['health']);captures.add(frame+1)
        if not state['health']:failure='hero_died'
        if frame>start and state['hurt']>128:failure='guard_not_released'
        if state['gold']!=initial[0xdd] or state['magic']!=initial[0xdb]:failure='unexpected_currency_or_magic_change'
        if first_cure and not state['curse'] and state['selected']==1 and state['game']==12 and state['hero']==1 and not state['counter'] and frame-first_cure['frame']>100 and done is None:
            done=frame;captures.add(frame+1)
        if not events or any(state[k]!=events[-1][k] for k in ('health','curse','oil','selected')):
            events.append(dict(frame=frame,**{k:v for k,v in state.items() if k!='tilemap'}))
    def choose(frame):
        nonlocal direction
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if done or failure:return []
        wanted=1 if first_cure else 2 if first_curse and not cursers else 0 if first_curse else state['selected']
        if state['selected']!=wanted or state['game']==16:
            if frame%20:return []
            if state['game']==12 and state['hero']==1 and not state['counter']:return [0]
            if state['game']==16:
                if state['selected']==wanted:return [0]
                if state['slot']//4!=wanted//4:return [5 if state['slot']//4<wanted//4 else 4]
                if state['slot']%4!=wanted%4:return [7 if state['slot']%4<wanted%4 else 6]
                return [8]
            return []
        if state['game']!=12 or state['hero']!=1:return []
        if state['counter']:return [4+direction]
        if first_cure:return []
        if first_curse and not cursers:return [8] if frame%3 else []
        if not cursers:return []
        target=min(cursers,key=lambda e:abs(e['x']-state['x'])+abs(e['y']-state['y']))
        x,y=state['x'],state['y'];dx,dy=target['x']-x,target['y']-y
        if first_curse and ((abs(dx)<=24 and abs(dy)<=8) or (abs(dy)<=24 and abs(dx)<=8)):
            direction=(2 if dx<0 else 3) if abs(dx)>abs(dy) else (0 if dy<0 else 1)
            return [4+direction,8] if frame%3 else []
        goal=(lambda q:abs(q[0]-target['x'])<=4 and abs(q[1]-target['y'])<=4) if not first_curse else (
            lambda q:(abs(q[0]-target['x'])<=24 and abs(q[1]-target['y'])<=8) or (abs(q[1]-target['y'])<=24 and abs(q[0]-target['x'])<=8))
        path=walk(state['tilemap'],(x,y),goal)
        if path:direction=path[0];return [4+direction]
        return []
    def control(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom,start+9000,out,captures,cap['presses'],skip_intro=False,
            input_provider=control,ram_observer=observe,ram_writes=FrameWrites(writes),core_options=cap['core_options'],
            stop_when=lambda:bool(failure) or done is not None and observed>done)
    result=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),
        curse_remedy_passed=done is not None and not failure,source_prefix=a.trace,rom_sha256=cap['rom_sha256'],
        first_curse=first_curse,first_cure=first_cure,complete_frame=done,room_cleared=False,
        last_state={k:v for k,v in state.items() if k!='tilemap'},primary_state_imports=0,new_assistance_writes=1,
        resource_or_actor_writes=0,sram_checkpoint_injection=False,
        scope='Actual curser contact with protection released, curser defeated and owned oil consumed; no HP/item/actor fixture.')
    assist=json.loads((source/'assistance.json').read_bytes());assert assist['first_boss_combat'] is None
    assist['release_write_frame']=start+1
    assist['early_guard_release']=dict(frame=start+1,boss_room=assist['boss_room'],reason='ordinary_curse_contact_and_real_oil')
    assist['writes']=[dict(frame=f,address=addr,data_hex=data.hex()) for f,addr,data in writes]
    actual=json.loads((out/'capture.json').read_bytes())
    if 'episodes' in assist:
        for key in EPISODE_KEYS:assist['episodes'][-1][key]=assist[key]
        assist['episodes'][-1]['end_frame']=actual['frames']+1
    (out/'assistance.json').write_text(json.dumps(assist,indent=2)+'\n');recording(out,actual)
    for name,value in [('report',result),('controls',controls),('events',events)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(result),flush=True)
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
