"""Earn real house money, then purchase Earth II before late optional visits."""
import argparse,json,subprocess,sys
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import entry_options
from continue_sms_plain_house_census import census_world
def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);a=p.parse_args()
    output=ROOT/'analysis/md_annex_earth2_preparation.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
    c=Campaign(old.get('last_verified_prefix',a.prefix),a.rom,'annex-earth2');verified=c.trace
    gifts=json.loads((ROOT/'analysis/house_gold_reference.json').read_bytes())['records']
    doors=json.loads((ROOT/'analysis/doors_reference.json').read_bytes())['direct_unconditional_doors']
    def save(status):output.write_bytes((json.dumps(dict(status=status,last_verified_prefix=verified,completed_visits=done,all_npcs_complete=False),indent=2)+'\n').encode())
    def enter(outside,house,tag):
        raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
        for d in range(4):
            w=census_world(raw,outside,house,d);options=entry_options(raw,outside,house,d,w)
            if options and w.route(start)[0] is not None:
                tool,extra=options;c.route(tag+'-entry01',extra,tool);return
        raise AssertionError(('No actual approach proposal',outside,house))
    def film(tag,first):
        with (ROOT/'validation'/(tag+'-video.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools/record_md_annex.py'),'--trace',c.trace,'--rom',str(c.rom),'--from-frame',str(first),'--name',tag],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    try:
        c.verify(lambda r:r['passed'])
        while c.sms_view()[0xe5]<2 and c.sms_view()[0xdd]<100:
            raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
            pending=[(n,v) for n,v in gifts if 0<v<128 and not raw[0x100+n]&2 and any(d['room']==n and d['target']==0x3f for d in doors)]
            pending.sort(key=lambda t:(-t[1],abs((t[0]&15)-(start[0]&15))+abs((t[0]>>4)-(start[0]>>4))))
            chosen=None
            for outside,gain in pending:
                for direction in range(4):
                    w=census_world(raw,outside,0x3f,direction);options=entry_options(raw,outside,0x3f,direction,w)
                    if options and w.route(start)[0] is not None:chosen=(outside,gain,options);break
                if chosen:break
            assert chosen,'No unclaimed reachable positive gold house'
            outside,gain,(tool,extra)=chosen;tag=f'argent-{outside:02x}'
            print('MD ACTUAL GOLD HOUSE',hex(outside),gain,'balance',raw[0xdd],flush=True)
            c.route(tag+'-entry01',extra,tool);first=c.cap()['frames']+1
            c.service(tag+'-gift01','natural_house_service',['--kind','gold','--outside',hex(outside),'--gold-gain',str(gain)])
            verified=c.trace;film('md-'+tag+'-cadeau01',first);done.append(dict(outside=outside,kind='gold',gain=gain,trace=verified));save('real_gold_gift_played_replayed_filmed')
        if c.sms_view()[0xe5]<2:
            enter(0xa3,0xbf,'battler');first=c.cap()['frames']+1;before=c.sms_view()
            c.service('battler-earth2-learn01','natural_house_service',['--outside','0xa3','--kind','teacher','--teacher','1','--expected-level','2'])
            after=c.sms_view();assert after[0xe5]==2 and after[0xdd]==before[0xdd]-100 and after[0xdc]==before[0xdc]
            verified=c.trace;film('md-battler-terre2-achat01',first);done.append(dict(outside=0xa3,kind='earth2_purchase',price=100,trace=verified))
        save('earth2_actually_purchased_ready_for_optional_entrances')
    except Exception:save('failed_stage_not_counted');raise
    finally:c.close()
if __name__=='__main__':main()
