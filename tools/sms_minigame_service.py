"""Play/refuse an actual SMS gambling room with observed text and real money."""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk

dialogue_events=[]


def main():
    p=argparse.ArgumentParser();p.add_argument('--sms',action='store_true',required=True)
    p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True)
    p.add_argument('--outside',type=lambda v:int(v,0),required=True)
    p.add_argument('--variant',choices=['play','refuse','poor'],default='play')
    p.add_argument('--rounds',type=int,choices=range(1,33),default=1)
    p.add_argument('--initial-wait',type=int,default=0);p.add_argument('--stop-on-lucky',action='store_true')
    p.add_argument('--assisted-prefix',action='store_true');a=p.parse_args()
    source=ROOT/'validation/natural-dungeon-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and prior['failure'] is None and prior['house_target']==0x5f and prior['house_outside']==a.outside
    assert cap['sram_input'] is None
    start=cap['frames'];initial=(source/f'ram_{start:05d}.bin').read_bytes()
    assert (initial[0xdd]<10) if a.variant=='poor' else (a.variant=='refuse' or initial[0xdd]>=10)
    reference=json.loads((ROOT/'analysis/minigame_reference.json').read_bytes());pcs=reference['text_pcs']
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],last,k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix)
    out=ROOT/'validation/natural-service-route'/('sms-'+a.trial);assert not out.exists()
    state={};cursor=0;direction=0;phase='walk';phase_started=0;ack_until=0
    outcome=None;expected_gold=None;admission=None;decline=None;poor=False;done=None;failure=None;observed=0
    outcomes=[];round_start_gold=initial[0xdd];round_number=1
    lucky_seen=False;board_wait_started=None
    entries=[];draws=[];captures={start}
    def observe(frame,r):
        nonlocal observed,failure,admission,done
        observed=frame
        if frame<start:return
        state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
            x=r[0x313],y=r[0x311],health=r[0x318],gold=r[0xdd],magic=r[0xdb],yes_no=r[0x1cc2],
            stage=r[0x73],cells=bytes(r[0x1c00:0x1ca0]),tilemap=bytes(r[0x1600:0x1c00]))
        if not state['health']:failure='hero_died'
        if state['room']==11 and admission is None:
            assert initial[0xdd]-state['gold']==10;admission=frame;captures.add(frame+1)
        ready=(outcome is not None if a.variant=='play' else poor if a.variant=='poor' else decline is not None)
        if ready and state['room']==a.outside and state['game']==12 and state['hero']==1:
            assert state['gold']==(expected_gold if a.variant=='play' else initial[0xdd])
            if a.variant=='play':assert len(outcomes)==a.rounds or a.stop_on_lucky and (lucky_seen or state['gold']<10)
            assert state['magic']==initial[0xdb] and state['health']==initial[0x318]
            if done is None:done=frame;captures.add(frame+40)
    def choose(frame):
        nonlocal cursor,direction,phase,phase_started,ack_until,outcome,expected_gold,decline,poor,round_start_gold,round_number,lucky_seen,board_wait_started
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if done or failure:return []
        while cursor<len(dialogue_events):
            e=dialogue_events[cursor];cursor+=1
            if e['frame']<=start or e['event_pc'] not in (0x50c,0x524):continue
            pc=e['text_pc'];entries.append(dict(frame=e['frame'],text_pc=pc));captures.add(frame+1)
            phase_started=e['frame']
            if pc==pcs[0]:phase='admission'
            elif pc==pcs[5]:phase='replay_no'
            elif pc==pcs[8]:
                if outcome is not None:
                    round_start_gold=state['gold'];round_number+=1;outcome=None
                phase='ack';ack_until=frame+160
            elif pc==0x8bcd:poor=True;phase='ack';ack_until=frame+160
            elif pc==pcs[1]:decline=e['frame'];phase='exit';direction=1;ack_until=frame+160
            else:
                phase='ack';ack_until=frame+160
                if pc in (pcs[3],pcs[4]):
                    tops=[state['cells'][n] for n in (3,6,9)]
                    assert all(0x34<=v<=0x37 for v in tops),tops
                    amount=sum([30,10,-10,-30][v-0x34] for v in tops)
                    expected_gold=max(0,min(255,round_start_gold-10+amount))
                    special=state['cells'][12];lucky_seen|=special==0x38
                    outcome=dict(frame=e['frame'],round=round_number,top_cards=tops,amount=amount,expected_gold=expected_gold,special_card=special)
                    if len(outcomes)<round_number:outcomes.append(outcome)
                    else:outcomes[round_number-1]=outcome
        if phase in ('admission','replay_no'):
            if frame-phase_started<140 or frame%20:return []
            yes=(phase=='admission' and a.variant!='refuse') or (phase=='replay_no' and len(outcomes)<a.rounds and not (a.stop_on_lucky and lucky_seen))
            return [8] if state['yes_no']==(255 if yes else 0) else [4 if yes else 5]
        if frame<ack_until:return [8] if frame%40==0 else []
        if state['game']!=12 or state['hero'] not in (0,1):return []
        if state['counter']:return [4+direction]
        room=state['room'];point=state['x'],state['y']
        if room==0x5f:
            leaving=decline is not None or outcome is not None or poor
            target=(136,160) if leaving else (136,88)
        elif room==11:
            if outcome is not None:return [8] if frame%40==0 else []
            if state['stage']!=1:return [8] if frame%40==0 else []
            if board_wait_started is None:board_wait_started=frame
            if frame-board_wait_started<a.initial_wait:return []
            slot=next((i for i in range(10) if state['cells'][0x33+i]==0x3a),None)
            if slot is None:return []
            target=(56+slot*16,72)
            key=list(state['cells'][0x33:0x3d])
            if not draws or draws[-1]['cards']!=key:draws.append(dict(frame=frame,cards=key));captures.add(frame+1)
        else:return []
        if point==target:direction=1 if room==0x5f and (decline or outcome or poor) else 0;return [4+direction]
        path=walk(state['tilemap'],point,lambda q:q==target)
        if path:direction=path[0];return [4+direction]
        return []
    def control(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):
        run(ROOT/'input/original.sms',start+14000+max(0,a.rounds-2)*6000,out,captures,cap['presses'],skip_intro=False,
            input_provider=control,ram_observer=observe,ram_writes=FrameWrites(writes),core_options=cap['core_options'],
            stop_when=lambda:bool(failure) or done is not None and observed>=done+40)
    result=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),
        outside=a.outside,variant=a.variant,source_prefix=a.prefix,rom_sha256=cap['rom_sha256'],complete_frame=done,
        admission_frame=admission,admission_cost=10*round_number if admission else 0,outcome=outcome,outcomes=outcomes,requested_rounds=a.rounds,decline_frame=decline,
        lucky_card_observed=lucky_seen,initial_wait=a.initial_wait,
        poor_text_observed=poor,gold_before=initial[0xdd],gold_after=state['gold'],text_entries=entries,draws=draws,last_state={k:v for k,v in state.items() if k not in ('tilemap','cells')},
        primary_state_imports=0,new_assistance_writes=0,sram_checkpoint_injection=False,
        scope='Actual original game draws and money, no RNG/resource edits. This selected result does not cover all luck outcomes or repeat-play branches.')
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(v) for v in presses]
    (out/'capture.json').write_text(json.dumps(actual,indent=2)+'\n')
    for name,value in [('report',result),('controls',controls)]:(out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    if writes:
        (out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(result),flush=True)
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
