"""Revisit all eight actual equipment/hidden-gift contexts after their rewards."""
import json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world


def main():
    initial='natural-service-route/sms-npc-hidden-rewards-55-gift01'
    output=ROOT/'analysis/sms_equipment_returns_campaign.json'
    old=json.loads(output.read_bytes()) if output.exists() else {};completed=old.get('completed_visits',[])
    c=Campaign(old.get('last_verified_prefix',initial),0x15e,'npc-equipment-returns');verified=c.family+'/'+c.current
    def save(status):output.write_text(json.dumps(dict(status=status,last_verified_prefix=verified,completed_visits=completed),indent=2)+'\n')
    try:
        c.verify(lambda r:r['passed'])
        for outside in [0x55,0xc7,0x92,0x4c,0x6a,0xb1,0x50,0x27]:
            if any(v['outside']==outside for v in completed):continue
            raw=c.raw();assert raw[0x100+outside]&2
            house=0x1f if outside in (0x55,0xc7) else 9 if outside==0x4c else 0x4f
            start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
            direction=next(d for d in range(4) if census_world(raw,outside,house,d).route(start)[0] is not None)
            n=1
            while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-equipment-returns-{outside:02x}-entry{n:02d}').exists():n+=1
            c.route(f'{outside:02x}-entry{n:02d}',['--house-outside',hex(outside),'--house-target',hex(house),
                '--persisted-only','--live-prefix-terrain','--door-entry-direction',str(direction)],tool='natural_bell_world_route.py')
            if house==0x1f:
                steps=[dict(kind='travel',room=0x1f,point=[104,24],direction=0,target_room=15),
                    dict(kind='silent',room=15,point=[104,56]),
                    dict(kind='travel',room=15,point=[104,152],direction=1,target_room=0x1f),
                    dict(kind='travel',room=0x1f,point=[136,160],direction=1,target_room=outside)]
            else:
                points=[[152,56],[168,56]] if house==9 else [[120,72],[136,72]]
                steps=[dict(kind='silent',room=house,point=point) for point in points]
                steps.append(dict(kind='travel',room=house,point=[136,160],direction=1,target_room=outside))
            c.service(f'{outside:02x}-return{n:02d}','sms_contact_plan',['--plan',json.dumps(dict(steps=steps))])
            verified=c.family+'/'+c.current;completed.append(dict(outside=outside,trace=verified,frame=c.cap()['frames']))
            save('running');print('EQUIPMENT RETURN VERIFIED',hex(outside),flush=True)
        save('all_eight_post_reward_contexts_contacted_and_replayed')
    except Exception:save('failed_objective_not_counted');raise
    finally:c.close()


if __name__=='__main__':main()
