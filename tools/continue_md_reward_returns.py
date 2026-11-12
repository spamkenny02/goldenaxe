"""Replay fully learned teacher replies and post-reward fairy contacts on MD."""
import argparse,json
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);a=p.parse_args()
    output=ROOT/'analysis/md_reward_returns_campaign.json'
    old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[])
    c=Campaign(old.get('last_verified_prefix',a.prefix),a.rom,'annex-reward-returns');verified=c.trace
    def save(status):
        output.write_bytes((json.dumps(dict(status=status,last_verified_prefix=verified,completed_visits=done,
            all_npcs_complete=False,scope='Separate genuine New Game continuation: known teachers after learning and fairies after their once-only rewards. No quest, money, health or save imports.'),indent=2)+'\n').encode())
    try:
        c.verify(lambda r:r['passed'])
        raw=c.sms_view();assert list(raw[0xe4:0xe8])==[2,2,2,1] and raw[0xda]==raw[0xdc]==128
        targets=[dict(kind='teacher',outside=outside,teacher=teacher,level=level) for outside,teacher,level in [(0xa3,1,2),(0xe6,0,2),(0xaa,3,1),(0x2c,2,2)]]
        targets += [dict(kind='fairy',outside=row['context']['outside'],reward_kind='magic' if row['context']['kind']==255 else 'life')
            for row in json.loads((ROOT/'analysis/full_completion_checklist.json').read_bytes())['cases'] if row['category']=='fairy']
        for target in targets:
            if any((v['kind'],v['outside'])==(target['kind'],target['outside']) for v in done):continue
            outside=target['outside'];kind=target['kind'];tag=f'{kind}-{outside:02x}'
            if kind=='fairy':assert c.sms_view()[0x100+outside]&2,'No first reward may be synthesized for a return'
            attempt=enter(c,outside,0xbf if kind=='teacher' else 0xaf,tag)
            first=c.cap()['frames']+1;before=c.sms_view()
            if kind=='teacher':
                c.service(tag+f'-return{attempt:02d}','natural_house_service',['--outside',hex(outside),'--kind','teacher','--teacher',str(target['teacher']),'--expected-level',str(target['level'])])
            else:
                c.service(tag+f'-return{attempt:02d}','natural_fairy_service',['--outside',hex(outside),'--kind',target['reward_kind'],'--expected-initial-capacity','128','--revisit'])
            after=c.sms_view()
            assert after[0xe0:0xf3]==before[0xe0:0xf3] and after[0xdd:0xdf]==before[0xdd:0xdf]
            assert after[0xda:0xdd]==before[0xda:0xdd] and after[0x100+outside]==before[0x100+outside]
            name=f'md-{c.label}-{tag}-return{attempt:02d}';film(c,name,first)
            verified=c.trace;done.append(dict(**target,trace=verified,video_report=f'videos/md-annexes-2026-11-12/{name}/report.json',items_currency_capacity_and_reward_flags_unchanged=True))
            save('played_replayed_filmed')
        assert len(done)==12
        save('four_teacher_replies_and_eight_fairy_returns_played_replayed_filmed')
    except Exception:save('failed_stage_not_counted');raise
    finally:c.close()


if __name__=='__main__':main()
