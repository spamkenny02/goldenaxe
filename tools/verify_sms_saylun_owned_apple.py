"""Buy an apple before the free Saylun gift, preserving the unclaimed quest."""
import json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter
from continue_sms_npc_d4 import invoke,SERVICE


def main():
    output=ROOT/'analysis/sms_owned_quest_item_saylun-owned-apple.json'
    if output.exists() and json.loads(output.read_bytes()).get('passed'):return
    initial='natural-service-route/sms-npc-villagec7-house1f-01'
    c=Campaign(initial,0x144,'npc-saylun-owned-apple');closed=False
    try:
        c.verify(lambda r:r['passed']);assert not c.raw()[0xe8] and not c.raw()[0x1c7]&2
        n=enter(c,0x55,1,'shop');entry=c.current;c.close();closed=True
        trial=f'npc-saylun-owned-apple-buy{n:02d}';purchase=SERVICE+'/sms-'+trial
        if not (ROOT/'validation'/purchase).exists():
            invoke('run_sms_dialogue_observed.py',['sms_merchant_cases','--dialogue-core',
                str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
                '--sms','--assisted-prefix','--prefix',entry,'--trial',trial,'--choices',json.dumps([dict(selection=0,expect='buy')]),
                '--refill-gold'],trial)
        assert json.loads((ROOT/'validation'/purchase/'report.json').read_bytes())['passed']
        case=f'npc-saylun-owned-apple-return{n:02d}';trace=SERVICE+'/sms-'+case
        if not (ROOT/'validation'/trace).exists():
            invoke('run_sms_dialogue_observed.py',['sms_economic_apple_return','--dialogue-core',
                str(ROOT.parents[1]/'work/genesis-plus-gx/genesis_plus_gx_sms_dialogue03_libretro.dll'),
                '--sms','--trace',purchase,'--trial',case],case)
        assert json.loads((ROOT/'validation'/trace/'report.json').read_bytes())['passed']
        proof=ROOT/'validation'/(trace+'-economic-fixed-replay')/'replay_report.json'
        if not proof.exists():invoke('replay_sms_economic_component.py',['--trace',trace],case+'-replay')
        assert json.loads(proof.read_bytes())['passed']
        output.write_text(json.dumps(dict(passed=True,trace=trace,purchase_trace=purchase,proof=proof.relative_to(ROOT).as_posix(),
            currency_assisted_component_test=True,natural_campaign_proof=False,inventory_actor_health_and_quest_writes=0,
            text_pc=0x905b,free_gift_unclaimed_before_and_after=True),indent=2)+'\n')
        print('SAYLUN OWNED APPLE REPLY REPLAYED; CURRENCY ASSISTANCE DECLARED',flush=True)
    finally:
        if not closed:c.close()


if __name__=='__main__':main()
