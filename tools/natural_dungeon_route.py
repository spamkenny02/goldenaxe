"""Read ROM maps and drive an unmodified game toward dungeon entrance1."""
import argparse,contextlib,io,json,collections
from functools import lru_cache
from run_core import ROOT,run,FrameWrites
from extract_world import initial_room
from extract_title import rle_planes
from movement_reference import Hero,collision_cache,choose_collision_direction
from validate_actor_tick import PRESSES
from validate_playable_sprite_limit import symbols
from archive_lossless_evidence import sha
from assisted_prefix import prefix_writes
from rebase_natural_campaign import evidence

class World:
    def __init__(self,door_index=1,house_outside=None,house_target=0xaf):
        self.canoe_owned=False;self.live_room=None;self.live_map=None;self.axe_terrain=False;self.rope_terrain=False;self.remote_unlocked=set()
        self.rom=(ROOT/'input/original.sms').read_bytes();_,self.meta,_,self.initial_map,self.arrays,_=initial_room(self.rom)
        doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes());self.doors=doors
        self.goal=next(d for d in doors['direct_unconditional_dungeon_doors'] if d['index']==door_index) if house_outside is None else next(d for d in doors['direct_unconditional_doors'] if d['room']==house_outside and d['target']==house_target)
        self.house_mouths={(d['room'],d['x'],d['y']+8) for d in doors['direct_unconditional_doors']}
        self.door_cells={(d['room'],d['x'],d['y']) for d in doors['direct_unconditional_doors']+doors['direct_unconditional_dungeon_doors']}
    def tilemap(self,room):
        return self.live_map if room==self.live_room else self.base_tilemap(room)
    @lru_cache(None)
    def base_tilemap(self,room):
        index=self.arrays['world_room_index'];p=int.from_bytes(index[room*2:room*2+2],'little')
        if p==65535:return None
        cells=bytearray(160);rle_planes(self.arrays['world_room_streams'],p,cells,0,1)
        return self.render_cells(room,cells)
    def render_cells(self,room,cells,meta=None):
        cells=bytearray(cells);out=bytearray(self.initial_map);meta=self.meta if meta is None else meta
        if self.axe_terrain:
            records={self.rom[p]:self.rom[p+1:p+4] for p in range(0x3620,0x3634,4)}
            cut=set()
            for n in range(160):
                if cells[n] not in records:continue
                after,paired,paired_after=records[cells[n]];cells[n]=after;cut.add(n)
                if n+16<160 and cells[n+16]==paired:cells[n+16]=paired_after
            metadata=self.arrays['world_room_metadata']
            for p in range(0,len(metadata)-3,4):
                number,index,target,kind=metadata[p:p+4]
                if number==room and index in cut and (target==index or room in self.remote_unlocked):
                    assert kind in [0,3,4],(room,index,kind)
                    cells[target]=kind
                    if target+16<160:cells[target+16]={0x27:1,0x28:3,0x29:0,0x39:0x3a}.get(cells[target+16],cells[target+16])
        for y in range(20):
            for x in range(32):
                a=cells[(y//2)*16+x//2]*8+(y&1)*4+(x&1)*2;off=(y*32+x)*2;out[off:off+2]=meta[a:a+2]
        return bytes(out)
    def edge(self,node,d,tilemap=None):
        room,x,y,phase=node
        if d==0 and node[:3] in self.house_mouths:return None
        cache=collision_cache(self.tilemap(room) if tilemap is None else tilemap,Hero(x=x<<8,y=y<<8),canoe=self.canoe_owned)
        if choose_collision_direction(d,cache)!=d:return None
        x+=[0,0,-8,8][d];y+=[-8,8,0,0][d]
        # Door contact also triggers while entering from a side or from above.
        # Stop proposals outside all mouths; final entry uses ordinary input.
        if (room,x,y) in self.door_cells:return None
        if x<16:room=(room&240)|((room-1)&15);x=240
        elif x>=241:room=(room&240)|((room+1)&15);x=16
        elif y<16:room=(room-16)&255;y=160
        elif y>=161:room=(room+16)&255;y=16
        if room<16 or room&15==15 or self.tilemap(room) is None:return None
        if room!=node[0]:
            if node[0]!=0x77 or room==0x76:phase=0
            else:
                phase+=1
                correct=(phase==1 and room==0x78 and node[2]>=96) or (phase==2 and room==0x67) or (phase==3 and room==0x78 and node[2]<96) or (phase==4 and room==0x87) or (phase==5 and room==0x67)
                if not correct:phase=0
                if not(correct and phase==5):room=0x77
        return room,x,y,phase
    def rope_paths(self,node):
        if not self.rope_terrain:return []
        room,x,y,phase=node;alignment=((x&8)>>3)|((y&8)>>2)
        if (x|y)&7:return []
        pointer=int.from_bytes(self.arrays['world_room_index'][room*2:room*2+2],'little');original=bytearray(160)
        if pointer==65535:return []
        rle_planes(self.arrays['world_room_streams'],pointer,original,0,1);paths=[]
        for direction in [0,1]:
            cells=bytearray(original)
            if direction==0:
                if alignment!=3:continue
                index=((y-16)&240)|(x>>4)
                if index>=160 or cells[index]!=2:continue
                cells[index]=0x6d
                while index>=16 and cells[index-16]==12:index-=16;cells[index]=0x6c
            else:
                if alignment!=1:continue
                index=(y&240)|(x>>4)
                if index>=160 or cells[index]!=12:continue
                while index<160:
                    old=cells[index];cells[index]=0x6c
                    if old==2:cells[index]=0x6d;break
                    index+=16
            tilemap=self.render_cells(room,cells);point=node;segment=[]
            for _ in range(48):
                nxt=self.edge(point,direction,tilemap)
                if nxt is None:break
                previous_room=point[0];segment.append((point,direction,nxt));point=nxt
                # The macro is only a proposed vertical climb. It introduces
                # no horizontal motion or room edit into the running game.
                if point[0]!=previous_room:
                    pointer=int.from_bytes(self.arrays['world_room_index'][point[0]*2:point[0]*2+2],'little')
                    cells=bytearray(160);rle_planes(self.arrays['world_room_streams'],pointer,cells,0,1)
                    index=(144 if direction==0 else 0)+(point[1]>>4)
                    while 0<=index<160 and cells[index]==12:
                        cells[index]=0x6c;index+=-16 if direction==0 else 16
                    if direction and index<160:cells[index]=0x6d
                    tilemap=self.render_cells(point[0],cells)
                if any(self.edge(point,d) is not None for d in range(4)):paths.append((point,list(segment)))
        return paths
    def route(self,start):
        if len(start)==3:start=(*start,0)
        goal=self.goal['room'],self.goal['x'],self.goal['y']+8
        queue=collections.deque([start]);parents={start:None};found=None
        while queue:
            here=queue.popleft()
            if here[:3]==goal:found=here;break
            neighbors=[]
            for d in [0,1,2,3]:
                nxt=self.edge(here,d)
                if nxt is not None:neighbors.append((nxt,[(here,d,nxt)]))
            neighbors.extend(self.rope_paths(here))
            for nxt,segment in neighbors:
                if nxt not in parents:parents[nxt]=(here,segment);queue.append(nxt)
        if found is None:return None,len(parents)
        segments=[]
        while parents[found] is not None:
            previous,segment=parents[found];segments.append(segment);found=previous
        return [step for segment in reversed(segments) for step in segment],len(parents)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--plan',action='store_true');parser.add_argument('--rope-terrain',action='store_true',help='Propose vertical source-like climbs using the already acquired rope');parser.add_argument('--required-chop',help='ROOM:cell prerequisite to cut before routing to the final house');parser.add_argument('--axe-terrain',action='store_true',help='Plan destructible exterior cells and cut them using an already owned/equipped axe');parser.add_argument('--sms',action='store_true');parser.add_argument('--pal',action='store_true');parser.add_argument('--frames',type=int,default=12000);parser.add_argument('--trial',default='01');parser.add_argument('--door-index',type=int,default=1);parser.add_argument('--retry-deaths',type=int,default=0,help='Use normal Continue after death, at most this many times');parser.add_argument('--house-outside',type=lambda x:int(x,0),help='Route to a source unconditional house door in this exterior room');parser.add_argument('--house-target',type=lambda x:int(x,0),default=0xaf);parser.add_argument('--prefix-replay',help='Validated cold rebase trace, relative to validation/');parser.add_argument('--prefix-service',help='Completed natural NPC service trace');parser.add_argument('--prefix-combat',help='Natural completed combat trace, replayed from cold boot');parser.add_argument('--prefix-rope',help='Verified acquired-rope route in natural-rope-route/');parser.add_argument('--live-prefix-terrain',action='store_true',help='Use the verified current room map until leaving it');parser.add_argument('--assisted-prefix',action='store_true',help='Explicitly continue a verified assisted recording');args=parser.parse_args()
    world=World(args.door_index,args.house_outside,args.house_target);world.axe_terrain=args.axe_terrain;world.rope_terrain=args.rope_terrain;start=(0x95,136,112);prefix_end=0;prefix_inputs=[];prefix_presses=[];inherited_writes=[];prefix_ram=None;live_initial_room=None
    assert sum(bool(v) for v in [args.prefix_combat,args.prefix_service,args.prefix_replay,args.prefix_rope])<=1
    has_prefix=bool(args.prefix_combat or args.prefix_service or args.prefix_replay or args.prefix_rope)
    assert not args.live_prefix_terrain or has_prefix
    if has_prefix:
        prefix=(ROOT/'validation/natural-rope-route'/args.prefix_rope).resolve() if args.prefix_rope else (ROOT/'validation'/args.prefix_replay).resolve() if args.prefix_replay else ROOT/'validation'/('natural-service-route' if args.prefix_service else 'natural-dungeon-combat')/(args.prefix_service or args.prefix_combat)
        assert prefix.resolve().is_relative_to(ROOT/'validation')
        prior=json.loads((prefix/('rebase_report.json' if args.prefix_replay else 'report.json')).read_bytes());capture=json.loads((prefix/'capture.json').read_bytes());recorded=json.loads((prefix/'controls.json').read_bytes())
        if args.prefix_replay:
            proof=json.loads((prefix.with_name(prefix.name+'-fixed-replay')/'replay_report.json').read_bytes())
            assert prior['passed'] and proof['passed'] and proof['rom_sha256']==capture['rom_sha256'] and not proof['ram_injections']
            st=prior['states'][-1];assert st['game_state']==12 and st['hero_health']>0
            prior['last_state']=dict(room=st['room_id'],x=st['hero_x']>>8,y=st['hero_y']>>8)
        elif args.prefix_rope:assert prior['passed'] and prior['failure'] is None and prior['new_assistance_writes']==0
        else:assert prior['failure'] is None and (prior['passed'] if args.prefix_service else prior['room_cleared'])
        assert capture['sram_input'] is None
        inherited_writes=prefix_writes(prefix,capture,args.assisted_prefix)
        assert capture['rom_sha256']==sha((ROOT/('input/original.sms' if args.sms else 'gaw-megadrive.bin')).read_bytes())
        st=prior['last_state'];start=(st['room'],st['x'],st['y']);assert start[0]<256
        prefix_end=capture['frames'];prefix_presses=list(map(tuple,capture['presses']));prefix_inputs=[()]*(prefix_end+1)
        for i,row in enumerate(recorded):
            end=recorded[i+1]['frame']-1 if i+1<len(recorded) else prefix_end
            prefix_inputs[row['frame']:end+1]=[tuple(row['buttons'])]*(end-row['frame']+1)
            prefix_presses.extend((row['frame'],end,b) for b in row['buttons'])
    if has_prefix:
        raw=evidence(prefix/f"ram_{prefix_end:05d}.bin");prefix_ram=raw
        address=0xec if args.sms else symbols(ROOT/'megadrive/out/release/symbol.txt')['hero_items']+12
        world.canoe_owned=bool(raw[address if args.sms else address^1])
    if args.rope_terrain:
        assert has_prefix,'An acquired-rope prefix is required'
        raw=evidence(prefix/f"ram_{prefix_end:05d}.bin")
        address=0xed if args.sms else symbols(ROOT/'megadrive/out/release/symbol.txt')['hero_items']+13
        assert raw[address if args.sms else address^1], 'The rope must be acquired in the real prefix'
    if args.axe_terrain and has_prefix:
        raw=evidence(prefix/f"ram_{prefix_end:05d}.bin")
        if args.sms:flags=raw[0x100:0x200]
        else:
            address=symbols(ROOT/'megadrive/out/release/symbol.txt')['game_save_state']+0x50;flags=bytes(raw[(address+i)^1] for i in range(256))
        world.remote_unlocked.update(room for room,flag in enumerate(flags) if flag&1)
    if args.live_prefix_terrain:
        prefix_ram=evidence(prefix/f"ram_{prefix_end:05d}.bin")
        if args.sms:live_map=prefix_ram[0x1600:0x1c00]
        else:
            address=symbols(ROOT/'megadrive/out/release/symbol.txt')['sms_vram']+0x3800
            live_map=bytes(prefix_ram[(address+i)^1] for i in range(1536))
        if args.axe_terrain:
            if args.sms:cells=prefix_ram[0x1c00:0x1ca0];meta=prefix_ram[0x900:0x1100]
            else:
                address=symbols(ROOT/'megadrive/out/release/symbol.txt')['scratch'];meta=bytes(prefix_ram[(address+i)^1] for i in range(2048));cells=bytes(prefix_ram[(address+0x800+i)^1] for i in range(160))
            live_map=world.render_cells(start[0],cells,meta)
        assert len(live_map)==1536
        live_initial_room=world.live_room=start[0];world.live_map=live_map
    required_chop=None;chop_done=False;final_goal=dict(world.goal)
    if args.required_chop:
        assert args.axe_terrain
        room,index=(int(v,0) for v in args.required_chop.split(':'));required_chop=(room,index)
        world.goal=dict(final_goal,room=room,x=(index&15)*16+8,y=(index&240)+16)
    assert args.plan or args.frames>prefix_end,('Frame budget must extend beyond prefix',args.frames,prefix_end)
    route_start=max(2500,prefix_end+1)
    path,visited=world.route(start);assert path is not None,('No base-map walking route',visited)
    rooms=list(dict.fromkeys([a[0] for a,d,b in path]+[path[-1][2][0]]))
    result=dict(canoe_acquired_in_prefix=world.canoe_owned,source_sha256=sha(world.rom),goal=world.goal,waypoints=len(path),visited_nodes=visited,rooms=[f'{r:02x}' for r in rooms],route=path,scope='Static base-ROM walking proposal with original collision/sliding rules. Does not include actors, quest edits, terrain-dependent speed or prove a playable route.')
    folder=ROOT/'validation/natural-dungeon-route';folder.mkdir(exist_ok=True);(folder/f'plan-door{args.door_index}-{args.trial}.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='route'})
    if args.plan:return
    tag='sms' if args.sms else 'md';rom=ROOT/'input/original.sms' if args.sms else ROOT/'gaw-megadrive.bin';sy=None if args.sms else symbols(ROOT/'megadrive/out/release/symbol.txt')
    live_cells=b'';live_tilemap=b'';chops=[];last_chop=None
    state={};events=[];samples=[];captures=set();controls=[];cursor=0;cached_frame=-1;cached_buttons=[];last_progress=route_start;reached_at=None;ready_at=None;room_entry_at=None;saw_target_reset=False;probe_before=None;probe_after=None;failure=None
    previous_key=None;observed_frame=0;death_active=False;deaths=0;menu_since=None
    def observe(f,r):
        nonlocal previous_key,reached_at,ready_at,room_entry_at,saw_target_reset,probe_before,probe_after,failure,observed_frame,death_active,deaths,menu_since,live_cells,live_tilemap,chop_done,path,cursor,last_progress
        observed_frame=f
        if args.sms:
            state.update(room=int.from_bytes(r[0xb9:0xbb],'little'),game_state=r[0x1d],hero_state=r[0x301],counter=r[0x304],x=int.from_bytes(r[0x312:0x314],'little')>>8,y=int.from_bytes(r[0x310:0x312],'little')>>8,health=r[0x318],gold=r[0xdd],maze=r[0x6c])
        else:
            word=lambda n:int.from_bytes(bytes(r[(sy[n]+i)^1] for i in range(2)),'big')
            state.update(room=word('room_id'),game_state=word('game_state'),hero_state=word('hero_state'),counter=word('hero_counter'),x=word('hero_x')>>8,y=word('hero_y')>>8,health=word('hero_health'),gold=word('hero_gold'),maze=r[sy['forest_maze_progress']^1],reveal_phase=word('resume_phase'),door_loading=r[sy['door_transition_loading']^1])
        if args.axe_terrain and f>=prefix_end:
            if args.sms:
                live_cells=r[0x1c00:0x1ca0];live_tilemap=r[0x1600:0x1c00];state.update(selected=r[0xdf],weapon=r[0xe1])
            else:
                data=lambda name,k:bytes(r[(sy[name]+i)^1] for i in range(k))
                live_cells=data('scratch',4096)[0x800:0x8a0];live_tilemap=data('sms_vram',16384)[0x3800:0x3e00];state.update(selected=word('hero_selected_item'),weapon=word('hero_weapon_level'))
            if f==prefix_end:assert state['selected']==1 and state['weapon'],('Owned equipped axe required',state)
        if required_chop and not chop_done and f>=route_start and state['room']==required_chop[0]:
            flag=r[0x100+required_chop[0]] if args.sms else data('game_save_state',592)[0x50+required_chop[0]]
            if flag&1:
                chop_done=True;world.remote_unlocked.add(required_chop[0]);world.base_tilemap.cache_clear();world.goal=final_goal
                path,examined=world.route((state['room'],state['x'],state['y'],state['maze']));assert path is not None
                cursor=0;last_progress=f;events.append(dict(frame=f,reason='required_chop_verified',room=required_chop[0],cell=required_chop[1],flag=flag));captures.add(f+1)
        if f==prefix_end and prefix_ram is not None:assert r==prefix_ram,'Verified prefix RAM must replay exactly before extending it'
        if f<route_start:return
        if world.live_room is not None and state['room']!=world.live_room:world.live_room=None;world.live_map=None
        row=dict(frame=f,waypoint=cursor,**state)
        if f%5==0:samples.append(row)
        key=state['room'],state['game_state'],state['health']
        if key!=previous_key:
            events.append(row);captures.add(f+1);previous_key=key;print(tag,'event',row,flush=True)
        if state['room']==world.goal['target'] and room_entry_at is None:room_entry_at=f;captures.add(f+1)
        if state['room']==world.goal['target'] and state['game_state']==12:
            if reached_at is None:reached_at=f;captures.add(f+1)
            if state['hero_state']==0:saw_target_reset=True
            settled=args.sms or not state['reveal_phase'] and not state['door_loading']
            if saw_target_reset and settled and state['hero_state']==1 and ready_at is None:ready_at=f;captures.add(f+1)
        if ready_at is not None and f in [ready_at+59,ready_at+84,ready_at+99]:captures.add(f+1)
        if ready_at is not None and f==ready_at+60:probe_before=dict(state)
        if ready_at is not None and f==ready_at+85:probe_after=dict(state)
        dying=state['game_state']==20 or (not state['health'] and state['hero_state'] in [8,9])
        if dying and not death_active:death_active=True;deaths+=1
        if state['game_state']==20 and menu_since is None:menu_since=f
        if state['health'] and state['game_state']==12 and state['hero_state']==1:death_active=False;menu_since=None
        if deaths>args.retry_deaths:failure='hero_died'
    def choose(f):
        nonlocal path,cursor,cached_frame,cached_buttons,last_progress,failure,last_chop
        if f<=prefix_end:return prefix_inputs[f]
        if f==cached_frame:return cached_buttons
        cached_frame=f;cached_buttons=[]
        if ready_at is not None and ready_at+70<=f<=ready_at+74:cached_buttons=[4];return cached_buttons
        if f<2501 or not state or reached_at is not None or failure:return cached_buttons
        if death_active:
            last_progress=f
            if state['game_state']==20 and menu_since is not None and f-menu_since>=180 and f%30==0:cached_buttons=[8]
            return cached_buttons
        if state['game_state']!=12 or state['hero_state'] not in [0,1]:return cached_buttons
        point=(state['room'],state['x'],state['y'])
        while cursor<len(path) and point==tuple(path[cursor][2][:3]):cursor+=1;last_progress=f
        if cursor==len(path):
            cut=required_chop and not chop_done
            if args.axe_terrain and state['hero_state']==1 and not state['counter']:
                cache=collision_cache(live_tilemap,Hero(x=point[1]<<8,y=point[2]<<8),canoe=world.canoe_owned)
                nearby=any(0x80<=cell<=0x84 and abs((n&15)*16+8-point[1])<=24 and abs((n>>4)*16+8-point[2])<=40 for n,cell in enumerate(live_cells))
                cut=cut or (nearby and choose_collision_direction(0,cache)!=0)
            cached_buttons=([4,8] if f%3 else []) if cut else [4]
        else:
            previous,d,nxt=path[cursor]
            if not state['counter'] and point!=tuple(previous[:3]):
                matches=[n for n,e in enumerate(path) if tuple(e[0][:3])==point]
                if matches:
                    resumed=min(matches,key=lambda n:abs(n-cursor));events.append(dict(frame=f,reason='recover_after_displacement',previous_waypoint=cursor,resumed_waypoint=resumed,actual=point));cursor=resumed;last_progress=f;previous,d,nxt=path[cursor]
                else:
                    replacement,examined=world.route((*point,state['maze']))
                    if replacement:
                        events.append(dict(frame=f,reason='replan_after_displacement',actual=point,remaining_waypoints=len(replacement),visited_nodes=examined));path=replacement;cursor=0;last_progress=f;previous,d,nxt=path[0]
                    else:
                        failure='unexpected_position';events.append(dict(frame=f,failure=failure,expected=previous,actual=point,waypoint=cursor));return []
            if args.axe_terrain and not state['counter'] and state['hero_state']==1:
                cache=collision_cache(live_tilemap,Hero(x=point[1]<<8,y=point[2]<<8),canoe=world.canoe_owned)
                if choose_collision_direction(d,cache)!=d:
                    # A blocked step is solved by a real ordinary axe swing.
                    # The source/native game itself chooses the affected cells.
                    nearby=[n for n,cell in enumerate(live_cells) if 0x80<=cell<=0x84 and abs((n&15)*16+8-point[1])<=32 and abs((n>>4)*16+8-point[2])<=40]
                    if nearby:
                        key=(point,d,tuple(live_cells[n] for n in nearby))
                        if key!=last_chop:chops.append(dict(frame=f,point=point,direction=d,candidates=nearby));last_chop=key
                        cached_buttons=[4+d,8] if f%3 else [];return cached_buttons
            cached_buttons=[4+d]
        if f-last_progress>300:
            failure='no_waypoint_progress';events.append(dict(frame=f,failure=failure,waypoint=cursor,**state));return []
        return cached_buttons
    def controller(f):
        buttons=list(choose(f))
        if not controls or controls[-1]['buttons']!=buttons:controls.append(dict(frame=f,buttons=list(buttons)))
        return buttons
    def stop():return bool(failure) or ready_at is not None and observed_frame-ready_at>=100
    directory=folder/(tag+('-pal' if args.pal else '')+'-'+args.trial)
    assert not directory.exists(),('Keep existing trial evidence; choose a new --trial',directory)
    with contextlib.redirect_stdout(io.StringIO()):run(rom,args.frames,directory,captures,(prefix_presses if has_prefix else ([(200,220,0)] if args.sms else [])+PRESSES[:8]),ram_writes=FrameWrites(inherited_writes),ram_observer=observe,input_provider=controller,stop_when=stop,core_options={'genesis_plus_gx_region_detect':'pal' if args.pal else 'auto'})
    if ready_at is None and failure is None:failure='frame_limit'
    if inherited_writes:(directory/'assistance.json').write_bytes((prefix/'assistance.json').read_bytes())
    (directory/'events.json').write_text(json.dumps(events,indent=2)+'\n');(directory/'samples.json').write_text(json.dumps(samples,indent=2)+'\n');(directory/'controls.json').write_text(json.dumps(controls,indent=2)+'\n')
    from PIL import Image
    visible=False
    if ready_at is not None:
        final=Image.open(directory/f'frame_{ready_at+60:05d}.png').convert('RGB');visible=final.getbbox() is not None and final.crop((0,160 if args.sms else 176,256,192 if args.sms else 208)).getbbox() is not None
    probe=bool(probe_before and probe_after and probe_before['room']==probe_after['room']==world.goal['target'] and probe_before['x']==probe_after['x']==(136 if args.house_outside is not None else 128) and probe_before['y']==152 and probe_after['y']==144)
    (directory/'axe_chops.json').write_text(json.dumps(chops,indent=2)+'\n')
    report=dict(canoe_acquired_in_prefix=world.canoe_owned,rope_terrain_requested=args.rope_terrain,required_chop=required_chop,required_chop_verified=chop_done,axe_terrain_requested=args.axe_terrain,axe_chop_decisions=len(chops),normal_continues=deaths,retry_deaths=args.retry_deaths,door_index=args.door_index,house_outside=args.house_outside,house_target=args.house_target if args.house_outside is not None else None,recorded_replay_prefix=args.prefix_replay,recorded_combat_prefix=args.prefix_combat,recorded_service_prefix=args.prefix_service,recorded_rope_prefix=args.prefix_rope,live_prefix_terrain=args.live_prefix_terrain,live_initial_room=live_initial_room,prefix_end=prefix_end,region='pal' if args.pal else 'auto',directional_probe_succeeded=probe,probe_before=probe_before,probe_after=probe_after,rendered_final_frame_nonblack=visible,rom_sha256=sha(rom.read_bytes()),reference_sha256=sha(world.rom),reached_entrance=ready_at is not None,first_published_target_room_frame=room_entry_at,first_target_state12_frame=reached_at,first_controllable_frame=ready_at,door_transition_frames=None if ready_at is None else ready_at-room_entry_at,failure=failure,waypoints_reached=cursor,waypoints_planned=len(path),last_state=state,ram_injections=bool(inherited_writes),sram_checkpoint_injection=False,scope='Read-only state-driven directional controller along ROM-derived static path, normal boot/name/opening. No combat strategy or whole-dungeon claim.')
    (directory/'route_report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':main()
