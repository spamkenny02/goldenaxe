"""Verify palc0046 axe, real fairy service and second-dungeon entry."""
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
assert sha((project/'gaw-megadrive.bin').read_bytes())==digest
prior=json.loads((ROOT/'analysis/c0046_d1_pal_report.json').read_bytes())
assert prior['passed'] and prior['rom_sha256']==digest and prior['actual_first_crystal_and_exterior']
paths={Path(__file__).resolve(),project/'tools/continue_after_d1_palc0046.py',ROOT/'analysis/c0046_d1_pal_report.json'}
snapshot=project/'validation/palc0046-after-d1-sources'
paths.update(p for p in snapshot.iterdir() if p.is_file())
def read(path):paths.add(path);return path.read_bytes()
def load(path):return json.loads(read(path))
index=load(snapshot/'source_index.json')
for name,expected in index.items():assert sha(read(snapshot/Path(name).name))==expected
stages=[]
for family,name in [('natural-dungeon-route','md-pal-palc0046-d1-axe-entry01'),
    ('natural-dungeon-combat','md-pal-palc0046-d1-axe-key01'),
    ('natural-dungeon-combat','md-pal-palc0046-d1-axe01'),
    ('natural-dungeon-combat','md-pal-palc0046-d1-axe-exit01'),
    ('natural-dungeon-route','md-pal-palc0046-fairy-route01'),
    ('natural-service-route','md-palc0046-fairy-service01'),
    ('natural-dungeon-route','md-pal-palc0046-d2-entry01')]:
    folder=project/'validation'/family/name
    cap=load(folder/'capture.json');report=load(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'))
    assert cap['rom_sha256']==digest and cap['sram_input'] is None and report['failure'] is None
    assert not report.get('deaths',0) and cap['core_options']['genesis_plus_gx_region_detect']=='pal'
    assist,writes=recording(folder,cap)
    read(folder/'assistance.json');read(folder/'controls.json')
    assert assist['primary_state_imports']==0 and not assist['boss_assistance'] and assist['health_refills']==0
    assert all(a==sy['hero_hurt'] for _,a,_ in writes)
    frame=cap['frames'];raw=read(folder/f'ram_{frame:05d}.bin');png=read(folder/f'frame_{frame:05d}.png')
    word=lambda n:int.from_bytes(bytes(raw[(sy[n]+i)^1] for i in range(2)),'big')
    proof_folder=folder.with_name(name+f'-assisted-fixed-replay-{frame}')
    proof=load(proof_folder/'replay_report.json')
    assert proof['passed'] and proof['rom_sha256']==digest and proof['whole_ram_bytes']==65536 and proof['final_png_exact']
    assert not proof['feedback_reads']
    for p,expected in proof['evidence'].items():assert sha(read(folder/p))==expected
    assert raw==read(proof_folder/f'ram_{frame:05d}.bin') and png==read(proof_folder/f'frame_{frame:05d}.png')
    if name=='md-pal-palc0046-d1-axe01':
        assert report['collect_item_requested']==1 and report['collect_item_target_value']==1
        assert word('hero_weapon_level')==1 and word('hero_items')!=0
    if name=='md-palc0046-fairy-service01':
        assert report['passed'] and report['initial_state']['max_health']==32
        assert report['last_state']['max_health']==40 and report['last_state']['outside_flags']&2
    stages.append(dict(trace=folder.relative_to(ROOT).as_posix(),frame=frame,room=word('room_id'),
        health=word('hero_health'),max_health=word('hero_max_health'),weapon=word('hero_weapon_level'),whole_ram_png_exact=True))
assert stages[-1]['room']==0x171 and stages[-1]['health']==stages[-1]['max_health']==40 and stages[-1]['weapon']==1
stream=project/'validation/palc0046-after-d1-cold-stream/completed.json';receipt=load(stream)
assert receipt['passed'] and receipt['cold_boot_count']==1 and receipt['rom_sha256']==digest and len(receipt['checkpoints'])==7
assert all(c['whole_ram_png_exact'] for c in receipt['checkpoints'])
assert receipt['checkpoints'][-1]['frames']==stages[-1]['frame']
paths.update([work/'prepare_pal_after_d1.py',work/'prepare_pal_d2.py'])
archive=ROOT/'analysis/palc0046-after-d1'
result=dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,
    actual_axe_and_life_fairy=True,second_dungeon_entered=True,stages=stages,
    full_candidate_campaign_verified=False,scope='Cold continuation after verified first crystal; real item/fairy rewards and controller-only progression, with approach-only hurt-counter writes. No resource or SRAM imports.',
    archive_manifest=(archive/'manifest.json').relative_to(ROOT).as_posix())
freeze(ROOT,archive,paths,result,[work])
(ROOT/'analysis/palc0046_after_d1_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
