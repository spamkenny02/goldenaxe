"""Actual MD service refusal, unchanged resources, source text and walking exit."""
import argparse,contextlib,hashlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk
from validate_playable_sprite_limit import symbols
def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);p.add_argument('--trial',required=True);p.add_argument('--outside',type=lambda x:int(x,0),required=True);p.add_argument('--kind',choices=['merchant','healer','save'],required=True);p.add_argument('--sms-reference',required=True);p.add_argument('--assisted-prefix',action='store_true');a=p.parse_args()
    source=ROOT/'validation/natural-dungeon-route'/a.prefix;cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes());assert prior['reached_entrance'] and prior['failure'] is None and prior['house_outside']==a.outside and cap['sram_input'] is None
    reference=ROOT/'validation'/a.sms_reference;sr=json.loads((reference/'report.json').read_bytes());assert sr['passed'] and sr['outside']==a.outside and sr['house']==prior['house_target'] and sr['kind']==a.kind and sr['variant']=='refusal'
    expected_bitmap=None
    if a.kind!='merchant':
        events=json.loads((reference/'dialogue_observations.json').read_bytes())['events'];pc={'healer':0x8cc7,'save':0x8db6}[a.kind]
        contact=next(e for e in sr['text_entries'] if e['text_pc']==pc)
        entry=next(e for e in events if e['event_pc'] in (0x50c,0x524) and e['text_pc']==pc and e['frame']==contact['frame'] and e['outside']==a.outside)
        # 0524 is the common/service formatter. Match its actual outer return;
        # earlier prefix conversations and recursive name returns are excluded.
        finish=next(e for e in events if e['event_pc']==0x6e3 and e['frame']>entry['frame'] and e['caller']==entry['caller'] and e['stack_pointer']==entry['stack_pointer'])
        expected_bitmap=finish['post_frame_bitmap_sha256']
    rom=ROOT/a.rom;digest=hashlib.sha256(rom.read_bytes()).hexdigest();assert digest==cap['rom_sha256'];sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    start=cap['frames'];presses=list(map(tuple,cap['presses']));prior_controls=json.loads((source/'controls.json').read_bytes())
    for i,row in enumerate(prior_controls):
        stop=prior_controls[i+1]['frame']-1 if i+1<len(prior_controls) else start
        presses.extend((row['frame'],min(stop,start),k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix);house=prior['house_target'];_,nx,ny=next(n for n in json.loads((ROOT/f'analysis/{a.kind}_assets.json').read_bytes())['nodes'] if n[0]==house)
    out=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not out.exists();state={};first=None;contact=None;confirm_no=None;cancel=None;matched=None;declined=None;departure=False;origin=None;done=None;failure=None;observed=0;direction=0;controls=[];events=[];captures=set()
    def observe(frame,raw):
        nonlocal observed,first,contact,matched,declined,origin,done,failure
        observed=frame
        if frame<start:return
        data=lambda n,k,off=0:bytes(raw[(sy[n]+off+i)^1] for i in range(k));word=lambda n:int.from_bytes(data(n,2),'big')
        state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),max_magic=word('hero_max_magic'),gold=word('hero_gold'),keys=word('hero_keys'),items=data('hero_items',17).hex(),basic=word('hero_basic_level'),armor=word('hero_armor_level'),shield=word('hero_shield_level'),weapon=word('hero_weapon_level'),yes=word('save_yes'),phase=word({'merchant':'merchant_phase','healer':'healer_phase','save':'save_service_phase'}[a.kind]),modal=word('house_dialogue_active'),audio_error=word('sound_unhandled_command'),no_cursor=data('sms_vram',2,0x3c74)==bytes.fromhex('8219'),tilemap=data('sms_vram',1536,0x3800))
        if first is None:first={n:state[n] for n in ('health','max_health','magic','max_magic','gold','keys','items','basic','armor','shield','weapon')}
        if not state['health'] or state['game']==20:failure='hero_died'
        if state['audio_error']:failure='native_audio_error'
        if any(state[n]!=v for n,v in first.items()):failure='refusal_changed_resources'
        if state['game']==22 and contact is None:contact=frame;events.append(dict(frame=frame,event='service_contact'));captures.add(frame+1)
        if contact and expected_bitmap and matched is None and hashlib.sha256(data('scratch',1040)).hexdigest()==expected_bitmap:matched=frame;events.append(dict(frame=frame,event='sms_decline_bitmap_exact'));captures.add(frame+1)
        if confirm_no is not None and state['phase']==(3 if a.kind=='healer' else 5) and declined is None:declined=frame
        if state['room']==a.outside and state['game']==12 and state['hero'] in (0,1) and contact:
            if origin is None:origin=(state['x'],state['y'])
            if abs(state['x']-origin[0])+abs(state['y']-origin[1])>=8 and done is None:done=frame;captures.add(frame+40)
    def choose(frame):
        nonlocal confirm_no,cancel,departure,direction
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if failure or done is not None:return []
        if state.get('room')==a.outside:return [5] if state['game']==12 and state['hero'] in (0,1) else []
        if contact is not None and state['game']==22:
            if a.kind=='merchant':
                if frame%40:return []
                cancel=frame;return [0]
            if declined is not None:return [8] if matched is not None and frame%40==0 else []
            if frame-contact<160 or frame%20:return []
            if state['yes']==0 and state['no_cursor']:
                confirm_no=frame;events.append(dict(frame=frame,event='confirm_actual_no'));return [8]
            return [5]
        if contact is not None and state['game']==12 and state['hero'] in (0,1):departure=True
        if state['room']!=house or state['game']!=12 or state['hero'] not in (0,1):return []
        if state['counter']:return [4+direction]
        point=(state['x'],state['y']);target=(136,160) if departure else (nx,ny)
        if point==target:direction=1 if departure else 0;return [4+direction]
        path=walk(state['tilemap'],point,lambda q:q==target)
        if path:direction=path[0];return [4+direction]
        return []
    def controller(frame):
        buttons=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=buttons):controls.append(dict(frame=frame,buttons=buttons))
        return buttons
    with contextlib.redirect_stdout(io.StringIO()):run(rom,start+6000,out,captures,cap['presses'],skip_intro=False,input_provider=controller,ram_observer=observe,ram_writes=FrameWrites(writes),core_options=cap['core_options'],stop_when=lambda:bool(failure) or done is not None and observed>=done+40)
    passed=done is not None and not failure and (cancel is not None if a.kind=='merchant' else confirm_no is not None and declined is not None and matched is not None)
    result=dict(passed=passed,failure=failure or (None if passed else 'missing_refusal_text_or_movement'),rom_sha256=digest,sms_reference=a.sms_reference,source_prefix=a.prefix,outside=a.outside,house=house,kind=a.kind,variant='refusal',initial_resources=first,resources_unchanged=not failure,service_contact_frame=contact,confirm_no_frame=confirm_no,cancel_frame=cancel,sms_decline_bitmap_sha256=expected_bitmap,sms_decline_bitmap_exact_frame=matched,complete_frame=done,last_state={k:v for k,v in state.items() if k!='tilemap'},new_assistance_writes=0,primary_state_imports=0,sram_checkpoint_injection=False,scope='Actual native refusal and moving exterior return. Healer/save require explicit visible No and exact final SMS refusal bitmap; merchant proves Cancel and unchanged resources, not every panel/timing pixel.')
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=presses;(out/'capture.json').write_bytes((json.dumps(actual,indent=2)+'\n').encode())
    for name,value in [('report',result),('controls',controls),('events',events)]:(out/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
    if writes:(out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(result),flush=True)
    if not passed:raise SystemExit(1)
if __name__=='__main__':main()
