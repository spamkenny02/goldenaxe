"""Play/refuse native MD gambling via actual controls, money and card draws."""
import argparse,contextlib,io,json,hashlib
from validate_playable_sprite_limit import symbols
from md_readonly_view import md_to_sms_view
from rebase_natural_campaign import evidence
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk

dialogue_events=[]


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',required=True)
    p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True)
    p.add_argument('--outside',type=lambda v:int(v,0),required=True)
    p.add_argument('--variant',choices=['play','refuse','poor'],default='play')
    p.add_argument('--rounds',type=int,choices=range(1,33),default=1)
    p.add_argument('--initial-wait',type=int,default=0);p.add_argument('--stop-on-lucky',action='store_true')
    p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--sms-reference');a=p.parse_args()
    source=ROOT/'validation/natural-dungeon-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and prior['failure'] is None and prior['house_target']==0x5f and prior['house_outside']==a.outside
    assert cap['sram_input'] is None
    rom=ROOT/a.rom;assert hashlib.sha256(rom.read_bytes()).hexdigest()==cap['rom_sha256'];sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    start=cap['frames'];initial=md_to_sms_view((source/f'ram_{start:05d}.bin').read_bytes(),sy)
    assert (initial[0xdd]<10) if a.variant=='poor' else (a.variant=='refuse' or initial[0xdd]>=10)
    reference=json.loads((ROOT/'analysis/minigame_reference.json').read_bytes());pcs=reference['text_pcs']
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],last,k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix)
    out=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not out.exists()
    state={};cursor=0;direction=0;phase='walk';phase_started=0;ack_until=0
    outcome=None;expected_gold=None;admission=None;decline=None;poor=False;done=None;failure=None;observed=0
    outcomes=[];round_start_gold=initial[0xdd];round_number=1
    lucky_seen=False;board_wait_started=None
    entries=[];draws=[];captures={start}
    poor_bitmap=None
    if a.variant=='poor':
        assert a.sms_reference
        ref=ROOT/'validation'/a.sms_reference;sr=json.loads(evidence(ref/'report.json'));assert sr['passed'] and sr['variant']=='poor' and sr['outside']==a.outside and sr['poor_text_observed']
        events=json.loads(evidence(ref/'dialogue_observations.json'))['events'];contact=next(e for e in sr['text_entries'] if e['text_pc']==0x8bcd)
        entry=next(e for e in events if e['event_pc'] in (0x50c,0x524) and e['frame']==contact['frame'] and e['text_pc']==0x8bcd)
        finish=next(e for e in events if e['event_pc']==0x6e3 and e['frame']>entry['frame'] and e['caller']==entry['caller'] and e['stack_pointer']==entry['stack_pointer']);poor_bitmap=finish['post_frame_bitmap_sha256']
    last_modal_key=None;poor_matched=None
    def observe(frame,raw):
        nonlocal observed,failure,admission,done,last_modal_key,poor_matched
        observed=frame
        if frame<start:return
        word=lambda n:raw[sy[n]]|raw[sy[n]+1]<<8
        r=bytearray(md_to_sms_view(raw,sy));r[0x73]=word('minigame_stage');r[0x1cc2]=255 if word('minigame_confirm_selection') else 0
        modal=word('house_dialogue_active');index=word('house_dialogue_index');room=word('room_id');key=(modal,index,room)
        if modal and key!=last_modal_key:
            assert 0<=index<len(pcs),(frame,key)
            dialogue_events.append(dict(frame=frame,event_pc=0x50c,text_pc=pcs[index],native_text_index=index))
        last_modal_key=key
        if poor_bitmap and not poor and modal and hashlib.sha256(bytes(raw[(sy['scratch']+i)^1] for i in range(1040))).hexdigest()==poor_bitmap:
            poor_matched=frame;dialogue_events.append(dict(frame=frame,event_pc=0x524,text_pc=0x8bcd))
        state.update(resume=word('resume_phase'),loading=raw[sy['door_transition_loading']^1],graphics=word('world_graphics_class'),audio_error=word('sound_unhandled_command'),room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
            x=r[0x313],y=r[0x311],health=r[0x318],gold=r[0xdd],magic=r[0xdb],yes_no=r[0x1cc2],
            stage=r[0x73],cells=bytes(r[0x1c00:0x1ca0]),tilemap=bytes(r[0x1600:0x1c00]))
        if not state['health']:failure='hero_died'
        if state['audio_error']:failure='native_audio_error'
        if state['room']==11 and admission is None:
            assert initial[0xdd]-state['gold']==10;admission=frame;captures.add(frame+1)
        ready=(outcome is not None if a.variant=='play' else poor if a.variant=='poor' else decline is not None)
        if ready and state['room']==a.outside and state['game']==12 and state['hero']==1 and not state['resume'] and not state['loading'] and state['graphics']==0:
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
        run(rom,start+14000+max(0,a.rounds-2)*6000,out,captures,cap['presses'],skip_intro=False,
            input_provider=control,ram_observer=observe,ram_writes=FrameWrites(writes),core_options=cap['core_options'],
            stop_when=lambda:bool(failure) or done is not None and observed>=done+40)
    result=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),
        outside=a.outside,variant=a.variant,sms_reference=a.sms_reference,poor_sms_bitmap_exact_frame=poor_matched,poor_sms_bitmap_sha256=poor_bitmap,source_prefix=a.prefix,rom_sha256=cap['rom_sha256'],complete_frame=done,
        admission_frame=admission,admission_cost=10*round_number if admission else 0,outcome=outcome,outcomes=outcomes,requested_rounds=a.rounds,decline_frame=decline,
        lucky_card_observed=lucky_seen,initial_wait=a.initial_wait,
        poor_text_observed=poor,gold_before=initial[0xdd],gold_after=state['gold'],text_entries=entries,draws=draws,last_state={k:v for k,v in state.items() if k not in ('tilemap','cells')},
        primary_state_imports=0,new_assistance_writes=0,sram_checkpoint_injection=False,
        scope='Actual native MD draws, confirmations, replay choices and money; text entries are read-only observations of native modal/index transitions. No RNG/resource/quest edits. Selected draws do not exhaust every RNG outcome.')
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(v) for v in presses]
    (out/'capture.json').write_text(json.dumps(actual,indent=2)+'\n')
    for name,value in [('report',result),('controls',controls)]:(out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    if writes:
        (out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(result),flush=True)
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
