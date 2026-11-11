"""Leave D3 after obtaining the rope, before its crystal; test A5 below 56 HP."""
import json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter


def main():
    output=ROOT/'analysis/sms_equipment_prerequisite_low-health-capacity.json'
    if output.exists() and json.loads(output.read_bytes()).get('passed'):return
    initial='natural-dungeon-combat/sms-auto-sms-npc-d3-rope02'
    c=Campaign(initial,0x1c3,'npc-equipment-low-capacity')
    try:
        c.verify(lambda r:r['item_acquisition_passed'])
        c.stage('supply-exit01','ordinary','0x1f4,0x1f3,0x1f2,0x1e2,0x1e7,0x1f7,0x1f8','0x62',
            ['--equip-axe','--exit-dungeon','--exit-before-crystal'],gate='dungeon_exit_verified')
        raw=c.raw();assert raw[0xe4] and raw[0xda]<56 and raw[0xed] and not raw[0xd1]&128
        n=enter(c,0x50,0x4f,'a5')
        steps=[dict(kind='silent',room=0x4f,point=[120,72]),dict(kind='talk',room=0x4f,point=[136,72],text_pc=0x8ed9),
            dict(kind='travel',room=0x4f,point=[136,160],direction=1,target_room=0x50)]
        c.service(f'hint{n:02d}','sms_contact_plan',['--plan',json.dumps(dict(steps=steps))])
        output.write_text(json.dumps(dict(passed=True,key='low-health-capacity',trace=c.family+'/'+c.current,
            initial_prefix=initial,health_capacity=raw[0xda],rope_obtained_before_third_crystal=True,
            text_pc=0x8ed9,gift_not_awarded=True),indent=2)+'\n')
        print('LOW CAPACITY GIVER REFUSAL AND HINT VERIFIED',flush=True)
    finally:c.close()


if __name__=='__main__':main()
