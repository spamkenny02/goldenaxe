"""Visit the remaining known ordinary house contexts, without claiming a full NPC census.

Continue before the palace, retain actual quest state, record each original
dialogue entry/return and require independent whole-RAM/pixel replay. Static
reachability is only a proposal; failed entrances never count as visits.
"""
import argparse,json
from run_core import ROOT
from natural_dungeon_route import World
from extract_title import rle_planes
from natural_bell_world_route import project_persisted_cells
from sms_campaign_runner import Campaign
from continue_sms_npc_d4 import ROUTE,SERVICE,COMBAT
COMBAT_ENTRANCES={r['room'] for r in json.loads((ROOT/'analysis/room_clear_reference.json').read_bytes())['records'] if r['kind']==7}


class CensusWorld(World):
    def render_cells(self,room,cells,meta=None):
        return super().render_cells(room,project_persisted_cells(self,room,cells,self.persisted_flags),meta)


def census_world(raw,outside,room,entry_direction=0):
    world=CensusWorld(house_outside=outside,house_target=room)
    world.persisted_flags=raw[0x100:0x200]
    world.axe_terrain=bool(raw[0xe1]);world.rope_terrain=bool(raw[0xed])
    world.canoe_owned=bool(raw[0xec]);world.boots_owned=bool(raw[0xee]);world.ship_owned=bool(raw[0xf0])
    world.crystal_bridge_open=bool(raw[0x149]&1)
    world.remote_unlocked={n for n,b in enumerate(raw[0x100:0x200]) if b&1}
    world.entry_direction=entry_direction
    # Propose the future doorway geometry only for a spell the hero owns.
    # The controller must actually cast it and prove the flag before entry.
    metadata=world.arrays['world_room_metadata']
    row=next((metadata[i:i+4] for i in range(0,len(metadata)-3,4) if metadata[i]==outside),None)
    if row and not raw[0x100+outside]&1 and raw[0xe5] and raw[0xdb]>=8:
        cells=bytearray(160);pointer=int.from_bytes(world.arrays['world_room_index'][outside*2:outside*2+2],'little')
        rle_planes(world.arrays['world_room_streams'],pointer,cells,0,1)
        if cells[row[1]] in (0x13,0x38,0x3d,0x85,0x86):
            proposed=bytearray(world.persisted_flags);proposed[outside]|=1;world.persisted_flags=proposed
    if row and not raw[0x100+outside]&1 and row[1]!=row[2] and raw[0xe1]:
        cells=world.base_cells(outside)
        if 0x80<=cells[row[1]]<=0x84:
            proposed=bytearray(world.persisted_flags);proposed[outside]|=1;world.persisted_flags=proposed
            world.remote_unlocked.add(outside)
    if row and outside in COMBAT_ENTRANCES and raw[0xe1] and not raw[0x100+outside]&1:
        proposed=bytearray(world.persisted_flags);proposed[outside]|=1;world.persisted_flags=proposed
    current=int.from_bytes(raw[0xb9:0xbb],'little')
    if current<256:
        # Ice and other temporary terrain belong to the actually occupied map,
        # even when there is no permanent outside flag for that transformation.
        world.live_room=current
        world.live_map=world.render_cells(current,raw[0x1c00:0x1ca0],raw[0x900:0x1100])
    return world


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prefix',help='Verified continuation after an actual transport/service');args=parser.parse_args()
    groups={}
    reference=json.loads((ROOT/'analysis/plain_house_dialogue_reference.json').read_bytes())
    previous=json.loads((ROOT/'analysis/sms_npc_coverage_report.json').read_bytes())
    room_clear={r['room']:r['kind'] for r in json.loads((ROOT/'analysis/room_clear_reference.json').read_bytes())['records']}
    known={(v['outside'],v['room'],v['coordinate']) for v in previous['visits']}
    for t in reference['contexts']:
        groups.setdefault((t['outside'],t['room']),[]).append(t)
    output=ROOT/'analysis/sms_plain_house_census_campaign.json'
    saved=json.loads(output.read_bytes()) if output.exists() else {}
    visited=saved.get('completed_houses',[]);proposals=saved.get('unreachable_static_proposals',[])
    for house in visited:
        known.update((house['outside'],house['room'],v['coordinate']) for v in house['conversations'])
    pending={key:rows for key,rows in groups.items() if any((key[0],key[1],t['coordinate']) not in known for t in rows)}
    initial=args.prefix or saved.get('last_verified_prefix') or (visited[-1]['trace'] if visited else COMBAT+'/sms-auto-sms-npc-d9-exit01')
    c=Campaign(initial,0x15e,'npc-census');first=not visited and not args.prefix;last_verified=initial
    def save(status):
        output.write_bytes((json.dumps(dict(status=status,source_sha256=reference['source_sha256'],
            scope='Known static ordinary-house contexts only; services, conditional NPCs and undiscovered contacts remain separate.',
            all_npcs_complete=False,all_text_variants_complete=False,
            source_campaign_prefix=COMBAT+'/sms-auto-sms-npc-d9-exit01',
            completed_houses=visited,remaining_houses=[dict(outside=k[0],room=k[1]) for k in pending],
            unreachable_static_proposals=proposals,current_prefix=c.family+'/'+c.current,
            last_verified_prefix=last_verified),indent=2)+'\n').encode())
    try:
        c.verify(lambda r:r.get('full_dungeon_cleared') or r.get('passed'))
        while pending:
            raw=c.raw();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
            ordered=sorted(pending,key=lambda k:abs((k[0]&15)-(start[0]&15))+abs((k[0]>>4)-(start[0]>>4)))
            chosen=None;chosen_direction=0
            for outside,room in ordered:
                for direction in range(4):
                    world=census_world(raw,outside,room,direction)
                    path,nodes=world.route(start)
                    if path is not None:chosen=(outside,room);chosen_direction=direction;break
                if chosen is not None:break
                proposals.append(dict(from_room=start[0],outside=outside,room=room,visited_nodes=nodes))
            if chosen is None:
                save('needs_additional_transport_or_terrain_route')
                print('STATIC COMPONENT EXHAUSTED; remaining houses need additional route proposals',flush=True)
                return
            outside,room=chosen;suffix=f'{outside:02x}-{room:02x}'
            attempt=1
            while (ROOT/'validation'/ROUTE/f'sms-sms-npc-census-{suffix}-entry{attempt:02d}').exists():attempt+=1
            extra=['--house-outside',hex(outside),'--house-target',hex(room),'--persisted-only']
            extra+=['--door-entry-direction',str(chosen_direction)]
            if room_clear.get(outside)==7 and not raw[0x100+outside]&1:extra+=['--fight-for-entrance']
            tool='natural_bell_world_route.py'
            world=World(house_outside=outside,house_target=room);meta=world.arrays['world_room_metadata']
            node=next((meta[i:i+4] for i in range(0,len(meta),4) if meta[i]==outside),None)
            if node and not raw[0x100+outside]&1:
                cells=bytearray(160);pointer=int.from_bytes(world.arrays['world_room_index'][outside*2:outside*2+2],'little')
                rle_planes(world.arrays['world_room_streams'],pointer,cells,0,1)
                if cells[node[1]] in (0x13,0x38,0x3d,0x85,0x86):
                    tool='natural_earth_world_route.py';extra+=['--earth-world-cell',hex(node[1])]
                elif 0x80<=cells[node[1]]<=0x84 and node[1]!=node[2]:
                    extra+=['--required-chop',f'{hex(outside)}:{hex(node[1])}']
            c.route(suffix+f'-entry{attempt:02d}',extra,
                    new_episode=first,tool=tool);first=False
            attempt=1
            while (ROOT/'validation'/SERVICE/f'sms-sms-npc-census-{suffix}-visit{attempt:02d}').exists():attempt+=1
            trial='sms-npc-census-'+suffix+f'-visit{attempt:02d}';name='sms-'+trial
            c.invoke('run_sms_dialogue_observed.py',['sms_npc_visit','--dialogue-core',
                str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
                '--sms','--assisted-prefix','--prefix',c.family+'/'+c.current,'--out',SERVICE+'/'+name,
                '--outside',hex(outside),'--room',hex(room),'--frames',str(c.cap()['frames']+12000)],
                SERVICE,name,lambda r:r['passed'])
            report=json.loads((ROOT/'validation'/SERVICE/name/'report.json').read_bytes())
            assert len(report['visited'])==len(pending[chosen])
            visited.append(dict(outside=outside,room=room,trace=SERVICE+'/'+name,
                                frame=c.cap()['frames'],conversations=report['visited']))
            last_verified=c.family+'/'+c.current
            del pending[chosen];save('running')
            print('ORDINARY HOUSE VERIFIED',suffix,'new conversations',len(report['visited']),flush=True)
        save('all_known_ordinary_house_contexts_visited')
    except Exception:
        save('failed_objective_not_counted');raise
    finally:c.close()


if __name__=='__main__':main()
