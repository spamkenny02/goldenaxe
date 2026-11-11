"""Read-only observed SMS service contact, explicit refusal and ordinary exit.

This covers a refusal only, never a successful purchase, save or paid night.
"""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk

dialogue_events=[]


def main():
    p=argparse.ArgumentParser();p.add_argument('--sms',action='store_true',required=True)
    p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True)
    p.add_argument('--outside',type=lambda v:int(v,0),required=True)
    p.add_argument('--kind',choices=['merchant','healer','save'],required=True)
    p.add_argument('--assisted-prefix',action='store_true');a=p.parse_args()
    source=ROOT/'validation/natural-dungeon-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and prior['failure'] is None and prior['house_outside']==a.outside
    assert cap['sram_input'] is None
    house=prior['house_target'];assets=json.loads((ROOT/'analysis'/f'{a.kind}_assets.json').read_bytes())
    _,nx,ny=next(n for n in assets['nodes'] if n[0]==house)
    start=cap['frames'];raw_initial=(source/f'ram_{start:05d}.bin').read_bytes()
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        end=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],end,k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix)
    out=ROOT/'validation/natural-service-route'/('sms-'+a.trial);assert not out.exists()
    state={};captures={start};events=[];observed=0;first=None;done=None;failure=None;direction=0;cursor=0
    contacts=[];declined=False;departure=False
    decline_pc={'healer':0x8cc7,'save':0x8db6}.get(a.kind)
    def observe(frame,r):
        nonlocal observed,failure,done
        observed=frame
        if frame<start:return
        if frame==start:assert r==raw_initial
        state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],
            counter=r[0x304],x=r[0x313],y=r[0x311],health=r[0x318],magic=r[0xdb],
            gold=r[0xdd],keys=r[0xde],yes_no=r[0x1cc2],items=bytes(r[0xe0:0xf3]).hex(),tilemap=bytes(r[0x1600:0x1c00]))
        if not state['health']:failure='hero_died'
        if contacts and any(state[k] != initial_value for k,initial_value in
            [('health',raw_initial[0x318]),('magic',raw_initial[0xdb]),('gold',raw_initial[0xdd]),
             ('keys',raw_initial[0xde]),('items',raw_initial[0xe0:0xf3].hex())]):failure='refusal_changed_resources'
        if state['room']==a.outside and state['game']==12 and state['hero']==1 and contacts and (declined or a.kind=='merchant'):
            if done is None:done=frame;captures.add(frame+40)
    def choose(frame):
        nonlocal cursor,first,direction,declined,departure
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if failure or done:return []
        while cursor<len(dialogue_events):
            e=dialogue_events[cursor];cursor+=1
            if e['frame']<=start or e['event_pc'] not in (0x50c,0x524):continue
            if e['room']!=house:continue
            contacts.append(e);captures.add(frame+1)
            if first is None:first=frame
            if e['text_pc']==decline_pc:declined=True;direction=1
        if first is not None and state['game']==12 and state['hero']==1 and frame-first>200:
            if not departure:direction=1
            departure=True
        if first is not None and (state['game']==22 or not departure):
            if a.kind=='merchant':return [0] if frame%40==0 else []
            if declined:return [8] if frame%40==20 else []
            if frame-first<140 or frame%20:return []
            # Original 60F5..6147 stores FF=Yes/00=No at DCC2.
            # Confirm only after an actual No selection, irrespective of the
            # text's completion phase or the frame modulo at first contact.
            return [8] if state['yes_no']==0 else [5]
        if state['room']!=house or state['game']!=12 or state['hero'] not in (0,1):return []
        if state['counter']:return [4+direction]
        point=state['x'],state['y'];target=(136,160) if departure else (nx,ny)
        if point==target:direction=1 if departure else 0;return [4+direction]
        path=walk(state['tilemap'],point,lambda q:q==target)
        if path:direction=path[0];return [4+direction]
        return []
    def controller(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):
        run(ROOT/'input/original.sms',start+6000,out,captures,cap['presses'],skip_intro=False,
            input_provider=controller,ram_observer=observe,ram_writes=FrameWrites(writes),
            core_options=cap['core_options'],stop_when=lambda:bool(failure) or done is not None and observed>=done+40)
    result=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),
        outside=a.outside,house=house,kind=a.kind,variant='refusal',source_prefix=a.prefix,
        complete_frame=done,text_entries=[dict(frame=e['frame'],text_pc=e['text_pc'],caller=e['caller']) for e in contacts],
        explicit_decline_text_observed=declined,resources_unchanged=not failure,
        rom_sha256=cap['rom_sha256'],last_state={k:v for k,v in state.items() if k!='tilemap'},
        new_assistance_writes=0,primary_state_imports=0,sram_checkpoint_injection=False,
        scope='Service refusal, original text entries and exterior exit; successful transactions and other choices remain separate.')
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(v) for v in presses]
    (out/'capture.json').write_text(json.dumps(actual,indent=2)+'\n')
    for name,value in [('report',result),('controls',controls)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    if writes:
        (out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(result),flush=True)
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
