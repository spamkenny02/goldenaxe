"""Pay an actual MD inn, observe the night and healing, and leave normally."""
import argparse,contextlib,hashlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from validate_playable_sprite_limit import symbols
from natural_dungeon_combat import walk

def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);p.add_argument('--trial',required=True);p.add_argument('--outside',type=lambda v:int(v,0),required=True);p.add_argument('--assisted-prefix',action='store_true');a=p.parse_args()
    source=ROOT/'validation/natural-dungeon-route'/a.prefix;cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and not prior['failure'] and prior['house_outside']==a.outside and cap['sram_input'] is None
    rom=ROOT/a.rom;digest=hashlib.sha256(rom.read_bytes()).hexdigest();assert digest==cap['rom_sha256'];sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    assets=json.loads((ROOT/'analysis/healer_assets.json').read_bytes());cost=next(cost for outside,cost in assets['prices'] if outside==a.outside);house=prior['house_target'];_,nx,ny=next(row for row in assets['nodes'] if row[0]==house)
    start=cap['frames'];old=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for n,row in enumerate(old):
        end=old[n+1]['frame']-1 if n+1<len(old) else start
        presses.extend((row['frame'],min(end,start),key) for key in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=FrameWrites(prefix_writes(source,cap,a.assisted_prefix));inherited=len(writes)
    out=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not out.exists();state={};first=None;contact=None;night=None;reply=None;done=None;failure=None;observed=0;direction=0;controls=[];events=[];captures=set()
    def observe(frame,raw):
        nonlocal observed,first,contact,night,reply,done,failure
        observed=frame
        if frame<start:return
        data=lambda n,k,off=0:bytes(raw[(sy[n]+off+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),gold=word('hero_gold'),keys=word('hero_keys'),items=data('hero_items',17).hex(),yes=word('save_yes'),phase=word('healer_phase'),modal=word('house_dialogue_active'),resume=word('resume_phase'),loading=data('door_transition_loading',1)[0],graphics=word('world_graphics_class'),audio_error=word('sound_unhandled_command'),tilemap=data('sms_vram',1536,0x3800))
        actors=data('world_actor_state',768);assert not any(actors[n+24] and (0x63<=actors[n]<=0x6d or 0x78<=actors[n]<=0x7c) for n in range(0,768,48))
        writes.append((frame+1,sy['hero_hurt'],b'\0\x81'))
        if first is None:
            first={k:v for k,v in state.items() if k!='tilemap'};assert first['room']==house and first['gold']>=cost
        if not state['health'] or state['game']==20:failure='hero_died'
        if state['audio_error']:failure='native_audio_error'
        for key in ('max_health','magic','keys','items'):assert state[key]==first[key],key
        if contact is None and state['phase']==1:contact=frame;captures.add(frame+1)
        if night is None and state['phase']==2:night=frame;captures.add(frame+1)
        if reply is None and state['phase']==3:reply=frame;captures.add(frame+200)
        if night and reply and state['room']==a.outside and state['game']==12 and state['hero']==1 and not state['resume'] and not state['loading'] and not state['graphics'] and done is None:
            assert state['gold']==first['gold']-cost and state['health']==first['max_health'];done=frame;captures.add(frame+40)
        row={k:v for k,v in state.items() if k!='tilemap'}
        if not events or any(row[k]!=events[-1][k] for k in ('room','game','phase','gold','health')):events.append(dict(frame=frame,**row))
    def choose(frame):
        nonlocal direction
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if done or failure:return []
        if state['phase']==1:
            if contact is None or frame-contact<160 or frame%20:return []
            return [8] if state['yes'] else [4]
        if state['phase']==2:return []
        if state['phase']==3:return [8] if reply and frame-reply>=200 and frame%40==0 else []
        if state['room']!=house or state['game']!=12 or state['hero'] not in (0,1):return []
        if state['counter']:return [4+direction]
        point=state['x'],state['y'];target=(136,160) if reply else (nx,ny)
        if point==target:direction=1 if reply else 0;return [4+direction]
        path=walk(state['tilemap'],point,lambda q:q==target)
        if path:direction=path[0];return [4+direction]
        return []
    def control(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):run(rom,start+6000,out,captures,cap['presses'],skip_intro=False,input_provider=control,ram_observer=observe,ram_writes=writes,core_options=cap['core_options'],stop_when=lambda:bool(failure) or done is not None and observed>=done+40)
    result=dict(passed=done is not None and not failure,failure=failure or (None if done else 'service_incomplete'),rom_sha256=digest,source_prefix=a.prefix,outside=a.outside,house=house,price=cost,first_state=first,last_state={k:v for k,v in state.items() if k!='tilemap'},contact_frame=contact,night_frame=night,reply_frame=reply,complete_frame=done,new_assistance_writes=len(writes)-inherited,declared_approach_guard=True,primary_state_imports=0,sram_checkpoint_injection=False,scope='Actual payment, night, health restoration and fully restored exterior. Existing gold only; approach hurt guard recorded, no resources or quest edits. Text bitmap and timing comparison remain separate.')
    for name,value in [('report',result),('controls',controls),('events',events)]:(out/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=presses;(out/'capture.json').write_bytes((json.dumps(actual,indent=2)+'\n').encode())
    assist=json.loads((source/'assistance.json').read_bytes());assist['writes']=[dict(frame=f,address=addr,data_hex=data.hex()) for f,addr,data in writes]
    if 'episodes' in assist:assist['episodes'][-1]['end_frame']=actual['frames']+1
    (out/'assistance.json').write_bytes((json.dumps(assist,indent=2)+'\n').encode());recording(out,actual)
    print(json.dumps(result),flush=True)
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
