"""Finish current D8 through its mechanisms, thief key, main boss and exit."""
import json,shutil
from cold_replay_stream import ReplayStream
from archive_lossless_evidence import sha
from continue_d8_entry_v0314 import ROOT,EVIDENCE,run,report,assert_canonical
FAMILY='natural-dungeon-combat'
COMMON=['--assisted-prefix','--max-deaths','0','--collision-aim','--settle-attacks','--doorway-ranges','--ignore-inactive-actors']

def state(name):
    return report(ROOT/'validation'/FAMILY/name,'report.json')

def replay(name):
    STREAM.prove(FAMILY+'/'+name)
    assert_canonical(FAMILY,name)

def frame(name):
    return report(ROOT/'validation'/FAMILY/name,'capture.json')['frames']


def finish(name, predicate):
    result=state(name)
    assert result['failure'] is None and not result['deaths'] and predicate(result), result
    replay(name)


def main():
    receipt=report(ROOT/'analysis','d8_midboss_v0314_report.json')
    assert receipt['passed'] and receipt['intermediate_defeated'] and not receipt['intermediate_assistance']
    snapshot=EVIDENCE/'main-sources';snapshot.mkdir()
    source_index={}
    for name in ('continue_d8_finish_v0314.py','recipes/d8-thief-route-v0306.json','continue_d8_entry_v0314.py','resume_after_intermediate.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_combat.py','natural_contact_passage.py','natural_item_acquisition.py','natural_earth_passage.py','close_assisted_approach.py','unassisted_dungeon_continuation.py','unassisted_arrival_prediction.py','unassisted_fast_prediction.py','natural_boss_evasive_planner.py','natural_exit_planner.py','natural_combat_beam.py','prediction_video_skip.py','cold_replay_stream.py','run_core.py'):
        target=snapshot/name.split('/')[-1];shutil.copyfile(ROOT/'tools'/name,target);source_index['tools/'+name]=sha(target.read_bytes())
    (snapshot/'source_index.json').write_text(json.dumps(source_index,indent=2)+'\n')
    global STREAM
    STREAM=ReplayStream(snapshot/'cold-stream')
    try:
        executed=[]
        boss='md-auto-v0314-d8-midboss01'
        assert_canonical(FAMILY,boss)
        assert state(boss)['room_cleared'] and not state(boss)['new_assistance_writes']
        run('resume_after_intermediate.py',['--trace',FAMILY+'/'+boss,'--boss-room','0x196','--trial','v0314-d8-approach-resume01'])
        previous='md-auto-v0314-d8-approach-resume01'
        finish(previous,lambda r:r['resumed_after_verified_intermediate'])
        recipes=json.loads((ROOT/'tools/recipes/d8-thief-route-v0306.json').read_bytes())
        for recipe in recipes:
            tool,*args=recipe['arguments']
            args=[s.replace('v0306','v0314') for s in args]
            assert args[args.index('--continuation')+1]==previous
            args[args.index('--frames')+1]=str(frame(previous)+14000)
            executed.append(dict(source_recipe=recipe,arguments=[tool,*args,'--max-deaths','0']))
            (snapshot/'executed_recipes.json').write_text(json.dumps(executed,indent=2)+'\n')
            run(tool.removeprefix('tools/'),[*args,'--max-deaths','0'])
            previous='md-auto-'+args[args.index('--trial')+1]
            field={'ordinary':'room_cleared','contact':'contact_route_passed','earth':'earth_route_passed','item':'item_acquisition_passed'}[recipe['planner']]
            finish(previous,lambda r:r[field])
        run('close_assisted_approach.py',['--trace',FAMILY+'/'+previous,'--before-room','0x196','--trial','v0314-d8-main-release01'])
        previous='md-auto-v0314-d8-main-release01'
        finish(previous,lambda r:r['last_state']['hurt']==0)
        run('unassisted_arrival_prediction.py',[*COMMON,'--planner','evasive','--planning-step','8','--entry-boss-kind','0x6b','--continuation',previous,'--rooms','0x1a6,0x196','--target-room','0x196','--collect-gem','--equip-basic','--frames',str(frame(previous)+12000),'--trial','v0314-d8-boss01'])
        previous='md-auto-v0314-d8-boss01'
        finish(previous,lambda r:r['room_cleared'] and r['last_state']['progress']==128 and not r['new_assistance_writes'])
        run('unassisted_fast_prediction.py',[*COMMON,'--planner','exit','--planning-step','8','--continuation',previous,'--rooms','0x196,0x1a6,0x1a7,0x1eb,0x1ea','--target-room','0x29','--exit-dungeon','--equip-axe','--frames',str(frame(previous)+8000),'--trial','v0314-d8-exit01'])
        finish('md-auto-v0314-d8-exit01',lambda r:r['full_dungeon_cleared'] and not r['new_assistance_writes'])
        print('EIGHTH CRYSTAL AND EXIT VERIFIED',flush=True)
    finally:STREAM.close()


if __name__=='__main__':
    main()
