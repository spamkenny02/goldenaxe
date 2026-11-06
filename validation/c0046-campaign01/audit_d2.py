"""Verify the actual second c0046 crystal, with boss guard removed."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from assisted_prefix import recording
from archive_lossless_evidence import freeze,sha
from validate_playable_sprite_limit import symbols

work=Path(__file__).resolve().parent;project=work/'isolated/project'
rom=ROOT/'versions/candidates/c0046-9e747d38/gaw-megadrive-c0046.bin'
digest=sha(rom.read_bytes());sy=symbols(rom.with_name('symbol.txt'))
prior=json.loads((ROOT/'analysis/c0046_after_d1_report.json').read_bytes())
assert prior['passed'] and prior['rom_sha256']==digest and prior['second_dungeon_entered']
paths={Path(__file__).resolve(),project/'tools/continue_d2_c0046.py',project/'tools/resume_d2_c0046.py',ROOT/'analysis/c0046_after_d1_report.json'}
paths.add(project/'tools/resume_d2_boss_c0046.py')
snapshot=project/'validation/c0046-d2-sources';paths.update(p for p in snapshot.iterdir() if p.is_file())
def read(path):paths.add(path);return path.read_bytes()
def load(path):return json.loads(read(path))
index=load(snapshot/'source_index.json')
for name,expected in index.items():assert sha(read(snapshot/Path(name).name))==expected
source=(ROOT/'input/original.sms').read_bytes();kind=source[0x3234e+0x144*8]
hp=source[0x320ea+(kind-32)*4];assert kind==0x63 and hp==30
stages=[];fight=None
for suffix in ['key101','key202','key301','pre-boss01','release01','boss01','boss02','exit01']:
    name='md-auto-c0046-d2-'+suffix;folder=project/'validation/natural-dungeon-combat'/name
    cap=load(folder/'capture.json');report=load(folder/'report.json')
    assert cap['rom_sha256']==digest and cap['sram_input'] is None
    assert report['failure']==('frame_limit' if suffix=='boss01' else None)
    assert report['deaths']==0 and report['primary_state_imports']==0
    assist,writes=recording(folder,cap)
    read(folder/'assistance.json');read(folder/'controls.json')
    assert not assist['boss_assistance'] and assist['health_refills']==0
    assert all(address==sy['hero_hurt'] for _,address,_ in writes)
    frame=cap['frames'];raw=read(folder/f'ram_{frame:05d}.bin');png=read(folder/f'frame_{frame:05d}.png')
    word=lambda n:int.from_bytes(bytes(raw[(sy[n]+i)^1] for i in range(2)),'big')
    proof_folder=folder.with_name(name+f'-assisted-fixed-replay-{frame}')
    proof=load(proof_folder/'replay_report.json')
    assert proof['passed'] and proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
    assert proof['rom_sha256']==digest
    for path,expected in proof['evidence'].items():assert sha(read(folder/path))==expected
    assert raw==read(proof_folder/f'ram_{frame:05d}.bin') and png==read(proof_folder/f'frame_{frame:05d}.png')
    assert raw[(sy['hero_items']+1)^1]==1 and word('sound_unhandled_command')==0
    if suffix=='boss01':
        assert not report['room_cleared'] and not report['new_assistance_writes']
        assert report['last_actors'][0]['hp']==8 and word('hero_health')==40
    if suffix=='boss02':
        first=report['first_intermediate_combat']
        assert first['room']==0x144 and first['actors']==[dict(slot=0,kind=kind,hp=hp)]
        assert first['hurt']<=128 and first['frame']>assist['release_write_frame']
        assert all(f<=assist['release_write_frame'] for f,_,_ in writes)
        assert report['room_cleared'] and not report['new_assistance_writes']
        assert report['full_ram_prediction_matches']==report['verified_persistent_prediction_windows']>0
        assert not report['stack_only_difference_windows']
        fight=dict(first=first,release_frame=assist['release_write_frame'],prediction_windows=report['full_ram_prediction_matches'])
    if suffix=='exit01':
        assert report['dungeon_exit_verified'] and not report['new_assistance_writes']
        save=bytes(raw[(sy['game_save_state']+i)^1] for i in range(592))
        assert all(v&128 for v in save[0x1f:0x21]) and not any(v&128 for v in save[0x21:0x28])
        assert word('room_id')==0xd6 and word('hero_max_health')==48
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=frame,room=word('room_id'),
        health=word('hero_health'),max_health=word('hero_max_health'),keys=word('hero_keys'),
        partial_living_fight=suffix=='boss01',whole_ram_png_exact=True))
failed=project/'validation/natural-dungeon-combat/md-auto-c0046-d2-key201'
old=load(failed/'report.json');load(failed/'capture.json')
assert old['failure']=='frame_limit' and old['last_state']['room']==0x151 and not old['deaths']
assert load(project/'validation/natural-dungeon-combat/md-auto-c0046-d2-key202/report.json')['isolated_foe_retries']==1
archive=ROOT/'analysis/c0046-d2'
result=dict(passed=True,candidate='c0046',region='auto',rom_sha256=digest,
    actual_second_crystal_and_exterior=True,stages=stages,fight=fight,
    previous_controller_limit=dict(trace=failed.relative_to(ROOT).as_posix(),failure='frame_limit',room=0x151,resolved_by_one_ordinary_leave_and_return=True),
    full_candidate_campaign_verified=False,
    scope='Cold continuation with real keys and crystal, approach-only hurt-counter aid removed before boss, no health/item/progression/SRAM imports; independent whole RAM/image replays.',
    archive_manifest=(archive/'manifest.json').relative_to(ROOT).as_posix())
freeze(ROOT,archive,paths,result,[work])
(ROOT/'analysis/c0046_d2_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
