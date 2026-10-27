"""Controller-only combat, rewards and dungeon traversal from a recorded new game."""
import argparse,collections,contextlib,io,json
from pathlib import Path
from run_core import ROOT,run
from verify_natural_dungeon_route import CASES
from movement_reference import Hero,collision_cache,choose_collision_direction
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes

CANOE_OWNED=False
AVOID_PORTAL_COORDINATES=set()

def walk(tilemap,start,goal,enemies=(),geometry=False):
    queue=collections.deque([start]);parent={start:None};finish=None
    while queue:
        p=queue.popleft()
        if goal(p):finish=p;break
        cache=collision_cache(tilemap,Hero(x=p[0]<<8,y=p[1]<<8),canoe=CANOE_OWNED)
        for d,(dx,dy) in enumerate([(0,-8),(0,8),(-8,0),(8,0)]):
            nxt=p[0]+dx,p[1]+dy
            if nxt in parent or not(8<=nxt[0]<=248 and 8<=nxt[1]<=168):continue
            coordinate=(((nxt[1]-12)&248)<<3)+((((nxt[0]-12)&255)>>2)&62)+126
            if coordinate in AVOID_PORTAL_COORDINATES:continue
            if geometry:
                from natural_combat_aim import contact
                if any(contact(nxt,e,0) if not e.get('hp') else abs(nxt[0]-e['x'])<12 and abs(nxt[1]-e['y'])<12 for e in enemies):continue
            elif any(abs(nxt[0]-e['x'])<12 and abs(nxt[1]-e['y'])<12 for e in enemies):continue
            if choose_collision_direction(d,cache)!=d:continue
            parent[nxt]=(p,d);queue.append(nxt)
    if finish is None:return None
    path=[]
    while parent[finish] is not None:previous,d=parent[finish];path.append(d);finish=previous
    return list(reversed(path))

def attack_position(p,e,reach=24,align=8):
    dx=e['x']-p[0];dy=e['y']-p[1]
    return abs(dx)<=align and reach-12<=abs(dy)<=reach or abs(dy)<=align and reach-12<=abs(dx)<=reach

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sms',action='store_true');parser.add_argument('--pal',action='store_true');parser.add_argument('--trial',required=True);parser.add_argument('--frames',type=int,default=14000);parser.add_argument('--target-room',type=lambda x:int(x,0),default=0x1d4);parser.add_argument('--reach',type=int,default=24);parser.add_argument('--align',type=int,default=8);parser.add_argument('--rooms',help='Comma-separated adjacent room IDs');parser.add_argument('--continue-after-clear',action='store_true',help='Let a scripted wrapper finish its action after room combat has cleared');parser.add_argument('--collect-key',action='store_true');parser.add_argument('--item-first-when-blocked',action='store_true',help='Seek the real reward when enemies cannot yet be reached');parser.add_argument('--collect-item',type=int);parser.add_argument('--collect-gem',action='store_true');parser.add_argument('--exit-dungeon',action='store_true');parser.add_argument('--exit-before-crystal',action='store_true',help='Verify an ordinary supply-trip exit without claiming the dungeon crystal');parser.add_argument('--max-deaths',type=int,default=3,help='Maximum normal Continue retries');parser.add_argument('--avoid-portal-rooms',default='',help='Avoid stepping back onto return portals while fighting/navigating these rooms');parser.add_argument('--defer-puzzles-rooms',default='',help='Walk past optional puzzles in these rooms while following the requested itinerary');parser.add_argument('--doorway-ranges',action='store_true',help='Accept the source doorway span and actual screen boundary,including off-grid approach positions');parser.add_argument('--ignore-inactive-actors',action='store_true',help='Continue walking around actors whose source active/contact bit is clear');parser.add_argument('--rush-rooms',default='',help='Pass through these rooms while avoiding live actors');parser.add_argument('--puzzle-first-when-blocked',action='store_true',help='Try a pending source puzzle when no enemy attack position is reachable');parser.add_argument('--early-boss-side',action='store_true',help='Experimental63/64 side placement and volley evasions');parser.add_argument('--settle-attacks',action='store_true',help='Wait until a walking step ends before starting an attack');parser.add_argument('--collision-aim',action='store_true',help='Aim from original descriptor hit rectangles');parser.add_argument('--equip-axe',action='store_true',help='Equip owned axe via normal inventory buttons');parser.add_argument('--prefix',help='Recorded natural route directory for this ROM');parser.add_argument('--continuation',help='Replay a completed combat trial from boot before extending its route');parser.add_argument('--assisted-prefix',action='store_true',help='Explicitly continue a verified assisted recording');args=parser.parse_args()
    assert args.collect_item is None or 0<=args.collect_item<17
    assert not args.exit_before_crystal or args.exit_dungeon
    itinerary=[int(x,0) for x in args.rooms.split(',')] if args.rooms else list(range(0x1e4,args.target_room-1,-16))
    # Entry is checked against actual replay RAM at prefix_end; support later dungeons.
    assert itinerary and 256<=itinerary[0]<512
    assert (256<=itinerary[-1]<512 and args.target_room<256 if args.exit_dungeon else itinerary[-1]==args.target_room)
    portal_reference=json.loads((ROOT/'analysis/contact_script_reference.json').read_bytes())
    assert portal_reference['source_sha256']==sha((ROOT/'input/original.sms').read_bytes())
    portals={(row['room'],row['destination_room']):row for row in portal_reference['records'] if row['kind']=='moving_aligned_portal'}
    assert all(abs(a-b) in [1,16] or (a,b) in portals for a,b in zip(itinerary,itinerary[1:]))
    rush_rooms={int(x,0) for x in args.rush_rooms.split(',') if x}
    itinerary_index=0
    puzzle_reference=json.loads((ROOT/'analysis/room_puzzles_reference.json').read_bytes())
    assert puzzle_reference['source_sha256']==sha((ROOT/'input/original.sms').read_bytes())
    avoided_portal_rooms={int(v,0) for v in args.avoid_portal_rooms.split(',') if v}
    deferred_puzzles={int(v,0) for v in args.defer_puzzles_rooms.split(',') if v}
    puzzles={r['room']:r for r in puzzle_reference['records'] if r['room'] not in deferred_puzzles}
    region='pal' if args.pal else 'auto';prefix_name=args.continuation or args.prefix or next(a if args.sms else b for r,a,b in CASES if r==region);prefix=ROOT/('validation/natural-dungeon-combat' if args.continuation else 'validation/natural-dungeon-route')/prefix_name
    capture=json.loads((prefix/'capture.json').read_bytes());recorded=json.loads((prefix/'controls.json').read_bytes());prefix_end=capture['frames'];presses=list(map(tuple,capture['presses']))
    prefix_inputs=[()]*(prefix_end+1)
    for n,item in enumerate(recorded):
        end=recorded[n+1]['frame']-1 if n+1<len(recorded) else prefix_end
        if args.continuation:
            prefix_inputs[item['frame']:min(end,prefix_end)+1]=[tuple(item['buttons'])]*(min(end,prefix_end)-item['frame']+1)
        else:presses.extend((item['frame'],min(end,prefix_end),b) for b in item['buttons'] if item['frame']<=prefix_end)
    rom=ROOT/'input/original.sms' if args.sms else ROOT/'gaw-megadrive.bin';sy=None if args.sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
    assert capture['rom_sha256']==sha(rom.read_bytes()) and capture['sram_input'] is None
    inherited_writes=prefix_writes(prefix,capture,args.assisted_prefix)
    tag='sms' if args.sms else 'md';folder=ROOT/f'validation/natural-dungeon-combat/{tag}-{region}-{args.trial}';assert not folder.exists(),folder
    state={};actors=[];loot=[];tilemap=b'';events=[];samples=[];controls=[];captures=set();observed=0;cached=-1;buttons=[];last_direction=0;seen_room=False;seen_enemies=False;cleared=None;failure=None;menu_since=None;deaths=0;last_key=None
    if args.continuation:controls=list(recorded)
    puzzle_goal=None;pilot_decisions=[]
    target_entry_keys=None
    gem_picked_at=None
    exit_reset_seen=False
    boss_dodge_until=0;boss_dodge_x=0;boss_last_shot=-1000
    boss_frames=[];item_picked_at=None;pilot_progress_key=None;pilot_progress_frame=0;exit_dungeon_number=None;exit_max_health=None
    item_reference=json.loads((ROOT/'analysis/item_rewards_reference.json').read_bytes())
    assert item_reference['source_sha256']==sha((ROOT/'input/original.sms').read_bytes())
    rewards={r['room']:r for r in item_reference['records']}
    def observe(f,r):
        global CANOE_OWNED,AVOID_PORTAL_COORDINATES
        nonlocal actors,loot,tilemap,observed,seen_room,seen_enemies,cleared,target_entry_keys,failure,menu_since,deaths,last_key,itinerary_index,gem_picked_at,exit_reset_seen,item_picked_at,pilot_progress_key,pilot_progress_frame,exit_dungeon_number,exit_max_health
        observed=f
        if f<prefix_end:
            # Prefix inputs are fixed. Preserve historical target-enemy
            # detection without decoding unused maps/loot on every frame.
            room=int.from_bytes(r[0xb9:0xbb],'little') if args.sms else (r[sy['room_id']^1]<<8)|r[(sy['room_id']+1)^1]
            if room==args.target_room:
                if any((r[0x600+n*48] if args.sms else r[(sy['world_actor_state']+n*48)^1])>=0x20 for n in range(16)):seen_enemies=True
            return
        if args.sms:
            data=lambda a,n:bytes(r[a:a+n]);state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game=r[0x1d],hero=r[0x301],counter=r[0x304],x=int.from_bytes(r[0x312:0x314],'little')>>8,y=int.from_bytes(r[0x310:0x312],'little')>>8,health=r[0x318],keys=r[0xde],audio_error=0)
            raw=data(0x600,768);loot_raw=data(0x4b0,336);tilemap=data(0x1600,1536)
            state['room_flags']=r[0x100+(state['room']&255)]
            state.update(dungeon=r[0x37],progress=r[0xce+r[0x37]],first_gem=r[0xcf],max_health=r[0xda],magic=r[0xdb],max_magic=r[0xdc],reward_active=0)
            state.update(weapon=r[0xe1],selected=r[0xdf],item_value=r[0xe0+args.collect_item] if args.collect_item is not None else 0)
        else:
            data=lambda a,n:bytes(r[(a+i)^1] for i in range(n));word=lambda n:int.from_bytes(data(sy[n],2),'big')
            state.update(room=word('room_id'),game=word('game_state'),hero=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),keys=word('hero_keys'),audio_error=word('sound_unhandled_command'))
            raw=data(sy['world_actor_state'],768);loot_raw=data(sy['world_loot_state'],336);tilemap=data(sy['sms_vram']+0x3800,1536)
            state['room_flags']=data(sy['game_save_state']+0x50+(state['room']&255),1)[0]
            dungeon=word('world_dungeon_number');state.update(dungeon=dungeon,progress=data(sy['game_save_state']+0x1e+dungeon,1)[0],max_health=word('hero_max_health'),magic=word('hero_magic'),max_magic=word('hero_max_magic'),reward_active=word('item_reward_active'),resume_phase=word('resume_phase'),door_loading=data(sy['door_transition_loading'],1)[0])
            state['first_gem']=data(sy['game_save_state']+0x1f,1)[0]
            state.update(weapon=word('hero_weapon_level'),selected=word('hero_selected_item'),item_value=data(sy['hero_items']+args.collect_item,1)[0] if args.collect_item is not None else 0)
        actors=[dict(slot=n,type=raw[n*48],state=raw[n*48+1],counter=raw[n*48+4],flags=raw[n*48+3],hp=raw[n*48+0x18],hurt=raw[n*48+5],hit_box=raw[n*48+0x1b],contact_box=raw[n*48+0x1c],vx=int.from_bytes(raw[n*48+0x16:n*48+0x18],'little',signed=True)/256,vy=int.from_bytes(raw[n*48+0x14:n*48+0x16],'little',signed=True)/256,x=raw[n*48+0x13],y=raw[n*48+0x11]) for n in range(16) if raw[n*48]]
        loot=[dict(slot=n,type=loot_raw[n*48],x=loot_raw[n*48+0x13],y=loot_raw[n*48+0x11]) for n in range(7) if loot_raw[n*48]]
        state['inventory_slot']=r[0xa0] if args.sms else word('inventory_slot')
        state['canoe']=r[0xec] if args.sms else data(sy['hero_items']+12,1)[0]
        state['terrain']=r[0x41] if args.sms else word('hero_terrain_context')
        CANOE_OWNED=bool(state['canoe'])
        AVOID_PORTAL_COORDINATES={p['coordinate'] for p in portals.values() if p['room']==state['room']} if state['room'] in avoided_portal_rooms else set()
        if f==prefix_end and args.exit_dungeon:exit_dungeon_number=state['dungeon'];exit_max_health=state['max_health']
        if exit_dungeon_number is not None:state['completed_dungeon_progress']=r[0xce+exit_dungeon_number] if args.sms else data(sy['game_save_state']+0x1e+exit_dungeon_number,1)[0]
        if f==prefix_end and not(state['room']==itinerary[0] and state['game']==12 and state['health']):failure='recorded_prefix_did_not_reach_expected_room'
        # A continuation can start during the reward after the boss died.
        # Observe actual prefix actors, rather than discarding that history.
        if state['room']==args.target_room and any(e['type']>=0x20 for e in actors):seen_enemies=True
        if f<=prefix_end:return
        if args.collect_item is not None and state['item_value'] and item_picked_at is None:item_picked_at=f;captures.update([f+1,f+150])
        if actors and actors[0]['slot']==0 and actors[0]['type']==7:
            boss_frames.append(dict(frame=f,state=raw[1],timer=raw[0x28],counter=raw[4]))
        if state['progress']==128 and gem_picked_at is None:gem_picked_at=f;captures.update([f+1,f+150])
        if itinerary_index+1<len(itinerary) and state['room']==itinerary[itinerary_index+1]:itinerary_index+=1
        if state['game']==6:itinerary_index=0
        if state['game']==12 and state['room']!=itinerary[itinerary_index] and state['room'] in itinerary:
            candidates=[n for n,room in enumerate(itinerary) if room==state['room']]
            previous_index=itinerary_index;itinerary_index=min(candidates,key=lambda n:abs(n-previous_index))
            events.append(dict(frame=f,reason='recover_after_room_displacement',previous_itinerary_index=previous_index,itinerary_index=itinerary_index,**state))
        if state['room']==args.target_room:
            if target_entry_keys is None:target_entry_keys=state['keys']
            seen_room=True
            if state['hero']==0:exit_reset_seen=True
            if any(e['type']>=0x20 for e in actors):seen_enemies=True
            gem_done=not args.collect_gem or state['progress']==128 and state['max_health']>=32 and state['health']==state['max_health'] and state['magic']==state['max_magic'] and not state['reward_active']
            item_done=args.collect_item is None or item_picked_at is not None and f-item_picked_at>=300 and state['item_value'] and not state['reward_active']
            if seen_enemies and state['health'] and state['game']==12 and not any(e['slot']<8 for e in actors) and (not args.collect_key or state['keys']>target_entry_keys) and gem_done and item_done and cleared is None:cleared=f;captures.add(f+1)
            if args.exit_dungeon and exit_reset_seen and (args.exit_before_crystal or state.get('completed_dungeon_progress')==128) and state.get('dungeon')==0 and state['max_health']==exit_max_health and state['health'] and state['game']==12 and state['hero']==1 and not state.get('resume_phase',0) and not state.get('door_loading',0) and cleared is None:cleared=f;captures.add(f+1)
        if state['game']==20:
            if menu_since is None:menu_since=f;deaths+=1
        else:menu_since=None
        if deaths>args.max_deaths:failure='death_retry_limit'
        if args.continuation and deaths:failure='continuation_route_died'
        if state['audio_error']:failure='native_audio_error'
        key=state['room'],state['game'],state['health'],state['keys'],state['room_flags'],state['progress'],state['max_health'],state['reward_active'],state['item_value'],state['selected'],tuple((e['slot'],e['type'],e['hp']) for e in actors if e['slot']<8),tuple((e['slot'],e['type']) for e in loot)
        row=dict(frame=f,**state,actors=actors,loot=loot,itinerary_index=itinerary_index)
        if key!=last_key:events.append(row);last_key=key;captures.add(f+1)
        progress=(key,state['x'],state['y'],tuple((e['slot'],e['type'],e['hp'],e['x'],e['y']) for e in actors if e['slot']<8))
        if progress!=pilot_progress_key:pilot_progress_key=progress;pilot_progress_frame=f
        elif f-pilot_progress_frame>2400:failure='controller_stalled'
        if f%10==0:samples.append(row)
        if cleared is not None and f==cleared+149:captures.add(f+1)
    def choose(f):
        nonlocal cached,buttons,last_direction,boss_dodge_until,boss_dodge_x,boss_last_shot,puzzle_goal
        if f==cached:return buttons
        cached=f;buttons=[]
        if f<=prefix_end:buttons=list(prefix_inputs[f]);return buttons
        if failure or cleared is not None:return buttons
        if args.collect_item is not None and item_picked_at is not None and f-item_picked_at<300:
            if f-item_picked_at>=200 and f%30==0:buttons=[8]
            return buttons
        if args.collect_gem and gem_picked_at is not None:
            if f-gem_picked_at>=200 and f%30==0:buttons=[8]
            return buttons
        if state.get('game')==20:
            if menu_since is not None and f-menu_since>=180 and f%30==0:buttons=[8]
            return buttons
        if args.equip_axe and state['weapon'] and (state['selected']!=1 or state['game']==16):
            if f%20:return buttons
            if state['game']==12 and state['hero']==1:buttons=[0]
            elif state['game']==16:
                if state['selected']==1:buttons=[0]
                elif state['inventory_slot']!=1:buttons=[7 if state['inventory_slot']<1 else 6]
                else:buttons=[8]
            return buttons
        if state.get('game')!=12 or not state.get('health'):return buttons
        # A3BF/2F0D: six fresh direction edges release a thief's grab.
        if state['hero']==12:buttons=[[4],[5],[6],[7]][f%4];return buttons
        if state['hero'] not in [0,1,2,3,4,5]:return buttons
        p=state['x'],state['y']
        if state['room'] not in itinerary:return buttons
        enemies=[e for e in actors if e['type']>=0x20 and e['hp'] and e['flags']&2]
        hazards=[e for e in actors if e['type']>=0x20 and not e['hp'] and e['flags']&2]
        rushing=state['room'] in rush_rooms
        if rushing:
            enemies=[];hazards=[e for e in actors if e['type']>=0x10 and e['flags']&2]
        helpful=[e for e in loot if (e['type'] in (10,11) and state['health']<state['max_health']) or (e['type']==12 and state['magic']<state['max_magic']) or (e['type']==13 and enemies)]
        seeking_loot=bool(helpful and (not enemies or min(abs(e['x']-p[0])+abs(e['y']-p[1]) for e in helpful)<=64))
        boss=next((e for e in actors if e['type'] in [0x63,0x64] and e['hp']),None)
        if args.early_boss_side and boss and state['selected']==1:
            from natural_combat_aim import directions
            if state['hero'] in [2,3,4,5]:buttons=[7,8];return buttons
            if state['counter']:buttons=[4+last_direction];return buttons
            if boss['x']!=128 or not boss['hit_box']:return buttons
            # Escape an overlapping starting position before asking the path
            # planner, which otherwise rejects the first step out of contact.
            if p[0]>112:last_direction=2;buttons=[6];return buttons
            if boss['state']==8 and 0<boss['counter']<=8 and f-boss_last_shot>24:
                boss_last_shot=f;boss_dodge_until=f+24
                boss_dodge_x=max(32,p[0]-48)
            if any(e['type']==0x72 and e['counter']>90 for e in actors) and f-boss_last_shot>24:
                boss_last_shot=f;boss_dodge_until=f+20
                boss_dodge_x=max(32,p[0]-40)
            if f<boss_dodge_until:
                if p[0]>boss_dodge_x:last_direction=2;buttons=[6]
                return buttons
            if boss['state']==8 and 0<boss['counter']<=24:
                # Finish the current swing before the aimed volley, then
                # preserve a held C without starting another fresh action.
                buttons=[7,8] if controls and 8 in controls[-1]['buttons'] else []
                return buttons
            variant=state['weapon']+1;target_y=min(144,max(32,round((boss['y']+8)/8)*8))
            if p[0]!=112 or abs(p[1]-target_y)>8 or 3 not in directions(p,boss,variant):
                path=walk(tilemap,p,lambda q:q[0]==112 and abs(q[1]-target_y)<=8,enemies+hazards,geometry=args.collision_aim)
                if path:last_direction=path[0];buttons=[4+last_direction];return buttons
            if 3 in directions(p,boss,variant):
                # Release C while stationary, then start a fresh right-facing
                # axe swing. Never start it with a walking counter in flight.
                buttons=[] if controls and 8 in controls[-1]['buttons'] else [7,8]
                last_direction=3;return buttons
        near=sorted(enemies,key=lambda e:abs(e['x']-p[0])+abs(e['y']-p[1]))
        variant=state['weapon']+1 if state['selected']==1 else 0
        def aim(q,e):
            if not args.collision_aim:return ()
            from natural_combat_aim import directions
            return directions(q,e,variant)
        def can_attack(q,e):
            # Original98FF wakes a dormant46 when both distances are<29.
            # Its attack box is intentionally zero until that proximity event.
            if e['type']==0x46 and e['state']==2 and not e['hit_box']:
                return abs(q[0]-e['x'])<=24 and abs(q[1]-e['y'])<=24
            return bool(aim(q,e)) if args.collision_aim else attack_position(q,e,args.reach,args.align)
        if state['hero'] in [2,3,4,5] or (not args.settle_attacks or not state['counter']) and near and (not seeking_loot and can_attack(p,near[0]) or abs(near[0]['x']-p[0])+abs(near[0]['y']-p[1])<16):
            if near:
                options=aim(p,near[0])
                if options:last_direction=options[0]
                elif not args.collision_aim or state['hero'] not in [2,3,4,5]:
                    dx=near[0]['x']-p[0];dy=near[0]['y']-p[1];last_direction=(3 if dx>=0 else 2) if abs(dx)>abs(dy) else (1 if dy>=0 else 0)
            buttons=[4+last_direction,8] if f%3 else []
            return buttons
        if state['counter']:buttons=[4+last_direction];return buttons
        keys=[e for e in loot if e['type']==14]
        gems=[e for e in actors if e['type']==15]
        if puzzle_goal and (puzzle_goal[0]!=state['room'] or state['room_flags']&4):
            pilot_decisions.append(dict(frame=f,reason='puzzle_goal_released',room=state['room'],flags=state['room_flags']))
            puzzle_goal=None
        if puzzle_goal:
            point=puzzle_goal[1]
            if p==point:buttons=[4];return buttons
            goal=lambda q:q==point
        elif seeking_loot:goal=lambda q:any(abs(q[0]-e['x'])<8 and abs(q[1]-e['y'])<8 for e in helpful)
        elif enemies:goal=lambda q:any(can_attack(q,e) for e in enemies)
        elif keys:goal=lambda q:any(abs(q[0]-e['x'])<8 and abs(q[1]-e['y'])<8 for e in keys)
        elif gems:goal=lambda q:any(abs(q[0]-e['x'])<=8 and abs(q[1]-e['y'])<=16 for e in gems)
        elif not rushing and any(e['slot']<8 and (e['type']<0x20 or e['hp'] and (not args.ignore_inactive_actors or e['flags']&2)) for e in actors):return buttons # Wait for enemies/particles, not invulnerable hazards.
        elif args.collect_item is not None and state['room'] in rewards and not state['item_value']:
            coordinate=rewards[state['room']]['coordinate']
            point=next((x,y) for y in range(8,169,8) for x in range(8,249,8) if (((y-12)&248)<<3)+(((x-12)&255)>>2&62)+126==coordinate)
            if p==point:buttons=[4];return buttons
            goal=lambda q:q==point
        elif state['room'] in puzzles and not state['room_flags']&4:
            coordinate=puzzles[state['room']]['coordinate']
            point=next((x,y) for y in range(8,169,8) for x in range(8,249,8) if (((y-12)&248)<<3)+(((x-12)&255)>>2&62)+126==coordinate)
            if p==point:buttons=[4];return buttons
            goal=lambda q:q==point
        elif itinerary_index+1<len(itinerary) and (state['room'],itinerary[itinerary_index+1]) in portals:
            portal=portals[state['room'],itinerary[itinerary_index+1]]
            coordinate=portal['coordinate']
            point=next((x,y) for y in range(8,169,8) for x in range(8,249,8) if (((y-12)&248)<<3)+(((x-12)&255)>>2&62)+126==coordinate)
            if p==point:last_direction=1;buttons=[5];return buttons # leave/re-enter the moving-contact point
            goal=lambda q:q==point
        elif itinerary_index+1<len(itinerary):
            delta=itinerary[itinerary_index+1]-state['room'];direction={-16:0,16:1,-1:2,1:3}[delta]
            goal=lambda q:q==[(128,8),(128,168),(8,88),(248,88)][direction]
            if args.doorway_ranges:
                goal=lambda q: (q[1]<=15 if direction==0 else q[1]>=161) and 128<=q[0]<=143 if direction<2 else (q[0]<=15 if direction==2 else q[0]>=241) and 80<=q[1]<=88
        else:goal=lambda q:q==((128,168) if args.exit_dungeon else (128,96))
        route=walk(tilemap,p,goal,enemies+hazards,geometry=args.collision_aim)
        if route is None and args.item_first_when_blocked and enemies and args.collect_item is not None and state['room'] in rewards and not state['item_value']:
            coordinate=rewards[state['room']]['coordinate']
            point=next((x,y) for y in range(8,169,8) for x in range(8,249,8) if (((y-12)&248)<<3)+(((x-12)&255)>>2&62)+126==coordinate)
            alternate=walk(tilemap,p,lambda q:q==point,enemies+hazards,geometry=args.collision_aim)
            if alternate is not None:
                if not pilot_decisions or pilot_decisions[-1].get('reason')!='blocked_attack_try_real_reward':pilot_decisions.append(dict(frame=f,reason='blocked_attack_try_real_reward',room=state['room'],point=point))
                if p==point:buttons=[4];return buttons
                route=alternate
        if route is None and args.puzzle_first_when_blocked and enemies and state['room'] in puzzles and not state['room_flags']&4:
            coordinate=puzzles[state['room']]['coordinate']
            point=next((x,y) for y in range(8,169,8) for x in range(8,249,8) if (((y-12)&248)<<3)+(((x-12)&255)>>2&62)+126==coordinate)
            alternate=walk(tilemap,p,lambda q:q==point,enemies+hazards,geometry=args.collision_aim)
            if alternate is not None:
                if not puzzle_goal:pilot_decisions.append(dict(frame=f,reason='blocked_attack_try_source_puzzle',room=state['room'],point=point,enemies=[e['type'] for e in enemies]))
                puzzle_goal=state['room'],point
                if p==point:buttons=[4];return buttons
                route=alternate
        if route is None and not enemies and itinerary_index+1<len(itinerary) and state['keys'] and (state['room'],itinerary[itinerary_index+1]) not in portals:
            delta=itinerary[itinerary_index+1]-state['room'];direction={-16:0,16:1,-1:2,1:3}[delta]
            probe=[(128,40),(128,144),(32,88),(224,88)][direction]
            aligned=lambda q: q[0]==probe[0] and abs(q[1]-probe[1])<=7 if direction<2 else q[1]==probe[1] and abs(q[0]-probe[0])<=7
            if aligned(p):last_direction=direction;buttons=[4+direction];return buttons
            route=walk(tilemap,p,aligned)
        if route:last_direction=route[0];buttons=[4+last_direction]
        return buttons
    def controller(f):
        nonlocal failure
        try:value=choose(f)
        except Exception as error:failure='controller_exception:'+repr(error);value=[]
        if f>prefix_end and (not controls or controls[-1]['buttons']!=value):controls.append(dict(frame=f,buttons=list(value)))
        return value
    def stop():return bool(failure) or not args.continue_after_clear and cleared is not None and observed-cleared>=150
    with contextlib.redirect_stdout(io.StringIO()):run(rom,args.frames,folder,captures,presses,ram_writes=inherited_writes,ram_observer=observe,input_provider=controller,stop_when=stop,core_options={'genesis_plus_gx_region_detect':region})
    for name,data in [('events',events),('samples',samples),('controls',controls),('boss_frames',boss_frames),('pilot_decisions',pilot_decisions)]: (folder/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    if cleared is None and failure is None:failure='frame_limit'
    result=dict(avoided_portal_rooms=sorted(avoided_portal_rooms),item_first_when_blocked_requested=args.item_first_when_blocked,deferred_puzzles=sorted(deferred_puzzles),doorway_ranges_requested=args.doorway_ranges,ignore_inactive_actors_requested=args.ignore_inactive_actors,rom_sha256=sha(rom.read_bytes()),region=region,recorded_new_game_prefix=prefix_name,prefix_end=prefix_end,itinerary=itinerary,attack_reach=args.reach,attack_alignment=args.align,collision_aim_requested=args.collision_aim,settle_attacks_requested=args.settle_attacks,early_boss_side_requested=args.early_boss_side,puzzle_first_when_blocked_requested=args.puzzle_first_when_blocked,driver_sha256=sha(Path(__file__).read_bytes()),aim_sha256=sha((ROOT/'tools/natural_combat_aim.py').read_bytes()) if args.collision_aim else None,equip_axe_requested=args.equip_axe,rush_rooms=sorted(rush_rooms),collect_key_requested=args.collect_key,target_entry_keys=target_entry_keys,new_key_verified=bool(args.collect_key and target_entry_keys is not None and cleared is not None and state['keys']>target_entry_keys),collect_gem_requested=args.collect_gem,collect_item_requested=args.collect_item,exit_dungeon_requested=args.exit_dungeon,target_room=args.target_room,entered_room=seen_room,seen_target_enemies=seen_enemies,room_cleared=cleared is not None,clear_frame=cleared,deaths=deaths,failure=failure,last_state=state,last_actors=actors,ram_injections=bool(inherited_writes),rom_modifications=False,sram_checkpoint_injection=False,dungeon_exit_verified=bool(args.exit_dungeon and cleared is not None),exit_before_crystal_requested=args.exit_before_crystal,full_dungeon_cleared=bool(args.exit_dungeon and not args.exit_before_crystal and cleared is not None))
    (folder/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(result)

if __name__=='__main__':main()
