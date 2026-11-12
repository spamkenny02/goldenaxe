"""Extend an exact recorded conversation through completed exit and actual walking."""
import argparse,contextlib,hashlib,io,json
from pathlib import Path
from run_core import ROOT,run,FrameWrites,compile_fixed_inputs
from assisted_prefix import prefix_writes,recording
from validate_playable_sprite_limit import symbols
from natural_dungeon_combat import walk
import natural_dungeon_combat as navigation
def main():
    p=argparse.ArgumentParser();p.add_argument('--trace',required=True);p.add_argument('--rom',required=True);p.add_argument('--trial',required=True);a=p.parse_args()
    source=ROOT/'validation'/a.trace;cap=json.loads((source/'capture.json').read_bytes());prior=json.loads((source/'report.json').read_bytes());assert prior['passed'] and cap['sram_input'] is None
    rom=ROOT/a.rom;assert hashlib.sha256(rom.read_bytes()).hexdigest()==cap['rom_sha256'];start=cap['frames'];initial=(source/f'ram_{start:05d}.bin').read_bytes();sy=symbols(ROOT/'megadrive/out/release/symbol.txt')
    writes=prefix_writes(source,cap,bool(cap['test_ram_writes']));controls=json.loads((source/'controls.json').read_bytes());presses=list(map(tuple,cap['presses']))
    for i,row in enumerate(controls):
        stop=controls[i+1]['frame']-1 if i+1<len(controls) else start
        presses.extend((row['frame'],min(stop,start),k) for k in row['buttons'])
    masks=compile_fixed_inputs(presses,start);controls=list(controls);out=ROOT/'validation/natural-service-route'/('md-'+a.trial);assert not out.exists()
    state={};ready=None;origin=None;moved=None;done=None;observed=0;direction=None;failure=None;captures=set();events=[]
    def observe(frame,raw):
        nonlocal ready,origin,moved,done,observed,failure
        observed=frame
        if frame<start:return
        if frame==start:assert raw==initial,'Recorded prefix must reproduce exactly before extending'
        data=lambda n,k,off=0:bytes(raw[(sy[n]+off+i)^1] for i in range(k));w=lambda n:int.from_bytes(data(n,2),'big')
        items=data('hero_items',17);navigation.CANOE_OWNED=bool(items[12]);navigation.SHIP_OWNED=bool(items[16])
        state.update(weapon=w('hero_weapon_level'),selected=w('hero_selected_item'),cells=data('scratch',160,0x800),room=w('room_id'),game=w('game_state'),hero=w('hero_state'),counter=w('hero_counter'),x=w('hero_x')>>8,y=w('hero_y')>>8,health=w('hero_health'),resume_phase=w('resume_phase'),graphics_class=w('world_graphics_class'),door_loading=data('door_transition_loading',1)[0],audio_error=w('sound_unhandled_command'),tilemap=data('sms_vram',1536,0x3800))
        if not state['health'] or state['game']==20:failure='hero_died'
        if state['audio_error']:failure='native_audio_error'
        settled=state['room']==prior['outside'] and state['game']==12 and state['hero']==1 and not state['counter'] and not state['resume_phase'] and not state['door_loading'] and not state['graphics_class']
        if frame>start and settled and ready is None:ready=frame;origin=(state['x'],state['y']);captures.add(frame+1);events.append(dict(frame=frame,event='fully_settled_exterior',**{k:v for k,v in state.items() if k not in ('tilemap','cells')}))
        if ready is not None and moved is None and settled and abs(state['x']-origin[0])+abs(state['y']-origin[1])>=8:moved=frame;done=frame+30;captures.add(done);events.append(dict(frame=frame,event='actual_settled_exterior_movement',x=state['x'],y=state['y']))
    def controller(frame):
        nonlocal direction
        if frame<=start:return [k for k in range(16) if masks[frame]&(1<<k)]
        buttons=[]
        if ready is not None and moved is None and state['room']==prior['outside'] and state['game']==12 and state['hero'] in (0,1) and not state['resume_phase'] and not state['door_loading']:
            if direction is None:
                for d,(dx,dy) in enumerate([(0,-8),(0,8),(-8,0),(8,0)]):
                    if d==0:continue # Clear the exit, do not re-enter the door.
                    target=(state['x']+dx,state['y']+dy)
                    if 16<=target[0]<=240 and 16<=target[1]<=160:
                        route=walk(state['tilemap'],(state['x'],state['y']),lambda q:q==target)
                        if route and len(route)==1:direction=route[0];break
            if direction is not None:buttons=[4+direction]
            elif state['weapon'] and state['selected']==1 and state['hero']==1 and not state['counter']:
                nearby=[n for n,b in enumerate(state['cells']) if 0x80<=b<=0x84 and abs((n&15)*16+8-state['x'])<=32 and abs((n>>4)*16+8-state['y'])<=40]
                if nearby:buttons=[5,8] if frame%3 else []
        if not controls or controls[-1]['buttons']!=buttons:controls.append(dict(frame=frame,buttons=buttons))
        return buttons
    with contextlib.redirect_stdout(io.StringIO()):run(rom,start+1800,out,captures,cap['presses'],skip_intro=False,ram_writes=FrameWrites(writes),ram_observer=observe,input_provider=controller,core_options=cap['core_options'],stop_when=lambda:bool(failure) or done is not None and observed>=done)
    actual=json.loads((out/'capture.json').read_bytes());actual['presses']=presses;(out/'capture.json').write_bytes((json.dumps(actual,indent=2)+'\n').encode())
    initial_health=initial[sy['hero_health']]|(initial[sy['hero_health']+1]<<8)
    result=dict(prior,passed=done is not None and not failure,failure=failure or (None if done else 'settled_exit_or_movement_missing'),last_state={k:v for k,v in state.items() if k not in ('tilemap','cells')},settled_exit_extension_of=a.trace,fully_settled_exit_frame=ready,actual_exterior_movement_frame=moved,complete_frame=moved,post_prefix_health_delta=state['health']-initial_health,scope=prior['scope']+' Extended with an exact-prefix check until resume0/loading0/class0, then real exterior movement and a quiet capture tail. The health delta of this separate exterior-control tail is reported explicitly; no health refill is applied.')
    for name,r in [('report',result),('controls',controls),('settled_exit_events',events)]:(out/(name+'.json')).write_bytes((json.dumps(r,indent=2)+'\n').encode())
    if writes:(out/'assistance.json').write_bytes((source/'assistance.json').read_bytes());recording(out,actual)
    print(json.dumps(result),flush=True)
    if not result['passed']:raise SystemExit(1)
if __name__=='__main__':main()
