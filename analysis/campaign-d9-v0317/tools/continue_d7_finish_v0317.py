"""Continue current D7 through the ship, main boss, seventh crystal and exit."""
import json,shutil
from cold_replay_stream import ReplayStream
import subprocess
import sys
from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from run_core import ROOT


def main():
    prior=json.loads(evidence(ROOT/'analysis/d7_midboss_v0317_report.json'))
    assert prior['passed'] and prior['intermediate_defeated'] and not prior['intermediate_assistance']
    assert prior['md_sha256'] == sha((ROOT/'gaw-megadrive.bin').read_bytes())
    prefix='v0317-d7-02-'
    previous=prior['stages'][-1]['trace'].split('/')[-1]
    assert previous=='md-auto-'+prefix+'resume01'
    out=ROOT/'validation/run-v0317-d7-finish-02'
    out.mkdir(exist_ok=False)
    source_index={}
    for name in ('continue_d7_finish_v0317.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py','natural_contact_passage.py','natural_item_acquisition.py','natural_earth_passage.py','close_assisted_approach.py','unassisted_dungeon_continuation.py','unassisted_arrival_prediction.py','unassisted_fast_prediction.py','natural_exit_planner.py','natural_boss_evasive_planner.py','natural_combat_beam.py','prediction_video_skip.py','cold_replay_stream.py','run_core.py'):
        target=out/name;shutil.copyfile(ROOT/'tools'/name,target);source_index['tools/'+name]=sha(target.read_bytes())
    (out/'source_index.json').write_text(json.dumps(source_index,indent=2)+'\n')
    stream=ReplayStream(out/'cold-stream')
    try:
        points=[]
        common=['--assisted-prefix','--max-deaths','0','--collision-aim',
                '--settle-attacks','--doorway-ranges','--ignore-inactive-actors']

        def load(path):
            return json.loads(evidence(path))

        def run(tool,arguments):
            print('START',tool,*arguments,flush=True)
            with (out/'commands.jsonl').open('ab') as journal:
                journal.write((json.dumps(dict(tool=tool,sha256=sha((ROOT/'tools'/tool).read_bytes()),arguments=arguments))+'\n').encode())
            subprocess.run([sys.executable,'-u',str(ROOT/'tools'/tool),*arguments],cwd=ROOT,check=True)

        def canonical(name,gate):
            folder=ROOT/'validation/natural-dungeon-combat'/name
            r,cap=load(folder/'report.json'),load(folder/'capture.json')
            assert r['failure'] is None and not r.get('deaths',0) and r[gate]
            assert cap['sram_input'] is None and cap['rom_sha256']==prior['md_sha256']
            stream.prove('natural-dungeon-combat/'+name)
            proof_folder=folder.with_name(name+f'-assisted-fixed-replay-{cap["frames"]}')
            proof=load(proof_folder/'replay_report.json')
            assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
            for stem,ext in [('ram','bin'),('frame','png')]:
                filename=f'{stem}_{cap["frames"]:05d}.{ext}'
                assert evidence(folder/filename)==evidence(proof_folder/filename)
            points.append(dict(trace=folder.relative_to(ROOT).as_posix(),frames=cap['frames'],gate=gate))
            (out/'verified_endpoints.json').write_text(json.dumps(points,indent=2)+'\n')
            return r

        def stage(name,planner,rooms,target,extra,assisted,gate):
            nonlocal previous
            cap=load(ROOT/'validation/natural-dungeon-combat'/previous/'capture.json')
            tool='assisted_boss_route.py' if assisted else (
                 'unassisted_arrival_prediction.py' if planner=='evasive' else 'unassisted_fast_prediction.py' if planner=='exit' else 'unassisted_dungeon_continuation.py')
            guard=['--boss-room','0x179'] if assisted else []
            run(tool,[*guard,'--planner',planner,'--continuation',previous,'--trial',prefix+name,
                '--rooms',rooms,'--target-room',target,'--frames',str(cap['frames']+12000),*common,*extra])
            previous='md-auto-'+prefix+name
            r=canonical(previous,gate)
            if not assisted:
                assert r['unassisted_extension'] and not r['new_assistance_writes']
            print('VERIFIED',name,r['last_state'],flush=True)
            return r

        stage('south01','ordinary','0x1b8,0x1b7,0x1c7,0x1c6,0x1d6','0x1d6',
              ['--equip-axe','--avoid-portal-rooms','0x1b7'],True,'room_cleared')
        stage('remote01','contact','0x1d6,0x1e6,0x1d6,0x1d5','0x1d5',
              ['--equip-axe','--avoid-portal-rooms','0x1e6','--contact-room','0x1e6',
               '--contact-destination','0x1d6'],True,'contact_route_passed')
        r=stage('ship01','item','0x1d6,0x1d5','0x1d5',
              ['--equip-axe','--collect-item','16','--item-first-when-blocked'],True,'item_acquisition_passed')
        assert r['last_state']['ship']==1
        stage('north01','ordinary','0x1d5,0x1d6,0x1c6,0x1c7,0x1b7,0x1b8','0x1b8',
              ['--equip-axe','--avoid-portal-rooms','0x1b7','--rush-rooms','0x1d5'],True,'room_cleared')
        stage('warp01','earth','0x1b8,0x1a8,0x198','0x198',
              ['--equip-axe','--avoid-portal-rooms','0x198','--earth-room','0x1a8','--earth-cell','0x34',
               '--earth-cast-x','72','--earth-cast-y','80','--passage-destination','0x198'],True,'earth_route_passed')
        stage('approach01','ordinary','0x198,0x199,0x189','0x189',
              ['--equip-axe','--avoid-portal-rooms','0x198','--wake-sentinels'],True,'room_cleared')
        run('close_assisted_approach.py',['--trace','natural-dungeon-combat/'+previous,
            '--before-room','0x179','--trial',prefix+'main-release01'])
        previous='md-auto-'+prefix+'main-release01'
        canonical(previous,'passed')
        r=stage('boss01','evasive','0x189,0x179','0x179',
              ['--planning-step','16','--entry-boss-kind','0x67','--collect-gem','--equip-basic'],False,'room_cleared')
        assert r['last_state']['progress']==128
        stage('return-earth01','earth','0x179,0x189,0x199,0x198,0x1a8,0x1b8,0x1b7,0x1cb,0x1db','0x1b',
              ['--exit-dungeon','--earth-room','0x1b7','--earth-cell','0x57','--earth-cast-x','120',
               '--earth-cast-y','112','--earth-during-combat','--earth-action-only',
               '--passage-destination','0x1b7','--equip-axe'],False,'earth_route_passed')
        stage('exit01','exit','0x1b7,0x1cb,0x1db','0x1b',
              ['--exit-dungeon','--planning-step','8','--equip-axe'],False,'full_dungeon_cleared')
        print('D7 seventh crystal and exterior return verified',flush=True)
    finally:stream.close()


if __name__=='__main__':
    main()
