"""Accept each reached inn in a distinct ordinary-input cold branch."""
import json
from run_core import ROOT
from continue_sms_npc_d4 import invoke,checked,SERVICE


def main():
    output=ROOT/'analysis/sms_inn_locations_campaign.json'
    old=json.loads(output.read_bytes()) if output.exists() else {}
    completed=old.get('completed_locations',[])
    tour=json.loads((ROOT/'analysis/sms_service_refusal_campaign.json').read_bytes())
    visits=[r for r in tour['completed_visits'] if r['kind']=='healer']
    def save():
        output.write_text(json.dumps(dict(status='all_eleven_inns_accepted_and_replayed' if len(completed)==11 else 'partial_locations_verified',
            completed_locations=completed,expected_locations=11,separate_branches=True,
            resource_fixtures=False,all_inn_variants_complete=False),indent=2)+'\n')
    for visit in visits:
        outside=visit['outside']
        if any(r['outside']==outside for r in completed):continue
        if outside==0x2e:name='sms-npc-paid-healer-2e-01'
        else:
            refusal=json.loads((ROOT/'validation'/visit['trace']/'report.json').read_bytes())
            trial=f'npc-inn-location-{outside:02x}-accept01';name='sms-'+trial
            if not (ROOT/'validation'/SERVICE/name).exists():
                invoke('run_sms_dialogue_observed.py',['sms_healer_service','--dialogue-core',
                    str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
                    '--sms','--assisted-prefix','--prefix',refusal['source_prefix'],'--trial',trial,
                    '--outside',hex(outside)],trial)
        checked(SERVICE,name,lambda r:r['passed'])
        report=json.loads((ROOT/'validation'/SERVICE/name/'report.json').read_bytes())
        completed.append(dict(outside=outside,trace=SERVICE+'/'+name,
            price=report['price'],health_before=report['health_before'],health_after=report['health_after'],
            gold_before=report['gold_before'],gold_after=report['gold_after'],
            magic_before=report['magic_before'],magic_after=report['magic_after']))
        save();print('ACTUAL INN VERIFIED',hex(outside),flush=True)
    save()


if __name__=='__main__':main()
