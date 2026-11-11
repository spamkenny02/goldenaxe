"""Return to a paid inn after its real night, and pay again at full health."""
import json
from run_core import ROOT
from sms_campaign_runner import Campaign
from sms_campaign_navigation import enter


def main():
    output=ROOT/'analysis/sms_inn_repeat_report.json'
    if output.exists() and json.loads(output.read_bytes()).get('passed'):return
    old=json.loads((ROOT/'analysis/sms_inn_locations_campaign.json').read_bytes())
    first=next(v for v in old['completed_locations'] if v['outside']==0x55)
    c=Campaign(first['trace'],0x15e,'npc-inn-repeat')
    try:
        c.verify(lambda r:r['passed']);before=c.raw();assert before[0x318]==before[0xda] and before[0xdd]>=20
        n=enter(c,0x55,1,'kari')
        c.service(f'rest{n:02d}','sms_healer_service',['--outside','0x55'])
        after=c.raw();assert after[0x318]==before[0xda] and after[0xdd]==before[0xdd]-20 and after[0xdb]==before[0xdb]
        output.write_text(json.dumps(dict(passed=True,first_night_trace=first['trace'],second_night_trace=c.family+'/'+c.current,
            health_already_full=True,gold_before=before[0xdd],gold_after=after[0xdd],magic_preserved=True),indent=2)+'\n')
        print('PAID INN RETURN AT FULL HEALTH VERIFIED',flush=True)
    finally:c.close()


if __name__=='__main__':main()
