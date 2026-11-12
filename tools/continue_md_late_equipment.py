"""Acquire and revisit remaining optional MD equipment with actual controls."""
import argparse,json,subprocess,sys
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter as enter_house
from continue_sms_plain_house_census import census_world
def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);a=p.parse_args()
    output=ROOT/'analysis/md_late_equipment_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
    c=Campaign(old.get('last_verified_prefix',a.prefix),a.rom,'annex-late-equipment');verified=c.trace
    def save(status):output.write_bytes((json.dumps(dict(status=status,last_verified_prefix=verified,completed_visits=done,all_npcs_complete=False,scope='Separate actual New Game branch for the late gifts; early Plate Mail/Long Sword and absent-prerequisite branches have their own recordings.'),indent=2)+'\n').encode())
    def enter(outside,house,tag):
        return enter_house(c,outside,house,tag)
    def film(tag,first,kind,**fields):
        nonlocal verified
        with (ROOT/'validation'/(tag+'-video.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools/record_md_annex.py'),'--trace',c.trace,'--rom',str(c.rom),'--from-frame',str(first),'--name',tag],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        verified=c.trace;done.append(dict(kind=kind,trace=verified,**fields));save('played_replayed_filmed')
    def has(k):return any(v['kind']==k for v in done)
    try:
        c.verify(lambda r:r['passed'])
        for outside,house,field,value in [(0xb1,0x4f,0xf1,3),(0x6a,0x4f,0xe0,3),(0x4c,9,0xf2,3),(0x92,0x4f,0xe8,1),(0x55,0x1f,0xe2,1)]:
            kind=f'equipment-{outside:02x}'
            if not has(kind):
                assert not c.sms_view()[0x100+outside]&2,'A first-gift proof must start before the original reward flag'
                enter(outside,house,kind);first=c.cap()['frames']+1
                if house==0x1f:c.service(kind+'-gift01','natural_oil_stairs_service',['--outside',hex(outside)])
                else:c.service(kind+'-gift01','natural_house_quest',['--outside',hex(outside)])
                assert c.sms_view()[field]==value and c.sms_view()[0x100+outside]&2
                film('md-late-'+kind+'-cadeau01',first,kind,outside=outside)
            if has(kind+'-return'):continue
            enter(outside,house,kind+'-return');first=c.cap()['frames']+1
            if house==0x1f:
                steps=[dict(kind='travel',room=0x1f,point=[104,24],direction=0,target_room=15),dict(kind='silent',room=15,point=[104,56]),dict(kind='travel',room=15,point=[104,152],direction=1,target_room=0x1f),dict(kind='travel',room=0x1f,point=[136,160],direction=1,target_room=outside)]
            else:
                points=([152,56],[168,56]) if house==9 else ([120,72],[136,72])
                steps=[dict(kind='silent',room=house,point=point) for point in points]+[dict(kind='travel',room=house,point=[136,160],direction=1,target_room=outside)]
            reference=f'natural-service-route/sms-npc-equipment-returns-{outside:02x}-return'+('02' if outside==0x55 else '01')
            if not (ROOT/'validation'/reference/'report.json').exists():subprocess.run([sys.executable,str(ROOT/'tools/restore_validation_cache.py'),'--prefix','validation/'+reference],cwd=ROOT,check=True)
            c.service(kind+'-return01','md_contact_plan',['--plan',json.dumps(dict(steps=steps)),'--sms-reference',reference])
            film('md-late-'+kind+'-retour01',first,kind+'-return',outside=outside)
        save('five_late_gifts_and_their_returns_played_replayed_filmed')
    except Exception:save('failed_stage_not_counted');raise
    finally:c.close()
if __name__=='__main__':main()
