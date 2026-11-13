"""Actual MD merchant choices, exact source result bitmap and native resources."""
import argparse,contextlib,io,json,hashlib
from validate_playable_sprite_limit import symbols
from md_readonly_view import md_to_sms_view
from rebase_natural_campaign import evidence
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk

dialogue_events=[]
OUTCOMES={0x8bc2:'buy',0x8bcd:'poor',0x8bea:'owned',0x8c01:'better',0x8c45:'full'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--sms-reference',required=True)
    p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--prefix',required=True)
    p.add_argument('--trial',required=True);p.add_argument('--choices',required=True)
    p.add_argument('--refill-gold',action='store_true',help='Explicit user-authorized currency-assisted component test, never a campaign proof')
    p.add_argument('--budget',type=int,default=18000);a=p.parse_args()
    assert not a.refill_gold or a.sms_reference=='natural-service-route/sms-npc-key-capacity99-01','Only the explicitly isolated99-key currency component is supported'
    rom=ROOT/a.rom;sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    ref=ROOT/'validation'/a.sms_reference;sr=json.loads(evidence(ref/'report.json'));assert sr['passed']
    se=json.loads(evidence(ref/'dialogue_observations.json'))['events'];bitmaps={}
    for trade in sr['completed']:
        entry=next(e for e in se if e['frame']==trade['frame'] and e['event_pc'] in (0x50c,0x524) and e['text_pc']==trade['text_pc'])
        finish=next(e for e in se if e['event_pc']==0x6e3 and e['frame']>entry['frame'] and e['caller']==entry['caller'] and e['stack_pointer']==entry['stack_pointer'])
        bitmaps[trade['expect']]=finish['post_frame_bitmap_sha256']
    choices=json.loads(a.choices);assert choices==sr['choices'];source=ROOT/'validation/natural-dungeon-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and not prior['failure'] and cap['sram_input'] is None
    outside=prior['house_outside'];house=prior['house_target'];start=cap['frames']
    assets=json.loads((ROOT/'analysis/merchant_assets.json').read_bytes())
    _,mode,parameter=next(t for t in assets['towns'] if t[0]==outside)
    _,nx,ny=next(t for t in assets['nodes'] if t[0]==house)
    assert hashlib.sha256(rom.read_bytes()).hexdigest()==cap['rom_sha256'] and outside==sr['outside']
    initial=md_to_sms_view((source/f'ram_{start:05d}.bin').read_bytes(),sy);expected=bytearray(initial)
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],min(last,start),k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=FrameWrites(prefix_writes(source,cap,a.assisted_prefix));gold_refills=[];refilled_index=None
    out=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not out.exists()
    state={};cursor=0;index=0;direction=0;phase='walk';phase_at=start;wanted=None;result=None
    completed=[];entries=[];captures={start};done=None;failure=None;observed=0;raw_now=None
    def offer(selection):
        assert 0<=selection<(1 if mode==1 else 3)
        if mode==0:return assets['goods'][parameter][selection][:2]
        if mode==1:return 12,parameter
        return 0x100+[16,32,64][selection],[20,30,50][selection]
    def prepare():
        nonlocal wanted
        selection=choices[index]['selection'];item,price=offer(selection)
        refusal=('better' if item==25 and expected[0xf2]>2 else 'owned' if item==25 and expected[0xf2]==2 else
            'full' if item==27 and expected[0x318]==expected[0xda] or item==30 and expected[0xde]>=99 or item>=0x100 and expected[0xdb]==expected[0xdc] else
            'owned' if item in (6,13,12) and expected[{6:0xe2,13:0xe9,12:0xe8}[item]] else
            'poor' if expected[0xdd]<price else 'buy')
        assert refusal==choices[index]['expect'],(choices[index],refusal)
        wanted=dict(selection=selection,item=item,price=price,expect=refusal,gold_before=expected[0xdd])
        if refusal=='buy':
            expected[0xdd]-=price
            if item==25:expected[0xf2]=2
            elif item==27:expected[0x318]=expected[0xd9]=expected[0xda]
            elif item==30:expected[0xde]+=1
            elif item>=0x100:expected[0xdb]=min(expected[0xdc],expected[0xdb]+item-0x100)
            else:expected[{6:0xe2,13:0xe9,12:0xe8}[item]]=1
    def check_resources(raw):
        assert raw[0xcf:0xf3]==expected[0xcf:0xf3],('resource_mismatch',list(raw[0xcf:0xf3]),list(expected[0xcf:0xf3]))
        assert raw[0x318]==expected[0x318],('health_mismatch',raw[0x318],expected[0x318])
    menu_seen=False
    def observe(frame,raw):
        nonlocal observed,failure,done,raw_now,menu_seen
        observed=frame
        if frame<start:return
        word=lambda n:raw[sy[n]]|raw[sy[n]+1]<<8
        r=md_to_sms_view(raw,sy);raw_now=bytes(r)
        if word('game_state')==22 and not menu_seen:
            dialogue_events.append(dict(frame=frame,event_pc=0x524,text_pc=0));menu_seen=True
        if phase=='walk' and word('game_state')!=22:menu_seen=False
        bitmap=hashlib.sha256(bytes(raw[(sy['scratch']+i)^1] for i in range(1040))).hexdigest()
        if wanted is not None and phase=='await' and bitmap==bitmaps[wanted['expect']]:
            dialogue_events.append(dict(frame=frame,event_pc=0x524,text_pc=next(pc for pc,value in OUTCOMES.items() if value==wanted['expect'])))
        state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
            resume=word('resume_phase'),loading=raw[sy['door_transition_loading']^1],graphics=word('world_graphics_class'),audio_error=word('sound_unhandled_command'),x=r[0x313],y=r[0x311],health=r[0x318],selection=word('merchant_selection'),gold=r[0xdd],tilemap=bytes(r[0x1600:0x1c00]))
        if not state['health']:failure='hero_died'
        if state['audio_error']:failure='native_audio_error'
        if index==len(choices) and done is None and state['room']==outside and state['game']==12 and state['hero']==1 and not state['resume'] and not state['loading'] and state['graphics']==0:
            check_resources(r);done=frame;captures.add(frame+10)
    def choose(frame):
        nonlocal cursor,index,direction,phase,phase_at,result,wanted,failure,refilled_index
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if done or failure:return []
        while cursor<len(dialogue_events):
            e=dialogue_events[cursor];cursor+=1
            if e['frame']<=start or e['event_pc'] not in (0x50c,0x524):continue
            entries.append(dict(frame=e['frame'],text_pc=e['text_pc']));captures.add(frame+1)
            if e['text_pc'] in OUTCOMES:
                assert wanted is not None and OUTCOMES[e['text_pc']]==wanted['expect'],(wanted,e['text_pc'])
                result=dict(frame=e['frame'],text_pc=e['text_pc'],sms_bitmap_sha256=bitmaps[wanted['expect']],bitmap_exact_bytes=1040);phase='result';phase_at=frame
            elif phase=='walk':phase='menu';phase_at=frame
        if phase=='result':
            if frame-phase_at<max(240,wanted['price']*2+160):return []
            check_resources(raw_now)
            completed.append(dict(**wanted,**result,verified_frame=frame,gold_after=state['gold']))
            was_purchase=wanted['expect']=='buy'
            index+=1;wanted=None;result=None
            phase=('walk' if mode==1 and was_purchase else 'menu') if index<len(choices) else 'exit'
            phase_at=frame;return []
        if phase in ('menu','await'):
            if phase=='await' or frame-phase_at<180 or frame%20:return []
            if index==len(choices):phase='exit';return [0]
            if wanted is None:
                if a.refill_gold and refilled_index!=index:
                    writes.append((frame+1,sy['hero_gold'],b'\0\xff'));gold_refills.append(frame+1)
                    expected[0xdd]=255;refilled_index=index;return []
                prepare()
            if state['selection']!=wanted['selection']:return [5 if state['selection']<wanted['selection'] else 4]
            captures.add(frame+1);phase='await';phase_at=frame;return [8]
        if state['game']==22:return ([8] if mode==2 and choices[-1]['expect']=='full' else [0]) if phase=='exit' and frame%40==0 else []
        if state['room']!=house or state['game']!=12 or state['hero'] not in (0,1):return []
        if state['counter']:return [4+direction]
        point=state['x'],state['y'];target=(136,160) if phase=='exit' else (nx,ny)
        if point==target:direction=1 if phase=='exit' else 0;return [4+direction]
        path=walk(state['tilemap'],point,lambda q:q==target)
        if path:direction=path[0];return [4+direction]
        failure='merchant_unreachable';return []
    def control(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom,start+a.budget,out,captures,cap['presses'],skip_intro=False,
            input_provider=control,ram_observer=observe,ram_writes=writes,core_options=cap['core_options'],
            stop_when=lambda:bool(failure) or done is not None and observed>=done+10)
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(v) for v in presses]
    if a.refill_gold:actual['currency_assisted_component_test']=True
    (out/'capture.json').write_bytes((json.dumps(actual,indent=2)+'\n').encode())
    report=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),
        rom_sha256=cap['rom_sha256'],sms_reference=a.sms_reference,source_prefix=a.prefix,outside=outside,mode=mode,parameter=parameter,choices=choices,completed=completed,
        text_entries=entries,complete_frame=done,new_assistance_writes=len(gold_refills),primary_state_imports=0,
        currency_assisted_component_test=a.refill_gold,gold_refill_frames=gold_refills,natural_campaign_proof=False,
        last_state={k:v for k,v in state.items() if k!='tilemap'},
        scope='Actual native goods, exact 1040-byte played SMS result bitmap, exact currency/resources and fully settled normal exit. No resource, quest or actor fixture.')
    for name,value in [('report',report),('controls',controls)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    if a.refill_gold:
        report['scope']='Separate user-authorized infinite-currency component test. Keys are bought normally; only currency and inherited approach guard are written. Not an uninterrupted campaign or all-NPC proof.'
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        (out/'controlled_economic_assistance.json').write_text(json.dumps(dict(
            source_prefix='natural-dungeon-route/'+a.prefix,source_frame=start,
            writes=[dict(frame=f,address=addr,data_hex=data.hex()) for f,addr,data in writes],
            inventory_actor_health_and_quest_writes=0,currency_assisted_component_test=True),indent=2)+'\n')
    elif writes:(out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(report),flush=True)
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
