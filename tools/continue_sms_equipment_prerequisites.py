"""Play the distinct original equipment prerequisites and associated hints."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter


def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);a=p.parse_args()
    specs={
        'shield-before-crystal':('natural-dungeon-combat/sms-auto-sms-npc-d5-exit01',0x4c,9,0x115,True,
            [dict(kind='talk',room=9,point=[152,56],text_pc=0xa52f),dict(kind='silent',room=9,point=[168,56])]),
        'shield-after-crystal-hint':('natural-dungeon-combat/sms-auto-sms-npc-d6-exit02',0x4c,9,0x1b8,True,
            [dict(kind='talk',room=9,point=[152,56],text_pc=0xac1e)]),
    }
    for key in a.cases.split(','):
        if key=='no-lightning':
            from continue_sms_equipment_no_lightning import main as play
            play();continue
        if key=='low-health-capacity':
            from continue_sms_equipment_low_capacity import main as play
            play();continue
        output=ROOT/f'analysis/sms_equipment_prerequisite_{key}.json'
        if output.exists() and json.loads(output.read_bytes()).get('passed'):continue
        initial,outside,house,boss,new_episode,steps=specs[key]
        c=Campaign(initial,boss,'npc-equipment-prerequisite-'+key)
        try:
            c.verify(lambda r:r.get('passed') or r.get('full_dungeon_cleared') or r.get('room_cleared'))
            raw=c.raw()
            assert (not raw[0xe4] if key=='no-lightning' else raw[0xe4] and raw[0xda]<56 if key=='low-health-capacity' else
                not raw[0xd4]&128 if key=='shield-before-crystal' else raw[0xd4]&128)
            n=enter(c,outside,house,key,new_episode=new_episode)
            plan=dict(steps=steps+[dict(kind='travel',room=house,point=[136,160],direction=1,target_room=outside)])
            c.service(f'case{n:02d}','sms_contact_plan',['--plan',json.dumps(plan)])
            output.write_text(json.dumps(dict(passed=True,key=key,trace=c.family+'/'+c.current,
                initial_prefix=initial,prerequisite_health_capacity=raw[0xda],prerequisite_lightning=raw[0xe4],
                prerequisite_crystal6=bool(raw[0xd4]&128)),indent=2)+'\n')
            print('EQUIPMENT PREREQUISITE VERIFIED',key,flush=True)
        finally:c.close()


if __name__=='__main__':main()
