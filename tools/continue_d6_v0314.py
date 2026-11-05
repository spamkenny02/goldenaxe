"""Execute the source-derived D6 route afresh, using recorded inputs only for proofs."""
import json,shutil
import continue_d8_entry_v0312 as helper
from continue_after_d1_v0314 import ROM
from continue_d8_entry_v0312 import ROOT,COMBAT,ROUTE,SERVICE,report,assert_canonical
from archive_lossless_evidence import sha
from cold_replay_stream import ReplayStream
helper.EVIDENCE=ROOT/'validation/v0314-d6-sources02'
def frame(f,n):return report(ROOT/'validation'/f/n,'capture.json')['frames']
def main():
    prior=report(ROOT/'analysis','d5_campaign_v0314_report.json')
    assert prior['passed'] and prior['fifth_crystal_and_exterior_return'] and prior['md_sha256']==ROM==sha((ROOT/'gaw-megadrive.bin').read_bytes())
    current=prior['stages'][-1]['trace'].split('/')[-1];family=COMBAT;assert_canonical(family,current)
    helper.EVIDENCE.mkdir(exist_ok=False);index={}
    for name in ('recipes/d6-route-v0312.json','continue_d6_v0314.py','continue_d8_entry_v0312.py','assisted_boss_route.py','assisted_prefix.py','natural_dungeon_route.py','natural_dungeon_combat.py','natural_weapon_selection.py','natural_earth_passage.py','natural_contact_passage.py','cold_replay_stream.py','run_core.py'):
        shutil.copyfile(ROOT/'tools'/name,helper.EVIDENCE/name.split('/')[-1]);index['tools/'+name]=sha((helper.EVIDENCE/name.split('/')[-1]).read_bytes())
    (helper.EVIDENCE/'source_index.json').write_text(json.dumps(index,indent=2)+'\n')
    native={p.name:sha(p.read_bytes()) for p in (ROOT/'megadrive/src').iterdir() if p.is_file()}
    (helper.EVIDENCE/'native_source_index.json').write_text(json.dumps(native,indent=2)+'\n')
    recipes=report(ROOT/'tools/recipes','d6-route-v0312.json');assert len(recipes)==15
    (helper.EVIDENCE/'historical_recipes.json').write_text(json.dumps(recipes,indent=2)+'\n')
    executed=[];stream=ReplayStream(helper.EVIDENCE/'cold-stream')
    def finish(check):
        r=report(ROOT/'validation'/family/current,'route_report.json' if family==ROUTE else 'report.json')
        assert r['failure'] is None and not r.get('deaths',0) and check(r),r
        stream.prove(family+'/'+current);assert_canonical(family,current)
    try:
        if not (ROOT/'validation'/SERVICE/'md-v0314-d6-axe-equip01/capture.json').exists():helper.run('natural_weapon_selection.py',['--trace',family+'/'+current,'--slot','1','--assisted-prefix','--trial','v0314-d6-axe-equip01'])
        current='md-v0314-d6-axe-equip01';family=SERVICE;assert_canonical(family,current)
        weapon=report(ROOT/'validation'/family/current,'report.json');assert weapon['passed'] and weapon['selected_slot']==1
        helper.run('assisted_boss_route.py',['--boss-room','0x115','--world-route','--preserve-floor-hurt','--assisted-prefix','--new-assistance-episode','--completed-exit-proof',COMBAT+'/md-auto-v0314-d5-exit02','--prefix-service',current,'--door-index','6','--axe-terrain','--rope-terrain','--live-prefix-terrain','--live-room-replan','--frames',str(frame(family,current)+18000),'--trial','v0314-d6-entry01'])
        current='md-v0314-d6-entry01';family=ROUTE;finish(lambda r:r['reached_entrance'])
        for recipe in recipes:
            tool,*args=recipe['arguments'];assert tool=='tools/assisted_boss_route.py'
            args=[s.replace('v0312','v0314') for s in args]
            prefix='--prefix' if family==ROUTE else '--continuation';assert args[args.index(prefix)+1]==current
            assert args[args.index('--boss-room')+1]=='0x115'
            args[args.index('--frames')+1]=str(frame(family,current)+18000)
            executed.append(dict(source_recipe=recipe['source_recipe'],kind=recipe['kind'],arguments=[tool,*args]))
            (helper.EVIDENCE/'executed_recipes.json').write_text(json.dumps(executed,indent=2)+'\n')
            helper.run('assisted_boss_route.py',args)
            current='md-auto-'+args[args.index('--trial')+1];family=COMBAT
            field={'clear':'room_cleared','key':'new_key_verified','contact':'contact_route_passed','earth':'earth_route_passed','item':'room_cleared'}[recipe['kind']]
            finish(lambda r:r[field])
        print('V314 D6 KEYS, EARTH, CONTACTS AND ICE BELL VERIFIED',flush=True)
    finally:stream.close()
if __name__=='__main__':main()
