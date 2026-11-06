"""Release the D7 approach guard, fight the real intermediate, then resume."""
import argparse,shutil
from cold_replay_stream import ReplayStream
import json
import subprocess
import sys

from archive_lossless_evidence import sha
from rebase_natural_campaign import evidence
from run_core import ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trial',default='02')
    args = parser.parse_args()
    assert args.trial.isalnum()
    prior = json.loads(evidence(ROOT/'analysis/d7_prep_v0317_report.json'))
    assert prior['passed'] and not prior['intermediate_boss_entered']
    assert prior['md_sha256'] == sha((ROOT/'gaw-megadrive.bin').read_bytes())
    previous = prior['stages'][-1]['trace'].removeprefix('validation/')
    out = ROOT/'validation'/('run-v0317-d7-midboss-'+args.trial)
    out.mkdir(exist_ok=False)
    prefix = 'v0317-d7-'+args.trial+'-'
    source_index={}
    for name in ('continue_d7_midboss_v0317.py','close_assisted_approach.py','unassisted_dungeon_continuation.py','natural_contact_passage.py','unassisted_arrival_prediction.py','unassisted_fast_prediction.py','natural_boss_evasive_planner.py','natural_boss_side_planner.py','natural_boss_escape_planner.py','natural_combat_beam.py','natural_dungeon_combat.py','resume_after_intermediate.py','assisted_prefix.py','prediction_video_skip.py','cold_replay_stream.py','run_core.py'):
        target=out/name;shutil.copyfile(ROOT/'tools'/name,target);source_index['tools/'+name]=sha(target.read_bytes())
    (out/'source_index.json').write_text(json.dumps(source_index,indent=2)+'\n')
    stream=ReplayStream(out/'cold-stream')
    try:
        points = []

        def load(path):
            return json.loads(evidence(path))

        def run(tool, arguments):
            print('START',tool,*arguments,flush=True)
            with (out/'commands.jsonl').open('ab') as journal:
                journal.write((json.dumps(dict(tool=tool,sha256=sha((ROOT/'tools'/tool).read_bytes()),arguments=arguments))+'\n').encode())
            subprocess.run([sys.executable,'-u',str(ROOT/'tools'/tool),*arguments],cwd=ROOT,check=True)

        def canonical(name,gate):
            folder = ROOT/'validation/natural-dungeon-combat'/name
            r,cap = load(folder/'report.json'),load(folder/'capture.json')
            assert r['failure'] is None and not r.get('deaths',0) and r[gate]
            stream.prove('natural-dungeon-combat/'+name)
            proof_folder = folder.with_name(name+f'-assisted-fixed-replay-{cap["frames"]}')
            proof = load(proof_folder/'replay_report.json')
            assert proof['passed'] and proof['whole_ram_bytes'] == 65536 and proof['final_png_exact']
            assert proof['rom_sha256'] == prior['md_sha256'] and cap['sram_input'] is None
            for stem,ext in [('ram','bin'),('frame','png')]:
                filename=f'{stem}_{cap["frames"]:05d}.{ext}'
                assert evidence(folder/filename) == evidence(proof_folder/filename)
            points.append(dict(trace=folder.relative_to(ROOT).as_posix(),frames=cap['frames'],gate=gate))
            (out/'verified_endpoints.json').write_text(json.dumps(points,indent=2)+'\n')
            return cap

        run('close_assisted_approach.py',['--trace',previous,'--before-room','0x1b8','--trial',prefix+'release01'])
        name='md-auto-'+prefix+'release01'
        cap=canonical(name,'passed')
        common=['--assisted-prefix','--max-deaths','0','--target-room','0x1b8','--equip-axe',
                '--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors']
        run('unassisted_dungeon_continuation.py',['--planner','contact','--continuation',name,
            '--trial',prefix+'contact01','--rooms','0x1b9,0x1b8','--contact-room','0x1b9',
            '--contact-destination','0x1b8','--frames',str(cap['frames']+12000),*common])
        name='md-auto-'+prefix+'contact01'
        cap=canonical(name,'contact_route_passed')
        run('unassisted_arrival_prediction.py',['--planner','evasive','--planning-step','8','--entry-boss-kind','0x78',
            '--continuation',name,'--trial',prefix+'midboss01','--rooms','0x1b8',
            '--frames',str(cap['frames']+12000),*common])
        name='md-auto-'+prefix+'midboss01'
        canonical(name,'room_cleared')
        run('resume_after_intermediate.py',['--trace','natural-dungeon-combat/'+name,'--boss-room','0x1b8',
            '--next-boss-room','0x179','--trial',prefix+'resume01'])
        canonical('md-auto-'+prefix+'resume01','resumed_after_verified_intermediate')
        print('D7 intermediate defeated without assistance; next approach resumed',flush=True)
    finally:stream.close()


if __name__ == '__main__':
    main()
