"""Actual money-house contact, exterior exit/re-entry, and once-only return."""
import argparse,contextlib,hashlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from validate_playable_sprite_limit import symbols
from natural_dungeon_combat import walk
from md_readonly_view import md_to_sms_view

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',required=True);p.add_argument('--prefix',required=True);p.add_argument('--trial',required=True);p.add_argument('--outside',type=lambda v:int(v,0),required=True);p.add_argument('--gain',type=int,required=True);p.add_argument('--sms-reference',required=True);p.add_argument('--assisted-prefix',action='store_true');a=p.parse_args()
    source=ROOT/'validation/natural-dungeon-route'/a.prefix;cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes());assert prior['reached_entrance'] and not prior['failure'] and prior['house_target']==0x3f and prior['house_outside']==a.outside and cap['sram_input'] is None
    rom=ROOT/a.rom;digest=hashlib.sha256(rom.read_bytes()).hexdigest();assert digest==cap['rom_sha256'];sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    sr=json.loads((ROOT/'validation'/a.sms_reference/'report.json').read_bytes());assert sr['passed'] and sr['kind']=='gold' and sr['revisit']
    start=cap['frames'];old=json.loads((source/'controls.json').read_bytes());controls=list(old);presses=list(map(tuple,cap['presses']))
    for n,row in enumerate(old):
        end=old[n+1]['frame']-1 if n+1<len(old) else start;presses.extend((row['frame'],min(end,start),key) for key in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix);out=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not out.exists()
    state={};first=None;expected_gold=None;already=False;phase='first';modal_start=None;first_text_pc=None;first_exit=None;reentered=None;contact=None;contact_end=None;away=False;done=None;failure=None;observed=0;direction=0;events=[];captures={start};map_now=b''
    doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors'];door=next(d for d in doors if d['room']==a.outside and d['target']==0x3f);entrance=door['x'],door['y']
    def observe(frame,raw):
        nonlocal first,expected_gold,already,phase,modal_start,first_text_pc,first_exit,reentered,done,failure,observed,map_now
        observed=frame
        if frame<start:return
        word=lambda n:raw[sy[n]]|raw[sy[n]+1]<<8
        state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),gold=word('hero_gold'),magic=word('hero_magic'),modal=word('house_dialogue_active'),resume=word('resume_phase'),loading=raw[sy['door_transition_loading']^1],graphics=word('world_graphics_class'),audio_error=word('sound_unhandled_command'))
        r=md_to_sms_view(raw,sy);map_now=r[0x1600:0x1c00];state['outside_flags']=r[0x100+a.outside]
        if first is None:
            first=dict(state);assert state['room']==0x3f and state['health'];already=bool(state['outside_flags']&2);expected_gold=first['gold'] if already else max(0,min(255,first['gold']+a.gain));phase='return' if already else 'first'
        if not state['health'] or state['game']==20:failure='hero_died'
        if state['audio_error']:failure='native_audio_error'
        if state['magic']!=first['magic']:failure='contact_changed_magic'
        if state['modal'] and phase=='return':failure='reward_return_opened_dialogue'
        if state['modal'] and phase=='first' and modal_start is None:
            modal_start=frame;first_text_pc=word('house_dialogue_index');assert first_text_pc==(0x8df6 if a.gain<0 else 0x8e30);captures.add(frame+1)
        outside_ready=state['room']==a.outside and state['game']==12 and state['hero']==1 and not state['counter'] and not state['resume'] and not state['loading'] and state['graphics']==0
        if outside_ready and state['outside_flags']&2:
            assert state['gold']==expected_gold
            if contact_end is not None and done is None:done=frame;captures.add(frame+80)
            elif not already and first_exit is None:first_exit=frame;phase='reenter';captures.add(frame+1)
        if phase=='reenter' and state['room']==0x3f and state['game']==12 and state['hero']==1 and not state['resume'] and not state['loading']:
            reentered=frame;phase='return';captures.add(frame+1)
        if phase=='return':assert state['gold']==expected_gold and state['outside_flags']&2
        row=dict(state)
        if not events or any(row[k]!=events[-1][k] for k in ('room','game','gold','modal','outside_flags')):events.append(dict(frame=frame,phase=phase,**row))
    def choose(frame):
        nonlocal direction,contact,contact_end,away
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if done or failure:return []
        if phase=='reenter':
            if state['room']!=a.outside or state['game']!=12 or state['hero']!=1 or state['resume'] or state['loading']:return []
            if state['counter']:return [4+direction]
            point=state['x'],state['y']
            if point!=entrance:away=True
            if away:
                path=walk(map_now,point,lambda q:q==entrance)
                if path:direction=path[0];return [4+direction]
                return []
            for d in (1,2,3,0):
                dx,dy=[(0,-8),(0,8),(-8,0),(8,0)][d];target=point[0]+dx,point[1]+dy
                path=walk(map_now,point,lambda q:q==target)
                if path and len(path)==1:direction=d;return [4+d]
            return []
        if state['modal']:return [8] if modal_start is not None and frame-modal_start>=max(220,abs(a.gain)*2+180) and frame%40==0 else []
        if state['room']!=0x3f or state['game']!=12 or state['hero']not in (0,1):return []
        if state['counter']:return [4+direction]
        point=state['x'],state['y']
        if phase=='return' and contact_end is None:
            if state['x']==136 and state['y']<=88:
                if contact is None:contact=frame;captures.add(frame+1)
                if frame-contact<80:return [4]
                contact_end=frame;captures.add(frame+1)
            target=(136,88) if contact_end is None else (136,160)
        else:target=(136,160) if state['outside_flags']&2 else (136,88)
        if point==target:direction=1 if target[1]==160 else 0;return [4+direction]
        path=walk(map_now,point,lambda q:q==target)
        if path:direction=path[0];return [4+direction]
        return []
    def control(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):run(rom,start+6000,out,captures,cap['presses'],skip_intro=False,input_provider=control,ram_observer=observe,ram_writes=FrameWrites(writes),core_options=cap['core_options'],stop_when=lambda:bool(failure) or done is not None and observed>=done+80)
    result=dict(passed=done is not None and not failure,failure=failure or (None if done else 'contact_or_reentry_incomplete'),rom_sha256=digest,sms_reference=a.sms_reference,source_prefix=a.prefix,outside=a.outside,variant='gold_house_and_return',gain=a.gain,previously_collected=already,first_state=first,last_state=state,expected_final_gold=expected_gold,first_text_pc=first_text_pc,first_exterior_exit_frame=first_exit,reentered_frame=reentered,return_contact_start=contact,return_contact_end=contact_end,complete_frame=done,primary_state_imports=0,new_assistance_writes=0,sram_checkpoint_injection=False,scope='Actual once-only money contact where unclaimed, then a real exterior exit/re-entry and silent 80-frame post-reward contact. Previously claimed houses verify the return only; no money, item, actor or quest fixtures.')
    for name,value in [('report',result),('controls',controls),('events',events)]:(out/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())
    if writes:(out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,json.loads((out/'capture.json').read_bytes()))
    print(json.dumps(result),flush=True)
    if not result['passed']:raise SystemExit(1)

if __name__=='__main__':main()
