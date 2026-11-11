"""Take a real paid passage only when its destination reaches a pending house."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix');a=p.parse_args()
    census=json.loads((ROOT/'analysis/sms_plain_house_census_campaign.json').read_bytes())
    assert census['status']=='needs_additional_transport_or_terrain_route'
    prefix=a.prefix or census['last_verified_prefix'];c=Campaign(prefix,0x15e,'npc-census-transport')
    try:
        c.verify(lambda r:r['passed']);raw=c.raw()
        assert raw[0xdd]>=10,'Earn actual currency before using the passage'
        start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
        routes=json.loads((ROOT/'analysis/paid_passage_reference.json').read_bytes())['routes'];chosen=None
        for outside,destination,y,x in routes:
            entry_direction=None
            for direction in range(4):
                path,_=census_world(raw,outside,0x9f,direction).route(start)
                if path is not None:entry_direction=direction;break
            if entry_direction is None:continue
            for target in census['remaining_houses']:
                for direction in range(4):
                    onward,_=census_world(raw,target['outside'],target['room'],direction).route((destination,x,y))
                    if onward is not None:chosen=(outside,destination,target,entry_direction);break
                if chosen:break
            if chosen:break
        assert chosen,'No paid passage proposal reaches the remaining houses; solve the missing terrain prerequisite'
        outside,destination,target,entry_direction=chosen;attempt=1
        while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-census-transport-{outside:02x}-entry{attempt:02d}').exists():attempt+=1
        c.route(f'{outside:02x}-entry{attempt:02d}',['--house-outside',hex(outside),'--house-target','0x9f','--persisted-only','--door-entry-direction',str(entry_direction)],tool='natural_bell_world_route.py')
        c.service(f'{outside:02x}-payment{attempt:02d}','natural_paid_passage',['--outside',hex(outside)])
        assert int.from_bytes(c.raw()[0xb9:0xbb],'little')==destination
        report=dict(passed=True,previous_prefix=prefix,trace=c.family+'/'+c.current,
            paid_outside=outside,actual_destination=destination,pending_house_proposal=target,
            scope='Ordinary ten-horn payment and independent fixed replay. The onward path remains a proposal until actually played.')
        path=ROOT/f'analysis/sms_census_transport_{outside:02x}_{attempt:02d}.json'
        path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
    finally:c.close()


if __name__=='__main__':main()
