"""Learn Fire I/II and Water with real SMS house services, before magic fairies."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_npc_d4 import ROUTE
from natural_dungeon_route import World
from continue_sms_plain_house_census import census_world


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
    output=ROOT/'analysis/sms_remaining_magic_campaign.json'
    old=json.loads(output.read_bytes()) if output.exists() else {}
    visits=old.get('completed_visits',[]);prefix=visits[-1]['trace'] if visits else a.prefix
    c=Campaign(prefix,0x15e,'npc-extra-magic')
    def save(status):
        output.write_text(json.dumps(dict(status=status,initial_prefix=a.prefix,last_verified_prefix=c.family+'/'+c.current,
            completed_visits=visits,all_npcs_complete=False,all_side_quests_complete=False),indent=2)+'\n')
    try:
        c.verify(lambda r:r['passed']);assert all(b&128 for b in c.raw()[0xcf:0xd8])
        for outside,teacher,levels in [(0x2c,2,[1,2]),(0xaa,3,[1])]:
            for level in levels:
                if c.raw()[0xe4+teacher]>=level:continue
                raw=c.raw();tool='natural_bell_world_route.py';extra=['--house-outside',hex(outside),'--house-target','0xbf']
                start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);chosen=None
                for direction in range(4):
                    world=census_world(raw,outside,0xbf,direction)
                    if outside==0x2c:
                        original_render=world.render_cells
                        world.render_cells=lambda room,cells,meta=None,render=original_render:render(room,bytearray(0x3a if b==0x3f else b for b in cells) if room==0x2c else cells,meta)
                    path,_=world.route(start)
                    if path is not None:chosen=direction;break
                assert chosen is not None,'No proposed approach to teacher; solve terrain/transport first'
                extra+=['--door-entry-direction',str(chosen)]
                if outside==0xaa and not raw[0x1aa]&1:extra+=['--bell-room','0xaa']
                else:
                    extra+=['--persisted-only']
                    if outside==0x2c and not raw[0x12c]&1:
                        assert raw[0xdb]>=8,'Restore magic through an ordinary service before opening Tyris entrance'
                        extra+=['--earth-world-cell','0x41'];tool='natural_frozen_earth_world_route.py'
                attempt=1
                while (ROOT/'validation'/ROUTE/f'sms-sms-npc-extra-magic-{outside:02x}-level{level}-entry{attempt:02d}').exists():attempt+=1
                c.route(f'{outside:02x}-level{level}-entry{attempt:02d}',extra,tool=tool)
                before=c.raw()
                c.service(f'{outside:02x}-level{level}-learn{attempt:02d}','natural_house_service',
                    ['--outside',hex(outside),'--kind','teacher','--teacher',str(teacher),'--expected-level',str(level)])
                after=c.raw();assert after[0xe4+teacher]==level and after[0xdb]==after[0xdc]
                expected=before[0xdc]
                if not before[0xe4+teacher] and ((expected+24)&255)<128:expected=(expected+24)&255
                assert after[0xdc]==expected
                visits.append(dict(outside=outside,teacher=teacher,level=level,max_magic_before=before[0xdc],
                    max_magic_after=after[0xdc],trace=c.family+'/'+c.current,frame=c.cap()['frames']))
                save('running');print('MAGIC LEARNED',hex(outside),level,flush=True)
        raw=c.raw();assert list(raw[0xe4:0xe8])==[2,2,2,1]
        save('lightning2_earth2_fire2_water1_verified')
    finally:c.close()


if __name__=='__main__':main()
