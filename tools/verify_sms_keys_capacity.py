"""Buy keys normally up to 99 using the user's authorized currency assistance."""
import json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter
from continue_sms_npc_d4 import invoke,SERVICE


def main():
    output=ROOT/'analysis/sms_keys_capacity_component_report.json'
    if output.exists() and json.loads(output.read_bytes()).get('passed'):return
    initial='natural-service-route/sms-npc-gold-funding-ee-gift01'
    c=Campaign(initial,0x15e,'npc-key-capacity');closed=False
    try:
        c.verify(lambda r:r['passed']);n=enter(c,0x94,0,'keys');entry=c.current
        count=99-c.raw()[0xde];assert count>0
        choices=[dict(selection=0,expect='buy') for _ in range(count)]+[dict(selection=0,expect='full')]
        c.close();closed=True;trial=f'npc-key-capacity99-{n:02d}';trace=SERVICE+'/sms-'+trial
        if not (ROOT/'validation'/trace).exists():
            invoke('run_sms_dialogue_observed.py',['sms_merchant_cases','--dialogue-core',
                str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
                '--sms','--assisted-prefix','--prefix',entry,'--trial',trial,'--choices',json.dumps(choices),
                '--refill-gold','--budget','80000'],trial)
        r=json.loads((ROOT/'validation'/trace/'report.json').read_bytes());assert r['passed']
        proof=ROOT/'validation'/(trace+'-economic-fixed-replay')/'replay_report.json'
        if not proof.exists():invoke('replay_sms_economic_component.py',['--trace',trace],trial+'-replay')
        checked=json.loads(proof.read_bytes());assert checked['passed'] and checked['final_keys']==99
        assert len([x for x in r['completed'] if x['expect']=='buy'])==count and r['completed'][-1]['text_pc']==0x8c45
        output.write_text(json.dumps(dict(passed=True,trace=trace,proof=proof.relative_to(ROOT).as_posix(),
            ordinary_key_purchases=count,final_keys=99,full_refusal_text=0x8c45,
            currency_assisted_component_test=True,natural_campaign_proof=False,
            inventory_actor_health_and_quest_writes=0),indent=2)+'\n')
        print('99 KEYS PURCHASED AND FULL REFUSAL REPLAYED; CURRENCY ASSISTANCE DECLARED',flush=True)
    finally:
        if not closed:c.close()


if __name__=='__main__':main()
