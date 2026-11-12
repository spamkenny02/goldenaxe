"""Reveal an exterior entrance with the owned Earth spell and ordinary input."""
import argparse,json,sys
from pathlib import Path
import natural_dungeon_route as game
import natural_dungeon_combat as combat
import natural_bell_world_route as persistent
from run_core import ROOT
from archive_lossless_evidence import sha


def reaches_target(tilemap,cells,point,facing,target,level,allow_blocker=False):
    """Propose a cast using the original 3A9A probes and projectile wall test."""
    x,y=point
    probes=[(-12,-4),(-4,-4),(-12,-4),(-12,4),(-12,4),(-4,4),(-4,-4),(-4,4)]
    mutable={0x38,0x85,0x3d,0x13,0x86} if level==2 else {0x13,0x86}
    for _ in range(64):
        if not(8<=x<248 and 0<=y<161):return False
        offset=((y-8)&248)*8+((x>>2)&62)
        if offset+1>=len(tilemap) or tilemap[offset+1]&128:return False
        hit=False;changed=False
        for probe in (facing,facing+4):
            dy,dx=probes[probe];index=((y+dy)&240)|(((x+dx)&255)>>4)
            if index<160 and cells[index] in mutable:
                changed=True;hit|=index==target
        if changed:return hit or allow_blocker
        x+=[0,0,-2,2][facing];y+=[-2,2,0,0][facing]
    return False


def main():
    p=argparse.ArgumentParser(add_help=False);p.add_argument('--earth-world-cell',type=lambda v:int(v,0),required=True)
    a,remaining=p.parse_known_args();sms='--sms' in remaining
    from md_readonly_view import md_to_sms_view
    from validate_playable_sprite_limit import symbols
    sy=None if sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
    outside=int(remaining[remaining.index('--house-outside')+1],0);index=a.earth_world_cell
    flag='--prefix-combat' if '--prefix-combat' in remaining else '--prefix-service'
    family='natural-dungeon-combat' if flag=='--prefix-combat' else 'natural-service-route'
    cap=json.loads((ROOT/'validation'/family/remaining[remaining.index(flag)+1]/'capture.json').read_bytes())
    initial=(ROOT/'validation'/family/remaining[remaining.index(flag)+1]/f'ram_{cap["frames"]:05d}.bin').read_bytes()
    if not sms:initial=md_to_sms_view(initial,sy)
    preexisting=bool(initial[0x100+outside]&1)
    aim_step=16 if not sms and initial[0xee] else 8
    start=cap['frames'];original=game.run;original_render=game.World.render_cells;state={};actual=[];events=[];decisions=[];result={};opened=None;approached=False;direction=0;sequence=False
    entry_direction=int(remaining[remaining.index('--door-entry-direction')+1]) if '--door-entry-direction' in remaining else 0
    cast=((index&15)*16+8+[0,0,16,-16][entry_direction],(index&240)+[24,8,16,16][entry_direction])
    behind=(cast[0]+[0,0,aim_step,-aim_step][entry_direction],cast[1]+[aim_step,-aim_step,0,0][entry_direction])
    house=int(remaining[remaining.index('--house-target')+1],0)
    goal=game.World(house_outside=outside,house_target=house).goal
    mouth=(goal['x']-[0,0,-8,8][entry_direction],goal['y']-[-8,8,0,0][entry_direction])
    assert 8<=cast[0]<=248 and 8<=cast[1]<=160
    candidates=[];cast_direction=entry_direction;terrain_candidates_generated=False;back_reachable=True;turning=False;turn_shot_started=False
    for facing in [entry_direction]+[d for d in range(4) if d!=entry_direction]:
        origin=((index&15)*16+8+[0,0,16,-16][facing],(index&240)+[24,8,16,16][facing])
        for n in range(5):
            candidates.append((origin[0]+[0,0,aim_step,-aim_step][facing]*n,origin[1]+[aim_step,-aim_step,0,0][facing]*n,facing))
    def proposed_render(world,room,cells,meta=None):
        if room==outside:
            flags=bytearray(256);flags[outside]=1
            cells=persistent.project_persisted_cells(world,room,cells,flags)
        return original_render(world,room,cells,meta)
    def wrapped(*args,**kwargs):
        result['folder']=Path(args[2]);base_observe=kwargs['ram_observer'];base_control=kwargs['input_provider']
        def observe(f,r):
            nonlocal opened,sequence,approached
            base_observe(f,r)
            if f<start:return
            if not sms:
                word=lambda n:int.from_bytes(bytes(r[(sy[n]+i)^1] for i in range(2)),'big')
                state.update(resume_phase=word('resume_phase'),door_loading=r[sy['door_transition_loading']^1])
                r=md_to_sms_view(r,sy)
            old_cells=state.get('cells')
            state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],
                x=r[0x313],y=r[0x311],direction=r[0x30a],selected=r[0xdf],slot=r[0xa0],level=r[0xe5],magic=r[0xdb],
                flags=r[0x100+outside],cell=r[0x1c00+index],spell=r[0x330],terrain=r[0x41],tilemap=bytes(r[0x1600:0x1c00]),cells=bytes(r[0x1c00:0x1ca0]))
            if state['room']==outside and state['game']==12:
                assert state['level'] and state['magic']>=0
                row={k:v for k,v in state.items() if k not in ('tilemap','cells')}
                if not events or any(row[k]!=events[-1][k] for k in ['flags','cell','selected','magic']):events.append(dict(frame=f,**row));args[3].add(f+1)
                if state['flags']&1 and opened is None:opened=dict(frame=f,**row)
                if old_cells is not None and old_cells!=state['cells'] and not state['flags']&1:
                    changed=[n for n,(a,b) in enumerate(zip(old_cells,state['cells'])) if a!=b]
                    events.append(dict(frame=f,**row,excavation_cells_changed=changed))
                    args[3].add(f+1)
                    if not turning:sequence=False;approached=False
        def control(f):
            nonlocal approached,direction,sequence,cast,behind,cast_direction,terrain_candidates_generated,back_reachable,turning,turn_shot_started
            settled=(state.get('game')==12 and state.get('hero')==1 and not state.get('counter')
                     and not state.get('resume_phase',0) and not state.get('door_loading',0))
            if f>start and state.get('room')==outside and settled and not terrain_candidates_generated:
                # Some entrances require opening an approach through several
                # breakable rocks, rather than shooting the marked rock along
                # a single straight ray (notably E1).
                rocks=[n for n,b in enumerate(state['cells']) if b in (0x13,0x38,0x3d,0x85,0x86) and n!=index]
                rocks.sort(key=lambda n:abs((n&15)-(index&15))+abs((n>>4)-(index>>4)))
                for rock in rocks:
                    for facing in range(4):
                        origin=((rock&15)*16+8+[0,0,16,-16][facing],(rock&240)+[24,8,16,16][facing])
                        for n in range(5):candidates.append((origin[0]+[0,0,aim_step,-aim_step][facing]*n,origin[1]+[aim_step,-aim_step,0,0][facing]*n,facing))
                terrain_candidates_generated=True
            if f>start and state.get('room')==outside and settled and state['terrain'] not in (3,5) and not sequence and opened is None:
                for allow_blocker,cx,cy,facing in [(allow,*q) for allow in (False,True) for q in candidates]:
                    candidate=(cx,cy)
                    if not (8<=candidate[0]<=248 and 8<=candidate[1]<=160):continue
                    if reaches_target(state['tilemap'],state['cells'],candidate,facing,index,state['level'],allow_blocker):
                        approach=combat.walk(state['tilemap'],(state['x'],state['y']),lambda q:q==candidate)
                        if approach is not None:
                            back=(candidate[0]+[0,0,aim_step,-aim_step][facing],candidate[1]+[aim_step,-aim_step,0,0][facing])
                            # Collision can be asymmetric at rocks: being able
                            # to back away does not guarantee a return step.
                            back_reachable=(combat.walk(state['tilemap'],candidate,lambda q:q==back) is not None
                                and combat.walk(state['tilemap'],back,lambda q:q==candidate) is not None)
                            if not sms and not back_reachable and not (approach and approach[-1]==facing or not approach and state['direction']==facing):
                                # Never repeatedly spend MP trying to turn
                                # against a blocked corner while pressing C.
                                # Use a stance whose approach already faces
                                # the shot, or one with a real retreat step.
                                continue
                            cast=candidate;cast_direction=facing;behind=back;sequence=True;turning=False
                            decisions.append(dict(frame=f,cast=cast,facing=facing,behind=behind,back_reachable=back_reachable,allow_blocker=allow_blocker))
                            break
            active=f>start and sequence and state.get('room')==outside
            wanted=5 if sequence and not opened else 1
            if f>start and state.get('room')==outside and (state['selected']!=wanted or state['game']==16):
                # The ordinary route may still need to chop a path through
                # bushes. Never let its axe inputs cast Earth repeatedly.
                value=[]
                if f%20==0:
                    if state['game']==12 and state['hero']==1:value=[0]
                    elif state['game']==16:
                        if state['selected']==wanted:value=[0]
                        elif state['slot']//4!=wanted//4:value=[5 if state['slot']//4<wanted//4 else 4]
                        elif state['slot']%4!=wanted%4:value=[7 if state['slot']%4<wanted%4 else 6]
                        else:value=[8]
            elif not active:value=base_control(f)
            elif turning:
                # A held attack button lets the original move routine change
                # facing without walking after the casting animation. This
                # uses one real extra spell when there is no rear stance.
                if state['hero']==11 or state['spell']:turn_shot_started=True
                if turn_shot_started and state['hero']==1 and state['direction']==cast_direction:
                    turning=False;value=[]
                else:value=[8,4+cast_direction] if turn_shot_started and state['hero']==1 else [8]
            elif state['game']!=12 or state['hero'] not in (0,1):value=[]
            elif state['spell']:value=[]
            elif opened:
                point=(state['x'],state['y']);value=[]
                if state['counter']:value=[4+direction]
                elif point==mouth:direction=entry_direction;value=[4+direction]
                else:
                    path=combat.walk(state['tilemap'],point,lambda q:q==mouth)
                    if path:direction=path[0];value=[4+direction]
            elif (state['x'],state['y'])==cast and state['direction']==cast_direction:value=[] if state['counter'] or f%3==0 else [8]
            elif state['counter']:value=[4+direction]
            elif (state['x'],state['y'])==cast:
                # Turning with a direction also walks (or slides) in the SMS.
                # Back up to the reachable stance, then approach in the actual
                # cast direction instead of oscillating across the cast point.
                if back_reachable:approached=False;direction=cast_direction^1;value=[4+direction]
                else:turning=True;turn_shot_started=False;value=[8]
            else:
                point=(state['x'],state['y'])
                if point==behind:approached=True
                path=combat.walk(state['tilemap'],point,lambda q:q==(cast if approached else behind));value=[]
                if path is None:path=combat.walk(state['tilemap'],point,lambda q:q==cast)
                if path is None:
                    # Reconsider the stance against the current map rather
                    # than waiting forever at an approach that is no longer
                    # reachable after the room settles.
                    sequence=False;approached=False;value=[]
                if path:direction=path[0];value=[4+direction]
            if not actual or actual[-1]['buttons']!=list(value):actual.append(dict(frame=f,buttons=list(value)))
            return value
        kwargs.update(ram_observer=observe,input_provider=control);return original(*args,**kwargs)
    game.run=wrapped;game.World.render_cells=proposed_render;sys.argv=[sys.argv[0]]+remaining
    try:persistent.main()
    finally:game.run=original;game.World.render_cells=original_render
    folder=result['folder'];report=json.loads((folder/'route_report.json').read_bytes())
    assert not report['reached_entrance'] or opened is not None
    report.update(earth_exterior_opened=opened,earth_exterior_cell=index,earth_exterior_preexisting_in_prefix=preexisting,earth_exterior_new_resource_writes=0,
                  earth_controller_aim_step=aim_step,earth_exterior_driver_sha256=sha(Path(__file__).read_bytes()),earth_cast_position=cast,earth_cast_direction=cast_direction)
    for name,value in [('controls',actual),('earth_world_events',events),('earth_controller_decisions',decisions),('route_report',report)]:
        (folder/(name+'.json')).write_bytes((json.dumps(value,indent=2)+'\n').encode())


if __name__=='__main__':main()
