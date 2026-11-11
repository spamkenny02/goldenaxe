"""Play the six goods groups and shared economic branches from genuine states."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter


def main():
    p=argparse.ArgumentParser();p.add_argument('--cases',required=True);a=p.parse_args()
    specs={
        'g0':(0xf9,[(1,'buy'),(1,'full'),(2,'buy'),(2,'owned'),(0,'poor')]),
        'g1':(0x4e,[(0,'buy'),(0,'owned'),(1,'buy'),(1,'owned'),(2,'poor')]),
        'g2':(0x2e,[(0,'buy'),(1,'buy'),(2,'poor')]),
        'g3':(0xd7,[(0,'buy'),(1,'buy'),(2,'buy'),(1,'owned'),(2,'owned')]),
        'g4':(0xf2,[(0,'buy'),(0,'full'),(1,'buy'),(2,'buy')]),
        'g5':(0x94,[(0,'buy'),(1,'buy'),(2,'buy')]),
        'g2oil':(0x2e,[(2,'buy'),(1,'buy'),(0,'poor')]),
        'shield-owned':(0xf9,[(0,'owned')]),
        'shield-better':(0xf9,[(0,'better')]),
        'apple-only':(0xf0,[(0,'buy'),(0,'owned')]),
        'apple-poor':(0xf0,[(0,'poor')]),
        'magic64':(0x7b,[(2,'buy'),(0,'buy'),(1,'full')]),
        'magic32-poor':(0x7b,[(1,'buy'),(1,'buy'),(0,'poor')]),
        'magic-clamp':(0x7b,[(2,'buy'),(0,'full')]),
        'magic-poor':(0x7b,[(0,'poor')]),
    }
    for key in a.cases.split(','):
        output=ROOT/f'analysis/sms_merchant_variant_{key}.json'
        if output.exists() and json.loads(output.read_bytes()).get('passed'):continue
        outside,choices=specs[key]
        initial=('natural-service-route/sms-npc-service-refusals-8d-merchant-refuse04' if key in ('magic64','magic32-poor') else
            'natural-service-route/sms-npc-knight-shield-f9-buy01' if key in ('shield-owned','magic-poor','apple-poor') else
            'natural-service-route/sms-npc-hidden-rewards-55-gift01' if key=='shield-better' else
            'natural-service-route/sms-npc-gold-funding-ee-gift01')
        c=Campaign(initial,0x15e,'npc-merchant-variant-'+key)
        try:
            c.verify(lambda r:r['passed'])
            doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors']
            house=next(d['target'] for d in doors if d['room']==outside and d['target'] in (0,1,0x2f))
            n=enter(c,outside,house,key)
            c.service(f'{key}-choices{n:02d}','sms_merchant_cases',['--choices',json.dumps([dict(selection=s,expect=e) for s,e in choices])])
            result=dict(passed=True,key=key,outside=outside,initial_prefix=initial,trace=c.family+'/'+c.current,
                frame=c.cap()['frames'],choices=choices)
            output.write_text(json.dumps(result,indent=2)+'\n');print('MERCHANT VARIANTS VERIFIED',key,flush=True)
        finally:c.close()


if __name__=='__main__':main()
