"""Write an actual SMS save through a reached NPC; verify its live 592-byte payload."""
import argparse,contextlib,io,json,hashlib
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk

dialogue_events=[]


def main():
    p=argparse.ArgumentParser();p.add_argument('--sms',action='store_true',required=True)
    p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True)
    p.add_argument('--slot',type=int,choices=range(3),default=0)
    p.add_argument('--assisted-prefix',action='store_true');a=p.parse_args()
    source=ROOT/'validation/natural-dungeon-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and prior['failure'] is None and cap['sram_input'] is None
    outside=prior['house_outside'];house=prior['house_target']
    _,nx,ny=next(n for n in json.loads((ROOT/'analysis/save_assets.json').read_bytes())['nodes'] if n[0]==house)
    start=cap['frames'];controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],last,k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix)
    out=ROOT/'validation/natural-service-route'/('sms-'+a.trial);assert not out.exists()
    state={};cursor=0;phase='walk';direction=0;payload=None;saved=None;done=None;failure=None;observed=0
    last_raw=None;captures={start};entries=[]
    def observe(frame,r):
        nonlocal last_raw,observed,failure,done
        observed=frame
        if frame<start:return
        last_raw=bytes(r)
        state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
            x=r[0x313],y=r[0x311],health=r[0x318],slot=r[0xa0],tilemap=bytes(r[0x1600:0x1c00]))
        if not state['health']:failure='hero_died'
        if saved and state['room']==outside and state['game']==12 and state['hero']==1 and done is None:
            done=frame;captures.add(frame+40)
    def choose(frame):
        nonlocal cursor,phase,direction,payload,saved
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if failure or done:return []
        while cursor<len(dialogue_events):
            e=dialogue_events[cursor];cursor+=1
            if e['frame']<=start or e['event_pc'] not in (0x50c,0x524):continue
            entries.append(dict(frame=e['frame'],text_pc=e['text_pc']));captures.add(frame+1)
            if e['text_pc']==0x8d70:phase='yes'
            elif e['text_pc']==0x8da7:phase='slots'
            elif e['text_pc']==0x8ddd:
                payload=last_raw[0xb0:0x300];saved=e['frame'];phase='saved';direction=1
        if phase!='walk' and (state['game']==22 or not saved):
            if frame%40:return []
            if phase=='slots' and state['slot']!=a.slot:return [5 if state['slot']<a.slot else 4]
            return [8]
        if state['room']!=house or state['game']!=12 or state['hero'] not in (0,1):return []
        if state['counter']:return [4+direction]
        point=state['x'],state['y'];target=(136,160) if saved else (nx,ny)
        if point==target:direction=1 if saved else 0;return [4+direction]
        path=walk(state['tilemap'],point,lambda q:q==target)
        if path:direction=path[0];return [4+direction]
        return []
    def control(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):
        run(ROOT/'input/original.sms',start+6000,out,captures,cap['presses'],skip_intro=False,
            input_provider=control,ram_observer=observe,ram_writes=FrameWrites(writes),
            core_options=cap['core_options'],sram_out=out/'game-written.srm',
            stop_when=lambda:bool(failure) or done is not None and observed>=done+40)
    sram=(out/'game-written.srm').read_bytes();offset=0x400+a.slot*0x400
    exact=payload is not None and len(payload)==592 and sram[offset:offset+592]==payload and sram[0x30]==a.slot+1
    report=dict(passed=done is not None and not failure and exact,
        failure=failure or (None if done and exact else 'save_payload_or_exit_unverified'),
        outside=outside,house=house,slot=a.slot,complete_frame=done,save_written_frame=saved,
        game_written_save=True,serialized_payload_exact=exact,payload_bytes=592,
        payload_sha256=hashlib.sha256(payload).hexdigest() if payload else None,
        sram_sha256=hashlib.sha256(sram).hexdigest(),text_entries=entries,source_prefix=a.prefix,
        rom_sha256=cap['rom_sha256'],primary_state_imports=0,new_assistance_writes=0,sram_checkpoint_injection=False,
        scope='Actual NPC save and exit with SRAM payload matched to live source RAM. Independent replay and fresh Continue load are separate requirements.')
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(v) for v in presses]
    (out/'capture.json').write_text(json.dumps(actual,indent=2)+'\n')
    for name,value in [('report',report),('controls',controls)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    if writes:
        (out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(report),flush=True)
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
