"""Verify real D3 entry, portal traversal and rope acquisition on c0046."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

work=Path(__file__).resolve().parent;project=work/'isolated/project'
rom=ROOT/'versions/candidates/c0046-9e747d38/gaw-megadrive-c0046.bin'
digest=sha(rom.read_bytes());sy=symbols(rom.with_name('symbol.txt'))
paths={Path(__file__).resolve(),work/'portal_controller_fix.json',project/'tools/resume_d3_c0046.py'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
prior=load(ROOT/'analysis/oil_service_c0046_report.json')
assert prior['passed'] and prior['real_oil_gift'] and prior['md_sha256']==digest
for dirname in ['c0046-d3-sources02','c0046-d3-sources03']:
    snapshot=project/'validation'/dirname
    index=load(snapshot/'source_index.json')
    for name,expected in index.items():assert sha(read(snapshot/Path(name).name))==expected
stages=[]
for family,name in [('natural-dungeon-route','md-c0046-d3-entry01'),('natural-dungeon-combat','md-auto-c0046-d3-rope03')]:
    folder=project/'validation'/family/name
    cap=load(folder/'capture.json');r=load(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'))
    assert cap['rom_sha256']==digest and cap['sram_input'] is None and r['failure'] is None
    assist,writes=recording(folder,cap);read(folder/'assistance.json');read(folder/'controls.json')
    assert not assist['boss_assistance'] and not assist['health_refills'] and not assist['primary_state_imports']
    assert assist['first_boss_entry'] is None and all(a==sy['hero_hurt'] for _,a,_ in writes)
    frame=cap['frames'];raw=read(folder/f'ram_{frame:05d}.bin');png=read(folder/f'frame_{frame:05d}.png')
    word=lambda n:int.from_bytes(bytes(raw[(sy[n]+i)^1] for i in range(2)),'big')
    proof_folder=folder.with_name(name+f'-assisted-fixed-replay-{frame}')
    p=load(proof_folder/'replay_report.json')
    assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
    for path,h in p['evidence'].items():assert sha(read(folder/path))==h
    assert raw==read(proof_folder/f'ram_{frame:05d}.bin') and png==read(proof_folder/f'frame_{frame:05d}.png')
    rope=raw[(sy['hero_items']+13)^1]
    if family=='natural-dungeon-route':assert r['reached_entrance'] and word('room_id')==0x1f8 and not rope
    else:
        assert r['item_acquisition_passed'] and not r['item_acquisition_state_writes']
        assert r['collect_item_requested']==13 and r['item_acquisition_first']['owned']==0
        assert r['item_acquisition_last']['owned']==1 and rope==1 and not word('item_reward_active')
        assert word('room_id')==0x1f4 and r['avoided_portal_rooms']==[0x1e2]
        events=load(folder/'events.json');rooms=[]
        for e in events:
            if not rooms or rooms[-1]!=e['room']:rooms.append(e['room'])
        assert rooms==[0x1f8,0x1f7,0x1e7,0x1e2,0x1f2,0x1f3,0x1f4],rooms
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frames=frame,room=word('room_id'),
        health=word('hero_health'),max_health=word('hero_max_health'),rope=rope,whole_ram_png_exact=True))
rejected=[]
for suffix in ['rope01','rope02']:
    folder=project/'validation/natural-dungeon-combat'/('md-auto-c0046-d3-'+suffix)
    r=load(folder/'report.json');c=load(folder/'capture.json');read(folder/'controls.json')
    assert r['failure']=='controller_stalled' and not r['item_acquisition_passed']
    rejected.append(dict(trace=folder.relative_to(ROOT).as_posix(),failure=r['failure'],room=r['last_state']['room']))
result=dict(passed=True,candidate='c0046',region='auto',rom_sha256=digest,real_rope_acquired=True,
    portal_rooms=[0x1e7,0x1e2],stages=stages,rejected_controller_trials=rejected,
    full_candidate_campaign_verified=False,scope='Real rope after cold boot and normal portal traversal. Approach-only hurt writes, no item/health/SRAM imports, independent whole RAM/image replay.')
archive=ROOT/'analysis/c0046-d3-rope'
freeze(ROOT,archive,paths,result,[work])
result['archive_manifest']=(archive/'manifest.json').relative_to(ROOT).as_posix()
(ROOT/'analysis/c0046_d3_rope_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
