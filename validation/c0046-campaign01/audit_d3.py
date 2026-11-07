"""Audit the third c0046 crystal and controller-only exterior return."""
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
paths={Path(__file__).resolve(),ROOT/'analysis/c0046_d3_rope_report.json'}
def read(path):paths.add(path);return path.read_bytes()
def load(path):return json.loads(read(path))
prior=load(ROOT/'analysis/c0046_d3_rope_report.json')
assert prior['passed'] and prior['real_rope_acquired'] and prior['rom_sha256']==digest
snapshot=project/'validation/c0046-d3-sources03'
paths.update(p for p in snapshot.iterdir() if p.is_file())
for name,h in load(snapshot/'source_index.json').items():assert sha(read(snapshot/Path(name).name))==h
source=(ROOT/'input/original.sms').read_bytes()
kind=source[0x3234e+0x1c3*8];hp=source[0x320ea+(kind-32)*4]
assert kind==0x69 and hp==32
stages=[];fight=None
for suffix in ['switch01','key01','pre-boss01','release01','boss01','exit01']:
    name='md-auto-c0046-d3-'+suffix;folder=project/'validation/natural-dungeon-combat'/name
    cap=load(folder/'capture.json');r=load(folder/'report.json')
    assert cap['rom_sha256']==digest and cap['sram_input'] is None
    assert r['failure'] is None and not r['deaths'] and not r['primary_state_imports']
    assist,writes=recording(folder,cap);read(folder/'controls.json');read(folder/'assistance.json')
    assert not assist['boss_assistance'] and not assist['health_refills'] and all(a==sy['hero_hurt'] for _,a,_ in writes)
    frame=cap['frames'];raw=read(folder/f'ram_{frame:05d}.bin');png=read(folder/f'frame_{frame:05d}.png')
    word=lambda n:int.from_bytes(bytes(raw[(sy[n]+i)^1] for i in range(2)),'big')
    proof_folder=folder.with_name(name+f'-assisted-fixed-replay-{frame}')
    proof=load(proof_folder/'replay_report.json')
    assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
    assert proof['rom_sha256']==digest
    for path,h in proof['evidence'].items():assert sha(read(folder/path))==h
    assert raw==read(proof_folder/f'ram_{frame:05d}.bin') and png==read(proof_folder/f'frame_{frame:05d}.png')
    assert raw[(sy['hero_items']+13)^1]==1 and word('sound_unhandled_command')==0
    if suffix=='switch01':assert r['contact_route_passed'] and not r['contact_state_writes']
    if suffix=='key01':assert r['new_key_verified']
    if suffix=='release01':assert word('hero_hurt')==0
    if suffix=='boss01':
        first=r['first_intermediate_combat']
        assert first['room']==0x1c3 and first['actors']==[dict(slot=0,kind=kind,hp=hp)]
        assert first['frame']>assist['release_write_frame'] and first['hurt']<=128
        assert all(f<=assist['release_write_frame'] for f,_,_ in writes) and not r['new_assistance_writes']
        assert r['room_cleared'] and r['full_ram_prediction_matches']==r['verified_persistent_prediction_windows']>0
        assert not r['stack_only_difference_windows']
        fight=dict(first=first,release_frame=assist['release_write_frame'],prediction_windows=r['full_ram_prediction_matches'])
    if suffix=='exit01':
        assert r['dungeon_exit_verified'] and not r['new_assistance_writes']
        save=bytes(raw[(sy['game_save_state']+i)^1] for i in range(592))
        assert all(v&128 for v in save[0x1f:0x22]) and not any(v&128 for v in save[0x22:0x28])
        assert word('room_id')==0x62 and word('hero_max_health')==56
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=frame,room=word('room_id'),
        health=word('hero_health'),max_health=word('hero_max_health'),magic=word('hero_magic'),whole_ram_png_exact=True))
archive=ROOT/'analysis/c0046-d3'
result=dict(passed=True,candidate='c0046',region='auto',rom_sha256=digest,actual_third_crystal_and_exterior=True,
    stages=stages,fight=fight,full_candidate_campaign_verified=False,
    scope='Cold continuation after real rope. Mechanism, key, original-stat boss with aid removed, third crystal and exterior; no resource, actor, progression or SRAM imports.',
    archive_manifest=(archive/'manifest.json').relative_to(ROOT).as_posix())
freeze(ROOT,archive,paths,result,[work])
(ROOT/'analysis/c0046_d3_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
