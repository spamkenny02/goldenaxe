"""Complete refusal and insufficient-funds variants in genuine played states."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter


def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);a=p.parse_args()
    for key in a.cases.split(','):
        output=ROOT/f'analysis/sms_service_alternative_{key}.json'
        if output.exists() and json.loads(output.read_bytes()).get('passed'):continue
        if key.startswith('passage-refuse-'):
            outside=int(key.rsplit('-',1)[1],16)
            tour=json.loads((ROOT/'analysis/sms_passage_census_campaign.json').read_bytes())
            trace=next(r['trace'] for r in tour['completed_passages'] if r['outside']==outside)
            initial='natural-dungeon-route/'+json.loads((ROOT/'validation'/trace/'report.json').read_bytes())['source_prefix']
            kind='passage';variant='refuse'
        else:
            initial='natural-service-route/sms-npc-knight-shield-f9-buy01'
            kind='passage' if key=='passage-poor' else 'inn';variant='poor'
            outside=0x6d if kind=='passage' else 0x55 if key=='inn20-poor' else 0x2e
        c=Campaign(initial,0x15e,'npc-service-alt-'+key)
        try:
            c.verify(lambda r:r.get('passed') or r.get('reached_entrance'))
            n=1
            if c.family!='natural-dungeon-route':
                doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors']
                houses=(0x9f,) if kind=='passage' else tuple(r[0] for r in json.loads((ROOT/'analysis/healer_assets.json').read_bytes())['nodes'])
                house=next(d['target'] for d in doors if d['room']==outside and d['target'] in houses)
                n=enter(c,outside,house,key)
            else:
                while (ROOT/f'validation/natural-service-route/sms-npc-service-alt-{key}-case{n:02d}').exists():n+=1
            c.service(f'case{n:02d}','sms_service_alternatives',['--kind',kind,'--variant',variant])
            output.write_text(json.dumps(dict(passed=True,key=key,outside=outside,trace=c.family+'/'+c.current),indent=2)+'\n')
            print('SERVICE ALTERNATIVE VERIFIED',key,flush=True)
        finally:c.close()


if __name__=='__main__':main()
