"""Audit each regenerated c0046 first-crystal campaign and fixed replay."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,'tools')
from run_core import ROOT
from archive_lossless_evidence import freeze,sha
from assisted_prefix import recording
from validate_playable_sprite_limit import symbols

parser=argparse.ArgumentParser();parser.add_argument('region',choices=['auto','pal'])
region=parser.parse_args().region
work=Path(__file__).resolve().parent;project=work/'isolated/project'
published=ROOT/'versions/candidates/c0046-9e747d38'
digest=sha((published/'gaw-megadrive-c0046.bin').read_bytes())
assert sha((project/'gaw-megadrive.bin').read_bytes())==digest
sy=symbols(published/'symbol.txt')
paths={Path(__file__).resolve(),work/'run_d1.py',work/'resume_d1_key.py',work/(region+'-commands.jsonl'),work/'setup.json'}
def read(path):paths.add(path);return path.read_bytes()
def load(path):return json.loads(read(path))
names=['md-'+region+'-c46-d1-key01','md-'+region+'-c46-d1-ready01',
       'md-'+region+'-c46-d1-key2-01','md-'+region+'-c46-d1-ready02',
       'md-auto-c46-'+region+'-d1-release02','md-'+region+'-c46-d1-boss02',
       'md-'+region+'-c46-d1-exit02']
stages=[];fights=[]
for name in names:
    folder=project/'validation/natural-dungeon-combat'/name
    cap=load(folder/'capture.json');report=load(folder/'report.json')
    assert cap['rom_sha256']==digest and cap['sram_input'] is None
    assert report['failure'] is None and report['deaths']==0 and report['primary_state_imports']==0
    assist,writes=recording(folder,cap)
    assert not assist['boss_assistance'] and assist['health_refills']==0
    assert all(address==sy['hero_hurt'] for _,address,_ in writes)
    read(folder/'assistance.json');read(folder/'controls.json')
    end=cap['frames'];raw=read(folder/f'ram_{end:05d}.bin');read(folder/f'frame_{end:05d}.png')
    word=lambda n:int.from_bytes(bytes(raw[(sy[n]+i)^1] for i in range(2)),'big')
    proof_path=folder.with_name(folder.name+f'-assisted-fixed-replay-{end}')
    proof=load(proof_path/'replay_report.json')
    assert proof['passed'] and proof['rom_sha256']==digest
    assert proof['whole_ram_bytes']==65536 and proof['final_png_exact'] and not proof['feedback_reads']
    for path,expected in proof['evidence'].items():assert sha(read(folder/path))==expected
    assert read(proof_path/f'ram_{end:05d}.bin')==raw
    assert read(proof_path/f'frame_{end:05d}.png')==read(folder/f'frame_{end:05d}.png')
    stages.append(dict(trace=str(folder.relative_to(ROOT)),frames=end,room=word('room_id'),
        health=word('hero_health'),max_health=word('hero_max_health'),keys=word('hero_keys'),whole_ram_png_exact=True))
    if name.endswith('boss02'):
        assert report['room_cleared'] and not report['new_assistance_writes']
        first=report['first_intermediate_combat']
        assert first['room']==0x175 and first['actors']==[dict(slot=0,kind=0x68,hp=12)]
        assert assist['release_write_frame']<first['frame'] and first['hurt']<=128
        assert all(f<=assist['release_write_frame'] for f,_,_ in writes)
        assert report['full_ram_prediction_matches']==report['verified_persistent_prediction_windows']>0
        assert not report['stack_only_difference_windows']
        fights.append(dict(first_combat=first,release_frame=assist['release_write_frame'],
            prediction_windows=report['verified_persistent_prediction_windows']))
    if name.endswith('exit02'):
        assert report['dungeon_exit_verified'] and not report['new_assistance_writes']
        assert word('room_id')==0xb9 and word('hero_max_health')==32
        save=bytes(raw[(sy['game_save_state']+i)^1] for i in range(592))
        assert save[0x1f]&128 and not any(v&128 for v in save[0x20:0x28])
source=(ROOT/'input/original.sms').read_bytes()
assert source[0x3234e+0x175*8]==0x68 and source[0x320ea+(0x68-32)*4]==12
archive=ROOT/f'analysis/c0046-d1-{region}'
result=dict(passed=True,candidate='c0046',region=region,rom_sha256=digest,stages=stages,fights=fights,
    actual_first_crystal_and_exterior=True,full_candidate_campaign_verified=False,
    scope='Cold New Game with approach-only hurt-counter writes, removed before boss; no health, item, progression or SRAM imports. Fixed independent whole RAM/image replays.',
    archive_manifest=str((archive/'manifest.json').relative_to(ROOT)))
freeze(ROOT,archive,paths,result,[work])
(ROOT/f'analysis/c0046_d1_{region}_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
