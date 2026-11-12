"""Replay actual Gillian/apple and first equipment branches before higher gear."""
import argparse,json,subprocess,sys
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import entry_options
from continue_sms_plain_house_census import census_world
def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);a=p.parse_args()
    output=ROOT/'analysis/md_early_equipment_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
    c=Campaign(old.get('last_verified_prefix',a.prefix),a.rom,'annex-early-equipment');verified=c.trace
    def save(status):output.write_bytes((json.dumps(dict(status=status,last_verified_prefix=verified,completed_visits=done,all_npcs_complete=False),indent=2)+'\n').encode())
    def enter(outside,house,tag):
        raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
        for d in range(4):
            w=census_world(raw,outside,house,d);options=entry_options(raw,outside,house,d,w)
            if options and w.route(start)[0] is not None:tool,extra=options;c.route(tag+'-entry01',extra,tool);return
        raise AssertionError(('Missing actual early approach',outside,house))
    def complete(tag,first,kind,**fields):
        nonlocal verified
        with (ROOT/'validation'/(tag+'-video.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools/record_md_annex.py'),'--trace',c.trace,'--rom',str(c.rom),'--from-frame',str(first),'--name',tag],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        verified=c.trace;done.append(dict(kind=kind,trace=verified,**fields));save('played_replayed_filmed')
    def has(kind):return any(d['kind']==kind for d in done)
    try:
        c.verify(lambda r:r['passed'])
        for tag in ('gillian-introduction','gillian-apple-absent'):
            if has(tag):continue
            assert not c.sms_view()[0xe4]
            # A later retained campaign already owns the real C7 apple.
            # Do not erase it to manufacture an absent-item branch.
            if tag=='gillian-apple-absent' and c.sms_view()[0xe8]:continue
            enter(0xe6,0xbf,tag);first=c.cap()['frames']+1
            c.service(tag+'-contact01','natural_house_service',['--outside','0xe6','--kind','teacher','--teacher','0','--expected-level','0']);complete('md-'+tag+'01',first,tag)
        if not has('saylun-apple-gift') and not c.sms_view()[0xe8]:
            enter(0xc7,0x1f,'saylun-chimney');first=c.cap()['frames']+1
            c.service('saylun-apple-gift01','natural_oil_stairs_service',['--outside','0xc7']);assert c.sms_view()[0xe8]==1
            complete('md-saylun-cheminee-pomme01',first,'saylun-apple-gift',outside=0xc7)
        if not has('gillian-lightning1'):
            enter(0xe6,0xbf,'gillian-apple-present');first=c.cap()['frames']+1
            c.service('gillian-lightning1-learn01','natural_house_service',['--outside','0xe6','--kind','teacher','--teacher','0','--expected-level','1']);assert not c.sms_view()[0xe8] and c.sms_view()[0xe4]==1
            complete('md-gillian-foudre1-pomme-consommee01',first,'gillian-lightning1')
        for outside,field,value in [(0x27,0xf1,2),(0x50,0xe0,2)]:
            kind=f'equipment-{outside:02x}'
            if has(kind):continue
            enter(outside,0x4f,kind);first=c.cap()['frames']+1
            c.service(kind+'-gift01','natural_house_quest',['--outside',hex(outside)]);assert c.sms_view()[field]==value
            complete('md-'+kind+'-cadeau01',first,kind,outside=outside)
        save('selected_gillian_and_equipment_branches_verified_earlier_apple_absent_and_gift_require_separate_prefix')
    except Exception:save('failed_stage_not_counted');raise
    finally:c.close()
if __name__=='__main__':main()
