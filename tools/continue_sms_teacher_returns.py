"""Return to each fully learned teacher and verify the original owned-spell reply."""
import argparse,json
from run_core import ROOT
from sms_campaign_runner import Campaign
from continue_sms_plain_house_census import census_world


def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);a=p.parse_args()
    output=ROOT/'analysis/sms_teacher_returns_campaign.json'
    old=json.loads(output.read_bytes()) if output.exists() else {};visits=old.get('completed_visits',[])
    c=Campaign(visits[-1]['trace'] if visits else a.prefix,0x15e,'npc-teacher-returns');verified=c.family+'/'+c.current
    def save(status):
        output.write_text(json.dumps(dict(status=status,initial_prefix=a.prefix,last_verified_prefix=verified,
            completed_visits=visits,all_teacher_variants_complete=False),indent=2)+'\n')
    try:
        c.verify(lambda r:r['passed']);assert list(c.raw()[0xe4:0xe8])==[2,2,2,1]
        pending=[(0xa3,1,2),(0xe6,0,2),(0xaa,3,1),(0x2c,2,2)]
        for outside,teacher,level in pending:
            if any(v['teacher']==teacher for v in visits):continue
            raw=c.raw();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);chosen=None
            for d in range(4):
                w=census_world(raw,outside,0xbf,d)
                if outside==0x2c:
                    render=w.render_cells
                    w.render_cells=lambda room,cells,meta=None,render=render:render(room,bytearray(0x3a if b==0x3f else b for b in cells) if room==0x2c else cells,meta)
                if w.route(start)[0] is not None:chosen=d;break
            assert chosen is not None
            extra=['--house-outside',hex(outside),'--house-target','0xbf','--persisted-only',
                '--live-prefix-terrain','--door-entry-direction',str(chosen)]
            tool='natural_bell_world_route.py'
            if outside==0x2c:tool='natural_frozen_earth_world_route.py';extra+=['--earth-world-cell','0x41']
            n=1
            while (ROOT/f'validation/natural-dungeon-route/sms-sms-npc-teacher-returns-{outside:02x}-entry{n:02d}').exists():n+=1
            c.route(f'{outside:02x}-entry{n:02d}',extra,tool=tool);before=c.raw()
            c.service(f'{outside:02x}-visit{n:02d}','natural_house_service',
                ['--outside',hex(outside),'--kind','teacher','--teacher',str(teacher),'--expected-level',str(level)])
            after=c.raw();assert after[0xe0:0xf3]==before[0xe0:0xf3] and after[0xdd]==before[0xdd]
            assert after[0xda]==before[0xda] and after[0xdc]==before[0xdc]
            verified=c.family+'/'+c.current
            visits.append(dict(outside=outside,teacher=teacher,level=level,trace=verified,frame=c.cap()['frames']))
            save('running');print('FULLY LEARNED TEACHER RETURN VERIFIED',hex(outside),flush=True)
        save('all_four_fully_learned_teacher_returns_replayed')
    except Exception:save('failed_objective_not_counted');raise
    finally:c.close()


if __name__=='__main__':main()
