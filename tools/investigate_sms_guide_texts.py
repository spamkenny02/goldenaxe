"""Play guide-identified NPC candidates, accepting any actual dialogue variant."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter
from continue_sms_npc_d4 import SERVICE


def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=['aires-bell','aires-after-linda','l10-earth1','l10-earth2','l15-earth2'],required=True);a=p.parse_args()
    specs={
        'aires-bell':('natural-service-route/sms-sms-npc-census-fe-03-visit01',0xfe,3),
        'aires-after-linda':('natural-service-route/sms-npc-extra-magic-aa-level1-learn02',0xfe,3),
        'l10-earth1':('natural-dungeon-combat/sms-auto-sms-npc-d5-exit01',0xab,0x8f),
        'l10-earth2':('natural-service-route/sms-sms-npc-census-ab-8f-visit01',0xab,0x8f),
        'l15-earth2':('natural-service-route/sms-sms-npc-census-fb-8f-visit01',0xfb,0x8f)}
    initial,outside,house=specs[a.case];label='guide-text-'+a.case;c=Campaign(initial,0x15e,label)
    output=ROOT/f'analysis/sms_guide_text_test_{a.case}.json'
    if output.exists() and json.loads(output.read_bytes()).get('passed'):c.close();return
    try:
        c.verify(lambda r:r.get('passed') or r.get('full_dungeon_cleared'))
        before=c.raw();bell_trace=None
        if a.case=='aires-after-linda':assert before[0xe7]==1 and before[0x1aa]&1
        if a.case=='aires-bell':
            ring=1
            while (ROOT/f'validation/natural-service-route/sms-{label}-ring{ring:02d}').exists():
                prior=ROOT/f'validation/natural-service-route/sms-{label}-ring{ring:02d}/report.json'
                if prior.exists() and json.loads(prior.read_bytes()).get('passed'):break
                ring+=1
            c.service(f'ring{ring:02d}','sms_bell_dialogue_probe',[]);bell_trace=c.family+'/'+c.current
            attempt=1
            while (ROOT/f'validation/natural-service-route/sms-{label}-weapon{attempt:02d}').exists():attempt+=1
            c.equip(1,f'weapon{attempt:02d}')
        n=enter(c,outside,house,'entry',new_episode=a.case=='l10-earth1')
        trial='sms-'+label+f'-probe{n:02d}';trace=SERVICE+'/'+trial
        c.invoke('run_sms_dialogue_observed.py',['sms_npc_visit','--dialogue-core',
            str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
            '--sms','--assisted-prefix','--probe-text-variants','--prefix',c.family+'/'+c.current,
            '--outside',hex(outside),'--room',hex(house),'--out',trace],SERVICE,trial,lambda r:r['passed'])
        played=json.loads((ROOT/'validation'/trace/'report.json').read_bytes())
        result=dict(passed=True,case=a.case,initial_prefix=initial,bell_action_trace=bell_trace,
            trace=trace,outside=outside,room=house,earth_level=before[0xe5],bell_owned=before[0xea],
            water_level=before[0xe7],linda_bell_passage_open=bool(before[0x1aa]&1),ninth_crystal=bool(before[0xd7]&128),
            actual_visits=played['visited'],unknown_variants_accepted_by_controller=True,
            no_inventory_currency_or_quest_injections=True,
            reported_strings_triggered=[v for v in played['visited'] if v['text_pc'] in (0x9a58,0x9a7c,0xad3c)])
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
    finally:c.close()


if __name__=='__main__':main()
