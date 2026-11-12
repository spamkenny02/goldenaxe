"""Play, cold-replay and film the same 48 service refusals retained on SMS."""
import argparse,json,subprocess,sys,hashlib
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import entry_options
from continue_sms_plain_house_census import census_world
def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);a=p.parse_args()
    source=json.loads((ROOT/'analysis/sms_service_refusal_campaign.json').read_bytes());targets=source['completed_visits'];assert len(targets)==48
    output=ROOT/'analysis/md_service_refusal_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_visits',[]);pending=[t for t in targets if not any((t['outside'],t['kind'])==(d['outside'],d['kind']) for d in done)]
    c=Campaign(old.get('last_verified_prefix',a.prefix),a.rom,'annex-services');verified=c.trace
    def save(status):output.write_bytes((json.dumps(dict(status=status,last_verified_prefix=verified,completed_visits=done,pending=pending,all_48_refusals_verified_and_filmed=not pending,all_npcs_complete=False),indent=2)+'\n').encode())
    try:
        c.verify(lambda r:r['passed'])
        while pending:
            raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);chosen=None
            for target in sorted(pending,key=lambda t:abs((t['outside']&15)-(start[0]&15))+abs((t['outside']>>4)-(start[0]>>4))):
                for direction in range(4):
                    w=census_world(raw,target['outside'],target['room'],direction);options=entry_options(raw,target['outside'],target['room'],direction,w)
                    if options and w.route(start)[0] is not None:chosen=target,options;break
                if chosen:break
            assert chosen,'Pending services need actual transport or missing ability'
            t,(tool,extra)=chosen;tag=f'{t["outside"]:02x}-{t["kind"]}';attempt=1
            while (ROOT/f'validation/natural-dungeon-route/md-annex-services-{tag}-entry{attempt:02d}').exists():attempt+=1
            print('MD SERVICE START',tag,'remaining',len(pending),flush=True)
            previous=c.family,c.current;entered=False
            # Combat can reveal an entrance from a different side than the
            # base-map proposal. Retry only planning failures from the same
            # verified controller prefix; never count a failed attempt.
            for direction in range(4):
                c.family,c.current=previous
                known_failure=False
                for earlier in (ROOT/'validation/natural-dungeon-route').glob(f'md-annex-services-{tag}-entry*/route_report.json'):
                    old_route=json.loads(earlier.read_bytes())
                    if old_route.get('door_entry_direction')!=direction or old_route.get('recorded_service_prefix')!=previous[1] or old_route.get('failure') not in ('unexpected_position','no_waypoint_progress','frame_limit'):continue
                    if old_route.get('route_driver_sha256')!=hashlib.sha256((ROOT/'tools/natural_dungeon_route.py').read_bytes()).hexdigest():continue
                    assist_path=earlier.parent/'assistance.json'
                    if not assist_path.exists():continue
                    assist=json.loads(assist_path.read_bytes())
                    if assist.get('prefix_capture_sha256')==hashlib.sha256((ROOT/'validation'/c.trace/'capture.json').read_bytes()).hexdigest():known_failure=True;break
                if known_failure:
                    print('SKIP IDENTICAL FAILED ENTRY PROPOSAL',tag,direction,flush=True);continue
                w=census_world(raw,t['outside'],t['room'],direction);options=entry_options(raw,t['outside'],t['room'],direction,w)
                if not options or w.route(start)[0] is None:continue
                tool,extra=options
                while (ROOT/f'validation/natural-dungeon-route/md-annex-services-{tag}-entry{attempt:02d}').exists():attempt+=1
                try:
                    c.route(tag+f'-entry{attempt:02d}',extra,tool);entered=True;break
                except (AssertionError,subprocess.CalledProcessError):
                    trial=ROOT/f'validation/natural-dungeon-route/md-annex-services-{tag}-entry{attempt:02d}/route_report.json'
                    if not trial.exists():raise
                    failed=json.loads(trial.read_bytes())
                    if failed['failure'] not in ('unexpected_position','no_waypoint_progress','frame_limit') or failed.get('normal_continues') or not failed['last_state']['health']:raise
                    print('MD ENTRY PLANNER RETRY',tag,'direction',direction,'reason',failed['failure'],flush=True)
            assert entered,('No actual entrance verified from any proposed side',tag)
            first=c.cap()['frames']+1
            ref=ROOT/'validation'/t['trace']
            if not (ref/'report.json').exists():subprocess.run([sys.executable,str(ROOT/'tools/restore_validation_cache.py'),'--prefix','validation/'+t['trace']],cwd=ROOT,check=True)
            c.service(tag+f'-refuse{attempt:02d}','md_service_refusal',['--outside',hex(t['outside']),'--kind',t['kind'],'--sms-reference',t['trace'],'--approach-guard']);verified=c.trace
            name='service-'+tag+f'-refus-ntsc{attempt:02d}'
            with (ROOT/'validation'/(name+'-video.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools/record_md_annex.py'),'--trace',c.trace,'--rom',str(c.rom),'--from-frame',str(first),'--name',name],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            done.append(dict(outside=t['outside'],room=t['room'],kind=t['kind'],sms_reference=t['trace'],trace=c.trace,video_report='videos/md-annexes-2026-11-12/'+name+'/report.json'));pending.remove(t);save('running_played_replayed_filmed')
            subprocess.run([sys.executable,str(ROOT/'tools/summarize_md_annex_replay.py')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        save('all_48_refusals_played_replayed_filmed')
    except Exception:save('failed_stage_not_counted');raise
    finally:c.close()
if __name__=='__main__':main()
