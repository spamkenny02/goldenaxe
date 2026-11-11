"""Accept a real SMS inn service, verify price, life restoration and exit."""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk

dialogue_events=[]


def main():
    p=argparse.ArgumentParser();p.add_argument('--sms',action='store_true',required=True)
    p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True)
    p.add_argument('--outside',type=lambda v:int(v,0),required=True)
    p.add_argument('--assisted-prefix',action='store_true');a=p.parse_args()
    source=ROOT/'validation/natural-dungeon-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and prior['failure'] is None and prior['house_outside']==a.outside and cap['sram_input'] is None
    assets=json.loads((ROOT/'analysis/healer_assets.json').read_bytes());house=prior['house_target']
    _,nx,ny=next(n for n in assets['nodes'] if n[0]==house);cost=next(v for o,v in assets['prices'] if o==a.outside)
    start=cap['frames'];initial=(source/f'ram_{start:05d}.bin').read_bytes();assert initial[0xdd]>=cost
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],last,k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix)
    out=ROOT/'validation/natural-service-route'/('sms-'+a.trial);assert not out.exists()
    state={};first=None;done=None;failure=None;observed=0;cursor=0;direction=0;completed_text=None;entries=[];captures={start}
    def observe(frame,r):
        nonlocal observed,failure,done
        observed=frame
        if frame<start:return
        state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
            x=r[0x313],y=r[0x311],health=r[0x318],max_health=r[0xda],magic=r[0xdb],gold=r[0xdd],
            items=bytes(r[0xe0:0xf3]).hex(),yes_no=r[0x1cc2],tilemap=bytes(r[0x1600:0x1c00]))
        if not state['health']:failure='hero_died'
        if completed_text and state['room']==a.outside and state['game']==12 and state['hero']==1:
            assert state['health']==initial[0xda] and state['max_health']==initial[0xda]
            assert state['gold']==initial[0xdd]-cost and state['magic']==initial[0xdb]
            assert state['items']==initial[0xe0:0xf3].hex()
            if done is None:done=frame;captures.add(frame+40)
    def choose(frame):
        nonlocal cursor,first,direction,completed_text
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if done or failure:return []
        while cursor<len(dialogue_events):
            e=dialogue_events[cursor];cursor+=1
            if e['frame']<=start or e['event_pc'] not in (0x50c,0x524):continue
            entries.append(dict(frame=e['frame'],text_pc=e['text_pc']));captures.add(frame+1)
            if e['text_pc'] in (0x8c7b,0x8d3f):first=e['frame']
            if e['text_pc']==0x8cf5:completed_text=e['frame'];direction=1
        if first and state['game']==22:
            if completed_text:return [8] if frame%40==0 else []
            if frame-first<140 or frame%40:return []
            return [8] if state['yes_no']==255 else [4]
        if state['room']!=house or state['game']!=12 or state['hero'] not in (0,1):return []
        if state['counter']:return [4+direction]
        target=(136,160) if completed_text else (nx,ny);point=state['x'],state['y']
        if point==target:direction=1 if completed_text else 0;return [4+direction]
        path=walk(state['tilemap'],point,lambda q:q==target)
        if path:direction=path[0];return [4+direction]
        return []
    def control(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):
        run(ROOT/'input/original.sms',start+6000,out,captures,cap['presses'],skip_intro=False,
            input_provider=control,ram_observer=observe,ram_writes=FrameWrites(writes),core_options=cap['core_options'],
            stop_when=lambda:bool(failure) or done is not None and observed>=done+40)
    result=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),
        outside=a.outside,house=house,price=cost,complete_frame=done,completed_text=completed_text,
        source_prefix=a.prefix,rom_sha256=cap['rom_sha256'],health_before=initial[0x318],health_after=state['health'],
        gold_before=initial[0xdd],gold_after=state['gold'],magic_before=initial[0xdb],magic_after=state['magic'],
        text_entries=entries,primary_state_imports=0,new_assistance_writes=0,sram_checkpoint_injection=False,
        scope='Actual accepted inn, exact price, HP restoration, preserved MP/inventory and exterior exit; refusals and insufficient funds remain separate.')
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(v) for v in presses]
    (out/'capture.json').write_text(json.dumps(actual,indent=2)+'\n')
    for name,value in [('report',result),('controls',controls)]:(out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    if writes:
        (out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(result),flush=True)
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
