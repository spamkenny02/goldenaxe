"""Ring an actually owned Ice Bell with ordinary menu/buttons; no state edits."""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording


def main():
    p=argparse.ArgumentParser();p.add_argument('--sms',action='store_true',required=True)
    p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True);a=p.parse_args()
    source=ROOT/'validation/natural-service-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes());start=cap['frames'];assert cap['sram_input'] is None
    initial=(source/f'ram_{start:05d}.bin').read_bytes();assert initial[0xea] and initial[0xac]==0
    outside=int.from_bytes(initial[0xb9:0xbb],'little');assert outside>=16 and outside&15!=15
    presses=list(map(tuple,cap['presses']));old=json.loads((source/'controls.json').read_bytes())
    for i,row in enumerate(old):
        end=old[i+1]['frame']-1 if i+1<len(old) else start
        presses.extend((row['frame'],min(end,start),key) for key in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix)
    out=ROOT/'validation/natural-service-route'/('sms-'+a.trial);assert not out.exists()
    state={};controls=[];events=[];captures={start};first=None;done=None;observed=0;failure=None
    def observe(frame,raw):
        nonlocal observed,first,done,failure
        observed=frame
        if frame<start:return
        state.update(room=int.from_bytes(raw[0xb9:0xbb],'little'),game=raw[0x1d],hero=raw[0x301],counter=raw[0x304],
            x=raw[0x313],y=raw[0x311],slot=raw[0xa0],selected=raw[0xdf],bell=raw[0xac],health=raw[0x318])
        if not state['health']:failure='hero_died'
        if not events or any(state[k]!=events[-1][k] for k in ('game','selected','slot','bell','hero')):events.append(dict(frame=frame,**state))
        if frame>start and state['bell'] and first is None:first=frame;captures.add(frame+1)
        if done is None and first and frame>=first+180 and state['game']==12 and state['hero']==1 and not state['counter']:
            assert raw[0xcf:0xd8]==initial[0xcf:0xd8] and raw[0xda:0xdf]==initial[0xda:0xdf]
            assert raw[0xe0:0xf3]==initial[0xe0:0xf3] and raw[0x100:0x200]==initial[0x100:0x200]
            done=frame;captures.add(frame+1)
    def control(frame):
        if frame<=start:return [key for key in range(16) if masks[frame]&(1<<key)]
        value=[]
        if not first and frame%20==0:
            if state['game']==12 and state['hero']==1 and not state['counter']:value=[8] if state['selected']==10 else [0]
            elif state['game']==16:
                slot=state['slot']
                if state['selected']==10:value=[0]
                elif slot//4!=2:value=[5 if slot//4<2 else 4]
                elif slot%4!=2:value=[7 if slot%4<2 else 6]
                else:value=[8]
        if not controls or controls[-1]['buttons']!=value:controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):
        run(ROOT/'input/original.sms',start+3000,out,captures,cap['presses'],skip_intro=False,
            input_provider=control,ram_observer=observe,ram_writes=FrameWrites(writes),core_options=cap['core_options'],
            stop_when=lambda:failure is not None or done is not None and observed>done)
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(v) for v in presses];(out/'capture.json').write_text(json.dumps(actual,indent=2)+'\n')
    report=dict(passed=done is not None and failure is None,failure=failure,source_prefix=a.prefix,outside=outside,
        first_bell_activation_frame=first,events=events,last_state=state,inventory_and_quest_flags_unchanged=done is not None,
        primary_state_imports=0,new_assistance_writes=0,scope='Real owned Bell selected through menu and rung outside; no new state writes.')
    for name,data in [('report',report),('controls',controls)]: (out/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    (out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(report),flush=True)
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
