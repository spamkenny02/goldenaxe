"""Play ordinary original draws until the remaining lucky-card branch is seen."""
import json
from run_core import ROOT
from sms_campaign_runner import Campaign


def main():
    output=ROOT/'analysis/sms_minigame_lucky_campaign.json'
    if output.exists() and json.loads(output.read_bytes()).get('passed'):return
    old=json.loads(output.read_bytes()) if output.exists() else {};attempts=old.get('attempts',[])
    entry='natural-dungeon-route/sms-sms-npc-minigame-a7-play-entry01'
    for delay in (0,217,443,791):
        if any(r['initial_wait']==delay for r in attempts):continue
        c=Campaign(entry,0x15e,f'npc-minigame-lucky-wait{delay}')
        try:
            c.verify(lambda r:r['reached_entrance'])
            c.service('play01','sms_minigame_service',['--outside','0xa7','--variant','play','--rounds','16',
                '--initial-wait',str(delay),'--stop-on-lucky'])
            trace=c.family+'/'+c.current;r=json.loads((ROOT/'validation'/trace/'report.json').read_bytes())
            attempts.append(dict(initial_wait=delay,trace=trace,rounds=len(r['outcomes']),lucky_seen=r['lucky_card_observed']))
            result=dict(passed=r['lucky_card_observed'],attempts=attempts,source_rng_writes=0,currency_or_inventory_writes=0)
            if result['passed']:result['trace']=trace
            output.write_text(json.dumps(result,indent=2)+'\n')
            if result['passed']:print('ORIGINAL LUCKY CARD AND RESULT REPLAYED',flush=True);return
        finally:c.close()
    raise AssertionError('Lucky card not observed; no coverage claimed')


if __name__=='__main__':main()
