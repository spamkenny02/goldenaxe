"""Native contact plans, exact played SMS hint bitmaps, and actual stairs/exits."""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk
from md_readonly_view import md_to_sms_view
from validate_playable_sprite_limit import symbols
import hashlib
from rebase_natural_campaign import evidence

dialogue_events=[]


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',required=True)
    p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--prefix',required=True)
    p.add_argument('--trial',required=True);p.add_argument('--plan',required=True);p.add_argument('--sms-reference');p.add_argument('--single-ack-reference',action='store_true');a=p.parse_args()
    plan=json.loads(a.plan);steps=plan['steps'];assert steps and all(s['kind'] in ('silent','travel','talk') for s in steps)
    has_talk=any(s['kind']=='talk' for s in steps);expected_bitmaps={};expected_raw={};samples={}
    assert not has_talk or a.sms_reference,'Talk plans require an actually played SMS reference'
    rom=ROOT/a.rom;sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    source=ROOT/'validation/natural-dungeon-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and not prior['failure'] and cap['sram_input'] is None
    outside=prior['house_outside'];start=cap['frames'];initial=md_to_sms_view((source/f'ram_{start:05d}.bin').read_bytes(),sy)
    assert hashlib.sha256(rom.read_bytes()).hexdigest()==cap['rom_sha256']
    if a.sms_reference:
        reference=ROOT/'validation'/a.sms_reference;sr=json.loads(evidence(reference/'report.json'))
        assert sr['passed']
        if a.single_ack_reference:
            assert outside==0xc7 and sr['last_state']['room']==outside and sr['text_pc']==0x905b and sr['rendered_and_acknowledged']
            assert sr['inventory_actor_health_and_quest_writes']==0 and initial[0xe8] and not initial[0x100+outside]&2
            assert steps==[dict(kind='travel',room=0x1f,point=[104,24],direction=0,target_room=15),dict(kind='talk',room=15,point=[104,56],text_pc=0x905b),dict(kind='travel',room=15,point=[104,152],direction=1,target_room=0x1f),dict(kind='travel',room=0x1f,point=[136,160],direction=1,target_room=outside)]
        else:assert sr['outside']==outside and sr['plan']==plan and (has_talk or initial[0x100+outside]&2)
        if has_talk:
            observations=json.loads(evidence(reference/'dialogue_observations.json'))['events']
            previous=0
            for i,step in enumerate(steps):
                if a.single_ack_reference and step['kind']!='talk':continue
                finish=dict(frame=sr['complete_frame']) if a.single_ack_reference else next(row for row in sr['completed'] if row['step']==i)
                if step['kind']=='talk':
                    entry=next(row for row in sr['text_entries'] if row['text_pc']==step['text_pc'] and previous<=row['frame']<finish['frame'])
                    if a.single_ack_reference:assert any(e['event_pc'] in (0x50c,0x524) and e['text_pc']==step['text_pc'] and e['room']==15 and (e['x'],e['y'])==(104,56) for e in observations)
                    completion=[e for e in observations if e['event_pc']==0x627a and entry['frame']<=e['frame']<finish['frame']][-1]
                    expected_bitmaps[i]=completion['post_frame_bitmap_sha256']
                    expected_raw[i]=evidence(reference/f'ram_{completion["frame"]+1:05d}.bin')[0x1100:0x1510]
                    assert hashlib.sha256(expected_raw[i]).hexdigest()==expected_bitmaps[i]
                previous=finish['frame']
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],min(last,start),k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix)
    out=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not out.exists()
    state={};captures={start};cursor=0;index=0;direction=0;contact=None;active=None;rendered=False
    completed=[];entries=[];done=None;observed=0;failure=None;matched=None
    def observe(frame,r):
        nonlocal done,observed,failure,active,rendered,matched
        observed=frame
        if frame<start:return
        word=lambda n:r[sy[n]]|(r[sy[n]+1]<<8)
        modal=word('house_dialogue_active') or word('game_state')==22
        talk=index<len(steps) and steps[index]['kind']=='talk'
        if word('item_reward_active') or modal and not talk:failure='unexpected_native_dialogue_or_reward'
        if modal and talk:
            pc=word('house_quest_text_pc')
            if pc!=steps[index]['text_pc']:failure='unexpected_native_quest_text'
            if active is None:
                active=dict(frame=frame,text_pc=pc,x=word('hero_x')>>8,y=word('hero_y')>>8);entries.append(dict(frame=frame,room=word('room_id'),text_pc=pc));captures.add(frame+1)
            bitmap=bytes(r[(sy['scratch']+n)^1] for n in range(1040))
            digest=hashlib.sha256(bitmap).hexdigest();samples.setdefault(index,{}).setdefault(digest,(frame,bitmap))
            if digest==expected_bitmaps[index] and matched is None:matched=frame;rendered=True;captures.add(frame+1)
        if word('sound_unhandled_command'):failure='native_audio_error'
        ready=word('resume_phase')==0 and word('world_graphics_class')==0 and not r[sy['door_transition_loading']^1]
        r=md_to_sms_view(r,sy)
        state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
            x=r[0x313],y=r[0x311],health=r[0x318],modal=bool(modal),tilemap=bytes(r[0x1600:0x1c00]),cells=bytes(r[0x1c00:0x1ca0]))
        if not state['health']:failure='hero_died'
        if index==len(steps) and done is None and state['room']==outside and state['game']==12 and state['hero']==1 and ready:
            assert r[0xcf:0xf3]==initial[0xcf:0xf3],'Contact changed crystals, resources or equipment'
            assert r[0x100:0x200]==initial[0x100:0x200],'Contact changed permanent room flags'
            done=frame;captures.add(frame+10)
    def choose(frame):
        nonlocal cursor,index,direction,contact,active,rendered,failure,matched
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if done or failure:return []
        while cursor<len(dialogue_events):
            e=dialogue_events[cursor];cursor+=1
            if e['frame']<=start:continue
            if e['event_pc'] in (0x50c,0x524):
                entries.append(dict(frame=e['frame'],room=e['room'],text_pc=e['text_pc']))
                if index>=len(steps) or steps[index].get('text_pc')!=e['text_pc']:
                    failure='unexpected_dialogue';return []
                active=e;rendered=False;captures.add(frame+1)
            elif e['event_pc']==0x627a and active is not None:rendered=True;captures.add(frame+1)
        if index>=len(steps):return []
        step=steps[index]
        if step['kind']=='travel' and state['room']==step['target_room']:
            completed.append(dict(step=index,frame=frame,transition=True));index+=1;contact=None;active=None;return []
        if state['room']!=step['room'] or state['game'] not in (12,22):return []
        if contact is not None and step['kind']=='travel':return [4+step.get('direction',0)]
        if active is not None:
            if has_talk:
                if state['modal']:
                    if matched is not None and frame>=matched+30:return [8] if frame%4==0 else []
                    return [8] if frame-active['frame']>180 and frame%60==0 else []
                if matched is None:failure='dialogue_closed_without_exact_sms_bitmap';return []
                if state['game']==12 and state['hero']==1 and not state['counter'] and (state['x'],state['y'])!=(active['x'],active['y']):
                    completed.append(dict(step=index,frame=frame,text_pc=active['text_pc'],rendered=True,bitmap_exact_bytes=1040,bitmap_exact_frame=matched,sms_bitmap_sha256=expected_bitmaps[index]));index+=1;active=None;contact=None;matched=None;rendered=False;direction=1;return []
                return [5]
            if rendered and frame-active['frame']>=160:
                if state['game']==12 and state['hero']==1 and not state['counter'] and (state['x'],state['y'])!=(active['x'],active['y']):
                    completed.append(dict(step=index,frame=frame,text_pc=active['text_pc'],rendered=True))
                    index+=1;active=None;contact=None;direction=1;return []
                return [5]
            return [8] if frame-active['frame']>=140 and frame%40==0 else []
        if state['game']!=12 or state['hero'] not in (0,1):return []
        if contact is not None and step['kind']=='silent':
            if frame-contact['frame']>=90:
                completed.append(dict(step=index,frame=frame,silent_contact=True,contact=contact))
                index+=1;contact=None;direction=1;return []
            return [4]
        if state['counter']:return [4+direction]
        point=state['x'],state['y'];target=tuple(step['point'])
        if point==target:
            if contact is None:contact=dict(frame=frame,point=list(point),cells_hex=state['cells'].hex());captures.add(frame+1)
            direction=step.get('direction',0);return [4+direction]
        path=walk(state['tilemap'],point,lambda q:q==target)
        if path:direction=path[0];return [4+direction]
        failure='contact_point_unreachable';return []
    def control(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    with contextlib.redirect_stdout(io.StringIO()):
        run(rom,start+9000,out,captures,cap['presses'],skip_intro=False,
            input_provider=control,ram_observer=observe,ram_writes=FrameWrites(writes),core_options=cap['core_options'],
            stop_when=lambda:bool(failure) or done is not None and observed>=done+10)
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(v) for v in presses]
    (out/'capture.json').write_text(json.dumps(actual,indent=2)+'\n')
    if failure and samples:
        diagnostic=[]
        for i,values in samples.items():
            best=min(values.values(),key=lambda item:sum(a!=b for a,b in zip(item[1],expected_raw[i])))
            frame,bitmap=best;differences=[dict(offset=n,sms=a,md=b) for n,(a,b) in enumerate(zip(expected_raw[i],bitmap)) if a!=b]
            (out/f'closest-native-step{i}.bin').write_bytes(bitmap);(out/f'expected-sms-step{i}.bin').write_bytes(expected_raw[i])
            diagnostic.append(dict(step=i,frame=frame,unique_bitmaps=len(values),different_bytes=len(differences),differences=differences))
        (out/'bitmap-differences.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
    result=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),
        rom_sha256=cap['rom_sha256'],sms_reference=a.sms_reference,variant='quest_hint_contact' if has_talk else 'post_reward_silent_return',source_prefix=a.prefix,outside=outside,plan=plan,completed=completed,text_entries=entries,
        last_state={k:v for k,v in state.items() if k not in ('cells','tilemap')},
        complete_frame=done,resources_and_flags_unchanged=done is not None,primary_state_imports=0,new_assistance_writes=0,
        scope='Actual contacts and room transitions, silent contact with no native dialogue or item-reward state, ordinary exit. No new resource, actor or quest writes.')
    for name,value in [('report',result),('controls',controls)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    if writes:(out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(result),flush=True)
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
