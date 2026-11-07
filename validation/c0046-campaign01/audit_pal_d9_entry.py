"""Verify V318 PAL's paid return, Ice Bell, and first D9 guardian."""
import argparse,json
import sys
from pathlib import Path

sys.path.insert(0, 'tools')
from archive_lossless_evidence import freeze, sha
from assisted_prefix import recording
from run_core import ROOT as PUBLIC_ROOT
ROOT=PUBLIC_ROOT/'validation/c0046-campaign01/isolated/project'
parser=argparse.ArgumentParser();parser.add_argument('--prefix-only',action='store_true');options=parser.parse_args()
from validate_playable_sprite_limit import symbols

work=ROOT/'validation/palc0046-d9-entry-sources'
digest = sha((ROOT/'gaw-megadrive.bin').read_bytes())
prior = json.loads((PUBLIC_ROOT/'analysis/palc0046_d8_report.json').read_bytes())
assert prior['passed'] and prior['actual_eighth_crystal_and_exterior'] and prior['rom_sha256']==digest
sy = symbols(ROOT/'megadrive/out/release/symbol.txt')
sms = (ROOT/'input/original.sms').read_bytes()
assert sms[0x3234e + 0x1be*8]==0x79
assert sms[0x320ea + (0x79-32)*4]==60

paths={Path(__file__).resolve(),PUBLIC_ROOT/'validation/c0046-campaign01/prepare_pal_d9_entry.py',work/'commands.jsonl',ROOT/'analysis/paid_passage_reference.json',PUBLIC_ROOT/'analysis/palc0046_d8_report.json'}
for name,h in json.loads((work/'entry-tools/source_index.json').read_bytes()).items():
    for p in (work/'entry-tools'/name,ROOT/'tools'/name):assert sha(p.read_bytes())==h;paths.add(p)

def read(path):
    assert path.is_file(), path
    paths.add(path)
    return path.read_bytes()

def load(path):
    return json.loads(read(path))

spec = [('natural-dungeon-route','md-pal-palc0046-d9-paid1a-route01',0x9f),
        ('natural-service-route','md-palc0046-d9-paid1a-service01',0x3c),
        ('natural-dungeon-route','md-pal-palc0046-d9-entry02',0x1fc),
        ('natural-dungeon-combat','md-pal-palc0046-d9-switch1de-02',0x1ce),
        ('natural-dungeon-combat','md-pal-palc0046-d9-earth1ce-01',0x1ce),
        ('natural-dungeon-combat','md-pal-palc0046-d9-mini-ready01',0x1ce),
        ('natural-dungeon-combat','md-auto-palc0046-d9-guard-release01',0x1ce),
        ('natural-dungeon-combat','md-pal-palc0046-d9-midboss01',0x1be)]
if prior['stages'][-1]['gold']<10:
    spec[:0]=[('natural-dungeon-route','md-pal-palc0046-d9-goldb5-route01',0x3f),('natural-service-route','md-palc0046-d9-goldb5-service01',0xb5)]
cold=load(ROOT/'validation/palc0046-d9-entry-cold-stream01'/('checkpoints.json' if options.prefix_only else 'completed.json'))
if options.prefix_only:spec=spec[:len(cold['checkpoints'])]
else:assert cold['passed']
assert cold['cold_boot_count']==1 and cold['rom_sha256']==digest
assert len(cold['checkpoints'])==len(spec)
stages, reports = [], []
previous_frame = prior['campaign_frames']
previous=PUBLIC_ROOT/prior['current_campaign_trace'];previous_cap=load(previous/'capture.json');_,previous_writes=recording(previous,previous_cap)
assert sha(read(previous/f'ram_{previous_frame:05d}.bin'))==prior['final_ram_sha256']
for (family,name,room), checkpoint in zip(spec,cold['checkpoints']):
    relative = f'{family}/{name}'
    folder = ROOT/'validation'/relative
    cap = load(folder/'capture.json')
    frame = cap['frames']
    assert checkpoint==dict(trace=relative,frames=frame,whole_ram_png_exact=True)
    assert cap['rom_sha256']==digest and cap['sram_input'] is None and frame>previous_frame and cap['core_options']['genesis_plus_gx_region_detect']=='pal'
    report = load(folder/('route_report.json' if family=='natural-dungeon-route' else 'report.json'))
    assert report.get('failure') is None and not report.get('deaths',0)
    if family=='natural-service-route':
        assert report['source_prefix']==previous.name and report['passed'] and not report['new_assistance_writes']
    else:
        assert report['prefix_end']==previous_frame
        assert previous.name in (report.get('recorded_new_game_prefix'),report.get('recorded_combat_prefix'),report.get('recorded_service_prefix'))
    proof = folder.with_name(name+f'-assisted-fixed-replay-{frame}')
    validation = load(proof/'replay_report.json')
    assert validation['passed'] and validation['whole_ram_bytes']==65536 and validation['final_png_exact']
    for filename, expected in validation['evidence'].items():
        assert sha(read(folder/filename))==expected
    for file in (f'ram_{frame:05d}.bin',f'frame_{frame:05d}.png'):
        assert read(folder/file)==read(proof/file)
    aid,writes = recording(folder,cap)
    assert not aid['boss_assistance'] and not aid['primary_state_imports'] and not aid['health_refills']
    assert all(address==sy['hero_hurt'] and value in (b'\0\0',b'\0\x81') for _,address,value in writes)
    if previous_writes is not None:
        assert writes[:len(previous_writes)]==previous_writes
    if family=='natural-service-route':assert writes==previous_writes
    if name.endswith('goldb5-service01'):
        assert report['last_state']['gold']-report['first_state']['gold']==10 and report['last_state']['outside_flags']&2
    raw=read(folder/f'ram_{frame:05d}.bin')
    def data(name,size):
        return bytes(raw[(sy[name]+i)^1] for i in range(size))
    def word(name):
        return int.from_bytes(data(name,2),'big')
    save=data('game_save_state',592)
    assert save[0x1f:0x28]==bytes([128]*8+[0])
    assert word('room_id')==room and word('hero_health')>0
    assert word('sound_unhandled_command')==0
    stages.append(dict(trace=folder.relative_to(PUBLIC_ROOT).as_posix(),frames=frame,room=room,
        health=word('hero_health'),magic=word('hero_magic'),gold=word('hero_gold'),
        keys=word('hero_keys'),whole_ram_png_exact=True))
    previous=folder
    previous_frame=frame
    previous_writes=writes
    reports.append(report)

if options.prefix_only:
    print('Read-only D9 entry prefix audit passed:',len(stages),'stages; last',stages[-1],flush=True);raise SystemExit(0)
house,paid,entrance,contact,earth,ready,release,boss=reports[-8:]
assert house['reached_entrance'] and house['directional_probe_succeeded']
assert paid['passed'] and paid['price']==10 and paid['outside']==0x1a and paid['target']==0x3c
assert paid['first_state']['gold']-paid['last_state']['gold']==10
assert entrance['reached_entrance'] and entrance['directional_probe_succeeded']
assert entrance['bell_passage_verified'] and entrance['bell_opened']['bell']==1
assert contact['passed'] and earth['earth_route_passed'] and ready['room_cleared']
assert release['last_state']['hurt']==0 and boss['room_cleared'] and not boss['deaths']
assert not boss['new_assistance_writes']
windows=boss['full_ram_prediction_matches']
assert windows>0 and boss['verified_persistent_prediction_windows']==windows
first=boss['first_intermediate_combat']
assert first['room']==0x1be and first['hurt']==0 and first['health']>0 and first['actors']==[dict(slot=0,kind=0x79,hp=60)]
release_frame=aid['release_write_frame']
assert release_frame==stages[-2]['frames']<first['frame'] and max(f for f,_,_ in writes)==release_frame
assert boss['extension_guard_checks_through_frame']==frame and not validation['feedback_reads'] and validation['live_boss_guard_check']

manifest = PUBLIC_ROOT/'analysis/palc0046-d9-midboss'
result = dict(passed=True,candidate='c0046',region='pal',rom_sha256=digest,stages=stages,current_campaign_trace=stages[-1]['trace'],campaign_frames=stages[-1]['frames'],
    toll_price=paid['price'],bell_opened=entrance['bell_opened'],
    guard_release_frame=release_frame,first_intermediate_combat=first,
    first_intermediate_defeated=True,intermediate_assistance=False,
    first_damage=boss["first_extension_damage"],full_ram_prediction_windows=windows,
    eight_crystals_preserved=True,ninth_crystal_obtained=False,
    archive_manifest=(manifest/'manifest.json').relative_to(PUBLIC_ROOT).as_posix())
freeze(PUBLIC_ROOT,manifest,paths,result,[PUBLIC_ROOT/'validation/c0046-campaign01'])
(PUBLIC_ROOT/'analysis/palc0046_d9_midboss_report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
