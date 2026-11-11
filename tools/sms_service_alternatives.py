"""Actual poor-service replies and passage refusals with ordinary Yes/No input."""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk

dialogue_events=[]


def main():
    p=argparse.ArgumentParser();p.add_argument('--sms',action='store_true',required=True)
    p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--prefix',required=True)
    p.add_argument('--trial',required=True);p.add_argument('--kind',choices=['inn','passage'],required=True)
    p.add_argument('--variant',choices=['poor','refuse'],required=True);a=p.parse_args()
    source=ROOT/'validation/natural-dungeon-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and not prior['failure'] and cap['sram_input'] is None
    house=prior['house_target'];outside=prior['house_outside'];start=cap['frames']
    initial=(source/f'ram_{start:05d}.bin').read_bytes()
    if a.kind=='inn':
        assets=json.loads((ROOT/'analysis/healer_assets.json').read_bytes());_,nx,ny=next(n for n in assets['nodes'] if n[0]==house)
        cost=next(v for n,v in assets['prices'] if n==outside);prompts=(0x8c7b,0x8d3f)
    else:nx,ny=136,72;cost=10;prompts=(0x911e,)
    if a.variant=='poor':assert initial[0xdd]<cost
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],min(last,start),k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix)
    out=ROOT/'validation/natural-service-route'/('sms-'+a.trial);assert not out.exists()
    state={};cursor=0;direction=0;prompt=None;confirmed=None;poor=None;decline=None;done=None;observed=0;failure=None
    captures={start};entries=[]
    def observe(frame,r):
        nonlocal observed,failure,done
        observed=frame
        if frame<start:return
        state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
            x=r[0x313],y=r[0x311],health=r[0x318],yes_no=r[0x1cc2],tilemap=bytes(r[0x1600:0x1c00]))
        if not state['health']:failure='hero_died'
        ready=poor is not None if a.variant=='poor' else confirmed is not None
        if ready and done is None and state['room']==outside and state['game']==12 and state['hero']==1:
            assert r[0xcf:0xf3]==initial[0xcf:0xf3] and r[0x318]==initial[0x318]
            assert r[0x100:0x200]==initial[0x100:0x200]
            done=frame;captures.add(frame+10)
    def choose(frame):
        nonlocal cursor,direction,prompt,confirmed,poor,decline
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if done or failure:return []
        while cursor<len(dialogue_events):
            e=dialogue_events[cursor];cursor+=1
            if e['frame']<=start or e['event_pc'] not in (0x50c,0x524):continue
            entries.append(dict(frame=e['frame'],text_pc=e['text_pc']));captures.add(frame+1)
            if e['text_pc'] in prompts:prompt=e['frame']
            elif e['text_pc']==0x8bcd:poor=e['frame'];direction=1
            elif e['text_pc']==0x8cc7:decline=e['frame'];direction=1
        if a.variant=='refuse' and confirmed is not None and frame-confirmed>100 and (state['x'],state['y'])==(nx,ny):
            # Down also walks away once the original confirmation has closed.
            # A C edge alone would repeatedly swing at the NPC afterwards.
            return [5,8] if frame%80==0 and state['yes_no']==0 else [5]
        selecting=(confirmed is None or a.variant=='poor' and poor is None or
            a.variant=='refuse' and (state['x'],state['y'])==(nx,ny))
        if prompt is not None and selecting:
            if frame-prompt<160 or frame%20:return []
            wanted=255 if a.variant=='poor' else 0
            if state['yes_no']!=wanted:return [4 if wanted else 5]
            if confirmed is None:confirmed=frame
            direction=1;return [8]
        if confirmed is not None and (frame-confirmed<100 or a.variant=='poor' and poor is None):return []
        if poor is not None and frame-poor<160:return [8] if frame%40==0 and frame-poor>100 else []
        if state['game']==22:return [8] if frame%40==0 else []
        if state['room']!=house or state['game']!=12 or state['hero'] not in (0,1):return []
        if state['counter']:return [4+direction]
        target=(136,160) if confirmed is not None else (nx,ny);point=state['x'],state['y']
        if point==target:direction=1 if confirmed is not None else 0;return [4+direction]
        path=walk(state['tilemap'],point,lambda q:q==target)
        if path:direction=path[0];return [4+direction]
        return []
    def control(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):
        run(ROOT/'input/original.sms',start+7000,out,captures,cap['presses'],skip_intro=False,
            input_provider=control,ram_observer=observe,ram_writes=FrameWrites(writes),core_options=cap['core_options'],
            stop_when=lambda:bool(failure) or done is not None and observed>=done+10)
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(v) for v in presses]
    (out/'capture.json').write_text(json.dumps(actual,indent=2)+'\n')
    report=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),
        source_prefix=a.prefix,outside=outside,kind=a.kind,variant=a.variant,cost=cost,gold=initial[0xdd],
        prompt_frame=prompt,confirmation_frame=confirmed,poor_text_frame=poor,text_entries=entries,complete_frame=done,
        last_state={k:v for k,v in state.items() if k!='tilemap'},primary_state_imports=0,new_assistance_writes=0,
        scope='Actual Yes/No decision, original refusal/poor reply where applicable, preserved resources and flags, normal exit.')
    for name,value in [('report',report),('controls',controls)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    if writes:(out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(report),flush=True)
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
