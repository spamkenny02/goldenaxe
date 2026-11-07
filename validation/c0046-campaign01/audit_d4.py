"""Verify real Earth passages, canoe, fourth boss and exterior return."""
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
paths={Path(__file__).resolve(),ROOT/'analysis/earth_learning_c0046_report.json'}
def read(p):paths.add(p);return p.read_bytes()
def load(p):return json.loads(read(p))
prior=load(ROOT/'analysis/earth_learning_c0046_report.json')
assert prior['passed'] and prior['earth_level']==1 and prior['md_sha256']==digest
snapshot=project/'validation/c0046-d4-sources'
paths.update(p for p in snapshot.iterdir() if p.is_file())
for name,h in load(snapshot/'source_index.json').items():assert sha(read(snapshot/Path(name).name))==h
stream=load(project/'validation/c0046-d4-cold-stream/checkpoints.json')
assert stream['cold_boot_count']==1 and stream['rom_sha256']==digest and len(stream['checkpoints'])==10
resumed=load(project/'validation/c0046-d4-exit-cold-stream03/checkpoints.json')
assert resumed['cold_boot_count']==1 and resumed['rom_sha256']==digest and len(resumed['checkpoints'])==1
checkpoints=stream['checkpoints']+resumed['checkpoints']
retry_snapshot=project/'validation/c0046-d4-exit-sources03'
paths.update(p for p in retry_snapshot.iterdir() if p.is_file())
for name,h in load(retry_snapshot/'source_index.json').items():assert sha(read(retry_snapshot/Path(name).name))==h
failed=load(project/'validation/natural-dungeon-combat/md-auto-c0046-d4-exit01/report.json')
assert failed['failure']=='controller_stalled' and failed['last_state']['room']==0x1b0
assert not failed['deaths'] and not failed['new_assistance_writes']
ordinary=load(project/'validation/natural-dungeon-combat/md-auto-c0046-d4-exit02/report.json')
assert ordinary['failure']=='continuation_route_died' and ordinary['deaths']==1
assert not ordinary['new_assistance_writes']
paths.update(p for p in (project/'validation/c0046-d4-exit-sources02').iterdir() if p.is_file())
source=(ROOT/'input/original.sms').read_bytes();kind=source[0x3234e+0x180*8]
hp=source[0x320ea+(kind-32)*4];assert kind==0x6a and hp==30
cases=[('natural-dungeon-route','md-c0046-d4-entry01')]
cases += [('natural-dungeon-combat','md-auto-c0046-d4-'+suffix) for suffix in
          ['key01','earth01','a1-key01','canoe01','warp01','boss-key01','pre-boss01','release01','boss01','exit03']]
stages=[];earth=[];fight=None
for i,(family,name) in enumerate(cases):
    folder=project/'validation'/family/name
    cap=load(folder/'capture.json');r=load(folder/('route_report.json' if i==0 else 'report.json'))
    assert cap['rom_sha256']==digest and cap['sram_input'] is None and r['failure'] is None
    assert not r.get('deaths',0)
    assist,writes=recording(folder,cap);read(folder/'controls.json');read(folder/'assistance.json')
    assert not assist['primary_state_imports'] and not assist['health_refills'] and not assist['boss_assistance']
    assert all(a==sy['hero_hurt'] for _,a,_ in writes)
    frame=cap['frames'];raw=read(folder/f'ram_{frame:05d}.bin');png=read(folder/f'frame_{frame:05d}.png')
    data=lambda n,k:bytes(raw[(sy[n]+j)^1] for j in range(k))
    word=lambda n:int.from_bytes(data(n,2),'big')
    proof_folder=folder.with_name(name+f'-assisted-fixed-replay-{frame}')
    p=load(proof_folder/'replay_report.json')
    assert p['passed'] and p['whole_ram_bytes']==65536 and p['final_png_exact'] and not p['feedback_reads']
    assert p['rom_sha256']==digest
    assert checkpoints[i]==dict(trace=family+'/'+name,frames=frame,whole_ram_png_exact=True)
    for path,h in p['evidence'].items():assert sha(read(folder/path))==h
    assert raw==read(proof_folder/f'ram_{frame:05d}.bin') and png==read(proof_folder/f'frame_{frame:05d}.png')
    assert word('sound_unhandled_command')==0 and data('hero_items',17)[5]==1
    if name.endswith(('key01','a1-key01','boss-key01')):assert r['new_key_verified']
    if name.endswith(('earth01','warp01')):
        assert r['earth_route_passed'] and not r['earth_state_writes']
        before,opened=r['earth_before'],r['earth_opened']
        assert before['cell']==11 and opened['cell'] in [0,12] and before['magic']-opened['magic']==8
        earth.append(dict(room=r['earth_passage_room'],cell=r['earth_cell'],before=before,opened=opened))
    if name.endswith('canoe01'):
        assert r['item_acquisition_passed'] and not r['item_acquisition_state_writes'] and r['collect_item_requested']==12
        assert r['item_acquisition_first']['owned']==0 and r['item_acquisition_last']['owned']==data('hero_items',17)[12]==1
    if name.endswith('pre-boss01'):assert r['target_room_reached'] and word('room_id')==0x190
    if name.endswith('release01'):assert word('hero_hurt')==0
    if name.endswith('boss01') and not name.endswith('pre-boss01'):
        first=r['first_intermediate_combat']
        assert first['room']==0x180 and first['actors']==[dict(slot=0,kind=kind,hp=hp)]
        assert first['frame']>assist['release_write_frame'] and first['hurt']<=128
        assert all(f<=assist['release_write_frame'] for f,_,_ in writes) and not r['new_assistance_writes']
        assert r['room_cleared'] and r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0
        assert not r['stack_only_difference_windows']
        fight=dict(first=first,release_frame=assist['release_write_frame'],prediction_windows=r['full_ram_prediction_matches'])
    if name.endswith('exit03'):
        assert r['dungeon_exit_verified'] and not r['new_assistance_writes']
        save=data('game_save_state',592)
        assert all(v&128 for v in save[0x1f:0x23]) and not any(v&128 for v in save[0x23:0x28])
        assert word('room_id')==0x10 and word('hero_max_health')==64 and data('hero_items',17)[12]==1
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=frame,room=word('room_id'),
        health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),whole_ram_png_exact=True))
archive=ROOT/'analysis/c0046-d4'
result=dict(passed=True,candidate='c0046',region='auto',rom_sha256=digest,actual_fourth_crystal_and_exterior=True,
    actual_canoe_acquired=True,earth_casts=earth,stages=stages,fight=fight,full_candidate_campaign_verified=False,
    scope='Real Earth casts and MP costs, keys, canoe, source-stat boss after guard release, fourth crystal and exterior. No resources, actors, progression or SRAM imports; ten checkpoints from one independent cold replay, then an independent cold replay of the corrected exit from the same verified boss endpoint. The failed optional-puzzle detour is retained and excluded from the successful itinerary.',
    archive_manifest=(archive/'manifest.json').relative_to(ROOT).as_posix())
freeze(ROOT,archive,paths,result,[work])
(ROOT/'analysis/c0046_d4_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
