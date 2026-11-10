"""Record one reachable conditional NPC variant from an actual campaign prefix.

Alternative prefixes are explicitly separate branches, never silently inserted
into the main route. All effects still come from the original controller input.
"""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_npc_d4 import SERVICE,COMBAT,ROUTE
from natural_dungeon_route import World
from extract_title import rle_planes


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--prefix',required=True)
    p.add_argument('--outside',type=lambda x:int(x,0),choices=[0x22,0xce],required=True)
    p.add_argument('--label',required=True)
    p.add_argument('--expected-variant',required=True)
    p.add_argument('--new-episode',action='store_true')
    p.add_argument('--boss-room',type=lambda x:int(x,0),default=0x15e)
    a=p.parse_args();room=7 if a.outside==0x22 else 2
    assert all(c.isalnum() or c=='-' for c in a.label)
    c=Campaign(a.prefix,a.boss_room,a.label)
    try:
        c.verify(lambda r:r.get('full_dungeon_cleared') or r.get('passed'))
        extra=['--house-outside',hex(a.outside),'--house-target',hex(room),'--persisted-only']
        tool='natural_bell_world_route.py';w=World(house_outside=a.outside,house_target=room)
        m=w.arrays['world_room_metadata'];node=next((m[i:i+4] for i in range(0,len(m)-3,4) if m[i]==a.outside),None)
        if node and not c.raw()[0x100+a.outside]&1:
            cells=bytearray(160);pointer=int.from_bytes(w.arrays['world_room_index'][a.outside*2:a.outside*2+2],'little')
            rle_planes(w.arrays['world_room_streams'],pointer,cells,0,1)
            if cells[node[1]] in (0x13,0x38,0x3d,0x85,0x86):
                tool='natural_earth_world_route.py';extra+=['--earth-world-cell',hex(node[1])]
        c.route('entry01',extra,new_episode=a.new_episode,tool=tool)
        trial='sms-'+a.label+'-visit01';name='sms-'+trial
        c.invoke('run_sms_dialogue_observed.py',['sms_npc_visit','--dialogue-core',
            str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
            '--sms','--conditional','--assisted-prefix','--prefix',c.family+'/'+c.current,
            '--outside',hex(a.outside),'--room',hex(room),'--out',SERVICE+'/'+name,
            '--frames',str(c.cap()['frames']+12000)],SERVICE,name,
            lambda r:r['passed'] and r['conditional_effects_verified'] and r['conditional_variant']==a.expected_variant)
        report=json.loads((ROOT/'validation'/SERVICE/name/'report.json').read_bytes())
        output=ROOT/'analysis'/('sms-conditional-'+a.label+'.json')
        output.write_text(json.dumps(dict(passed=True,branch_prefix=a.prefix,trace=SERVICE+'/'+name,
            outside=a.outside,room=room,variant=report['conditional_variant'],visits=report['visited'],
            source_sha256=report['source_sha256'],all_npcs_complete=False,
            scope='One conditional variant on an explicitly separate continuous cold-boot branch. No all-variant or merged-route claim.'),indent=2)+'\n')
        print('CONDITIONAL VARIANT VERIFIED',a.expected_variant,flush=True)
    finally:c.close()


if __name__=='__main__':main()
