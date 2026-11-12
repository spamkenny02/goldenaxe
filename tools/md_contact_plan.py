"""Native silent post-reward contacts and real stairs; any dialogue is a failure."""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from natural_dungeon_combat import walk
from md_readonly_view import md_to_sms_view
from validate_playable_sprite_limit import symbols
import hashlib

dialogue_events=[]


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',required=True)
    p.add_argument('--assisted-prefix',action='store_true');p.add_argument('--prefix',required=True)
    p.add_argument('--trial',required=True);p.add_argument('--plan',required=True);p.add_argument('--sms-reference');a=p.parse_args()
    plan=json.loads(a.plan);steps=plan['steps'];assert steps and all(s['kind'] in ('silent','travel') for s in steps)
    rom=ROOT/a.rom;sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    source=ROOT/'validation/natural-dungeon-route'/a.prefix
    cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'route_report.json').read_bytes())
    assert prior['reached_entrance'] and not prior['failure'] and cap['sram_input'] is None
    outside=prior['house_outside'];start=cap['frames'];initial=md_to_sms_view((source/f'ram_{start:05d}.bin').read_bytes(),sy)
    assert hashlib.sha256(rom.read_bytes()).hexdigest()==cap['rom_sha256']
    if a.sms_reference:
        reference=ROOT/'validation'/a.sms_reference;sr=json.loads((reference/'report.json').read_bytes())
        assert sr['passed'] and sr['outside']==outside and sr['plan']==plan and initial[0x100+outside]&2
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],min(last,start),k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);writes=prefix_writes(source,cap,a.assisted_prefix)
    out=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not out.exists()
    state={};captures={start};cursor=0;index=0;direction=0;contact=None;active=None;rendered=False
    completed=[];entries=[];done=None;observed=0;failure=None
    def observe(frame,r):
        nonlocal done,observed,failure
        observed=frame
        if frame<start:return
        word=lambda n:r[sy[n]]|(r[sy[n]+1]<<8)
        if word('house_dialogue_active') or word('item_reward_active') or word('game_state')==22:failure='unexpected_native_dialogue_or_reward'
        if word('sound_unhandled_command'):failure='native_audio_error'
        ready=word('resume_phase')==0 and word('world_graphics_class')==0 and not r[sy['door_transition_loading']^1]
        r=md_to_sms_view(r,sy)
        state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
            x=r[0x313],y=r[0x311],health=r[0x318],tilemap=bytes(r[0x1600:0x1c00]),cells=bytes(r[0x1c00:0x1ca0]))
        if not state['health']:failure='hero_died'
        if index==len(steps) and done is None and state['room']==outside and state['game']==12 and state['hero']==1 and ready:
            assert r[0xcf:0xf3]==initial[0xcf:0xf3],'Contact changed crystals, resources or equipment'
            assert r[0x100:0x200]==initial[0x100:0x200],'Contact changed permanent room flags'
            done=frame;captures.add(frame+10)
    def choose(frame):
        nonlocal cursor,index,direction,contact,active,rendered,failure
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
    result=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),
        rom_sha256=cap['rom_sha256'],sms_reference=a.sms_reference,variant='post_reward_silent_return',source_prefix=a.prefix,outside=outside,plan=plan,completed=completed,text_entries=entries,
        last_state={k:v for k,v in state.items() if k not in ('cells','tilemap')},
        complete_frame=done,resources_and_flags_unchanged=done is not None,primary_state_imports=0,new_assistance_writes=0,
        scope='Actual contacts and room transitions, silent contact with no native dialogue or item-reward state, ordinary exit. No new resource, actor or quest writes.')
    for name,value in [('report',result),('controls',controls)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    if writes:(out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(result),flush=True)
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
