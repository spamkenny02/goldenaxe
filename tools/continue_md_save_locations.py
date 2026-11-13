"""Write and normally reload a genuine game save at every known MD save NPC."""
import argparse,json,subprocess,sys
from run_core import ROOT
from md_campaign_runner import Campaign
from md_campaign_navigation import enter,film,entry_options,refill_magic
from continue_sms_plain_house_census import census_world

def main():
    p=argparse.ArgumentParser();p.add_argument('--prefix',required=True);p.add_argument('--rom',required=True);a=p.parse_args()
    output=ROOT/'analysis/md_save_locations_campaign.json';old=json.loads(output.read_bytes()) if output.exists() else {};done=old.get('completed_locations',[])
    targets=[r for r in json.loads((ROOT/'analysis/sms_service_refusal_campaign.json').read_bytes())['completed_visits'] if r['kind']=='save'];assert len(targets)==14
    c=Campaign(old.get('last_verified_prefix',a.prefix),a.rom,'annex-save-locations');verified=c.trace
    def save(status):output.write_bytes((json.dumps(dict(status=status,last_verified_prefix=verified,completed_locations=done,required_locations=14,all_fourteen_written_replayed_and_loaded=len(done)==14,all_npcs_complete=False),indent=2)+'\n').encode())
    def invoke(tool,args,label):
        with (ROOT/'validation'/(label+'.log')).open('w') as log:subprocess.run([sys.executable,str(ROOT/'tools'/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    try:
        c.verify(lambda r:r['passed'])
        while len(done)<14:
            if c.sms_view()[0xdb]<8:refill_magic(c);verified=c.trace;save('genuine_magic_refill_filmed')
            raw=c.sms_view();start=(int.from_bytes(raw[0xb9:0xbb],'little'),raw[0x313],raw[0x311]);choices=[]
            for target in targets:
                if any(row['outside']==target['outside'] for row in done):continue
                for d in range(4):
                    world=census_world(raw,target['outside'],target['room'],d)
                    if not entry_options(raw,target['outside'],target['room'],d,world):continue
                    path,_=world.route(start)
                    if path is not None:choices.append((len(path),target['outside'],target));break
            assert choices,'A remaining save NPC requires a new genuine access route'
            target=min(choices,key=lambda row:row[:2])[2];outside=target['outside'];tag=f'{outside:02x}'
            attempt=enter(c,outside,target['room'],tag);first=c.cap()['frames']+1
            raw=c.raw();at=c.sy['save_last_slot'];overwrite=bool(raw[at]|raw[at+1]<<8)
            c.service(tag+f'-write{attempt:02d}','natural_save_service',['--slot','0','--exit-after',*(['--overwrite'] if overwrite else [])]);write_trace=c.trace
            film(c,f'md-{c.label}-{tag}-write{attempt:02d}',first)
            trial=f'md-save-{tag}-continue{attempt:02d}';reload_trace='game-written-save-load/'+trial
            report=ROOT/'validation'/reload_trace/'report.json'
            if not report.exists():invoke('validate_game_written_save.py',['--trace',write_trace,'--rom',str(c.rom),'--trial',trial,'--release-report-name',trial+'.json'],trial+'-write-and-load')
            assert json.loads(report.read_bytes())['passed']
            if not report.parent.with_name(report.parent.name+'-fixed-replay').exists():invoke('replay_natural_campaign.py',['--trace',reload_trace,'--rom',str(c.rom),'--game-written-continue'],trial+'-fixed')
            invoke('record_md_annex.py',['--trace',reload_trace,'--rom',str(c.rom),'--from-frame','1','--name',trial,'--game-written-continue'],trial+'-movie')
            verified=c.trace;done.append(dict(outside=outside,save_trace=write_trace,continue_trace=reload_trace,slot=0,overwrote_existing_game_save=overwrite,continue_report=report.relative_to(ROOT).as_posix(),continue_video_report=f'videos/md-annexes-2026-11-12/{trial}/report.json'));save('actual_write_full_sram_replay_and_normal_continue_filmed')
        save('all_fourteen_save_locations_written_replayed_loaded_and_filmed')
    except Exception:save('failed_stage_not_counted');raise
    finally:c.close()

if __name__=='__main__':main()
