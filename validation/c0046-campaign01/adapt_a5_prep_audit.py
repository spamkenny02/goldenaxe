"""Check the original gift reader and recovered A5-combat reader separately."""
from pathlib import Path
root=Path(__file__).resolve().parents[2]
path=root/'validation/c0046-campaign01/isolated/project/tools/summarize_d7_prep_c0046.py'
t=path.read_text()
before="    manifest = 'validation/run-c0046-d7-02/'\n    points = load(manifest+'verified_endpoints.json')"
after="""    original_manifest='validation/run-c0046-d7-02/'
    manifest='validation/run-c0046-d7-recovered03-02/'
    original_points=load(original_manifest+'verified_endpoints.json')
    assert len(original_points)==2
    points=original_points+load(manifest+'verified_endpoints.json')
    original_index=load(original_manifest+'source_index.json')
    for name,h in original_index.items():assert sha(read(original_manifest+name.split('/')[-1]))==h
    failed=load('validation/natural-dungeon-route/md-c0046-d7-02-key-shop-route/route_report.json')
    assert failed['failure']=='no_waypoint_progress' and failed['last_state']['room']==0xa5
"""
assert t.count(before)==1;t=t.replace(before,after)
t=t.replace('md-c0046-d7-02-key-shop-route\'','md-c0046-d7-02-key-shop-route02\'')
before="    assert len(points)==len(expected) and len(points) in (7,9,11)"
after="    expected.insert(2,('natural-dungeon-combat/md-auto-c0046-d7-02-a5-clear01','exterior-clear',0xa5))\n    assert len(points)==len(expected) and len(points) in (10,12)"
assert t.count(before)==1;t=t.replace(before,after)
before="        aid,writes = recording(ROOT/trace,cap)"
after="""        if kind=='exterior-clear':
            assert r['room_cleared'] and r['recorded_new_game_prefix']==previous.split('/')[-1]
            assert r['driver_sha256']==sha(read('tools/natural_combat_from_service_c0046.py'))
            assert r['last_state']['room']==0xa5 and r['last_state']['room_flags']&1
            assert not r['last_actors']
        aid,writes = recording(ROOT/trace,cap)"""
assert t.count(before)==1;t=t.replace(before,after)
before="        if kind == 'entry':\n            assert word('room_id') == 0x1db"
after="        if kind=='exterior-clear':assert word('room_id')==0xa5 and data('scratch',4096)[0x883]==4\n"+before
assert t.count(before)==1;t=t.replace(before,after)
before="    cold=load(manifest+'cold-stream/completed.json')"
after="""    first_cold=load(original_manifest+'cold-stream/completed.json')
    assert first_cold['passed'] and first_cold['cold_boot_count']==1 and not first_cold['primary_state_imports']
    assert first_cold['rom_sha256']==digest and len(first_cold['checkpoints'])==2
    cold=load(manifest+'cold-stream/completed.json')"""
assert t.count(before)==1;t=t.replace(before,after)
t=t.replace("for r in cold['checkpoints']","for r in first_cold['checkpoints']+cold['checkpoints']")
t=t.replace("result = dict(passed=True,candidate='c0046',", "result = dict(passed=True,candidate='c0046',cold_replay_streams=2,a5_hidden_shop_opened_by_combat=True,")
t=t.replace('match full RAM/PNG in one independent continuous cold replay','match full RAM/PNG in two independent cold readers, joined at the exact verified gift endpoint')
path.write_text(t,encoding='utf-8')
print('A5 audit retains ten successful checkpoints, two cold readers and failed direct-entry diagnosis')
