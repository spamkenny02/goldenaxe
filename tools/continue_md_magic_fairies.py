"""Acquire remaining teachings before fairy rewards, entirely by MD controls."""
import argparse,json,subprocess,sys
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import entry_options
from continue_sms_plain_house_census import census_world
def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);a=p.parse_args()
    output=ROOT/'analysis/md_magic_fairy_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
    c=Campaign(old.get('last_verified_prefix',a.prefix),a.rom,'annex-magic-fairies');verified=c.trace
    def save(status):output.write_bytes((json.dumps(dict(status=status,last_verified_prefix=verified,completed_visits=done,all_npcs_complete=False),indent=2)+'\n').encode())
    def enter(outside,house,tag):
        raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311])
        for direction in range(4):
            w=census_world(raw,outside,house,direction)
            if outside==0x2c:
                render=w.render_cells;w.render_cells=lambda room,cells,meta=None,render=render:render(room,bytearray(0x3a if b==0x3f else b for b in cells) if room==outside else cells,meta)
            options=entry_options(raw,outside,house,direction,w)
            if options and w.route(start)[0] is not None:
                tool,extra=options
                if outside==0xaa and not raw[0x1aa]&1:
                    extra=[x for x in extra if x!='--persisted-only'];extra+=['--bell-room','0xaa']
                attempt=1
                while (ROOT/f'validation/natural-dungeon-route/md-annex-magic-fairies-{tag}-entry{attempt:02d}').exists():attempt+=1
                c.route(tag+f'-entry{attempt:02d}',extra,tool);return
        raise AssertionError(('No reachable teacher/fairy proposal',outside,house))
    def film(tag,first):
        with (ROOT/'validation'/(tag+'-video.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools/record_md_annex.py'),'--trace',c.trace,'--rom',str(c.rom),'--from-frame',str(first),'--name',tag],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    try:
        c.verify(lambda r:r['passed'])
        # Complete the early-stat-dependent upgrades before remaining magic
        # fairies; source capacity growth deliberately rejects wrapping at128.
        for outside,teacher,levels in [(0xe6,0,[2]),(0x2c,2,[1,2]),(0xaa,3,[1])]:
            for level in levels:
                raw=c.sms_view()
                if raw[0xe4+teacher]>=level:continue
                if outside==0xaa:assert raw[0xea],'Bell must be owned in actual campaign'
                tag=f'teacher-{outside:02x}-level{level}'
                enter(outside,0xbf,tag);first=c.cap()['frames']+1;before=c.sms_view()
                c.service(tag+'-learn01','natural_house_service',['--outside',hex(outside),'--kind','teacher','--teacher',str(teacher),'--expected-level',str(level)])
                after=c.sms_view();assert after[0xe4+teacher]==level and after[0xdb]==after[0xdc]
                expected=before[0xdc]
                if not before[0xe4+teacher] and ((expected+24)&255)<128:expected=(expected+24)&255
                assert after[0xdc]==expected
                verified=c.trace;film('md-'+tag+'-learn01',first);done.append(dict(kind='teacher',outside=outside,teacher=teacher,level=level,magic_before=before[0xdc],magic_after=after[0xdc],trace=verified));save('teaching_played_replayed_filmed')
        assert list(c.sms_view()[0xe4:0xe8])==[2,2,2,1]
        targets=[x['context'] for x in json.loads((ROOT/'analysis/full_completion_checklist.json').read_bytes())['cases'] if x['category']=='fairy']
        for target in targets:
            outside=target['outside'];raw=c.sms_view()
            if any(v.get('kind')=='fairy' and v['outside']==outside for v in done):continue
            revisit=bool(raw[0x100+outside]&2);kind='magic' if target['kind']==255 else 'life';tag=f'fairy-{outside:02x}'
            enter(outside,0xaf,tag);first=c.cap()['frames']+1;before=c.sms_view();capacity=before[0xdc if kind=='magic' else 0xda]
            c.service(tag+'-contact01','natural_fairy_service',['--outside',hex(outside),'--kind',kind,'--expected-initial-capacity',str(capacity),*(['--revisit'] if revisit else [])])
            after=c.sms_view();verified=c.trace;film('md-'+tag+'-contact01',first);done.append(dict(kind='fairy',outside=outside,reward_kind=kind,revisit=revisit,capacity_before=capacity,capacity_after=after[0xdc if kind=='magic' else 0xda],trace=verified));save('fairy_played_replayed_filmed')
        assert c.sms_view()[0xda]==c.sms_view()[0xdc]==128
        save('all_teachings_and_eight_fairy_contacts_replayed_filmed_capacity128')
    except Exception:save('failed_stage_not_counted');raise
    finally:c.close()
if __name__=='__main__':main()
