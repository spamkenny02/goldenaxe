"""Return a genuinely bought apple to Saylun's still unclaimed hidden giver.

Currency assistance remains explicit; no inventory or quest flag is injected.
"""
import argparse,contextlib,io,json
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from continue_sms_plain_house_census import census_world

dialogue_events=[]


def main():
    p=argparse.ArgumentParser();p.add_argument('--sms',action='store_true',required=True);p.add_argument('--trace',required=True);p.add_argument('--trial',required=True);a=p.parse_args()
    source=(ROOT/'validation'/a.trace).resolve();assert source.is_relative_to(ROOT/'validation')
    previous=json.loads((source/'report.json').read_bytes());assert previous['passed'] and previous['currency_assisted_component_test']
    cap=json.loads((source/'capture.json').read_bytes());start=cap['frames'];initial=(source/f'ram_{start:05d}.bin').read_bytes()
    assert initial[0xe8] and not initial[0x1c7]&2
    aid=json.loads((source/'controlled_economic_assistance.json').read_bytes())
    writes=FrameWrites((w['frame'],w['address'],bytes.fromhex(w['data_hex'])) for w in aid['writes'])
    controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        last=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],min(last,start),k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start)
    origin=(int.from_bytes(initial[0xb9:0xbb],'little'),initial[0x313],initial[0x311]);world=None;path=None
    for d in range(4):
        candidate=census_world(initial,0xc7,0x1f,d);route,_=candidate.route(origin)
        if route is not None:world=candidate;path=route;entry_direction=d;break
    assert path is not None
    out=ROOT/'validation/natural-service-route'/('sms-'+a.trial);assert not out.exists()
    state={};cursor=0;waypoint=0;direction=0;phase='world';active=None;rendered=False;done=None;observed=0;failure=None
    captures={start};entries=[];acknowledged=False
    def observe(frame,r):
        nonlocal observed,done,failure
        observed=frame
        if frame<start:return
        state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
            x=r[0x313],y=r[0x311],health=r[0x318],maze=r[0x6c],tilemap=bytes(r[0x1600:0x1c00]))
        if not state['health']:failure='hero_died'
        if done is None and acknowledged and phase=='outside' and state['room']==0xc7 and state['game']==12 and state['hero']==1:
            assert r[0xcf:0xf3]==initial[0xcf:0xf3] and r[0x318]==initial[0x318] and not r[0x1c7]&2
            done=frame;captures.add(frame+10)
        if frame>=start and done is None:writes.append((frame+1,0x305,b'\x81'))
    def choose(frame):
        nonlocal cursor,waypoint,direction,phase,active,rendered,acknowledged,failure,path
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        if done or failure:return []
        while cursor<len(dialogue_events):
            e=dialogue_events[cursor];cursor+=1
            if e['frame']<=start:continue
            if e['event_pc'] in (0x50c,0x524):
                assert e['text_pc']==0x905b,(phase,e['text_pc'])
                active=e;entries.append(dict(frame=e['frame'],text_pc=e['text_pc']));captures.add(frame+1)
            elif e['event_pc']==0x627a and active:rendered=True;captures.add(frame+1)
        if active:
            if rendered and frame-active['frame']>=160:
                if state['hero']==1 and not state['counter'] and (state['x'],state['y'])!=(active['x'],active['y']):
                    acknowledged=True;active=None;phase='leave-basement';direction=1;return []
                return [5]
            return [8] if frame-active['frame']>140 and frame%40==0 else []
        if state['game']!=12 or state['hero'] not in (0,1):return []
        room=state['room'];point=(room,state['x'],state['y'])
        if phase=='world':
            if room==0x1f:phase='stairs';direction=0;return []
            if state['counter']:return [4+direction]
            while waypoint<len(path) and point==tuple(path[waypoint][2][:3]):waypoint+=1
            if waypoint==len(path):direction=entry_direction;return [4+direction]
            if point!=tuple(path[waypoint][0][:3]):
                world.live_room=room;world.live_map=state['tilemap'];path,_=world.route((*point,state['maze']));waypoint=0
                if path is None:failure='no_live_world_route';return []
                if not path:direction=entry_direction;return [4+direction]
            direction=path[waypoint][1];return [4+direction]
        if phase=='stairs' and room==15:phase='talk'
        if phase=='leave-basement' and room==0x1f:phase='outside'
        if phase=='outside' and room==0xc7:return []
        if state['counter']:return [4+direction]
        xy=point[1:]
        if phase=='stairs':
            if xy[0]==104 and xy[1]<=24:direction=0;return [4]
            goal=(104,24)
        elif phase=='talk':goal=(104,56)
        elif phase=='leave-basement':
            if xy[0]==104 and xy[1]>=152:direction=1;return [5]
            goal=(104,152)
        else:
            if xy[0]==136 and xy[1]>=152:direction=1;return [5]
            goal=(136,152)
        if xy==goal:direction=0 if phase in ('stairs','talk') else 1;return [4+direction]
        route=walk(state['tilemap'],xy,lambda q:q==goal)
        if route:direction=route[0];return [4+direction]
        failure='interior_unreachable';return []
    def control(frame):
        value=choose(frame)
        if frame>start and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=frame,buttons=value))
        return value
    from natural_dungeon_combat import walk
    with contextlib.redirect_stdout(io.StringIO()):
        run(ROOT/'input/original.sms',start+20000,out,captures,cap['presses'],skip_intro=False,
            input_provider=control,ram_observer=observe,ram_writes=writes,core_options=cap['core_options'],
            stop_when=lambda:bool(failure) or done is not None and observed>=done+10)
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=[list(v) for v in presses]
    (out/'capture.json').write_text(json.dumps(actual,indent=2)+'\n')
    aid['writes']=[dict(frame=f,address=addr,data_hex=data.hex()) for f,addr,data in writes]
    report=dict(passed=done is not None and not failure,failure=failure or (None if done else 'frame_limit'),
        currency_assisted_component_test=True,natural_campaign_proof=False,source_purchase_trace=a.trace,
        text_entries=entries,text_pc=0x905b,rendered_and_acknowledged=acknowledged,complete_frame=done,
        inventory_actor_health_and_quest_writes=0,last_state={k:v for k,v in state.items() if k!='tilemap'},
        scope='Genuinely purchased apple brought to unclaimed Saylun giver. Declared currency assistance and approach guard only; no inventory or quest fixture.')
    for name,value in [('controlled_economic_assistance',aid),('controls',controls),('report',report)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(report),flush=True)
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
