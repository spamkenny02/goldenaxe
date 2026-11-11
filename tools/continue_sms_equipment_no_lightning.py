"""Reach the rope before finishing D2, without learning Lightning, then visit A5."""
import json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter


def main():
    output=ROOT/'analysis/sms_equipment_prerequisite_no-lightning.json'
    if output.exists() and json.loads(output.read_bytes()).get('passed'):return
    initial='natural-dungeon-combat/sms-auto-sms-npc-axe-exit01'
    c=Campaign(initial,0x144,'npc-equipment-no-lightning')
    try:
        c.verify(lambda r:r['room_cleared']);assert not c.raw()[0xe4] and c.raw()[0xde]
        c.route('d3-entry01',['--door-index','3','--live-prefix-terrain'])
        c.boss=0x1c3
        c.stage('rope01','item','0x1f8,0x1f7,0x1e7,0x1e2,0x1f2,0x1f3,0x1f4','0x1f4',
            ['--equip-axe','--retarget-pending-boss','--collect-item','13'],gate='item_acquisition_passed')
        c.stage('supply-exit01','ordinary','0x1f4,0x1f3,0x1f2,0x1e2,0x1e7,0x1f7,0x1f8','0x62',
            ['--equip-axe','--exit-dungeon','--exit-before-crystal'],gate='dungeon_exit_verified')
        raw=c.raw();assert not raw[0xe4] and raw[0xed] and not raw[0xd1]&128
        n=enter(c,0x50,0x4f,'a5')
        steps=[dict(kind='silent',room=0x4f,point=[120,72]),dict(kind='talk',room=0x4f,point=[136,72],text_pc=0x8e5c),
            dict(kind='travel',room=0x4f,point=[136,160],direction=1,target_room=0x50)]
        c.service(f'hint{n:02d}','sms_contact_plan',['--plan',json.dumps(dict(steps=steps))])
        output.write_text(json.dumps(dict(passed=True,key='no-lightning',trace=c.family+'/'+c.current,
            initial_prefix=initial,lightning_level=raw[0xe4],rope_obtained_without_lightning=True,
            text_pc=0x8e5c,gift_not_awarded=True),indent=2)+'\n')
        print('NO LIGHTNING GIVER REFUSAL AND HINT VERIFIED',flush=True)
    finally:c.close()


if __name__=='__main__':main()
